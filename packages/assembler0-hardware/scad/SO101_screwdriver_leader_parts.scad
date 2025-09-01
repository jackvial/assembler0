plate_radius = 10.5;
plate_thickness = 6;
screw_hole_radius = 1.8;
countersink_radius = 3;
screw_hole_offset = 6.9;
level_length = 25;

module plate_screw_hole() {
  cylinder(h=plate_thickness, r=screw_hole_radius, $fn=32);
  translate([0, 0, 3.6]) {
    cylinder(r=countersink_radius, h=10, $fn=32);
  }
}

module plate() {
  cylinder(h=plate_thickness, r=plate_radius);
  translate([-plate_radius, -level_length, 0]) {
    cube([plate_radius * 2, level_length, 6]);
  }
  translate([0, -level_length, 0]) {
    cylinder(h=plate_thickness, r=plate_radius);
  }
}

module trigger_assembly() {
  difference() {
    plate();

    translate([0, 0, -1]) {
      cylinder(r=3, h=10);
    }

    // Screw holes with cylinders above them
    translate([0, screw_hole_offset, -1]) {
      plate_screw_hole();
    }

    translate([0, -screw_hole_offset, -1]) {
      plate_screw_hole();
    }

    translate([screw_hole_offset, 0, -1]) {
      plate_screw_hole();
    }

    translate([-screw_hole_offset, 0, -1]) {
      plate_screw_hole();
    }
  }

  handle_length = 60;
  translate([0, -level_length, 0]) {
    translate([0, 0, -20]) {
      cylinder(h=20, r=5, r2=plate_radius, $fn=64);
    }
    translate([0, 0, -handle_length]) {
      cylinder(h=handle_length, r=4, r2=6, $fn=64);
    }
  }
}

module so101_writ_roll() {
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
    rotate([90, 0, 0]) {
      translate([8, 0, -70]) {
        cylinder(r=8, h=50);
      }
    }
  }
}

module so101_handle() {
  import("../stl/Handle_SO101.stl");
}

module wrist_roll_assembly() {
  so101_writ_roll();
  rotate([90, 0, -90]) {
    translate([10, 49, -40]) {
      so101_handle();
    }
  }

  // Create a hull over intersections to smoothly connect the handle
  // to the wrist roll
  hull() {

    // Intersection 1 - wrist roll and mask
    // Duplicate the wrist roll and intersect with masking cube
    intersection() {
      so101_writ_roll();
      translate([-50, -50, 36]) {
        cube([100, 100, 30]);
      }
    }

    // Intersection 2 - handle and mask
    // Duplicate the handle and intersect with "masking" cube
    intersection() {
      rotate([90, 0, -90]) {
        translate([10, 49, -40]) {
          so101_handle();
        }
      }
      translate([-27, -10, 36]) {
        cube([30, 30, 30]);
      }
    }
  }
}

module assembly() {
  wrist_roll_assembly();

  translate([20, -18, 24]) {
    rotate([90, 180, 0]) {
      trigger_assembly();
    }
  }
}

assembly();
