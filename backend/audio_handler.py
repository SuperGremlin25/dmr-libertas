"""
Audio Handler for DMR Libertas

This module handles audio capture, processing, and AI integration for DMR radio audio.
Supports both real audio devices and mock mode for development.
"""
import asyncio
import logging
import os
import wave
import numpy as np
from dataclasses import dataclass
from typing import Optional, Callable, Any, Dict

# Optional imports for audio processing
try:
    import sounddevice as sd
    import soundfile as sf
    import webrtcvad
    AUDIO_DEPS_AVAILABLE = True
except ImportError:
    AUDIO_DEPS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Audio configuration
SAMPLE_RATE = 16000  # Hz
CHANNELS = 1         # Mono audio
CHUNK_SIZE = 480     # 30ms at 16kHz
SAMPLE_WIDTH = 2     # 16-bit audio
VAD_MODE = 3         # Aggressiveness of voice activity detection (0-3)

# Audio processing parameters
SILENCE_THRESHOLD = 0.01  # RMS threshold for silence detection
MIN_VOICE_ACTIVITY = 0.5  # Minimum voice activity ratio to consider as speech

@dataclass
class AudioBuffer:
    """Circular buffer for audio data."""
    data: bytearray
    size: int
    write_pos: int = 0
    read_pos: int = 0
    
    @classmethod
    def from_seconds(cls, seconds: int, sample_rate: int = SAMPLE_RATE, 
                    channels: int = CHANNELS, sample_width: int = SAMPLE_WIDTH):
        """Create a buffer that can hold the specified number of seconds of audio."""
        size = seconds * sample_rate * channels * sample_width
        return cls(bytearray(size), size)
    
    def write(self, data: bytes) -> int:
        """Write data to the buffer, overwriting old data if necessary."""
        data_len = len(data)
        if data_len >= self.size:
            # If data is larger than buffer, only keep the end
            data = data[-self.size:]
            self.write_pos = 0
            self.data[:] = data
            return data_len
            
        remaining = self.size - self.write_pos
        if data_len <= remaining:
            # Data fits in remaining space
            self.data[self.write_pos:self.write_pos + data_len] = data
        else:
            # Wrap around to beginning of buffer
            self.data[self.write_pos:] = data[:remaining]
            self.data[:data_len - remaining] = data[remaining:]
            
        self.write_pos = (self.write_pos + data_len) % self.size
        self.read_pos = max(0, self.write_pos - self.size // 2)  # Keep some history
        return data_len
    
    def read(self, size: int) -> bytes:
        """Read up to size bytes from the buffer."""
        available = (self.write_pos - self.read_pos) % self.size
        if available == 0:
            return b''
            
        read_size = min(size, available)
        if self.read_pos + read_size <= self.size:
            # Read doesn't wrap around
            result = bytes(self.data[self.read_pos:self.read_pos + read_size])
        else:
            # Read wraps around to beginning of buffer
            first_part = self.data[self.read_pos:]
            second_part = self.data[:read_size - len(first_part)]
            result = bytes(first_part + second_part)
            
        self.read_pos = (self.read_pos + read_size) % self.size
        return result


class AudioHandler:
    """Handles audio capture, processing, and AI integration."""
    
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.channels = CHANNELS
        self.chunk_size = CHUNK_SIZE
        self.sample_width = SAMPLE_WIDTH
        self.mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
        
        # Audio state
        self.is_recording = False
        self.stream = None
        self.audio_buffer = AudioBuffer.from_seconds(30)  # 30-second buffer
        self.vad = None
        self.current_transcription = ""
        self.audio_processor = None
        
        # Initialize VAD if available
        if AUDIO_DEPS_AVAILABLE and not self.mock_mode:
            try:
                self.vad = webrtcvad.Vad()
                self.vad.set_mode(VAD_MODE)
            except Exception as e:
                logger.warning(f"Failed to initialize VAD: {e}")
    
    async def start(self) -> bool:
        """Start audio capture and processing."""
        if self.is_recording:
            return True
            
        if self.mock_mode:
            logger.info("Running in MOCK MODE - No real audio capture")
            self.is_recording = True
            return True
            
        if not AUDIO_DEPS_AVAILABLE:
            logger.error("Audio dependencies not available. Install with: pip install sounddevice soundfile webrtcvad")
            return False
            
        try:
            # Initialize audio stream
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16',
                blocksize=self.chunk_size,
                callback=self._audio_callback
            )
            
            self.stream.start()
            self.is_recording = True
            logger.info("Audio capture started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start audio capture: {e}")
            self.is_recording = False
            return False
    
    async def stop(self) -> None:
        """Stop audio capture and processing."""
        if not self.is_recording:
            return
            
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                logger.error(f"Error stopping audio stream: {e}")
            finally:
                self.stream = None
                
        self.is_recording = False
        logger.info("Audio capture stopped")
    
    def _audio_callback(self, indata: np.ndarray, frames: int, time_info: dict, status: int) -> None:
        """Callback for audio stream data."""
        if status:
            logger.warning(f"Audio stream status: {status}")
            
        # Convert to bytes and add to buffer
        audio_data = indata.tobytes()
        self.audio_buffer.write(audio_data)
        
        # Process audio in background
        asyncio.create_task(self._process_audio(audio_data))
    
    async def _process_audio(self, audio_data: bytes) -> None:
        """Process audio data for voice activity and transcription."""
        try:
            # Convert to numpy array for processing
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Check for voice activity
            is_speech = self._detect_voice_activity(audio_array)
            
            if is_speech:
                # Process speech
                await self._process_speech(audio_array)
                
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
    
    def _detect_voice_activity(self, audio_data: np.ndarray) -> bool:
        """Detect if audio contains voice activity."""
        if self.vad is None:
            # Fallback to simple RMS-based detection
            rms = np.sqrt(np.mean(np.square(audio_data.astype(np.float32))))
            return rms > SILENCE_THRESHOLD * 32768  # Scale to 16-bit range
            
        # Use WebRTC VAD if available
        try:
            # Convert to 16kHz, 1 channel if needed
            if len(audio_data.shape) > 1:
                audio_data = audio_data[:, 0]  # Take first channel if stereo
                
            # Resample to 16kHz if needed
            if len(audio_data) != 160:  # 10ms at 16kHz
                # Simple decimation for demo - use proper resampling in production
                audio_data = audio_data[::2] if len(audio_data) > 160 else audio_data
                
            # Convert to bytes for VAD
            audio_bytes = audio_data.astype(np.int16).tobytes()
            
            # Check for voice activity
            return self.vad.is_speech(audio_bytes, 16000)  # 16kHz sample rate
            
        except Exception as e:
            logger.warning(f"VAD error: {e}")
            return True  # Default to processing if VAD fails
    
    async def _process_speech(self, audio_data: np.ndarray) -> None:
        """Process speech audio (transcription, etc.)."""
        # This is where you would integrate with Whisper or other ASR
        # For now, just log that we detected speech
        logger.debug("Speech detected in audio")
        
        # In a real implementation, you would:
        # 1. Buffer audio until end of speech is detected
        # 2. Send to Whisper for transcription
        # 3. Process the transcription (translate, extract keywords, etc.)
        # 4. Send results via WebSocket to the frontend
    
    async def play_audio(self, audio_data: bytes, sample_rate: int = None) -> bool:
        """Play audio data through the default output device."""
        if not AUDIO_DEPS_AVAILABLE or self.mock_mode:
            logger.warning("Audio playback not available in mock mode")
            return False
            
        try:
            sample_rate = sample_rate or self.sample_rate
            
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Play asynchronously
            sd.play(audio_array, samplerate=sample_rate)
            sd.wait()  # Wait for playback to finish
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
    
    async def save_audio(self, file_path: str, audio_data: bytes = None, 
                        sample_rate: int = None, format: str = 'wav') -> bool:
        """Save audio data to a file."""
        if not AUDIO_DEPS_AVAILABLE:
            return False
            
        try:
            sample_rate = sample_rate or self.sample_rate
            audio_array = np.frombuffer(audio_data or self.audio_buffer.read(-1), dtype=np.int16)
            
            # Reshape if stereo
            if len(audio_array.shape) == 1 and self.channels > 1:
                audio_array = audio_array.reshape(-1, self.channels)
                
            sf.write(file_path, audio_array, sample_rate, format=format)
            return True
            
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            return False
    
    def get_audio_level(self, window_ms: int = 100) -> float:
        """Get the current audio level in dBFS."""
        if not self.is_recording or self.mock_mode:
            return -100.0  # Silence in dBFS
            
        try:
            # Calculate RMS of the last window_ms of audio
            window_samples = (window_ms * self.sample_rate) // 1000
            audio_data = self.audio_buffer.read(window_samples * self.sample_width * self.channels)
            
            if not audio_data:
                return -100.0
                
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            rms = np.sqrt(np.mean(np.square(audio_array.astype(np.float32))))
            
            # Convert to dBFS
            if rms < 1e-6:  # Avoid log(0)
                return -100.0
                
            dbfs = 20 * np.log10(rms / 32768.0)  # 16-bit full scale
            return max(-100.0, min(0.0, dbfs))  # Clamp to -100..0 dBFS
            
        except Exception as e:
            logger.error(f"Error getting audio level: {e}")
            return -100.0