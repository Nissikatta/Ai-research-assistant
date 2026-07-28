from fastapi import APIRouter, HTTPException
from app.models.pydantic_models import PredictRequest, PredictResponse
from app.services.classifier import classifier_service

router = APIRouter(prefix="/api/classifier", tags=["TensorFlow Classifier"])

@router.post("/predict", response_model=PredictResponse)
def predict_category(payload: PredictRequest):
    """
    Predict document category and confidence score for any given text snippet using the trained TensorFlow model.
    """
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Input text must not be empty.")

    category, confidence, probs = classifier_service.predict(payload.text)
    if isinstance(probs, tuple):
        category, confidence = category, confidence
        probs = {}

    return PredictResponse(
        predicted_category=category,
        confidence=confidence,
        probabilities=probs if probs else {category: confidence}
    )
