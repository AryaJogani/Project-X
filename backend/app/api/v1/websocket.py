"""
WebSocket endpoints for real-time communication
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

    async def send_to_room(self, message: str, room: str):
        """Send message to specific room (future feature)"""
        # TODO: Implement room-based messaging
        await self.broadcast(message)

manager = ConnectionManager()

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time communication"""
    
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            message_type = message.get("type")
            
            if message_type == "ping":
                await manager.send_personal_message(
                    json.dumps({"type": "pong", "timestamp": message.get("timestamp")}),
                    websocket
                )
            
            elif message_type == "subscribe":
                # TODO: Implement subscription to specific events
                await manager.send_personal_message(
                    json.dumps({"type": "subscribed", "channel": message.get("channel")}),
                    websocket
                )
            
            elif message_type == "unsubscribe":
                # TODO: Implement unsubscription
                await manager.send_personal_message(
                    json.dumps({"type": "unsubscribed", "channel": message.get("channel")}),
                    websocket
                )
            
            else:
                # Echo back unknown message types
                await manager.send_personal_message(
                    json.dumps({"type": "echo", "original": message}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await manager.send_personal_message(
                json.dumps({"type": "error", "message": str(e)}),
                websocket
            )
        except:
            pass
    finally:
        manager.disconnect(websocket)

@router.websocket("/gaps")
async def gaps_websocket(websocket: WebSocket):
    """WebSocket endpoint for gap-related real-time updates"""
    
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle gap-specific messages
            message_type = message.get("type")
            
            if message_type == "analyze_document":
                document_id = message.get("document_id")
                # TODO: Implement real-time gap analysis
                await manager.send_personal_message(
                    json.dumps({
                        "type": "analysis_started",
                        "document_id": document_id,
                        "message": "Gap analysis started"
                    }),
                    websocket
                )
            
            elif message_type == "get_gap_status":
                gap_id = message.get("gap_id")
                # TODO: Implement gap status checking
                await manager.send_personal_message(
                    json.dumps({
                        "type": "gap_status",
                        "gap_id": gap_id,
                        "status": "open"
                    }),
                    websocket
                )
            
            else:
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Unknown message type"}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Gaps WebSocket error: {e}")
        try:
            await manager.send_personal_message(
                json.dumps({"type": "error", "message": str(e)}),
                websocket
            )
        except:
            pass
    finally:
        manager.disconnect(websocket)

@router.websocket("/questions")
async def questions_websocket(websocket: WebSocket):
    """WebSocket endpoint for question-related real-time updates"""
    
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle question-specific messages
            message_type = message.get("type")
            
            if message_type == "generate_questions":
                gap_id = message.get("gap_id")
                # TODO: Implement real-time question generation
                await manager.send_personal_message(
                    json.dumps({
                        "type": "generation_started",
                        "gap_id": gap_id,
                        "message": "Question generation started"
                    }),
                    websocket
                )
            
            elif message_type == "get_question_status":
                question_id = message.get("question_id")
                # TODO: Implement question status checking
                await manager.send_personal_message(
                    json.dumps({
                        "type": "question_status",
                        "question_id": question_id,
                        "status": "pending"
                    }),
                    websocket
                )
            
            else:
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Unknown message type"}),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Questions WebSocket error: {e}")
        try:
            await manager.send_personal_message(
                json.dumps({"type": "error", "message": str(e)}),
                websocket
            )
        except:
            pass
    finally:
        manager.disconnect(websocket)
