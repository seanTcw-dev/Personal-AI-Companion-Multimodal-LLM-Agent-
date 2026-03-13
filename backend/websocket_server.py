import asyncio
import websockets
import json
import logging
from typing import Callable, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PositionWebSocketServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.callback: Optional[Callable] = None
        self.dialog_callback: Optional[Callable] = None
        self.server = None
        self.connected_clients = set()
        
    def set_callback(self, callback: Callable):
        """Set the callback function to be called when position updates are received"""
        self.callback = callback
    
    def set_dialog_callback(self, callback: Callable):
        """Set the callback for dialog mask updates"""
        self.dialog_callback = callback
        
    async def handle_client(self, websocket):
        """Handle incoming WebSocket connections"""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.connected_clients)}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    # Handle dialog mask updates
                    if data.get('type') == 'dialog_mask':
                        if self.dialog_callback:
                            self.dialog_callback(
                                data.get('visible', False),
                                int(data.get('x', 0)),
                                int(data.get('y', 0)),
                                int(data.get('width', 0)),
                                int(data.get('height', 0))
                            )
                        continue
                    
                    # Validate data structure (position update)
                    if all(key in data for key in ['x', 'y', 'width', 'height']):
                        # Call the callback with position data
                        if self.callback:
                            self.callback(
                                int(data['x']),
                                int(data['y']),
                                int(data['width']),
                                int(data['height'])
                            )
                    else:
                        logger.warning(f"Invalid data format: {data}")
                        
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON: {message}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        finally:
            self.connected_clients.remove(websocket)
            logger.info(f"Client removed. Total clients: {len(self.connected_clients)}")
            
    async def start(self):
        """Start the WebSocket server"""
        self.server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port
        )
        logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
        
    async def run_forever(self):
        """Run the server indefinitely"""
        await self.start()
        await asyncio.Future()  # Run forever
        
    def stop(self):
        """Stop the WebSocket server"""
        if self.server:
            self.server.close()
            logger.info("WebSocket server stopped")
