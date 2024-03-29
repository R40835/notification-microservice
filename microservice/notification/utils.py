from asgiref.sync import sync_to_async
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import ModelSerializer
from adrf.requests import Request
from rest_framework.response import Response
from django.db.models.query import QuerySet


class ApiResponse:
    """    
    Utility class providing predefined responses for API endpoints.
    """
    NOTIF_POST_SUCCESS  = {"Response": "User notified successfully."}
    NOT_FOUND           = {"Response": "Item requested not found."}
    KEY_ERROR           = staticmethod(lambda e: {"Error": f"Missing key: {e}"})


class AsyncPaginator:
    """
    Asynchronous generic paginator to support pagination in the asynchronous views.
    """
    
    def __init__(self, items_per_page: int):
        """
        The constructor instantiates a paginator and sets the number of items per page.

        Parameters:
            items_per_page (int): number of items (instances) per page. 
        """
        self.paginator = PageNumberPagination()
        self.paginator.page_size = items_per_page

    @sync_to_async
    def response(self, Serializer: ModelSerializer, query_set: QuerySet, request: Request) -> Response:
        """
        This method returns the paginated response with serialized data. Though pagination 
            does not provide asynchronous support, This sync method is converted to an async method 
            using the sync_to_async decorator provided by the asgiref module. This is essential as 
            the api views are asynchronous.

        Parameters:
            Serializer (ModelSerializer): Built-in synchronous serializer.
            query_set (QuerySet): The query set of the Model corresponding to the Serializer.
            request (Request): User request handled by the framework.
        Returns:
            Response: A JSON object containing paginated instances.
        """
        result_page = self.paginator.paginate_queryset(query_set, request)
        serializer = Serializer(result_page, many=True)
        return self.paginator.get_paginated_response(serializer.data)
    

@sync_to_async
def async_serializer(Serializer: ModelSerializer, data: dict) -> dict | ModelSerializer:
    """
    Validates the serialization of data sent in the client request. This function is 
        converted to an asynchronous function to ensure compatibility with asynchronous views.

    Parameters:
        Serializer (ModelSerializer): Built-in synchronous serializer.
        data (dict): The serialized payload sent by the client.
    Returns:
        dict: The validated data if formatted correctly.
        ModelSerializer: The serializer if the data isn't valid.
    """
    serializer = Serializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data
    return serializer