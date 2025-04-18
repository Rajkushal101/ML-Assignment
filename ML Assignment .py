# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vlP3f9E__fPfu_DYJAr0dXlocQ1dZcvP
"""

# Part 1: Importing Libraries
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import pandas as pd
import torch
from skimage.feature import hog, local_binary_pattern, graycomatrix, graycoprops
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0, DenseNet121, MobileNetV2, VGG16, ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.efficientnet import preprocess_input as effnet_preprocess
from tensorflow.keras.applications.densenet import preprocess_input as densenet_preprocess
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input as mobilenet_preprocess
from tensorflow.keras.applications.vgg16 import preprocess_input as vgg_preprocess
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_preprocess
import tensorflow as tf

# Suppress warnings
warnings.filterwarnings("ignore")

# Part 2: Loading and Preprocessing Dataset
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

# Combine train and test to sample 5000 images
X_total = np.concatenate((x_train, x_test), axis=0)
y_total = np.concatenate((y_train, y_test), axis=0)

# Randomly select 5000 samples
indices = np.random.choice(len(X_total), 5000, replace=False)
X_sampled = X_total[indices]
y_sampled = y_total[indices]

# Split into 70% train (3500) and 30% test (1500)
X_train, X_test, y_train, y_test = train_test_split(X_sampled, y_sampled, test_size=0.3, random_state=42, stratify=y_sampled)

# Normalize images
X_train = (X_train * 255).astype("uint8")
X_test = (X_test * 255).astype("uint8")

# Part 3: Feature Extraction Functions
def extract_hog_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return hog(gray, pixels_per_cell=(8, 8), cells_per_block=(2, 2), feature_vector=True)

def extract_lbp_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    lbp = local_binary_pattern(gray, P=24, R=3, method="uniform")
    (hist, _) = np.histogram(lbp.ravel(), bins=np.arange(0, 27), range=(0, 26))
    hist = hist.astype("float") / (hist.sum() + 1e-6)  # Normalize
    return hist

def extract_glcm_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype("uint8")
    glcm = graycomatrix(gray, distances=[1], angles=[0], levels=256, symmetric=True, normed=True)
    contrast = graycoprops(glcm, 'contrast')[0, 0]
    energy = graycoprops(glcm, 'energy')[0, 0]
    homogeneity = graycoprops(glcm, 'homogeneity')[0, 0]
    return [contrast, energy, homogeneity]

def extract_orb_features(image):
    orb = cv2.ORB_create()
    keypoints, descriptors = orb.detectAndCompute(image, None)
    if descriptors is None:
        return np.zeros(32)
    return descriptors.mean(axis=0)

def extract_deep_features(model, dataset, preprocess_func):
    dataset_prep = np.array([preprocess_func(img_to_array(img)) for img in dataset])
    features = model.predict(dataset_prep)
    return features.reshape(features.shape[0], -1)

# Part 4: Defining Models
models = {
    "EfficientNetB0": (EfficientNetB0(weights="imagenet", include_top=False), effnet_preprocess),
    "DenseNet121": (DenseNet121(weights="imagenet", include_top=False), densenet_preprocess),
    "MobileNetV2": (MobileNetV2(weights="imagenet", include_top=False), mobilenet_preprocess),
    "VGG16": (VGG16(weights="imagenet", include_top=False), vgg_preprocess),
    "ResNet50": (ResNet50(weights="imagenet", include_top=False), resnet_preprocess)
}

# Part 5: Training and Evaluating Models with Multiple Classifiers
results = []
feature_extractors = {"HOG": extract_hog_features, "LBP": extract_lbp_features, "GLCM": extract_glcm_features, "ORB": extract_orb_features}

classifiers = {
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
    "LogisticRegression": LogisticRegression(max_iter=1000),
    "KNN": KNeighborsClassifier(n_neighbors=5),
    "SVM": SVC(kernel="linear")
}

for classifier_name, clf in classifiers.items():
    for feature_name, feature_extractor in feature_extractors.items():
        print(f"\nEvaluating {feature_name} Features with {classifier_name}...")
        X_train_feat = np.array([feature_extractor(img) for img in X_train])
        X_test_feat = np.array([feature_extractor(img) for img in X_test])

        scaler = StandardScaler()
        X_train_feat = scaler.fit_transform(X_train_feat)
        X_test_feat = scaler.transform(X_test_feat)

        clf.fit(X_train_feat, y_train.ravel())
        y_pred = clf.predict(X_test_feat)

        acc = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)

        print(report)
        print("Confusion Matrix:")
        print(conf_matrix)
        sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues')
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        plt.title(f"Confusion Matrix for {feature_name} using {classifier_name}")
        plt.show()

        results.append({
            "Feature": feature_name,
            "Classifier": classifier_name,
            "Accuracy": acc
        })

# Displaying Results
df_results = pd.DataFrame(results)
print("\nFinal Results Table (Traditional Features & Classifiers):")
print(df_results)