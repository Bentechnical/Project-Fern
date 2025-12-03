# Project Fern - ESG Investment Preference Chatbot

## Project Overview

An AI-powered conversational chatbot that helps investors articulate their ESG (Environmental, Social, Governance) investment preferences through adaptive dialogue. The system conducts 15-30 minute conversations, explores topics based on user interest, and generates structured preference profiles for financial advisors.

## Core Concept

**The Problem:** Investors struggle to articulate nuanced ESG preferences across ~1,000 potential categories. Advisors need efficient ways to capture these preferences.

**The Solution:** An adaptive chatbot that:
- Asks about high-level ESG topics
- Dives deeper when user shows interest
- Skips/minimizes areas of low interest
- Generates actionable preference profiles

## Tech Stack

### Current (Prototype)
- **Frontend:** Streamlit (Python-based web framework for rapid prototyping)
- **Backend:** Python 3.x
- **LLM:** Google Gemini 1.5 Flash (free tier, 15 req/min)
- **Data Storage:** JSON files (will migrate to SQLite later)

### Why These Choices?
- **Streamlit:** Fastest path to working prototype (built-in chat UI, no frontend coding)
- **Gemini:** Free tier perfect for initial development/testing (~$0 for first 100 conversations)
- **Python:** Best ecosystem for AI/LLM integration, easy to work with AI coding assistants

### Future Migration Path
If prototype validates, consider rebuilding in:
- **Next.js** (TypeScript) - One codebase for frontend + backend, professional UI
- **FastAPI** + React - More traditional separation of concerns
- **Claude API** - Better conversational quality (~$0.015 per conversation with Haiku)

## Project Structure

```
Project-Fern/
├── .env                      # API keys (NEVER commit!)
├── .env.example              # Template for .env file
├── .gitignore               # Includes .env, Python artifacts, Streamlit configs
├── LICENSE                  # MIT License
├── README.md                # Basic project description
├── PROJECT_DOCUMENTATION.md # This file - comprehensive reference
├── requirements.txt         # Python dependencies
├── app.py                   # Main Streamlit application
├── data/
│   └── esg_categories.json  # ESG taxonomy (5 top-level, ~25 subcategories)
└── src/
    ├── llm.py              # Gemini API wrapper
    ├── conversation.py     # Conversation state & routing logic
    └── prompts.py          # System prompts and templates
```

## ESG Category Structure

**Current Sample Data (5 top-level categories):**
1. **Climate & Emissions** - GHG emissions, targets, adaptation (5 subcategories)
2. **Water Management** - Consumption, quality, stress areas (3 subcategories)
3. **Labor Practices** - Wages, safety, rights, supply chain (4 subcategories)
4. **Diversity, Equity & Inclusion** - Board/workforce diversity, pay equity (3 subcategories)
5. **Corporate Governance** - Board structure, exec comp, shareholder rights, ethics (4 subcategories)

**Data Model:**
```json
{
  "id": "climate",
  "name": "Climate & Emissions",
  "description": "Climate change mitigation, greenhouse gas emissions...",
  "level": 1,
  "parent_id": null,
  "subcategories": [
    {
      "id": "climate_scope1",
      "name": "Direct Emissions (Scope 1)",
      "description": "...",
      "level": 2,
      "parent_id": "climate"
    }
  ]
}
```

**Expansion Plan:**
- Phase 1: 5 categories → 25 subcategories (current)
- Phase 2: Expand to 100-200 categories
- Phase 3: Full 1,000 category taxonomy (if validated)

## Conversation Flow (Adaptive Branching)

### High-Level Logic:

1. **Introduction** - Explain purpose, estimated time
2. **Top-Level Assessment** - Ask about each major category (E, S, G)
   - "How important is climate change to you in investments?" (High/Medium/Low)
3. **Adaptive Exploration:**
   - **If HIGH interest:** Ask about subcategories
   - **If MEDIUM interest:** Ask 1-2 clarifying questions
   - **If LOW interest:** Skip subcategories, move on
