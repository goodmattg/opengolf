import React, { useState, useMemo } from "react";
import { invoke } from "@tauri-apps/api/core";
import { Canvas } from "@react-three/fiber";
import * as THREE from "three";

interface FlightPath {
  points: Array<[number, number, number, number]>;
  flight_time: number;
  distance: number;
  x_apex: number;
  y_apex: number;
  x_launch: number;
  y_launch: number;
  z_launch: number;
  x_landing: number;
  y_landing: number;
  z_landing: number;
}

// A simple ball rendered as a circle on the ground.
function Ball() {
  return (
    <mesh position={[0, 0.2, 0]}>
      <circleGeometry args={[0.2, 16]} />
      <meshBasicMaterial color="blue" side={THREE.DoubleSide} />
    </mesh>
  );
}

type FlightArcProps = {
  points: [number, number, number, number][];
};

// Renders the flight arc returned from simulate_3d as a red line.
const FlightArc: React.FC<FlightArcProps> = ({ points }) => {
  // Convert the simulation points ([x, y, z, t]) into a flattened Float32Array.
  const positions = useMemo(() => {
    const arr: number[] = [];
    points.forEach(([x, y, z]) => {
      arr.push(x, y, z);
    });
    return new Float32Array(arr);
  }, [points]);

  return (
    <line>
      <bufferGeometry attach="geometry">
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <lineBasicMaterial attach="material" color="red" />
    </line>
  );
};

function App() {
  // Input field states.
  const [velocity, setVelocity] = useState<number>(50);
  const [launchAngle, setLaunchAngle] = useState<number>(45);
  const [azimuthAngle, setAzimuthAngle] = useState<number>(0);
  const [spinRate, setSpinRate] = useState<number>(0);
  const [backspin, setBackspin] = useState<number>(0);
  const [sidespin, setSidespin] = useState<number>(0);

  // State for the 3D flight path returned from simulate_3d.
  const [flightPath, setFlightPath] = useState<
    [number, number, number, number][]
  >([]);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    console.log(
      "handleSubmit",
      velocity,
      launchAngle,
      azimuthAngle,
      spinRate,
      backspin,
      sidespin
    );
    e.preventDefault();
    try {
      // Call the new simulate_3d command.
      // Note: We send keys using underscore names to match the Rust definitions.
      const result: FlightPath = await invoke("simulate_3d", {
        velocity,
        launchAngle,
        azimuthAngle,
        spinRate,
        backspin,
        sidespin,
        sampleRate: 100,
        xLaunch: 0,
        yLaunch: 0,
        zLaunch: 0,
      });
      setFlightPath(result.points);
      console.log("flightPath", result);
    } catch (error) {
      console.error("Simulation error:", error);
    }
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
            Simulate 3D
          </button>
        </form>
      </div>

      {/* Right pane with the 3D rendering */}
      <div style={{ flexGrow: 1, background: "#f8f8f8" }}>
        <Canvas
          camera={{ position: [0, 5, 10], fov: 60 }}
          style={{ height: "100%", width: "100%" }}
        >
          {/* Simple lighting */}
          <ambientLight intensity={0.5} />
          <directionalLight position={[0, 10, 5]} intensity={1} />
          {/* A ground plane */}
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
            <planeGeometry args={[50, 50]} />
            <meshStandardMaterial color="#dddddd" />
          </mesh>
          {/* Render the ball as a circle positioned at the center bottom of the scene */}
          <Ball />
          {/* Draw the flight arc if one exists */}
          {flightPath.length > 0 && <FlightArc points={flightPath} />}
        </Canvas>
      </div>
    </div>
  );
}

export default App;
