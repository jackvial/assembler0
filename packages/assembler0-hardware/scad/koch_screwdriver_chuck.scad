plate_radius = 9;
plate_thickness = 2;
chuck_height = 22;
chuck_radius = 4.2;
chuck_base_radius = 7.4;  // Wider base for the cone
screw_hole_radius = 1.4;
screw_hole_offset = 5.75;
top_cylinder_height = chuck_height + 2;  // Height of cylinders above screw holes
top_cylinder_radius = 2.3;  // Radius of cylinders above screw holes

module solid_parts() {
    // Chuck plate
    cylinder(h=plate_thickness, r=plate_radius);
    
    // Chuck shaft
    translate([0, 0, plate_thickness]) {    
        cylinder(h=chuck_height, r1=chuck_base_radius, r2=chuck_radius);
    }
}

module plat_screw_hole() {
    cylinder(h=plate_thickness + 2, r=screw_hole_radius);
}

module magnet_cavity() {
    cylinder(h=10, r=3.4);
}

difference() {
    solid_parts();
    
    translate([0, 0, plate_thickness]) {
        cylinder(h=chuck_height + 1, r=2.5, $fn=6);
    }
    
    // Screw holes with cylinders above them
    translate([0, screw_hole_offset, -1]) {
        plat_screw_hole();
    }
    translate([0, screw_hole_offset, plate_thickness]) {
        cylinder(h=top_cylinder_height, r=top_cylinder_radius);
    }
    
    translate([0, -screw_hole_offset, -1]) {
        plat_screw_hole();
    }
    translate([0, -screw_hole_offset, plate_thickness]) {
        cylinder(h=top_cylinder_height, r=top_cylinder_radius);
    }
    
    translate([screw_hole_offset, 0, -1]) {
        plat_screw_hole();
    }
    translate([screw_hole_offset, 0, plate_thickness]) {
        cylinder(h=top_cylinder_height, r=top_cylinder_radius);
    }
    
    translate([-screw_hole_offset, 0, -1]) {
        plat_screw_hole();
    }
    translate([-screw_hole_offset, 0, plate_thickness]) {
        cylinder(h=top_cylinder_height, r=top_cylinder_radius);
    }
    
    translate([0, 0, plate_thickness]) {
        magnet_cavity();
    } 
}