4. **Synthesis** - Summarize preferences, ask for corrections
5. **Profile Generation** - Create structured output

### Example Exchange:

```
Bot: "How important is climate change in your investment decisions?"
User: "Very important - it's my top priority"
Bot: [Detects high interest, dives deeper]
    "Great! Let's explore climate topics. Are you more concerned with:
     - Current emissions (Scope 1, 2, 3)?
     - Future commitments (net-zero targets)?
     - Climate resilience and adaptation?"
User: "I care most about actual emissions reductions, not just commitments"
Bot: [Notes preference: emissions > targets]
    "Understood. Should we focus on direct emissions (company operations)
     or their entire value chain (including suppliers)?"
```

### State Management:

Track for each category:
- **Interest level:** high/medium/low
- **Specific preferences:** User's nuanced views
- **Confidence:** How strongly they feel
- **Exploration depth:** Which subcategories were discussed

## LLM Integration (`src/llm.py`)

### GeminiChat Class:

```python
chat = GeminiChat(api_key="...")
chat.start_chat(system_instruction="You are an ESG investment advisor...")
response = chat.send_message("User's message")
history = chat.get_chat_history()
```

**Key Features:**
- Wraps Google Gemini API
- Manages conversation history automatically
- Supports system instructions (behavior/persona)
- Easy to swap for Claude/OpenAI later (just change this file)

**API Costs:**
- Free tier: 15 requests/min (plenty for solo testing)
- If switching to Claude Haiku: ~$0.015 per 30-message conversation

## Conversation Logic (`src/conversation.py`)

**TODO - Will contain:**
- `ConversationState` class - Track preferences, current topic, exploration depth
- `determine_next_question()` - Branching logic based on user responses
- `extract_preference()` - Parse user answers into structured data
- `should_explore_deeper()` - Decide if subcategories warrant exploration

**Key Design Principles:**
1. **Parse user intent, not just keywords** - LLM interprets "I care about this" vs "not really"
2. **Graceful "don't know" handling** - Don't force opinions, note uncertainty
3. **Progress indicators** - Show user how far along they are
4. **Save/resume capability** - For longer conversations

## Prompts (`src/prompts.py`)

**TODO - Will contain:**

### System Prompt Template:
```
You are an ESG investment preference advisor. Your role is to help users
articulate their values and priorities for sustainable investing through
natural conversation.

Key guidelines:
- Be neutral and non-judgmental about their preferences
- Ask clear, jargon-free questions
- Provide brief context when needed (1 sentence explanations)
- Recognize when users are uncertain vs. indifferent
- Adapt depth based on their interest level

Current category being explored: {category_name}
User's interest level in this topic: {interest_level}
```

### Question Templates:
```
Initial: "How important is {category} in your investment decisions?"
High interest follow-up: "Let's explore {category} in more depth. Which aspects matter most to you?"
Clarification: "Just to confirm, you prioritize {aspect_a} over {aspect_b}?"
```

## Streamlit App (`app.py`)

**TODO - Will contain:**

```python
import streamlit as st
from src.llm import GeminiChat
from src.conversation import ConversationState

st.title("ESG Investment Preference Discovery")

# Initialize chat and state
if "chat" not in st.session_state:
    st.session_state.chat = GeminiChat()
    st.session_state.conversation = ConversationState()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Share your thoughts..."):
    # Process user input
    # Get LLM response
    # Update conversation state
    # Display response
```

**Features to Implement:**
- Progress bar (5 of 12 topics explored)
- Sidebar with preference summary
- Export button for final profile
- Save/resume functionality

## Output: Preference Profile

