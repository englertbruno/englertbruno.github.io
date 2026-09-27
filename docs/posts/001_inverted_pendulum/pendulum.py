"""Uniform-rod cart pendulum; SI units, upright-zero clockwise-positive angle.

The numerical core uses only the Python standard library. Run this file with
Matplotlib installed to regenerate free_motion.svg beside it.
"""

from dataclasses import dataclass
from math import ceil, cos, isfinite, sin
from pathlib import Path


@dataclass(frozen=True)
class Parameters:
    M: float = 1.0  # cart mass, kg
    m: float = 0.5  # uniform rod mass, kg
    L: float = 1.0  # full rod length, m
    b: float = 0.1  # linear cart damping, N s / m
    g: float = 9.81  # gravitational acceleration, m / s^2

    def __post_init__(self):
        if not all(isfinite(v) and v > 0 for v in (self.M, self.m, self.L, self.g)):
            raise ValueError("masses, length, and gravity must be finite and positive")
        if not isfinite(self.b) or self.b < 0:
            raise ValueError("damping must be finite and nonnegative")

    @property
    def l(self):
        return self.L / 2

    @property
    def I(self):
        return self.m * self.L**2 / 12

    @property
    def J(self):
        return self.I + self.m * self.l**2


@dataclass(frozen=True)
class State:
    x: float = 0.0  # cart position, m
    v: float = 0.0  # cart velocity, m / s
    theta: float = 0.1  # angle from upright, rad; positive leans right
    omega: float = 0.0  # angular velocity, rad / s


def accelerations(state, force, parameters=Parameters()):
    """Solve the two coupled equations at the current state."""
    p = parameters
    if not all(isfinite(v) for v in (state.x, state.v, state.theta, state.omega, force)):
        raise ValueError("state and force must be finite")
    a = p.M + p.m
    coupling = p.m * p.l * cos(state.theta)
    rhs_x = force - p.b * state.v + p.m * p.l * state.omega**2 * sin(state.theta)
    rhs_theta = p.m * p.g * p.l * sin(state.theta)
    determinant = a * p.J - coupling**2
    x_ddot = (p.J * rhs_x - coupling * rhs_theta) / determinant
    theta_ddot = (a * rhs_theta - coupling * rhs_x) / determinant
    return x_ddot, theta_ddot


def step(state, force, dt, parameters=Parameters()):
    """One velocity-first Euler step; both accelerations use the old state."""
    if not isfinite(dt) or dt <= 0:
        raise ValueError("dt must be finite and positive")
    x_ddot, theta_ddot = accelerations(state, force, parameters)
    v = state.v + dt * x_ddot
    omega = state.omega + dt * theta_ddot
    return State(state.x + dt * v, v, state.theta + dt * omega, omega)


def simulate(initial=State(), duration=1.2, dt=0.001, controller=None, parameters=Parameters()):
    """Return times, states, and forces; controller(state) supplies force in N.

    The controller is evaluated at each sampled state. The last force is shown
    for completeness but is not integrated beyond the requested duration.
    """
    if not isfinite(duration) or duration < 0:
        raise ValueError("duration must be finite and nonnegative")
    if not isfinite(dt) or dt <= 0:
        raise ValueError("dt must be finite and positive")
    times, states, forces = [0.0], [initial], []
    count = ceil(duration / dt)
    for i in range(count):
        end = min((i + 1) * dt, duration)
        # Floating-point division can make ceil(duration / dt) one too large.
        if end <= times[-1]:
            break
        force = 0.0 if controller is None else float(controller(states[-1]))
        forces.append(force)
        states.append(step(states[-1], force, end - times[-1], parameters))
        times.append(end)
    forces.append(0.0 if controller is None else float(controller(states[-1])))
    return times, states, forces


def style_plot_svg(path):
    """Make the SVG transparent and adapt its ink to the embedding page's theme."""
    path = Path(path)
    svg = path.read_text()
    if 'id="pendulum-plot-theme"' in svg:
        return
    # Matplotlib writes explicit colors for lines, but glyphs inherit their fill.
    for color, replacement in {
        "#ffffff": "none",
        "#000000": "var(--ink)",
        "#555555": "var(--axis)",
        "#b0b0b0": "var(--grid)",
        "#1763a6": "var(--blue)",
        "#ba4b18": "var(--orange)",
    }.items():
        svg = svg.replace(color, replacement)
    svg = svg.replace('id="figure_1"', 'id="figure_1" fill="var(--ink)"')
    theme = """<style id="pendulum-plot-theme">
    :root {
      color-scheme: light dark;
      --ink: #25384a;
      --axis: #52677b;
      --grid: #66788a;
      --blue: #1763a6;
      --orange: #ad4715;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --ink: #e2e8f0;
        --axis: #b1c2d1;
        --grid: #859bb0;
        --blue: #75baff;
        --orange: #f4a66a;
      }
    }
  </style>"""
    start = svg.index(">", svg.index("<svg")) + 1
    svg = svg[:start] + "\n " + theme + svg[start:]
    path.write_text(svg)


def save_plot(path=None):
    """Generate the article's open-loop trajectory without opening a window."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from math import degrees

    plt.rcParams.update({"font.family": "DejaVu Serif", "mathtext.fontset": "dejavuserif"})
    times, states, _ = simulate()
    fig, axes = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True, layout="constrained")
    axes[0].plot(times, [degrees(s.theta) for s in states], color="#1763a6")
    axes[0].set_ylabel("Tilt from upright (degrees)")
    axes[0].set_title("No controller: a 5.73° initial tilt grows")
    axes[1].plot(times, [s.x for s in states], color="#ba4b18")
    axes[1].set_ylabel("Cart position (m)")
    axes[1].set_xlabel("Time (s)")
    for axis in axes:
        axis.grid(alpha=0.25)
        axis.axhline(0, color="#555555", linewidth=0.6)
    output = Path(path) if path else Path(__file__).with_name("free_motion.svg")
    fig.savefig(output, metadata={"Date": None}, transparent=True)
    plt.close(fig)
    style_plot_svg(output)
    return output


if __name__ == "__main__":
    initial = State()
    print("Initial accelerations:", accelerations(initial, 0.0))
    print("After 1 ms:", step(initial, 0.0, 0.001))
    print("Saved", save_plot())
