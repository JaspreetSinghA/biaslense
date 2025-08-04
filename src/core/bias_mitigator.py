"""
BAMIP - Bias-Aware Mitigation and Intervention Pipeline
Modular framework for reducing bias in AI-generated text
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class MitigationStrategy(Enum):
    """Available bias mitigation strategies"""
    INSTRUCTIONAL_PROMPTING = "instructional_prompting"
    CONTEXTUAL_REFRAMING = "contextual_reframing"
    RETRIEVAL_GROUNDING = "retrieval_grounding"
    COUNTER_NARRATIVE = "counter_narrative"
    NEUTRAL_LANGUAGE = "neutral_language"


@dataclass
class MitigationResult:
    """Container for bias mitigation results"""
    original_text: str
    mitigated_text: str
    strategy_used: MitigationStrategy
    bias_reduction_score: float
    confidence: float
    explanations: List[str]
    suggested_prompts: List[str]


class BAMIPMitigator:
    """
    Bias-Aware Mitigation and Intervention Pipeline
    Implements modular strategies for reducing bias in AI-generated text
    """
    
    def __init__(self):
        self.mitigation_strategies = self._load_mitigation_strategies()
        self.counter_narratives = self._load_counter_narratives()
        self.neutral_phrases = self._load_neutral_phrases()
        
    def _load_mitigation_strategies(self) -> Dict:
        """Load bias mitigation strategies"""
        return {
            MitigationStrategy.INSTRUCTIONAL_PROMPTING: {
                "description": "Add bias-aware instructions to prompts",
                "templates": [
                    "Please provide a factual, unbiased description of {topic} that avoids stereotypes and generalizations.",
                    "When discussing {topic}, focus on accurate information and avoid making assumptions about groups.",
                    "Provide a balanced perspective on {topic} that respects cultural diversity and individual differences."
                ]
            },
            MitigationStrategy.CONTEXTUAL_REFRAMING: {
                "description": "Reframe biased language with more neutral alternatives",
                "patterns": {
                    r'\b(all|every|always|never)\s+(sikh|muslim|jew|hindu)\b': "some {group}",
                    r'\b(terrorist|militant|extremist)\b': "individual",
                    r'\b(backward|primitive|uncivilized)\b': "traditional",
                    r'\b(dangerous|threatening)\b': "distinctive",
                    r'\b(violent|aggressive)\b': "martial"
                }
            },
            MitigationStrategy.RETRIEVAL_GROUNDING: {
                "description": "Ground responses in factual, verified information",
                "factual_anchors": [
                    "Sikhism is a monotheistic religion founded in the 15th century",
                    "Sikhs believe in equality, service, and honest work",
                    "The turban is a religious article of faith, not a weapon",
                    "Sikhism promotes peace, tolerance, and community service"
                ]
            },
            MitigationStrategy.COUNTER_NARRATIVE: {
                "description": "Provide counter-narratives to challenge stereotypes",
                "narratives": [
                    "Sikhs have contributed significantly to society through service and philanthropy",
                    "The Sikh community is known for its commitment to equality and justice",
                    "Sikhism teaches respect for all religions and peaceful coexistence",
                    "Sikhs have a rich tradition of defending human rights and dignity"
                ]
            },
            MitigationStrategy.NEUTRAL_LANGUAGE: {
                "description": "Replace emotionally charged language with neutral alternatives",
                "replacements": {
                    "fear": "awareness",
                    "threat": "difference", 
                    "dangerous": "distinctive",
                    "violent": "martial",
                    "aggressive": "assertive",
                    "radical": "devout",
                    "extremist": "faithful"
                }
            }
        }
    
    def _load_counter_narratives(self) -> List[str]:
        """Load counter-narratives for bias mitigation"""
        return [
            "Sikhism promotes universal brotherhood and service to humanity",
            "The Sikh community has a long history of humanitarian work and disaster relief",
            "Sikhs believe in the equality of all human beings regardless of religion, caste, or gender",
            "The turban represents dignity, self-respect, and commitment to Sikh values",
            "Sikhism emphasizes honest work, sharing with others, and remembering God",
            "Sikhs have been at the forefront of civil rights movements and social justice",
            "The Sikh community values education, hard work, and community service"
        ]
    
    def _load_neutral_phrases(self) -> Dict[str, str]:
        """Load neutral language alternatives"""
        return {
            "all sikhs": "some Sikhs",
            "every sikh": "many Sikhs", 
            "sikhs always": "Sikhs often",
            "sikhs never": "Sikhs rarely",
            "terrorist": "individual",
            "militant": "devout",
            "extremist": "faithful",
            "radical": "traditional",
            "fundamentalist": "practicing",
            "violent": "martial",
            "aggressive": "assertive",
            "dangerous": "distinctive",
            "threatening": "noticeable"
        }
    
    def mitigate_bias(self, text: str, strategy: MitigationStrategy = None) -> MitigationResult:
        """
        Apply bias mitigation strategies to input text
        
        Args:
            text: Input text to mitigate
            strategy: Specific strategy to use (if None, uses best-fit approach)
            
        Returns:
            MitigationResult with mitigated text and analysis
        """
        original_text = text
        
        if strategy is None:
            strategy = self._select_best_strategy(text)
        
        mitigated_text = self._apply_strategy(text, strategy)
        bias_reduction = self._calculate_bias_reduction(original_text, mitigated_text)
        confidence = self._calculate_mitigation_confidence(original_text, mitigated_text)
        explanations = self._generate_mitigation_explanations(original_text, mitigated_text, strategy)
        suggested_prompts = self._generate_suggested_prompts(strategy)
        
        return MitigationResult(
            original_text=original_text,
            mitigated_text=mitigated_text,
            strategy_used=strategy,
            bias_reduction_score=bias_reduction,
            confidence=confidence,
            explanations=explanations,
            suggested_prompts=suggested_prompts
        )
    
    def _select_best_strategy(self, text: str) -> MitigationStrategy:
        """Select the most appropriate mitigation strategy based on text content"""
        text_lower = text.lower()
        
        # Check for different bias patterns
        if re.search(r'\b(all|every|always|never)\s+(sikh|muslim|jew|hindu)\b', text_lower):
            return MitigationStrategy.CONTEXTUAL_REFRAMING
        
        if re.search(r'\b(terrorist|militant|extremist|radical)\b', text_lower):
            return MitigationStrategy.NEUTRAL_LANGUAGE
        
        if re.search(r'\b(backward|primitive|uncivilized)\b', text_lower):
            return MitigationStrategy.COUNTER_NARRATIVE
        
        if re.search(r'\b(sikh.*muslim|muslim.*sikh|sikh.*islam|islam.*sikh)\b', text_lower):
            return MitigationStrategy.RETRIEVAL_GROUNDING
        
        # Check for emotional language
        if re.search(r'\b(fear|danger|threat|violent|aggressive)\b', text_lower):
            return MitigationStrategy.NEUTRAL_LANGUAGE
        
        # Default to instructional prompting for general bias
        return MitigationStrategy.INSTRUCTIONAL_PROMPTING
    
    def _apply_strategy(self, text: str, strategy: MitigationStrategy) -> str:
        """Apply the selected mitigation strategy"""
        if strategy == MitigationStrategy.CONTEXTUAL_REFRAMING:
            return self._apply_contextual_reframing(text)
        elif strategy == MitigationStrategy.NEUTRAL_LANGUAGE:
            return self._apply_neutral_language(text)
        elif strategy == MitigationStrategy.COUNTER_NARRATIVE:
            return self._apply_counter_narrative(text)
        elif strategy == MitigationStrategy.RETRIEVAL_GROUNDING:
            return self._apply_retrieval_grounding(text)
        else:
            return text  # No text modification for instructional prompting
    
    def _apply_contextual_reframing(self, text: str) -> str:
        """Apply contextual reframing to reduce bias"""
        mitigated_text = text
        
        # Apply pattern replacements
        patterns = self.mitigation_strategies[MitigationStrategy.CONTEXTUAL_REFRAMING]["patterns"]
        for pattern, replacement in patterns.items():
            # Handle group-specific replacements
            if "{group}" in replacement:
                # Extract the group name from the match
                matches = re.findall(pattern, mitigated_text, flags=re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        group = match[1] if len(match) > 1 else "individuals"
                    else:
                        group = "individuals"
                    specific_replacement = replacement.replace("{group}", group)
                    mitigated_text = re.sub(pattern, specific_replacement, mitigated_text, flags=re.IGNORECASE, count=1)
            else:
                mitigated_text = re.sub(pattern, replacement, mitigated_text, flags=re.IGNORECASE)
        
        return mitigated_text
    
    def _apply_neutral_language(self, text: str) -> str:
        """Replace emotionally charged language with neutral alternatives"""
        mitigated_text = text
        
        for biased_term, neutral_term in self.neutral_phrases.items():
            pattern = r'\b' + re.escape(biased_term) + r'\b'
            mitigated_text = re.sub(pattern, neutral_term, mitigated_text, flags=re.IGNORECASE)
        
        return mitigated_text
    
    def _apply_counter_narrative(self, text: str) -> str:
        """Add counter-narratives to challenge stereotypes"""
        # Add a counter-narrative at the end
        counter_narrative = "It's important to note that " + self.counter_narratives[0].lower()
        return text + ". " + counter_narrative + "."
    
    def _apply_retrieval_grounding(self, text: str) -> str:
        """Ground the text in factual information"""
        factual_anchor = self.mitigation_strategies[MitigationStrategy.RETRIEVAL_GROUNDING]["factual_anchors"][0]
        return factual_anchor + ". " + text
    
    def _calculate_bias_reduction(self, original: str, mitigated: str) -> float:
        """Calculate the degree of bias reduction"""
        # Simple heuristic based on bias term reduction
        bias_terms = [
            'all', 'every', 'always', 'never', 'terrorist', 'militant', 
            'extremist', 'radical', 'backward', 'primitive', 'dangerous'
        ]
        
        original_count = sum(1 for term in bias_terms if term in original.lower())
        mitigated_count = sum(1 for term in bias_terms if term in mitigated.lower())
        
        if original_count == 0:
            return 1.0
        
        reduction = (original_count - mitigated_count) / original_count
        return max(0.0, min(1.0, reduction))
    
    def _calculate_mitigation_confidence(self, original: str, mitigated: str) -> float:
        """Calculate confidence in the mitigation approach"""
        # Confidence based on text similarity and bias reduction
        bias_reduction = self._calculate_bias_reduction(original, mitigated)
        
        # Higher confidence if we made meaningful changes
        if bias_reduction > 0.5:
            return 0.9
        elif bias_reduction > 0.2:
            return 0.7
        else:
            return 0.5
    
    def _generate_mitigation_explanations(self, original: str, mitigated: str, strategy: MitigationStrategy) -> List[str]:
        """Generate explanations for the mitigation approach"""
        explanations = []
        
        strategy_info = self.mitigation_strategies[strategy]
        explanations.append(f"Applied {strategy.value.replace('_', ' ')} strategy")
        explanations.append(f"Strategy: {strategy_info['description']}")
        
        bias_reduction = self._calculate_bias_reduction(original, mitigated)
        if bias_reduction > 0:
            explanations.append(f"Reduced bias by {bias_reduction:.1%}")
        
        return explanations
    
    def _generate_suggested_prompts(self, strategy: MitigationStrategy) -> List[str]:
        """Generate suggested prompts for future bias-free responses"""
        if strategy == MitigationStrategy.INSTRUCTIONAL_PROMPTING:
            return self.mitigation_strategies[strategy]["templates"]
        else:
            return [
                "Please provide a factual, unbiased description that avoids stereotypes.",
                "Focus on accurate information and avoid making assumptions about groups.",
                "Provide a balanced perspective that respects cultural diversity."
            ]
    
    def get_available_strategies(self) -> List[Dict]:
        """Get list of available mitigation strategies"""
        return [
            {
                "strategy": strategy.value,
                "description": info["description"],
                "applicable_to": self._get_applicable_patterns(strategy)
            }
            for strategy, info in self.mitigation_strategies.items()
        ]
    
    def _get_applicable_patterns(self, strategy: MitigationStrategy) -> List[str]:
        """Get patterns that each strategy can address"""
        if strategy == MitigationStrategy.CONTEXTUAL_REFRAMING:
            return ["Generalizations", "Stereotypes", "Absolute statements"]
        elif strategy == MitigationStrategy.NEUTRAL_LANGUAGE:
            return ["Emotional language", "Polarizing terms", "Loaded words"]
        elif strategy == MitigationStrategy.COUNTER_NARRATIVE:
            return ["Negative stereotypes", "Cultural bias", "Misrepresentations"]
        elif strategy == MitigationStrategy.RETRIEVAL_GROUNDING:
            return ["Factual errors", "Religious conflation", "Historical inaccuracies"]
        else:
            return ["General bias", "Prompt-level issues"] 