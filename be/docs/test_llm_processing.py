"""
Test LLM post-processing with sample Browser.cash responses
"""

from scraper.llm_processor import process_with_llm

# Sample messy Browser.cash response (similar to what we actually get)
sample_trustpilot_response = """
Okay, I scrolled and found the 5 most recent reviews:

1. Ayesha Amna - November 15, 2025 - 1 star
   Review: "Words are coming off. Boots are cool, but I asked them to write 'be happy and let it be' and they charged me 20 AED per word. Now I've worn them for four days, and the 'L' in 'let it be' is coming off."

2. Dillon J - November 12, 2025 - 1 star
   Text: "Good luck returning items here. I've been waiting a month for my refund. You would think such a big company can handle a simple thing like a timely refund, but nope."

3. Ana Boutin - Nov 10, 2025 - 2 stars
   Review: "slow delivery"

4. Meltem Gocerkaya - 11/7/2025 - 1 star
   "They are just a rubbish company. Do not order online. I didn't receive my order and they didn't refund me the money."

5. Mike Jenkins - 3 days ago - 1 star
   "not at all happy, bought my son's trainers which are already torn apart now. Nike has lost its charm, cheap quality material"

That's the 5 most recent reviews I found.
"""

print("=" * 80)
print("TESTING LLM POST-PROCESSING")
print("=" * 80)

print("\n📥 INPUT (Browser.cash response):")
print("-" * 80)
print(sample_trustpilot_response)
print("-" * 80)

print("\n🤖 PROCESSING WITH LLM...")
print("-" * 80)

try:
    result = process_with_llm(
        raw_answer=sample_trustpilot_response,
        source_type="trustpilot",
        brand_name="Nike"
    )
    
    print("\n📤 OUTPUT (Structured JSON):")
    print("-" * 80)
    import json
    print(json.dumps(result, indent=2))
    print("-" * 80)
    
    print("\n✅ VALIDATION:")
    print("-" * 80)
    for idx, item in enumerate(result, 1):
        date = item.get('date', 'N/A')
        score = item.get('sentiment_score', 0.0)
        summary = item.get('summary', '')
        
        # Check date format
        import re
        date_valid = bool(re.match(r'\d{2}-\d{2}-\d{4}', date))
        
        # Check score range
        score_valid = -1.0 <= score <= 1.0
        
        # Check summary length
        summary_valid = len(summary) <= 200
        
        print(f"\nEntry {idx}:")
        print(f"  Date: {date} {'✅' if date_valid else '❌ Invalid format'}")
        print(f"  Score: {score:.2f} {'✅' if score_valid else '❌ Out of range'}")
        print(f"  Summary length: {len(summary)} chars {'✅' if summary_valid else '❌ Too long'}")
        print(f"  Summary: {summary[:80]}...")
    
    print("\n" + "=" * 80)
    print("✅ LLM POST-PROCESSING TEST PASSED!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
