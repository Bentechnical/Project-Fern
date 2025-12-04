# Hierarchy Refactor - Taxonomy-Based Conversation Structure

## Summary

The conversation system has been refactored to use the **actual ESG taxonomy hierarchy** instead of hardcoded test categories.

## What Changed

### Before (Hardcoded)
```
data/esg_categories.json (5 arbitrary categories)
├─ Water Management
├─ Climate & Emissions
├─ Labor Practices
├─ Diversity & Inclusion
└─ Corporate Governance
```

### After (Taxonomy-Based)
```
data/processed/esg_taxonomy.json (819 fields, hierarchical)
├─ Environmental (Pillar)
│   ├─ Air Quality (Issue)
│   │   ├─ Emissions to Air (Sub-Issue)
│   │   └─ Outdoor Air Quality (Sub-Issue)
│   ├─ Biodiversity & Natural Capital (Issue)
│   ├─ Climate Exposure (Issue)
│   ├─ Energy Management (Issue)
│   └─ ... 6 more issues
├─ Social (Pillar)
│   ├─ Access & Affordability (Issue)
│   ├─ Community Rights & Relations (Issue)
│   └─ ... 9 more issues
└─ Governance (Pillar)
    ├─ Audit (Issue)
    ├─ Board Composition (Issue)
    ├─ Executive Compensation (Issue)
    └─ Shareholder Rights (Issue)
```

## New Structure

### Conversation Flow

**Level 1: Pillar Selection**
- User is asked about **Environmental**, **Social**, or **Governance**
- LLM determines interest level (HIGH, MEDIUM, LOW, UNCERTAIN)

**Level 2: Issue Exploration** (if interest is HIGH)
- System presents Issues under the Pillar
- Examples for Environmental:
  - Air Quality
  - Biodiversity & Natural Capital
  - Climate Exposure
  - Energy Management
  - Water Management
  - Waste Management
  - etc.

**Level 3: Field Matching** (via ESG Classifier)
- User mentions specific concerns
- ESG matcher maps to Field IDs
- Example: "I care about carbon emissions" → SR383 (Scope 1 GHG Emissions)

### Taxonomy Hierarchy

```
3 Pillars
└─ 25 Issues (total across all pillars)
   └─ Sub-Issues (varies by issue)
      └─ 819 Fields (specific metrics with SR### codes)
```

**Breakdown by Pillar:**
- **Environmental**: 10 Issues
- **Social**: 11 Issues
- **Governance**: 4 Issues

## Files Modified

### New Files

#### [src/taxonomy_hierarchy.py](src/taxonomy_hierarchy.py)
- `TaxonomyHierarchy` class: Loads and indexes the taxonomy
- `build_conversation_categories()`: Converts taxonomy to conversation structure
- Methods:
  - `get_pillars()` → ['Environmental', 'Governance', 'Social']
  - `get_issues(pillar)` → ['Air Quality', 'Biodiversity', ...]
  - `get_sub_issues(pillar, issue)` → ['Emissions to Air', 'Outdoor Air Quality']
  - `get_fields(pillar, issue, sub_issue)` → [{field details}, ...]

### Modified Files

#### [src/conversation.py](src/conversation.py)
**Changed:**
```python
# Old
def __init__(self, esg_data_path: str = "data/esg_categories.json"):
    with open(esg_data_path, 'r') as f:
        data = json.load(f)
        self.categories = data['categories']

# New
def __init__(self, use_taxonomy_hierarchy: bool = True):
    if use_taxonomy_hierarchy:
        from src.taxonomy_hierarchy import TaxonomyHierarchy, build_conversation_categories
        hierarchy = TaxonomyHierarchy.load_default()
        self.categories = build_conversation_categories(hierarchy)
```

**Result:**
- `self.categories` now contains 3 Pillars (not 5 hardcoded categories)
- Each Pillar has Issues as "subcategories"
- Compatible with existing conversation logic

#### [src/prompts.py](src/prompts.py)
**Updated:**
- Welcome message now mentions "Environmental, Social, and Governance (ESG)"
- Subcategory question shows up to 5 issues (was 3)
- Clearer language: "issues" instead of generic "aspects"

### Deleted Files

