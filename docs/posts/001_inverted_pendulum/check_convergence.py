"""Compare velocity-first Euler with a refined RK4 reference at t = 0.5 s.

Run with Python's standard library: python check_convergence.py
Uses the article's default parameters, initial theta = 0.1 rad, and zero force.
"""

from dataclasses import astuple

from pendulum import State, accelerations, simulate


def reference_solution(dt):
    """Classical fourth-order Runge–Kutta, with a timestep dividing 0.5 s."""
    if dt <= 0:
        raise ValueError("The reference timestep must be positive.")
    steps = round(0.5 / dt)
    if abs(steps * dt - 0.5) > 1e-12:
        raise ValueError("The reference timestep must divide 0.5 s.")
    values = astuple(State(theta=0.1))

    def derivative(y):
        x_ddot, theta_ddot = accelerations(State(*y), force=0.0)
        return (y[1], x_ddot, y[3], theta_ddot)

    def shifted(y, slope, interval):
        return tuple(value + interval * change for value, change in zip(y, slope))

    for _ in range(steps):
        k1 = derivative(values)
        k2 = derivative(shifted(values, k1, dt / 2))
        k3 = derivative(shifted(values, k2, dt / 2))
        k4 = derivative(shifted(values, k3, dt))
        values = tuple(
            value + dt * (a + 2 * b + 2 * c + d) / 6
            for value, a, b, c, d in zip(values, k1, k2, k3, k4)
        )
    return State(*values)


def check_convergence():
    coarse_reference = reference_solution(0.0001)
    reference = reference_solution(0.00005)
    # Each state component is compared in its SI unit (m, m/s, rad, rad/s).
    assert all(abs(a - b) < 1e-10
               for a, b in zip(astuple(coarse_reference), astuple(reference)))
    rows = []
    for dt in (0.004, 0.002, 0.001):
        _, states, _ = simulate(State(theta=0.1), duration=0.5, dt=dt)
        error_x = abs(states[-1].x - reference.x)
        error_theta = abs(states[-1].theta - reference.theta)
        rows.append((dt, error_x, error_theta))
    for coarse, fine in zip(rows, rows[1:]):
        # First-order convergence should reduce both errors by about a half.
        assert 0.45 < fine[1] / coarse[1] < 0.55
        assert 0.45 < fine[2] / coarse[2] < 0.55
    return reference, rows


if __name__ == "__main__":
    reference, rows = check_convergence()
    print(f"RK4 reference: x={reference.x:.9f} m, theta={reference.theta:.9f} rad")
    print("dt (s)    |x error| (m)    |theta error| (rad)")
    for dt, error_x, error_theta in rows:
        print(f"{dt:.3f}     {error_x:.6e}     {error_theta:.6e}")
