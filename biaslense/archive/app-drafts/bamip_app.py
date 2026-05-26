"""
BAMIP Pipeline - Bias-Aware Mitigation and Intervention Pipeline
Follows the research framework: Prompt → AI Response → Bias Detection → Mitigation → Improved Response
Incorporates research findings on optimal strategy selection and model-specific considerations
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .rubric_scoring import BiasRubricScorer, BiasAnalysisResult
from .embedding_checker import EmbeddingChecker, SimilarityResult
from .bias_mitigator import BAMIPMitigator, MitigationResult, MitigationStrategy


class RiskLevel(Enum):
    """Risk levels for bias assessment"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AIModel(Enum):
    """Supported AI models with their bias characteristics"""
    GPT_4 = "gpt-4"
    GPT_3_5 = "gpt-3.5-turbo"
    CLAUDE_3 = "claude-3"
    CLAUDE_2 = "claude-2"
    LLAMA_2 = "llama-2"
    GEMINI = "gemini"
    UNKNOWN = "unknown"


@dataclass
class BAMIPResult:
    """Complete BAMIP pipeline result"""
    original_prompt: str
    ai_response: str
    ai_model: Optional[AIModel]
    bias_detection_result: BiasAnalysisResult
    similarity_result: SimilarityResult
    risk_level: RiskLevel
    mitigation_result: MitigationResult
    improved_response: str
    recommendations: List[str]
    strategy_selection_reasoning: str


