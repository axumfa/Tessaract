import joblib
model = joblib.load('src/fraud_detection_model.pkl')
print(model)

import numpy as np

samples = np.array([
    [50, 12, 2, 3, 150, 0.15],
    [15000, 3, 0, 20, 100000, 0.92],
    [50000, 1, 6, 40, 200000, 0.95],
    [100, 14, 3, 2, 200, 0.05]
])

probs = model.predict_proba(samples)
print(probs)
