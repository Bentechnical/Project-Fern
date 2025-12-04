"""
LLM wrapper for Google Gemini API
Provides a simple interface for chat completions
"""

import os
import google.generativeai as genai
from typing import List, Dict


class GeminiChat:
    """Wrapper for Google Gemini chat completions"""

    def __init__(self, api_key: str = None, model_name: str = "gemini-2.0-flash"):
        """
        Initialize Gemini chat client

        Args:
            api_key: Gemini API key (will use GEMINI_API_KEY env var if not provided)
            model_name: Model to use (default: gemini-1.5-flash for free tier)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        self.chat_session = None

    def start_chat(self, system_instruction: str = None):
        """
        Start a new chat session

        Args:
            system_instruction: System-level instructions for the model
        """
        config = {}
        if system_instruction:
            # Create a new model instance with system instruction
            self.model = genai.GenerativeModel(
                model_name=self.model.model_name,
                system_instruction=system_instruction
            )

        self.chat_session = self.model.start_chat(history=[])

    def send_message(self, message: str) -> str:
        """
        Send a message and get response

        Args:
            message: User message to send

        Returns:
            Model's response text
        """
        if not self.chat_session:
            self.start_chat()

        response = self.chat_session.send_message(message)
        return response.text

    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Get the chat history

        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        if not self.chat_session:
            return []

        history = []
        for message in self.chat_session.history:
            history.append({
                "role": message.role,
                "content": message.parts[0].text
            })
        return history


def test_connection():
    """Test Gemini API connection"""
    try:
        chat = GeminiChat()
        chat.start_chat(system_instruction="You are a helpful assistant.")
        response = chat.send_message("Hello! Please respond with 'Connection successful!'")
        print(f"✓ Gemini API connected successfully")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"✗ Gemini API connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection when run directly
    test_connection()
