# ESG Dataset Interpretation Guide

## Overview
This document provides a comprehensive guide to understanding and interpreting ESG (Environmental, Social, Governance) scoring datasets. The patterns and structure described here are based on the "All ES Scores Fields.csv" sample dataset, but should apply to similar ESG scoring frameworks.

**Sample Dataset Characteristics (for reference):**
- **Total Records:** 739 rows (varies by dataset)
- **Structure:** Hierarchical ESG scoring framework
- **Industry Coverage:** 106 different industry sub-sectors (varies by dataset)
- **Scope:** Environmental and Social pillars (Governance appears to be in a separate dataset)

**Note:** Specific numbers (row counts, industry counts, field counts) will vary across different datasets, but the structural patterns and hierarchical organization should remain consistent.

---

## Dataset Structure

### 1. File Format
- **Type:** Typically CSV (Comma-Separated Values)
- **Header Rows:** Multiple rows (e.g., lines 1-9 in sample) contain metadata and hierarchical industry classifications
  - May vary in count depending on dataset complexity
  - Look for explanation rows, sector hierarchies, and column definitions
- **Data Start:** After header rows, actual scoring fields begin
  - Tip: Look for the first row with "Pillar" in column 1 as the column header row

### 2. Column Organization

#### A. Metadata Columns (Typically First 6-10 Columns)
**Common columns found in ESG datasets:**

| Column | Name | Description |
|--------|------|-------------|
| 1 | Pillar | Top-level category (Environmental, Social, Governance) |
| 2 | Issue | Second-level category within each pillar |
| 3 | Sub-Issue | Third-level category (more granular) |
| 4 | Score Field ID | Unique identifier (e.g., SR001, ST168, SA089) |
| 5 | Field Name | Human-readable name of the metric |
| 6 | Field Type | Classification of the score type |
| 7 | Underlying Field ID | Reference to base data field (may include asterisks) |
| 8 | Score Count | Number of industries this field applies to |

**Note:** Column count and order may vary. Key indicators to identify metadata columns:
- Look for hierarchical categorization (Pillar > Issue > Sub-Issue)
- Unique identifiers or codes
- Descriptive names
- Classification or type fields

**Important Notes on Column 7 (Underlying Field ID):**
- **One asterisk (*)** = Field transformation formula is used (see "Field Transformation" tab)
- **Two asterisks (**)** = Score based on a separately calculated field

#### B. Industry Columns (Remaining Columns After Metadata)
- **Variable number of industry sub-sectors** (sample dataset: 106) organized hierarchically
- **Multi-row headers** for industry classification:
  - First header row: Primary industry categories (e.g., Communications, Consumer Discretionary)
  - Second header row: Industry sub-categories (e.g., Telecommunications & Media, Apparel & Textile)
  - Third header row: Detailed industry classifications (e.g., "Advertising and Media Content")
- **Data Values:** "Y" indicates the field applies to that industry, blank means not applicable
- **Variations:** Some datasets may use different markers (X, 1, TRUE) instead of "Y"

---

## Hierarchical Framework

### Level 1: Pillars
The dataset contains two main pillars:
1. **Environmental** - Environmental impact and sustainability metrics
2. **Social** - Social responsibility and community impact metrics

### Level 2: Issues (Examples)
Environmental Pillar Issues:
- Air Quality
- Biodiversity & Natural Capital
- Climate Exposure
- Energy Management
- GHG Emissions
- Toxic Emissions & Waste
- Water Management

Social Pillar Issues:
- Human Capital Management
- Product Quality Management
- Social Supply Chain Management
- Community Relations
- Health & Safety

### Level 3: Sub-Issues (Examples)
Each Issue breaks down into more specific Sub-Issues:
- **Air Quality** → Air Emissions, Air Emissions Policies
- **Energy Management** → Energy Consumption, Energy Efficiency, Renewable Energy
- **Climate Exposure** → Transition Risk, Physical Risk

---

## Score Field Types

### 1. Headline Score
- **Example:** SR001 - ESG Score
- **Purpose:** Overall aggregated score
- **Applicability:** Typically applies to all industries in the dataset

### 2. Pillar Scores
- **Example:** SR002 - Environmental Pillar Score
- **Fields Include:**
  - Pillar Score (the actual score value)
  - Pillar Disclosure (transparency metric)
  - Pillar Percentile (relative ranking)
  - Pillar Weight (importance in overall score)

