# Prompt Engineering Guide for Project Fern

## Overview
This guide covers best practices for writing effective prompts for your ESG chatbot using Google's Gemini models.

---

## Core Principles

### 1. **Be Specific and Direct**
Bad: "Help the user with their preferences"
Good: "Ask the user to rate their interest in climate change on a scale of low/medium/high"

### 2. **Provide Context First**
Structure: Context → Task → Constraints → Output Format

```
You are an ESG investment advisor. [CONTEXT]
Ask the user about their climate priorities. [TASK]
Keep responses under 3 sentences. [CONSTRAINT]
End with a clear question. [OUTPUT FORMAT]
```

### 3. **Use Examples (Few-Shot Prompting)**
Show the model what you want:

```
User: "I guess climate is okay"
Response: "It sounds like climate is moderately important to you. Which specific aspects matter most - carbon emissions, renewable energy, or something else?"

User: "Climate is everything to me!"
Response: "I can tell climate is a top priority for you. Let's explore the specific climate issues you care most about..."

Now respond to: [USER INPUT]
```

---

## Important Syntax & Structure

### System Prompts
Set the model's role and behavior at initialization:
```python
chat.start_chat(system_instruction="""
You are a friendly ESG advisor.
- Use warm, conversational tone
- Keep responses 2-3 sentences
- Never be judgmental
""")
```

### Structured Output Requests
When you need specific data back:

```
Analyze this response: "{user_message}"

Output in this exact format:
Interest Level: [LOW/MEDIUM/HIGH/UNCERTAIN]
Reason: [1 sentence explanation]
Suggested Follow-up: [your next question]
```

### Chain of Thought
For complex logic, ask the model to think step-by-step:

```
Based on: "{user_message}"

Think through this:
1. What interest level are they expressing?
2. Are they certain or uncertain?
3. Do they want more detail or to move on?

Then respond naturally to the user.
```

---

## Common Pitfalls

### ❌ Vague Instructions
```python
prompt = "Respond to the user about ESG"
# Model doesn't know HOW to respond
```

### ✅ Clear Instructions
```python
prompt = f"""
Respond to: "{user_message}"

If they show HIGH interest: Ask 1 specific follow-up question
If they show LOW interest: Acknowledge and say you'll move on
Keep response under 3 sentences.
"""
```

### ❌ Multiple Conflicting Tasks
```python
# Don't do this:
"Determine interest level AND generate a response AND summarize their preferences"
# Too much at once - model will get confused
```

### ✅ Separate Concerns
```python
# First call - analyze:
"What interest level: LOW/MEDIUM/HIGH?"

# Second call - respond:
"Given they have {interest_level}, generate appropriate response"
```

---

## Project-Specific Tips

### For Your Conversation Flow

**Current Issue:** The code asks the LLM to respond, but ALSO uses a separate heuristic to determine interest. These can conflict.

**Better Approach:**

**Option 1: LLM Does Everything**
```python
prompt = f"""
User said: "{user_message}" about {category_name}

Step 1: Determine interest (LOW/MEDIUM/HIGH/UNCERTAIN)
Step 2: Respond appropriately

Format:
INTEREST: [level]
RESPONSE: [your message to user]
"""

# Then parse the output:
interest = extract_interest_level(llm_response)
response = extract_response_text(llm_response)
```

**Option 2: Separate Calls (More Control)**
```python
# Call 1 - Classify only:
classify_prompt = f"""
Classify interest level: "{user_message}"
Output only: LOW, MEDIUM, HIGH, or UNCERTAIN
"""
interest = chat.send_message(classify_prompt).strip()

# Call 2 - Generate response based on classification:
response_prompt = f"""
User has {interest} interest in {category}.
Generate a natural 2-3 sentence response that:
- Acknowledges their level of interest
- {'Asks a follow-up question' if interest == 'HIGH' else 'Transitions to next topic'}
"""
response = chat.send_message(response_prompt)
```

---

## Testing Prompts

### Quick Test Loop
```python
# In your terminal:
python3 src/llm.py

# Or create a test file:
# test_prompt.py
from src.llm import GeminiChat
from dotenv import load_dotenv

load_dotenv()
chat = GeminiChat()
chat.start_chat(system_instruction="Your system prompt here")

# Test different user inputs:
test_inputs = [
    "I really care about climate change",
    "Not sure about governance",
    "Don't care about diversity"
]

for user_input in test_inputs:
    response = chat.send_message(f"Your prompt template: {user_input}")
    print(f"Input: {user_input}")
    print(f"Output: {response}\n")
```

---

## Advanced Techniques

### Temperature Control
```python
# Lower = more consistent/predictable (0.0 - 1.0)
# Higher = more creative/varied

# For classification tasks:
model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content(
    prompt,
    generation_config={'temperature': 0.1}  # Very consistent
)

# For creative responses:
generation_config={'temperature': 0.7}  # More natural variety
```

### Token Limits
```python
generation_config={
    'max_output_tokens': 100,  # Keep responses short
    'temperature': 0.7
}
```

---

## Debugging Checklist

When the bot misbehaves:

1. **Print the actual prompts** being sent
   ```python
   print(f"PROMPT: {interpretation_prompt}")
   print(f"RESPONSE: {llm_response}")
   ```

2. **Test prompts in isolation** (outside Streamlit)

3. **Check for state issues** - Is conversation history getting polluted?

4. **Simplify** - Remove complexity until it works, then add back

5. **Read the model's actual output** - Often it's doing what you asked, just not what you meant

---

## Resources

- [Google Gemini Prompt Guide](https://ai.google.dev/gemini-api/docs/prompting-intro)
- [Prompting Best Practices](https://ai.google.dev/gemini-api/docs/prompting-strategies)

---

## Quick Reference

| Goal | Technique |
|------|-----------|
| Consistent format | Provide exact output template |
| Better accuracy | Add examples (few-shot) |
| Complex reasoning | Use chain-of-thought |
| Short responses | Set token limit + explicit instruction |
| Reduce randomness | Lower temperature (0.1-0.3) |
| Natural conversation | Higher temperature (0.7-0.9) |