class BAMIPPipeline:
    """
    Complete BAMIP Pipeline following the research framework
    Incorporates research findings on optimal strategy selection
    """
    
    def __init__(self):
        self.scorer = BiasRubricScorer()
        self.embedder = EmbeddingChecker()
        self.mitigator = BAMIPMitigator()
        
        # Research-based strategy effectiveness mapping
        self.strategy_effectiveness = self._load_research_findings()
        
        # Model-specific bias characteristics
        self.model_bias_profiles = self._load_model_profiles()
        
    def _load_research_findings(self) -> Dict:
        """Load research findings on which strategies work best for which bias types"""
        return {
            # Based on research findings from the paper
            "religious_conflation": {
                "best_strategy": MitigationStrategy.RETRIEVAL_GROUNDING,
                "effectiveness": 0.85,
                "reasoning": "Research shows retrieval grounding is most effective for factual errors and religious conflation"
            },
            "terrorism_association": {
                "best_strategy": MitigationStrategy.NEUTRAL_LANGUAGE,
                "effectiveness": 0.78,
                "reasoning": "Neutral language replacement shows highest effectiveness for terrorism-related bias"
            },
            "harmful_generalizations": {
                "best_strategy": MitigationStrategy.CONTEXTUAL_REFRAMING,
                "effectiveness": 0.82,
                "reasoning": "Contextual reframing most effective for reducing harmful generalizations"
            },
            "cultural_bias": {
                "best_strategy": MitigationStrategy.COUNTER_NARRATIVE,
                "effectiveness": 0.76,
                "reasoning": "Counter narratives most effective for challenging cultural stereotypes"
            },
            "emotional_language": {
                "best_strategy": MitigationStrategy.NEUTRAL_LANGUAGE,
                "effectiveness": 0.71,
                "reasoning": "Neutral language replacement effective for emotional bias"
            },
            "factual_errors": {
                "best_strategy": MitigationStrategy.RETRIEVAL_GROUNDING,
                "effectiveness": 0.88,
                "reasoning": "Retrieval grounding most effective for correcting factual inaccuracies"
            }
        }
    
    def _load_model_profiles(self) -> Dict:
        """Load model-specific bias characteristics based on research"""
        return {
            AIModel.GPT_4: {
                "bias_tendencies": ["religious_conflation", "harmful_generalizations"],
                "strategy_preferences": [MitigationStrategy.RETRIEVAL_GROUNDING, MitigationStrategy.CONTEXTUAL_REFRAMING],
                "confidence_modifier": 1.1  # Higher confidence in GPT-4 responses
            },
            AIModel.GPT_3_5: {
                "bias_tendencies": ["terrorism_association", "emotional_language"],
                "strategy_preferences": [MitigationStrategy.NEUTRAL_LANGUAGE, MitigationStrategy.INSTRUCTIONAL_PROMPTING],
                "confidence_modifier": 0.9  # Lower confidence in GPT-3.5 responses
            },
            AIModel.CLAUDE_3: {
                "bias_tendencies": ["cultural_bias", "factual_errors"],
                "strategy_preferences": [MitigationStrategy.COUNTER_NARRATIVE, MitigationStrategy.RETRIEVAL_GROUNDING],
                "confidence_modifier": 1.0
            },
            AIModel.CLAUDE_2: {
                "bias_tendencies": ["religious_conflation", "emotional_language"],
                "strategy_preferences": [MitigationStrategy.RETRIEVAL_GROUNDING, MitigationStrategy.NEUTRAL_LANGUAGE],
                "confidence_modifier": 0.95
            },
            AIModel.LLAMA_2: {
                "bias_tendencies": ["terrorism_association", "harmful_generalizations"],
                "strategy_preferences": [MitigationStrategy.NEUTRAL_LANGUAGE, MitigationStrategy.CONTEXTUAL_REFRAMING],
                "confidence_modifier": 0.85
            },
            AIModel.GEMINI: {
                "bias_tendencies": ["factual_errors", "cultural_bias"],
                "strategy_preferences": [MitigationStrategy.RETRIEVAL_GROUNDING, MitigationStrategy.COUNTER_NARRATIVE],
                "confidence_modifier": 1.0
            },
            AIModel.UNKNOWN: {
                "bias_tendencies": ["religious_conflation", "terrorism_association", "harmful_generalizations"],
                "strategy_preferences": [MitigationStrategy.RETRIEVAL_GROUNDING, MitigationStrategy.NEUTRAL_LANGUAGE],
                "confidence_modifier": 1.0
            }
        }
        
    def process_prompt(self, prompt: str, ai_response: str, ai_model: Optional[AIModel] = None) -> BAMIPResult:
        """
        Complete BAMIP pipeline processing with research-based strategy selection
        
        Args:
            prompt: Original user prompt
            ai_response: Response from AI model
            ai_model: AI model used (optional, for model-specific considerations)
            
        Returns:
            BAMIPResult with complete analysis and mitigation
        """
        
        if ai_model is None:
            ai_model = AIModel.UNKNOWN
        
        # STEP 1: Bias Detection
        bias_result = self.scorer.score_text(ai_response)
        similarity_result = self.embedder.compute_similarity(ai_response)
        
        # STEP 2: Risk Assessment
        risk_level = self._assess_risk(bias_result, similarity_result)
        
        # STEP 3: Research-Based Strategy Selection
        selected_strategy, reasoning = self._select_optimal_strategy(
            ai_response, bias_result, similarity_result, ai_model
        )
        
        # STEP 4: BAMIP Intervention
        mitigation_result = self.mitigator.mitigate_bias(ai_response, selected_strategy)
        
        # STEP 5: Generate Improved Response
        improved_response = self._generate_improved_response(
            prompt, ai_response, mitigation_result, risk_level, ai_model
        )
        
        # STEP 6: Generate Recommendations
        recommendations = self._generate_recommendations(
            bias_result, similarity_result, risk_level, mitigation_result, ai_model
        )
        
        return BAMIPResult(
            original_prompt=prompt,
            ai_response=ai_response,
            ai_model=ai_model,
            bias_detection_result=bias_result,
            similarity_result=similarity_result,
            risk_level=risk_level,
            mitigation_result=mitigation_result,
            improved_response=improved_response,
            recommendations=recommendations,
            strategy_selection_reasoning=reasoning
        )
    
    def _select_optimal_strategy(self, ai_response: str, bias_result: BiasAnalysisResult, 
                               similarity_result: SimilarityResult, ai_model: AIModel) -> Tuple[MitigationStrategy, str]:
        """Select optimal strategy based on research findings and model characteristics"""
        
        text_lower = ai_response.lower()
        detected_bias_types = []
        
        # Detect specific bias types based on research categories
        if re.search(r'\b(sikh.*muslim|muslim.*sikh|sikh.*islam|islam.*sikh|sikh.*subset.*islam|essentially.*muslim)\b', text_lower):
            detected_bias_types.append("religious_conflation")
        
        if re.search(r'\b(terrorist|terrorism|militant|extremist)\b', text_lower):
            detected_bias_types.append("terrorism_association")
        
        if re.search(r'\b(all|every|always|never)\s+(sikh|muslim|jew|hindu)\b', text_lower):
            detected_bias_types.append("harmful_generalizations")
        
        if re.search(r'\b(backward|primitive|uncivilized|outdated)\b', text_lower):
            detected_bias_types.append("cultural_bias")
        
        if re.search(r'\b(fear|danger|threat|violent|aggressive|dangerous|threatening)\b', text_lower):
            detected_bias_types.append("emotional_language")
        
        if bias_result.accuracy_score < 5.0:
            detected_bias_types.append("factual_errors")
        
        # Select strategy based on research findings
        best_strategy = None
        best_effectiveness = 0.0
        reasoning = ""
        
        for bias_type in detected_bias_types:
            if bias_type in self.strategy_effectiveness:
                effectiveness = self.strategy_effectiveness[bias_type]["effectiveness"]
                strategy = self.strategy_effectiveness[bias_type]["best_strategy"]
                bias_reasoning = self.strategy_effectiveness[bias_type]["reasoning"]
                
                # Apply model-specific modifier
                model_profile = self.model_bias_profiles[ai_model]
                if strategy in model_profile["strategy_preferences"]:
                    effectiveness *= 1.1  # Boost effectiveness for model-preferred strategies
                
                if effectiveness > best_effectiveness:
                    best_effectiveness = effectiveness
                    best_strategy = strategy
                    reasoning = f"Selected {strategy.value.replace('_', ' ')} for {bias_type}: {bias_reasoning}"
        
        # Fallback to model-preferred strategy if no specific bias detected
        if best_strategy is None:
            model_profile = self.model_bias_profiles[ai_model]
            best_strategy = model_profile["strategy_preferences"][0]
            reasoning = f"No specific bias detected, using model-preferred strategy: {best_strategy.value.replace('_', ' ')}"
        
        return best_strategy, reasoning
    
    def _assess_risk(self, bias_result: BiasAnalysisResult, similarity_result: SimilarityResult) -> RiskLevel:
        """Assess overall risk level based on bias and similarity analysis"""
        
        # Risk assessment based on rubric score
        if bias_result.overall_score >= 8.5:
            rubric_risk = RiskLevel.LOW
        elif bias_result.overall_score >= 6.0:
            rubric_risk = RiskLevel.MEDIUM
        else:
            rubric_risk = RiskLevel.HIGH
        
        # Risk assessment based on similarity
        if similarity_result.max_similarity >= 0.8:
            similarity_risk = RiskLevel.HIGH
        elif similarity_result.max_similarity >= 0.5:
            similarity_risk = RiskLevel.MEDIUM
        else:
            similarity_risk = RiskLevel.LOW
        
        # Combine risks - take the higher risk level
        if rubric_risk == RiskLevel.HIGH or similarity_risk == RiskLevel.HIGH:
            return RiskLevel.HIGH
        elif rubric_risk == RiskLevel.MEDIUM or similarity_risk == RiskLevel.MEDIUM:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_improved_response(self, prompt: str, ai_response: str, 
                                  mitigation_result: MitigationResult, 
                                  risk_level: RiskLevel,
                                  ai_model: AIModel) -> str:
        """Generate improved response based on risk level, mitigation, and model"""
        
        if risk_level == RiskLevel.LOW:
            # Low risk - minimal changes, just add disclaimer
            model_info = f" (Generated by {ai_model.value})" if ai_model != AIModel.UNKNOWN else ""
            return f"{ai_response}\n\n*Note: This response has been reviewed for bias and found to be generally balanced.{model_info}*"
        
        elif risk_level == RiskLevel.MEDIUM:
            # Medium risk - apply mitigation and add context
            improved = mitigation_result.mitigated_text
            model_info = f" (Generated by {ai_model.value})" if ai_model != AIModel.UNKNOWN else ""
            improved += f"\n\n*This response has been improved to reduce potential bias and provide more balanced information.{model_info}*"
            return improved
        
        else:  # HIGH risk
            # High risk - significant mitigation and strong disclaimer
            improved = mitigation_result.mitigated_text
            
            model_info = f" (Generated by {ai_model.value})" if ai_model != AIModel.UNKNOWN else ""
            disclaimer = (
                f"\n\n⚠️ **Bias Alert**: The original response contained significant bias. "
                f"This version has been modified to provide more accurate and balanced information. "
                f"Please verify facts from reliable sources.{model_info}"
            )
            
            return improved + disclaimer
    
    def _generate_recommendations(self, bias_result: BiasAnalysisResult, 
                                similarity_result: SimilarityResult,
                                risk_level: RiskLevel,
                                mitigation_result: MitigationResult,
                                ai_model: AIModel) -> List[str]:
        """Generate specific recommendations based on analysis and model"""
        
        recommendations = []
        
        # Risk-based recommendations
        if risk_level == RiskLevel.HIGH:
            recommendations.append("🚨 HIGH RISK: This content requires significant revision before use")
            recommendations.append("📚 Use suggested bias-free prompts for future queries")
            recommendations.append("🔍 Verify all factual claims from authoritative sources")
        
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.append("⚠️ MEDIUM RISK: Review content before publication")
            recommendations.append("📝 Consider additional fact-checking")
            recommendations.append("🎯 Apply suggested mitigation strategies")
        
        else:  # LOW risk
            recommendations.append("✅ LOW RISK: Content is generally balanced")
            recommendations.append("📖 Continue using similar prompts for this topic")
        
        # Model-specific recommendations
        model_profile = self.model_bias_profiles[ai_model]
        if ai_model != AIModel.UNKNOWN:
            recommendations.append(f"🤖 Model-specific: {ai_model.value} tends toward {', '.join(model_profile['bias_tendencies'])}")
            recommendations.append(f"🎯 Preferred strategies for {ai_model.value}: {', '.join([s.value.replace('_', ' ') for s in model_profile['strategy_preferences'][:2]])}")
        
        # Strategy-specific recommendations
        if mitigation_result.strategy_used == MitigationStrategy.RETRIEVAL_GROUNDING:
            recommendations.append("📚 Add more factual context about the topic")
            recommendations.append("🔍 Include verified sources and references")
        
        elif mitigation_result.strategy_used == MitigationStrategy.NEUTRAL_LANGUAGE:
            recommendations.append("🗣️ Replace emotional language with neutral terms")
            recommendations.append("⚖️ Use balanced, objective language")
        
        elif mitigation_result.strategy_used == MitigationStrategy.CONTEXTUAL_REFRAMING:
            recommendations.append("🔄 Avoid generalizations about groups")
            recommendations.append("📊 Use specific, evidence-based statements")
        
        elif mitigation_result.strategy_used == MitigationStrategy.COUNTER_NARRATIVE:
            recommendations.append("🔄 Include diverse perspectives")
            recommendations.append("📖 Add counter-examples to challenge stereotypes")
        
        # Bias-specific recommendations
        if bias_result.accuracy_score < 5.0:
            recommendations.append("📖 Fact-check all claims about religious/cultural groups")
        
        if bias_result.fairness_score < 5.0:
            recommendations.append("⚖️ Avoid stereotypes and generalizations")
        
        if similarity_result.max_similarity > 0.5:
            recommendations.append("🔍 Review for potential stereotype associations")
        
        return recommendations
    
    def get_pipeline_summary(self, result: BAMIPResult) -> Dict:
        """Get a summary of the BAMIP pipeline results"""
        
        return {
            "risk_level": result.risk_level.value,
            "bias_score": result.bias_detection_result.overall_score,
            "similarity_score": result.similarity_result.max_similarity,
            "mitigation_strategy": result.mitigation_result.strategy_used.value,
            "bias_reduction": result.mitigation_result.bias_reduction_score,
            "confidence": result.bias_detection_result.confidence,
            "key_issues": result.bias_detection_result.explanations,
            "recommendations": result.recommendations,
            "strategy_reasoning": result.strategy_selection_reasoning,
            "ai_model": result.ai_model.value if result.ai_model else "unknown"
        }
    
    def apply_multiple_strategies(self, ai_response: str) -> str:
        """Apply multiple BAMIP strategies for comprehensive mitigation"""
        
        # Apply strategies in order of priority
        strategies = [
            MitigationStrategy.RETRIEVAL_GROUNDING,
            MitigationStrategy.NEUTRAL_LANGUAGE,
            MitigationStrategy.CONTEXTUAL_REFRAMING,
            MitigationStrategy.COUNTER_NARRATIVE
        ]
        
        mitigated_text = ai_response
        
        for strategy in strategies:
            # Check if strategy is applicable
            if self._is_strategy_applicable(mitigated_text, strategy):
                result = self.mitigator.mitigate_bias(mitigated_text, strategy)
                mitigated_text = result.mitigated_text
        
        return mitigated_text
    
    def _is_strategy_applicable(self, text: str, strategy: MitigationStrategy) -> bool:
        """Check if a strategy is applicable to the text"""
        
        text_lower = text.lower()
        
        if strategy == MitigationStrategy.RETRIEVAL_GROUNDING:
            return bool(re.search(r'\b(sikh.*muslim|muslim.*sikh|sikh.*islam|islam.*sikh|subset.*islam)\b', text_lower))
        
        elif strategy == MitigationStrategy.NEUTRAL_LANGUAGE:
            return bool(re.search(r'\b(terrorist|terrorism|militant|extremist|fear|danger|threat|violent)\b', text_lower))
        
        elif strategy == MitigationStrategy.CONTEXTUAL_REFRAMING:
            return bool(re.search(r'\b(all|every|always|never)\s+(sikh|muslim|jew|hindu)\b', text_lower))
        
        elif strategy == MitigationStrategy.COUNTER_NARRATIVE:
            return bool(re.search(r'\b(backward|primitive|uncivilized)\b', text_lower))
        
        return False 