### 3. Issue Scores
- **Example:** SR208 - Air Quality Issue Score
- **Fields Include:**
  - Issue Score
  - Issue Disclosure
  - Issue Performance Score
  - Issue Weight
  - Issue Percentile
  - Issue Upper Target (benchmark)
  - Issue Lower Target (threshold)
  - BI Issue Priority (1-10 priority ranking)

### 4. Sub-Issue Scores
- **Example:** SR209 - Air Emissions Score
- **Purpose:** More granular measurement within an Issue

### 5. Field Scores
- **Example:** SR271 - Nitrogen Oxide Emissions
- **Purpose:** Individual data points/metrics
- **Most Granular Level:** Actual measurable data
- **Underlying Field ID:** References raw data field (e.g., ES007, F0949, SA089)

---

## Industry Coverage Patterns

### High Coverage Metrics (Applies to Most Industries)
**Pattern:** Universal or near-universal applicability
- **Examples from sample dataset:**
  - Energy Management Issue Score (80 industries)
  - GHG Emissions metrics
  - Total Energy Consumption
  - Environmental Pillar metrics
- **Characteristic:** Core sustainability metrics relevant across sectors

### Medium Coverage Metrics (Applies to Multiple Industry Groups)
**Pattern:** Sector-specific but spans multiple related industries
- **Examples from sample dataset:**
  - Biodiversity & Natural Capital (40 industries)
  - Air Quality (24 industries)
- **Characteristic:** Specific to heavy industries, manufacturing, energy sectors, etc.

### Low Coverage Metrics (Industry-Specific)
**Pattern:** Highly specialized to 1-10 industries
- **Examples from sample dataset:**
  - Aviation-specific: Number of Airworthiness Directives
  - Real Estate-specific: Area of Properties in Flood Zones
  - Oil & Gas-specific: Embedded Carbon in Coal Reserves
  - Healthcare-specific: Anti-Microbial Resistance Policy
- **Characteristic:** Addresses unique operational or regulatory aspects of specific sectors

---

## Key Metrics Breakdown

### Environmental Metrics Examples

#### Climate & Emissions
- **GHG Scope 1, 2, 3 Emissions**
- Carbon dioxide (CO2), Methane (CH4), Nitrous oxide (N2O)
- Climate Scenario Analysis
- Internal Carbon Pricing
- Transition Risk vs Physical Risk

#### Air Quality
- Nitrogen Oxide (NOx) Emissions
- Sulfur Dioxide (SO2/SOx) Emissions
- Volatile Organic Compounds (VOC)
- Particulate Matter (PM10)
- Carbon Monoxide (CO)
- Mercury (Hg), Lead emissions

#### Energy
- Total Energy Consumption
- Grid Electricity Used
- Renewable Energy Percentage
- Energy Intensity (Per Unit of Production)
- Fuel Type Breakdown (Coal, Natural Gas, etc.)

#### Water
- Water Withdrawal
- Water Consumption
- Water Recycled/Reused
- Water Discharge Quality
- Water Stress Exposure

#### Waste
- Hazardous Waste
- Non-Hazardous Waste
- Waste Recycled/Recovered
- Waste to Landfill

### Social Metrics Examples

#### Human Capital
- Employee Turnover Rate
- Training Hours Per Employee
- Diversity Metrics (Gender, Ethnicity)
- Employee Satisfaction
- Health & Safety (Injury rates, fatalities)

#### Product Quality
- Product Safety Incidents
- Product Recalls
- Quality Certifications
- Customer Satisfaction Metrics

#### Supply Chain
- Supplier Social Audits
- Percentage Suppliers in Non-Compliance
- Modern Slavery Statement

---

## Field ID Naming Conventions

### Prefix Patterns
- **SR###** - Standard score/rating field
- **ST###** - Sub-type or specialized field
- **SA###** - Underlying data field (assessment)
- **ES###** - Environmental data field
- **F####** - Formula-based field
- **M####** - Mining/materials specific field
- **SB###** - Sub-category field

### Examples
- SR001: ESG Score (top-level)
- SR002: Environmental Pillar Score
- SR208: Air Quality Issue Score
- ES007: Nitrogen Oxide Emissions (underlying data)
- SA089: PM10 Emissions (underlying data)

