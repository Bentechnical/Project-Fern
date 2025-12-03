# Quick Start Guide - Project Fern

## First Time Setup (5 minutes)

### 1. Get Your Gemini API Key
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza...`)

### 2. Set Up the Project

Open Terminal and run these commands:

```bash
# Navigate to project
cd ~/Desktop/Project-Fern/Project-Fern

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### 3. Add Your API Key

Edit the `.env` file:
```bash
# Option 1: Use a text editor
nano .env

# Option 2: Use VS Code
code .env
```

Replace `your_api_key_here` with your actual Gemini API key:
```
GEMINI_API_KEY=AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Save and close the file.

### 4. Test the Connection

```bash
python src/llm.py
```

You should see:
```
✓ Gemini API connected successfully
Response: Connection successful!
```

### 5. Run the App

```bash
streamlit run app.py
```

Your browser will open automatically to `http://localhost:8501`

---

## Every Time After (30 seconds)

```bash
# Navigate to project
cd ~/Desktop/Project-Fern/Project-Fern

# Activate virtual environment
source venv/bin/activate

# Run app
streamlit run app.py
```

---

## Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure `.env` file exists in the project root
- Check that it contains `GEMINI_API_KEY=your_key_here` (no spaces, no quotes)
- Restart the app after editing `.env`

### "No module named 'streamlit'"
- Make sure you activated the virtual environment: `source venv/bin/activate`
- You should see `(venv)` in your terminal prompt
- If still doesn't work: `pip install -r requirements.txt`

### Port already in use
- Try a different port: `streamlit run app.py --server.port 8502`
- Or kill the existing process and restart

### App is slow to respond
- Gemini free tier should respond in 1-3 seconds
- Check your internet connection
- Free tier limit: 15 requests/minute (shouldn't hit during testing)

---

## Making Changes

### Edit ESG Categories
Edit `data/esg_categories.json` to add/modify categories

### Change Prompts
Edit `src/prompts.py` to customize conversation style

### Modify Conversation Logic
Edit `src/conversation.py` to change branching behavior

**Streamlit auto-reloads** when you save files - just refresh your browser!

---

## Sharing with Others

### Option 1: Share Code (they run locally)
1. Push to GitHub (already set up)
2. Share repo URL
3. They follow this Quick Start guide

### Option 2: Deploy Online (anyone can use)
See `PROJECT_DOCUMENTATION.md` for deployment instructions

---

## Next Steps

1. **Test the conversation flow** - Go through the full experience
2. **Refine prompts** - Edit `src/prompts.py` based on how it feels
3. **Test with real users** - Get feedback from friends/advisors
4. **Read PROJECT_DOCUMENTATION.md** - Full technical details

---

Need help? Check `PROJECT_DOCUMENTATION.md` for comprehensive documentation.
