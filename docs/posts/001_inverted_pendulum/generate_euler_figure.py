"""Generate the Euler illustration with only the Python standard library.

The illustrative equation is y' = 3y with y(0) = 1 (dimensionless variables).
The exact solution is exp(3t); explicit Euler uses steps of length 0.25 and 0.05.
Run this file to regenerate euler_method.svg next to it.
"""

from math import exp
from pathlib import Path


def make_figure():
    left, right, top, bottom = 90.0, 720.0, 100.0, 442.0
    low, high = 0.0, 21.5
    growth_rate = 3.0

    def xy(t, y):
        return left + (right - left) * t, bottom - (bottom - top) * (y - low) / (high - low)

    def point(t, y):
        x, y = xy(t, y)
        return f"{x:.3f},{y:.3f}"

    def euler_points(dt):
        values = [(0.0, 1.0)]
        for step in range(1, round(1 / dt) + 1):
            values.append((step * dt, values[-1][1] * (1 + growth_rate * dt)))
        return values

    euler = euler_points(0.25)
    fine = euler_points(0.05)

    # This right triangle is the actual fourth step, not a tangent drawn at
    # a point of the exact solution. Its rise equals the derivative 3y times dt.
    ta, ya = euler[3]
    tb, yb = euler[4]
    ax, ay = xy(ta, ya)
    bx, by = xy(tb, yb)

    svg = ['''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="525" viewBox="0 0 960 525" role="img" aria-labelledby="title desc">
<title id="title">Euler's method uses the current derivative for each straight step</title>
<desc id="desc">A steepening blue curve shows the exact solution y = exp(3t) of dy/dt = 3y with y(0) = 1. A solid orange polyline with square nodes takes four Euler steps of length 0.25, ending near 9.38 while the exact solution reaches 20.09. A green dashed polyline with small circular nodes takes twenty steps of length 0.05, ending near 16.37 and staying closer to the exact curve. The coarse node at t = 0.75 is labeled slope = dy/dt = 3y, evaluated at that approximate node. A right triangle below the final straight segment shows the time step of 0.25 and the rise equal to this derivative times the time step. Both axes are dimensionless.</desc>
<style>
  :root {
    color-scheme: light dark;
    --ink: #25384a;
    --line: #52677b;
    --grid: #66788a;
    --blue: #1763a6;
    --orange: #ad4715;
    --green: #267451;
    --wash: rgba(173, 71, 21, 0.06);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --ink: #e2e8f0;
      --line: #b1c2d1;
      --grid: #859bb0;
      --blue: #75baff;
      --orange: #f4a66a;
      --green: #88d4b0;
      --wash: rgba(244, 166, 106, 0.06);
    }
  }
</style>
<g font-family="DejaVu Serif, serif" font-size="23" fill="var(--ink)" stroke-linecap="butt" stroke-linejoin="miter">
<path d="M90 40H135" fill="none" stroke="var(--blue)" stroke-width="3"/>
<text x="148" y="48">Exact</text>
<path d="M286 40H331" fill="none" stroke="var(--orange)" stroke-width="3"/>
<rect x="303" y="35" width="10" height="10" fill="var(--orange)"/>
<text x="344" y="48">Euler Δt = 0.25</text>
<path d="M592 40H637" fill="none" stroke="var(--green)" stroke-width="2.5" stroke-dasharray="6 4"/>
<circle cx="615" cy="40" r="3" fill="var(--green)"/>
<text x="650" y="48">Euler Δt = 0.05</text>
''']

    for y in [0, 5, 10, 15, 20]:
        _, py = xy(0, y)
        svg.append(f'<path d="M{left} {py:.3f}H{right}" stroke="var(--grid)" stroke-opacity="0.22" stroke-width="1"/>')
        svg.append(f'<text x="{left - 17}" y="{py + 8:.3f}" text-anchor="end" font-size="21">{y:g}</text>')

    svg.append(f'<path d="M{left} {top}V{bottom}H{right + 28}" fill="none" stroke="var(--line)" stroke-width="2"/>')
    for t in [0, 0.25, 0.5, 0.75, 1]:
        px, _ = xy(t, 0)
        svg.append(f'<path d="M{px:.3f} {bottom}v7" stroke="var(--line)" stroke-width="2"/>')
        svg.append(f'<text x="{px:.3f}" y="{bottom + 34}" text-anchor="middle" font-size="21">{t:g}</text>')

    svg.append('<text x="48" y="95" font-style="italic">y</text>')
    svg.append('<text x="771" y="477" font-style="italic">t</text>')

    svg.append(f'<path d="M{ax:.3f} {ay:.3f}H{bx:.3f}V{by:.3f}Z" fill="var(--wash)"/>')
    svg.append(f'<path d="M{ax:.3f} {ay:.3f}H{bx:.3f}V{by:.3f}" fill="none" stroke="var(--line)" stroke-width="1.8" stroke-dasharray="5 5"/>')
    svg.append(f'<path d="M{bx - 11:.3f} {ay:.3f}v-11h11" fill="none" stroke="var(--line)" stroke-width="1.2"/>')
    svg.append(f'<text x="{(ax + bx) / 2:.3f}" y="{ay + 29:.3f}" text-anchor="middle">Δt = 0.25</text>')
    svg.append(f'<text x="{bx + 17:.3f}" y="{(ay + by) / 2 + 8:.3f}">Δy = (dy/dt) Δt</text>')

    exact = ' '.join(point(i / 200, exp(growth_rate * i / 200)) for i in range(201))
    approx = ' '.join(point(t, y) for t, y in euler)
    fine_approx = ' '.join(point(t, y) for t, y in fine)
    svg.append(f'<polyline id="exact-curve" points="{exact}" fill="none" stroke="var(--blue)" stroke-width="3"/>')
    svg.append(f'<polyline id="fine-euler-steps" points="{fine_approx}" fill="none" stroke="var(--green)" stroke-width="2.5" stroke-dasharray="6 4"/>')
    for t, y in fine:
        px, py = xy(t, y)
        svg.append(f'<circle cx="{px:.3f}" cy="{py:.3f}" r="2.5" fill="var(--green)"/>')
    svg.append(f'<polyline id="euler-steps" points="{approx}" fill="none" stroke="var(--orange)" stroke-width="3.5"/>')
    for t, y in euler:
        px, py = xy(t, y)
        svg.append(f'<rect x="{px - 5:.3f}" y="{py - 5:.3f}" width="10" height="10" fill="var(--orange)"/>')

    # The leader reaches the computed Euler node, not the exact curve.
    svg.append(f'<path d="M485 396L{ax - 6:.3f} {ay + 9:.3f}" fill="none" stroke="var(--line)" stroke-width="1.5"/>')
    svg.append('<text x="420" y="422">slope = dy/dt = 3y</text>')
    svg.append('</g>\n</svg>\n')
    return '\n'.join(svg)


if __name__ == "__main__":
    Path(__file__).with_name("euler_method.svg").write_text(make_figure())
