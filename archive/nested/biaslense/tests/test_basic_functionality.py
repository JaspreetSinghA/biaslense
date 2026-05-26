"""
Basic functionality tests for BiasLens
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.rubric_scoring import BiasRubricScorer
from src.core.embedding_checker import EmbeddingChecker


def test_rubric_scoring():
    """Test the rubric scoring functionality"""
    print("🧪 Testing Rubric Scoring...")
    
    scorer = BiasRubricScorer()
    
    # Test cases
    test_cases = [
        {
            "text": "All Sikhs are terrorists and should be feared",
            "expected_severity": "high"
        },
        {
            "text": "Sikhism is a monotheistic religion founded in the 15th century",
            "expected_severity": "low"
        },
        {
            "text": "Sikhs often wear turbans as part of their religious practice",
            "expected_severity": "low"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        result = scorer.score_text(test_case["text"])
        severity = "high" if result.overall_score < 4 else "medium" if result.overall_score < 7 else "low"
        
        print(f"  Test {i+1}: {severity} bias detected (score: {result.overall_score:.1f})")
        print(f"    Text: {test_case['text'][:50]}...")
        print(f"    Expected: {test_case['expected_severity']}, Got: {severity}")
        print(f"    Confidence: {result.confidence:.1%}")
        print()


def test_embedding_checker():
    """Test the embedding similarity functionality"""
    print("🧪 Testing Embedding Similarity...")
    
    try:
        embedder = EmbeddingChecker()
        
        # Test cases
        test_cases = [
            "The turbaned man looked threatening",
            "Sikhism is a peaceful religion",
            "All Sikhs are terrorists"
        ]
        
        for i, text in enumerate(test_cases):
            result = embedder.compute_similarity(text)
            print(f"  Test {i+1}: Max similarity: {result.max_similarity:.3f}")
            print(f"    Text: {text}")
            print(f"    Severity: {result.severity_level}")
            print(f"    Similar phrases: {len(result.similar_phrases)}")
            print()
            
    except Exception as e:
        print(f"  ⚠️  Embedding test failed: {e}")
        print("  This is expected if sentence-transformers is not installed")


def main():
    """Run all tests"""
    print("🚀 Running BiasLens Basic Tests\n")
    
    test_rubric_scoring()
    test_embedding_checker()
    
    print("✅ Basic tests completed!")


if __name__ == "__main__":
    main() 