use serde::Serialize;
use tauri::State;

#[derive(Serialize)]
struct TwoDimFlightPath {
    points: Vec<(f64, f64)>,
}

#[derive(Serialize)]
struct FlightPath {
    points: Vec<(f64, f64, f64, f64)>,
    flight_time: f64,
    distance: f64,
    x_apex: f64,
    y_apex: f64,
    // Launch point (provided as input)
    x_launch: f64,
    y_launch: f64,
    z_launch: f64,
    // Landing point (assumed to be at y = 0 unless otherwise specified)
    x_landing: f64,
    y_landing: f64,
    z_landing: f64,
}

#[tauri::command]
fn simulate_3d(
    velocity: f64,
    launch_angle: f64,
    azimuth_angle: f64,
    spin_rate: f64,
    backspin: f64,
    sidespin: f64,
    sample_rate: u32,
    // TODO: Add wind speed and direction
    // TODO: Add temperature
    // TODO: Add humidity
    // TODO: Add elevation
    // TODO: Add green speed
    // TODO: Add green slope
    // TODO: Add green grain
    // TODO: Add green grain height
    // TODO: Add green grain density
    // TODO: Add green grain size
    // TODO: Add green grain shape
    // TODO: Add green grain orientation
    // TODO: Add green grain speed
    // TODO: Add green grain speed variance
    // Default launch point origin
    x_launch: f64,
    y_launch: f64,
    z_launch: f64,
) -> FlightPath {
    // Start Generation Here
    {
        // Physical constants and ball parameters
        let g = 9.81; // gravitational acceleration in m/s²
        let rho = 1.225; // air density in kg/m³
        let mass = 0.04593; // golf ball mass in kg (typical)
        let radius = 0.021335; // golf ball radius in meters (~42.67 mm diameter)
        let area = std::f64::consts::PI * radius * radius; // cross-sectional area in m²
        let C_d = 0.25; // drag coefficient (approximate value for a dimpled golf ball)

        // Time step for the numerical (Euler) integration simulation
        let dt = 0.01;

        // Convert launch and azimuth angles from degrees to radians.
        let launch_rad = launch_angle.to_radians();
        let azimuth_rad = azimuth_angle.to_radians();

        // Adjusted so that azimuth = 0 launches the ball along the z-axis.
        let mut vx = velocity * launch_rad.cos() * azimuth_rad.sin();
        let mut vz = velocity * launch_rad.cos() * azimuth_rad.cos();
        let mut vy = velocity * launch_rad.sin();

        // Start at the provided launch point.
        let mut pos = [x_launch, y_launch, z_launch];
        let mut t = 0.0;

        // We'll record a high-resolution simulation trajectory as (time, [x,y,z]).
        let mut traj: Vec<(f64, [f64; 3])> = Vec::new();
        traj.push((t, pos));
        // Initialize apex tracking using the launch position.
        let mut max_y = y_launch;
        let mut x_apex = x_launch;

        // Convert spin inputs (assumed in RPM) to rad/s.
        let omega_back = backspin * 2.0 * std::f64::consts::PI / 60.0;
        let omega_side = sidespin * 2.0 * std::f64::consts::PI / 60.0;

        // The following simulation implements a simplified model of golf ball flight
        // that includes gravity, aerodynamic drag, and the Magnus force due to spin.
        // For the Magnus effect, we decouple the contributions:
        //   • Backspin is assumed to produce an additional upward (vertical) force.
        //     Empirically, many sources use C_l ≈ 0.1 + 1.4 * (ω·r/v) for backspin.
        //   • Sidespin produces a lateral force perpendicular to the horizontal
        //     velocity component. Here we compute the lateral unit vector by rotating
        //     the horizontal velocity by 90°.
        //
        // Note: This "trick" of decoupling the spin effects is well publicized on golfing
        // simulation websites and provides a tractable analytical approximation.

        // Numerical integration loop until the ball lands (y becomes negative).
        while pos[1] >= 0.0 {
            // Compute current speed.
            let speed = (vx * vx + vy * vy + vz * vz).sqrt();
            if speed == 0.0 {
                break;
            }
            // Unit vector of velocity.
            let ux = vx / speed;
            let uy = vy / speed;
            let uz = vz / speed;

            // Drag acceleration: F_drag = 0.5 * rho * area * C_d * speed^2,
            // acceleration = F_drag/m in the direction opposite to velocity.
            let k_drag = 0.5 * rho * area * C_d / mass;
            let ax_drag = -k_drag * speed * vx; // (speed² * vx/speed)
            let ay_drag = -k_drag * speed * vy;
            let az_drag = -k_drag * speed * vz;

            // Magnus (lift) force due to backspin.
            // Empirical lift coefficient: C_l_back = 0.1 + 1.4 * (omega_back * radius / speed)
            let C_l_back = 0.1 + 1.4 * (omega_back * radius / speed);
            let a_mag_back = 0.5 * rho * area * C_l_back * speed * speed / mass;
            // For our simplified model, we apply the backspin lift entirely upward.
            let ax_mag_back = 0.0;
            let ay_mag_back = a_mag_back;
            let az_mag_back = 0.0;

            // Magnus (curving) force due to sidespin.
            // Empirical lift coefficient for sidespin is taken proportional to (omega_side * radius / speed)
            let C_l_side = (omega_side * radius / speed);
            let a_mag_side = 0.5 * rho * area * C_l_side * speed * speed / mass;
            // Lateral (horizontal) force: compute unit vector perpendicular to the horizontal velocity.
            let horizontal_speed = (vx * vx + vz * vz).sqrt();
            let (lx, lz) = if horizontal_speed > 0.0 {
                (-vz / horizontal_speed, vx / horizontal_speed)
            } else {
                (0.0, 0.0)
            };
            let ax_mag_side = a_mag_side * lx;
            let ay_mag_side = 0.0;
            let az_mag_side = a_mag_side * lz;

            // Total accelerations combining drag, Magnus forces, and gravity.
            let ax = ax_drag + ax_mag_back + ax_mag_side;
            let ay = -g + ay_drag + ay_mag_back + ay_mag_side;
            let az = az_drag + az_mag_back + az_mag_side;

            // Update velocity (Euler integration)
            vx += ax * dt;
            vy += ay * dt;
            vz += az * dt;

            // Update position
            pos[0] += vx * dt;
            pos[1] += vy * dt;
            pos[2] += vz * dt;
            t += dt;

            traj.push((t, pos));
            // Track the highest point (apex) of the flight.
            if pos[1] > max_y {
                max_y = pos[1];
                x_apex = pos[0];
            }
        }

        // Adjust the final point by linearly interpolating to the exact ground contact (y = 0).
        if traj.len() >= 2 {
            let n = traj.len();
            let (t_prev, pos_prev) = traj[n - 2];
            let (t_last, pos_last) = traj[n - 1];
            if pos_last[1] < 0.0 && pos_prev[1] > 0.0 {
                let frac = pos_prev[1] / (pos_prev[1] - pos_last[1]);
                let t_ground = t_prev + frac * (t_last - t_prev);
                let x_ground = pos_prev[0] + frac * (pos_last[0] - pos_prev[0]);
                let z_ground = pos_prev[2] + frac * (pos_last[2] - pos_prev[2]);
                // Replace last point with the ground contact point exactly at y = 0.
                traj.pop();
                traj.push((t_ground, [x_ground, 0.0, z_ground]));
            }
        }

        // Resample the trajectory to have exactly 'sample_rate' points evenly spaced in time.
        let total_time = traj.last().map(|(time, _)| *time).unwrap_or(0.0);
        let num_samples = if sample_rate < 2 { 2 } else { sample_rate } as usize;
        let mut resampled: Vec<(f64, f64, f64, f64)> = Vec::with_capacity(num_samples);

        // For each sample, determine the target time and interpolate the position linearly.
        for i in 0..num_samples {
            let t_target = (i as f64) * total_time / ((num_samples - 1) as f64);
            // Find simulation points bracketing t_target.
            let mut j = 0;
            while j < traj.len() - 1 && traj[j + 1].0 < t_target {
                j += 1;
            }
            let (t1, pos1) = traj[j];
            let (t2, pos2) = traj[j + 1];
            let factor = if (t2 - t1).abs() > 1e-6 {
                (t_target - t1) / (t2 - t1)
            } else {
                0.0
            };
            let x_interp = pos1[0] + factor * (pos2[0] - pos1[0]);
            let y_interp = pos1[1] + factor * (pos2[1] - pos1[1]);
            let z_interp = pos1[2] + factor * (pos2[2] - pos1[2]);
            resampled.push((x_interp, y_interp, z_interp, t_target));
        }

        // Landing point: take the final position from the trajectory (force y to 0)
        let [x_landing, y_landing, z_landing] = traj.last().unwrap().1;
        // Compute horizontal distance from the launch point.
        let distance = ((x_landing - x_launch).powi(2) + (z_landing - z_launch).powi(2)).sqrt();

        return FlightPath {
            points: resampled,
            flight_time: total_time,
            distance,
            x_apex,
            y_apex: max_y,
            x_launch,
            y_launch,
            z_launch,
            x_landing,
            y_landing,
            z_landing,
        };
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![simulate_3d])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
