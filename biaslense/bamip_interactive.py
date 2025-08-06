#!/usr/bin/env python3
"""
BAMIP Interactive Interface - Direct Python GUI
Simple interactive interface for BAMIP pipeline that works without web servers
"""

import sys
import os
from datetime import datetime

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.core.bamip_pipeline import BAMIPPipeline, AIModel

def print_banner():
    print("=" * 60)
    print("🧠 BAMIP INTERACTIVE INTERFACE")
    print("Bias-Aware Mitigation and Intervention Pipeline")
    print("=" * 60)

def print_menu():
    print("\n📋 MENU:")
    print("1. 🧪 Analyze a prompt for bias")
    print("2. 📜 View analysis history")
    print("3. ℹ️  About BAMIP methodology")
    print("4. 🚪 Exit")
    print("-" * 40)

def print_methodology():
    print("\n🔬 BAMIP FRAMEWORK")
    print("=" * 50)
    print("The BAMIP (Bias-Aware Mitigation and Intervention Pipeline)")
    print("framework implements a comprehensive two-layer methodology")
    print("for detecting and mitigating bias in AI-generated content.")
    print()
    print("📊 TWO-LAYER DETECTION METHODOLOGY:")
    print("• Layer 1: Bias Detection")
    print("  - Rubric-based scoring (Accuracy, Fairness, Representation, Neutrality, Relevance)")
    print("  - Embedding-based similarity to stereotype anchors")
    print("• Layer 2: BAMIP Classification & Intervention")
    print("  - Bias type classification (Historical, Representational, Measurement, etc.)")
    print("  - Strategy selection and mitigation application")
    print()
    print("🛠️  MITIGATION STRATEGIES:")
    print("• Instructional Prompting - Clear, explicit instructions to avoid bias")
    print("• Contextual Reframing - Reframe prompts to encourage balanced perspectives")
    print("• Retrieval-Based Grounding - Provide factual grounding with trusted sources")

def analyze_prompt(pipeline, history):
    print("\n🧪 BIAS ANALYSIS")
    print("-" * 30)
    
    # Get user input
    prompt = input("Enter your prompt: ").strip()
    if not prompt:
        print("❌ No prompt entered.")
        return
    
    print(f"\n🔄 Analyzing: '{prompt}'")
    print("⏳ Processing through BAMIP pipeline...")
    
    try:
        # Generate a simple AI response (you can integrate OpenAI here)
        ai_response = f"This is a sample AI response to: {prompt}"
        
        # Process through BAMIP pipeline
        result = pipeline.process_prompt(prompt, ai_response, AIModel.GPT_4)
        
        # Display results
        print("\n" + "=" * 50)
        print("📊 BIAS ANALYSIS RESULTS")
        print("=" * 50)
        
        print(f"📝 Original Prompt: {prompt}")
        print(f"📊 Bias Score: {result.bias_detection_result.overall_score:.1f}/10")
        print(f"⚠️  Risk Level: {result.risk_level.value.upper()}")
        print(f"🏷️  Bias Type: {result.bias_type}")
        print(f"🛠️  Mitigation Strategy: {result.mitigation_result.strategy_used.value.replace('_', ' ').title()}")
        print(f"📈 Bias Reduction: {result.mitigation_result.bias_reduction_score:.1%}")
        print(f"🎯 Confidence: {result.mitigation_result.confidence:.1%}")
        
        print(f"\n💬 ORIGINAL RESPONSE:")
        print(f"   {ai_response}")
        
        print(f"\n✨ IMPROVED RESPONSE:")
        print(f"   {result.improved_response}")
        
        print(f"\n💡 STRATEGY REASONING:")
        print(f"   {result.strategy_selection_reasoning}")
        
        if result.recommendations:
            print(f"\n📋 RECOMMENDATIONS:")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Store in history
        history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'prompt': prompt,
            'bias_score': result.bias_detection_result.overall_score,
            'risk_level': result.risk_level.value,
            'bias_type': result.bias_type,
            'strategy': result.mitigation_result.strategy_used.value,
            'improved_response': result.improved_response
        })
        
        print("\n✅ Analysis complete and saved to history!")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

def view_history(history):
    print("\n📜 ANALYSIS HISTORY")
    print("=" * 40)
    
    if not history:
        print("No analysis history yet. Run some analyses to see results here.")
        return
    
    for i, analysis in enumerate(reversed(history), 1):
        print(f"\n📊 Analysis #{len(history) - i + 1}")
        print(f"🕒 Time: {analysis['timestamp']}")
        print(f"📝 Prompt: {analysis['prompt']}")
        print(f"📊 Bias Score: {analysis['bias_score']:.1f}/10")
        print(f"⚠️  Risk Level: {analysis['risk_level'].upper()}")
        print(f"🏷️  Bias Type: {analysis['bias_type']}")
        print(f"🛠️  Strategy: {analysis['strategy'].replace('_', ' ').title()}")
        print(f"✨ Improved Response: {analysis['improved_response'][:100]}...")
        print("-" * 40)

def main():
    # Initialize
    print_banner()
    
    print("\n🔧 Initializing BAMIP Pipeline...")
    try:
        pipeline = BAMIPPipeline()
        print("✅ BAMIP Pipeline initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize BAMIP Pipeline: {e}")
        return
    
    history = []
    
    # Main loop
    while True:
        print_menu()
        
        try:
            choice = input("Select an option (1-4): ").strip()
            
            if choice == '1':
                analyze_prompt(pipeline, history)
            elif choice == '2':
                view_history(history)
            elif choice == '3':
                print_methodology()
            elif choice == '4':
                print("\n👋 Thank you for using BAMIP!")
                print("Your bias analysis results have been helpful for research validation.")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 BAMIP session ended by user.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == '__main__':
    main()
