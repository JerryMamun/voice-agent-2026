# 🎙️ Voice Agent 2026 - Production-Ready AI Voice Assistant

A modern, fully-featured AI voice assistant built with **Deepgram (Speech)**, **Groq/OpenAI (LLM)**, and **Python 3.11+**.

## ✨ Features

- ✅ **Real-time Speech Recognition** - Deepgram Nova-2 model with VAD
- ✅ **Multiple LLM Support** - Groq (free, fast) or OpenAI
- ✅ **Natural Voice Output** - Deepgram TTS with automatic fallbacks
- ✅ **Conversation Memory** - Maintains context across turns
- ✅ **Robust Error Handling** - Graceful fallbacks for all components
- ✅ **Production Ready** - Logging, configuration management, signal handling
- ✅ **Fixed PyAudio** - Works on Ubuntu without compilation issues
- ✅ **Modern Dependencies** - All packages updated for 2026

## 🔧 System Requirements

- **Ubuntu 20.04+** or Linux-based system
- **Python 3.11+**
- **microphone** for voice input
- **speaker** for audio output (optional - text fallback available)

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone <repo-url>
cd voice-agent-2026
chmod +x setup.sh
./setup.sh
```

### 2. Configure API Keys

```bash
nano .env
```

Add your API keys:
```
DEEPGRAM_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

### 3. Run

```bash
chmod +x run.sh
./run.sh
```

Or directly:
```bash
python3 voice_agent.py
```

## 📝 API Keys Setup

### Deepgram (Speech-to-Text & Text-to-Speech)
1. Visit: https://console.deepgram.com/
2. Sign up (free tier available)
3. Create API key
4. Add to `.env`: `DEEPGRAM_API_KEY=...`

### Groq (LLM - Recommended)
1. Visit: https://groq.com/
2. Create account
3. Get API key from console
4. Add to `.env`: `GROQ_API_KEY=...`

### OpenAI (Alternative LLM)
1. Visit: https://platform.openai.com/
2. Create account and add payment
3. Get API key
4. Update `.env`:
   ```
   LLM_PROVIDER=openai
   OPENAI_API_KEY=...
   ```

## ⚙️ Configuration

Edit `.env` file to customize:

```bash
# Choose LLM
LLM_PROVIDER=groq              # or 'openai'
LLM_MODEL=mixtral-8x7b-32768   # or 'gpt-4-turbo'

# Speech Settings
LANGUAGE=en-US
DEEPGRAM_STT_MODEL=nova-2
DEEPGRAM_TTS_MODEL=aura-asteria-en

# Performance
LLM_TEMPERATURE=0.7            # 0=deterministic, 1=creative
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR
```

## 🐛 Troubleshooting

### PyAudio Installation Issues
```bash
# Option 1: System package (recommended)
sudo apt-get install python3-pyaudio

# Option 2: Compile from source
sudo apt-get install portaudio19-dev
pip install --upgrade setuptools wheel
pip install pyaudio

# Option 3: Use sounddevice instead (auto-fallback)
```

### No Audio Output
- Check speakers: `aplay -l`
- Test audio: `speaker-test -t sine -f 1000 -l 1`
- Ensure ffplay or PyAudio is installed
- Check `LOG_LEVEL=DEBUG` for details

### Microphone Not Working
```bash
# List audio devices
arecord -l

# Test microphone
arecord -d 5 test.wav

# Check permissions
# Your user may need to be added to audio group:
sudo usermod -a -G audio $USER
# Then log out and back in
```

### Deepgram/LLM Connection Issues
- Verify API keys in `.env`
- Check internet connection
- Try: `curl -I https://api.deepgram.com`
- Enable `LOG_LEVEL=DEBUG` for detailed errors

### Server Setup (No Display)
```bash
# For headless servers, use text input fallback:
# The app will automatically switch to text input if no audio devices
```

## 📊 Project Structure

