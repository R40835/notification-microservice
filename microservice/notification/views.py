from adrf.decorators import api_view
from adrf.requests import Request

from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .models import AppNotification
from .serializers import AppNotificationSerializer
from .utils import ApiResponse, AsyncPaginator, async_serializer

from channels.layers import get_channel_layer


@api_view(['POST'])
async def send_notification(request: Request) -> Response:
    """
    Api view to send real-time notifications to clients. This is achieved by sending 
        a message through websockets to the user's designated channel. Additionally, a notification 
        entry is created in the database, so that the user can track notifications within the app.

    Parameters:
        request (Request): User request handled by the framework.
    Returns:
        Response: A JSON object indicating the status of the operation.
    """
    if request.method == 'POST':
        data = request.data
        # validating client data
        validated_data = await async_serializer(AppNotificationSerializer, data)
        if not isinstance(validated_data, dict):
            return Response(data=validated_data.errors, status=status.HTTP_400_BAD_REQUEST)
        blog        = validated_data['blog']
        sender      = validated_data['sender']
        receiver    = validated_data['receiver']
        text        = validated_data['text']
        notif_type  = validated_data['type']
        # saving entry in the database
        await AppNotification.objects.acreate(
            blog=blog,
            sender=sender,
            receiver=receiver,
            text=text,
            type=notif_type,
            timestamp=timezone.now()
        )
        # sending message to the channel
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f'notification_channel_{receiver.pk}',
            {
                'type': 'ws.message',
                'message': {
                    'blog': blog.pk,
                    'sender': sender.pk,
                    'receiver': receiver.pk,
                    'text': text,
                    'type': notif_type
                }
            }
        )
        return Response(data=ApiResponse.NOTIF_POST_SUCCESS, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
async def user_notifications(request: Request) -> Response:
    """
    API view to retrieve a the authenticated user's notifications. 
        Pagination with 10 items per page has been implemented.

    Parameters:
        request: User request handled by the framework.
    Returns:
        Response: A JSON object containing all the notifications.
    """
    if request.method == 'GET':
        try:
            receiver_id = request.data['user']
        except KeyError as e:
            return Response(data=ApiResponse.KEY_ERROR(e), status=status.HTTP_400_BAD_REQUEST)
        try:
            notifications = AppNotification.objects.filter(receiver_id=receiver_id)
        except AppNotification.DoesNotExist:
            return Response(ApiResponse.NOT_FOUND, status=status.HTTP_404_NOT_FOUND)
        paginator = AsyncPaginator(items_per_page=10)
        return await paginator.response(AppNotificationSerializer, notifications, request)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)