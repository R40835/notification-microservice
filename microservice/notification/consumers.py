import json

from channels.generic.websocket import AsyncWebsocketConsumer


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

        await self.close(code=close_code)

    async def ws_message(self, event: dict) -> None:
        """
        Sends a message to the notified user's channel.
        
        Parameters:
            event (dict): Websocket event containing the message to send. 
        """
        message = event["message"]

        await self.send(
            text_data=json.dumps(
                {
                    "message": message
                }
            )
        )