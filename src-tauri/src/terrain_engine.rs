// WRONG I think the coolest way to do a golf course is to try a generative prompt an aerial view
// of the displacement map represententing the elevations of the golf course.
struct HoleTerrain {
    indices: Vec<u32>,
    vertices: Vec<f32>,
    normals: Vec<f32>,
    uvs: Vec<f32>,
}

fn generate_terrain(
    par: u8,
    hole_to_tee_xz_variance: f64,
    hole_to_tee_xy_variance: f64,
    flatness_coefficient: f64,
    gender: PlayerGender,
) -> HoleTerrain {
    let par_to_distance_from_hole_map = if gender == PlayerGender::Male {
        PAR_TO_DISTANCE_FROM_HOLE_MAP_MEN
    } else {
        PAR_TO_DISTANCE_FROM_HOLE_MAP_WOMEN
    };
    let distance_from_hole = par_to_distance_from_hole_map[&par];
}
