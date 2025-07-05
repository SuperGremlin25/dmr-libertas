"""
DMR Serial Handler

This module handles low-level serial communication with DMR radios.
Supports both real hardware and mock mode for development.
"""
import asyncio
import json
import logging
import os
import random
import time
from typing import Dict, Optional, Any, Union

import serial
import serial_asyncio
from serial.tools import list_ports

logger = logging.getLogger(__name__)

# Constants
DEFAULT_BAUDRATE = 460800
SERIAL_TIMEOUT = 1.0
READ_INTERVAL = 0.1  # seconds

# Known radio vendor IDs
RADIO_VENDOR_IDS = {
    "1A86": "Anytone",  # CH340/CH341 USB-Serial
    "067B": "Prolific",  # PL2303 USB-Serial
    "0403": "FTDI",     # FTDI USB-Serial
    "10C4": "Silicon Labs"  # CP210x USB-Serial
}

class DMRSerialHandler:
    """Handles serial communication with DMR radios."""
    
    def __init__(self):
        self.port = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
        self.baudrate = DEFAULT_BAUDRATE
        self.timeout = SERIAL_TIMEOUT
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        
        # Connection state
        self.connected = False
        self.serial_conn = None
        self.reader = None
        self.writer = None
        self._read_task = None
        self._stop_event = asyncio.Event()
        
        # Radio state
        self.radio_model = None
        self.firmware_version = None
        self.rssi = 0
        self.battery_level = 0
        self.gps_data = None
        self.last_transmission = None
        
        # Mock data
        self._mock_data = {
            "radio_model": "Anytone AT-D578UVIII Plus",
            "firmware": "V1.2.3",
            "rssi": 75,
            "battery": 85,
            "gps": {
                "lat": 37.7749 + random.uniform(-0.1, 0.1),
                "lon": -122.4194 + random.uniform(-0.1, 0.1),
                "alt": 10.5,
                "sats": 8,
                "timestamp": time.time()
            },
            "last_heard": {
                "caller_id": "W1ABC",
                "talkgroup": 91,
                "time": time.time() - 60,
                "rssi": 80,
                "location": "San Francisco, CA"
            }
        }
    
    async def connect(self) -> bool:
        """Establish connection to the radio."""
        if self.connected:
            return True
            
        if self.mock_mode:
            logger.info("Running in MOCK MODE - No real radio connection")
            self.connected = True
            self.radio_model = self._mock_data["radio_model"]
            self.firmware_version = self._mock_data["firmware"]
            self._stop_event.clear()
            self._read_task = asyncio.create_task(self._mock_read_loop())
            return True
            
        try:
            # Try to auto-detect radio if port is not specified
            if not self.port or self.port == "auto":
                self.port = self._detect_radio_port()
                
            if not self.port:
                logger.error("No radio detected. Please connect a radio or use MOCK_MODE=true")
                return False
                
            logger.info(f"Connecting to {self.port} at {self.baudrate} baud...")
            
            # Use asyncio serial library for non-blocking I/O
            self.reader, self.writer = await serial_asyncio.open_serial_connection(
                url=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout
            )
            
            self.connected = True
            self._stop_event.clear()
            self._read_task = asyncio.create_task(self._read_loop())
            
            # Initialize radio
            await self._initialize_radio()
            
            logger.info(f"Connected to {self.radio_model} (FW: {self.firmware_version})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to radio: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Close the serial connection."""
        if not self.connected:
            return
            
        logger.info("Disconnecting from radio...")
        
        # Signal read loop to stop
        self._stop_event.set()
        
        # Cancel read task
        if self._read_task:
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass
            self._read_task = None
        
        # Close serial connection
        if self.writer:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception as e:
                logger.error(f"Error closing serial connection: {e}")
            
        self.reader = None
        self.writer = None
        self.connected = False
        logger.info("Disconnected from radio")
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        """Read and parse data from the radio."""
        if not self.connected:
            return None
            
        # In mock mode, return mock data
        if self.mock_mode:
            return self._generate_mock_data()
            
        # Real implementation would read from serial and parse DMR data
        # This is a simplified example
        try:
            if self.reader and not self.reader.at_eof():
                data = await self.reader.read(1024)
                if data:
                    # Parse DMR data here
                    return self._parse_dmr_data(data)
        except Exception as e:
            logger.error(f"Error reading from radio: {e}")
            await self.disconnect()
            
        return None
    
    async def send_message(self, message: str) -> bool:
        """Send a message to the radio."""
        if not self.connected:
            return False
            
        if self.mock_mode:
            logger.info(f"[MOCK] Sending message: {message}")
            return True
            
        try:
            if self.writer:
                self.writer.write(message.encode() + b"\r\n")
                await self.writer.drain()
                return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            await self.disconnect()
            
        return False
    
    async def _read_loop(self):
        """Background task to continuously read from the radio."""
        while not self._stop_event.is_set():
            try:
                data = await self.read_data()
                if data:
                    # Process incoming data
                    self._update_radio_state(data)
            except Exception as e:
                logger.error(f"Error in read loop: {e}")
                await asyncio.sleep(1)  # Prevent tight loop on errors
            
            await asyncio.sleep(READ_INTERVAL)
    
    async def _mock_read_loop(self):
        """Mock version of the read loop for testing."""
        while not self._stop_event.is_set():
            try:
                data = self._generate_mock_data()
                if data:
                    self._update_radio_state(data)
            except Exception as e:
                logger.error(f"Error in mock read loop: {e}")
                
            await asyncio.sleep(READ_INTERVAL * 5)  # Less frequent updates in mock mode
    
    def _generate_mock_data(self) -> Dict[str, Any]:
        """Generate realistic-looking mock radio data."""
        now = time.time()
        
        # Slightly modify values to simulate changes
        self._mock_data["rssi"] = max(0, min(100, self._mock_data["rssi"] + random.randint(-5, 5)))
        self._mock_data["battery"] = max(0, min(100, self._mock_data["battery"] - 0.1))
        
        # Update GPS position slightly
        self._mock_data["gps"]["lat"] += random.uniform(-0.001, 0.001)
        self._mock_data["gps"]["lon"] += random.uniform(-0.001, 0.001)
        self._mock_data["gps"]["timestamp"] = now
        
        # Occasionally simulate a transmission
        if random.random() < 0.05:  # 5% chance per read
            self._mock_data["last_heard"] = {
                "caller_id": f"W{random.randint(1,9)}{chr(random.randint(65, 90))}{random.randint(1,9)}{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}",
                "talkgroup": random.choice([91, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 2, 9, 90, 92, 93, 94, 95, 96, 97, 98, 99]),
                "time": now,
                "rssi": random.randint(50, 100),
                "location": random.choice(["San Francisco, CA", "New York, NY", "Chicago, IL", "Denver, CO", "Dallas, TX"])
            }
        
        return self._mock_data.copy()
    
    def _update_radio_state(self, data: Dict[str, Any]):
        """Update internal radio state from received data."""
        if "rssi" in data:
            self.rssi = data["rssi"]
        if "battery" in data:
            self.battery_level = data["battery"]
        if "gps" in data:
            self.gps_data = data["gps"]
        if "last_heard" in data:
            self.last_transmission = data["last_heard"]
    
    def _parse_dmr_data(self, data: bytes) -> Dict[str, Any]:
        """Parse raw DMR data into a structured format."""
        # This is a simplified example - real implementation would parse actual DMR protocol
        try:
            # Try to decode as JSON (some radios support this)
            decoded = data.decode().strip()
            if decoded.startswith('{') and decoded.endswith('}'):
                return json.loads(decoded)
                
            # Otherwise, parse as raw data
            return {
                "raw": data.hex(),
                "timestamp": time.time(),
                "rssi": self.rssi,
                "battery": self.battery_level
            }
        except Exception as e:
            logger.error(f"Error parsing DMR data: {e}")
            return {"error": str(e), "raw": data.hex()}
    
    def _detect_radio_port(self) -> Optional[str]:
        """Try to automatically detect the radio's serial port."""
        try:
            ports = list_ports.comports()
            for port in ports:
                # Check if this looks like a DMR radio
                if port.vid and port.pid:
                    vid = f"{port.vid:04X}"
                    if vid in RADIO_VENDOR_IDS:
                        logger.info(f"Detected {RADIO_VENDOR_IDS[vid]} radio on {port.device}")
                        return port.device
            
            logger.warning("No radio detected on any serial port")
            return None
            
        except Exception as e:
            logger.error(f"Error detecting radio port: {e}")
            return None
    
    async def _initialize_radio(self):
        """Initialize the radio and get its information."""
        if self.mock_mode:
            return
            
        # Send initialization commands and parse responses
        # This is radio-specific and would need to be customized
        try:
            # Example: Get radio model
            await self.send_message("AT+DMOCONNECT\r\n")
            await asyncio.sleep(0.1)
            
            # Example: Get firmware version
            await self.send_message("AT+VERSION\r\n")
            
            # Set up callbacks for incoming data
            # This would be implemented based on the radio's protocol
            
        except Exception as e:
            logger.error(f"Error initializing radio: {e}")
            await self.disconnect()
            raise