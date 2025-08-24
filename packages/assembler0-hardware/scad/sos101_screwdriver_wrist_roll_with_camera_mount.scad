// ========================= Parameters =========================
plate_thickness = 2;                // thickness of all small plates
screw_r         = 1.4;              // radius for M2.5 screw holes
mount_angle_1   = 50;               // first camera bracket angle (deg)
mount_angle_2   = 110;              // second camera bracket angle (deg)
mount_angle_3   = 40;               // third camera bracket angle (deg) 
socket_cut_size = [12, 24, 4];       // cut-out that clears the flat cable socket
cube_cut_size   = [50, 50, 70];     // large cube used to lob off the claw
cube_cut_pos    = [-40, -25, 38];   // position of cube_cut
follower_offset = [-222, 50, 37];   // translation for imported STL
mount_origin    = [-30, 0, 8];     // where the camera mount attaches
mount_plate_size = [40, 38, plate_thickness];
gusset_size     = 8;                // side length of the strengthening gussets
gusset_height   = 10;               // height of the corner gussets
// screw-hole pattern (XY translation); Z comes from each element's third value
screw_pattern = [
    [7,  5, -1],
    [7, 33, -1],
    [35, 5, -1],
    [35, 33, -1]
];

$fn        = 64;    // global smoothness for all circular geometry
$fn_screws = 32;    // finer tessellation for small screw holes
$render_vitamines = true;

// ========================= Utility Modules =========================

module plate(size) {
    cube(size, center = false);
}
module screw_hole(h, r = screw_r) {
    cylinder(h = h, r = r, $fn = $fn_screws);
}

module socket_cut() {
    cube(socket_cut_size, center = false);
}

// module follower_gripper() {
//     import("../stl/Follower_Gripper_Static_Part.STL");
// }

module follower_gripper() {
    import("/Users/jackvial/Code/assembler0/packages/assembler0-hardware/stl/Wrist_Roll_Follower_SO101.stl");
}

// ========================= Assemblies =========================
module mounting_plate() {
    difference() {
        plate(mount_plate_size);
        // socket clearance
        // translate([2, 7, -1]) {
        //     socket_cut();
        // }
        
        translate([27, 7, -1]) {
            socket_cut();
        }
        // screw holes in the four corners
        for (p = screw_pattern) translate(p) screw_hole(plate_thickness + 2);
    }
}

module camera_mount() {
    // first small plate
    // rotate([0, mount_angle_1, 0]) plate([15, 29, plate_thickness]);

    // The rest of the mount is transformed together, preserving the original nesting.
    translate([9.3, 0, -9.5]) {
        // second small plate
        // rotate([0, mount_angle_2, 0])
        //     plate([10, 29, plate_thickness]);

        // main mounting plate with holes and socket cut
        translate([-3.5, -4.5, -9.5])
            rotate([0, mount_angle_3, 0]) {
                mounting_plate();
                
                // Camera line of sight
                if ($render_vitamines) {
                    translate([(mount_plate_size[0] / 2) + plate_thickness, (mount_plate_size[1] / 2), -100]) {
                        cylinder(h = 100, r = 1.4);
                    }
                }
            }
    }
}

// ========================= Top-level Model =========================
    
// Drill bit to align the camera mount
if ($render_vitamines) {
    translate([10, -30, 25]) {
        rotate([0, -90, 90]) {
            cylinder(h = 57, r = 1);
        }
    }
}

difference() {
    // imported follower gripper body
    // translate(follower_offset) { 
    follower_gripper();
    // }

    // cube used to remove claw section
    translate(cube_cut_pos) { 
        cube(cube_cut_size, center = false); 
    }
}

// camera mount assembly
translate(mount_origin) {
    rotate([90, 0, 180]) {
        camera_mount();
    }
}