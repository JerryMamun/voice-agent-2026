"""
Configuration management for Voice Agent 2026
Handles environment variables and settings
"""

import os
import logging
from pathlib import Path
from typing import Optional

# Configure logging
def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get configured logger"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # Formatter with timestamps
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.setLevel(level)
    
    return logger


class Config:
    """Configuration class for Voice Agent"""
    
    def __init__(self):
        """Initialize configuration from environment variables"""
        
        # API Keys (required)
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY", "").strip()
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        # Validate API keys
        self._validate_api_keys()
        
        # LLM Configuration
        self.llm_provider = os.getenv("LLM_PROVIDER", "groq").lower()
        self.llm_model = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        # Deepgram Configuration
        self.deepgram_stt_model = os.getenv("DEEPGRAM_STT_MODEL", "nova-2")
        self.deepgram_tts_model = os.getenv("DEEPGRAM_TTS_MODEL", "aura-asteria-en")
        
        # Audio Configuration
        self.sample_rate = int(os.getenv("SAMPLE_RATE", "16000"))
        self.channels = int(os.getenv("CHANNELS", "1"))
        self.encoding = os.getenv("ENCODING", "linear16")
        
        # Speech Configuration
        self.language = os.getenv("LANGUAGE", "en-US")
        self.endpointing_ms = int(os.getenv("ENDPOINTING_MS", "300"))
        self.vad_enabled = os.getenv("VAD_ENABLED", "true").lower() == "true"
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # Timeouts
        self.speech_timeout_seconds = int(os.getenv("SPEECH_TIMEOUT_SECONDS", "30"))
        self.llm_timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
        
        logger = get_logger(__name__)
        logger.debug("Configuration loaded successfully")
    
    def _validate_api_keys(self):
        """Validate required API keys"""
        logger = get_logger(__name__)
        
        if not self.deepgram_api_key:
            logger.warning("⚠️  DEEPGRAM_API_KEY not set. Speech features will be limited.")
        
        if not self.groq_api_key and not self.openai_api_key:
            raise ValueError(
                "❌ Neither GROQ_API_KEY nor OPENAI_API_KEY is set. "
                "Please set at least one LLM API key in .env file"
            )
    
    def get_llm_model_for_provider(self) -> str:
        """Get appropriate model name for LLM provider"""
        if self.llm_provider == "groq":
            # Available Groq models as of 2026
            return self.llm_model or "mixtral-8x7b-32768"
        elif self.llm_provider == "openai":
            # Latest OpenAI models
            return self.llm_model or "gpt-4-turbo"
        else:
            raise ValueError(f"Unknown provider: {self.llm_provider}")
    
    def to_dict(self) -> dict:
        """Convert config to dictionary for logging"""
        return {
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "deepgram_stt_model": self.deepgram_stt_model,
            "deepgram_tts_model": self.deepgram_tts_model,
            "language": self.language,
            "vad_enabled": self.vad_enabled,
            "log_level": self.log_level,
        }
