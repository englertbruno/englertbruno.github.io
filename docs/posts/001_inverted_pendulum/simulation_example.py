"""Cart-and-rod simulation from the article. Requires NumPy.

Run: python3 simulation_example.py
Units: metres, kilograms, seconds, radians, newtons.
"""

import numpy as np

M, m, L = 1.0, 0.5, 1.0
b, g = 0.1, 9.81
l = L / 2
I = m * L**2 / 12


def step(state, force, dt):
    x, v, theta, omega = state
    coupling = m * l * np.cos(theta)

    A = np.array([
        [M + m, coupling],
        [coupling, I + m * l**2],
    ])
    r = np.array([
        force - b * v + m * l * omega**2 * np.sin(theta),
        m * g * l * np.sin(theta),
    ])
    cart_acc, angular_acc = np.linalg.solve(A, r)

    v += cart_acc * dt
    omega += angular_acc * dt
    x += v * dt
    theta += omega * dt
    return x, v, theta, omega


if __name__ == "__main__":
    state = (0.0, 0.0, 0.1, 0.0)
    for _ in range(1200):
        state = step(state, force=0.0, dt=0.001)

    x, v, theta, omega = state
    print(f"x = {x:.3f} m, theta = {np.degrees(theta):.1f} degrees")
