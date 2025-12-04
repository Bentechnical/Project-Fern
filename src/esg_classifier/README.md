# ESG Classifier Module

This module provides tools for classifying user input into standardized ESG (Environmental, Social, Governance) field categories.

## Purpose

The ESG Classifier maps natural language descriptions to standardized ESG Field IDs from a comprehensive taxonomy. This allows the application to:

1. **Understand user concerns** - Convert "I care about water contamination" into specific ESG metrics
2. **Track priorities** - Remember which ESG topics matter to each user
3. **Generate structured output** - Include relevant Field IDs in reports and analysis

## Architecture

```
src/esg_classifier/
├── __init__.py           # Module exports
├── taxonomy.py           # Load and manage ESG field taxonomy
├── matcher.py            # Match user text to Field IDs
├── tracker.py            # Track user priorities
└── README.md            # This file
```

## Quick Start

### 1. Load the Taxonomy

```python
from src.esg_classifier import ESGTaxonomy

# Load the default taxonomy
taxonomy = ESGTaxonomy.load_default()

# Get statistics
stats = taxonomy.get_stats()
print(f"Loaded {stats['total_fields']} fields")
# Output: Loaded 730 fields
```

### 2. Match User Text to Field IDs

```python
from src.esg_classifier import ESGMatcher

# Create a matcher
matcher = ESGMatcher(taxonomy)

# Find matches for user text
user_text = "I'm concerned about contamination of local freshwater"
matches = matcher.find_matches(user_text, top_k=5)

for match in matches:
    print(f"{match['field_name']} ({match['field_id']}) - Score: {match['match_score']}")
```

Output:
```
Percentage of Produced Water Injected (SR449) - Score: 6.0
Percentage of Produced Water Recycled (SR450) - Score: 6.0
Water Discharge Quality (SR362) - Score: 5.0
```

### 3. Track User Priorities

```python
from src.esg_classifier import UserPriorities

# Create a tracker
priorities = UserPriorities()

# Add fields the user cares about
priorities.add("SR362", importance="critical", notes="User very concerned about water quality")
priorities.add("SR449", importance="high")

# Check if a field is tracked
if priorities.has("SR362"):
    print("Water quality is a user priority!")

# Get all Field IDs
all_ids = priorities.get_all_field_ids()
print(f"User cares about: {all_ids}")
# Output: User cares about: ['SR362', 'SR449']
```

### 4. Save and Load Priorities

```python
# Save to JSON
priorities.to_json("data/user_priorities.json")

# Load from JSON
loaded = UserPriorities.from_json("data/user_priorities.json")
```

## API Reference

### ESGTaxonomy

Main class for loading and querying the ESG field taxonomy.

**Methods:**

- `load_default()` - Load the default taxonomy from `data/processed/esg_taxonomy.json`
- `from_json(path)` - Load from a specific JSON file
- `get_field(field_id)` - Get a field by its Field ID
- `get_fields_by_pillar(pillar)` - Get all fields for a pillar (e.g., "Environmental")
- `get_fields_by_issue(issue)` - Get all fields for an issue (e.g., "Water Management")
- `search_fields(query, limit)` - Simple text search
- `get_all_pillars()` - List all unique pillars
- `get_all_issues()` - List all unique issues
- `get_stats()` - Get taxonomy statistics

**Field Structure:**

```python
{
    "field_id": "SR362",
    "field_name": "Water Discharge Quality",
    "field_type": "Field Score",
    "pillar": "Environmental",
    "issue": "Water Management",
    "sub_issue": "Water Quality",
    "underlying_field_id": "ES045",
    "search_text": "water discharge quality water management water quality environmental"
}
```

### ESGMatcher

Matches natural language text to ESG Field IDs using keyword similarity.

**Methods:**

- `find_matches(user_text, top_k)` - Find top matching fields
- `find_by_keywords(keywords, top_k)` - Match using keyword list
- `get_field_context(field_id)` - Get human-readable context string

**Match Scoring:**

The matcher uses a weighted scoring system:
- Exact field name match: +10 points
- Word overlap in field name: +3 points per word
- Issue name match: +5 points
- Sub-issue match: +4 points
- Pillar match: +2 points
- Keyword boosts: +3 points for domain-specific keywords

**Keyword Boosting:**

Special keywords receive extra weight:
- Water: `water`, `freshwater`, `wastewater`, `contamination`, `pollution`
- Emissions: `emissions`, `ghg`, `carbon`, `co2`, `greenhouse`
- Energy: `energy`, `renewable`, `electricity`, `fuel`
- Waste: `waste`, `recycling`, `landfill`, `hazardous`
- Biodiversity: `biodiversity`, `nature`, `ecosystem`, `habitat`, `species`

### UserPriorities

Tracks which ESG fields the user cares about and their importance levels.

**Methods:**

- `add(field_id, importance, notes, added_from)` - Add a priority
- `remove(field_id)` - Remove a priority
- `update_importance(field_id, importance)` - Update importance level
- `get(field_id)` - Get priority details
- `has(field_id)` - Check if field is tracked
- `get_all_field_ids()` - List all tracked Field IDs
- `get_by_importance(importance)` - Get fields by importance level
- `get_critical()` - Get critical priority fields
- `get_high()` - Get high priority fields
- `get_medium()` - Get medium priority fields
- `get_low()` - Get low priority fields
- `to_dict()` - Export as dictionary
- `to_json(file_path)` - Save to JSON
- `from_json(file_path)` - Load from JSON
- `get_summary()` - Get counts by importance

