# Character Chatbot Evaluation System

A comprehensive evaluation platform for character-based conversational AI with multi-AI consensus scoring, reasoning capture, and systematic improvement insights.

## 🎯 What It Does

- **Multi-AI Evaluation**: DeepSeek Reasoner, Claude Thinking, and O3 evaluate character conversations
- **Universal Scenarios**: 5 test scenarios work across Fantasy and Real character types
- **Reasoning Capture**: Full AI thinking/reasoning content stored for analysis
- **Performance Insights**: Token usage, timing, cost tracking, and improvement recommendations
- **Consensus Analysis**: Agreement tracking and outlier detection across evaluators

## ⚡ Quick Start

### 1. Setup
```bash
pip install -r requirements.txt
touch .env
# Add your API keys to .env:
# ANTHROPIC_API_KEY=your_claude_key
# OPENAI_API_KEY=your_openai_key  
# DEEPSEEK_API_KEY=your_deepseek_key
```

### 2. Add Characters
Place character JSON files in `characters/` directory. See existing characters for format.

### 3. Run Evaluation
```bash
# Quick test of all providers
python -c "from src.ai_handler import AIHandler; AIHandler().test_all_providers()"

# Full evaluation pipeline
python phase1_integration_test.py

# Interactive character chat
python main.py
```

## 🤖 Model Configuration

**Character Conversations** (Natural, Spontaneous):
- Claude Sonnet 4 (no thinking mode)
- GPT-4.1

**Evaluation Tasks** (Reasoning-Enhanced):
- DeepSeek Reasoner (default) - Thorough analysis with reasoning capture
- Claude Sonnet 4 with thinking mode - Balanced evaluation with thinking logs
- O3 with reasoning effort - Fast evaluation with built-in reasoning

## 📊 Example Results

**Recent Performance** (Phase 1 Validation):
- **Average Score**: 7.3/10 across character evaluations
- **Evaluator Agreement**: 58.3% consensus
- **Cost Efficiency**: ~$0.047 per evaluation
- **Character Insights**: Lysandra (7.7/10) > Marco (6.9/10)

## 📁 Enhanced Data Structure

```
evaluation_results/
├── conversations/       # Raw conversation data
├── evaluations/        # Evaluation results with consensus
├── detailed_logs/      # Full AI responses with reasoning content
├── reasoning_analysis/ # Analysis of AI thinking patterns
├── analysis/          # System reports and insights
├── logs/             # Operation logs
└── exports/          # CSV exports with metrics
```

## 🎭 Available Characters

**Fantasy Characters** (6): Aurelia, Fenric, Lysandra, Cassia, Aria, Dorian
**Real Characters** (8): Marco, Juniper, Hana, Camila, Selena, Ren, Lisa, Elara

Each character has unique personality, backstory, and response style defined in JSON.

## 🧪 Evaluation Criteria

1. **Character Immersion Quality** - World-building and storytelling
2. **Story Progression & Development** - Plot advancement and narrative hooks
3. **Interactive Agency & User Impact** - User influence on conversation
4. **Emotional Journey Creation** - Emotional range and authentic reactions
5. **Fantasy Fulfillment & Escapism** - Wish fulfillment and novelty
6. **Character Authenticity** - Internal consistency and believability

## 📈 Key Features

- **Multi-AI Consensus**: Reduces bias, increases reliability
- **Reasoning Transparency**: Full thinking processes captured and analyzed
- **Cost Tracking**: Token usage and estimated costs for budget planning
- **Quality Control**: Conversation validation and outlier detection
- **Actionable Insights**: Specific improvement recommendations per character
- **Export Ready**: CSV and JSON exports for further analysis

## 🚀 What's Next

**Phase 1**: ✅ **COMPLETED** - Individual conversation evaluation system
**Phase 2**: 🔄 **READY** - Automated batch evaluation (5 scenarios × 14 characters × 3 providers = 210 evaluations)
**Phase 3**: ⏳ **PLANNED** - Advanced analytics and reporting interfaces

## 🛠 Development

**Core Components**:
- `ai_handler.py` - Multi-provider AI integration with reasoning capture
- `ai_evaluator.py` - Multi-AI consensus evaluation engine
- `enhanced_results_manager.py` - Comprehensive data storage and analysis
- `test_scenarios.py` - Universal test scenarios for all character types

**Testing**: Run `phase1_integration_test.py` for full pipeline validation.

## 📋 Requirements

- Python 3.11+
- API keys for Anthropic Claude, OpenAI, and/or DeepSeek
- ~$0.05 per character evaluation (cost varies by model usage)

---

Transform character AI development from intuition to data-driven excellence. 🎯
