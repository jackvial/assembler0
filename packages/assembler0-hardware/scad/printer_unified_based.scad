include <BOSL2/std.scad>

$render_vitamines = false;

module body() {
  translate([-100, 50, 27]) {
    import(file="../stl/community_arm/robot_belt_arm socket.stl");
  }
}

module leg() {
  color("red")
    import(file="../stl/ftobler_arm/files/leg_45mm.stl");
}

module basering() {
  color("green")
    difference() {
      import(file="../stl/community_arm/robot_belt_arm basering.stl");
      translate([60, -49, -70]) {
        cuboid([30, 43, 10], anchor=CENTER);
      }
    }
}

module limit_switch() {
  color("blue")
    import(file="../stl/creality_liimit_switch.stl");
}

module limit_switch_mount() {
  translate([0, 0, 1.9]) {
    cuboid([20, 5, 7.1], anchor=BOTTOM + FRONT);
  }
  difference() {
    translate([0, 0, 1.9]) {
      cuboid([20, 2.6, 27], anchor=BOTTOM, rounding=1.6, except=[BOTTOM, FRONT, BACK]);
    }

    // big solder ends
    translate([3, 11, 25.4]) {
      rotate([90, 0, 0]) {
        cylinder(r=2, h=20, $fn=32);
      }
    }

    translate([3, 11, 20.6]) {
      rotate([90, 0, 0]) {
        cylinder(r=2, h=20, $fn=32);
      }
    }

    translate([3, 11, 15.8]) {
      rotate([90, 0, 0]) {
        cylinder(r=2, h=20, $fn=32);
      }
    }

    // More small solder ends
    translate([6, 11, 23]) {
      rotate([90, 0, 0]) {
        cylinder(r=1.3, h=20, $fn=32);
      }
    }

    translate([6, 11, 18]) {
      rotate([90, 0, 0]) {
        cylinder(r=1.3, h=20, $fn=32);
      }
    }

    // small solder ends
    translate([-4.8, 1, 15.2]) {
      cuboid([2.4, 5, 8], anchor=BOTTOM);
    }

    // screw hole 1
    translate([-7, 10, 11.65]) {
      color("green")
        rotate([90, 0, 0]) {
          cylinder(r=1.6, h=20, $fn=32);
        }
    }

    // screw hole 2
    translate([-7, 10, 26.65]) {
      color("green")
        rotate([90, 0, 0]) {
          cylinder(r=1.6, h=20, $fn=32);
        }
    }
  }

  translate([-5, 5, 1.9]) {
    cube([10, 10, 5], anchor=BOTTOM);
  }
}

module cut_old_mount() {
  // color("green")
  cube([20, 30, 30]);
}

module main_body() {
  // color("red")
  translate([-160, 390, 22])
    import(file="../stl/community_arm/main_body_dual_v2.stl");
}

module gear() {
  // color("red")
  translate([-100.5, 48.5, 1.6])
    import(file="../stl/community_arm/robot_belt_arm rotategear.stl");
}

module main() {
  translate([-42, -31.4, -2.1]) {
    limit_switch_mount();
  }

  difference() {
    body();
    translate([-48, -40, 4.8]) {
      cut_old_mount();
    }
  }

  translate([-42, -30, 17]) {
    rotate([0, 90, 90]) {
      if ($render_vitamines) {
        limit_switch();
      }
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

  if ($render_vitamines) {
    translate([0, 0, 25]) {
      rotate([0, 0, 200]) {
        main_body();
        gear();
      }
    }
  }
}

main();
