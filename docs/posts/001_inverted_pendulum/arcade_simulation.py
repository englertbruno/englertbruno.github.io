"""Interactive cart-and-pendulum simulation.

Run: python3 arcade_simulation.py
Controls: left/right arrows apply force; space saves a screenshot.
"""

import numpy as np

G = 9.81


class CartPendulum:
    def __init__(self, dt, length=200., pendulum_mass=0.5, cart_mass=1., friction_coefficient=0.0008):
        self.dt = dt
        self.length = length
        self.pendulum_mass = pendulum_mass
        self.cart_mass = cart_mass
        self.friction_coefficient = friction_coefficient

        self.cart_pos = 0.
        self.cart_speed = 0.

        self.pendulum_angle = np.pi / 2. + 1e-1  # angle
        self.pendulum_speed = 0.  # angular speed

        self.friction_force = 0.


    def step(self, force_on_cart):
        pendulum_mass_length = self.pendulum_mass * self.length
        total_mass = self.cart_mass + self.pendulum_mass
        pendulum_inertia = self.length ** 2 * self.pendulum_mass + self.pendulum_mass * (self.length / 2.) ** 2

        cosphi = np.cos(self.pendulum_angle)
        sinphi = -np.sin(self.pendulum_angle)
        self.friction_force = -self.friction_coefficient * self.cart_speed ** 2. * np.sign(self.cart_speed)

        cart_acc = ((cosphi * pendulum_mass_length * self.pendulum_speed ** 2 + force_on_cart + self.friction_force) * pendulum_inertia -
                    (pendulum_mass_length * -G * cosphi) * (pendulum_mass_length*sinphi)) / \
                   (total_mass * pendulum_inertia - pendulum_mass_length*sinphi*pendulum_mass_length*sinphi)

        angular_acc = (-cart_acc * pendulum_mass_length * sinphi + (pendulum_mass_length * -G * cosphi)) / pendulum_inertia

        self.cart_pos += self.cart_speed * self.dt
        self.cart_speed += cart_acc * self.dt
        self.pendulum_angle += self.pendulum_speed * self.dt
        self.pendulum_speed += angular_acc * self.dt


import math
import arcade


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600


class Simulation:
    def __init__(self):
        self.cart_pendulum = CartPendulum(0.05)
        self.shift = 300
        self.x0 =  self.cart_pendulum.cart_pos + self.shift
        self.y0 = self.shift
        self.x1 = self.shift
        self.y1 = self.shift

        self.user_applied_force = 0

    def step(self):
        self.cart_pendulum.step(self.user_applied_force)

    def draw(self):
        """ Draw our rectangle """
        self.x0 = self.cart_pendulum.cart_pos + self.shift
        self.y0 = self.shift
        self.x1 = self.cart_pendulum.cart_pos + self.cart_pendulum.length * math.cos(self.cart_pendulum.pendulum_angle) + self.shift
        self.y1 = self.cart_pendulum.length * math.sin(self.cart_pendulum.pendulum_angle) + self.shift

        overflow = (self.x0 // SCREEN_WIDTH) * SCREEN_WIDTH
        self.x0 -= overflow
        self.x1 -= overflow

        # Draw cart
        arcade.draw_lrbt_rectangle_outline(self.x0 - 100, self.x0 + 100,
                                           self.y0 - 25, self.y0 + 25, arcade.color.BLACK)
        # Draw pendulum
        arcade.draw_line(self.x0, self.y0, self.x1, self.y1, color=arcade.color.RED, line_width=4)
        arcade.draw_circle_filled(self.x0, self.y0, 10, arcade.color.BLACK)
        # Draw wheels
        wheel_distance = 60
        arcade.draw_circle_filled(self.x0 - wheel_distance, self.y0 - 25, 20, arcade.color.BLACK)
        arcade.draw_circle_filled(self.x0 + wheel_distance, self.y0 - 25, 20, arcade.color.BLACK)
        arcade.draw_arc_filled(self.x0 + wheel_distance, self.y0 - 25, 19, 19, color=(255, 255, 255),
                                             start_angle=0,
                                             end_angle=30, tilt_angle=-self.x0 * 360 / (2 * np.pi * 20))
        arcade.draw_arc_filled(self.x0 - wheel_distance, self.y0 - 25, 19, 19, color=(255, 255, 255),
                                             start_angle=0,
                                             end_angle=30, tilt_angle=-self.x0 * 360 / (2 * np.pi * 20))
        # Terrain
        arcade.draw_line(0, self.y0 - 45, SCREEN_WIDTH, self.y0 - 45, arcade.color.BLACK, 2)


        def draw_force(center, force, y, color, thickness=3, multiplier=3):
            if force >= 0:
                left = center
                right = np.fmin(center + force * multiplier, SCREEN_WIDTH)
            else:
                left = np.fmax(center + force * multiplier, 0)
                right = center

            arcade.draw_lrbt_rectangle_filled(left, right, y - thickness, y + thickness, color)

        draw_force(self.x0, self.cart_pendulum.friction_force, self.y0, color=arcade.color.BLUE_GREEN)
        draw_force(self.x0, self.user_applied_force, self.y0 - 5, color=arcade.color.YELLOW_ORANGE)

        text_y0 = 5
        text_y_diff = 22

        arcade.draw_text(
            text="{:0.2f}N Friction force".format(self.cart_pendulum.friction_force),
            x=SCREEN_WIDTH - 5,
            y=text_y0 + text_y_diff * 1,
            color=arcade.color.BLUE_GREEN,
            font_size=14,
            anchor_x='right')
        arcade.draw_text(
            text="{:0.2f}N User applied force".format(self.user_applied_force),
            x=SCREEN_WIDTH - 5,
            y=text_y0 + text_y_diff * 2,
            color=arcade.color.YELLOW_ORANGE,
            font_size=14,
            anchor_x='right')
        arcade.draw_text(
            text="{:0.2f}° Angle".format(((-self.cart_pendulum.pendulum_angle / (2 * np.pi) - 1 / 4) * 360) % 360 - 180),
            x=SCREEN_WIDTH - 5,
            y=text_y0 + text_y_diff * 3,
            color=arcade.color.BLACK,
            font_size=14,
            anchor_x='right')
        arcade.draw_text(
            text="{:0.2f}°/s Angular speed".format(-self.cart_pendulum.pendulum_speed / (2 * np.pi) * 360),
            x=SCREEN_WIDTH - 5,
            y=text_y0 + text_y_diff * 4,
            color=arcade.color.BLACK,
            font_size=14,
            anchor_x='right')



class Application(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        super().__init__(width, height, title="Pendulum On Cart")
        arcade.set_background_color(arcade.color.WHITE)
        self.simulation = None

    def setup(self):
        """ Set up the game and initialize the variables. """
        self.set_update_rate(1. / 160)  # set fps
        self.simulation = Simulation()

    def on_update(self, dt):
        """ Move everything """
        # print(1/dt)
        self.simulation.step()


    def on_draw(self):
        """
        Render the screen.
        """
        self.clear()
        self.simulation.draw()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        force = 10.
        if key == arcade.key.LEFT:
            self.simulation.user_applied_force = -force
        elif key == arcade.key.RIGHT:
            self.simulation.user_applied_force = force
        elif key == arcade.key.SPACE:
            image = arcade.get_image()
            image.save('screenshot.png', 'PNG')

    def on_key_release(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.LEFT:
            self.simulation.user_applied_force = 0

        elif key == arcade.key.RIGHT:
            self.simulation.user_applied_force = 0


    def on_close(self):
        super().on_close()


if __name__ == "__main__":
    window = Application(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()
