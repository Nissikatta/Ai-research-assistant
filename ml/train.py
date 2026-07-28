import os
import sys
import json
import numpy as np

# Ensure root directory and ml package are in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tensorflow as tf
from tensorflow.keras import layers, models

try:
    from ml.prepare_dataset import get_training_data
except ImportError:
    from prepare_dataset import get_training_data

def train_and_save_model():
    dataset = get_training_data()
    texts = [item["text"] for item in dataset]
    labels_raw = [item["label"] for item in dataset]

    # Unique sorted label categories
    categories = sorted(list(set(labels_raw)))
    label_to_index = {label: i for i, label in enumerate(categories)}
    index_to_label = {i: label for i, label in enumerate(categories)}
    
    y_train = np.array([label_to_index[lbl] for lbl in labels_raw], dtype=np.int32)

    # Text Vectorization Layer
    max_tokens = 1000
    sequence_length = 100
    vectorize_layer = layers.TextVectorization(
        max_tokens=max_tokens,
        output_mode='int',
        output_sequence_length=sequence_length
    )
    vectorize_layer.adapt(texts)
    
    vocab = vectorize_layer.get_vocabulary()

    # Keras Sequential Model Architecture
    embedding_dim = 64
    num_classes = len(categories)

    model = models.Sequential([
        layers.Input(shape=(sequence_length,), dtype=tf.int32),
        layers.Embedding(input_dim=max_tokens, output_dim=embedding_dim),
        layers.GlobalAveragePooling1D(),
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation='softmax')
    ])

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # Vectorize input texts
    X_train = vectorize_layer(np.array(texts))

    print("Training TensorFlow Document Classifier...")
    model.fit(X_train, y_train, epochs=40, batch_size=4, verbose=1)

    loss, acc = model.evaluate(X_train, y_train, verbose=0)
    print(f"Model Training Evaluation Accuracy: {acc * 100:.2f}%")

    # Persist model artifacts
    save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "saved_models"))
    os.makedirs(save_dir, exist_ok=True)

    model_path = os.path.join(save_dir, "tf_classifier.keras")
    vocab_path = os.path.join(save_dir, "vocab.json")
    labels_path = os.path.join(save_dir, "labels.json")

    model.save(model_path)

    with open(vocab_path, "w") as f:
        json.dump(vocab, f)

    with open(labels_path, "w") as f:
        json.dump(index_to_label, f)

    print(f"Successfully saved trained model to {model_path}")
    print(f"Saved vocabulary to {vocab_path}")
    print(f"Saved label mappings to {labels_path}")

if __name__ == "__main__":
    train_and_save_model()
