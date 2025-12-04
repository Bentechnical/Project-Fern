"""
Build hierarchical conversation structure from ESG taxonomy
"""

from typing import Dict, List, Set
from collections import defaultdict
from pathlib import Path
import json


class TaxonomyHierarchy:
    """
    Builds a navigable hierarchy from the ESG taxonomy:
    Pillar → Issue → Sub-Issue → Fields
    """

    def __init__(self, taxonomy_data: dict):
        """
        Initialize hierarchy from taxonomy data

        Args:
            taxonomy_data: Loaded esg_taxonomy.json data
        """
        self.fields = taxonomy_data.get('fields', [])
        self._build_hierarchy()

    def _build_hierarchy(self):
        """Build the hierarchical structure"""
        self.pillars = {}  # pillar_name -> issues dict
        self.issues_by_pillar = defaultdict(dict)  # pillar -> {issue_name -> sub_issues}
        self.sub_issues_by_issue = defaultdict(lambda: defaultdict(list))  # pillar -> issue -> [sub_issues]
        self.fields_by_sub_issue = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))  # pillar -> issue -> sub_issue -> [fields]

        for field in self.fields:
            pillar = field.get('pillar', '').strip()
            issue = field.get('issue', '').strip()
            sub_issue = field.get('sub_issue', '').strip()

            if not pillar or not issue:
                continue

            # Track pillars
            if pillar not in self.pillars:
                self.pillars[pillar] = set()

            # Track issues under pillar
            if issue not in self.issues_by_pillar[pillar]:
                self.issues_by_pillar[pillar][issue] = set()

            # Track sub-issues under issue
            if sub_issue:
                self.issues_by_pillar[pillar][issue].add(sub_issue)
                self.sub_issues_by_issue[pillar][issue].append(sub_issue)

            # Track fields under sub-issue
            self.fields_by_sub_issue[pillar][issue][sub_issue].append(field)

    def get_pillars(self) -> List[str]:
        """Get list of all pillars in standard ESG order: Environmental, Social, Governance"""
        # Return in standard ESG order, not alphabetically
        standard_order = ['Environmental', 'Social', 'Governance']
        return [p for p in standard_order if p in self.pillars]

    def get_issues(self, pillar: str) -> List[str]:
        """Get list of issues under a pillar"""
        return sorted(self.issues_by_pillar.get(pillar, {}).keys())

    def get_sub_issues(self, pillar: str, issue: str) -> List[str]:
        """Get list of sub-issues under an issue"""
        sub_issues = self.issues_by_pillar.get(pillar, {}).get(issue, set())
        return sorted([s for s in sub_issues if s])

    def get_fields(self, pillar: str, issue: str, sub_issue: str = None) -> List[Dict]:
        """
        Get fields under a sub-issue, or all fields under an issue if sub_issue is None

        Args:
            pillar: Pillar name
            issue: Issue name
            sub_issue: Optional sub-issue name

        Returns:
            List of field dictionaries
        """
        if sub_issue:
            return self.fields_by_sub_issue.get(pillar, {}).get(issue, {}).get(sub_issue, [])
        else:
            # Return all fields under this issue
            all_fields = []
            for sub in self.sub_issues_by_issue.get(pillar, {}).get(issue, []):
                all_fields.extend(self.fields_by_sub_issue[pillar][issue][sub])
            return all_fields

    def get_hierarchy_summary(self) -> Dict:
        """Get summary statistics of the hierarchy"""
        return {
            'pillar_count': len(self.pillars),
            'issue_count': sum(len(issues) for issues in self.issues_by_pillar.values()),
            'sub_issue_count': sum(
                len(sub_issues)
                for pillar_issues in self.sub_issues_by_issue.values()
                for sub_issues in pillar_issues.values()
            ),
            'field_count': len(self.fields)
        }

    @classmethod
    def load_default(cls) -> 'TaxonomyHierarchy':
        """Load hierarchy from default taxonomy location"""
        taxonomy_path = Path(__file__).parent.parent / 'data' / 'processed' / 'esg_taxonomy.json'
        with open(taxonomy_path, 'r') as f:
            taxonomy_data = json.load(f)
        return cls(taxonomy_data)


def build_conversation_categories(hierarchy: TaxonomyHierarchy) -> List[Dict]:
    """
    Build conversation categories from taxonomy hierarchy.

    TWO-PHASE STRUCTURE:
    Phase 1: Pillar Introduction - Ask broadly about what matters within each Pillar
    Phase 2: Issue Exploration - Drill into specific Issues user mentioned

    Structure:
    - 3 Pillar intro categories (Environmental, Social, Governance)
    - 25 Issue categories (specific topics within each Pillar)
    - ESG matcher automatically captures Fields in the background
    - Sub-Issues are never shown to user (too granular - 642 of them!)

    Navigation Flow:
    1. Pillar Intro: "What concerns you about Environmental topics?"
    2. User mentions specific Issues in natural language
    3. System drills into those specific Issues
    4. Skip Issues user didn't mention
    5. Move to next Pillar

    Args:
        hierarchy: TaxonomyHierarchy instance

    Returns:
        List of category dictionaries (Pillar intros + Issues)
    """
    categories = []

    for pillar in hierarchy.get_pillars():
        # Phase 1: Add Pillar introduction category
        pillar_intro = {
            'id': f"{pillar.lower().replace(' ', '_')}_intro",
            'name': pillar,
            'pillar': pillar,
            'pillar_id': pillar.lower().replace(' ', '_'),
            'description': f'{pillar} topics in general',
            'type': 'pillar_intro'  # Mark as Pillar-level intro
        }
        categories.append(pillar_intro)

        # Phase 2: Add Issue categories under this Pillar
        issues = hierarchy.get_issues(pillar)

        for issue in issues:
            category = {
                'id': f"{pillar.lower().replace(' ', '_')}_{issue.lower().replace(' ', '_').replace('&', 'and')}",
                'name': issue,
                'pillar': pillar,
                'pillar_id': pillar.lower().replace(' ', '_'),
                'description': f'{issue} within {pillar}',
                'type': 'issue'  # Mark as Issue-level category
            }
            categories.append(category)

    return categories
