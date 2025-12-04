"""
ESG Investment Preference Chatbot - Streamlit Application
"""

import streamlit as st
import os
import time
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
    page_title="Ferne",
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

    if "awaiting_start_confirmation" not in st.session_state:
        st.session_state.awaiting_start_confirmation = False

    if "current_category_id" not in st.session_state:
        st.session_state.current_category_id = None

    if "category_turn_count" not in st.session_state:
        st.session_state.category_turn_count = 0

    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = True  # Enable debug logging by default

    if "debug_panel_expanded" not in st.session_state:
        st.session_state.debug_panel_expanded = False

    if "last_processing_result" not in st.session_state:
        st.session_state.last_processing_result = None

    if "mentioned_issues" not in st.session_state:
        st.session_state.mentioned_issues = set()  # Track which Issues user mentioned in Pillar intro


def add_message(role: str, content: str):
    """
    Add a message to chat history

    Args:
        role: Message role (user/assistant)
        content: Message content
    """
    st.session_state.messages.append({"role": role, "content": content})


def stream_message(message_placeholder, content: str, delay: float = 0.01):
    """
    Display message with typewriter effect

    Args:
        message_placeholder: Streamlit placeholder to write to
        content: Message content to display
        delay: Delay between characters (seconds)
    """
    displayed_text = ""
    for char in content:
        displayed_text += char
        message_placeholder.markdown(displayed_text + "▌")
        time.sleep(delay)
    message_placeholder.markdown(content)


def parse_llm_classification(llm_output: str) -> tuple:
    """
    Parse structured LLM output to extract interest level, suggested action, response, and mentioned issues

    Args:
        llm_output: LLM output in format:
            INTEREST_LEVEL: X
            SUGGESTED_ACTION: Y
            RESPONSE: Z
            MENTIONED_ISSUES: [optional, for pillar intro only]

    Returns:
        Tuple of (interest_level, suggested_action, response_text, mentioned_issues)
    """
    lines = llm_output.strip().split('\n')

    interest_level = InterestLevel.MEDIUM  # Default fallback
    suggested_action = "CONTINUE"  # Default fallback
    response_text = llm_output  # Fallback to full output
    mentioned_issues = []  # List of Issue names user mentioned

    try:
        # Parse each line
        response_started = False
        response_lines = []

        for i, line in enumerate(lines):
            if 'INTEREST_LEVEL:' in line and not response_started:
                level_str = line.split('INTEREST_LEVEL:')[1].strip().upper()
                if 'HIGH' in level_str:
                    interest_level = InterestLevel.HIGH
                elif 'LOW' in level_str:
                    interest_level = InterestLevel.LOW
                elif 'UNCERTAIN' in level_str:
                    interest_level = InterestLevel.UNCERTAIN
                else:
                    interest_level = InterestLevel.MEDIUM

            elif 'SUGGESTED_ACTION:' in line and not response_started:
                action_str = line.split('SUGGESTED_ACTION:')[1].strip().upper()
                if 'NEXT_ISSUE' in action_str or 'NEXT' in action_str:
                    suggested_action = "NEXT_ISSUE"
                elif 'SKIP_PILLAR' in action_str or 'SKIP' in action_str:
                    suggested_action = "SKIP_PILLAR"
                else:
                    suggested_action = "CONTINUE"

            elif 'RESPONSE:' in line and not response_started:
                # Start capturing response text
                response_started = True
                response_lines.append(line.split('RESPONSE:')[1].strip())

            elif 'MENTIONED_ISSUES:' in line:
                # Parse mentioned issues (for pillar intro)
                issues_str = line.split('MENTIONED_ISSUES:')[1].strip()
                if issues_str.lower() != 'none':
                    # Split by comma and clean up
                    mentioned_issues = [issue.strip() for issue in issues_str.split(',') if issue.strip()]
                # Stop capturing response here
                break

            elif response_started:
                # Continue capturing response lines
                response_lines.append(line)

        # Combine response lines
        if response_lines:
            response_text = '\n'.join(response_lines).strip()

    except Exception as e:
        # If parsing fails, return defaults
        print(f"Warning: Failed to parse LLM output: {e}")

    return interest_level, suggested_action, response_text, mentioned_issues


def start_conversation():
    """Start the conversation with welcome message"""
    # Add initial message without typing (appears immediately on load)
    st.session_state.messages.append({"role": "assistant", "content": WELCOME_MESSAGE})
    st.session_state.conversation_started = True
    st.session_state.awaiting_start_confirmation = True


def ask_about_category():
    """Ask about the current category"""
    conv_state = st.session_state.conversation_state
    category = conv_state.get_current_category()

    if category is None:
        # Conversation complete
        complete_conversation()
        return

    # Ask about this category - pass category_type to get appropriate intro
    category_type = category.get('type', 'issue')
    question = get_category_intro(category['name'], category['description'], category_type)

    # Add a brief delay before showing the next question
    time.sleep(0.3)
    add_message("assistant", question)

    st.session_state.awaiting_category_response = True
    st.session_state.current_category_id = category['id']


