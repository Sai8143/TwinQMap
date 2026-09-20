import time
import numpy as np
from sklearn.ensemble import RandomForestRegressor

def test_speed():
    X = np.random.rand(100, 14)
    y = np.random.rand(100, 3)
    
    print("Training 133 Random Forests with n_jobs=None...")
    start = time.time()
    for i in range(133):
        rf = RandomForestRegressor(n_estimators=10, random_state=42)
        rf.fit(X, y)
    end = time.time()
    print(f"Finished training 133 models in {end - start:.4f} seconds.")

if __name__ == "__main__":
    test_speed()
