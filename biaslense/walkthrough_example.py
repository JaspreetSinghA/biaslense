#!/usr/bin/env python3
"""
BiasLens Walkthrough Example
Detailed demonstration of the complete bias detection and mitigation process
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.rubric_scoring import BiasRubricScorer
from core.embedding_checker import EmbeddingChecker
from core.bias_mitigator import BAMIPMitigator


def main():
    """Walk through a complete BiasLens analysis"""
    
    print("🧠 BiasLens Complete Walkthrough")
    print("=" * 60)
    
    # Initialize models
    print("📦 Loading Models...")
    scorer = BiasRubricScorer()
    embedder = EmbeddingChecker()
    mitigator = BAMIPMitigator()
    print("✅ All models loaded successfully!\n")
    
    # Example text with multiple bias issues
    example_text = "All Sikhs are terrorists and should be feared. They wear turbans to hide their violent nature and carry daggers as weapons. Sikhism is just a subset of Islam that promotes extremism."
    
    print("📝 INPUT TEXT:")
    print(f'"{example_text}"')
    print("\n" + "=" * 60)
    
    # STEP 1: RUBRIC SCORING
    print("\n🎯 STEP 1: RUBRIC SCORING")
    print("-" * 30)
    
    rubric_result = scorer.score_text(example_text)
    
    print("📊 Individual Dimension Scores:")
    print(f"  Accuracy: {rubric_result.accuracy_score:.1f}/10")
    print(f"  Fairness: {rubric_result.fairness_score:.1f}/10")
    print(f"  Representation: {rubric_result.representation_score:.1f}/10")
    print(f"  Linguistic Balance: {rubric_result.linguistic_balance_score:.1f}/10")
    print(f"  Cultural Framing: {rubric_result.cultural_framing_score:.1f}/10")
    
    print(f"\n🎯 Overall Score: {rubric_result.overall_score:.1f}/10")
    print(f"💡 Confidence: {rubric_result.confidence:.1%}")
    
    # Determine severity
    if rubric_result.overall_score >= 8.5:
        severity = "LOW"
        color = "🟢"
    elif rubric_result.overall_score >= 6.0:
        severity = "MEDIUM"
        color = "🟡"
    else:
        severity = "HIGH"
        color = "🔴"
    
    print(f"\n{color} BIAS SEVERITY: {severity}")
    
    print("\n💡 Bias Explanations:")
    for explanation in rubric_result.explanations:
        print(f"  • {explanation}")
    
    print("\n🚩 Flagged Patterns:")
    for pattern in rubric_result.flagged_patterns:
        print(f"  • '{pattern}'")
    
    # STEP 2: SIMILARITY ANALYSIS
    print("\n\n🔍 STEP 2: SIMILARITY ANALYSIS")
    print("-" * 30)
    
    similarity_result = embedder.compute_similarity(example_text)
    
    print(f"📊 Max Similarity: {similarity_result.max_similarity:.3f}")
    print(f"🎯 Threshold Exceeded: {'Yes' if similarity_result.threshold_exceeded else 'No'}")
    print(f"📈 Severity Level: {similarity_result.severity_level.title()}")
    
    print(f"\n🔍 Similar Stereotype Phrases ({len(similarity_result.similar_phrases)} found):")
    for phrase in similarity_result.similar_phrases[:5]:  # Show top 5
        score = similarity_result.similarity_scores.get(phrase, 0.0)
        print(f"  • '{phrase}' (similarity: {score:.3f})")
    
    # STEP 3: BAMIP STRATEGY SELECTION
    print("\n\n🛠️ STEP 3: BAMIP STRATEGY SELECTION")
    print("-" * 30)
    
    # Show strategy selection process
    text_lower = example_text.lower()
    
    print("🔍 Pattern Analysis:")
    
    # Check each pattern in priority order
    patterns_to_check = [
        (r'\b(sikh.*muslim|muslim.*sikh|sikh.*islam|islam.*sikh|sikh.*subset.*islam)\b', "Religious Conflation", "Retrieval Grounding"),
        (r'\b(terrorist|terrorism|militant|extremist)\b', "Terrorism Association", "Neutral Language"),
        (r'\b(all|every|always|never)\s+(sikh|muslim|jew|hindu)\b', "Harmful Generalizations", "Contextual Reframing"),
        (r'\b(backward|primitive|uncivilized)\b', "Cultural Bias", "Counter Narrative"),
        (r'\b(fear|danger|threat|violent|aggressive)\b', "Emotional Language", "Neutral Language"),
    ]
    
    selected_strategy = None
    for pattern, description, strategy in patterns_to_check:
        if re.search(pattern, text_lower):
            print(f"  ✅ Found: {description} → {strategy}")
            if selected_strategy is None:
                selected_strategy = strategy
                print(f"  🎯 SELECTED STRATEGY: {strategy}")
        else:
            print(f"  ❌ Not found: {description}")
    
    if selected_strategy is None:
        selected_strategy = "Instructional Prompting"
        print(f"  🎯 DEFAULT STRATEGY: {selected_strategy}")
    
    # STEP 4: BAMIP MITIGATION
    print("\n\n🛠️ STEP 4: BAMIP MITIGATION")
    print("-" * 30)
    
    mitigation_result = mitigator.mitigate_bias(example_text)
    
    print(f"🎯 Strategy Used: {mitigation_result.strategy_used.value.replace('_', ' ').title()}")
    print(f"📉 Bias Reduction: {mitigation_result.bias_reduction_score:.1%}")
    print(f"💡 Confidence: {mitigation_result.confidence:.1%}")
    
    print(f"\n📝 ORIGINAL TEXT:")
    print(f'"{mitigation_result.original_text}"')
    
    print(f"\n📝 MITIGATED TEXT:")
    print(f'"{mitigation_result.mitigated_text}"')
    
    print(f"\n💡 Mitigation Strategy:")
    for explanation in mitigation_result.explanations:
        print(f"  • {explanation}")
    
    print(f"\n🎯 Suggested Bias-Free Prompts:")
    for i, prompt in enumerate(mitigation_result.suggested_prompts, 1):
        print(f"  {i}. {prompt}")
    
    # STEP 5: FINAL ANALYSIS
    print("\n\n📊 STEP 5: FINAL ANALYSIS")
    print("-" * 30)
    
    print("🎯 COMPLETE ASSESSMENT:")
    print(f"  Bias Level: {color} {severity}")
    print(f"  Overall Score: {rubric_result.overall_score:.1f}/10")
    print(f"  Similarity Risk: {similarity_result.severity_level.title()}")
    print(f"  Mitigation Applied: {mitigation_result.strategy_used.value.replace('_', ' ').title()}")
    print(f"  Bias Reduced: {mitigation_result.bias_reduction_score:.1%}")
    
    print(f"\n🚨 KEY ISSUES IDENTIFIED:")
    print(f"  • Factual errors about Sikhism and Islam")
    print(f"  • Harmful generalizations ('All Sikhs')")
    print(f"  • Terrorism association")
    print(f"  • Emotional language ('feared', 'violent')")
    
    print(f"\n✅ MITIGATION ACTIONS:")
    print(f"  • Added factual context about Sikhism")
    print(f"  • Suggested bias-free prompts for future use")
    print(f"  • Provided educational explanations")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    print(f"  • Use suggested bias-free prompts")
    print(f"  • Apply additional Neutral Language strategy")
    print(f"  • Include more factual context about Sikhism")
    print(f"  • Avoid generalizations about religious groups")
    
    print("\n" + "=" * 60)
    print("🎉 Walkthrough Complete!")
    print("This demonstrates the complete BiasLens pipeline from detection to mitigation.")


if __name__ == "__main__":
    import re
    main() 