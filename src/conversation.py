"""
Conversation state management and routing logic
"""

import json
from typing import Dict, List, Optional
from enum import Enum
from pathlib import Path

# Import ESG classifier if available
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.esg_classifier import ESGTaxonomy, ESGMatcher, UserPriorities
    ESG_CLASSIFIER_AVAILABLE = True
except ImportError:
    ESG_CLASSIFIER_AVAILABLE = False


class InterestLevel(Enum):
    """User's interest level in a category"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"
    UNKNOWN = "unknown"


class ConversationState:
    """Manages conversation state and preference tracking"""

    def __init__(self, use_taxonomy_hierarchy: bool = True):
        """
        Initialize conversation state

        Args:
            use_taxonomy_hierarchy: If True, build categories from taxonomy (default: True)
        """
        # Load ESG categories from taxonomy hierarchy
        if use_taxonomy_hierarchy:
            from src.taxonomy_hierarchy import TaxonomyHierarchy, build_conversation_categories
            hierarchy = TaxonomyHierarchy.load_default()
            self.categories = build_conversation_categories(hierarchy)
        else:
            # Fallback to old method (deprecated)
            with open("data/esg_categories.json", 'r') as f:
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

        # NEW: Loop prevention tracking
        self.discussed_topics = set()  # Set of topic IDs that have been discussed
        self.topic_turn_counts = {}  # topic_id -> number of turns spent on topic
        self.subcategory_asked = {}  # category_id -> bool (has subcategory question been asked?)

        # NEW: ESG classifier integration
        if ESG_CLASSIFIER_AVAILABLE:
            try:
                self.taxonomy = ESGTaxonomy.load_default()
                self.matcher = ESGMatcher(self.taxonomy)
                self.field_priorities = UserPriorities()
            except Exception as e:
                print(f"Warning: Could not load ESG classifier: {e}")
                self.taxonomy = None
                self.matcher = None
                self.field_priorities = None
        else:
            self.taxonomy = None
            self.matcher = None
            self.field_priorities = None

    def get_current_category(self) -> Optional[Dict]:
        """Get the current category being discussed"""
        if self.current_category_index >= len(self.categories):
            return None
        return self.categories[self.current_category_index]

    def get_progress(self) -> Dict:
        """Get conversation progress"""
        # Cap current at total to avoid showing 4/3
        current = min(self.current_category_index + 1, self.topics_total)
        return {
            "current": current,
            "total": self.topics_total,
            "percentage": int((current / self.topics_total) * 100)
        }

    def record_preference(self, category_id: str, interest_level: str, notes: str = ""):
        """
        Record user's preference for a category

        Args:
            category_id: ID of the category
            interest_level: User's interest level (high/medium/low/uncertain)
            notes: Additional context or specific preferences
        """
        # Only increment topics_explored if this is a new category
        is_new_category = category_id not in self.preferences

        self.preferences[category_id] = {
            "interest_level": interest_level,
            "notes": notes,
            "subcategories": {}
        }

        if is_new_category:
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

        # NEW: Don't explore if we've already asked about subcategories
        if self.subcategory_asked.get(category_id, False):
            return False

        # NEW: Don't explore if topic has been discussed (commitment detected)
        if category_id in self.discussed_topics:
            return False

        interest = self.preferences[category_id].get("interest_level", "unknown")
        return interest == InterestLevel.HIGH.value

    def move_to_next_category(self):
        """Advance to the next category (Issue)"""
        self.current_category_index += 1
        self.current_subcategory_index = 0
        self.exploring_subcategories = False

    def skip_to_next_pillar(self):
        """
        Skip remaining Issues in current Pillar, jump to next Pillar.
        Used when user says they don't care about entire Pillar.
        """
        if self.current_category_index >= len(self.categories):
            return

        current_category = self.categories[self.current_category_index]
        current_pillar = current_category.get('pillar_id')

        # Find first category in next pillar
        for i in range(self.current_category_index + 1, len(self.categories)):
            if self.categories[i].get('pillar_id') != current_pillar:
                self.current_category_index = i
                return

        # No more pillars, conversation complete
        self.current_category_index = len(self.categories)

    def is_conversation_complete(self) -> bool:
        """Check if we've covered all categories"""
        return self.current_category_index >= len(self.categories)

    def process_user_response(self, user_text: str, category_id: str, debug: bool = False) -> Dict:
        """
        NEW: Process user response with ESG classifier and loop detection.

        Args:
            user_text: User's statement
            category_id: Current category being discussed
            debug: If True, print detailed logging to console

        Returns:
            Dictionary with signals about commitment, looping, and ESG matches
        """
        if debug:
            print(f"\n{'='*60}")
            print(f"PROCESSING USER RESPONSE")
            print(f"{'='*60}")
            print(f"Category: {category_id}")
            print(f"User input: '{user_text}'")

        # Track turn count for this category
        self.topic_turn_counts[category_id] = self.topic_turn_counts.get(category_id, 0) + 1
        turn_count = self.topic_turn_counts[category_id]

        if debug:
            print(f"Turn count: {turn_count}")

        result = {
            "turn_count": turn_count,
            "commitment_detected": False,
            "is_looping": False,
            "esg_matches": [],
            "matched_fields": [],  # Field IDs that were added
            "should_move_on": False
        }

        # Detect explicit "move on" signal from user
        explicit_move_on = self._detect_commitment(user_text)
        result["commitment_detected"] = explicit_move_on

        if debug:
            print(f"Explicit move-on signal: {explicit_move_on}")

        # Check for loop condition (5+ turns - failsafe for stuck conversations)
        is_looping = turn_count >= 5
        result["is_looping"] = is_looping

        if debug and is_looping:
            print(f"⚠️  Loop prevention: 5+ turns reached")

        # Use ESG classifier if available
        if self.matcher:
            try:
                matches = self.matcher.find_matches(user_text, top_k=5)
                result["esg_matches"] = matches

                if debug:
                    print(f"\nESG Matching Results:")
                    if matches:
                        for i, match in enumerate(matches[:3], 1):
                            print(f"  {i}. {match['field_id']}: {match['field_name']}")
                            print(f"     Score: {match['match_score']:.1f} | Importance: {'HIGH' if match['match_score'] > 6 else 'MEDIUM'}")
                    else:
                        print("  No matches found")

                # Add to field priorities if we have a strong match
                # Don't require commitment detection - any substantive answer should be captured
                # Lower threshold to 3.0 to capture more matches (keyword matching has limitations)
                if matches and matches[0]['match_score'] >= 3.0:
                    added_fields = []
                    for match in matches[:3]:  # Top 3 matches
                        if match['match_score'] >= 3.0:  # Only matches above threshold
                            self.field_priorities.add(
                                match['field_id'],
                                importance="high" if match['match_score'] > 6 else "medium",
                                notes=user_text,
                                added_from=user_text
                            )
                            added_fields.append(match['field_id'])

                    result["matched_fields"] = added_fields

                    if debug and added_fields:
                        print(f"\n✓ Added to priorities: {', '.join(added_fields)}")

            except Exception as e:
                print(f"Warning: ESG matching failed: {e}")

        # Mark topic as discussed if user explicitly said to move on
        if explicit_move_on:
            self.discussed_topics.add(category_id)
            result["should_move_on"] = True

        # Force move on if looping (3+ turns)
        if is_looping:
            result["should_move_on"] = True

        if debug:
            print(f"\nDecision: {'MOVE TO NEXT CATEGORY' if result['should_move_on'] else 'STAY ON TOPIC'}")
            print(f"{'='*60}\n")

        return result

    def _detect_commitment(self, user_text: str) -> bool:
        """
        Detect if user has explicitly signaled they want to move on.

        This only detects EXPLICIT move-on signals, not topic commitment.
        We rely on the LLM and turn counting for flow control.

        Args:
            user_text: User's statement

        Returns:
            True if user explicitly wants to move to next topic
        """
        user_lower = user_text.lower().strip()

        # Only detect explicit "move on" signals
        move_on_phrases = [
            "let's move on",
            "next topic",
            "move on",
            "that's all",
            "that's it",
            "that covers it",
            "nothing else",
            "we can move on",
            "ready for next",
            "next",
            "done with this"
        ]

        return any(phrase in user_lower for phrase in move_on_phrases)

    def mark_subcategory_asked(self, category_id: str):
        """
        Mark that subcategory question has been asked for this category.

        Args:
            category_id: Category ID
        """
        self.subcategory_asked[category_id] = True

    def get_esg_field_priorities(self) -> Dict:
        """
        Get ESG field priorities for export.

        Returns:
            Dictionary with field IDs and details
        """
        if not self.field_priorities:
            return {"field_ids": [], "details": []}

        field_ids = self.field_priorities.get_all_field_ids()

        return {
            "field_ids": field_ids,
            "summary": self.field_priorities.get_summary(),
            "field_details": [
                {
                    "field_id": fid,
                    **self.taxonomy.get_field(fid)
                }
                for fid in field_ids
            ] if self.taxonomy else []
        }

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