**Importance Levels:**

- `critical` - Highest priority
- `high` - High priority
- `medium` - Medium priority
- `low` - Low priority

## Usage Examples

### Example 1: Process User Feedback

```python
from src.esg_classifier import ESGTaxonomy, ESGMatcher, UserPriorities

# Setup
taxonomy = ESGTaxonomy.load_default()
matcher = ESGMatcher(taxonomy)
priorities = UserPriorities()

# User provides feedback
user_statements = [
    "We need to reduce our carbon footprint",
    "Water conservation is really important to us",
    "Employee safety is our top concern"
]

# Process each statement
for statement in user_statements:
    matches = matcher.find_matches(statement, top_k=1)

    if matches:
        top_match = matches[0]
        field_id = top_match['field_id']

        # Add to priorities
        priorities.add(
            field_id,
            importance="high",
            added_from=statement
        )

        print(f"✓ Matched: '{statement}'")
        print(f"  → {top_match['field_name']} ({field_id})")

# Save priorities
priorities.to_json("data/user_priorities.json")
print(f"\nTracking {len(priorities)} ESG priorities")
```

### Example 2: Generate Report with Relevant Fields

```python
# Load user priorities
priorities = UserPriorities.from_json("data/user_priorities.json")

# Get high-priority field IDs for report
critical_fields = priorities.get_critical()
high_fields = priorities.get_high()

# Include these in your report/output
report_field_ids = critical_fields + high_fields

print("Report should include these ESG metrics:")
for field_id in report_field_ids:
    field = taxonomy.get_field(field_id)
    context = matcher.get_field_context(field_id)
    print(f"  - {context}")
```

### Example 3: Explore the Taxonomy

```python
# See what issues are tracked
issues = taxonomy.get_all_issues()
print("Available ESG Issues:")
for issue in issues:
    fields = taxonomy.get_fields_by_issue(issue)
    print(f"  - {issue} ({len(fields)} fields)")

# Example output:
# Available ESG Issues:
#   - Air Quality (24 fields)
#   - Water Management (45 fields)
#   - GHG Emissions Management (67 fields)
#   - ...
```

## Data Files

### Input Data

- **All ES Scores Fields.csv** - Raw CSV containing ESG field definitions
  - Location: Project root
  - Columns 1-7 contain the taxonomy metadata

### Processed Data

- **data/processed/esg_taxonomy.json** - Cleaned taxonomy in JSON format
  - Generated by: `scripts/process_esg_taxonomy.py`
  - 730 fields across Environmental and Social pillars
  - Structured for fast lookup and searching

### User Data

- **data/user_priorities.json** - Saved user priorities
  - Generated by: `UserPriorities.to_json()`
  - Contains Field IDs and importance levels

## Extending the Framework

### Adding Custom Matching Logic

You can extend `ESGMatcher` to add custom matching logic:

```python
class CustomMatcher(ESGMatcher):
    def _calculate_match_score(self, user_text_lower, field):
        # Call parent scoring
        score = super()._calculate_match_score(user_text_lower, field)

        # Add your custom logic
        if "climate" in user_text_lower and "ghg" in field['field_name'].lower():
            score += 5.0

        return score
```

### Using with LLMs

The matcher provides a starting point, but for more accurate classification, consider using an LLM:

```python
from openai import OpenAI

def classify_with_llm(user_text, taxonomy):
    """Use LLM to classify user text to ESG fields"""

    # Get potential matches as context
    matcher = ESGMatcher(taxonomy)
    candidates = matcher.find_matches(user_text, top_k=10)

    # Build prompt for LLM
    prompt = f"""
    User statement: "{user_text}"

    Potential ESG fields:
    """

    for i, field in enumerate(candidates, 1):
        prompt += f"\n{i}. {field['field_name']} ({field['field_id']})"
        prompt += f"\n   Context: {matcher.get_field_context(field['field_id'])}"

    prompt += "\n\nWhich field(s) best match the user's concern? Return Field IDs."

    # Call LLM
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse field IDs from response
    # ... (implementation depends on response format)
```

## Testing

Run the example script to see the framework in action:

```bash
python3 examples/test_esg_classifier.py
```

This will:
1. Load the taxonomy
2. Test with 5 example user statements
3. Show matching results
4. Track priorities
5. Save to JSON

## Future Enhancements

Potential improvements:

1. **Semantic Search** - Use embeddings (OpenAI, sentence-transformers) for better matching
2. **Multi-language Support** - Add translations for field names
3. **Fuzzy Matching** - Handle typos and variations better
4. **Context Awareness** - Remember previous user statements for better classification
5. **Confidence Scores** - Return probability distributions over matches
6. **Industry Filtering** - Use column 8+ to filter by industry when applicable

## Troubleshooting

### "Taxonomy file not found"

Make sure you've run the processing script:
```bash
python3 scripts/process_esg_taxonomy.py
```

This creates `data/processed/esg_taxonomy.json`.

### Poor matching results

Try these approaches:
1. Use more specific keywords in your text
2. Lower the `top_k` parameter to see more matches
3. Check the `match_score` - scores below 3.0 are usually weak matches
4. Consider using an LLM for better classification

### Missing ESG categories

The current dataset covers Environmental and Social pillars only. Governance metrics may be in a separate dataset. Check the CSV source for completeness.

## License

Part of Project Fern. See main project LICENSE file.