def process_category_response(user_message: str):
    """Process user's response about a category"""
    conv_state = st.session_state.conversation_state
    category = conv_state.get_current_category()

    if category is None:
        return

    # NEW: Use enhanced processing with ESG classifier and loop detection
    processing_result = conv_state.process_user_response(
        user_message,
        category['id'],
        debug=st.session_state.debug_mode
    )

    # Store for debug panel
    st.session_state.last_processing_result = processing_result

    turn_count = processing_result['turn_count']
    commitment_detected = processing_result['commitment_detected']
    should_move_on = processing_result['should_move_on']
    is_looping = processing_result['is_looping']

    # Get category type and available issues (for Pillar intro)
    category_type = category.get('type', 'issue')
    available_issues = None

    if category_type == 'pillar_intro':
        # Get list of Issues under this Pillar for LLM to match against
        from src.taxonomy_hierarchy import TaxonomyHierarchy
        hierarchy = TaxonomyHierarchy.load_default()
        available_issues = hierarchy.get_issues(category['pillar'])

    # Use LLM to interpret the response and determine interest level
    interpretation_prompt = get_clarification_prompt(
        user_message,
        category['name'],
        turn_count,
        category_type=category_type,
        available_issues=available_issues
    )

    # Get LLM's interpretation and response (structured output with SUGGESTED_ACTION)
    llm_output = st.session_state.chat.send_message(interpretation_prompt)

    # Parse the structured output
    interest_level, suggested_action, response_text, mentioned_issues = parse_llm_classification(llm_output)

    # Display only the response part to the user
    add_message("assistant", response_text)

    # Record preference using LLM's classification
    conv_state.record_preference(
        category['id'],
        interest_level.value,
        notes=user_message
    )

    # If this was a Pillar intro and user mentioned specific Issues, track them
    if category_type == 'pillar_intro' and mentioned_issues:
        st.session_state.mentioned_issues.update(mentioned_issues)
        if st.session_state.debug_mode:
            print(f"[DEBUG] User mentioned Issues: {mentioned_issues}")
            print(f"[DEBUG] Total mentioned Issues so far: {st.session_state.mentioned_issues}")

    # Decision logic: Use SUGGESTED_ACTION from LLM + explicit move-on signals + loop prevention
    if should_move_on or is_looping:
        # User explicitly said "move on" OR we're looping (5+ turns)
        if category_type == 'pillar_intro':
            # Move to first mentioned Issue, or skip Pillar if none mentioned
            if mentioned_issues:
                _navigate_to_next_relevant_category()
            else:
                conv_state.skip_to_next_pillar()
        else:
            conv_state.move_to_next_category()
        st.session_state.needs_next_category_question = True
        st.session_state.awaiting_category_response = False
        st.session_state.category_turn_count = 0
    elif suggested_action == "SKIP_PILLAR":
        # User doesn't care about this entire Pillar - skip to next Pillar
        if category_type == 'pillar_intro':
            # Clear any mentioned issues for this Pillar
            st.session_state.mentioned_issues.clear()
        conv_state.skip_to_next_pillar()
        st.session_state.needs_next_category_question = True
        st.session_state.awaiting_category_response = False
        st.session_state.category_turn_count = 0
    elif suggested_action == "NEXT_ISSUE":
        # User has expressed their view - move to next relevant category
        if category_type == 'pillar_intro':
            # Move to first mentioned Issue, or next Pillar if none mentioned
            if mentioned_issues:
                _navigate_to_next_relevant_category()
            else:
                conv_state.skip_to_next_pillar()
        else:
            # Move to next mentioned Issue in same Pillar, or next Pillar if done
            _navigate_to_next_relevant_category()
        st.session_state.needs_next_category_question = True
        st.session_state.awaiting_category_response = False
        st.session_state.category_turn_count = 0
    else:
        # suggested_action == "CONTINUE" - stay on current category
        # User is engaged and wants to explore more
        st.session_state.awaiting_category_response = True


