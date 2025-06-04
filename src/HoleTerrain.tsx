import React, { useMemo } from "react";
import * as THREE from "three";

export interface HoleTerrainProps {
  distanceFromHole: number;
}

const HoleTerrain: React.FC<HoleTerrainProps> = ({ distanceFromHole }) => {
  // Create the terrain geometry when the distance changes.
  const geometry = useMemo(() => {
    const geom = new THREE.BufferGeometry();

    // Define the dimensions based on the distance parameter.
    // We create an elongated grid: length equals distanceFromHole, and width is half that.
    const length = distanceFromHole;
    const width = distanceFromHole / 2;
    // Use a grid subdivision that offers sufficient detail.
    const segmentsX = 20; // divisions along the width
    const segmentsZ = 20; // divisions along the length

    const vertices: number[] = [];
    const normals: number[] = [];
    const uvs: number[] = [];
    const indices: number[] = [];

    // Height function to simulate a slightly undulating fairway with a dip near the hole.
    // The "hole" is assumed to be at the far end (z = length) and centered along x = 0.
    function height(x: number, z: number): number {
      // A Gaussian dip centered at the hole location.
      const dipIntensity = 1.0; // maximum depth of the depression
      const dipWidth = width / 2; // controls the width of the dip
      const centerX = 0;
      const centerZ = length;
      const distSq =
        (x - centerX) * (x - centerX) + (z - centerZ) * (z - centerZ);
      const dip = -dipIntensity * Math.exp(-distSq / (2 * dipWidth * dipWidth));

      // Add a mild undulation over the whole fairway for natural variation.
      const undulation =
        0.2 *
        Math.sin((x / width) * Math.PI * 2) *
        Math.sin((z / length) * Math.PI);

      return dip + undulation;
    }

    // Generate vertices, normals, and UV coordinates.
    // x will range from -width/2 to width/2; z from 0 (tee) to length (hole).
    for (let iz = 0; iz <= segmentsZ; iz++) {
      const z = (iz / segmentsZ) * length;
      for (let ix = 0; ix <= segmentsX; ix++) {
        const x = (ix / segmentsX) * width - width / 2;
        const y = height(x, z);
        vertices.push(x, y, z);
        // Start with an upward normal; this will be refined by computeVertexNormals().
        normals.push(0, 1, 0);
        uvs.push(ix / segmentsX, iz / segmentsZ);
      }
    }

    // Create indices for the grid.
    for (let iz = 0; iz < segmentsZ; iz++) {
      for (let ix = 0; ix < segmentsX; ix++) {
        const a = ix + (segmentsX + 1) * iz;
        const b = ix + (segmentsX + 1) * (iz + 1);
        const c = ix + 1 + (segmentsX + 1) * (iz + 1);
        const d = ix + 1 + (segmentsX + 1) * iz;
        // Two triangles per grid square
        indices.push(a, b, d);
        indices.push(b, c, d);
      }
    }

    geom.setIndex(indices);
    geom.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(vertices, 3)
    );
    geom.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
    geom.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));

    // Recompute vertex normals for accurate lighting.
    geom.computeVertexNormals();

    return geom;
  }, [distanceFromHole]);

  // Render the geometry as a mesh with a standard green material.
  return (
    <mesh geometry={geometry} receiveShadow>
      <meshStandardMaterial color="#228B22" side={THREE.DoubleSide} />
    </mesh>
  );
};

export default HoleTerrain;