def format_preference_report(summary: Dict, esg_field_data: Optional[Dict] = None) -> str:
    """
    Format preference summary into a readable report

    Args:
        summary: Preference summary from get_preference_summary()
        esg_field_data: Optional ESG field priorities from get_esg_field_priorities()

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

    # NEW: ESG Field IDs section
    if esg_field_data and esg_field_data.get('field_ids'):
        report += "## 📊 Specific ESG Metrics Matched\n\n"
        report += "Based on your stated preferences, the following specific ESG metrics have been identified:\n\n"

        field_details = esg_field_data.get('field_details', [])
        if field_details:
            # Group by pillar for better organization
            by_pillar = {}
            for field in field_details:
                pillar = field.get('pillar', 'Other')
                if pillar not in by_pillar:
                    by_pillar[pillar] = []
                by_pillar[pillar].append(field)

            for pillar, fields in sorted(by_pillar.items()):
                if pillar:  # Skip empty pillars
                    report += f"### {pillar}\n\n"
                    for field in fields:
                        field_id = field.get('field_id', 'N/A')
                        field_name = field.get('field_name', 'Unknown')
                        issue = field.get('issue', '')
                        sub_issue = field.get('sub_issue', '')

                        report += f"**{field_id}**: {field_name}\n"
                        if issue:
                            report += f"  - *Issue*: {issue}\n"
                        if sub_issue:
                            report += f"  - *Sub-Issue*: {sub_issue}\n"
                        report += "\n"
        else:
            # Fallback: just list Field IDs
            report += ", ".join(esg_field_data['field_ids']) + "\n\n"

    # Footer
    report += f"\n---\n\n"
    report += f"*Based on conversation covering {summary['topics_explored']} of {summary['topics_total']} ESG topic areas*\n"

    return report
