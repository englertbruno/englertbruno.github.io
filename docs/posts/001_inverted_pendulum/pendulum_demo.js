/* Browser version of pendulum.py: SI units, clockwise angle from upright.
 * Keep this calculation independent of drawing so it can be compared with Python.
 */
"use strict";

const Pendulum = (() => {
  const parameters = Object.freeze({ M: 1, m: 0.5, L: 1, b: 0.1, g: 9.81 });
  const initialState = () => ({ x: 0, v: 0, theta: 0.1, omega: 0 });

  function accelerations(state, force, p = parameters) {
    const l = p.L / 2;
    const J = p.m * p.L ** 2 / 12 + p.m * l ** 2;
    const a = p.M + p.m;
    const coupling = p.m * l * Math.cos(state.theta);
    const rhsX = force - p.b * state.v + p.m * l * state.omega ** 2 * Math.sin(state.theta);
    const rhsTheta = p.m * p.g * l * Math.sin(state.theta);
    const determinant = a * J - coupling ** 2;
    return [
      (J * rhsX - coupling * rhsTheta) / determinant,
      (a * rhsTheta - coupling * rhsX) / determinant,
    ];
  }

  function step(state, force, dt, p = parameters) {
    const [xDDot, thetaDDot] = accelerations(state, force, p);
    const v = state.v + dt * xDDot;
    const omega = state.omega + dt * thetaDDot;
    return { x: state.x + dt * v, v, theta: state.theta + dt * omega, omega };
  }

  return { parameters, initialState, accelerations, step };
})();

// Node can load the same numerical functions for comparison with pendulum.py.
if (typeof module !== "undefined") module.exports = Pendulum;

