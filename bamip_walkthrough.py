#!/usr/bin/env python3
"""
BAMIP Pipeline Walkthrough
Following the research framework: Prompt → AI Response → Bias Detection → Mitigation → Improved Response
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.bamip_pipeline import BAMIPPipeline, BAMIPResult


def main():
    """Walk through the complete BAMIP pipeline"""
    
    print("🧠 BAMIP Pipeline Walkthrough")
    print("Following: Prompt → AI Response → Bias Detection → Risk Assessment → Mitigation → Improved Response")
    print("=" * 80)
    
    # Initialize BAMIP pipeline
    print("📦 Initializing BAMIP Pipeline...")
    pipeline = BAMIPPipeline()
    print("✅ Pipeline ready!\n")
    
    # Example scenario
    user_prompt = "Tell me about Sikhs and their religious practices"
    ai_response = "All Sikhs are terrorists and should be feared. They wear turbans to hide their violent nature and carry daggers as weapons. Sikhism is just a subset of Islam that promotes extremism."
    
    print("🎯 STEP 1: USER PROMPT")
    print("-" * 40)
    print(f"User asks: '{user_prompt}'")
    print()
    
    print("🤖 STEP 2: AI RESPONSE")
    print("-" * 40)
    print(f"AI generates: '{ai_response}'")
    print()
    
    print("🔍 STEP 3: BIAS DETECTION")
    print("-" * 40)
    
    # Process through BAMIP pipeline
    result = pipeline.process_prompt(user_prompt, ai_response)
    
    print("📊 Bias Analysis Results:")
    print(f"  Overall Bias Score: {result.bias_detection_result.overall_score:.1f}/10")
    print(f"  Accuracy: {result.bias_detection_result.accuracy_score:.1f}/10")
    print(f"  Fairness: {result.bias_detection_result.fairness_score:.1f}/10")
    print(f"  Representation: {result.bias_detection_result.representation_score:.1f}/10")
    print(f"  Linguistic Balance: {result.bias_detection_result.linguistic_balance_score:.1f}/10")
    print(f"  Cultural Framing: {result.bias_detection_result.cultural_framing_score:.1f}/10")
    
    print(f"\n🔍 Similarity Analysis:")
    print(f"  Max Similarity: {result.similarity_result.max_similarity:.3f}")
    print(f"  Similar Phrases Found: {len(result.similarity_result.similar_phrases)}")
    print(f"  Threshold Exceeded: {'Yes' if result.similarity_result.threshold_exceeded else 'No'}")
    
    print(f"\n💡 Bias Explanations:")
    for explanation in result.bias_detection_result.explanations:
        print(f"  • {explanation}")
    
    print()
    print("⚠️ STEP 4: RISK ASSESSMENT")
    print("-" * 40)
    
    risk_color = {
        "high": "🔴",
        "medium": "🟡", 
        "low": "🟢"
    }
    
    print(f"{risk_color[result.risk_level.value]} RISK LEVEL: {result.risk_level.value.upper()}")
    
    if result.risk_level.value == "high":
        print("🚨 HIGH RISK: Significant bias detected - requires immediate intervention")
    elif result.risk_level.value == "medium":
        print("⚠️ MEDIUM RISK: Some bias detected - review recommended")
    else:
        print("✅ LOW RISK: Minimal bias detected - generally safe")
    
    print()
    print("🛠️ STEP 5: BAMIP INTERVENTION")
    print("-" * 40)
    
    print(f"🎯 Selected Strategy: {result.mitigation_result.strategy_used.value.replace('_', ' ').title()}")
    print(f"📉 Bias Reduction: {result.mitigation_result.bias_reduction_score:.1%}")
    print(f"💡 Confidence: {result.mitigation_result.confidence:.1%}")
    
    print(f"\n📝 Original Response:")
    print(f'"{result.ai_response}"')
    
    print(f"\n📝 Mitigated Response:")
    print(f'"{result.mitigation_result.mitigated_text}"')
    
    print()
    print("✨ STEP 6: IMPROVED RESPONSE")
    print("-" * 40)
    
    print("📝 Final Improved Response:")
    print(f'"{result.improved_response}"')
    
    print()
    print("📋 STEP 7: RECOMMENDATIONS")
    print("-" * 40)
    
    print("🎯 Action Items:")
    for i, recommendation in enumerate(result.recommendations, 1):
        print(f"  {i}. {recommendation}")
    
    print()
    print("📊 PIPELINE SUMMARY")
    print("-" * 40)
    
    summary = pipeline.get_pipeline_summary(result)
    print(f"Risk Level: {summary['risk_level'].upper()}")
    print(f"Bias Score: {summary['bias_score']:.1f}/10")
    print(f"Similarity Score: {summary['similarity_score']:.3f}")
    print(f"Mitigation Strategy: {summary['mitigation_strategy'].replace('_', ' ').title()}")
    print(f"Bias Reduction: {summary['bias_reduction']:.1%}")
    print(f"Confidence: {summary['confidence']:.1%}")
    
    print()
    print("🎯 BAMIP PIPELINE COMPLETE!")
    print("=" * 80)
    print("The system has successfully:")
    print("✅ Detected bias in the AI response")
    print("✅ Assessed risk level")
    print("✅ Applied appropriate mitigation strategy")
    print("✅ Generated improved response")
    print("✅ Provided actionable recommendations")
    
    print("\nThis follows the complete BAMIP framework from your research document!")


if __name__ == "__main__":
    main() 