import asyncio
from typing import Optional

from fastapi import WebSocket
from pydantic import UUID4

from main.utils.logger import log
from notification.channels.websocket.ws_repository import ws_actions
from notification.channels.websocket.ws_schema import WsResponse
from notification.models import NotificationDispatch
from notification.schemas.notification_dispatch import NotificationChannel, NotificationStatus


class WSService:
    def __init__(self):
        self.repo = ws_actions

    async def connect(self, user_id: UUID4, websocket: object):
        # save connection
        await self.repo.create(user_id=user_id, websocket=websocket)

        # send unread notifications
        from notification.use_cases.notification_dispatch import notification_dispatch_service

        user_connections = await self.repo.list_user_connections(user_id=user_id)
        unread_notifications = await notification_dispatch_service.read(
            user_id=user_id,
            channels=[NotificationChannel.WEBSOCKET],
            status=[
                NotificationStatus.FAILED,
                NotificationStatus.PENDING,
                NotificationStatus.SENT,
                NotificationStatus.DELIVERED
            ],
        )
        await asyncio.gather(*[self.send_notification(
            user_id=user_id,
            user_connections=user_connections,
            dispatch=notification
        ) for notification in unread_notifications])

        # mark sent notifications as delivered
        await notification_dispatch_service.bulk_mark_as_delivered(
            notification_ids=[n.id for n in unread_notifications],
            notification_objs=unread_notifications
        )

    async def disconnect(self, user_id: UUID4):
        return await self.repo.remove(id=user_id)

    async def list_user_connections(self, user_id: UUID4):
        return await self.repo.list_user_connections(user_id=user_id)

    async def list_connected_users(self):
        return await self.repo.list_connected_users()

    async def send_notification(
            self,
            user_id: UUID4,
            dispatch: NotificationDispatch,
            user_connections: list[WebSocket] = None
    ) -> Optional[UUID4]:
        if not user_connections:
            user_connections = await self.list_user_connections(user_id=user_id)

        if not user_connections: raise Exception(
            "User not connected."
        )
        if not isinstance(dispatch, NotificationDispatch): raise Exception(
            f"invalid payload format. expected dispatch obj got {type(dispatch)}"
        )
        if not dispatch.channel == NotificationChannel.WEBSOCKET.name: raise Exception(
            f"invalid payload format. expected channel {NotificationChannel.WEBSOCKET.name} got {dispatch.channel}"
        )

        await asyncio.gather(*[conn.send_json(WsResponse.data(
            id=dispatch.id,
            subject=dispatch.subject,
            heading=dispatch.heading,
            content=dispatch.content,
            status=dispatch.status,
            elapsed_time=dispatch.notification.elapsed_time
        )) for conn in user_connections])

        log.debug("Notification successfully sent via websocket")
        return user_id


ws_service = WSService()