**JSON Structure:**
```json
{
  "user_id": "...",
  "timestamp": "2025-12-03T...",
  "summary": {
    "top_priorities": ["Climate Emissions", "Labor Practices"],
    "low_priorities": ["Executive Compensation"],
    "uncertain_areas": ["Water Management"]
  },
  "detailed_preferences": {
    "climate": {
      "interest_level": "high",
      "subcategories": {
        "scope1": {"priority": "high", "notes": "Wants actual reductions"},
        "scope3": {"priority": "medium"},
        "targets": {"priority": "low", "notes": "Skeptical of commitments"}
      }
    }
  },
  "conversation_metadata": {
    "duration_minutes": 18,
    "topics_explored": 8,
    "confidence_score": 0.85
  }
}
```

**Advisor Report (Human-Readable):**
```markdown
# ESG Preference Summary

**Client:** [Name]
**Date:** [Date]

## Top Priorities
1. **Climate Emissions (High Priority)**
   - Focus on Scope 1 & 2 reductions (actual operational emissions)
   - Values measurable progress over commitments
   - Less concerned with Scope 3 or future targets

2. **Labor Practices (High Priority)**
   - Strong emphasis on supply chain labor standards
   - Values fair wages and safety over other labor metrics

## Areas of Lower Interest
- Executive compensation (low priority)
- Board diversity (medium - values but not primary focus)

## Recommendations
- Screen for companies with declining Scope 1/2 emissions
- Prioritize firms with supply chain labor audits
- De-emphasize governance factors in portfolio construction
```

## Development Workflow

### Phase 1: Build Prototype (2-3 days)
1. ✅ Set up project structure
2. ✅ Create ESG category data
3. ✅ Build LLM wrapper
4. 🔄 Create conversation logic
5. 🔄 Build Streamlit UI
6. 🔄 Test end-to-end flow

### Phase 2: User Testing (1 week)
1. Test with 5-10 users
2. Iterate on question phrasing
3. Refine branching logic
4. Improve preference parsing

### Phase 3: Enhancement (if validated)
1. Expand to 100-200 categories
2. Add save/resume
3. Improve report generation
4. Consider migration to Next.js/FastAPI

## Setup Instructions

### 1. Clone Repository
```bash
cd ~/Desktop/Project-Fern/Project-Fern
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up API Key
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get key from: https://aistudio.google.com/app/apikey
echo "GEMINI_API_KEY=your_actual_key_here" > .env
```

### 5. Test LLM Connection
```bash
python src/llm.py
# Should print: "✓ Gemini API connected successfully"
```

### 6. Run Streamlit App
```bash
streamlit run app.py
# Opens browser at http://localhost:8501
```

## Key Learnings & Design Decisions

### Why Streamlit for Prototype?
- ✅ Built-in chat UI (`st.chat_message`, `st.chat_input`)
- ✅ Session state management (`st.session_state`)
- ✅ No frontend coding required
- ✅ Fast iteration (change code → auto-refresh)
- ❌ Not production-ready for complex apps
- ❌ Limited UI customization

### Why Gemini vs. Claude?
- **Gemini:** Free tier, good enough for validation, 15 req/min
- **Claude:** Better quality, worth paying ~$0.015/conversation once validated

### Why JSON for Data (not database)?
- ✅ Simple for prototype
- ✅ Easy to manually edit categories
- ✅ No setup overhead
- 🔄 Migrate to SQLite when adding user accounts

### Prompt Engineering Insights
- **Neutral framing is critical** - "How important is X?" not "Do you care about X?"
- **Brief context helps** - One sentence explanation of unfamiliar terms
- **Distinguish uncertainty from indifference** - "I don't know" ≠ "I don't care"
- **Confirm interpretations** - "Just to clarify, you prioritize A over B?"

## Future Enhancements

### Short-term (if prototype validates):
- [ ] Save/resume conversations (SQLite)
- [ ] PDF report generation
- [ ] Email results to user/advisor
- [ ] Progress indicator improvements
- [ ] Add 100-200 categories

### Medium-term:
- [ ] User authentication
- [ ] Advisor dashboard (view client preferences)
- [ ] A/B test question phrasing
- [ ] Multi-language support
- [ ] Mobile-responsive UI

