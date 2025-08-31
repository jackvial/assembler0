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
    translate([-11, -40, 0]) {
        cube([22, 40, 6]);
    }
    translate([0, -40, 0]) {
        cylinder(h=plate_thickness, r=plate_radius);
    }
}

module trigger_assembly() {
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
    
    handle_length = 60;
    translate([0, -40, 0]) {
        translate([0, 0, -20]) {
            cylinder(h = 20, r = 5, r2 = 11, $fn = 64);
        }
        translate([0, 0, -handle_length]) {
            cylinder(h = handle_length, r = 4, r2 = 6, $fn = 64);
        }
    }
}

module writ_roll() {
    difference() {
        import("../stl/Wrist_Roll_SO101_leader.stl");
        translate([-30, -10, 38]) {
            cube([25, 20, 6]);
        }
    }
}

module handle() {
        translate([-35.19, -4.5, 37]) {
            cube([16, 20, 0.1]);
            // translate([19.6, -12, 1]) {
            //     cube([10, 10, 0.1]);
            // }
            rotate([90, 0, 0]) {
                translate([8, 0, -70]) {
                    cylinder(r=8, h=50);
                }
            }
        }
}

module handle_readymade() {
    import("../stl/Handle_SO101.stl");
}

module wrist_roll_assembly() {
    writ_roll();
    rotate([90, 0, -90]) {
        translate([10, 49, -40]) {
            handle_readymade();
        }
    }
    hull() {
    
        // Intersection 1 - handle and mask
        intersection() {
            rotate([90, 0, -90]) {
                translate([10, 49, -40]) {
                    handle_readymade();
                }
            }
            translate([-27, -10, 36]) {
                cube([30, 30, 30]);
            }
        }
        
        // Intersection 2 - wrist roll and mask
        intersection() {
            writ_roll();
            translate([-50, -50, 36]) {
                cube([100, 100, 30]);
            }
        }
        
    }
}

module assembly() {
    wrist_roll_assembly();
    
    // translate([20, -18, 20]) {
    //     rotate([90, 180, 0]) {
    //         trigger_assembly();
    //     }
    // }
}

assembly();