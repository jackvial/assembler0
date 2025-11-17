include <BOSL2/std.scad>
include <BOSL2/gears.scad>

r = 55;
h=65;
shaft_r=6.5;
top_h = 14;
ep=0.1;
motor_w = 45;

module base() {
    difference() {
        union() {
            tube(h=h, or=r, ir=r-5, anchor=BOTTOM);
            translate([0, 0, h]) {
                tube(h=top_h, or=r, ir=shaft_r+0.5, anchor=TOP);
                translate([0, 0, -(top_h/2)]) {
                    // lip
                    tube(h=top_h/2, or=r, ir=shaft_r, anchor=TOP);
                }
            }
        }
        translate([-40, 0, -ep]) {
            cuboid([motor_w, motor_w, h-top_h], anchor=BOTTOM);
        }
    }
}

module main() {
    base();
}

main();
