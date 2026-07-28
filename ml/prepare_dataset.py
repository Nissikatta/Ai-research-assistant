import json
import os

DATASET = [
    # Artificial Intelligence
    {"text": "Artificial intelligence algorithms enable reasoning, decision making, and autonomous agents in complex stochastic environments using search trees, heuristic evaluation functions, and multi-agent coordination frameworks.", "label": "Artificial Intelligence"},
    {"text": "General artificial intelligence systems model cognitive architectures, knowledge representation, constraint satisfaction, and symbolic reasoning to solve complex real-world decision problems.", "label": "Artificial Intelligence"},
    {"text": "Ethical AI, explainable artificial intelligence, and safety alignment techniques in autonomous systems, expert systems, and heuristic search graph algorithms.", "label": "Artificial Intelligence"},

    # Machine Learning
    {"text": "Supervised machine learning algorithms including gradient boosted decision trees, random forests, and support vector machines for feature extraction and predictive modeling on tabular datasets.", "label": "Machine Learning"},
    {"text": "Unsupervised machine learning methods including k-means clustering, principal component analysis PCA, gaussian mixture models, and dimensionality reduction techniques.", "label": "Machine Learning"},
    {"text": "Reinforcement learning, Q-learning, deep Q-networks, actor-critic policy gradients, loss function convergence, and hyperparameter tuning in machine learning training pipelines.", "label": "Machine Learning"},

    # Computer Vision
    {"text": "Convolutional neural networks CNNs, ResNet architectures, object detection using YOLO and Faster R-CNN, image segmentation, optical flow, and visual feature extraction in video streams.", "label": "Computer Vision"},
    {"text": "Vision transformers ViT, image classification, semantic segmentation, image generation using diffusion models and GANs, and pixel-level bounding box object tracking.", "label": "Computer Vision"},
    {"text": "3D point cloud processing, camera calibration, pose estimation, depth estimation, and visual simultaneous localization and mapping VSLAM for autonomous vehicles.", "label": "Computer Vision"},

    # Natural Language Processing
    {"text": "Transformer language models, self-attention mechanisms, BERT, GPT models, sequence-to-sequence translation, tokenization, text classification, and named entity recognition NER.", "label": "Natural Language Processing"},
    {"text": "Large language models LLMs, retrieval-augmented generation RAG, sentiment analysis, part-of-speech tagging, dependency parsing, text summarization, and vector embeddings.", "label": "Natural Language Processing"},
    {"text": "Word2vec, GloVe, subword tokenization, prompt engineering, fine-tuning language models, semantic similarity search, and computational linguistics.", "label": "Natural Language Processing"},

    # Robotics
    {"text": "Kinematics, dynamics, motion planning, trajectory optimization, inverse kinematics, robot manipulators, ROS robot operating system, and sensor fusion for robotic arms.", "label": "Robotics"},
    {"text": "Mobile robotics navigation, SLAM, lidar point clouds, wheel odometry, obstacle avoidance, quadruped locomotion, and feedback control loops.", "label": "Robotics"},
    {"text": "Human-robot interaction HRI, haptic feedback, robotic surgery precision control, actuators, force sensing, and autonomous swarm robotics coordination.", "label": "Robotics"},

    # Cyber Security
    {"text": "Network security, intrusion detection systems IDS, cryptography, AES encryption, RSA public key infrastructure, zero-trust architecture, and vulnerability assessments.", "label": "Cyber Security"},
    {"text": "Malware detection, reverse engineering, endpoint detection and response EDR, ransomware mitigation, penetration testing, and secure software development lifecycles.", "label": "Cyber Security"},
    {"text": "Phishing detection, threat intelligence, identity access management IAM, firewalls, zero-day exploit analysis, and cryptographic authentication protocols.", "label": "Cyber Security"},

    # Cloud Computing
    {"text": "Microservices architecture, Kubernetes container orchestration, Docker containerization, AWS cloud infrastructure, serverless computing, and auto-scaling clusters.", "label": "Cloud Computing"},
    {"text": "Cloud storage, distributed databases, multi-region failover, load balancing, infrastructure as code Terraform, and cloud-native serverless APIs.", "label": "Cloud Computing"},
    {"text": "DevOps pipelines, CI/CD automated deployment, virtual machines, hypervisors, cloud security policies, and high availability system design.", "label": "Cloud Computing"},
]

def get_training_data():
    return DATASET

if __name__ == "__main__":
    os.makedirs("./data", exist_ok=True)
    with open("./data/sample_dataset.json", "w") as f:
        json.dump(DATASET, f, indent=2)
    print(f"Dataset generated with {len(DATASET)} samples across 7 categories.")
