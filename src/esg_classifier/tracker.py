"""
User Priorities Tracker

Tracks which ESG fields/buckets the user cares about.
"""

import json
from typing import List, Dict, Optional, Set
from enum import Enum


class ImportanceLevel(str, Enum):
    """Importance levels for user priorities"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class UserPriorities:
    """
    Tracks ESG fields that the user cares about and their importance levels.
    """

    def __init__(self):
        """Initialize empty priorities"""
        # Dict: field_id -> {"importance": str, "notes": str, "added_from": str}
        self.priorities: Dict[str, Dict] = {}

    def add(self, field_id: str, importance: str = "high", notes: str = "", added_from: str = ""):
        """
        Add a field to the user's priorities.

        Args:
            field_id: ESG Field ID (e.g., 'SR362')
            importance: Importance level (critical, high, medium, low)
            notes: Optional notes about why this is important
            added_from: Optional context about where this came from (user statement)
        """
        self.priorities[field_id] = {
            "importance": importance,
            "notes": notes,
            "added_from": added_from
        }

    def remove(self, field_id: str):
        """
        Remove a field from priorities.

        Args:
            field_id: ESG Field ID to remove
        """
        if field_id in self.priorities:
            del self.priorities[field_id]

    def update_importance(self, field_id: str, importance: str):
        """
        Update the importance level of a field.

        Args:
            field_id: ESG Field ID
            importance: New importance level
        """
        if field_id in self.priorities:
            self.priorities[field_id]["importance"] = importance

    def get(self, field_id: str) -> Optional[Dict]:
        """
        Get priority details for a field.

        Args:
            field_id: ESG Field ID

        Returns:
            Priority details or None if not in priorities
        """
        return self.priorities.get(field_id)

    def has(self, field_id: str) -> bool:
        """
        Check if a field is in the user's priorities.

        Args:
            field_id: ESG Field ID

        Returns:
            True if field is tracked
        """
        return field_id in self.priorities

    def get_all_field_ids(self) -> List[str]:
        """
        Get list of all tracked Field IDs.

        Returns:
            List of Field IDs
        """
        return list(self.priorities.keys())

    def get_by_importance(self, importance: str) -> List[str]:
        """
        Get all Field IDs with a specific importance level.

        Args:
            importance: Importance level to filter by

        Returns:
            List of Field IDs
        """
        return [
            field_id
            for field_id, data in self.priorities.items()
            if data["importance"] == importance
        ]

    def get_critical(self) -> List[str]:
        """Get all critical priority Field IDs"""
        return self.get_by_importance("critical")

    def get_high(self) -> List[str]:
        """Get all high priority Field IDs"""
        return self.get_by_importance("high")

    def get_medium(self) -> List[str]:
        """Get all medium priority Field IDs"""
        return self.get_by_importance("medium")

    def get_low(self) -> List[str]:
        """Get all low priority Field IDs"""
        return self.get_by_importance("low")

    def to_dict(self) -> Dict:
        """
        Export priorities as a dictionary.

        Returns:
            Dictionary of priorities
        """
        return self.priorities.copy()

    def to_json(self, file_path: str):
        """
        Save priorities to a JSON file.

        Args:
            file_path: Path where JSON should be saved
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.priorities, f, indent=2)

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserPriorities':
        """
        Load priorities from a dictionary.

        Args:
            data: Dictionary of priorities

        Returns:
            UserPriorities instance
        """
        instance = cls()
        instance.priorities = data.copy()
        return instance

    @classmethod
    def from_json(cls, file_path: str) -> 'UserPriorities':
        """
        Load priorities from a JSON file.

        Args:
            file_path: Path to JSON file

        Returns:
            UserPriorities instance
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def get_summary(self) -> Dict:
        """
        Get a summary of tracked priorities.

        Returns:
            Summary dictionary with counts by importance
        """
        return {
            "total": len(self.priorities),
            "critical": len(self.get_critical()),
            "high": len(self.get_high()),
            "medium": len(self.get_medium()),
            "low": len(self.get_low()),
        }

    def __len__(self) -> int:
        """Number of tracked priorities"""
        return len(self.priorities)

    def __contains__(self, field_id: str) -> bool:
        """Check if field_id is in priorities"""
        return field_id in self.priorities

    def __repr__(self) -> str:
        summary = self.get_summary()
        return f"UserPriorities(total={summary['total']}, critical={summary['critical']}, high={summary['high']}, medium={summary['medium']}, low={summary['low']})"
