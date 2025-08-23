
// Koch gripper with the claw lobbed off
translate([0, 0, 1]) {
    difference() {
        translate([-230, 0, 37]) {
            import("../stl/Follower_Gripper_Static_Part.STL");
        }
       
        translate([-33, -43, -15]) {
            cube([50, 50, 50]);
        }
   }
}