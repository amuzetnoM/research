"""
Emotional Dimensionality Framework (EDF) for Advanced Sentiment Analysis.

This module implements the Emotional Dimensionality Framework described in
the research paper "Sentiment Analysis in Machine Learning: Beyond Surface Interpretation".
"""

import logging
import numpy as np
import json
import os
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum

logger = logging.getLogger('ai.emotional_dimensionality')

class EmotionalDimension(Enum):
    """Core emotional dimensions used in the EDF framework."""
    VALENCE = "valence"           # Positive-negative spectrum
    AROUSAL = "arousal"           # Intensity or energy level
    DOMINANCE = "dominance"       # Degree of control or power
    SOCIAL = "social"             # Connection or distance from others
    TEMPORAL = "temporal"         # Relation to past, present, or future
    CERTAINTY = "certainty"       # Confidence or uncertainty
    INTENTIONALITY = "intentionality"  # Direction toward specific target


class ContextualDimension(Enum):
    """Contextual dimensions that modify emotional interpretation."""
    CULTURAL = "cultural"         # Cultural norms and references
    RELATIONAL = "relational"     # Relationship between parties
    HISTORICAL = "historical"     # Prior interactions and knowledge
    MEDIUM = "medium"             # Communication channel influences
    PRAGMATIC = "pragmatic"       # Purpose behind communication


