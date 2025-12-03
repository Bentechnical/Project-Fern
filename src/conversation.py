"""
Conversation state management and routing logic
"""

import json
from typing import Dict, List, Optional
from enum import Enum


class InterestLevel(Enum):
    """User's interest level in a category"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"
    UNKNOWN = "unknown"


class ConversationState:
    """Manages conversation state and preference tracking"""

    def __init__(self, esg_data_path: str = "data/esg_categories.json"):
        """
        Initialize conversation state

        Args:
            esg_data_path: Path to ESG categories JSON file
        """
        # Load ESG categories
        with open(esg_data_path, 'r') as f:
            data = json.load(f)
            self.categories = data['categories']

        # Track conversation progress
        self.current_category_index = 0
        self.current_subcategory_index = 0
        self.exploring_subcategories = False

        # Track user preferences
        self.preferences = {}  # category_id -> preference data
        self.conversation_log = []  # Full conversation history

        # Conversation metadata
        self.topics_explored = 0
        self.topics_total = len(self.categories)

    def get_current_category(self) -> Optional[Dict]:
        """Get the current category being discussed"""
        if self.current_category_index >= len(self.categories):
            return None
        return self.categories[self.current_category_index]

    def get_progress(self) -> Dict:
        """Get conversation progress"""
        return {
            "current": self.current_category_index + 1,
            "total": self.topics_total,
            "percentage": int((self.current_category_index / self.topics_total) * 100)
        }

    def record_preference(self, category_id: str, interest_level: str, notes: str = ""):
        """
        Record user's preference for a category

        Args:
            category_id: ID of the category
            interest_level: User's interest level (high/medium/low/uncertain)
            notes: Additional context or specific preferences
        """
        self.preferences[category_id] = {
            "interest_level": interest_level,
            "notes": notes,
            "subcategories": {}
        }
        self.topics_explored += 1

    def record_subcategory_preference(self, category_id: str, subcategory_id: str, notes: str = ""):
        """Record preference for a subcategory"""
        if category_id not in self.preferences:
            self.preferences[category_id] = {"interest_level": "unknown", "subcategories": {}}

        self.preferences[category_id]["subcategories"][subcategory_id] = {
            "notes": notes
        }

    def should_explore_subcategories(self, category_id: str) -> bool:
        """
        Determine if we should explore subcategories based on user's interest

        Args:
            category_id: ID of the category

        Returns:
            True if we should dive deeper, False otherwise
        """
        if category_id not in self.preferences:
            return False

        interest = self.preferences[category_id].get("interest_level", "unknown")
        return interest == InterestLevel.HIGH.value

    def move_to_next_category(self):
        """Advance to the next category"""
        self.current_category_index += 1
        self.current_subcategory_index = 0
        self.exploring_subcategories = False

    def is_conversation_complete(self) -> bool:
        """Check if we've covered all categories"""
        return self.current_category_index >= len(self.categories)

    def get_preference_summary(self) -> Dict:
        """
        Generate a summary of user preferences

        Returns:
            Dictionary with categorized preferences
        """
        high_priority = []
        medium_priority = []
        low_priority = []
        uncertain = []

        for cat_id, pref in self.preferences.items():
            # Find category name
            cat_name = next((c['name'] for c in self.categories if c['id'] == cat_id), cat_id)

            interest = pref.get('interest_level', 'unknown')
            item = {
                'name': cat_name,
                'notes': pref.get('notes', ''),
                'subcategories': pref.get('subcategories', {})
            }

            if interest == InterestLevel.HIGH.value:
                high_priority.append(item)
            elif interest == InterestLevel.MEDIUM.value:
                medium_priority.append(item)
            elif interest == InterestLevel.LOW.value:
                low_priority.append(item)
            elif interest == InterestLevel.UNCERTAIN.value:
                uncertain.append(item)

        return {
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "uncertain": uncertain,
            "topics_explored": self.topics_explored,
            "topics_total": self.topics_total
        }

    def interpret_interest_level(self, user_message: str) -> InterestLevel:
        """
        Interpret user's interest level from their message
        This is a simple heuristic - in practice, the LLM does this interpretation

        Args:
            user_message: User's response

        Returns:
            Estimated interest level
        """
        message_lower = user_message.lower()

        # High interest indicators
        high_keywords = ['very important', 'top priority', 'care a lot', 'really matters',
                        'essential', 'critical', 'key concern', 'extremely']
        if any(keyword in message_lower for keyword in high_keywords):
            return InterestLevel.HIGH

        # Low interest indicators
        low_keywords = ['not important', "don't care", 'not a priority', "doesn't matter",
                       'not concerned', 'low priority', 'skip']
        if any(keyword in message_lower for keyword in low_keywords):
            return InterestLevel.LOW

        # Uncertain indicators
        uncertain_keywords = ["don't know", 'not sure', 'uncertain', "haven't thought",
                            'unfamiliar', 'what is', 'explain']
        if any(keyword in message_lower for keyword in uncertain_keywords):
            return InterestLevel.UNCERTAIN

        # Default to medium
        return InterestLevel.MEDIUM


def load_esg_categories(file_path: str = "data/esg_categories.json") -> List[Dict]:
    """Load ESG categories from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
        return data['categories']


def format_preference_report(summary: Dict) -> str:
    """
    Format preference summary into a readable report

    Args:
        summary: Preference summary from get_preference_summary()

    Returns:
        Formatted markdown report
    """
    report = "# Your ESG Investment Preference Profile\n\n"

    # High priorities
    if summary['high_priority']:
        report += "## 🎯 Top Priorities\n\n"
        for item in summary['high_priority']:
            report += f"### {item['name']}\n"
            if item['notes']:
                report += f"{item['notes']}\n"
            if item['subcategories']:
                report += "\n**Specific interests:**\n"
                for sub_id, sub_data in item['subcategories'].items():
                    if sub_data.get('notes'):
                        report += f"- {sub_data['notes']}\n"
            report += "\n"

    # Medium priorities
    if summary['medium_priority']:
        report += "## ✓ Areas of Interest\n\n"
        for item in summary['medium_priority']:
            report += f"- **{item['name']}**"
            if item['notes']:
                report += f": {item['notes']}"
            report += "\n"
        report += "\n"

    # Low priorities
    if summary['low_priority']:
        report += "## Low Priority Areas\n\n"
        low_names = [item['name'] for item in summary['low_priority']]
        report += ", ".join(low_names) + "\n\n"

    # Uncertain areas
    if summary['uncertain']:
        report += "## Areas for Further Discussion\n\n"
        uncertain_names = [item['name'] for item in summary['uncertain']]
        report += "You expressed uncertainty about: " + ", ".join(uncertain_names)
        report += "\n\nThese might be worth exploring further with your advisor.\n\n"

    # Footer
    report += f"\n---\n\n"
    report += f"*Based on conversation covering {summary['topics_explored']} of {summary['topics_total']} ESG topic areas*\n"

    return report
