from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris
import pickle

X, y = load_iris(return_X_y=True)

# Increase the maximum number of iterations
model = LogisticRegression(max_iter=1000) # Increased from default 100
model.fit(X, y)

pickle.dump(model, open("model.pkl", "wb"))
print("Model trained and saved successfully with increased max_iter.")