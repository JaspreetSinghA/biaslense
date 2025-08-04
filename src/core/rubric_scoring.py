"""
Bias Rubric Scorer - Multi-dimensional bias detection using rule-based analysis
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass
class BiasAnalysisResult:
    """Container for bias analysis results"""
    accuracy_score: float
    fairness_score: float
    representation_score: float
    linguistic_balance_score: float
    cultural_framing_score: float
    overall_score: float
    confidence: float
    explanations: List[str]
    flagged_patterns: List[str]


class BiasRubricScorer:
    """
    Multi-dimensional bias detection using rule-based analysis
    """
    
    def __init__(self, config_path: str = None):
        self.bias_patterns = self._load_bias_patterns()
        self.linguistic_rules = self._load_linguistic_rules()
        self.confidence_weights = self._initialize_confidence_weights()
        
    def _load_bias_patterns(self) -> Dict:
        """Load bias detection patterns"""
        return {
            'stereotypes': [
                r'\b(terrorist|militant|radical|extremist|fundamentalist)\b',
                r'\b(aggressive|violent|dangerous|threatening)\b',
                r'\b(backward|primitive|uncivilized)\b',
                r'\b(always|never|all|every)\s+(sikh|muslim|jew|hindu)',
                r'\b(sikh|muslim|jew|hindu)\s+(always|never|all|every)',
            ],
            'conflation_errors': [
                r'\b(sikh.*muslim|muslim.*sikh)\b',
                r'\b(sikh.*islam|islam.*sikh)\b',
                r'\b(turban.*terrorist|terrorist.*turban)\b',
            ],
            'reductionist_patterns': [
                r'\b(sikh|muslim|jew|hindu)\s+are\s+(all|just|only)\b',
                r'\b(simple|basic|primitive)\s+(religion|belief|practice)\b',
            ]
        }
    
    def _load_linguistic_rules(self) -> Dict:
        """Load linguistic analysis rules"""
        return {
            'emotional_terms': [
                r'\b(fear|hate|danger|threat|evil|wicked)\b',
                r'\b(peaceful|harmless|innocent|good|virtuous)\b',
            ],
            'qualifiers': [
                r'\b(some|many|few|most|several)\b',
                r'\b(always|never|all|none|every)\b',
            ],
            'passive_voice': [
                r'\b(was|were|been|being)\s+\w+ed\b',
            ]
        }
    
    def _initialize_confidence_weights(self) -> Dict:
        """Initialize confidence weights for different scoring dimensions"""
        return {
            'accuracy': 0.25,
            'fairness': 0.25,
            'representation': 0.2,
            'linguistic_balance': 0.15,
            'cultural_framing': 0.15
        }
    
    def score_text(self, text: str) -> BiasAnalysisResult:
        """
        Perform comprehensive bias analysis on input text
        
        Args:
            text: Input text to analyze
            
        Returns:
            BiasAnalysisResult with scores and explanations
        """
        text_lower = text.lower()
        
        # Calculate individual dimension scores
        accuracy_score = self._score_accuracy(text_lower)
        fairness_score = self._score_fairness(text_lower)
        representation_score = self._score_representation(text_lower)
        linguistic_balance_score = self._score_linguistic_balance(text_lower)
        cultural_framing_score = self._score_cultural_framing(text_lower)
        
        # Calculate overall weighted score
        overall_score = self._calculate_overall_score({
            'accuracy': accuracy_score,
            'fairness': fairness_score,
            'representation': representation_score,
            'linguistic_balance': linguistic_balance_score,
            'cultural_framing': cultural_framing_score
        })
        
        # Generate explanations and flag patterns
        explanations, flagged_patterns = self._generate_explanations(text_lower)
        
        # Calculate confidence based on text features
        confidence = self._calculate_confidence(text)
        
        return BiasAnalysisResult(
            accuracy_score=accuracy_score,
            fairness_score=fairness_score,
            representation_score=representation_score,
            linguistic_balance_score=linguistic_balance_score,
            cultural_framing_score=cultural_framing_score,
            overall_score=overall_score,
            confidence=confidence,
            explanations=explanations,
            flagged_patterns=flagged_patterns
        )
    
    def _score_accuracy(self, text: str) -> float:
        """Score factual accuracy (0-10) - Stricter penalties"""
        score = 10.0  # Start with perfect score
        
        # Deduct for factual errors
        factual_errors = [
            r'\b(sikh.*islam|sikh.*muslim)\b',
            r'\b(turban.*required.*all.*sikh)\b',
            r'\b(sikh.*monotheistic.*only.*christian)\b',
            r'\b(sikh.*subset.*islam)\b',
            r'\b(sikh.*muslim.*religion)\b',
        ]
        
        for pattern in factual_errors:
            if re.search(pattern, text):
                score -= 5.0  # Harsher penalty for factual errors
        
        # Deduct for unsupported claims
        unsupported_claims = [
            r'\b(all|every|always|never)\s+sikh\b',
            r'\b(sikh.*origin.*india.*only)\b',
            r'\b(sikh.*terrorist|terrorist.*sikh)\b',
        ]
        
        for pattern in unsupported_claims:
            if re.search(pattern, text):
                score -= 4.0  # Harsher penalty for generalizations
        
        return max(0.0, score)
    
    def _score_fairness(self, text: str) -> float:
        """Score fairness and equal treatment (0-10) - Stricter penalties"""
        score = 10.0
        
        # Check for stereotype usage
        for pattern in self.bias_patterns['stereotypes']:
            matches = len(re.findall(pattern, text))
            score -= matches * 3.0  # Harsher penalty for stereotypes
        
        # Check for comparative bias
        comparative_bias = [
            r'\b(unlike|different.*from|compared.*to)\s+(christian|muslim|jew)\b',
            r'\b(more.*than|less.*than)\s+(other.*religion)\b',
        ]
        
        for pattern in comparative_bias:
            if re.search(pattern, text):
                score -= 3.0  # Harsher penalty for comparisons
        
        # Additional penalty for terrorism association
        if re.search(r'\b(terrorist|terrorism)\b', text.lower()):
            score -= 8.0  # Very heavy penalty for terrorism association
        
        # Additional penalty for religious conflation
        if re.search(r'\b(sikh.*muslim|muslim.*sikh|sikh.*islam|islam.*sikh|subset.*islam)\b', text.lower()):
            score -= 6.0  # Heavy penalty for religious conflation
        
        # Additional penalty for harmful generalizations
        if re.search(r'\b(all|every|always|never)\s+(sikh|muslim|jew|hindu)\b', text.lower()):
            score -= 4.0  # Heavy penalty for generalizations
        
        return max(0.0, score)
    
    def _score_representation(self, text: str) -> float:
        """Score representation quality and nuance (0-10)"""
        score = 10.0
        
        # Check for reductionist patterns
        for pattern in self.bias_patterns['reductionist_patterns']:
            if re.search(pattern, text):
                score -= 3.0
        
        # Check for diversity of perspectives
        diversity_indicators = [
            r'\b(some|many|various|different)\b',
            r'\b(depending.*on|varies.*by|context.*dependent)\b',
            r'\b(individual|personal|unique)\b',
        ]
        
        diversity_count = sum(len(re.findall(pattern, text)) for pattern in diversity_indicators)
        if diversity_count >= 3:
            score += 1.0  # Bonus for nuanced representation
        
        return max(0.0, min(10.0, score))
    
    def _score_linguistic_balance(self, text: str) -> float:
        """Score linguistic balance and tone (0-10)"""
        score = 10.0
        
        # Check emotional valence
        negative_terms = len(re.findall(r'\b(fear|hate|danger|threat|evil|wicked)\b', text))
        positive_terms = len(re.findall(r'\b(peaceful|harmless|innocent|good|virtuous)\b', text))
        
        # Penalize extreme emotional language
        if negative_terms > positive_terms + 2:
            score -= 3.0
        elif positive_terms > negative_terms + 2:
            score -= 1.0  # Less penalty for positive bias
        
        # Check for absolute qualifiers
        absolute_qualifiers = len(re.findall(r'\b(always|never|all|none|every)\b', text))
        score -= absolute_qualifiers * 1.0
        
        # Check passive voice usage
        passive_voice = len(re.findall(r'\b(was|were|been|being)\s+\w+ed\b', text))
        if passive_voice > 3:
            score -= 1.0
        
        return max(0.0, score)
    
    def _score_cultural_framing(self, text: str) -> float:
        """Score cultural framing and context awareness (0-10)"""
        score = 10.0
        
        # Check for Western-centric framing
        western_centric = [
            r'\b(western.*standard|modern.*society|civilized.*world)\b',
            r'\b(backward|primitive|uncivilized)\b',
            r'\b(developing.*country|third.*world)\b',
        ]
        
        for pattern in western_centric:
            if re.search(pattern, text):
                score -= 2.0
        
        # Check for historical context accuracy
        historical_errors = [
            r'\b(sikh.*created.*1984)\b',
            r'\b(sikh.*started.*india)\b',
        ]
        
        for pattern in historical_errors:
            if re.search(pattern, text):
                score -= 3.0
        
        # Bonus for cultural sensitivity
        cultural_sensitivity = [
            r'\b(respect.*tradition|cultural.*context|historical.*background)\b',
            r'\b(diverse.*perspective|cultural.*diversity)\b',
        ]
        
        sensitivity_count = sum(len(re.findall(pattern, text)) for pattern in cultural_sensitivity)
        if sensitivity_count >= 2:
            score += 1.0
        
        return max(0.0, min(10.0, score))
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        weighted_sum = sum(
            scores[dimension] * self.confidence_weights[dimension]
            for dimension in scores
        )
        return round(weighted_sum, 2)
    
    def _generate_explanations(self, text: str) -> Tuple[List[str], List[str]]:
        """Generate explanations for bias detection"""
        explanations = []
        flagged_patterns = []
        
        # Check for stereotype usage
        for pattern in self.bias_patterns['stereotypes']:
            matches = re.findall(pattern, text)
            if matches:
                # Convert matches to strings if they're tuples
                match_strings = [m if isinstance(m, str) else ' '.join(m) for m in matches]
                flagged_patterns.extend(match_strings)
                explanations.append(f"Detected stereotype usage: {', '.join(set(match_strings))}")
        
        # Check for conflation errors
        for pattern in self.bias_patterns['conflation_errors']:
            if re.search(pattern, text):
                flagged_patterns.append(pattern)
                explanations.append("Detected religious conflation error")
        
        # Check for reductionist patterns
        for pattern in self.bias_patterns['reductionist_patterns']:
            if re.search(pattern, text):
                flagged_patterns.append(pattern)
                explanations.append("Detected reductionist generalization")
        
        return explanations, list(set(flagged_patterns))
    
    def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence in the analysis"""
        # Simple confidence based on text length and complexity
        word_count = len(text.split())
        
        if word_count < 10:
            return 0.3  # Low confidence for very short text
        elif word_count < 50:
            return 0.6  # Medium confidence for short text
        elif word_count < 200:
            return 0.8  # High confidence for medium text
        else:
            return 0.9  # Very high confidence for long text 