class EmotionalState:
    """Representation of an emotional state in the dimensional model."""
    
    def __init__(self):
        """Initialize a neutral emotional state with default values."""
        # Initialize core dimensions with neutral values
        self.dimensions = {dim.value: 0.0 for dim in EmotionalDimension}
        
        # Initialize contextual modifiers
        self.contextual = {dim.value: 0.0 for dim in ContextualDimension}
        
        # Confidence in this emotional assessment
        self.confidence = 0.0
        
        # Source of the emotional assessment
        self.source = None
    
    def set_dimension(self, dimension: Union[EmotionalDimension, str], value: float):
        """Set the value for a core emotional dimension.
        
        Args:
            dimension: The dimension to set
            value: Value between -1.0 and 1.0 (typically)
        """
        if isinstance(dimension, EmotionalDimension):
            dimension = dimension.value
            
        if dimension in self.dimensions:
            self.dimensions[dimension] = value
    
    def set_contextual(self, dimension: Union[ContextualDimension, str], value: float):
        """Set the value for a contextual dimension.
        
        Args:
            dimension: The contextual dimension to set
            value: Value between 0.0 and 1.0 (typically)
        """
        if isinstance(dimension, ContextualDimension):
            dimension = dimension.value
            
        if dimension in self.contextual:
            self.contextual[dimension] = value
    
    def to_vector(self) -> np.ndarray:
        """Convert the emotional state to a numeric vector.
        
        Returns:
            Numpy array of dimension values
        """
        # Combine core and contextual dimensions
        return np.array(list(self.dimensions.values()) + list(self.contextual.values()))
    
    @classmethod
    def from_vector(cls, vector: np.ndarray):
        """Create an emotional state from a numeric vector.
        
        Args:
            vector: Numeric vector representation
            
        Returns:
            EmotionalState object
        """
        state = cls()
        
        # Get the number of core dimensions
        core_dims = len(EmotionalDimension)
        
        # Set core dimensions
        for i, dim in enumerate(EmotionalDimension):
            if i < len(vector):
                state.dimensions[dim.value] = float(vector[i])
        
        # Set contextual dimensions
        for i, dim in enumerate(ContextualDimension):
            idx = i + core_dims
            if idx < len(vector):
                state.contextual[dim.value] = float(vector[idx])
        
        return state
    
    def emotional_distance(self, other: 'EmotionalState') -> float:
        """Calculate emotional distance between two states.
        
        Args:
            other: Another emotional state
            
        Returns:
            Euclidean distance between the states
        """
        v1 = self.to_vector()
        v2 = other.to_vector()
        
        # Handle vectors of different length
        min_len = min(len(v1), len(v2))
        return np.linalg.norm(v1[:min_len] - v2[:min_len])
    
    def serialize(self) -> Dict:
        """Serialize to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'dimensions': self.dimensions,
            'contextual': self.contextual,
            'confidence': self.confidence,
            'source': self.source
        }
    
    @classmethod
    def deserialize(cls, data: Dict) -> 'EmotionalState':
        """Create from serialized dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            EmotionalState object
        """
        state = cls()
        
        if 'dimensions' in data:
            for dim, value in data['dimensions'].items():
                if dim in state.dimensions:
                    state.dimensions[dim] = value
        
        if 'contextual' in data:
            for dim, value in data['contextual'].items():
                if dim in state.contextual:
                    state.contextual[dim] = value
        
        if 'confidence' in data:
            state.confidence = data['confidence']
            
        if 'source' in data:
            state.source = data['source']
            
        return state


class EmotionalDimensionalityModel:
    """Base class for emotional dimensionality analysis models."""
    
    def __init__(self):
        """Initialize the model."""
        self.model_name = "BaseEDFModel"
        self.dimensions = [dim.value for dim in EmotionalDimension]
        self.contextual_dimensions = [dim.value for dim in ContextualDimension]
    
    def analyze(self, text: str, context: Dict = None) -> EmotionalState:
        """Analyze text to produce an emotional state representation.
        
        Args:
            text: The text to analyze
            context: Optional contextual information
            
        Returns:
            EmotionalState representing the analysis
        """
        # Base implementation returns neutral state
        # Subclasses should override this method
        state = EmotionalState()
        state.confidence = 0.5
        state.source = self.model_name
        return state
    
    def batch_analyze(self, texts: List[str], 
                     contexts: List[Dict] = None) -> List[EmotionalState]:
        """Analyze multiple texts in batch.
        
        Args:
            texts: List of texts to analyze
            contexts: Optional list of context dictionaries
            
        Returns:
            List of EmotionalState objects
        """
        results = []
        
        # Default implementation calls analyze for each text
        for i, text in enumerate(texts):
            context = None
            if contexts and i < len(contexts):
                context = contexts[i]
                
            results.append(self.analyze(text, context))
            
        return results


class RuleBasedEDFModel(EmotionalDimensionalityModel):
    """Rule-based implementation of the EDF model for simple cases."""
    
    def __init__(self, lexicon_path: Optional[str] = None):
        """Initialize the rule-based model.
        
        Args:
            lexicon_path: Path to emotion lexicon file (optional)
        """
        super().__init__()
        self.model_name = "RuleBasedEDF"
        
        # Load lexicon if provided
        self.lexicon = {}
        if lexicon_path and os.path.exists(lexicon_path):
            self._load_lexicon(lexicon_path)
        else:
            # Create a small default lexicon
            self._create_default_lexicon()
    
    def _load_lexicon(self, lexicon_path: str):
        """Load emotion lexicon from file.
        
        Args:
            lexicon_path: Path to lexicon file
        """
        try:
            with open(lexicon_path, 'r', encoding='utf-8') as f:
                self.lexicon = json.load(f)
                logger.info(f"Loaded lexicon with {len(self.lexicon)} entries")
        except Exception as e:
            logger.error(f"Error loading lexicon: {e}")
            self._create_default_lexicon()
    
    def _create_default_lexicon(self):
        """Create a small default lexicon for demonstration."""
        # This is a minimal lexicon - in practice, you would use a comprehensive one
        self.lexicon = {
            "happy": {
                "valence": 0.8,
                "arousal": 0.5,
                "dominance": 0.4
            },
            "sad": {
                "valence": -0.7,
                "arousal": -0.3,
                "dominance": -0.4
            },
            "angry": {
                "valence": -0.6,
                "arousal": 0.8,
                "dominance": 0.6
            },
            "afraid": {
                "valence": -0.7,
                "arousal": 0.6,
                "dominance": -0.7
            },
            "excited": {
                "valence": 0.7,
                "arousal": 0.9,
                "dominance": 0.5
            },
            "calm": {
                "valence": 0.4,
                "arousal": -0.7,
                "dominance": 0.1
            }
        }
        logger.info("Created default lexicon")
    
    def analyze(self, text: str, context: Dict = None) -> EmotionalState:
        """Analyze text using rule-based approach.
        
        Args:
            text: Text to analyze
            context: Optional contextual information
            
        Returns:
            EmotionalState representing the analysis
        """
        state = EmotionalState()
        words = text.lower().split()
        
        # Count matches from lexicon
        matches = 0
        for word in words:
            if word in self.lexicon:
                matches += 1
                for dim, value in self.lexicon[word].items():
                    if dim in state.dimensions:
                        # Accumulate values
                        current = state.dimensions[dim]
                        state.dimensions[dim] = current + value
        
        # Average the values if we had matches
        if matches > 0:
            for dim in state.dimensions:
                state.dimensions[dim] /= matches
        
        # Process contextual dimensions if provided
        if context:
            self._analyze_context(state, context)
        
        # Set confidence based on number of matches
        state.confidence = min(0.9, matches / max(1, len(words) / 2))
        state.source = self.model_name
        
        return state
    
    def _analyze_context(self, state: EmotionalState, context: Dict):
        """Analyze and apply contextual dimensions.
        
        Args:
            state: EmotionalState to update
            context: Contextual information
        """
        # Extract cultural context if available
        if 'culture' in context:
            state.set_contextual(ContextualDimension.CULTURAL, 0.8)
            
            # Cultural adjustments could be applied here
            # For example, different cultures may interpret certain
            # emotional expressions differently
        
        # Extract relational context
        if 'relationship' in context:
            state.set_contextual(ContextualDimension.RELATIONAL, 0.7)
        
        # Historical context
        if 'history' in context:
            state.set_contextual(ContextualDimension.HISTORICAL, 0.6)
        
        # Medium context
        if 'medium' in context:
            state.set_contextual(ContextualDimension.MEDIUM, 0.5)
            
            # Adjust for medium (e.g., email vs chat)
            medium = context['medium'].lower()
            if medium == 'email':
                # Formal medium might dampen emotional expression
                for dim in state.dimensions:
                    state.dimensions[dim] *= 0.8
            elif medium == 'chat':
                # Chat might amplify emotional expression
                for dim in state.dimensions:
                    state.dimensions[dim] *= 1.2
        
        # Pragmatic intent
        if 'intent' in context:
            state.set_contextual(ContextualDimension.PRAGMATIC, 0.9)
            
            # Adjust based on intent
            intent = context['intent'].lower()
            if intent == 'persuade':
                state.dimensions['intentionality'] = 0.8


class NeuralEDFModel(EmotionalDimensionalityModel):
    """Neural network implementation of the EDF model."""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the neural EDF model.
        
        Args:
            model_path: Path to saved model (optional)
        """
        super().__init__()
        self.model_name = "NeuralEDF"
        self.model = None
        self.tokenizer = None
        self.model_loaded = False
        
        # Try to load model if path provided
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str) -> bool:
        """Load a pre-trained model.
        
        Args:
            model_path: Path to the model
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This is a placeholder for actual model loading code
            # In a real implementation, you would load your PyTorch,
            # TensorFlow, or other model format here
            
            # Simulate model loading for demonstration
            if os.path.exists(model_path):
                logger.info(f"Loading neural EDF model from {model_path}")
                # self.model = torch.load(model_path)
                # self.tokenizer = AutoTokenizer.from_pretrained(...)
                self.model_loaded = True
                return True
            else:
                logger.warning(f"Model path not found: {model_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def analyze(self, text: str, context: Dict = None) -> EmotionalState:
        """Analyze text using neural model.
        
        Args:
            text: Text to analyze
            context: Optional contextual information
            
        Returns:
            EmotionalState representing the analysis
        """
        state = EmotionalState()
        
        if not self.model_loaded:
            # Return low-confidence state if model not loaded
            logger.warning("Neural model not loaded, returning placeholder analysis")
            state.confidence = 0.1
            state.source = f"{self.model_name} (not loaded)"
            return state
        
        try:
            # This is a placeholder for actual neural model inference
            # In a real implementation, you would:
            # 1. Tokenize the input text
            # 2. Run it through your model
            # 3. Post-process the outputs
            
            # tokens = self.tokenizer(text, return_tensors="pt")
            # outputs = self.model(**tokens)
            # dimension_scores = outputs.logits.detach().numpy()
            
            # Simulate model output for demonstration
            # Generate pseudo-random output based on text characteristics
            import hashlib
            text_hash = int(hashlib.md5(text.encode()).hexdigest(), 16)
            np.random.seed(text_hash % 2**32)
            
            # Generate dimension values
            dimension_scores = np.random.uniform(-1, 1, len(self.dimensions))
            contextual_scores = np.random.uniform(0, 1, len(self.contextual_dimensions))
            
            # Set the dimensions
            for i, dim in enumerate(self.dimensions):
                state.dimensions[dim] = float(dimension_scores[i])
            
            # Set contextual dimensions if context provided
            if context:
                for i, dim in enumerate(self.contextual_dimensions):
                    state.contextual[dim] = float(contextual_scores[i])
                
                # Adjust based on specific context elements
                if 'culture' in context:
                    cultural_factor = 0.2
                    state.dimensions['valence'] *= (1 + cultural_factor)
            
            # Set reasonable confidence and source
            state.confidence = 0.75
            state.source = self.model_name
            
        except Exception as e:
            logger.error(f"Error during neural analysis: {e}")
            state.confidence = 0.1
            state.source = f"{self.model_name} (error)"
        
        return state
    
    def batch_analyze(self, texts: List[str], 
                     contexts: List[Dict] = None) -> List[EmotionalState]:
        """Analyze multiple texts in batch for efficiency.
        
        Args:
            texts: List of texts to analyze
            contexts: Optional list of context dictionaries
            
        Returns:
            List of EmotionalState objects
        """
        results = []
        
        if not self.model_loaded:
            # Fall back to individual analysis if model not loaded
            return super().batch_analyze(texts, contexts)
        
        try:
            # This is a placeholder for actual batch inference
            # In a real implementation, you would batch process all texts
            
            # Simulate batch processing
            for i, text in enumerate(texts):
                context = None
                if contexts and i < len(contexts):
                    context = contexts[i]
                
                results.append(self.analyze(text, context))
            
        except Exception as e:
            logger.error(f"Error during batch analysis: {e}")
            # Return empty results with low confidence
            for _ in texts:
                state = EmotionalState()
                state.confidence = 0.1
                state.source = f"{self.model_name} (batch error)"
                results.append(state)
        
        return results


class EmotionalDimensionalityFramework:
    """Main framework class for Emotional Dimensionality analysis."""
    
    def __init__(self, config: Dict = None):
        """Initialize the EDF framework.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.models = {}
        self.default_model = None
        
        # Initialize with a rule-based model by default
        self.add_model("rule_based", RuleBasedEDFModel())
        self.set_default_model("rule_based")
        
        logger.info("Emotional Dimensionality Framework initialized")
    
    def add_model(self, model_id: str, model: EmotionalDimensionalityModel):
        """Add a model to the framework.
        
        Args:
            model_id: Unique identifier for the model
            model: The model instance
        """
        self.models[model_id] = model
        logger.info(f"Added model '{model_id}' ({model.model_name})")
    
    def set_default_model(self, model_id: str):
        """Set the default model for analysis.
        
        Args:
            model_id: The model identifier
            
        Returns:
            True if successful, False if model not found
        """
        if model_id in self.models:
            self.default_model = model_id
            logger.info(f"Set default model to '{model_id}'")
            return True
        else:
            logger.error(f"Model '{model_id}' not found")
            return False
    
    def analyze(self, text: str, context: Dict = None, 
               model_id: str = None) -> EmotionalState:
        """Analyze text to produce an emotional state.
        
        Args:
            text: Text to analyze
            context: Optional contextual information
            model_id: Specific model to use (uses default if None)
            
        Returns:
            EmotionalState representing the analysis
        """
        # Determine which model to use
        if model_id is None:
            model_id = self.default_model
        
        if model_id not in self.models:
            logger.warning(f"Model '{model_id}' not found, using default")
            model_id = self.default_model
        
        # Run the analysis
        return self.models[model_id].analyze(text, context)
    
    def compare_models(self, text: str, context: Dict = None) -> Dict[str, EmotionalState]:
        """Compare analysis from all available models.
        
        Args:
            text: Text to analyze
            context: Optional contextual information
            
        Returns:
            Dictionary mapping model IDs to EmotionalState objects
        """
        results = {}
        
        for model_id, model in self.models.items():
            results[model_id] = model.analyze(text, context)
        
        return results
    
    def calculate_emotional_distance(self, state1: EmotionalState, 
                                    state2: EmotionalState) -> float:
        """Calculate distance between two emotional states.
        
        Args:
            state1: First emotional state
            state2: Second emotional state
            
        Returns:
            Distance metric between the states
        """
        return state1.emotional_distance(state2)
    
    def dominant_emotion(self, state: EmotionalState) -> Tuple[str, float]:
        """Determine the dominant emotion represented by a state.
        
        Args:
            state: The emotional state
            
        Returns:
            Tuple of (emotion_label, confidence)
        """
        # This is a simplified mapping from dimensional space to categorical emotions
        # A real implementation would have a more sophisticated mapping
        
        valence = state.dimensions['valence']
        arousal = state.dimensions['arousal']
        dominance = state.dimensions['dominance']
        
        # Simple quadrant-based categorization
        if valence > 0:
            if arousal > 0:
                if dominance > 0:
                    return ("joy", 0.7)
                else:
                    return ("excitement", 0.7)
            else:
                if dominance > 0:
                    return ("contentment", 0.7)
                else:
                    return ("relief", 0.6)
        else:
            if arousal > 0:
                if dominance > 0:
                    return ("anger", 0.8)
                else:
                    return ("fear", 0.8)
            else:
                if dominance > 0:
                    return ("disappointment", 0.6)
                else:
                    return ("sadness", 0.7)
    
    def serialize(self) -> Dict:
        """Serialize the framework configuration.
        
        Returns:
            Dictionary representation
        """
        return {
            'default_model': self.default_model,
            'available_models': list(self.models.keys()),
            'config': self.config
        }
    
    def save_configuration(self, filepath: str):
        """Save the framework configuration to a file.
        
        Args:
            filepath: Path to save the file
        """
        config = self.serialize()
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Configuration saved to {filepath}")
    
    @classmethod
    def load_from_configuration(cls, filepath: str) -> 'EmotionalDimensionalityFramework':
        """Create a framework instance from saved configuration.
        
        Args:
            filepath: Path to configuration file
            
        Returns:
            EmotionalDimensionalityFramework instance
        """
        if not os.path.exists(filepath):
            logger.error(f"Configuration file not found: {filepath}")
            return cls()
        
        try:
            with open(filepath, 'r') as f:
                config = json.load(f)
            
            framework = cls(config.get('config', {}))
            
            # Add rule-based model by default
            framework.add_model("rule_based", RuleBasedEDFModel())
            
            # Try to set default model from config
            default_model = config.get('default_model')
            if default_model and default_model in framework.models:
                framework.set_default_model(default_model)
            
            logger.info(f"Framework loaded from {filepath}")
            return framework
            
        except Exception as e:
            logger.error(f"Error loading framework configuration: {e}")
            return cls()  # Return default instance
