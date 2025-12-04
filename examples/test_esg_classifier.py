"""
Example script demonstrating the ESG Classifier framework.

This shows how to:
1. Load the ESG taxonomy
2. Match user text to Field IDs
3. Track user priorities
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.esg_classifier import ESGTaxonomy, ESGMatcher, UserPriorities


def main():
    print("=" * 70)
    print("ESG Classifier Example")
    print("=" * 70)

    # 1. Load the taxonomy
    print("\n[1] Loading ESG Taxonomy...")
    taxonomy = ESGTaxonomy.load_default()
    stats = taxonomy.get_stats()

    print(f"✓ Loaded {stats['total_fields']} fields")
    print(f"  - Pillars: {', '.join(stats['pillars'])}")
    print(f"  - Total Issues: {stats['total_issues']}")

    # 2. Create a matcher
    print("\n[2] Creating ESG Matcher...")
    matcher = ESGMatcher(taxonomy)
    print("✓ Matcher ready")

    # 3. Test with example user inputs
    print("\n[3] Testing with example user inputs...\n")

    test_cases = [
        "I'm really concerned about contamination of local freshwater",
        "Our company needs to reduce carbon emissions",
        "We want to improve employee diversity and inclusion",
        "How can we reduce waste going to landfills?",
        "What about renewable energy usage?"
    ]

    user_priorities = UserPriorities()

    for i, user_text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"  User says: \"{user_text}\"")
        print(f"  Matches:")

        matches = matcher.find_matches(user_text, top_k=3)

        for j, match in enumerate(matches, 1):
            field_id = match['field_id']
            field_name = match['field_name']
            score = match['match_score']
            context = matcher.get_field_context(field_id)

            print(f"    {j}. {field_name} ({field_id}) - Score: {score:.1f}")
            print(f"       {context}")

            # Add the top match to priorities
            if j == 1:
                importance = "critical" if i <= 2 else "high"
                user_priorities.add(
                    field_id,
                    importance=importance,
                    notes=f"User mentioned: {user_text}",
                    added_from=user_text
                )

    # 4. Show tracked priorities
    print("\n" + "=" * 70)
    print("[4] User Priorities Summary")
    print("=" * 70)
    print(f"\n{user_priorities}\n")

    print("Critical Priorities:")
    for field_id in user_priorities.get_critical():
        field = taxonomy.get_field(field_id)
        print(f"  - {field['field_name']} ({field_id})")

    print("\nHigh Priorities:")
    for field_id in user_priorities.get_high():
        field = taxonomy.get_field(field_id)
        print(f"  - {field['field_name']} ({field_id})")

    # 5. Export field IDs
    print("\n" + "=" * 70)
    print("[5] Exported Field IDs for Output")
    print("=" * 70)
    all_ids = user_priorities.get_all_field_ids()
    print(f"\nField IDs to include in output: {all_ids}")

    # 6. Save to JSON
    output_path = "data/user_priorities.json"
    user_priorities.to_json(output_path)
    print(f"\n✓ Priorities saved to: {output_path}")

    print("\n" + "=" * 70)
    print("Example Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
