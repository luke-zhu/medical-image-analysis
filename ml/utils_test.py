import keras
import numpy as np
import os
import pytest
import sklearn.preprocessing

import models.luke
import utils


def test_upload_to_slack():
    with open('test_upload_to_slack.png', 'w') as f:
        f.write('hello!')
    r = utils.upload_to_slack('test_upload_to_slack.png', 'just testing you')
    assert r.status_code == 200


# TODO
@pytest.mark.skip
def test_sensitivity():
    raise NotImplementedError()


@pytest.mark.skip
def test_specificity():
    raise NotImplementedError()


def test_full_multiclass_report_binary():
    model = models.luke.inception(num_classes=1)

    X = np.random.rand(500, 224, 224, 3)
    y = np.random.randint(0, 2, size=(500,))

    utils.full_multiclass_report(model,
                                 X,
                                 y,
                                 classes=[0, 1],
                                 binary=True)


def test_full_multiclass_report_multiclass():
    model = models.luke.inception(num_classes=3)

    X = np.random.rand(500, 224, 224, 3)
    y = np.random.randint(0, 3, size=(500,))
    y = sklearn.preprocessing.label_binarize(y, classes=[0, 1, 2])

    assert y.shape == (500, 3)

    utils.full_multiclass_report(model,
                                 X,
                                 y,
                                 classes=[0, 1, 2],
                                 binary=False)


def test_save_misclassification_plot():
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    model = keras.Sequential([
        keras.layers.Flatten(input_shape=(224, 224, 3)),
        keras.layers.Dense(3, activation='softmax'),
    ])
    X = np.random.rand(10, 224, 224, 3)
    y = np.random.randint(0, 3, size=(10,))
    y = sklearn.preprocessing.label_binarize(y, [0, 1, 2])
    y_pred = model.predict(X)
    print(y, y_pred)
    y_valid = y.argmax(axis=1)
    y_pred = y_pred.argmax(axis=1)
    print('starting save')
    utils.save_misclassification_plot(X,
                                      y_valid,
                                      y_pred)
    utils.upload_to_slack('/tmp/misclassify.png',
                          'testaloha')
