"""
ESG Taxonomy Loader

Loads and provides access to the ESG field taxonomy.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional


class ESGTaxonomy:
    """
    Loads and manages the ESG field taxonomy.

    The taxonomy contains all available ESG fields organized by:
    - Pillar (Environmental, Social, Governance)
    - Issue (e.g., Water Management, Air Quality)
    - Sub-Issue (e.g., Water Consumption, Air Emissions)
    - Field (individual metrics)
    """

    def __init__(self, taxonomy_data: dict):
        """
        Initialize with loaded taxonomy data.

        Args:
            taxonomy_data: Dictionary containing the taxonomy structure
        """
        self.version = taxonomy_data.get('version', '1.0')
        self.source = taxonomy_data.get('source', 'Unknown')
        self.fields = taxonomy_data.get('fields', [])

        # Create indices for fast lookup
        self._build_indices()

    def _build_indices(self):
        """Build indices for efficient lookup"""
        self.field_by_id = {f['field_id']: f for f in self.fields}

        # Group by pillar
        self.fields_by_pillar = {}
        for field in self.fields:
            pillar = field.get('pillar', '').strip()
            if pillar:
                if pillar not in self.fields_by_pillar:
                    self.fields_by_pillar[pillar] = []
                self.fields_by_pillar[pillar].append(field)

        # Group by issue
        self.fields_by_issue = {}
        for field in self.fields:
            issue = field.get('issue', '').strip()
            if issue:
                if issue not in self.fields_by_issue:
                    self.fields_by_issue[issue] = []
                self.fields_by_issue[issue].append(field)

    @classmethod
    def from_json(cls, json_path: str) -> 'ESGTaxonomy':
        """
        Load taxonomy from JSON file.

        Args:
            json_path: Path to the taxonomy JSON file

        Returns:
            ESGTaxonomy instance
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            taxonomy_data = json.load(f)
        return cls(taxonomy_data)

    @classmethod
    def load_default(cls) -> 'ESGTaxonomy':
        """
        Load the default taxonomy from the processed data directory.

        Returns:
            ESGTaxonomy instance
        """
        # Assume we're running from project root
        default_path = Path(__file__).parent.parent.parent / 'data' / 'processed' / 'esg_taxonomy.json'
        return cls.from_json(str(default_path))

    def get_field(self, field_id: str) -> Optional[Dict]:
        """
        Get a field by its Field ID.

        Args:
            field_id: The Field ID (e.g., 'SR362')

        Returns:
            Field dictionary or None if not found
        """
        return self.field_by_id.get(field_id)

    def get_fields_by_pillar(self, pillar: str) -> List[Dict]:
        """
        Get all fields for a specific pillar.

        Args:
            pillar: Pillar name (e.g., 'Environmental', 'Social')

        Returns:
            List of field dictionaries
        """
        return self.fields_by_pillar.get(pillar, [])

    def get_fields_by_issue(self, issue: str) -> List[Dict]:
        """
        Get all fields for a specific issue.

        Args:
            issue: Issue name (e.g., 'Water Management', 'Air Quality')

        Returns:
            List of field dictionaries
        """
        return self.fields_by_issue.get(issue, [])

    def search_fields(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Simple text search across all fields.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching field dictionaries
        """
        query_lower = query.lower()
        matches = []

        for field in self.fields:
            search_text = field.get('search_text', '')
            if query_lower in search_text:
                matches.append(field)

            if len(matches) >= limit:
                break

        return matches

    def get_all_pillars(self) -> List[str]:
        """Get list of all unique pillars"""
        return list(self.fields_by_pillar.keys())

    def get_all_issues(self) -> List[str]:
        """Get list of all unique issues"""
        return list(self.fields_by_issue.keys())

    def get_stats(self) -> Dict:
        """
        Get taxonomy statistics.

        Returns:
            Dictionary with stats about the taxonomy
        """
        return {
            'total_fields': len(self.fields),
            'total_pillars': len(self.fields_by_pillar),
            'total_issues': len(self.fields_by_issue),
            'pillars': list(self.fields_by_pillar.keys()),
            'issues': list(self.fields_by_issue.keys()),
        }
