// ========================= Parameters =========================
// Wrist roll dimensions
wrist_width = 51;
wrist_depth = 38;
wrist_origin_x = -wrist_width/2;  // Calculated to center assembly around x=0
wrist_origin_y = -15;

// Plate and structure dimensions
plate_thickness = 2; // thickness of all small plates
side_plate_thickness = 6;
top_plate_height = 6;
side_plate_height = 65;
large_counter_sink_depth = 5;
side_plate_height_from_top = 10;

// Screw hole dimensions
screw_hole_radius = 1.8;
top_plate_screw_radius = 1.8;
counter_sink_radius = 3;
top_plate_center_hole_radius = 3;
top_plate_screw_offset = 6.9;

// Extruder mounting dimensions
extruder_offset_from_front = 5;
extruder_screw_spacing = 9.5; // distance from center
extruder_front_row_offset = 8;
extruder_back_row_offset = 18;
extruder_center_hole_radius = 3;
extruder_cradle_thickness = 3;
mount_screw_access_cutaway = 10;
extruder_cradle_height = 60;

// Hotend mounting dimensions
hotend_hole_radius = 6.5;
hotend_hex_radius = 10;
hotend_cradle_thickness = 8;
screw_access_hole_radius = 2.4;

// Boolean difference offset
boolean_offset = -0.1;

$fn = 64; // global smoothness for all circular geometry
$render_vitamines = false;
$extruder_width = 38;


module wrist_roll() {
  translate([-wrist_width/2, wrist_origin_y, 4]) {
    
    // Top plate
    difference() {
        // Jut out to clear wrist roll holder
        union() {
            translate([wrist_width/2, wrist_depth/2, -5]) {
                cylinder(h=5, r=12);
            }
            // cube([wrist_width, wrist_depth,top_plate_height]);
        }
        
        // hole for filament
        // Filament will need to bend a bit forward to clear the wrist roll holder
        // todo(jack): Need to round this hole to reduce friction with the filament
        translate([wrist_width/2, 34, -6]) {
            cylinder(h=16, r=extruder_center_hole_radius);
        }
        
        // Large counter sink
        translate([wrist_width/2, wrist_depth/2, 3]) {
                cylinder(h=large_counter_sink_depth, r=10);
         }
        
        // hole at center
        translate([wrist_width/2, wrist_depth/2, - (large_counter_sink_depth + 0.2)]) {
            cylinder(h=3, r=top_plate_center_hole_radius);
        }
        
        // Four holes in a circular pattern around center
        for (angle = [45, 45 + 90, 45 + 180, 45 + 270]) {
            translate([wrist_width/2, wrist_depth/2, -5]) {
                rotate([0, 0, angle]) {
                    translate([top_plate_screw_offset, 0, boolean_offset]) {
                        cylinder(h=top_plate_height + 0.2, r=top_plate_screw_radius);
                        translate([0, 0, 4]) {
                            cylinder(h=6.2, r=counter_sink_radius);
                        }
                    }
                }
            }
        }
    }
  }
}

module main() {
  wrist_roll();
}

main();