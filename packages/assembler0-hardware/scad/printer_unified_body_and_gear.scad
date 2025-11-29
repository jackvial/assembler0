module body() {
    translate([-160, 390, 22])
        import(file = "../stl/community_arm/main_body_dual_v2.stl");
}

module gear() {
    color("red")
        translate([-100.5, 48.5 , 1.6])
            import(file = "../stl/community_arm/robot_belt_arm rotategear.stl");
}

module main() {
    body();
    gear();
}

main();