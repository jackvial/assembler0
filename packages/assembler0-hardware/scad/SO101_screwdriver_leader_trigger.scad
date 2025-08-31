plate_radius = 11;
plate_thickness = 6;
chuck_height = 22;
chuck_radius = 4.2;
chuck_base_radius = 7.4;  // Wider base for the cone
screw_hole_radius = 1.8;
countersink_radius = 3;
// screw_hole_offset = 6.44;
screw_hole_offset = 6.9;
top_cylinder_height = chuck_height + 2;  // Height of cylinders above screw holes
top_cylinder_radius = 2.8;  // Radius of cylinders above screw holes

module plat_screw_hole() {
    cylinder(h=plate_thickness, r=screw_hole_radius, $fn=32);
    translate([0, 0, 3.6]) {
        cylinder(r=countersink_radius, h=10, $fn=32);
    }
}

module magnet_cavity() {
    cylinder(h=10, r=3.4);
}

module plate() {
    cylinder(h=plate_thickness, r=plate_radius);
    translate([-11, -30, 0]) {
        cube([22, 30, 6]);
    }
    translate([0, -30, 0]) {
        cylinder(h=plate_thickness, r=plate_radius);
    }
}

module main() {
    difference() {
    plate();
    
    translate([0, 0, -1]) {
        cylinder(r=3, h=10);
    }
    
    // Screw holes with cylinders above them
    translate([0, screw_hole_offset, -1]) {
        plat_screw_hole();
    }
    
    translate([0, -screw_hole_offset, -1]) {
        plat_screw_hole();
    }

    translate([screw_hole_offset, 0, -1]) {
        plat_screw_hole();
    }
    
    translate([-screw_hole_offset, 0, -1]) {
            plat_screw_hole();
        }
    }
    
    // cylinder(h = 6, r = 10, $fn = 64);
    translate([0, -30, 0]) {
        translate([0, 0, -20]) {
            cylinder(h = 20, r = 5, r2 = 11, $fn = 64);
        }
        translate([0, 0, -40]) {
            cylinder(h = 40, r = 4, r2 = 6, $fn = 64);
        }
    }
}

main();