import json
from channels.generic.websocket import AsyncWebsocketConsumer

# Track users per room: {room_code: {channel_name: username}}
room_users = {}


class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'room_{self.room_code}'
        self.username = 'Unknown'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Notify others this user left
        if self.room_code in room_users and self.channel_name in room_users[self.room_code]:
            username = room_users[self.room_code].pop(self.channel_name)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'username': username,
                    'channel': self.channel_name,
                }
            )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')

        if msg_type == 'join':
            self.username = data.get('username', 'Guest')
            if self.room_code not in room_users:
                room_users[self.room_code] = {}
            
            # Send existing users to the new joiner
            existing = [
                {'channel': ch, 'username': u}
                for ch, u in room_users[self.room_code].items()
            ]
            await self.send(json.dumps({
                'type': 'existing_users',
                'users': existing,
            }))

            # Register this user
            room_users[self.room_code][self.channel_name] = self.username

            # Notify others of new user
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'username': self.username,
                    'channel': self.channel_name,
                }
            )

        elif msg_type in ('offer', 'answer', 'ice_candidate'):
            # Forward signaling messages to target
            target = data.get('target')
            await self.channel_layer.send(
                target,
                {
                    'type': 'signal_message',
                    'signal_type': msg_type,
                    'data': data.get('data'),
                    'sender': self.channel_name,
                    'username': self.username,
                }
            )

        elif msg_type == 'chat':
            # Broadcast chat message to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': data.get('message', ''),
                    'username': self.username,
                }
            )

        elif msg_type == 'toggle_media':
            # Broadcast media state change
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'media_toggle',
                    'username': self.username,
                    'channel': self.channel_name,
                    'video': data.get('video'),
                    'audio': data.get('audio'),
                }
            )

    # Group message handlers

    async def user_joined(self, event):
        await self.send(json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'channel': event['channel'],
        }))

    async def user_left(self, event):
        await self.send(json.dumps({
            'type': 'user_left',
            'username': event['username'],
            'channel': event['channel'],
        }))

    async def signal_message(self, event):
        await self.send(json.dumps({
            'type': event['signal_type'],
            'data': event['data'],
            'sender': event['sender'],
            'username': event['username'],
        }))

    async def chat_message(self, event):
        await self.send(json.dumps({
            'type': 'chat',
            'message': event['message'],
            'username': event['username'],
        }))

    async def media_toggle(self, event):
        await self.send(json.dumps({
            'type': 'media_toggle',
            'username': event['username'],
            'channel': event['channel'],
            'video': event['video'],
            'audio': event['audio'],
        }))
