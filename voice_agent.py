#!/usr/bin/env python3
"""
Voice Agent 2026 - Production-Ready AI Voice Assistant
All QuickAgent issues fixed: PyAudio, Voice Output, Updated Dependencies
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Optional
import time
import signal
import json
from datetime import datetime

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# LangChain imports (2026 compatible)
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain

# Deepgram SDK v3+ (fixed for 2026)
from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions

# Audio handling (PyAudio with fallbacks)
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

import requests
import wave
import io
import subprocess
import shutil

# ====================== LOGGING SETUP ======================
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_logger(name, level=logging.INFO):
    """Setup logger with colors"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    handler = logging.StreamHandler()
    handler.setLevel(level)
    
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    
    return logger

logger = setup_logger(__name__, logging.INFO)

# ====================== CONFIGURATION ======================
class Config:
    """Configuration management"""
    def __init__(self):
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY", "").strip()
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        self.llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self.llm_model = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        self.deepgram_stt_model = os.getenv("DEEPGRAM_STT_MODEL", "nova-2")
        self.deepgram_tts_model = os.getenv("DEEPGRAM_TTS_MODEL", "aura-asteria-en")
        
        self.language = os.getenv("LANGUAGE", "en-US")
        self.sample_rate = int(os.getenv("SAMPLE_RATE", "16000"))
        self.channels = int(os.getenv("CHANNELS", "1"))
        
        self._validate()
    
    def _validate(self):
        """Validate configuration"""
        if not self.deepgram_api_key:
            logger.warning("⚠️  DEEPGRAM_API_KEY not set - audio features limited")
        
        if not self.groq_api_key and not self.openai_api_key:
            raise ValueError("❌ Set GROQ_API_KEY or OPENAI_API_KEY in .env")

# ====================== LLM PROCESSOR ======================
class LanguageModelProcessor:
    """Language Model processing with memory"""
    
    def __init__(self, config: Config):
        self.config = config
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        
        logger.info(f"🤖 Initializing {config.llm_provider} LLM: {config.llm_model}")
        
        if config.llm_provider == "groq":
            self.llm = ChatGroq(
                temperature=config.llm_temperature,
                model_name=config.llm_model,
                groq_api_key=config.groq_api_key,
            )
        elif config.llm_provider == "openai":
            self.llm = ChatOpenAI(
                temperature=config.llm_temperature,
                model_name=config.llm_model,
                openai_api_key=config.openai_api_key,
            )
        else:
            raise ValueError(f"Unknown LLM provider: {config.llm_provider}")
        
        system_prompt = self._load_system_prompt()
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{text}"),
        ])
        
        self.conversation = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
        )
        logger.info("✅ LLM initialized successfully")
    
    def _load_system_prompt(self) -> str:
        """Load system prompt"""
        prompt_file = Path("system_prompt.txt")
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                return f.read().strip()
        
        default_prompt = """You are a helpful, friendly AI assistant created in 2026.
- Speak naturally and conversationally
- Keep responses concise (under 50 words for voice)
- Be helpful, harmless, and honest
- Maintain conversation context"""
        
        logger.warning("system_prompt.txt not found - using default prompt")
        return default_prompt
    
    def process(self, text: str) -> Optional[str]:
        """Process user input"""
        if not text or not text.strip():
            return None
        
        try:
            start_time = time.time()
            response = self.conversation.invoke({"text": text})
            elapsed = int((time.time() - start_time) * 1000)
            
            result = response.get('text', '').strip()
            logger.info(f"⏱️  LLM response ({elapsed}ms): {result}")
            
            return result
        except Exception as e:
            logger.error(f"❌ LLM error: {e}", exc_info=True)
            return None

