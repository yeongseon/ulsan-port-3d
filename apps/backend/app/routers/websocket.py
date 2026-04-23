import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.services.pubsub import RedisPubSubService

router = APIRouter(tags=["websocket"])


async def _stream_events(websocket: WebSocket) -> None:
    await websocket.accept()
    pubsub_service = RedisPubSubService()
    try:
        pubsub = await pubsub_service.subscribe()
    except Exception:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return

    async def forward_messages() -> None:
        async for message in pubsub_service.iter_messages(pubsub):
            await websocket.send_json(message)

    async def drain_client() -> None:
        while True:
            _ = await websocket.receive_text()

    sender = asyncio.create_task(forward_messages())
    receiver = asyncio.create_task(drain_client())
    try:
        done, pending = await asyncio.wait({sender, receiver}, return_when=asyncio.FIRST_EXCEPTION)
        for task in done:
            task.result()
        for task in pending:
            _ = task.cancel()
            _ = await asyncio.gather(task, return_exceptions=True)
    except WebSocketDisconnect:
        _ = sender.cancel()
        _ = receiver.cancel()
        _ = await asyncio.gather(sender, receiver, return_exceptions=True)
    finally:
        await pubsub_service.close_pubsub(pubsub)


@router.websocket("/ws/live")
async def websocket_live(websocket: WebSocket) -> None:
    await _stream_events(websocket)


@router.websocket("/ws/events")
async def websocket_events(websocket: WebSocket) -> None:
    await _stream_events(websocket)
