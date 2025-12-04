# ESG Classifier - Quick Start Guide

## What It Does

Maps user concerns (natural language) → ESG Field IDs (standardized codes)

**Example:**
- User says: *"I'm concerned about water contamination"*
- System returns: `SR448` (Percentage of Produced Water Discharged)
- You include SR448 in your output/report

## Installation

Already installed! The framework is in `src/esg_classifier/`

## 30-Second Usage

```python
from src.esg_classifier import ESGTaxonomy, ESGMatcher, UserPriorities

# Setup (do once)
taxonomy = ESGTaxonomy.load_default()
matcher = ESGMatcher(taxonomy)
priorities = UserPriorities()

# When user expresses a concern
user_text = "We need to reduce carbon emissions"
matches = matcher.find_matches(user_text, top_k=3)

# Add to priorities
top_match = matches[0]
priorities.add(top_match['field_id'], importance="high")

# Get Field IDs for output
field_ids = priorities.get_all_field_ids()
print(f"Include these in output: {field_ids}")
# Output: Include these in output: ['SR383']
```

## What's Available

### 819 ESG Fields Across 3 Pillars

**Environmental** (730 fields)
- Air Quality, Climate Exposure, Energy Management, GHG Emissions, Water Management, Waste Management, Biodiversity, etc.

**Social** (...)
- Labor Practices, Product Safety, Community Relations, Data Privacy, Health & Safety, etc.

**Governance** (89 fields)
- Board Composition, Executive Compensation, Audit, Shareholder Rights

## Common Queries

Test these in your terminal:

```bash
python3 -c "
from src.esg_classifier import ESGTaxonomy, ESGMatcher
taxonomy = ESGTaxonomy.load_default()
matcher = ESGMatcher(taxonomy)

# Your query here
matches = matcher.find_matches('water contamination', top_k=3)
for m in matches:
    print(f'{m[\"field_name\"]} ({m[\"field_id\"]})')
"
```

Try these queries:
- `"water contamination"`
- `"carbon emissions"`
- `"employee diversity"`
- `"board independence"`
- `"renewable energy"`
- `"waste reduction"`

## Importance Levels

When adding to priorities:

```python
priorities.add(field_id, importance="critical")  # Most important
priorities.add(field_id, importance="high")      # Important
priorities.add(field_id, importance="medium")    # Moderate
priorities.add(field_id, importance="low")       # Nice to have
```

## Get Specific Priorities

```python
# All Field IDs
all_ids = priorities.get_all_field_ids()

# By importance
critical = priorities.get_critical()
high = priorities.get_high()

# Check if tracked
if priorities.has("SR362"):
    print("Water quality is a priority!")
```

## Save/Load

```python
# Save
priorities.to_json("data/user_priorities.json")

# Load
priorities = UserPriorities.from_json("data/user_priorities.json")
```

## Field Information

```python
# Get field details
field = taxonomy.get_field("SR362")
print(field['field_name'])      # "Water Discharge Quality"
print(field['pillar'])          # "Environmental"
print(field['issue'])           # "Water Management"

# Get human-readable context
context = matcher.get_field_context("SR362")
print(context)
# "Pillar: Environmental > Issue: Water Management > Sub-Issue: Water Quality > Field: Water Discharge Quality (SR362)"
```

## Browse Taxonomy

```python
# See all pillars
pillars = taxonomy.get_all_pillars()
# ['Environmental', 'Social', 'Governance']

# See all issues
issues = taxonomy.get_all_issues()
# ['Air Quality', 'Water Management', 'Board Composition', ...]

# Get fields for a specific issue
water_fields = taxonomy.get_fields_by_issue("Water Management")
for field in water_fields[:5]:
    print(f"{field['field_name']} ({field['field_id']})")
```

## Full Example

```python
from src.esg_classifier import ESGTaxonomy, ESGMatcher, UserPriorities

# Initialize
taxonomy = ESGTaxonomy.load_default()
matcher = ESGMatcher(taxonomy)
priorities = UserPriorities()

# User feedback
user_concerns = [
    "We're worried about water pollution",
    "Need to cut carbon emissions",
    "Employee safety is critical"
]

# Process each concern
for concern in user_concerns:
    # Find matches
    matches = matcher.find_matches(concern, top_k=1)

    if matches:
        field_id = matches[0]['field_id']
        field_name = matches[0]['field_name']

        # Track it
        priorities.add(
            field_id,
            importance="high",
            notes=concern
        )

        print(f"✓ {concern}")
        print(f"  → Matched: {field_name} ({field_id})")

# Summary
print(f"\nTracking {len(priorities)} ESG priorities:")
for field_id in priorities.get_all_field_ids():
    field = taxonomy.get_field(field_id)
    print(f"  - {field['field_name']} ({field_id})")

# Save for later
priorities.to_json("data/user_priorities.json")
```

## Testing

Run the example script:

```bash
python3 examples/test_esg_classifier.py
```

This shows:
- How to load the taxonomy
- How to match 5 different user statements
- How to track priorities
- How to export Field IDs

## Files

- **Data Source**: `data/All ES Scores Fields.csv`, `data/All G Scores Fields.csv`
- **Processed Taxonomy**: `data/processed/esg_taxonomy.json` (819 fields)
- **Code**: `src/esg_classifier/` (taxonomy.py, matcher.py, tracker.py)
- **Examples**: `examples/test_esg_classifier.py`
- **Docs**:
  - `src/esg_classifier/README.md` - Detailed API reference
  - `ESG_CLASSIFIER_SUMMARY.md` - Complete overview
  - `DATASET_INTERPRETATION_GUIDE.md` - How to interpret ESG datasets

## Troubleshooting

**"Taxonomy file not found"**
```bash
python3 scripts/process_esg_taxonomy.py
```

**Poor matches**
- Try more specific keywords
- Increase `top_k` to see more options
- Check the match score (>5.0 is usually good)

**Want better matching?**
- Consider using an LLM for classification (see ESG_CLASSIFIER_SUMMARY.md)
- The keyword matcher provides good candidates that an LLM can refine

## Next: Integrate Into Your App

See `ESG_CLASSIFIER_SUMMARY.md` section "Usage in Your App" for integration examples.

The basic pattern:
1. User expresses concern
2. Match to Field ID(s)
3. Track in UserPriorities
4. Export Field IDs for output

That's it! You now have standardized ESG categories for any user input.
