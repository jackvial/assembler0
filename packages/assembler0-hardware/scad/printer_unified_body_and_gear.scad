module body() {
    color("red")
    translate([-160, 390, 22])
        import(file = "../stl/community_arm/main_body_dual_v2.stl");
}

module gear() {
    // color("red")
        translate([-100.5, 48.5 , 1.6])
            import(file = "../stl/community_arm/robot_belt_arm rotategear.stl");
}

module endstop() {
    translate([-100, 48.5, 1.5]) {
        import("../stl/community_arm/robot_belt_arm_endstop.stl");
    }
    
    translate([-24.5, -26.51, 0]) {
        cube([3.5, 52.1, 30]);
    }
    
    translate([-24.5, 18.5, 30]) {
        cube([3.5, 7, 11.5]);
    }
    
    translate([-24.5, -26.51,30]) {
        cube([3.5, 7, 11.5]);
    }
}

module main() {
    body();
    gear();
    endstop();
}

main();