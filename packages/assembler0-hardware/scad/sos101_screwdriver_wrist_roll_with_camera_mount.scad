module follower_gripper() {
    import("../stl/Wrist_Roll_Follower_SO101.stl");
}

module main() {
    difference() {
        follower_gripper();
        translate([-40, -30, 38]) {
            cube([60, 60, 80]);
        }
    }
}

main();