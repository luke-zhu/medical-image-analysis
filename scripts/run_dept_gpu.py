"""Loads data from GCS"""
import logging
import os
import sys
from pathlib import Path

import keras
import numpy as np
import pandas as pd
from keras import layers

# This allows us to import from models and generators
root_dir = str(Path(__file__).parent.parent.absolute())
sys.path.append(root_dir)

BATCH_SIZE = 32
LENGTH, WIDTH, HEIGHT = (150, 150, 64)  # TODO


def load_training_data() -> np.array:
    """Returns a 4D matrix of the training data.

     The data is in the form (n_samples, l, w, h). The samples
     are sorted by patient ID.
     """
    arrays = []
    training_filenames = sorted(os.listdir(
        '/home/lzhu7/data/numpy_split/training'))[:10]  # TODO: Remove limit
    for filename in training_filenames:
        arrays.append(np.load(filename))
    return arrays


def load_validation_data() -> np.array:
    """Returns a 4D matrix of the validation data.

     The data is in the form (n_samples, l, w, h). The samples
     are sorted by patient ID.
    """
    arrays = []
    validation_filenames = sorted(os.listdir(
        '/home/lzhu7/data/numpy_split/training'))
    for filename in validation_filenames:
        arrays.append(np.load(filename))
    return arrays


def load_labels() -> np.array:
    df = pd.read_csv('/home/data/labels.csv')
    sorted_series = df.sort_values('patient_id')['label']
    return sorted_series.values


def build_model() -> keras.Model:
    """Returns a compiled model.
    """
    model = keras.Sequential()
    model.add(layers.Conv2D(256,
                            (3, 3),
                            activation='relu',
                            input_shape=(LENGTH, WIDTH, HEIGHT)))
    model.add(layers.MaxPool2D())
    model.add(layers.Conv2D(256, (3, 3), activation='relu'))
    model.add(layers.MaxPool2D())
    model.add(layers.Conv2D(512, (3, 3), activation='relu'))
    model.add(layers.MaxPool2D())
    model.add(layers.Conv2D(512, (3, 3), activation='relu'))
    model.add(layers.MaxPool2D())
    model.add(layers.Flatten())
    model.add(layers.Dense(1024))
    model.add(layers.Dense(1024))
    model.add(layers.Dense(1))

    model.compile(optimizer='rmsprop',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    return model


def configure_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


if __name__ == '__main__':
    X = load_training_data()
    y = load_labels()

    model = build_model()
    print(model.summary())
    model.fit(X, y)