#### data/esg_categories.json
- Old hardcoded test data
- No longer needed - replaced by taxonomy

## Benefits

### 1. Accurate Mapping
- Conversation structure mirrors actual data structure
- No more arbitrary categories
- Every topic the system asks about exists in the taxonomy

### 2. Comprehensive Coverage
- 3 Pillars → 25 Issues → 819 Fields
- Complete coverage of ESG metrics
- User can express preferences at any level of detail

### 3. Scalability
- If taxonomy is updated (more fields added), conversation automatically includes them
- No manual updating of categories needed
- Single source of truth: `esg_taxonomy.json`

### 4. Better Field Matching
- System now asks about actual Issues from the taxonomy
- When user commits, ESG matcher finds Fields under that Issue
- More precise mapping: user statement → specific Field IDs

## How It Works Now

### Example Conversation

**1. Start with Pillar:**
```
Ferne: Let's talk about Environmental topics.
      On a scale from low to high, how important is environmental
      performance in your investment decisions?

User: Very important
```

**2. Explore Issues (if HIGH interest):**
```
Ferne: Since Environmental is important to you, let's explore which
      specific issues matter most:

      - Air Quality
      - Biodiversity & Natural Capital
      - Climate Exposure
      - Energy Management
      - Water Management
      - ...and 5 other topics

      Which of these resonate most with you?

User: I really care about water management and carbon emissions
```

**3. Map to Fields (ESG Matcher):**
```
System detects commitment: "really care about"
ESG Matcher finds:
  - Water-related fields: SR362, SR363, SR364...
  - Carbon-related fields: SR383, SR384, SR385...
Adds these Field IDs to user's priorities
```

**4. Move to Next Pillar:**
```
Ferne: Got it! I've noted your interest in water management and
      carbon emissions. Let's move on to Social topics...
```

### Conversation Length

**3 Pillars** instead of 5 categories:
- Faster conversation
- Better aligned with industry standards (ESG = Environmental, Social, Governance)
- More logical grouping

## Testing

### Quick Test

```bash
streamlit run app.py
```

**Expected behavior:**
1. First question: "Let's talk about **Environmental**"
2. If user says HIGH interest: Shows 10 environmental issues
3. Next question: "Let's talk about **Social**"
4. Final question: "Let's talk about **Governance**"
5. Report shows Field IDs mapped to user statements

### Verify Hierarchy

```python
from src.taxonomy_hierarchy import TaxonomyHierarchy

hierarchy = TaxonomyHierarchy.load_default()
print(hierarchy.get_pillars())
# ['Environmental', 'Governance', 'Social']

print(hierarchy.get_issues('Environmental'))
# ['Air Quality', 'Biodiversity & Natural Capital', ...]

print(hierarchy.get_sub_issues('Environmental', 'Water Management'))
# ['Water Consumption', 'Water Quality', 'Water Stress']
```

## Migration Notes

### No Breaking Changes

- Existing loop prevention logic: ✅ Still works
- Existing commitment detection: ✅ Still works
- Existing ESG field matching: ✅ Still works
- Existing report generation: ✅ Still works

### What's Different for Users

**Before:**
- 5 questions (Water, Climate, Labor, Diversity, Governance)

**After:**
- 3 questions (Environmental, Social, Governance)
- More comprehensive coverage under each pillar

## Future Enhancements

### Potential Improvements

1. **Dynamic Depth Control**
   - Don't over-drill into Issues user doesn't care about
   - Smart pruning based on relevance

2. **Issue Prioritization**
   - Show most commonly prioritized Issues first
   - Personalize based on user industry/context

3. **Sub-Issue Exploration**
   - Add optional Level 3: drill into Sub-Issues
   - Example: Water Management → Water Stress → Water stress in arid regions

4. **Field-Level Selection**
   - Let advanced users select specific Fields directly
   - Show Field IDs during conversation (optional)

## Summary

✅ **Conversation now uses actual taxonomy hierarchy**
✅ **3 Pillars → 25 Issues → 819 Fields**
✅ **Old test data removed**
✅ **All existing features still work**
✅ **Better alignment with ESG standards**

The system is now grounded in real data, making it more accurate, scalable, and maintainable.
