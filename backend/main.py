"""
DMR Libertas - Main FastAPI Application

This module initializes the FastAPI application, sets up WebSocket connections,
and defines the API endpoints for the DMR Libertas platform.
"""
import asyncio
import json
import logging
import os
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from serial_handler import DMRSerialHandler
from websocket_manager import ConnectionManager
from audio_handler import AudioHandler

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DMR Libertas API",
    description="Open Source DMR Radio Driver & AI Integration Platform",
    version="0.1.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
serial_handler = DMRSerialHandler()
ws_manager = ConnectionManager()
audio_handler = AudioHandler()

# Models
class RadioStatus(BaseModel):
    """Current status of the DMR radio."""
    connected: bool = Field(..., description="Whether the radio is connected")
    model: Optional[str] = Field(None, description="Radio model")
    firmware: Optional[str] = Field(None, description="Firmware version")
    rssi: Optional[int] = Field(None, description="Signal strength (0-100)")
    battery: Optional[int] = Field(None, description="Battery level (0-100)")
    gps: Optional[dict] = Field(None, description="GPS coordinates if available")
    last_heard: Optional[dict] = Field(None, description="Last transmission heard")


# Background task for monitoring serial data
async def monitor_serial():
    """Background task to monitor serial data and broadcast via WebSockets."""
    while True:
        try:
            if serial_handler.connected:
                data = await serial_handler.read_data()
                if data:
                    # Broadcast to all connected WebSocket clients
                    await ws_manager.broadcast_json({
                        "type": "radio_update",
                        "data": data
                    })
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in serial monitor: {e}")
            await asyncio.sleep(1)


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize components on application startup."""
    logger.info("Starting DMR Libertas...")
    
    # Start serial handler
    await serial_handler.connect()
    
    # Start background tasks
    asyncio.create_task(monitor_serial())
    
    logger.info("DMR Libertas started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down DMR Libertas...")
    await serial_handler.disconnect()
    logger.info("Shutdown complete")


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# REST API endpoints
@app.get("/api/status", response_model=RadioStatus)
async def get_radio_status():
    """Get current radio status."""
    return {
        "connected": serial_handler.connected,
        "model": serial_handler.radio_model,
        "firmware": serial_handler.firmware_version,
        "rssi": serial_handler.rssi,
        "battery": serial_handler.battery_level,
        "gps": serial_handler.gps_data,
        "last_heard": serial_handler.last_transmission
    }


@app.post("/api/transmit")
async def transmit_message(message: str):
    """Transmit a message via the radio."""
    if not serial_handler.connected:
        raise HTTPException(status_code=503, detail="Radio not connected")
    
    try:
        await serial_handler.send_message(message)
        return {"status": "success", "message": "Message transmitted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Audio handling endpoints
@app.post("/api/audio/start")
async def start_audio_capture():
    """Start capturing and processing audio."""
    try:
        await audio_handler.start()
        return {"status": "success", "message": "Audio capture started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/audio/stop")
async def stop_audio_capture():
    """Stop audio capture."""
    try:
        await audio_handler.stop()
        return {"status": "success", "message": "Audio capture stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "radio_connected": serial_handler.connected,
        "ws_clients": len(ws_manager.active_connections)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)