# ====================== AUDIO PLAYER ======================
class AudioPlayer:
    """Multi-backend audio player"""
    
    @staticmethod
    def play(audio_data: bytes):
        """Play audio with fallbacks"""
        # Try ffplay first
        if shutil.which("ffplay"):
            try:
                process = subprocess.Popen(
                    ["ffplay", "-autoexit", "-", "-nodisp", "-loglevel", "quiet"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                process.communicate(input=audio_data, timeout=30)
                logger.debug("✅ Audio played via ffplay")
                return
            except Exception as e:
                logger.warning(f"ffplay failed: {e}")
        
        # Try PyAudio
        if PYAUDIO_AVAILABLE:
            try:
                AudioPlayer._play_with_pyaudio(audio_data)
                logger.debug("✅ Audio played via PyAudio")
                return
            except Exception as e:
                logger.warning(f"PyAudio failed: {e}")
        
        # Fallback
        logger.info("🔊 (Audio would play here - no audio output available)")
    
    @staticmethod
    def _play_with_pyaudio(audio_data: bytes):
        """Play using PyAudio"""
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            wav_file.writeframes(audio_data)
        
        wav_buffer.seek(0)
        
        with wave.open(wav_buffer, 'rb') as wav_file:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=p.get_format_from_width(wav_file.getsampwidth()),
                channels=wav_file.getnchannels(),
                rate=wav_file.getframerate(),
                output=True,
            )
            
            chunk = 1024
            data = wav_file.readframes(chunk)
            while data:
                stream.write(data)
                data = wav_file.readframes(chunk)
            
            stream.stop_stream()
            stream.close()
            p.terminate()

# ====================== VOICE AGENT ======================
class VoiceAgent:
    """Main Voice Agent - 2026 Edition"""
    
    def __init__(self):
        self.config = Config()
        self.llm_processor = LanguageModelProcessor(self.config)
        self.stop_signal = False
        self.conversation_count = 0
        
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        
        logger.info("🎙️ Voice Agent 2026 Ready!")
    
    def _handle_shutdown(self, signum, frame):
        """Graceful shutdown"""
        logger.info("\n⏹️ Shutting down...")
        self.stop_signal = True
        sys.exit(0)
    
    async def run(self):
        """Main conversation loop"""
        logger.info("🎤 Say something... (or say 'goodbye' to exit)\n")
        
        while not self.stop_signal:
            try:
                self.conversation_count += 1
                logger.info(f"\n--- Turn {self.conversation_count} ---")
                
                # Get user input
                user_input = await self._get_speech_input()
                if not user_input or user_input.strip() == "":
                    continue
                
                logger.info(f"👤 You: {user_input}")
                
                # Check exit
                if any(word in user_input.lower() for word in ["goodbye", "exit", "quit", "bye"]):
                    logger.info("👋 Goodbye!")
                    break
                
                # Get LLM response
                response = self.llm_processor.process(user_input)
                if not response:
                    continue
                
                logger.info(f"🤖 AI: {response}")
                
                # Speak response
                await self._text_to_speech(response)
                
            except KeyboardInterrupt:
                logger.info("Interrupted")
                break
            except Exception as e:
                logger.error(f"Error: {e}", exc_info=True)
                continue
    
    async def _get_speech_input(self) -> str:
        """Get speech input with fallback"""
        try:
            if not os.getenv("DEEPGRAM_API_KEY"):
                return self._get_text_input()
            
            return await self._deepgram_stt()
        except Exception as e:
            logger.warning(f"Speech failed: {e}. Using text input.")
            return self._get_text_input()
    
    async def _deepgram_stt(self) -> str:
        """Speech-to-text with Deepgram v3"""
        transcript_parts = []
        transcription_complete = asyncio.Event()
        
        try:
            config = DeepgramClientOptions(
                options={"api_key": os.getenv("DEEPGRAM_API_KEY")}
            )
            deepgram = DeepgramClient(
                api_key=os.getenv("DEEPGRAM_API_KEY"),
                config=config
            )
            
            dg_connection = deepgram.listen.asynclive.v("1")
            logger.info("🎧 Listening...")
            
            async def on_transcript(result, **kwargs):
                try:
                    if result.channel.alternatives:
                        text = result.channel.alternatives[0].transcript
                        if result.speech_final:
                            transcript_parts.append(text)
                            transcription_complete.set()
                except Exception as e:
                    logger.debug(f"Transcript error: {e}")
            
            dg_connection.on(LiveTranscriptionEvents.Transcript, on_transcript)
            
            options = LiveOptions(
                model=self.config.deepgram_stt_model,
                language=self.config.language,
                encoding="linear16",
                channels=1,
                sample_rate=16000,
                endpointing=300,
                punctuate=True,
                smart_format=True,
            )
            
            await dg_connection.start(options)
            
            from deepgram import Microphone
            microphone = Microphone(dg_connection.send)
            microphone.start()
            
            try:
                await asyncio.wait_for(transcription_complete.wait(), timeout=30)
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for speech")
            
            microphone.finish()
            await dg_connection.finish()
            
            return ' '.join(transcript_parts).strip()
        
        except Exception as e:
            logger.error(f"STT error: {e}")
            raise
    
    def _get_text_input(self) -> str:
        """Fallback text input"""
        try:
            return input("📝 Enter text: ").strip()
        except EOFError:
            logger.info("EOF")
            sys.exit(0)
    
    async def _text_to_speech(self, text: str):
        """Convert text to speech"""
        if not text or not text.strip():
            return
        
        try:
            api_key = os.getenv("DEEPGRAM_API_KEY")
            if not api_key:
                logger.info(f"🔊 [Would speak]: {text}")
                return
            
            model = self.config.deepgram_tts_model
            url = f"https://api.deepgram.com/v1/speak?model={model}&encoding=linear16&sample_rate=24000"
            
            headers = {
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                url,
                json={"text": text},
                headers=headers,
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            audio_data = b""
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    audio_data += chunk
            
            if audio_data:
                AudioPlayer.play(audio_data)
        
        except Exception as e:
            logger.warning(f"TTS error: {e}")
            logger.info(f"🔊 [Would speak]: {text}")

# ====================== MAIN ======================
async def main():
    """Main entry point"""
    try:
        agent = VoiceAgent()
        await agent.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nExiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
