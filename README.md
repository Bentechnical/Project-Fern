# Project Fern 🌱

**ESG Investment Preference Discovery Chatbot**

An AI-powered conversational tool that helps investors articulate their Environmental, Social, and Governance (ESG) investment priorities through adaptive dialogue.

## 🎯 What It Does

- Conducts 15-20 minute guided conversations about ESG preferences
- Adapts depth of questioning based on user interest (dive deeper where they care, skip what they don't)
- Generates personalized preference profiles for financial advisors
- Covers 5 major ESG categories with 25+ subcategories

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key ([Get one free here](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone and navigate to the repository:**
   ```bash
   cd ~/Desktop/Project-Fern/Project-Fern
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key:**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your Gemini API key
   # GEMINI_API_KEY=your_actual_key_here
   ```

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
Project-Fern/
├── app.py                   # Main Streamlit application
├── data/
│   └── esg_categories.json  # ESG taxonomy (5 categories, 25 subcategories)
├── src/
│   ├── llm.py              # Gemini API wrapper
│   ├── conversation.py     # Conversation state & logic
│   └── prompts.py          # System prompts & templates
├── PROJECT_DOCUMENTATION.md # Comprehensive documentation
└── requirements.txt         # Python dependencies
```

## 🧪 Testing the LLM Connection

Before running the full app, test your API connection:

```bash
python src/llm.py
```

You should see: `✓ Gemini API connected successfully`

## 📊 ESG Categories Covered

1. **Climate & Emissions** - GHG emissions, targets, adaptation
2. **Water Management** - Consumption, quality, conservation
3. **Labor Practices** - Wages, safety, worker rights
4. **Diversity, Equity & Inclusion** - Board/workforce diversity, pay equity
5. **Corporate Governance** - Board structure, exec compensation, ethics

## 💡 How It Works

1. User starts conversation
2. Bot asks about each ESG category (high/medium/low importance)
3. **Adaptive branching:**
   - High interest → Explore subcategories in depth
   - Medium interest → Brief clarifying questions
   - Low interest → Note preference and move on
4. Generate personalized preference profile
5. Export report for financial advisor review

## 🔧 Tech Stack

- **Frontend:** Streamlit (rapid prototyping)
- **LLM:** Google Gemini 1.5 Flash (free tier)
- **Backend:** Python 3.x
- **Data:** JSON (will migrate to SQLite for production)

## 📚 Documentation

See [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) for comprehensive documentation including:
- Detailed architecture
- Conversation flow logic
- Future enhancement plans
- Cost projections
- Migration paths

## 🛣️ Roadmap

### Phase 1 (Current): Prototype
- ✅ Basic conversation flow
- ✅ Adaptive questioning
- ✅ Preference tracking
- ✅ Report generation

### Phase 2: User Testing
- [ ] Test with 10+ users
- [ ] Refine question phrasing
- [ ] Improve branching logic
- [ ] Add save/resume functionality

### Phase 3: Production
- [ ] Expand to 100-200 categories
- [ ] Add user authentication
- [ ] Build advisor dashboard
- [ ] Consider Next.js migration

## 🔐 Privacy & Security

- API keys stored in `.env` (never committed to git)
- No user data persisted currently (prototype phase)
- Private repository

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🤝 Contributing

This is currently a private prototype. If you have access and want to contribute, please reach out first.

---

**Status:** Prototype (v0.1.0)
**Last Updated:** December 2025
