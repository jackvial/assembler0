include <BOSL2/std.scad>

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

module limit_switch_mount_upper_shank() {
    // cuboid([20, 5, 9], anchor=BOTTOM+FRONT);
    difference() {
        translate([0, 0, 35.8]) {
            cuboid([20, 2.6, 52], anchor=TOP, except=[BOTTOM, FRONT, BACK]);
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
    
    // translate([-5, 5, 0]) {
    //     cube([10, 10, 4.9], anchor=BOTTOM);
    // }
}

module limit_switch_mount_lower_shank() {
    // cuboid([20, 5, 9], anchor=BOTTOM+FRONT);
    difference() {
        translate([0, 0, 29]) {
            cuboid([20, 2.6, 20], anchor=TOP, rounding=1.6, except=[BOTTOM, FRONT, BACK]);
            // Connect cross bar to lower shank limit switch
            translate([0, 0, -12]) {
                color("green")
                rotate([0, 45, 0]) {
                    cuboid([11, 2.6, 30], anchor=TOP);
                }
            }
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
            cuboid([2.4, 6, 8], anchor=BOTTOM);
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
                cylinder(r=1.6, h=20, $fn=32, anchor=BOTTOM);
            }
        }
    }
    
    // translate([-5, 5, 0]) {
    //     cube([10, 10, 4.9], anchor=BOTTOM);
    // }
}


module main() {
    body();
    gear();
    
    
    // Mount side 1
    translate([-24, 22.5, 40]) {
        color("red")
        cuboid([8, 6, 20], anchor=TOP);
    }
    
    // Mount side 2
    translate([-24, -23.5, 40]) {
        color("red")
        cuboid([8, 6, 20], anchor=TOP);
    }
    
    // Lower shank limit switch
    translate([-34, -10, 62]) {
        translate([13.5, -1.6, -13.5]) {
            rotate([0, -45, 0]) {
                limit_switch_mount_lower_shank();
            }
        }
        rotate([-90, 45, 0]) {
            // limit_switch();
        }
        
        // Fillet
        translate([5, -0.3, -31.5]) {
            color("red")
            rotate([0, 90, 90]) {
                fillet(r=2, h=2.6, anchor=TOP);
            }
        }
    }
    
    // Upper shank limit switch
    translate([-27, 9, 30]) {
        translate([-1.4, -19.2, 0]) {
            rotate([0, -90, -90]) {
                limit_switch_mount_upper_shank();
            }
        }
        rotate([-90, 0, -90]) {
            // limit_switch();
        }
    }
}

main();