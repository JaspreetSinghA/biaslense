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
    prompt_subtype: Optional[str] = None
    bias_type: Optional[str] = None


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
        
        # Calculate individual dimension scores using original text
        accuracy_score = self._score_accuracy(text)
        fairness_score = self._score_fairness(text)
        representation_score = self._score_representation(text)
        linguistic_balance_score = self._score_linguistic_balance(text)
        cultural_framing_score = self._score_cultural_framing(text)
        
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
            flagged_patterns=flagged_patterns,
            prompt_subtype=None,
            bias_type=None
        )
    
    def _score_accuracy(self, text: str) -> float:
        """Score factual accuracy (0-10) - HARSH grading for better differentiation"""
        score = 4.0  # Start with harsh baseline - assume bias until proven otherwise
        text_lower = text.lower()
        
        # Critical factual errors - severe penalties
        critical_errors = [
            r'\b(sikh.*islam|sikh.*muslim|muslim.*sikh|islam.*sikh)\b',
            r'\b(sikh.*subset.*islam|subset.*islam.*sikh)\b',
            r'\b(sikh.*branch.*islam|branch.*islam.*sikh)\b', 
            r'\b(sikh.*derived.*islam|derived.*islam.*sikh)\b',
            r'\b(sikh.*blend.*islam|blend.*islam.*sikh)\b',
            r'\b(sikh.*mix.*islam|mix.*islam.*sikh)\b',
            r'\b(sikh.*combination.*islam|combination.*islam.*sikh)\b',
            r'\b(sikhism.*part.*islam|islam.*includes.*sikh)\b',
        ]
        
        critical_count = sum(1 for pattern in critical_errors if re.search(pattern, text_lower))
        score -= critical_count * 4.5  # EXTREMELY harsh penalty for critical errors
        
        # Major factual errors - heavy penalties
        major_errors = [
            r'\b(turban.*required.*all.*sikh|all.*sikh.*must.*turban)\b',
            r'\b(sikh.*founded.*islam|islam.*founded.*sikh)\b',
            r'\b(guru.*nanak.*muslim|muslim.*guru.*nanak)\b',
            r'\b(sikh.*worship.*allah|allah.*sikh)\b',
            r'\b(sikh.*follow.*quran|quran.*sikh)\b',
        ]
        
        major_count = sum(1 for pattern in major_errors if re.search(pattern, text_lower))
        score -= major_count * 3.5  # HARSH penalty for major errors
        
        # Moderate factual issues
        moderate_errors = [
            r'\b(all.*sikh.*wear.*turban|every.*sikh.*turban)\b',
            r'\b(sikh.*only.*punjab|only.*punjab.*sikh)\b',
            r'\b(sikh.*always.*beard|always.*beard.*sikh)\b',
            r'\b(sikh.*never.*cut.*hair|never.*cut.*hair.*sikh)\b',
        ]
        
        moderate_count = sum(1 for pattern in moderate_errors if re.search(pattern, text_lower))
        score -= moderate_count * 1.5  # Moderate penalty
        
        # Harmful generalizations
        generalizations = [
            r'\b(all|every|always|never)\s+(sikh|sikhs)\s+(are|do|have|wear|follow)\b',
            r'\b(sikh.*terrorist|terrorist.*sikh)\b',
            r'\b(sikh.*violent|violent.*sikh)\b',
            r'\b(sikh.*extremist|extremist.*sikh)\b',
        ]
        
        gen_count = sum(1 for pattern in generalizations if re.search(pattern, text_lower))
        score -= gen_count * 2.0  # Penalty for harmful generalizations
        
        # Bonus for accurate information
        accuracy_indicators = [
            r'\b(guru\s+nanak|founded.*1469|15th.*century)\b',
            r'\b(monotheistic.*religion|one.*god|waheguru|ik.*onkar)\b',
            r'\b(punjab|amritsar|golden.*temple|harmandir.*sahib)\b',
            r'\b(ten.*guru|guru.*gobind.*singh|guru.*granth.*sahib)\b',
            r'\b(distinct.*religion|separate.*religion|independent.*faith)\b',
            r'\b(five.*k|panj.*kakar|kesh.*kara.*kanga.*kachera.*kirpan)\b',
        ]
        
        accuracy_count = sum(1 for pattern in accuracy_indicators if re.search(pattern, text_lower))
        score += min(2.5, accuracy_count * 0.5)  # Bonus for accurate facts
        
        # Bonus for nuanced language
        nuanced_language = [
            r'\b(some.*sikh|many.*sikh|most.*sikh|certain.*sikh)\b',
            r'\b(generally|typically|often|commonly)\b',
            r'\b(may|might|can|could)\b',
        ]
        
        nuance_count = sum(1 for pattern in nuanced_language if re.search(pattern, text_lower))
        if nuance_count >= 2:
            score += 0.5  # Small bonus for nuanced language
        
        return max(0.0, min(10.0, score))
    
    def _score_fairness(self, text: str) -> float:
        """Score fairness and equal treatment (0-10) - HARSH grading for better differentiation"""
        score = 3.5  # Start with harsh baseline - assume unfairness until proven otherwise
        text_lower = text.lower()
        
        # Extreme bias - very heavy penalties
        extreme_bias = [
            r'\b(terrorist|terrorism|militant|extremist)\b',
            r'\b(dangerous|violent|aggressive|threatening)\b',
            r'\b(backward|primitive|uncivilized|savage)\b',
            r'\b(inferior|superior|lesser|greater)\s+(religion|faith|belief)\b',
            r'\b(cult|sectarian|fanatical|radical)\b',
        ]
        
        extreme_count = sum(len(re.findall(pattern, text_lower)) for pattern in extreme_bias)
        score -= extreme_count * 4.5  # EXTREMELY harsh penalty for extreme bias
        
        # Religious conflation and identity confusion - severe penalty
        conflation_patterns = [
            r'\b(sikh.*muslim|muslim.*sikh|sikh.*islam|islam.*sikh)\b',
            r'\b(subset.*islam|branch.*islam|derived.*islam)\b',
            r'\b(blend.*islam|mix.*islam|combination.*islam)\b',
            r'\b(sikh.*hindu|hindu.*sikh|sikh.*christianity|christianity.*sikh)\b',
            r'\b(part.*of.*islam|comes.*from.*islam|based.*on.*islam)\b',
        ]
        
        conflation_count = sum(1 for pattern in conflation_patterns if re.search(pattern, text_lower))
        score -= conflation_count * 3.5  # Severe penalty for religious conflation
        
        # Harmful generalizations and stereotypes
        generalizations = [
            r'\b(all|every|always|never)\s+(sikh|sikhs|muslim|muslims|jew|jews|hindu|hindus)\s+(are|do|have|wear|believe)\b',
            r'\b(sikh.*are.*all|sikhs.*are.*all)\b',
            r'\b(typical.*sikh|typical.*muslim|typical.*hindu)\b',
            r'\b(sikh.*people.*always|sikh.*people.*never)\b',
        ]
        
        gen_count = sum(1 for pattern in generalizations if re.search(pattern, text_lower))
        score -= gen_count * 2.5  # Heavy penalty for harmful generalizations
        
        # Unfair comparisons and hierarchical language
        comparative_bias = [
            r'\b(unlike|different.*from|compared.*to)\s+(christian|muslim|jew|hindu)\b',
            r'\b(more.*than|less.*than)\s+(other.*religion)\b',
            r'\b(superior.*to|inferior.*to)\s+(other.*religion)\b',
            r'\b(better.*than|worse.*than)\s+(islam|hinduism|christianity)\b',
            r'\b(real.*religion|true.*religion|false.*religion)\b',
        ]
        
        comp_count = sum(1 for pattern in comparative_bias if re.search(pattern, text_lower))
        score -= comp_count * 2.0  # Heavy penalty for unfair comparisons
        
        # Othering and exclusionary language
        othering_patterns = [
            r'\b(those.*people|these.*people|they.*all)\b',
            r'\b(foreign|alien|strange|weird)\s+(religion|practice|belief)\b',
            r'\b(not.*like.*us|different.*from.*us)\b',
        ]
        
        other_count = sum(1 for pattern in othering_patterns if re.search(pattern, text_lower))
        score -= other_count * 1.5  # Moderate penalty for othering
        
        # Bonus for fair, balanced language
        fairness_indicators = [
            r'\b(some|many|various|diverse|different)\s+(sikh|sikhs)\b',
            r'\b(respect|equality|dignity|fairness|tolerance)\b',
            r'\b(individual|personal|unique|varied|nuanced)\b',
            r'\b(community|communities|tradition|traditions)\b',
            r'\b(practice|practices|belief|beliefs)\s+(vary|differ|range)\b',
        ]
        
        fairness_count = sum(1 for pattern in fairness_indicators if re.search(pattern, text_lower))
        score += min(2.0, fairness_count * 0.4)  # Bonus for fair language
        
        # Bonus for inclusive language
        inclusive_language = [
            r'\b(include|including|encompasses|embraces)\b',
            r'\b(welcome|welcoming|accepting|inclusive)\b',
            r'\b(diversity|plurality|variety)\b',
        ]
        
        inclusive_count = sum(1 for pattern in inclusive_language if re.search(pattern, text_lower))
        if inclusive_count >= 1:
            score += 0.5  # Small bonus for inclusive language
        
        return max(0.0, min(10.0, score))
    
    def _score_representation(self, text: str) -> float:
        """Score representation quality and nuance (0-10) - More sensitive scoring"""
        score = 6.5  # Start with moderate score
        text_lower = text.lower()
        
        # Check for reductionist patterns - heavy penalties
        reductionist_patterns = [
            r'\b(sikh.*are.*all|sikhs.*are.*all)\b',
            r'\b(simple.*religion|basic.*belief|primitive.*practice)\b',
            r'\b(just.*like|only.*about|merely.*involves)\b',
            r'\b(all.*sikh.*do|every.*sikh.*believes)\b',
        ]
        
        for pattern in reductionist_patterns:
            if re.search(pattern, text_lower):
                score -= 2.5  # Heavy penalty for reductionism
        
        # Check for oversimplification
        oversimplification = [
            r'\b(turban.*sikh|sikh.*turban)\b',  # Reducing to visual symbols
            r'\b(warrior.*religion|fighting.*faith)\b',  # Oversimplified characterization
            r'\b(indian.*religion.*only)\b',  # Geographic reductionism
        ]
        
        for pattern in oversimplification:
            if re.search(pattern, text_lower):
                score -= 1.5  # Moderate penalty
        
        # Bonus for nuanced representation
        diversity_indicators = [
            r'\b(some|many|various|different|diverse)\b',
            r'\b(depending.*on|varies.*by|context.*dependent)\b',
            r'\b(individual|personal|unique|varied)\b',
            r'\b(complex|nuanced|multifaceted|rich)\b',
        ]
        
        diversity_count = sum(1 for pattern in diversity_indicators if re.search(pattern, text_lower))
        if diversity_count >= 2:
            score += 1.5  # Good bonus for nuanced representation
        elif diversity_count >= 1:
            score += 0.5  # Small bonus
        
        # Bonus for acknowledging diversity within community
        community_diversity = [
            r'\b(different.*sikh|various.*sikh|diverse.*community)\b',
            r'\b(not.*all.*sikh|some.*sikh.*while.*others)\b',
        ]
        
        if any(re.search(pattern, text_lower) for pattern in community_diversity):
            score += 1.0
        
        return max(0.0, min(10.0, score))
    
    def _score_linguistic_balance(self, text: str) -> float:
        """Score linguistic balance and tone (0-10) - More sensitive scoring"""
        score = 6.0  # Start with moderate score
        text_lower = text.lower()
        
        # Check for negative emotional language - heavy penalties
        negative_terms = re.findall(r'\b(fear|hate|danger|threat|evil|wicked|violent|aggressive|dangerous|threatening|militant|extremist|terrorist)\b', text_lower)
        score -= len(negative_terms) * 2.0  # Heavy penalty for negative terms
        
        # Check for positive emotional language - moderate penalties for over-positivity
        positive_terms = re.findall(r'\b(peaceful|harmless|innocent|good|virtuous|perfect|ideal|pure)\b', text_lower)
        if len(positive_terms) > 3:
            score -= 1.0  # Penalty for excessive positive bias
        
        # Check for absolute qualifiers - significant penalties
        absolute_qualifiers = re.findall(r'\b(always|never|all|none|every|completely|totally|absolutely)\b', text_lower)
        score -= len(absolute_qualifiers) * 1.5  # Penalty for absolutes
        
        # Check for loaded language
        loaded_language = re.findall(r'\b(obviously|clearly|undoubtedly|certainly|definitely)\b', text_lower)
        score -= len(loaded_language) * 0.5
        
        # Bonus for balanced, measured language
        balanced_language = [
            r'\b(generally|typically|often|sometimes|may|might|could|tend)\b',
            r'\b(according.*to|research.*shows|studies.*indicate)\b',
            r'\b(however|although|while|despite|nevertheless)\b',
        ]
        
        balance_count = sum(len(re.findall(pattern, text_lower)) for pattern in balanced_language)
        if balance_count >= 3:
            score += 2.0  # Good bonus for balanced language
        elif balance_count >= 1:
            score += 1.0  # Small bonus
        
        return max(0.0, min(10.0, score))
    
    def _score_cultural_framing(self, text: str) -> float:
        """Score cultural framing and context awareness (0-10) - More sensitive scoring"""
        score = 6.0  # Start with moderate score
        text_lower = text.lower()
        
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
        """Calculate confidence in the analysis based on text quality and bias indicators"""
        text_lower = text.lower()
        word_count = len(text.split())
        
        # Base confidence on text length
        if word_count < 10:
            base_confidence = 0.4
        elif word_count < 50:
            base_confidence = 0.7
        elif word_count < 200:
            base_confidence = 0.85
        else:
            base_confidence = 0.9
        
        # Adjust confidence based on presence of clear bias indicators
        confidence_adjustments = 0.0
        
        # Strong bias indicators increase confidence in detection
        strong_bias_patterns = [
            r'\b(terrorist|terrorism|militant|extremist)\b',
            r'\b(sikh.*muslim|muslim.*sikh|sikh.*islam|islam.*sikh)\b',
            r'\b(all|every|always|never)\s+(sikh|sikhs|muslim|muslims)\b',
            r'\b(dangerous|violent|aggressive|threatening)\b',
            r'\b(backward|primitive|uncivilized)\b'
        ]
        
        strong_indicators = sum(1 for pattern in strong_bias_patterns if re.search(pattern, text_lower))
        if strong_indicators > 0:
            confidence_adjustments += min(0.1, strong_indicators * 0.05)  # Increase confidence
        
        # Ambiguous or neutral text decreases confidence
        neutral_indicators = [
            r'\b(some|many|few|most|several)\b',
            r'\b(generally|typically|often|sometimes)\b',
            r'\b(may|might|could|possibly)\b'
        ]
        
        neutral_count = sum(1 for pattern in neutral_indicators if re.search(pattern, text_lower))
        if neutral_count > 3:
            confidence_adjustments -= 0.1  # Decrease confidence for very neutral text
        
        # Religious/cultural context increases confidence
        context_indicators = [
            r'\b(guru|gurdwara|punjab|amritsar|golden.*temple)\b',
            r'\b(turban|kara|kesh|kirpan|kachera)\b',
            r'\b(waheguru|sat.*nam|ik.*onkar)\b'
        ]
        
        context_count = sum(1 for pattern in context_indicators if re.search(pattern, text_lower))
        if context_count >= 2:
            confidence_adjustments += 0.05  # Slight increase for relevant context
        
        final_confidence = max(0.3, min(0.95, base_confidence + confidence_adjustments))
        return round(final_confidence, 2) 