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

module main() {
    body();
    
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