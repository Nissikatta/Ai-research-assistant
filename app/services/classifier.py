import os
import json
import numpy as np
from app.config import settings

class TFClassifierService:
    def __init__(self):
        self.model = None
        self.vocab = None
        self.index_to_label = None
        self.word_to_index = {}
        self.is_loaded = False
        self._load_model()

    def _load_model(self):
        model_path = settings.TF_MODEL_PATH
        vocab_path = settings.TF_VOCAB_PATH
        labels_path = settings.TF_LABELS_PATH

        if not (os.path.exists(model_path) and os.path.exists(vocab_path) and os.path.exists(labels_path)):
            # If model files do not exist yet, attempt to train them on startup
            try:
                print("TensorFlow model artifacts not found. Initializing training...")
                from ml.train import train_and_save_model
                train_and_save_model()
            except Exception as e:
                print(f"Warning: Could not auto-train TensorFlow model: {e}")
                return

        try:
            import tensorflow as tf
            self.model = tf.keras.models.load_model(model_path)
            
            with open(vocab_path, "r") as f:
                self.vocab = json.load(f)
                self.word_to_index = {w: i for i, w in enumerate(self.vocab)}

            with open(labels_path, "r") as f:
                raw_labels = json.load(f)
                # Convert keys back to integers if saved as string keys in json
                self.index_to_label = {int(k): v for k, v in raw_labels.items()}

            self.is_loaded = True
            print("TensorFlow Document Classifier model loaded successfully.")
        except Exception as e:
            print(f"Failed to load TensorFlow classifier: {e}")
            self.is_loaded = False

    def _vectorize_text(self, text: str, max_length: int = 100) -> np.ndarray:
        import re
        tokens = re.findall(r'\b\w+\b', text.lower())
        vec = np.zeros((1, max_length), dtype=np.int32)
        idx = 0
        for token in tokens:
            if idx >= max_length:
                break
            if token in self.word_to_index:
                vec[0, idx] = self.word_to_index[token]
                idx += 1
        return vec

    def predict(self, text: str):
        if not text or not text.strip():
            return "Unclassified", 0.0

        if not self.is_loaded:
            self._load_model()

        if self.is_loaded and self.model is not None:
            try:
                vec = self._vectorize_text(text)
                preds = self.model.predict(vec, verbose=0)[0]
                best_idx = int(np.argmax(preds))
                category = self.index_to_label.get(best_idx, "Unclassified")
                confidence = float(preds[best_idx])
                
                probs = {self.index_to_label.get(i, f"Cat_{i}"): float(preds[i]) for i in range(len(preds))}
                return category, round(confidence, 4), probs
            except Exception as e:
                print(f"Prediction error: {e}")

        # Rule-based fallback if ML model is unavailable
        text_lower = text.lower()
        if any(k in text_lower for k in ["vision", "cnn", "image", "yolo", "segmentation"]):
            return "Computer Vision", 0.75, {}
        elif any(k in text_lower for k in ["nlp", "language", "bert", "gpt", "rag", "transformer"]):
            return "Natural Language Processing", 0.75, {}
        elif any(k in text_lower for k in ["robot", "kinematics", "ros", "slam", "actuator"]):
            return "Robotics", 0.75, {}
        elif any(k in text_lower for k in ["security", "cipher", "encryption", "intrusion", "malware", "cyber"]):
            return "Cyber Security", 0.75, {}
        elif any(k in text_lower for k in ["cloud", "kubernetes", "docker", "aws", "microservice"]):
            return "Cloud Computing", 0.75, {}
        elif any(k in text_lower for k in ["gradient", "clustering", "supervised", "dataset", "learning"]):
            return "Machine Learning", 0.75, {}
        elif any(k in text_lower for k in ["artificial intelligence", "reasoning", "agent", "heuristic"]):
            return "Artificial Intelligence", 0.75, {}

        return "Unclassified", 0.0, {}

classifier_service = TFClassifierService()