```
voice-agent-2026/
├── voice_agent.py          # Main application
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
├── .env                   # Your configuration (create from example)
├── setup.sh              # Automatic setup script
├── run.sh                # Run script
├── system_prompt.txt     # AI system prompt
└── README.md             # This file
```

## 🎯 Usage Examples

### Basic Usage
```bash
python3 voice_agent.py
```
Then speak or type your message.

### Text Input Fallback
If microphone fails, the app automatically switches to text input.

### Change LLM Provider
Edit `.env`:
```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo
OPENAI_API_KEY=sk-...
```

### Custom System Prompt
Edit `system_prompt.txt` to change AI behavior.

### Debug Mode
```bash
LOG_LEVEL=DEBUG python3 voice_agent.py
```

## 🔄 What's Fixed from Original QuickAgent

| Issue | Solution |
|-------|----------|
| PyAudio compilation errors | Added system package fallback + sounddevice alternative |
| No voice output | Multiple audio backends + fallback text output |
| AI generates responses without input | Fixed event handling + timeout logic |
| ffplay dependency issues | Added PyAudio + sounddevice alternatives |
| Outdated dependencies | All packages updated for 2026 |
| Poor error messages | Comprehensive logging with DEBUG mode |
| No configuration management | Added config.py with environment variables |
| Hardcoded API keys | Environment variable support |
| No conversation memory | LangChain memory management |
| VAD causing issues | Optional VAD with configuration |

## 📚 Advanced Configuration

### Environment Variables

```bash
# Speech Settings
SAMPLE_RATE=16000
CHANNELS=1
ENCODING=linear16
LANGUAGE=en-US
ENDPOINTING_MS=300                # Silence detection
VAD_ENABLED=true                  # Voice Activity Detection

# Timeouts
SPEECH_TIMEOUT_SECONDS=30
LLM_TIMEOUT_SECONDS=60

# LLM
LLM_TEMPERATURE=0.7               # 0=focused, 1=creative
```

### Models Available

**Deepgram STT:**
- `nova-2` (default) - Most accurate
- `nova-2-general` - Optimized for general speech

**Deepgram TTS:**
- `aura-asteria-en` (default) - Natural voice
- `aura-orpheus-en` - Alternative voice
- [More options available](https://developers.deepgram.com/docs/models-languages-voices)

**Groq Models:**
- `mixtral-8x7b-32768` (default) - Fast & good quality
- `llama-3-70b` - High quality
- `gemma-7b-it` - Lightweight

**OpenAI Models:**
- `gpt-4-turbo` - Most capable
- `gpt-3.5-turbo` - Fast & cheap

## 🚨 Common Commands

```bash
# Setup
./setup.sh

# Run
./run.sh
python3 voice_agent.py

# Debug
LOG_LEVEL=DEBUG python3 voice_agent.py

# Check audio devices
arecord -l
aplay -l

# Test microphone
arecord -d 5 test.wav

# Test speaker
speaker-test -t sine -f 1000 -l 1
```

## 📝 Logs

Check logs in console output. Enable debug mode:
```bash
LOG_LEVEL=DEBUG python3 voice_agent.py
```

## 🤝 Contributing

Found a bug? Have a feature idea?
- Report issues with full logs (`LOG_LEVEL=DEBUG`)
- Include your OS and audio setup
- Describe what you were trying to do

## 📄 License

MIT License - Feel free to use in production

## 🙏 Credits

- Built with [Deepgram](https://deepgram.com) - Speech AI
- Powered by [Groq](https://groq.com) - Fast LLM
- LangChain for LLM orchestration
- Original concept from [QuickAgent](https://github.com/gkamradt/QuickAgent)

## 🎓 Learning Resources

- [Deepgram Docs](https://developers.deepgram.com/docs)
- [Groq API Docs](https://groq.com/docs)
- [LangChain Python](https://python.langchain.com/)
- [AsyncIO Guide](https://docs.python.org/3/library/asyncio.html)

---

**Made with ❤️ in 2026**

For issues and questions, check the troubleshooting section above first!
