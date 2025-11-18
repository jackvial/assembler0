include <BOSL2/std.scad>

h = 65;
r1 = 55;
r2 = 35;
wall = 5;
shaft_r = 6.5;
top_h = 14;
ep = 0.1;
motor_w = 45;




module base_cone() {
  // Method 1: Using diff() (BOSL2's difference operation)
  diff() {
    cyl(h=h, r1=r1, r2=r2) {
      tag("remove")
        cyl(h=h + 1, r1=r1 - wall, r2=r2 - wall);
    }
  }
}

module base_top() {
  tube(h=top_h, or=r2, ir=shaft_r + 0.5, anchor=TOP);
  translate([0, 0, -(top_h / 2)]) {
    // ball bearing lip
    tube(h=top_h / 2, or=r, ir=shaft_r, anchor=TOP);
  }
}

module cut_away() {
    // motor main cutaway 
    translate([-motor_w, 0, -(h+ep)]) {
      cuboid([motor_w, motor_w, h - top_h], anchor=BOTTOM);
      translate([0, 0, h - (top_h - 4)]) {
        cuboid([motor_w, motor_w, top_h], anchor=BOTTOM);
      }

      // motor shaft hole
      translate([18, 0, h - top_h]) {
        tube(h=top_h + 1, or=10, ir=0, anchor=BOTTOM);
      }
    }
}

module main(){
    difference() {
        union() {
            translate([0, 0, -32.5]) {
                base_cone();
            }
            base_top();
        }
        
        cut_away();
    }

}

main();