if (typeof document !== "undefined") {
  const canvas = document.getElementById("scene");
  const ctx = canvas.getContext("2d");
  const toggle = document.getElementById("toggle");
  const readout = document.getElementById("readout");
  const status = document.getElementById("status");
  const cartMass = document.getElementById("cart-mass");
  const rodMass = document.getElementById("rod-mass");
  const forceControl = document.getElementById("force-magnitude");
  const theme = window.matchMedia("(prefers-color-scheme: dark)");
  const dt = 0.001;
  const keys = new Set();
  const pointers = new Map();
  let state = Pendulum.initialState();
  let ticks = 0;
  let running = false;
  let previousTime = null;
  let accumulator = 0;
  const parameters = { ...Pendulum.parameters };
  let forceMagnitude = Number(forceControl.value);
  let palette;

  function updatePalette() {
    const style = getComputedStyle(document.documentElement);
    palette = Object.fromEntries(
      ["ink", "muted", "border", "cart", "blue", "orange"].map(
        name => [name, style.getPropertyValue(`--${name}`).trim()]
      )
    );
  }
  updatePalette();
  theme.addEventListener("change", updatePalette);

  // Let the article's iframe grow when controls wrap on a narrow screen.
  if (window.frameElement) {
    const main = document.querySelector("main");
    new ResizeObserver(() => {
      window.frameElement.style.height = `${Math.ceil(main.getBoundingClientRect().height) + 2}px`;
    }).observe(main);
  }

  function force() {
    const directions = new Set([...keys, ...pointers.values()]);
    return forceMagnitude * (Number(directions.has("right")) - Number(directions.has("left")));
  }

  function clearControls() {
    keys.clear();
    pointers.clear();
  }

  function setRunning(value) {
    running = value;
    previousTime = null;
    accumulator = 0;
    if (!value) clearControls();
    toggle.textContent = value ? "Pause" : (ticks ? "Resume" : "Start");
    status.textContent = value ? "Running" : "Paused";
  }

  toggle.addEventListener("click", () => setRunning(!running));
  function reset() {
    state = Pendulum.initialState();
    ticks = 0;
    setRunning(false);
  }
  document.getElementById("reset").addEventListener("click", reset);

  for (const [control, key] of [[cartMass, "M"], [rodMass, "m"]]) {
    function updateMass() {
      parameters[key] = Number(control.value);
      const label = `${parameters[key].toFixed(1)} kg`;
      document.getElementById(`${control.id}-value`).textContent = label;
      control.setAttribute("aria-valuetext", label);
    }
    updateMass();
    control.addEventListener("input", () => {
      updateMass();
      reset();
    });
  }
  function updateForce() {
    forceMagnitude = Number(forceControl.value);
    const label = `${forceMagnitude.toFixed(1)} N`;
    document.getElementById("force-magnitude-value").textContent = label;
    forceControl.setAttribute("aria-valuetext", label);
    for (const direction of ["left", "right"]) {
      document.getElementById(direction).setAttribute(
        "aria-label", `Hold to push ${direction} with ${forceMagnitude.toFixed(1)} newtons`
      );
    }
  }
  forceControl.addEventListener("input", updateForce);
  updateForce();

  for (const direction of ["left", "right"]) {
    const button = document.getElementById(direction);
    button.addEventListener("pointerdown", event => {
      if (event.button !== 0) return;
      button.setPointerCapture(event.pointerId);
      pointers.set(event.pointerId, direction);
    });
    for (const name of ["pointerup", "pointercancel", "lostpointercapture"]) {
      button.addEventListener(name, event => pointers.delete(event.pointerId));
    }
    // Make the force buttons usable from the keyboard as well as with arrows.
    button.addEventListener("keydown", event => {
      if (event.code === "Space" || event.code === "Enter") {
        event.preventDefault();
        keys.add(direction);
      }
    });
    button.addEventListener("keyup", event => {
      if (event.code === "Space" || event.code === "Enter") keys.delete(direction);
    });
    button.addEventListener("blur", () => keys.delete(direction));
  }

  window.addEventListener("keydown", event => {
    // Arrow keys on sliders adjust the parameter, rather than pushing the cart.
    if (event.target instanceof HTMLInputElement) return;
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      keys.add(event.key === "ArrowLeft" ? "left" : "right");
    }
  });
  window.addEventListener("keyup", event => {
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      keys.delete(event.key === "ArrowLeft" ? "left" : "right");
    }
  });
  // A missed key release must not leave a force applied after changing tabs.
  window.addEventListener("blur", () => setRunning(false));
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) setRunning(false);
  });

  function line(x0, y0, x1, y1, color, width = 2) {
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
  }

  function draw() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const ratio = window.devicePixelRatio || 1;
    if (canvas.width !== Math.round(width * ratio) || canvas.height !== Math.round(height * ratio)) {
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
    }
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, width, height);
    const scale = Math.min(120, width / 3.2);
    const pivotX = width / 2;
    const pivotY = height / 2 - 10;
    const trackY = pivotY + 39;
    ctx.font = "14px system-ui, sans-serif";
    ctx.fillStyle = palette.muted;
    ctx.textAlign = "center";
    line(0, trackY, width, trackY, palette.border);
    const halfView = width / (2 * scale);
    for (let mark = Math.ceil((state.x - halfView) * 2); mark <= (state.x + halfView) * 2; mark++) {
      const x = pivotX + (mark / 2 - state.x) * scale;
      line(x, trackY, x, trackY + 7, palette.border);
      if (mark % 2 === 0) ctx.fillText(`${mark / 2} m`, x, trackY + 24);
    }
    // Draw the cart and rod to a fixed scale; the camera follows the cart.
    ctx.fillStyle = palette.cart;
    ctx.strokeStyle = palette.ink;
    ctx.lineWidth = 2;
    ctx.fillRect(pivotX - 40, pivotY, 80, 25);
    ctx.strokeRect(pivotX - 40, pivotY, 80, 25);
    ctx.fillStyle = palette.ink;
    for (const dx of [-25, 25]) {
      ctx.beginPath();
      ctx.arc(pivotX + dx, pivotY + 31, 8, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.setLineDash([4, 5]);
    line(pivotX, pivotY, pivotX, pivotY - scale, palette.border, 1);
    ctx.setLineDash([]);
    const rodX = pivotX + scale * Math.sin(state.theta);
    const rodY = pivotY - scale * Math.cos(state.theta);
    line(pivotX, pivotY, rodX, rodY, palette.orange, 7);
    ctx.beginPath();
    ctx.arc(pivotX, pivotY, 5, 0, Math.PI * 2);
    ctx.fill();
    const push = force();
    if (push) {
      const end = pivotX + Math.sign(push) * Math.min(width / 2 - 15, 25 + 10 * Math.abs(push));
      line(pivotX, pivotY + 12, end, pivotY + 12, palette.blue, 3);
      line(end, pivotY + 12, end - Math.sign(push) * 10, pivotY + 5, palette.blue, 3);
      line(end, pivotY + 12, end - Math.sign(push) * 10, pivotY + 19, palette.blue, 3);
    }
    readout.textContent = `t = ${(ticks * dt).toFixed(2)} s   ·   x = ${state.x.toFixed(3)} m   ·   θ = ${(state.theta * 180 / Math.PI).toFixed(1)}°   ·   F = ${push.toFixed(1)} N`;
    for (const direction of ["left", "right"]) {
      document.getElementById(direction).classList.toggle("held", direction === "left" ? push < 0 : push > 0);
    }
  }

  function frame(time) {
    if (running && previousTime !== null) {
      // Cap catch-up after a delayed frame; never enlarge the physics timestep.
      accumulator += Math.min((time - previousTime) / 1000, 0.05);
      while (accumulator >= dt) {
        state = Pendulum.step(state, force(), dt, parameters);
        ticks++;
        accumulator -= dt;
      }
    }
    previousTime = time;
    draw();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}
