enum PlayerGender {
    Male,
    Female,
}

// https://www.usga.org/content/usga/home-page/handicapping/roh/Content/rules/Appendix%20F%20Establishing%20Par.htm
const PAR_TO_DISTANCE_FROM_HOLE_MAP_MEN: Map<u8, [f64; 2]> = Map::from([
    (3, [0.0, 240.0]),
    (4, [220.0, 450.0]),
    (5, [410.0, 650.0]),
    (6, [610.0, 1000.0]),
]);

const PAR_TO_DISTANCE_FROM_HOLE_MAP_WOMEN: Map<u8, [f64; 2]> = Map::from([
    (3, [0.0, 200.0]),
    (4, [180.0, 380.0]),
    (5, [340.0, 550.0]),
    (6, [520.0, 900.0]),
]);
