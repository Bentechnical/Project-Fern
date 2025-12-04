# Testing Guide - Loop Fix & ESG Integration

## How to Test

### Run the App
```bash
streamlit run app.py
```

## Test Scenarios

### ✅ Scenario 1: Direct Commitment (Should NOT Loop)

**Steps:**
1. Start conversation
2. When asked about Water Management, say: **"high"** or **"very important"**
3. System asks subcategory question
4. Respond: **"Water Stress Areas resonate with me"**

**Expected Behavior:**
- System acknowledges your preference
- **Moves to next category (Climate & Emissions or Labor)**
- Does NOT re-ask the subcategory question

**Signals to Look For:**
- In console/logs: `commitment_detected = True`
- In console/logs: `should_move_on = True`
- Conversation advances to new topic

---

### ✅ Scenario 2: Multiple Commitment Phrases

**Steps:**
1. When asked about Water Management, say: **"I care about this"**
2. System asks subcategory question
3. Try any of these:
   - "Water Quality matters to me"
   - "I'm interested in Water Consumption"
   - "That one" (referring to a subcategory)
   - "Yes, Water Stress"

**Expected Behavior:**
- System recognizes commitment on ANY of these phrases
- Moves to next category
- Does NOT loop

---

### ✅ Scenario 3: Loop Prevention (Vague Responses)

**Steps:**
1. When asked about Water Management, say: **"high"**
2. System asks subcategory question
3. Give vague response: **"I guess quality?"**
4. System might ask for clarification
5. Give another vague response: **"Kind of, not really"**
6. Give third vague response: **"I don't understand the question"**

**Expected Behavior:**
- After **3 turns** on the same topic, system should:
  - Detect `is_looping = True`
  - Force `should_move_on = True`
  - Move to next category
- Prevents infinite back-and-forth

---

### ✅ Scenario 4: Low Interest (Should Move On Quickly)

**Steps:**
1. When asked about any category, say: **"low"** or **"not important"**

**Expected Behavior:**
- System acknowledges
- **Immediately** moves to next category
- Does NOT ask subcategory question

---

### ✅ Scenario 5: ESG Field Matching

**Steps:**
1. Throughout conversation, express specific concerns:
   - "I'm concerned about carbon emissions"
   - "Water contamination is important"
   - "Employee diversity matters"
   - "Board independence is key"

2. Complete the conversation
3. Check the final report/export

**Expected Behavior:**
- System should track specific ESG Field IDs
- Console should show matches like:
  - "Scope 1 GHG Emissions (SR383)"
  - "Water Discharge Quality (SR362)"
- Final report includes a section: **"📊 Specific ESG Metrics Matched"**
- Field IDs are displayed with full context:
  - Field ID (e.g., SR383)
  - Field Name (e.g., "Scope 1 GHG Emissions")
  - Issue and Sub-Issue classifications

**To Verify:**
- Scroll to bottom of final report
- Look for "Specific ESG Metrics Matched" section
- Verify Field IDs match your stated concerns

---

## Debugging

### Check Console Logs

When testing, watch for these in the console:

```
Processing user response...
turn_count: 1
commitment_detected: True
is_looping: False
should_move_on: True
```

### Force Debug Output

Add to `app.py` temporarily:

```python
# In process_category_response(), after processing_result:
print(f"DEBUG: {processing_result}")
```

### Check ESG Classifier

Test if classifier is working:

```python
python3 -c "
from src.esg_classifier import ESGTaxonomy, ESGMatcher
taxonomy = ESGTaxonomy.load_default()
matcher = ESGMatcher(taxonomy)
matches = matcher.find_matches('water stress areas', top_k=3)
for m in matches:
    print(f'{m[\"field_name\"]} ({m[\"field_id\"]})')
"
```

Should output water-related fields.

---

## Common Issues

### Issue 1: Still Looping

**Symptoms:** Subcategory question asked multiple times

**Check:**
1. Is commitment detection working?
   - Look for `commitment_detected` in logs
   - Verify commitment phrases are in response

2. Is subcategory tracking working?
   - Check `conv_state.subcategory_asked`
   - Should be `{category_id: True}` after first ask

**Fix:**
- Ensure you're using commitment phrases: "resonate", "interested in", "care about", etc.
- Or wait for 3 turns - loop prevention will kick in

### Issue 2: ESG Classifier Not Working

**Symptoms:** No Field IDs tracked, no matches found

**Check:**
```bash
# Verify taxonomy exists
ls data/processed/esg_taxonomy.json

# Verify it loads
python3 -c "from src.esg_classifier import ESGTaxonomy; ESGTaxonomy.load_default()"
```

**Fix:**
```bash
# Reprocess taxonomy
python3 scripts/process_esg_taxonomy.py
```

### Issue 3: Moving Too Fast

**Symptoms:** System moves to next topic before user is done

**This is expected if:**
- User uses commitment phrases ("yes", "that one", "resonate")
- User has been discussing topic for 3+ turns

**To Explore More:**
- Don't use strong commitment language
- Ask clarifying questions instead
- System will stay on topic if you're uncertain

---

## Success Criteria

### ✅ Loop Prevention Works
- No infinite loops on any topic
- Maximum 3 turns before force move-on
- Commitment detection works on first try

### ✅ ESG Integration Works
- User statements mapped to Field IDs
- Field priorities tracked
- Accessible in `conv_state.get_esg_field_priorities()`

### ✅ Natural Flow
- Conversation feels natural
- System respects user's clear preferences
- Doesn't waste time re-asking
- Moves on when appropriate

---

## Quick Test Script

Run through this in <5 minutes:

1. Start app
2. **Water:** Say "high" → then "Water Stress Areas resonate"
   - ✅ Should move to next topic immediately
3. **Climate:** Say "low"
   - ✅ Should skip subcategories, move on
4. **Labor:** Say "very important" → then give 3 vague responses
   - ✅ Should force move-on after turn 3
5. **Diversity:** Say "Board diversity is important"
   - ✅ Should detect commitment, track Field ID

If all 5 work: **System is functioning correctly!**

---

## Next: Production Testing

Once basic testing passes:

1. **User Testing**
   - Have real users try the conversation
   - Watch for edge cases
   - Collect feedback

2. **Edge Cases**
   - User changes their mind mid-topic
   - User asks unrelated questions
   - User gives contradictory answers

3. **Performance**
   - Check ESG matcher speed (<100ms per query)
   - Verify memory usage is reasonable
   - Test with full conversation (all 5 categories)

4. **Export**
   - Verify Field IDs appear in final report
   - Test download functionality
   - Check JSON export format

---

## Support

**If you encounter issues:**

1. Check console logs for error messages
2. Verify ESG taxonomy loaded: `conv_state.taxonomy is not None`
3. Check turn counts: `conv_state.topic_turn_counts`
4. Verify commitment phrases are being detected

**To reset:**
- Click "Start Over" button in sidebar
- Or close/reopen browser tab

Happy testing!
