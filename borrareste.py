import os
import numpy as np
from sklearn.linear_model import LogisticRegression

mckVector = [9125.0, 710.0, 1.0, 1.0, 0.0, 4.0, 0.87, 0.62, 0.87, 0.37, 0.62, 1]

modelo = [[[0.0002904009651149094, -0.006505294277009539, 0.3091851834686409, 0.2995719009390005, -0.46521308700475145, 1.3595358287453003, 0.3756392250537915, 0.24777743027099203, 0.37205920148901506, 0.11399153790083723, 0.25870784648621664, 0.4141176851687083]], [0.37525678072219765]]

prub = LogisticRegression()
prub.coef_ = np.array(modelo[0])
prub.intercept_ = np.array(modelo[1])
prub.classes_ = np.array([False, True])
print(prub.predict([mckVector]))