def _navigate_to_next_relevant_category():
    """
    Navigate to the next relevant category based on mentioned Issues.

    Logic:
    - If we're on a Pillar intro: move to first mentioned Issue in this Pillar
    - If we're on an Issue: move to next mentioned Issue in same Pillar
    - If no more mentioned Issues in this Pillar: skip to next Pillar intro
    """
    conv_state = st.session_state.conversation_state
    current_category = conv_state.get_current_category()

    if current_category is None:
        return

    current_pillar = current_category.get('pillar_id')
    current_index = conv_state.current_category_index

    # Find next relevant category
    for i in range(current_index + 1, len(conv_state.categories)):
        next_cat = conv_state.categories[i]

        # Check if this is a new Pillar intro - always include these
        if next_cat.get('type') == 'pillar_intro':
            conv_state.current_category_index = i
            # Clear mentioned issues when moving to new Pillar
            st.session_state.mentioned_issues.clear()
            return

        # Check if this Issue is in the mentioned list
        if next_cat.get('pillar_id') == current_pillar and next_cat.get('name') in st.session_state.mentioned_issues:
            conv_state.current_category_index = i
            return

    # No more relevant categories found - conversation complete
    conv_state.current_category_index = len(conv_state.categories)


def complete_conversation():
    """Complete the conversation and generate report"""
    add_message("assistant", CLOSING_MESSAGE)

    # Generate preference summary
    conv_state = st.session_state.conversation_state
    summary = conv_state.get_preference_summary()

    # Get ESG field priorities
    esg_field_data = conv_state.get_esg_field_priorities()

    # Format report with ESG field data
    report = format_preference_report(summary, esg_field_data)
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

        # Debug Panel - maintain expanded state across reruns
        with st.expander("🔍 Debug Info", expanded=st.session_state.debug_panel_expanded):
            # Toggle button for expanding/collapsing
            if st.button("📌 Keep Open" if not st.session_state.debug_panel_expanded else "📍 Auto-collapse"):
                st.session_state.debug_panel_expanded = not st.session_state.debug_panel_expanded
                st.rerun()

            debug_enabled = st.checkbox("Enable Console Logging", value=st.session_state.debug_mode)
            st.session_state.debug_mode = debug_enabled

            if st.session_state.last_processing_result:
                result = st.session_state.last_processing_result
                conv_state = st.session_state.conversation_state

                st.markdown("**Last Response Processing:**")
                st.markdown(f"- Turn count: `{result.get('turn_count', 0)}`")
                st.markdown(f"- Explicit move-on signal: `{result.get('commitment_detected', False)}`")
                st.markdown(f"- Loop prevention (5+ turns): `{result.get('is_looping', False)}`")
                st.markdown(f"- Should move on: `{result.get('should_move_on', False)}`")

                # Show matched fields with names
                if result.get('esg_matches'):
                    st.markdown("**Matched ESG Fields:**")
                    for match in result['esg_matches'][:3]:
                        if match['match_score'] >= 3.0:
                            st.markdown(f"- `{match['field_id']}`: {match['field_name']}")
                            st.caption(f"  Score: {match['match_score']:.1f}")
            else:
                st.caption("No processing data yet")

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
        avatar = "🌱" if message["role"] == "assistant" else None
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Start conversation if not started
    if not st.session_state.conversation_started:
        start_conversation()
        st.rerun()

    # Chat input (disabled if conversation complete)
    if not st.session_state.conversation_complete:
        if prompt := st.chat_input("Share your thoughts..."):
            # Add user message
            add_message("user", prompt)

            # Display user message immediately
            with st.chat_message("user"):
                st.markdown(prompt)

            # Process response and show with typewriter effect
            with st.chat_message("assistant", avatar="🌱"):
                message_placeholder = st.empty()

                # Handle initial start confirmation
                if st.session_state.awaiting_start_confirmation:
                    st.session_state.awaiting_start_confirmation = False
                    ask_about_category()
                    last_message = st.session_state.messages[-1]["content"]
                    stream_message(message_placeholder, last_message)

                elif st.session_state.awaiting_category_response:
                    process_category_response(prompt)
                    last_message = st.session_state.messages[-1]["content"]
                    stream_message(message_placeholder, last_message)

                else:
                    # General conversation - let LLM respond
                    response = st.session_state.chat.send_message(prompt)
                    add_message("assistant", response)
                    stream_message(message_placeholder, response)

            # Check if we need to ask a follow-up question (AFTER closing previous chat message)
            if st.session_state.get("needs_next_category_question", False):
                st.session_state.needs_next_category_question = False
                time.sleep(0.5)
                with st.chat_message("assistant", avatar="🌱"):
                    follow_up_placeholder = st.empty()
                    ask_about_category()
                    next_question = st.session_state.messages[-1]["content"]
                    stream_message(follow_up_placeholder, next_question)

            st.rerun()
    else:
        # Conversation complete - show download button
        st.success("✅ Conversation complete!")

        summary = st.session_state.conversation_state.get_preference_summary()
        esg_field_data = st.session_state.conversation_state.get_esg_field_priorities()
        report = format_preference_report(summary, esg_field_data)

        st.download_button(
            label="📥 Download Your ESG Profile",
            data=report,
            file_name="esg_preference_profile.md",
            mime="text/markdown"
        )


if __name__ == "__main__":
    main()
