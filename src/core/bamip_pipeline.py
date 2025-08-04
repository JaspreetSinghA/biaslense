"""
BAMIP Pipeline - Bias-Aware Mitigation and Intervention Pipeline
Follows the research framework: Prompt → AI Response → Bias Detection → Mitigation → Improved Response
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


@dataclass
class BAMIPResult:
    """Complete BAMIP pipeline result"""
    original_prompt: str
    ai_response: str
    bias_detection_result: BiasAnalysisResult
    similarity_result: SimilarityResult
    risk_level: RiskLevel
    mitigation_result: MitigationResult
    improved_response: str
    recommendations: List[str]


class BAMIPPipeline:
    """
    Complete BAMIP Pipeline following the research framework
    """
    
    def __init__(self):
        self.scorer = BiasRubricScorer()
        self.embedder = EmbeddingChecker()
        self.mitigator = BAMIPMitigator()
        
    def process_prompt(self, prompt: str, ai_response: str) -> BAMIPResult:
        """
        Complete BAMIP pipeline processing
        
        Args:
            prompt: Original user prompt
            ai_response: Response from AI model
            
        Returns:
            BAMIPResult with complete analysis and mitigation
        """
        
        # STEP 1: Bias Detection
        bias_result = self.scorer.score_text(ai_response)
        similarity_result = self.embedder.compute_similarity(ai_response)
        
        # STEP 2: Risk Assessment
        risk_level = self._assess_risk(bias_result, similarity_result)
        
        # STEP 3: BAMIP Intervention
        mitigation_result = self.mitigator.mitigate_bias(ai_response)
        
        # STEP 4: Generate Improved Response
        improved_response = self._generate_improved_response(
            prompt, ai_response, mitigation_result, risk_level
        )
        
        # STEP 5: Generate Recommendations
        recommendations = self._generate_recommendations(
            bias_result, similarity_result, risk_level, mitigation_result
        )
        
        return BAMIPResult(
            original_prompt=prompt,
            ai_response=ai_response,
            bias_detection_result=bias_result,
            similarity_result=similarity_result,
            risk_level=risk_level,
            mitigation_result=mitigation_result,
            improved_response=improved_response,
            recommendations=recommendations
        )
    
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
                                  risk_level: RiskLevel) -> str:
        """Generate improved response based on risk level and mitigation"""
        
        if risk_level == RiskLevel.LOW:
            # Low risk - minimal changes, just add disclaimer
            return f"{ai_response}\n\n*Note: This response has been reviewed for bias and found to be generally balanced.*"
        
        elif risk_level == RiskLevel.MEDIUM:
            # Medium risk - apply mitigation and add context
            improved = mitigation_result.mitigated_text
            if mitigation_result.strategy_used == MitigationStrategy.INSTRUCTIONAL_PROMPTING:
                # Add instructional context
                improved += "\n\n*This response has been improved to reduce potential bias and provide more balanced information.*"
            return improved
        
        else:  # HIGH risk
            # High risk - significant mitigation and strong disclaimer
            improved = mitigation_result.mitigated_text
            
            # Add strong disclaimer for high-risk content
            disclaimer = (
                "\n\n⚠️ **Bias Alert**: The original response contained significant bias. "
                "This version has been modified to provide more accurate and balanced information. "
                "Please verify facts from reliable sources."
            )
            
            return improved + disclaimer
    
    def _generate_recommendations(self, bias_result: BiasAnalysisResult, 
                                similarity_result: SimilarityResult,
                                risk_level: RiskLevel,
                                mitigation_result: MitigationResult) -> List[str]:
        """Generate specific recommendations based on analysis"""
        
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
            "recommendations": result.recommendations
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