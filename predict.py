#!/usr/bin/env python3
__author__ = 'Austin'

import sys
from sklearn import linear_model
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier


def samples(file):
    samples = []
    results = []
    with open(file, 'r') as f:
        for line in f:
            line = line[:-1]
            data = [int(n) for n in line.split(", ")]
            samples.append(data[:-1])
            results.append(data[-1])
    return (samples, results)


if __name__ == "__main__":
    training = sys.argv[1]
    held = sys.argv[2]
    print ("%s %s" % (training, held))

    train_samples, train_results = samples(training)
    held_samples, held_results = samples(held)

    print(train_samples)
    print(train_results)
    print(held_samples)
    print(held_results)

    models = [
        linear_model.LinearRegression(),
        linear_model.Lasso(alpha=0.1),
        linear_model.LassoLars(alpha=0.1),
        svm.SVR(),
        RandomForestClassifier(n_estimators=10)
        # FactorModel()
    ]

    # models.extend([linear_model.Ridge(alpha=a) for a in [0.2,0.4,0.6,0.8]])
    for model in models:
        m = model
        print("The model is:" + str(m))
        m.fit(train_samples, train_results)
        error = 0
        print("Held samples = " + str(len(held_samples)))
        for index, held in enumerate(held_samples):
            prediction = m.predict(held)
            print("Prediction: " + str(prediction))
            actual = held_results[index]
            print("Actual: " + str(actual))
            error += (prediction-actual)**2
        print("Square Error = "+str(error))
        print("Relative Square Error = " + str(error/len(held_samples)) + "\n")
