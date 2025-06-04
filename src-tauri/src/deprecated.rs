#[tauri::command]
fn simulate(
    velocity: f64,
    launch_angle: f64,
    azimuth_angle: f64,
    spin_rate: f64,
    backspin: f64,
    sidespin: f64,
) -> TwoDimFlightPath {
    // Compute the flight path using a simple projectile simulation.
    // Using the launch_angle and azimuth_angle, we calculate the initial velocity
    // components along the x, y, and z axes. The simulation then collects points where
    // x and z are combined to form the horizontal ground distance.
    let mut points = Vec::new();
    let time_step = 0.1;
    let total_time = 10.0; // extend simulation time to capture the flight arc
    let g = 9.81;

    // Convert angles to radians
    let rad_launch = launch_angle.to_radians();
    let rad_azimuth = azimuth_angle.to_radians();

    // Calculate initial velocity components
    let v_x = velocity * rad_launch.cos() * rad_azimuth.cos();
    let v_y = velocity * rad_launch.sin();
    let v_z = velocity * rad_launch.cos() * rad_azimuth.sin();

    for i in 0..((total_time / time_step) as usize) {
        let t = i as f64 * time_step;
        let x = v_x * t; // x component
        let z = v_z * t; // z component
        let r = (x * x + z * z).sqrt(); // horizontal distance (ground projection)
        let y = v_y * t - 0.5 * g * t * t;
        if y < 0.0 {
            break;
        }
        points.push((r, y));
    }
    TwoDimFlightPath { points }
}
