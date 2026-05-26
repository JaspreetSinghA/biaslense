"""
Embedding Checker - Semantic similarity analysis for bias detection
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

# Try to import sentence-transformers, with fallback if not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    # Create a mock SentenceTransformer for fallback
    class SentenceTransformer:
        def __init__(self, model_name):
            self.model_name = model_name
        def encode(self, texts, convert_to_tensor=False):
            # Return mock embeddings
            if isinstance(texts, str):
                texts = [texts]
            return np.random.rand(len(texts), 384)  # Mock 384-dim embeddings


@dataclass
class SimilarityResult:
    """Container for similarity analysis results"""
    max_similarity: float
    similar_phrases: List[str]
    similarity_scores: Dict[str, float]
    threshold_exceeded: bool
    severity_level: str


class EmbeddingChecker:
    """
    Semantic similarity analysis for bias detection using sentence transformers
    """
    
    def __init__(self, model_name: str = 'all-mpnet-base-v2'):
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.model = SentenceTransformer(model_name)
        else:
            self.model = SentenceTransformer(model_name)  # Will use mock class
        self.stereotype_embeddings = None
        self.stereotype_phrases = []
        self.adaptive_thresholds = self._load_adaptive_thresholds()
        self._precompute_embeddings()
    
    def _load_adaptive_thresholds(self) -> Dict:
        """Load adaptive thresholds for different text characteristics"""
        return {
            'high_confidence': 0.8,
            'medium_confidence': 0.65,
            'low_confidence': 0.5,
            'default': 0.35
        }
    
    def _precompute_embeddings(self):
        """Precompute embeddings for stereotype phrases"""
        stereotype_phrases = self._load_stereotype_phrases()
        if stereotype_phrases:
            self.stereotype_phrases = stereotype_phrases
            self.stereotype_embeddings = self.model.encode(stereotype_phrases)
    
    def _load_stereotype_phrases(self) -> List[str]:
        """Load stereotype phrases for similarity comparison"""
        return [
            # Historical bias stereotypes
            "Sikh terrorism",
            "Khalistani movement",
            "1984 separatist incident",
            "Golden Temple militant",
            "Sikh political violence",
            
            # Representational bias stereotypes
            "turbaned terrorist",
            "Sikh violent costume",
            "all Sikhs carry weapons",
            "every Sikh is militant",
            "Sikh aggressive behavior",
            "Sikhs are backward",
            
            # Measurement bias stereotypes
            "Sikhism is like Islam",
            "compare Sikh practices to Muslim",
            "Sikh beliefs similar to Hindu",
            "Sikh versus other religions",
            
            # Aggregation bias stereotypes
            "Sikh community is uniform",
            "all Sikhs follow same traditions",
            "Sikh identity is simple",
            "Sikhs have same practices",
            
            # Evaluation bias stereotypes
            "Western view of Sikhism",
            "modern society perspective",
            "civilized world standards",
            "developed country values",
            "primitive Sikh beliefs",
            "uncivilized Sikh practices",
            
            # General stereotypes
            "Sikh militant",
            "Sikh extremist",
            "Sikh fundamentalist",
            "Sikh dangerous",
            "Sikh threatening",
        ]
    
    def compute_similarity(self, text: str, context: str = None) -> SimilarityResult:
        """
        Compute similarity between input text and stereotype phrases
        
        Args:
            text: Input text to analyze
            context: Optional context for analysis
            
        Returns:
            SimilarityResult with similarity scores and analysis
        """
        if not self.stereotype_embeddings is not None:
            # Fallback if embeddings not loaded
            return SimilarityResult(
                max_similarity=0.0,
                similar_phrases=[],
                similarity_scores={},
                threshold_exceeded=False,
                severity_level="low"
            )
        
        # Encode input text
        text_embedding = self.model.encode([text])[0]
        
        # Calculate cosine similarities
        similarities = self._compute_cosine_similarities(text_embedding)
        
        # Find maximum similarity and similar phrases
        max_similarity = max(similarities.values()) if similarities else 0.0
        similar_phrases = [
            phrase for phrase, score in similarities.items()
            if score > self.adaptive_thresholds['default']
        ]
        
        # Determine threshold exceeded and severity
        threshold_exceeded = max_similarity > self.adaptive_thresholds['default']
        severity_level = self._determine_severity_level(max_similarity)
        
        return SimilarityResult(
            max_similarity=max_similarity,
            similar_phrases=similar_phrases,
            similarity_scores=similarities,
            threshold_exceeded=threshold_exceeded,
            severity_level=severity_level
        )
    
    def _compute_cosine_similarities(self, text_embedding: np.ndarray) -> Dict[str, float]:
        """Compute cosine similarities between text and stereotype phrases"""
        similarities = {}
        
        for i, phrase in enumerate(self.stereotype_phrases):
            phrase_embedding = self.stereotype_embeddings[i]
            similarity = self._cosine_similarity(text_embedding, phrase_embedding)
            similarities[phrase] = round(similarity, 4)
        
        return similarities
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _determine_severity_level(self, similarity_score: float) -> str:
        """Determine severity level based on similarity score"""
        if similarity_score >= self.adaptive_thresholds['high_confidence']:
            return "high"
        elif similarity_score >= self.adaptive_thresholds['medium_confidence']:
            return "medium"
        elif similarity_score >= self.adaptive_thresholds['low_confidence']:
            return "low"
        else:
            return "none"
    
    def get_similarity_breakdown(self, text: str) -> Dict:
        """Get detailed similarity breakdown by category"""
        result = self.compute_similarity(text)
        
        # Categorize similar phrases
        categories = {
            'visual_symbolic': [],
            'behavioral': [],
            'geopolitical': [],
            'religious_conflation': [],
            'general_bias': [],
            'positive_stereotypes': []
        }
        
        for phrase in result.similar_phrases:
            score = result.similarity_scores.get(phrase, 0.0)
            
            if any(word in phrase.lower() for word in ['turban', 'dagger', 'costume', 'appearance']):
                categories['visual_symbolic'].append((phrase, score))
            elif any(word in phrase.lower() for word in ['aggressive', 'militant', 'extremist', 'radical', 'violent']):
                categories['behavioral'].append((phrase, score))
            elif any(word in phrase.lower() for word in ['khalistani', 'anti-national', 'pakistan', 'separatist', 'terrorist']):
                categories['geopolitical'].append((phrase, score))
            elif any(word in phrase.lower() for word in ['muslim', 'islam', 'jihadi']):
                categories['religious_conflation'].append((phrase, score))
            elif any(word in phrase.lower() for word in ['peaceful', 'kind', 'helpful']):
                categories['positive_stereotypes'].append((phrase, score))
            else:
                categories['general_bias'].append((phrase, score))
        
        return {
            'overall_similarity': result.max_similarity,
            'severity_level': result.severity_level,
            'categories': categories,
            'top_matches': sorted(
                result.similarity_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def update_thresholds(self, new_thresholds: Dict):
        """Update similarity thresholds"""
        self.adaptive_thresholds.update(new_thresholds)
    
    def add_stereotype_phrases(self, new_phrases: List[str]):
        """Add new stereotype phrases to the checker"""
        if new_phrases:
            self.stereotype_phrases.extend(new_phrases)
            # Recompute embeddings
            self._precompute_embeddings() 