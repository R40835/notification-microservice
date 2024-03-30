import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone

from .models import AppNotification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        """
        Connects the client to the websocket.
        """
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f"notification_channel_{self.user_id}"
        self.connection_denied_code = 4000

        if self.scope['user_auth']:

            await self.channel_layer.group_add(
                self.room_group_name, 
                self.channel_name
            )

            await self.accept()
        else:
            await self.close(code=self.connection_denied_code)

    async def disconnect(self, close_code: int) -> None:
        """
        Disconnects the client from the websocket.

        Parameters:
            close_code (int): Websocket connection close code.
        """
        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name
        )

    async def send_notification(self, event: dict) -> None:
        """
        Sends a message to the notified user's channel. It receives the validated data
            to create a new notification instance, and sends the notification message 
            to the clients through their associated WebSockets.
        
        Parameters:
            event (dict): Websocket event containing the validated data dictionary. 
        """
        validated_data: dict = event["validated_data"]

        validated_data['timestamp'] = timezone.now()
        validated_data['text'] = await self.generate_message(
            sender_name=validated_data['sender_name'],
            notification_type=validated_data['type']
        )
        
        validated_data.pop('sender_name')

        await AppNotification.objects.acreate(**validated_data)

        await self.send(
            text_data=json.dumps(
                {
                    "blog_id": validated_data['blog_id'],
                    "message": validated_data['text'],
                    "type": validated_data["type"]
                }
            )
        )

    @staticmethod
    async def generate_message(sender_name: str, notification_type: str) -> str:
        """
        Utility method to generate notification messages based on the notification type. 

        Parameters:
            sender_name (str): The full name of the user sending the notification.
            notification_type (str): The type of notification sent.
        Returns:
            str: The notification message sent to the frontend.
        """
        notification_type = notification_type.lower()

        if notification_type == 'like':
            return f'{sender_name} liked your blog.'
        elif notification_type == 'comment':
            return f'{sender_name} commented on your blog.'
        elif notification_type == 'blog-approval':
            return f'{sender_name} approved your blog.'
        elif notification_type == 'blog-rejection':
            return f'{sender_name} rejected your blog.'
        elif notification_type == 'feedback':
            return f'{sender_name} has given you blog feedback.'
        

class EventConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        """
        Connects the client to the websocket.
        """
        self.room_group_name = "event_channel"
        self.connection_denied_code = 4000

        if self.scope['user_auth']:

            await self.channel_layer.group_add(
                self.room_group_name, 
                self.channel_name
            )

            await self.accept()
        else:
            await self.close(code=self.connection_denied_code)

    async def disconnect(self, close_code: int) -> None:
        """
        Disconnects the client from the websocket.

        Parameters:
            close_code (int): Websocket connection close code.
        """
        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name
        )

    async def send_event(self, event: dict) -> None:
        """
        Sends a message to the notified user's channel. The method customises
            this message by adding the first name of the user associated with 
            the current WebSocket connection before sending it to the client.
        
        Parameters:
            event (dict): Websocket event containing the message. 
        """
        message: str = event["message"]
        
        event_message = "Hey " + self.scope['user_first_name'] + ". " + message.capitalize()

        await self.send(
            text_data=json.dumps(
                {
                    "message": event_message,
                }
            )
        )