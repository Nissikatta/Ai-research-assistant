import pytest
from app.services.classifier import classifier_service

def test_classifier_prediction():
    text = "Convolutional Neural Networks and YOLO object detection models with deep feature maps."
    category, confidence, probs = classifier_service.predict(text)
    
    assert category is not None
    assert isinstance(confidence, float)
    assert confidence >= 0.0
    print(f"Predicted category: {category}, confidence: {confidence}")

def test_classifier_nlp_text():
    text = "Natural Language Processing with BERT transformer models and sentiment analysis tokenization."
    category, confidence, probs = classifier_service.predict(text)
    
    assert category in ["Natural Language Processing", "Artificial Intelligence", "Machine Learning"]
