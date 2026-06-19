"""
Basic functionality tests for BiasLens
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.rubric_scoring import BiasRubricScorer


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


def main():
    """Run all tests"""
    print("🚀 Running BiasLens Basic Tests\n")

    test_rubric_scoring()

    print("✅ Basic tests completed!")


if __name__ == "__main__":
    main() 