### Long-term:
- [ ] Integration with portfolio management tools
- [ ] Real-time ESG data feeds (via MCP servers)
- [ ] Multi-agent system (conversation agent + research agent)
- [ ] Actual investment recommendations (requires compliance review)

## Architecture: Current vs. Future

### Current (Prototype):
```
User → Streamlit UI → Python Backend → Gemini API
                    ↓
              JSON Data Files
```

### Future (Production):
```
User → Next.js Frontend → FastAPI Backend → Claude/Gemini API
                              ↓
                        PostgreSQL Database
                              ↓
                        MCP Servers (ESG data, CRM, etc.)
```

## Cost Projections

### Development (Prototype):
- Gemini API: $0 (free tier)
- Hosting: $0 (Streamlit Community Cloud free tier)
- **Total: $0**

### Production (if launched):
- Claude Haiku API: ~$1.50 per 100 conversations
- Hosting: $5-20/month (Vercel, Railway, or similar)
- Database: $0-25/month (Supabase free tier or paid)
- **Est: $10-50/month for first 1,000 conversations**

### Revenue Model (hypothetical):
- Charge advisors $50-200/month per user
- Or charge per conversation ($5-10 per client onboarding)
- API costs are <5% of revenue (high margin)

## Security & Privacy Considerations

### Current:
- ✅ `.env` in `.gitignore` (API keys not committed)
- ✅ Private GitHub repo
- ⚠️ No user authentication yet
- ⚠️ Conversations not persisted (lost on refresh)

### Future:
- [ ] User authentication (Auth0, Clerk, or similar)
- [ ] Encrypt stored preferences
- [ ] GDPR compliance (data deletion, export)
- [ ] Audit logs for advisor access
- [ ] SOC 2 compliance (if selling to institutions)

## Testing Strategy

### Manual Testing:
1. Test each category branch (high/medium/low interest)
2. Test "I don't know" responses
3. Test contradictory answers
4. Test conversation length (aim for 15-25 mins)

### User Testing:
- 5-10 beta users with diverse profiles:
  - Novice investor (knows little about ESG)
  - Sophisticated investor (specific preferences)
  - Institutional decision-maker
  - Financial advisor (to test report output)

### Metrics to Track:
- Completion rate (% who finish conversation)
- Average conversation time
- User satisfaction (post-conversation survey)
- Advisor feedback on report quality

## Common Issues & Solutions

### "GEMINI_API_KEY not found"
- Check `.env` file exists
- Verify format: `GEMINI_API_KEY=your_key_here` (no quotes)
- Restart app after creating `.env`

### Streamlit shows blank page
- Check terminal for errors
- Verify all dependencies installed: `pip install -r requirements.txt`
- Try: `streamlit run app.py --server.port 8502`

### LLM responses are slow
- Gemini Flash should respond in 1-3 seconds
- If slower, check internet connection
- Free tier limit is 15 req/min (shouldn't hit during solo testing)

## Resources & References

### APIs:
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Anthropic Claude API Docs](https://docs.anthropic.com/)
- [Streamlit Docs](https://docs.streamlit.io/)

### ESG Frameworks:
- SASB (Sustainability Accounting Standards Board)
- GRI (Global Reporting Initiative)
- TCFD (Task Force on Climate-related Financial Disclosures)

### Similar Tools (for inspiration):
- OpenInvest (ESG preference questionnaire)
- Ethic (values-based investing)
- Swell Investing (impact portfolios)

## Contact & Collaboration

**Repo:** Private (for now)
**License:** MIT
**Status:** Prototype phase (as of Dec 2025)

## Changelog

### 2025-12-03 - Initial Setup
- Created project structure
- Added 5 ESG categories with 25 subcategories
- Built Gemini API wrapper
- Set up Streamlit framework
- Created comprehensive documentation

---

**Last Updated:** 2025-12-03
**Version:** 0.1.0 (Prototype)
