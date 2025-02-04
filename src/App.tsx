import React, { useState, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";

function App() {
  // References and state for our input fields.
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [velocity, setVelocity] = useState<number>(50);
  const [launchAngle, setLaunchAngle] = useState<number>(45);
  const [azimuthAngle, setAzimuthAngle] = useState<number>(0);
  const [spinRate, setSpinRate] = useState<number>(0);
  const [backspin, setBackspin] = useState<number>(0);
  const [sidespin, setSidespin] = useState<number>(0);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    console.log("handleSubmit");
    console.log(
      velocity,
      launchAngle,
      azimuthAngle,
      spinRate,
      backspin,
      sidespin
    );
    e.preventDefault();
    try {
      // Call the simulate command from Rust
      const result: { points: [number, number][] } = await invoke("simulate", {
        velocity,
        launchAngle: launchAngle,
        azimuthAngle: azimuthAngle,
        spinRate: spinRate,
        backspin,
        sidespin,
      });
      drawFlightPath(result.points);
    } catch (error) {
      console.error("Simulation error:", error);
    }
  }

  // Draw the flight path based on the [ground distance, height] points.
  function drawFlightPath(points: [number, number][]) {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Clear the canvas for a new drawing.
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!points || points.length === 0) return;

    // Determine the maximum ground distance and height for scaling.
    let maxX = 0;
    let maxY = 0;
    points.forEach(([x, y]) => {
      if (x > maxX) maxX = x;
      if (y > maxY) maxY = y;
    });
    // Apply a margin for visual appeal.
    maxX *= 1.1;
    maxY *= 1.1;

    // Determine scaling factors.
    const scaleX = canvas.width / maxX;
    const scaleY = canvas.height / maxY;

    // Draw the flight path.
    ctx.beginPath();
    points.forEach(([x, y], index) => {
      const canvasX = x * scaleX;
      // Invert the y-axis so that the ground is at the bottom of the canvas.
      const canvasY = canvas.height - y * scaleY;
      if (index === 0) {
        ctx.moveTo(canvasX, canvasY);
      } else {
        ctx.lineTo(canvasX, canvasY);
      }
    });
    ctx.strokeStyle = "red";
    ctx.lineWidth = 2;
    ctx.stroke();
  }

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Left pane with the input form */}
      <div
        style={{
          width: "300px",
          padding: "15px",
          borderRight: "1px solid #ccc",
          boxSizing: "border-box",
        }}
      >
        <h2>Input Parameters</h2>
        <form onSubmit={handleSubmit}>
          <label htmlFor="velocity">Velocity:</label>
          <input
            type="number"
            id="velocity"
            value={velocity}
            onChange={(e) => setVelocity(parseFloat(e.target.value))}
            step="any"
            required
          />

          <label htmlFor="launch_angle">Launch Angle (degrees):</label>
          <input
            type="number"
            id="launch_angle"
            value={launchAngle}
            onChange={(e) => setLaunchAngle(parseFloat(e.target.value))}
            step="any"
            required
          />

          <label htmlFor="azimuth_angle">Azimuth Angle (degrees):</label>
          <input
            type="number"
            id="azimuth_angle"
            value={azimuthAngle}
            onChange={(e) => setAzimuthAngle(parseFloat(e.target.value))}
            step="any"
            required
          />

          <label htmlFor="spin_rate">Spin Rate:</label>
          <input
            type="number"
            id="spin_rate"
            value={spinRate}
            onChange={(e) => setSpinRate(parseFloat(e.target.value))}
            step="any"
            required
          />

          <label htmlFor="backspin">Backspin:</label>
          <input
            type="number"
            id="backspin"
            value={backspin}
            onChange={(e) => setBackspin(parseFloat(e.target.value))}
            step="any"
            required
          />

          <label htmlFor="sidespin">Sidespin:</label>
          <input
            type="number"
            id="sidespin"
            value={sidespin}
            onChange={(e) => setSidespin(parseFloat(e.target.value))}
            step="any"
            required
          />

          <button
            type="submit"
            style={{
              marginTop: "15px",
              width: "100%",
              padding: "10px",
              backgroundColor: "#007acc",
              color: "white",
              border: "none",
              cursor: "pointer",
            }}
          >
            Simulate
          </button>
        </form>
      </div>
      {/* Right pane with the canvas for rendering the flight path */}
      <div
        style={{
          flexGrow: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#f8f8f8",
        }}
      >
        <canvas
          ref={canvasRef}
          width={800}
          height={600}
          style={{ border: "1px solid #000" }}
        />
      </div>
    </div>
  );
}

export default App;
