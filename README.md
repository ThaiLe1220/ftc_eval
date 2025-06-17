# Character Chatbot CLI

A simplified Python CLI version of the character chatbot for AI evaluation and testing. This removes all web complexity and focuses on core character AI interactions.

## Features

- 🎭 **Character Personality System** - JSON-defined characters with rich personalities
- 🤖 **Dual AI Support** - Claude 3.5 Sonnet & GPT-4 
- 💬 **CLI Interface** - Simple terminal-based chat
- 🔄 **Character Switching** - Easy switching between characters
- 📝 **Conversation Memory** - Maintains context within chats
- 🎨 **Formatted Responses** - Color-coded narrative and dialogue

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Copy the template and add your keys:
```bash
cp .env.template .env
# Edit .env with your API keys
```

### 3. Add Character Files
Copy character JSON files to the `characters/` directory. The original character files from the Node.js version work directly.

Example character structure:
```json
{
  "id": "lysandra",
  "name": "Lysandra Stormwake", 
  "description": "The immortal high-elf matriarch...",
  "greeting_context": "Born from a moon-lit whirlpool...",
  "personality": "Serene and measured, speaks in ocean metaphors...",
  "greeting": "*Lysandra emerged from the mist...*",
  "response_style": "Greets with fluid courtesy...",
  "category": "Fantasy"
}
```

### 4. Run
```bash
python main.py
```

## Usage

### Basic Flow
1. **Setup** - Enter your name and gender
2. **Select Character** - Choose from available characters  
3. **Chat** - Type messages and get character responses
4. **Commands** - Use special commands for control

### Commands
- `/switch` - Change to different character
- `/provider` - Switch between Claude/GPT
- `/info` - Show session information
- `/clear` - Clear conversation history
- `/quit` - Exit application

### Example Session
```
👤 User Setup
Enter your name: Alex
Select your gender:
1. Male
2. Female  
3. Other
Enter choice (1-3): 1

✓ Welcome, Alex!

🎭 Available Characters:

 1. Lysandra Stormwake
     [Fantasy] The immortal high-elf matriarch and silent queen...

 2. Marco "Jet" Santoro  
     [Real] Racing star. Fearless Formula driver...

Select character (1-2): 1

✓ Selected: Lysandra Stormwake

 Lysandra Stormwake 
*Lysandra emerged from the mist-shrouded waters...*

"May calm tides carry your thoughts, wanderer. Which shore does your heart anchor to?"

💬 Chat started! Commands: /switch, /provider, /info, /clear, /quit

Alex: Hello Lysandra, I'm feeling lost in life.

Thinking...

 Lysandra Stormwake 
*Lysandra's ancient eyes reflected understanding as she folded another paper boat...*

"Loss often signals that tides are shifting, Alex. Tell me, what familiar shores no longer call to you?"
```

## Project Structure

```
character-chatbot-cli/
├── characters/           # Character JSON files
├── src/
│   ├── __init__.py
│   ├── character_manager.py  # Load characters, generate prompts
│   ├── ai_handler.py        # Claude/GPT API integration  
│   ├── conversation.py      # Simple conversation state
│   └── cli.py              # Main CLI interface
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── .env.template       # Environment variables template
└── README.md           # This file
```

## Key Simplifications from Original

**Removed:**
- ❌ Web interface (HTML/CSS/JS/Express)
- ❌ Image galleries and backgrounds
- ❌ Streaming responses  
- ❌ Multi-user session management
- ❌ File persistence
- ❌ Complex error handling/UI

**Kept:**
- ✅ Character personality system
- ✅ AI API integration (Claude + GPT)
- ✅ System prompt generation
- ✅ Response formatting (narrative/dialogue)
- ✅ Basic conversation memory
- ✅ Character switching

## Evaluation Benefits

This simplified version is perfect for:
- **Character Quality Testing** - Focus on personality consistency
- **AI Provider Comparison** - Easy Claude vs GPT switching  
- **Response Analysis** - Clean conversation logs
- **Rapid Iteration** - Quick character modification testing
- **Performance Evaluation** - Minimal overhead, pure AI focus

## API Keys

Get your API keys from:
- **Anthropic Claude**: https://console.anthropic.com/
- **OpenAI GPT**: https://platform.openai.com/api-keys

You need at least one API key to run the chatbot.

## Character Development

Characters are defined in JSON files with these fields:
- `id` - Unique identifier
- `name` - Character display name
- `description` - Short character description  
- `greeting_context` - Character backstory
- `personality` - Behavioral traits
- `greeting` - Initial greeting message
- `response_style` - How character typically responds
- `category` - Character category (Fantasy, Real, etc.)

The same character files from the original Node.js version work without modification.