from flask import Flask, render_template, request, redirect, url_for
from torch import cuda
import transformers
import pandas as pd
import matplotlib as plt
import seaborn as sb
import matplotlib.pyplot as ppl
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfTransformer
import re
import numpy as np
import os
import random
import cv2
import sklearn
import torch
import string
from PIL import Image
from pathlib import Path
from fastai.vision.all import *
from fastai.callback import *
from fastai.metrics import error_rate
from fastai.callback.tracker import EarlyStoppingCallback
from fastai.vision.all import get_image_files
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
import warnings
from flask import json
from flask import jsonify
import joblib
import base64
warnings.filterwarnings ('ignore')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/uploads'
tfidf_vectorizer = TfidfVectorizer()

#calling models
model=load_model(r"C:\Users\virin\OneDrive\Desktop\Synapse 2.0-Datadynamos\NeuralNet (2).pkl")
learn = load_learner(r"C:\Users\virin\OneDrive\Desktop\Synapse 2.0-Datadynamos\Images\model.pk1")

#Multiclass classification
def clean_text(text):
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return cleaned_text

json_file = 'SubtaskB\subtaskB_train.jsonl'
tdf = pd.read_json(json_file, lines=True)

json_file2 = 'SubtaskB\subtaskB_dev.jsonl'
ddf = pd.read_json(json_file, lines=True)

X_train = tdf['text'].values
y_train = tdf['label'].values

X_train_tfidf=tfidf_vectorizer.fit_transform(X_train)

# classifier = MultinomialNB()
# classifier.fit(X_train_tfidf, y_train)
classifier=model

label_mapping = {
    1:"chatGPT",
    0:"human",
    2:"cohere",
    3:"davinci",
    4:"bloomz",
    5:"dolly",
    # Add more labels as needed
}

#Image classification
def classify_image(img):
    img = img.resize((224, 224))
    img = PILImage.create(np.array(img))  
    pred, _, _ = learn.predict(img)
    if pred=="AiArtData":
        res="Image is AI generated"
    else:
        res="Image is not AI generated"
    return res


@app.route("/", methods=["POST","GET"])
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST","GET"])
def upload_and_classify():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        try:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img = Image.open(file)
            prediction = classify_image(img)
            img_resized = img.resize((224, 224))  # Resize for display
            return render_template('index.html', filename=filename, prediction= prediction)
        except Exception as e:
            return jsonify({'error': str(e)})
    return render_template('index.html')

@app.route("/chat", methods=["POST", "GET"])
def chat():
    user_input = request.form.get("user_input")
    user_input_vectorized = tfidf_vectorizer.transform([user_input])
    prediction = classifier.predict(user_input_vectorized)
    response = f"text is generated by {label_mapping[prediction[0]]}"
    return render_template("index.html", user_input=user_input, response=response)

if __name__ == "__main__":
    app.run(debug=True)
