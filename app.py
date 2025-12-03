"""
ESG Investment Preference Chatbot - Streamlit Application
"""

import streamlit as st
import os
from dotenv import load_dotenv
from src.llm import GeminiChat
from src.conversation import ConversationState, InterestLevel, format_preference_report
from src.prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE,
    CLOSING_MESSAGE,
    get_category_intro,
    get_subcategory_question,
    get_clarification_prompt
)

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="ESG Preference Discovery",
    page_icon="🌱",
    layout="wide"
)

# Custom CSS for better chat appearance
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .progress-text {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chat" not in st.session_state:
        try:
            st.session_state.chat = GeminiChat()
            st.session_state.chat.start_chat(system_instruction=SYSTEM_PROMPT)
        except ValueError as e:
            st.error(f"❌ {str(e)}")
            st.info("Please add your Gemini API key to the `.env` file. Get one at: https://aistudio.google.com/app/apikey")
            st.stop()

    if "conversation_state" not in st.session_state:
        st.session_state.conversation_state = ConversationState()

    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False

    if "conversation_complete" not in st.session_state:
        st.session_state.conversation_complete = False

    if "awaiting_category_response" not in st.session_state:
        st.session_state.awaiting_category_response = False

    if "current_category_id" not in st.session_state:
        st.session_state.current_category_id = None


def add_message(role: str, content: str):
    """Add a message to chat history"""
    st.session_state.messages.append({"role": role, "content": content})


def start_conversation():
    """Start the conversation with welcome message"""
    add_message("assistant", WELCOME_MESSAGE)
    st.session_state.conversation_started = True


def ask_about_category():
    """Ask about the current category"""
    conv_state = st.session_state.conversation_state
    category = conv_state.get_current_category()

    if category is None:
        # Conversation complete
        complete_conversation()
        return

    # Ask about this category
    question = get_category_intro(category['name'], category['description'])
    add_message("assistant", question)

    st.session_state.awaiting_category_response = True
    st.session_state.current_category_id = category['id']


def process_category_response(user_message: str):
    """Process user's response about a category"""
    conv_state = st.session_state.conversation_state
    category = conv_state.get_current_category()

    if category is None:
        return

    # Use LLM to interpret the response and determine interest level
    interpretation_prompt = get_clarification_prompt(user_message, category['name'])

    # Get LLM's interpretation and response
    llm_response = st.session_state.chat.send_message(interpretation_prompt)
    add_message("assistant", llm_response)

    # Simple heuristic to determine interest (in practice, we'd parse LLM's interpretation)
    interest_level = conv_state.interpret_interest_level(user_message)

    # Record preference
    conv_state.record_preference(
        category['id'],
        interest_level.value,
        notes=user_message
    )

    # Decide next step based on interest
    if interest_level == InterestLevel.HIGH and category.get('subcategories'):
        # Explore subcategories
        subcategory_q = get_subcategory_question(category['name'], category['subcategories'])
        add_message("assistant", subcategory_q)
        st.session_state.awaiting_subcategory_response = True
    else:
        # Move to next category
        conv_state.move_to_next_category()
        st.session_state.awaiting_category_response = False
        ask_about_category()


def complete_conversation():
    """Complete the conversation and generate report"""
    add_message("assistant", CLOSING_MESSAGE)

    # Generate preference summary
    conv_state = st.session_state.conversation_state
    summary = conv_state.get_preference_summary()

    # Format report
    report = format_preference_report(summary)
    add_message("assistant", report)

    st.session_state.conversation_complete = True


def main():
    """Main application"""
    initialize_session_state()

    # Sidebar
    with st.sidebar:
        st.title("🌱 ESG Preference Discovery")

        if st.session_state.conversation_started:
            st.markdown("---")
            st.subheader("Progress")

            progress = st.session_state.conversation_state.get_progress()
            st.progress(progress['percentage'] / 100)
            st.markdown(f"**Topic {progress['current']} of {progress['total']}**")

            st.markdown("---")
            st.subheader("Your Priorities So Far")

            summary = st.session_state.conversation_state.get_preference_summary()

            if summary['high_priority']:
                st.markdown("**🎯 High Priority:**")
                for item in summary['high_priority']:
                    st.markdown(f"- {item['name']}")

            if summary['medium_priority']:
                st.markdown("**✓ Medium Priority:**")
                for item in summary['medium_priority']:
                    st.markdown(f"- {item['name']}")

        st.markdown("---")
        st.caption("Built with Streamlit & Google Gemini")

        if st.button("🔄 Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Main chat area
    st.markdown('<div class="main-header">💬 Let\'s Discover Your ESG Priorities</div>', unsafe_allow_html=True)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Start conversation if not started
    if not st.session_state.conversation_started:
        start_conversation()
        ask_about_category()
        st.rerun()

    # Chat input (disabled if conversation complete)
    if not st.session_state.conversation_complete:
        if prompt := st.chat_input("Share your thoughts..."):
            # Add user message
            add_message("user", prompt)

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Process response
            with st.spinner("Thinking..."):
                if st.session_state.awaiting_category_response:
                    process_category_response(prompt)
                elif st.session_state.get("awaiting_subcategory_response", False):
                    # Record subcategory preference
                    conv_state = st.session_state.conversation_state
                    category = conv_state.get_current_category()
                    if category:
                        conv_state.record_subcategory_preference(
                            category['id'],
                            f"subcategory_response",
                            notes=prompt
                        )

                    # Move to next category
                    conv_state.move_to_next_category()
                    st.session_state.awaiting_category_response = False
                    st.session_state.awaiting_subcategory_response = False
                    ask_about_category()
                else:
                    # General conversation - let LLM respond
                    response = st.session_state.chat.send_message(prompt)
                    add_message("assistant", response)

            st.rerun()
    else:
        # Conversation complete - show download button
        st.success("✅ Conversation complete!")

        summary = st.session_state.conversation_state.get_preference_summary()
        report = format_preference_report(summary)

        st.download_button(
            label="📥 Download Your ESG Profile",
            data=report,
            file_name="esg_preference_profile.md",
            mime="text/markdown"
        )


if __name__ == "__main__":
    main()
