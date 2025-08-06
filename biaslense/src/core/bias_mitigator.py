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
    used_sources: List[dict] = None  # For retrieval-based grounding sources


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
                "description": "Ground responses in factual, verified information from trusted Sikh sources",
                "factual_anchors": [
                    {
                        "text": "Sikhism is a distinct monotheistic religion founded in the 15th century by Guru Nanak, separate from Islam and other religions",
                        "source": "Sikh Coalition Educational Resources",
                        "url": "https://www.sikhcoalition.org/about-sikhs/"
                    },
                    {
                        "text": "Sikhs believe in equality, service, and honest work as core principles established by Guru Nanak",
                        "source": "Guru Granth Sahib, Ang 1",
                        "url": "https://www.srigurugranth.org/"
                    },
                    {
                        "text": "The turban (dastaar) is a religious article of faith representing dignity, commitment, and spiritual discipline",
                        "source": "Sikh Research Institute",
                        "url": "https://www.sikhri.org/articles/the-turban"
                    },
                    {
                        "text": "Sikhism promotes peace, tolerance, and community service through the concept of seva (selfless service)",
                        "source": "World Sikh Organization",
                        "url": "https://www.worldsikh.org/sikh_beliefs"
                    },
                    {
                        "text": "Sikhs follow the teachings of the ten Gurus and the Guru Granth Sahib, their eternal living Guru",
                        "source": "Shiromani Gurdwara Parbandhak Committee",
                        "url": "https://sgpc.net/sikhism/"
                    }
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
        """Load neutral language alternatives - More comprehensive"""
        return {
            # Generalizations
            "all sikhs": "some Sikhs",
            "every sikh": "many Sikhs", 
            "sikhs always": "Sikhs often",
            "sikhs never": "Sikhs rarely",
            "all muslims": "some Muslims",
            "every muslim": "many Muslims",
            
            # Terrorism terms - completely remove
            "terrorist": "individual",
            "terrorism": "extremism",
            "militant": "devout",
            "extremist": "faithful",
            "radical": "traditional",
            "fundamentalist": "practicing",
            
            # Violent terms
            "violent": "martial",
            "aggressive": "assertive",
            "dangerous": "distinctive",
            "threatening": "noticeable",
            "fear": "concern",
            "danger": "risk",
            "threat": "challenge",
            
            # Religious conflation
            "sikh muslim": "Sikh",
            "muslim sikh": "Sikh",
            "sikh islam": "Sikhism",
            "islam sikh": "Sikhism",
            
            # Cultural bias
            "backward": "traditional",
            "primitive": "ancient",
            "uncivilized": "different",
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
        
        # Clear previous sources before applying strategy
        self.clear_used_sources()
        
        mitigated_text = self._apply_strategy(text, strategy)
        bias_reduction = self._calculate_bias_reduction(original_text, mitigated_text)
        confidence = self._calculate_mitigation_confidence(original_text, mitigated_text)
        explanations = self._generate_mitigation_explanations(original_text, mitigated_text, strategy)
        suggested_prompts = self._generate_suggested_prompts(strategy)
        
        # Get sources used during mitigation (for retrieval grounding)
        used_sources = self.get_used_sources() if strategy == MitigationStrategy.RETRIEVAL_GROUNDING else None
        
        return MitigationResult(
            original_text=original_text,
            mitigated_text=mitigated_text,
            strategy_used=strategy,
            bias_reduction_score=bias_reduction,
            confidence=confidence,
            explanations=explanations,
            suggested_prompts=suggested_prompts,
            used_sources=used_sources
        )
    
    def _select_best_strategy(self, text: str) -> MitigationStrategy:
        """Select the most appropriate mitigation strategy based on text content"""
        text_lower = text.lower()
        
        # Priority 1: Religious conflation (most harmful)
        if re.search(r'\b(sikh.*muslim|muslim.*sikh|sikh.*islam|islam.*sikh|sikh.*subset.*islam)\b', text_lower):
            return MitigationStrategy.RETRIEVAL_GROUNDING
        
        # Priority 2: Terrorism association (very harmful)
        if re.search(r'\b(terrorist|terrorism|militant|extremist)\b', text_lower):
            return MitigationStrategy.NEUTRAL_LANGUAGE
        
        # Priority 3: Harmful generalizations
        if re.search(r'\b(all|every|always|never)\s+(sikh|muslim|jew|hindu)\b', text_lower):
            return MitigationStrategy.CONTEXTUAL_REFRAMING
        
        # Priority 4: Cultural bias
        if re.search(r'\b(backward|primitive|uncivilized)\b', text_lower):
            return MitigationStrategy.COUNTER_NARRATIVE
        
        # Priority 5: Emotional language
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
        """Replace emotionally charged language with neutral alternatives - More aggressive"""
        mitigated_text = text
        
        # Apply replacements
        for biased_term, neutral_term in self.neutral_phrases.items():
            pattern = r'\b' + re.escape(biased_term) + r'\b'
            mitigated_text = re.sub(pattern, neutral_term, mitigated_text, flags=re.IGNORECASE)
        
        # Additional aggressive replacements for terrorism terms
        terrorism_replacements = {
            r'\bterrorist\b': 'individual',
            r'\bterrorism\b': 'extremism',
            r'\bmilitant\b': 'devout',
            r'\bextremist\b': 'faithful',
            r'\bradical\b': 'traditional',
            r'\bfundamentalist\b': 'practicing',
        }
        
        for pattern, replacement in terrorism_replacements.items():
            mitigated_text = re.sub(pattern, replacement, mitigated_text, flags=re.IGNORECASE)
        
        return mitigated_text
    
    def _apply_counter_narrative(self, text: str) -> str:
        """Add counter-narratives to challenge stereotypes"""
        # Add a counter-narrative at the end
        counter_narrative = "It's important to note that " + self.counter_narratives[0].lower()
        return text + ". " + counter_narrative + "."
    
    def _apply_retrieval_grounding(self, text: str) -> str:
        """Ground the text in factual information from trusted Sikh sources"""
        factual_anchors = self.mitigation_strategies[MitigationStrategy.RETRIEVAL_GROUNDING]["factual_anchors"]
        
        # Select most relevant anchor based on text content
        selected_anchor = factual_anchors[0]  # Default to first
        
        # Simple keyword matching to select most relevant source
        text_lower = text.lower()
        if "turban" in text_lower or "dastaar" in text_lower:
            selected_anchor = factual_anchors[2]  # Turban info
        elif "guru" in text_lower or "scripture" in text_lower:
            selected_anchor = factual_anchors[4]  # Guru Granth Sahib info
        elif "service" in text_lower or "seva" in text_lower:
            selected_anchor = factual_anchors[3]  # Service info
        elif "equality" in text_lower or "principles" in text_lower:
            selected_anchor = factual_anchors[1]  # Core principles
        
        # Store the selected source for later display
        if not hasattr(self, '_used_sources'):
            self._used_sources = []
        self._used_sources.append(selected_anchor)
        
        return selected_anchor["text"] + ". " + text
    
    def get_used_sources(self):
        """Get the sources used in the last mitigation"""
        return getattr(self, '_used_sources', [])
    
    def clear_used_sources(self):
        """Clear the used sources tracker"""
        if hasattr(self, '_used_sources'):
            self._used_sources = []
    
    def _calculate_bias_reduction(self, original: str, mitigated: str) -> float:
        """Calculate the degree of bias reduction - More comprehensive"""
        # Comprehensive bias terms
        bias_terms = [
            'all', 'every', 'always', 'never', 'terrorist', 'terrorism', 'militant', 
            'extremist', 'radical', 'backward', 'primitive', 'dangerous', 'violent',
            'aggressive', 'fear', 'danger', 'threat', 'sikh muslim', 'muslim sikh',
            'sikh islam', 'islam sikh', 'subset islam'
        ]
        
        original_count = sum(1 for term in bias_terms if term in original.lower())
        mitigated_count = sum(1 for term in bias_terms if term in mitigated.lower())
        
        if original_count == 0:
            return 1.0
        
        reduction = (original_count - mitigated_count) / original_count
        
        # Bonus for factual grounding
        if "Sikhism is a distinct" in mitigated or "Guru Nanak" in mitigated:
            reduction += 0.2
        
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