---

## Priority Scoring System

The "BI Issue Priority" field indicates importance ranking:
- **1** = Highest priority for this industry
- **2-3** = High priority
- **4-6** = Medium priority
- **7-9** = Lower priority
- **10** = Lowest priority (rare in dataset)

### Example Priority Distribution
- **Energy Management** for Electric Utilities: Priority 1
- **GHG Emissions** for Oil & Gas: Priority 1
- **Air Quality** for Cement: Priority 1
- **Biodiversity** for Agriculture: Priority 1

---

## Industry Taxonomy

**Note:** The exact industry taxonomy will vary by dataset provider and version. The example below is from the sample dataset.

### Major Sectors (Sample Dataset Example)
1. **Communications** (4 sub-industries)
   - Telecommunications & Media

2. **Consumer Discretionary** (8 sub-industries)
   - Apparel, Automotive, Retail, E-Commerce, etc.

3. **Consumer Staples** (6 sub-industries)
   - Agriculture, Food & Beverages, Retail, Tobacco & Cannabis

4. **Financials** (6 sub-industries)
   - Banking, Financial Services, Insurance

5. **Healthcare** (5 sub-industries)
   - Biotechnology, Healthcare Facilities, Medical Equipment, Pharmacies

6. **Industrial Products** (5 sub-industries)
   - Aerospace, Electrical Equipment, Machinery

7. **Industrial Services** (6 sub-industries)
   - Engineering, Transportation & Logistics, Waste Management

8. **Materials** (8 sub-industries)
   - Chemicals, Construction Materials, Metals & Mining, Steel

9. **Oil & Gas** (4 sub-industries)
   - Producers, Services & Equipment, Midstream, Refining

10. **Real Estate** (7 sub-industries)
    - Various REIT types (Residential, Commercial, Office, etc.)

11. **Renewable Energy** (3 sub-industries)
    - Biofuels, Equipment, Project Developers

12. **Technology** (3 sub-industries)
    - Semiconductors, Software, Hardware/EMS

13. **Utilities** (3 sub-industries)
    - Electric, Gas, Water

---

## Data Interpretation Best Practices

### 1. Understanding Applicability
- Check the "Score Count" (Column 8) to understand how many industries use this metric
- Review the industry columns to see which specific sectors this applies to
- Higher score counts = more universal metrics
- Lower score counts = highly specialized/sector-specific

### 2. Navigating the Hierarchy
- Start with Pillar-level scores for high-level overview
- Drill down to Issue-level for category analysis
- Go to Sub-Issue for detailed investigation
- Review Field Scores for raw data points

### 3. Comparing Across Industries
- Only compare metrics that apply to both industries (check for "Y" in both columns)
- Use percentile scores for relative comparisons
- Consider priority rankings when assessing materiality

### 4. Understanding Score Components
- **Score** = The actual value/rating
- **Disclosure** = How transparent the company is about this metric
- **Performance** = How well they perform on the metric
- **Percentile** = Ranking relative to peers
- **Weight** = Importance in calculating parent score

### 5. Target Setting
- **Upper Target** = Best-in-class benchmark
- **Lower Target** = Minimum acceptable threshold
- Use these for goal-setting and progress tracking

---

## Common Use Cases

### Use Case 1: Industry Benchmarking
**Goal:** Compare a company's environmental performance to industry peers

**Approach:**
1. Identify the company's industry column
2. Filter to metrics with "Y" in that column
3. Focus on high-priority issues (Priority 1-3)
4. Review percentile scores for relative performance
5. Compare to upper/lower targets

### Use Case 2: Portfolio ESG Screening
**Goal:** Screen multiple companies across different sectors

**Approach:**
1. Use headline scores (SR001 - ESG Score)
2. Review Pillar scores for balanced assessment
3. Check disclosure metrics to ensure data quality
4. Apply industry-appropriate thresholds based on priorities

### Use Case 3: Risk Assessment
**Goal:** Identify material ESG risks for a specific company

**Approach:**
1. Locate company's industry classification
2. Filter to Priority 1-2 issues for that industry
3. Review performance scores vs targets
4. Identify areas of non-compliance or low percentiles
5. Focus on high-weight issues in score calculation

### Use Case 4: Data Collection Planning
**Goal:** Determine what data to collect from a company

