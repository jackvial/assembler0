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

module main() {
    writ_roll();
    hull() {
        handle();
    }
    // handle();
}

main();