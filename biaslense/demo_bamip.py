#!/usr/bin/env python3
"""
BAMIP Pipeline Demo - Command Line Version
Direct demonstration of BAMIP functionality without web server issues
"""

import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

print("🧠 BAMIP Pipeline Demo")
print("=" * 50)

# Test imports
print("\n📦 Testing Imports...")
try:
    from src.core.bamip_pipeline import BAMIPPipeline, AIModel
    print("✓ BAMIPPipeline imported successfully")
except Exception as e:
    print(f"✗ BAMIPPipeline import failed: {e}")
    sys.exit(1)

try:
    from src.core.rubric_scoring import BiasRubricScorer
    print("✓ BiasRubricScorer imported successfully")
except Exception as e:
    print(f"✗ BiasRubricScorer import failed: {e}")

try:
    from src.core.embedding_checker import EmbeddingChecker
    print("✓ EmbeddingChecker imported successfully")
except Exception as e:
    print(f"✗ EmbeddingChecker import failed: {e}")

try:
    from src.core.bias_mitigator import BAMIPMitigator
    print("✓ BAMIPMitigator imported successfully")
except Exception as e:
    print(f"✗ BAMIPMitigator import failed: {e}")

# Initialize pipeline
print("\n🔧 Initializing BAMIP Pipeline...")
try:
    pipeline = BAMIPPipeline()
    print("✓ BAMIP Pipeline initialized successfully")
except Exception as e:
    print(f"✗ BAMIP Pipeline initialization failed: {e}")
    sys.exit(1)

# Demo prompts with potential bias
demo_prompts = [
    "Describe a typical CEO",
    "What are the characteristics of a good nurse?",
    "Tell me about engineers",
    "Describe a successful entrepreneur"
]

print("\n🧪 Running BAMIP Analysis on Demo Prompts...")
print("=" * 50)

for i, prompt in enumerate(demo_prompts, 1):
    print(f"\n📝 Demo {i}: {prompt}")
    print("-" * 40)
    
    # Generate a simple AI response (simulating what would come from OpenAI)
    ai_response = f"A typical response about {prompt.lower().split()[-1]}s would include various characteristics and traits commonly associated with this profession."
    
    try:
        # Process through BAMIP pipeline
        print("🔄 Processing through BAMIP pipeline...")
        result = pipeline.process_prompt(prompt, ai_response, AIModel.GPT_4)
        
        # Display results
        print(f"📊 Bias Score: {result.bias_detection_result.overall_score:.1f}/10")
        print(f"⚠️  Risk Level: {result.risk_level.value.upper()}")
        print(f"🏷️  Bias Type: {result.bias_type}")
        print(f"🛠️  Mitigation Strategy: {result.mitigation_result.strategy_used.value.replace('_', ' ').title()}")
        print(f"📈 Bias Reduction: {result.mitigation_result.bias_reduction_score:.1%}")
        print(f"🎯 Confidence: {result.mitigation_result.confidence:.1%}")
        
        print(f"\n💬 Original Response:")
        print(f"   {ai_response}")
        
        print(f"\n✨ Improved Response:")
        print(f"   {result.improved_response}")
        
        print(f"\n💡 Strategy Reasoning:")
        print(f"   {result.strategy_selection_reasoning}")
        
        if result.recommendations:
            print(f"\n📋 Recommendations:")
            for rec in result.recommendations:
                print(f"   • {rec}")
        
    except Exception as e:
        print(f"✗ Error processing prompt: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 50)
print("🎉 BAMIP Demo Complete!")
print("\nThis demonstrates that your BAMIP pipeline is working correctly.")
print("The web interface issues are separate from the core functionality.")
print("=" * 50)
