"""
ESG Matcher

Maps natural language user input to ESG Field IDs using text similarity.
"""

from typing import List, Dict, Tuple
from .taxonomy import ESGTaxonomy


class ESGMatcher:
    """
    Matches user text to ESG Field IDs using keyword and semantic similarity.

    This provides a simple keyword-based matching approach. For more sophisticated
    matching, you could integrate embeddings/semantic search later.
    """

    def __init__(self, taxonomy: ESGTaxonomy):
        """
        Initialize with an ESG taxonomy.

        Args:
            taxonomy: ESGTaxonomy instance
        """
        self.taxonomy = taxonomy

    def find_matches(self, user_text: str, top_k: int = 5) -> List[Dict]:
        """
        Find matching ESG fields for user text.

        Args:
            user_text: Natural language description from user
            top_k: Number of top matches to return

        Returns:
            List of field dictionaries with match scores
        """
        user_text_lower = user_text.lower()

        # Score each field based on keyword matches
        scored_fields = []

        for field in self.taxonomy.fields:
            score = self._calculate_match_score(user_text_lower, field)
            if score > 0:
                field_with_score = field.copy()
                field_with_score['match_score'] = score
                scored_fields.append(field_with_score)

        # Sort by score (highest first) and return top_k
        scored_fields.sort(key=lambda x: x['match_score'], reverse=True)
        return scored_fields[:top_k]

    def _calculate_match_score(self, user_text_lower: str, field: Dict) -> float:
        """
        Calculate a match score between user text and a field.

        Args:
            user_text_lower: Lowercased user input
            field: Field dictionary

        Returns:
            Match score (higher is better)
        """
        score = 0.0

        # Check field name (highest weight)
        field_name_lower = field.get('field_name', '').lower()
        field_name_words = set(field_name_lower.split())
        user_words = set(user_text_lower.split())

        # Exact field name match
        if field_name_lower in user_text_lower:
            score += 10.0

        # Word overlap in field name
        common_words = field_name_words.intersection(user_words)
        score += len(common_words) * 3.0

        # Check issue (medium weight)
        issue_lower = field.get('issue', '').lower()
        if issue_lower and issue_lower in user_text_lower:
            score += 5.0

        # Check sub-issue (medium weight)
        sub_issue_lower = field.get('sub_issue', '').lower()
        if sub_issue_lower and sub_issue_lower in user_text_lower:
            score += 4.0

        # Check pillar (low weight)
        pillar_lower = field.get('pillar', '').lower()
        if pillar_lower and pillar_lower in user_text_lower:
            score += 2.0

        # Keyword boosting for common terms
        score += self._apply_keyword_boosts(user_text_lower, field)

        return score

    def _apply_keyword_boosts(self, user_text_lower: str, field: Dict) -> float:
        """
        Apply score boosts for specific keyword patterns.

        Args:
            user_text_lower: Lowercased user input
            field: Field dictionary

        Returns:
            Additional score boost
        """
        boost = 0.0
        field_name_lower = field.get('field_name', '').lower()

        # Water-related keywords
        water_keywords = ['water', 'freshwater', 'wastewater', 'contamination', 'pollution']
        if any(kw in user_text_lower for kw in water_keywords):
            if 'water' in field_name_lower:
                boost += 3.0

        # Emissions-related keywords
        # Note: Be specific about carbon dioxide vs carbon monoxide
        if 'carbon dioxide' in user_text_lower or 'co2' in user_text_lower:
            if 'carbon dioxide' in field_name_lower or 'co2' in field_name_lower:
                boost += 5.0
        elif 'carbon monoxide' in user_text_lower or ' co ' in user_text_lower:
            if 'carbon monoxide' in field_name_lower:
                boost += 5.0
        elif 'carbon' in user_text_lower and 'emissions' in user_text_lower:
            # General carbon emissions - prefer GHG/CO2 fields
            if 'greenhouse' in field_name_lower or 'ghg' in field_name_lower or 'scope' in field_name_lower:
                boost += 5.0
            elif 'carbon dioxide' in field_name_lower:
                boost += 4.0

        # GHG/greenhouse gas keywords
        ghg_keywords = ['ghg', 'greenhouse gas', 'greenhouse']
        if any(kw in user_text_lower for kw in ghg_keywords):
            if any(kw in field_name_lower for kw in ['ghg', 'greenhouse', 'scope 1', 'scope 2', 'scope 3']):
                boost += 5.0

        # Energy-related keywords
        energy_keywords = ['energy', 'renewable', 'electricity', 'fuel']
        if any(kw in user_text_lower for kw in energy_keywords):
            if 'energy' in field_name_lower or 'electricity' in field_name_lower:
                boost += 3.0

        # Waste-related keywords
        waste_keywords = ['waste', 'recycling', 'landfill', 'hazardous']
        if any(kw in user_text_lower for kw in waste_keywords):
            if 'waste' in field_name_lower:
                boost += 3.0

        # Biodiversity keywords
        biodiversity_keywords = ['biodiversity', 'nature', 'ecosystem', 'habitat', 'species']
        if any(kw in user_text_lower for kw in biodiversity_keywords):
            if 'biodiversity' in field_name_lower or 'natural capital' in field_name_lower:
                boost += 3.0

        return boost

    def find_by_keywords(self, keywords: List[str], top_k: int = 5) -> List[Dict]:
        """
        Find matches based on a list of keywords.

        Args:
            keywords: List of keyword strings
            top_k: Number of top matches to return

        Returns:
            List of matching fields
        """
        combined_text = ' '.join(keywords)
        return self.find_matches(combined_text, top_k)

    def get_field_context(self, field_id: str) -> str:
        """
        Get a human-readable context string for a field.

        Args:
            field_id: Field ID

        Returns:
            Formatted string with field context
        """
        field = self.taxonomy.get_field(field_id)
        if not field:
            return f"Field {field_id} not found"

        parts = []
        if field.get('pillar'):
            parts.append(f"Pillar: {field['pillar']}")
        if field.get('issue'):
            parts.append(f"Issue: {field['issue']}")
        if field.get('sub_issue'):
            parts.append(f"Sub-Issue: {field['sub_issue']}")
        parts.append(f"Field: {field['field_name']} ({field['field_id']})")

        return " > ".join(parts)
