from uuid import UUID

from fastapi import HTTPException
from fastapi.websockets import WebSocket, WebSocketDisconnect
from pydantic import UUID4, ValidationError

from main.utils.exception_handling import SafeAPIRouter
from main.utils.logger import log
from .ws_schema import WsResponse as response
from .ws_service import ws_service

ws_notification_router = SafeAPIRouter()


@ws_notification_router.websocket("/account/{id}/notifications")
async def websocket_endpoint(websocket: WebSocket, id: UUID4):
    user_id = id
    user = None

    try:
        # Validate user before accepting connection
        from user_info.use_cases import user_info_service
        user = await user_info_service.repo.get_by_id(user_id)
        if not user:
            await websocket.close(code=1008, reason="User not found")
            log.warning(f"WebSocket connection denied. User {user_id} not found")
            return

    except HTTPException:
        await websocket.close(code=1011, reason="User not found")
        return
    except Exception as e:
        await websocket.close(code=1011, reason="Server error")
        log.error(f"Unexpected error during user lookup for {user_id}: {e}")
        return

    # Accept connection only after validation
    await websocket.accept()

    try:
        await ws_service.connect(user_id=user_id, websocket=websocket)
        log.info(f"WebSocket connection established for user {user_id}")

        while True:
            try:
                data = await websocket.receive_json()

                # Validate payload structure
                if not isinstance(data, dict) or "action" not in data:
                    await websocket.send_json(response.fail("Invalid payload format"))
                    continue

                # expected payload: {'action': 'read', 'ids': [<UUID4 string>]}
                # process action
                match data.get("action"):
                    case "read":
                        notification_ids = data.get('ids')
                        if not notification_ids:
                            await websocket.send_json(response.fail("'ids' are required"))
                            continue
                        try:
                            ids = [UUID(str(id)) for id in notification_ids]  # Validate UUID format
                            from notification.use_cases.notification_dispatch import notification_dispatch_service
                            await notification_dispatch_service.bulk_mark_as_read(notification_ids=ids)
                            await websocket.send_json(response.success(count=len(notification_ids)))

                        except (ValueError, ValidationError):
                            await websocket.send_json(response.fail("Invalid 'ids' format"))
                        except HTTPException as e:
                            await websocket.send_json(response.fail(e.detail))
                        except:
                            log.exception(f"Failed to send notification for user {user_id}")
                            await websocket.send_json(response.fail("Internal Server Error"))

                    case _:
                        log.warning(f"Received invalid WebSocket action from user {user_id}: {data}")
                        await websocket.send_json(response.fail(f"Invalid action: {data.get('action')}"))

            except WebSocketDisconnect:
                raise
            except ValidationError as e:
                await websocket.send_json(response.fail("Invalid JSON format"))
                log.warning(f"JSON validation error for user {user_id}: {e}")
            except:
                log.exception(f"Error processing WebSocket message for user {user_id}")
                await websocket.send_json(response.fail("Processing error"))

    except WebSocketDisconnect:
        pass
    except:
        log.exception(f"WebSocket connection error for user {user_id}")
    finally:
        # Ensure cleanup happens regardless of how we exit
        if user_id:
            try:
                await ws_service.disconnect(user_id=user_id)
                log.info(f"WebSocket disconnected for user {user_id}")
            except Exception as e:
                log.exception(f"Error during WebSocket cleanup for user {user_id}: {e}")
