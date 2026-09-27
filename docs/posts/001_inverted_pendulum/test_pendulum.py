"""Physical sanity checks and a timestep boundary regression (standard library)."""

import unittest

from pendulum import Parameters, State, accelerations, simulate, step


class PendulumChecks(unittest.TestCase):
    def test_upright_equilibrium_and_response_directions(self):
        self.assertEqual(accelerations(State(theta=0), 0), (0, 0))
        self.assertGreater(accelerations(State(theta=0.1), 0)[1], 0)
        self.assertLess(accelerations(State(theta=0), 1)[1], 0)

    def test_reflection_reverses_motion(self):
        right = State(0.3, 0.4, 0.2, -0.7)
        left = State(-0.3, -0.4, -0.2, 0.7)
        a = accelerations(right, 2)
        reflected = accelerations(left, -2)
        for first, second in zip(a, reflected):
            self.assertAlmostEqual(first, -second)

    def test_damping_opposes_cart_motion_while_upright(self):
        damped = accelerations(State(v=1, theta=0), 0, Parameters(b=0.1))
        undamped = accelerations(State(v=1, theta=0), 0, Parameters(b=0))
        self.assertLess(damped[0], 0)
        self.assertEqual(undamped, (0, 0))

    def test_decimal_duration_does_not_create_zero_length_step(self):
        times, states, forces = simulate(duration=0.07, dt=0.01)
        self.assertEqual(len(times), 8)
        self.assertEqual(times[-1], 0.07)
        self.assertEqual(len(times), len(states))
        self.assertEqual(len(times), len(forces))
        self.assertTrue(all(a < b for a, b in zip(times, times[1:])))

    def test_final_partial_step_and_zero_duration(self):
        times, states, forces = simulate(duration=0.075, dt=0.01)
        self.assertEqual(times[-1], 0.075)
        self.assertEqual(len(times), 9)
        self.assertEqual(len(times), len(states))
        self.assertEqual(len(times), len(forces))
        times, states, forces = simulate(duration=0)
        self.assertEqual(times, [0])
        self.assertEqual(states, [State()])
        self.assertEqual(forces, [0])

    def test_step_does_not_mutate_the_initial_state(self):
        initial = State()
        result = step(initial, 0, 0.001)
        self.assertEqual(initial, State())
        self.assertGreater(result.theta, initial.theta)


if __name__ == "__main__":
    unittest.main()
