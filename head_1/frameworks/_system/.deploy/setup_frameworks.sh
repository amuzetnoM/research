#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Setting up AI Frameworks in $SCRIPT_DIR"

# Create necessary directories
mkdir -p "$SCRIPT_DIR/data/models/self_awareness"
mkdir -p "$SCRIPT_DIR/data/models/edf"
mkdir -p "$SCRIPT_DIR/data/lexicons"
mkdir -p "$SCRIPT_DIR/data/config"

# Install Python dependencies
echo "Installing dependencies..."
pip install --no-cache-dir --upgrade pip
pip install --no-cache-dir numpy matplotlib pandas scikit-learn

# Optional ML dependencies if available
pip install --no-cache-dir torch torchvision || echo "PyTorch install failed, continuing without it"
pip install --no-cache-dir tensorflow || echo "TensorFlow install failed, continuing without it"
pip install --no-cache-dir transformers || echo "Transformers install failed, continuing without it"

# Create a basic emotion lexicon file
echo "Creating sample emotion lexicon..."
cat > "$SCRIPT_DIR/data/lexicons/emotion_lexicon.json" << EOL
{
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
  },
  "surprised": {
    "valence": 0.2,
    "arousal": 0.8,
    "dominance": -0.1
  },
  "disgusted": {
    "valence": -0.8,
    "arousal": 0.4,
    "dominance": 0.1
  },
  "loving": {
    "valence": 0.9,
    "arousal": 0.3,
    "dominance": 0.2
  },
  "worried": {
    "valence": -0.4,
    "arousal": 0.6,
    "dominance": -0.4
  }
}
EOL

# Create default configurations
echo "Creating default configurations..."
cat > "$SCRIPT_DIR/data/config/self_awareness_config.json" << EOL
{
  "monitoring_rate": 1.0,
  "memory_usage_threshold": 90,
  "cpu_usage_threshold": 80,
  "enable_assistance_requests": true,
  "enable_self_modification": false,
  "model_save_path": "/app/data/models/self_awareness",
  "safety_bounds": {
    "max_memory_usage": 95,
    "max_cpu_usage": 95,
    "max_disk_usage": 95
  }
}
EOL

cat > "$SCRIPT_DIR/data/config/emotional_config.json" << EOL
{
  "default_model": "rule_based",
  "lexicon_path": "/app/data/lexicons/emotion_lexicon.json",
  "neural_model_path": "/app/data/models/edf/neural_edf_model.pt",
  "batch_size": 32,
  "enable_contextual_dimensions": true,
  "confidence_threshold": 0.6,
  "results_cache_size": 1000
}
EOL

# Make sure the ai_frameworks directory exists with __init__.py
mkdir -p "$SCRIPT_DIR/system/ai_frameworks"
touch "$SCRIPT_DIR/system/ai_frameworks/__init__.py"

echo "Setup complete. AI Frameworks are ready to use."
echo "To enable the frameworks, set ENABLE_SELF_AWARENESS=true and ENABLE_EMOTIONAL_FRAMEWORK=true in your Docker environment."
