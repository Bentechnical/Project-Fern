"""
System prompts and templates for ESG preference chatbot
"""

SYSTEM_PROMPT = """You are an ESG (Environmental, Social, Governance) investment preference advisor. Your role is to help users articulate their values and priorities for sustainable investing through natural, friendly conversation.

Key guidelines:
- Be warm, conversational, and non-judgmental about user preferences
- Ask clear, jargon-free questions (explain technical terms briefly when needed)
- Provide brief context when needed (1-2 sentence explanations)
- Recognize when users are uncertain vs. indifferent - these are different
- Adapt conversation depth based on their interest level
- Keep responses concise (2-4 sentences typically)
- Never assume what they should care about - let them guide priorities

Remember: There are no "right" answers. Your job is to understand THEIR values, not to advocate for specific ESG priorities."""


def get_category_intro(category_name: str, description: str) -> str:
    """Generate introduction for a new category"""
    return f"""Let's talk about **{category_name}**.

{description}

On a scale from low to high, how important is {category_name.lower()} in your investment decisions?"""


def get_subcategory_question(category_name: str, subcategories: list) -> str:
    """Generate question about which subcategories matter most"""
    subcat_names = [sub['name'] for sub in subcategories[:3]]  # Limit to first 3 for simplicity

    if len(subcategories) <= 3:
        subcat_list = "\n".join([f"- {name}" for name in subcat_names])
    else:
        subcat_list = "\n".join([f"- {name}" for name in subcat_names])
        subcat_list += f"\n- ...and {len(subcategories) - 3} other aspects"

    return f"""Since {category_name.lower()} is important to you, let's explore which specific aspects matter most:

{subcat_list}

Which of these resonate most with you, or are there other aspects of {category_name.lower()} you care about?"""


def get_clarification_prompt(user_message: str, category_name: str) -> str:
    """Generate prompt for LLM to interpret user's interest level"""
    return f"""Based on this user response about {category_name}: "{user_message}"

Determine their interest level and respond appropriately:
- If HIGH interest (they clearly care a lot): Acknowledge their interest and say you'll explore it in more depth
- If MEDIUM interest (they care but not top priority): Acknowledge and ask 1-2 brief clarifying questions
- If LOW interest (they don't care much): Acknowledge respectfully and say you'll move on
- If UNCERTAIN (they don't know): Offer a brief explanation and ask if they want to learn more or skip

Keep your response natural and conversational."""


def get_summary_prompt(preferences: dict) -> str:
    """Generate prompt for creating a preference summary"""
    return f"""Based on this conversation, create a clear summary of the user's ESG investment preferences.

Their responses so far:
{preferences}

Create a concise summary that:
1. Lists their top 2-3 priorities (what they care most about)
2. Notes any areas of lower priority
3. Mentions any areas of uncertainty
4. Uses clear, non-technical language

Keep it to 3-4 sentences total."""


def get_followup_prompt(category: str, user_interest: str) -> str:
    """Generate appropriate follow-up based on interest level"""
    prompts = {
        "high": f"I can tell {category} really matters to you. Let's dive deeper into the specific aspects that are most important.",
        "medium": f"Thanks for sharing. Can you tell me a bit more about which aspects of {category} matter most to you?",
        "low": f"I understand {category} isn't a top priority for you. That's totally fine - let's move on to other topics.",
        "uncertain": f"No worries if you're not sure about {category} yet. Would you like a brief explanation, or should we skip to topics you're more familiar with?"
    }
    return prompts.get(user_interest.lower(), prompts["medium"])


# Initial greeting
WELCOME_MESSAGE = """👋 Welcome! I'm here to help you discover and articulate your ESG investment preferences.

**What to expect:**
- We'll have a ~15-20 minute conversation about your values
- I'll ask about different aspects of sustainable investing (Environmental, Social, Governance)
- We'll spend more time on topics you care about, and skip what doesn't matter to you
- There are no right or wrong answers - this is about YOUR priorities

**At the end, you'll get:**
- A clear summary of your ESG preferences
- A report you can share with your financial advisor

Ready to get started?"""


# Closing message
CLOSING_MESSAGE = """Thank you for sharing your preferences!

I'm now generating your personalized ESG preference profile. This will include:
- Your top priorities
- Areas of lower interest
- Specific insights from our conversation

You'll be able to review, download, and share this with your financial advisor."""
