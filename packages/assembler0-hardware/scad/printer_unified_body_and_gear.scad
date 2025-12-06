module body() {
    // color("red")
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

module limit_switch() {
    color("blue")
    import(file = "../stl/creality_liimit_switch.stl");
}


module main() {
    body();
    gear();
    // endstop();
    
    
    // Lower shank limit switch
    translate([-34, -10, 62]) {
        rotate([-90, 45, 0]) {
            limit_switch();
        }
    }
    
    // Upper shank limit switch
    translate([-27, 9, 30]) {
        rotate([-90, 0, -90]) {
            limit_switch();
        }
    }
}

main();