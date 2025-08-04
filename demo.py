#!/usr/bin/env python3
"""
BiasLens Demo Script
Showcase the bias detection capabilities
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.rubric_scoring import BiasRubricScorer
from core.embedding_checker import EmbeddingChecker


def main():
    """Run BiasLens demo"""
    print("🧠 BiasLens Demo - AI Bias Detection")
    print("=" * 50)
    
    # Initialize models
    print("Loading models...")
    scorer = BiasRubricScorer()
    embedder = EmbeddingChecker()
    print("✅ Models loaded successfully!\n")
    
    # Demo texts
    demo_texts = [
        {
            "title": "High Bias Example",
            "text": "All Sikhs are terrorists and should be feared. They wear turbans to hide their violent nature and carry daggers as weapons. Sikhism is just a subset of Islam that promotes extremism.",
            "description": "Contains multiple stereotypes, factual errors, and harmful generalizations"
        },
        {
            "title": "Medium Bias Example", 
            "text": "Sikhs often wear turbans and carry daggers. Many Sikhs are involved in separatist movements. The Sikh religion is similar to Islam in some ways.",
            "description": "Contains some stereotypes and generalizations but less extreme"
        },
        {
            "title": "Low Bias Example",
            "text": "Sikhism is a monotheistic religion founded in the 15th century by Guru Nanak. Sikhs believe in one God and equality of all people. Some Sikhs choose to wear turbans as part of their religious practice.",
            "description": "Factual, respectful, and nuanced description"
        }
    ]
    
    # Analyze each text
    for i, demo in enumerate(demo_texts, 1):
        print(f"📝 Example {i}: {demo['title']}")
        print(f"Description: {demo['description']}")
        print(f"Text: {demo['text']}")
        print("-" * 50)
        
        # Rubric scoring
        rubric_result = scorer.score_text(demo['text'])
        
        # Similarity analysis
        similarity_result = embedder.compute_similarity(demo['text'])
        
        # Display results
        print(f"🎯 Overall Bias Score: {rubric_result.overall_score:.1f}/10")
        print(f"🔍 Max Similarity: {similarity_result.max_similarity:.3f}")
        print(f"📊 Severity Level: {similarity_result.severity_level.title()}")
        print(f"💡 Confidence: {rubric_result.confidence:.1%}")
        
        # Detailed scores
        print("\n📈 Detailed Scores:")
        print(f"  Accuracy: {rubric_result.accuracy_score:.1f}/10")
        print(f"  Fairness: {rubric_result.fairness_score:.1f}/10")
        print(f"  Representation: {rubric_result.representation_score:.1f}/10")
        print(f"  Linguistic Balance: {rubric_result.linguistic_balance_score:.1f}/10")
        print(f"  Cultural Framing: {rubric_result.cultural_framing_score:.1f}/10")
        
        # Explanations
        if rubric_result.explanations:
            print("\n💡 Bias Explanations:")
            for explanation in rubric_result.explanations:
                print(f"  • {explanation}")
        
        # Similar phrases
        if similarity_result.similar_phrases:
            print(f"\n🔍 Similar Stereotype Phrases ({len(similarity_result.similar_phrases)} found):")
            for phrase in similarity_result.similar_phrases[:5]:  # Show top 5
                score = similarity_result.similarity_scores.get(phrase, 0.0)
                print(f"  • {phrase} (similarity: {score:.3f})")
        
        print("\n" + "=" * 50 + "\n")
    
    print("🎉 Demo completed! Run 'python run_app.py' to launch the full Streamlit application.")


if __name__ == "__main__":
    main() 