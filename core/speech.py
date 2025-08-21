"""
ZENO Speech Handler
Manages speech-to-text and text-to-speech functionality
"""
import asyncio
import logging
import threading
import queue
from typing import Optional, Callable
import json
import os

try:
    import sounddevice as sd
    import numpy as np
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    sd = None
    np = None

try:
    import vosk
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    vosk = None

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None

from config import Config

class SpeechHandler:
    """Handles speech input/output for ZENO"""
    
    def __init__(self):
        self.config = Config
        self.logger = logging.getLogger('ZENO.Speech')
        
        # STT components
        self.vosk_model = None
        self.vosk_rec = None
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.callback_function = None
        
        # TTS components
        self.tts_engine = None
        
        # Wake word detection
        self.wake_word_detected = False
        self.wake_word_threshold = Config.WAKE_WORD_THRESHOLD
        
        # Initialize components
        self._initialize_stt()
        self._initialize_tts()
    
    def _initialize_stt(self):
        """Initialize speech-to-text components"""
        if not VOSK_AVAILABLE:
            self.logger.warning("Vosk not available - speech recognition disabled")
            return
        
        if not SOUNDDEVICE_AVAILABLE:
            self.logger.warning("sounddevice not available - audio input disabled")
            return
        
        try:
            # Try to load Vosk model
            model_path = Config.DATA_DIR / "models" / Config.STT_MODEL
            
            if not model_path.exists():
                self.logger.warning(f"Vosk model not found at {model_path}")
                self.logger.info("To enable speech recognition, download a Vosk model:")
                self.logger.info("1. Visit https://alphacephei.com/vosk/models")
                self.logger.info(f"2. Download {Config.STT_MODEL}")
                self.logger.info(f"3. Extract to {model_path}")
                return
            
            self.vosk_model = vosk.Model(str(model_path))
            self.vosk_rec = vosk.KaldiRecognizer(self.vosk_model, 16000)
            self.logger.info("Speech recognition initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing STT: {e}")
    
    def _initialize_tts(self):
        """Initialize text-to-speech components"""
        if not PYTTSX3_AVAILABLE:
            self.logger.warning("pyttsx3 not available - speech synthesis disabled")
            return
        
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS settings
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to use a female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate and volume
            self.tts_engine.setProperty('rate', 180)  # Words per minute
            self.tts_engine.setProperty('volume', 0.8)  # Volume level (0.0 to 1.0)
            
            self.logger.info("Text-to-speech initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing TTS: {e}")
    
    def is_stt_available(self) -> bool:
        """Check if speech-to-text is available"""
        return self.vosk_model is not None and self.vosk_rec is not None
    
    def is_tts_available(self) -> bool:
        """Check if text-to-speech is available"""
        return self.tts_engine is not None
    
    def start_listening(self, callback: Callable[[str], None]):
        """
        Start continuous speech recognition
        
        Args:
            callback: Function to call with recognized text
        """
        if not self.is_stt_available():
            self.logger.error("STT not available")
            return False
        
        if self.is_listening:
            self.logger.warning("Already listening")
            return False
        
        self.callback_function = callback
        self.is_listening = True
        
        # Start audio input thread
        self.audio_thread = threading.Thread(target=self._audio_input_thread)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._audio_processing_thread)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        self.logger.info("Started listening for speech")
        return True
    
    def stop_listening(self):
        """Stop continuous speech recognition"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        self.callback_function = None
        
        # Clear the audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        self.logger.info("Stopped listening for speech")
    
    def _audio_input_thread(self):
        """Thread for capturing audio input"""
        try:
            with sd.RawInputStream(
                samplerate=16000, 
                blocksize=8000, 
                dtype='int16',
                channels=1,
                callback=self._audio_callback
            ):
                while self.is_listening:
                    sd.sleep(100)
        except Exception as e:
            self.logger.error(f"Audio input error: {e}")
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for audio input"""
        if status:
            self.logger.warning(f"Audio input status: {status}")
        
        if self.is_listening:
            self.audio_queue.put(bytes(indata))
    
    def _audio_processing_thread(self):
        """Thread for processing audio data"""
        while self.is_listening:
            try:
                # Get audio data from queue
                data = self.audio_queue.get(timeout=1.0)
                
                # Process with Vosk
                if self.vosk_rec.AcceptWaveform(data):
                    result = json.loads(self.vosk_rec.Result())
                    text = result.get('text', '').strip()
                    
                    if text:
                        self._handle_recognized_text(text)
                        
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Audio processing error: {e}")
    
    def _handle_recognized_text(self, text: str):
        """Handle recognized text"""
        self.logger.debug(f"Recognized: {text}")
        
        # Check for wake word
        if self.config.WAKE_WORD.lower() in text.lower():
            self.wake_word_detected = True
            self.logger.info("Wake word detected")
        
        # Call the callback function
        if self.callback_function:
            try:
                self.callback_function(text)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")
    
    def recognize_once(self, timeout: float = 5.0) -> Optional[str]:
        """
        Recognize speech for a single utterance
        
        Args:
            timeout: Maximum time to wait for speech
            
        Returns:
            Recognized text or None
        """
        if not self.is_stt_available():
            return None
        
        recognized_text = None
        recognition_complete = threading.Event()
        
        def callback(text: str):
            nonlocal recognized_text
            recognized_text = text
            recognition_complete.set()
        
        # Start temporary listening
        old_callback = self.callback_function
        was_listening = self.is_listening
        
        if not was_listening:
            self.start_listening(callback)
        else:
            self.callback_function = callback
        
        # Wait for recognition or timeout
        recognition_complete.wait(timeout)
        
        # Restore previous state
        if not was_listening:
            self.stop_listening()
        else:
            self.callback_function = old_callback
        
        return recognized_text
    
    def speak(self, text: str, async_speech: bool = True):
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            async_speech: Whether to speak asynchronously
        """
        if not self.is_tts_available():
            self.logger.warning("TTS not available")
            return
        
        if not text.strip():
            return
        
        self.logger.debug(f"Speaking: {text[:50]}...")
        
        if async_speech:
            # Speak in a separate thread to avoid blocking
            threading.Thread(
                target=self._speak_sync, 
                args=(text,),
                daemon=True
            ).start()
        else:
            self._speak_sync(text)
    
    def _speak_sync(self, text: str):
        """Synchronous speech synthesis"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
    
    def set_voice_properties(self, rate: int = None, volume: float = None, voice_id: str = None):
        """
        Set TTS voice properties
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            voice_id: Voice ID to use
        """
        if not self.is_tts_available():
            return
        
        try:
            if rate is not None:
                self.tts_engine.setProperty('rate', rate)
            
            if volume is not None:
                self.tts_engine.setProperty('volume', max(0.0, min(1.0, volume)))
            
            if voice_id is not None:
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if voice.id == voice_id:
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            self.logger.info("Voice properties updated")
            
        except Exception as e:
            self.logger.error(f"Error setting voice properties: {e}")
    
    def get_available_voices(self) -> list:
        """Get list of available TTS voices"""
        if not self.is_tts_available():
            return []
        
        try:
            voices = self.tts_engine.getProperty('voices')
            return [
                {
                    "id": voice.id,
                    "name": voice.name,
                    "languages": getattr(voice, 'languages', []),
                    "gender": getattr(voice, 'gender', 'unknown')
                }
                for voice in voices
            ]
        except Exception as e:
            self.logger.error(f"Error getting voices: {e}")
            return []
    
    def cleanup(self):
        """Clean up speech resources"""
        self.stop_listening()
        
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
        
        self.logger.info("Speech handler cleaned up")
    
    def get_status(self) -> dict:
        """Get speech handler status"""
        return {
            "stt_available": self.is_stt_available(),
            "tts_available": self.is_tts_available(),
            "listening": self.is_listening,
            "wake_word_detected": self.wake_word_detected,
            "vosk_available": VOSK_AVAILABLE,
            "sounddevice_available": SOUNDDEVICE_AVAILABLE,
            "pyttsx3_available": PYTTSX3_AVAILABLE
        }