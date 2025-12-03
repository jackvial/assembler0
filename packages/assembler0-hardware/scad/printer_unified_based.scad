include <BOSL2/std.scad>
module body() {
    translate([-100, 50, 27]) {
        import(file = "../stl/community_arm/robot_belt_arm socket.stl");
    }
}

module leg() {
    color("red")
    import(file = "../stl/ftobler_arm/files/leg_45mm.stl");
}

module basering() {
    color("green")
    import(file = "../stl/community_arm/robot_belt_arm basering.stl");
}

module limit_switch() {
    color("blue")
    import(file = "../stl/creality_liimit_switch.stl");
}

module limit_switch_mount() {
    // TODO: round the two top corners
    difference() {
        cuboid([20, 2.6, 29], anchor=BOTTOM);
        
        // screw hole 1
        translate([-7, 10, 11.5]) {
            color("green")
            rotate([90, 0, 0]) {
                cylinder(r=1.6, h=20, $fn=32);
            }
        }
        
        // screw hole 2
        translate([-7, 10, 26.5]) {
            color("green")
            rotate([90, 0, 0]) {
                cylinder(r=1.6, h=20, $fn=32);
            }
        }
    }
    
    translate([-5, 5, 0]) {
        cube([10, 10, 4.9], anchor=BOTTOM);
    }
}

module cut_old_mount() {
    // color("green")
    cube([20, 30, 30]);
}

module main() {
    difference() {
        body();
        translate([-48, -40, 4.8]) {
            cut_old_mount();
        }
    
    }
    translate([-42, -31.4, -0.1]) {
        limit_switch_mount();
    }
    
    translate([-42, -30, 19]) {
        rotate([0, 90, 90]) {
            limit_switch();
        }
    }
    
    translate([-100, 50, 18]) {
        basering();
    }
    
    // leg 1
    rotate([90, 0, 90]) {
        translate([-29, -6.2, 0]) {
            leg();
        }
    }
    
    // leg 2
    rotate([90, 0, 180]) {
        translate([-30, -6.2, 1]) {
            leg();
        }
    }
    
    // leg 3
    rotate([90, 0, -90]) {
        translate([-31, -6.2, 0]) {
            leg();
        }
    }
}

main();