**Approach:**
1. Identify relevant industry column
2. List all fields with "Y" marking
3. Trace to "Underlying Field ID" (Column 7)
4. Note fields with asterisks (require formulas)
5. Prioritize based on BI Issue Priority rankings

---

## Important Considerations

### Data Quality Indicators
1. **Disclosure Score** - Higher disclosure = more reliable data
2. **Score Count** - Very low counts may indicate emerging/experimental metrics
3. **Blank Cells** - Metric not applicable or not material to that industry

### Limitations
1. This sample covers Environmental and Social pillars only (other datasets may include Governance)
2. Temporal aspects (year, reporting period) not visible in this structure (may be in other files)
3. Actual values/numbers not present - this is a field definition/schema reference
4. Industry taxonomy is snapshot-specific and may change over time
5. Row counts, field counts, and specific metrics will differ across datasets

### Dataset Variations to Expect
When encountering new ESG datasets, expect variations in:
- **Row count:** Can range from dozens to thousands depending on granularity
- **Industry count:** May cover fewer or more industries (50-150+ range typical)
- **Pillar coverage:** May include all three pillars (E, S, G) or just specific ones
- **Metric depth:** Some datasets have more/fewer sub-issue levels
- **Field naming:** ID conventions may differ (SR, ST, SA prefixes may vary)
- **Applicability markers:** "Y" vs "X" vs "1" vs TRUE/FALSE
- **Additional columns:** May include data sources, update frequency, reporting standards

### What Should Stay Consistent
Across most ESG scoring datasets, expect:
- Hierarchical structure (Pillar > Issue > Sub-Issue pattern)
- Industry applicability matrices
- Score type classifications (headline, pillar, issue, field)
- Priority/weighting systems
- Underlying data field references
- Distinction between disclosure and performance metrics

---

## Quick Reference Checklist

When analyzing a new ESG dataset:
- [ ] **Count rows and columns** - Understand the dataset size
- [ ] **Identify header rows vs data rows** - Determine where actual data begins
- [ ] **Map out the hierarchical structure** - Identify levels of categorization (Pillar > Issue > Sub-Issue, etc.)
- [ ] **Count metadata columns** - Determine where industry columns begin
- [ ] **Understand the industry taxonomy** - Map out how industries are organized
- [ ] **Count total industries covered** - Understand scope
- [ ] **Identify score types and their relationships** - Headline, Pillar, Issue, Sub-Issue, Field scores
- [ ] **Check for applicability matrices** - Understand which metrics apply to which industries
- [ ] **Note any special indicators** - Asterisks, codes, footnotes
- [ ] **Understand priority/weighting schemes** - If present, note the scale (1-10, etc.)
- [ ] **Identify target or benchmark fields** - Upper/lower targets, percentiles
- [ ] **Map field IDs to underlying data sources** - Trace scoring fields to raw data
- [ ] **Note data quality or disclosure indicators** - Identify transparency metrics
- [ ] **Document variations from expected patterns** - Note deviations for future reference

---

## Glossary

**ESG** - Environmental, Social, and Governance factors used to evaluate corporate sustainability and ethical impact

**Pillar** - Top-level ESG category (E, S, or G)

**Issue** - Specific area within a pillar (e.g., Climate Change, Diversity)

**Sub-Issue** - Detailed topic within an issue (e.g., GHG Emissions within Climate Change)

**Field Score** - Individual metric or data point

**Disclosure** - Measure of transparency in reporting

**Percentile** - Relative ranking (0-100, higher is better)

**Materiality** - Relevance and importance of an issue to a specific industry

**BI Issue Priority** - Bloomberg Intelligence priority ranking for an issue by industry

**REIT** - Real Estate Investment Trust

**GHG** - Greenhouse Gas

**Scope 1/2/3** - Standard GHG emission categories (direct, indirect energy, value chain)

**NOx** - Nitrogen Oxides

**SOx** - Sulfur Oxides

**VOC** - Volatile Organic Compounds

**PM10** - Particulate Matter (10 micrometers or less)

---

## Version History
- **v1.0** (2025-12-03) - Initial guide based on "All ES Scores Fields.csv" sample dataset

---

## Contact & Updates
This guide should be updated as new ESG datasets are encountered and new patterns emerge. Document any deviations or special cases for future reference.
