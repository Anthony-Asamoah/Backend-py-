from typing import List, Optional

from fastapi import WebSocket
from pydantic import UUID4


class CRUDWSConnection:
    def __init__(self):
        self.connections: dict[str, List[WebSocket]] = {}

    async def create(self, user_id: UUID4, websocket: WebSocket) -> UUID4:
        connected_user = await self.list_user_connections(user_id=user_id)

        if not connected_user:
            self.connections[str(user_id)] = [websocket]
        else:
            self.connections[str(user_id)].append(websocket)

        return user_id

    async def remove(self, id: UUID4) -> Optional[UUID4]:
        return self.connections.pop(str(id), None)

    async def list_user_connections(self, user_id: UUID4) -> List[WebSocket]:
        return self.connections.get(str(user_id), [])

    async def list_connected_users(self) -> List[str]:
        return list(self.connections.keys())


ws_actions = CRUDWSConnection()
