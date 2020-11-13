import numpy as np


def f(t, params):
    """A powerlaw: a * e**(t*b)"""
    arr = np.sum(np.multiply(np.vstack(params[:-1:2]), np.exp(np.multiply(-t, np.vstack(params[1:-1:2]))))) + params[-1]
    return arr


params = np.array([0.037, 0.79, 0.013, 17466.18, 0.00589, 1052.53, 0.0055, 13.74, 0.004, 102.156, 0.933])
t = np.linspace(0, 1000, 2000)
data = f(t, params)

all_data = np.zeros((2000, 2000))
for i in range(2000):
    noise = np.random.default_rng().normal(size=2000)
    all_data[i] = data + noise

np.save('data_noise.npy', all_data)

