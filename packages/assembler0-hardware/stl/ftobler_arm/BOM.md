# Bill of Materials – 3D Printed Robot Arm (Florin Tobler, 2016 Design)

Below is a comprehensive Bill of Materials (BOM) for the 3D-printed robot arm designed by Florin Tobler in 2016. This list includes all 3D printed parts as well as the hardware and electronics required to assemble the arm. The BOM is formatted for builders in the United States, with example purchase links (favoring Amazon or US-stock suppliers for fast shipping) provided where applicable. Quantities needed are indicated, and buying in bulk (or kit form) is recommended for cost savings and spares.

## 3D Printed Parts (STL Components)

Print each of the following parts in plastic. Quantities refer to number of prints required. [[1]][[2]]

| Part Name | Quantity | Notes |
|-----------|----------|-------|
| Base | 1 | |
| Stabilizer | 1 | |
| Stabilizer_endstop | 1 | |
| GearBig | 2 | |
| GearSmall | 3 | |
| Lever | 1 | |
| LowerShank | 1 | |
| UpperShank | 1 | |
| Manipulator | 1 | |
| Pleuel | 1 | |
| Pleuel_bend | 2 | |
| Triplate | 1 | |
| GripperBase | 1 | |
| GripperFinger | 2 | |
| GripperHolePlate | 1 | |
| Socket | 1 | |
| GearRotate | 1 | Ensure a tight fit when printing |
| Leg | 3 | Legs can be any preferred height |
| BaseRing | 1 | Optional, used at the base |

## Motors and Electronics

| Component | Quantity | Description | Notes |
|-----------|----------|-------------|-------|
| NEMA 17 Stepper Motors | 3 | Standard NEMA17 bipolar stepper motors (1.8° step, ~42 mm frame). These drive the primary joints of the arm[[3]]. | A pack of 3 high-torque NEMA17 motors[[4]] (common in 3D printer kits) can be used. |
| 28BYJ-48 Stepper Motor (5 V) | 1 | A small 5V unipolar stepper used for one axis (e.g. base rotation or gripper)[[3]]. | 28BYJ-48 stepper with ULN2003 driver board (often sold in 5-packs)[[5]]. |
| Arduino Mega 2560 | 1 | Microcontroller board to control the arm. An Arduino Mega 2560 (or compatible) is used as the main controller. | |
| RAMPS 1.4 Shield | 1 | RepRap RAMPS 1.4 shield that plugs into the Mega 2560, providing stepper driver sockets and power interface. | Often available in kits with the Mega and drivers.[[6]] |
| Stepper Drivers (A4988 or DRV8825) | 3 | Stepper driver modules to plug into the RAMPS for each NEMA17 motor[[3]]. | Either A4988 or DRV8825 drivers can be used (3 needed for 3 motors). Many RAMPS+Mega kits include 5× A4988 drivers and heatsinks[[6]], which covers the 3 required (with spares). |
| Power Supply | 1 | Suitable DC power supply (e.g. 12 V) needed to drive the NEMA17 steppers via the RAMPS board. | Not explicitly in original BOM. Choose amperage based on motor current draw; a 12 V 5 A supply is a typical starting point for 3 steppers. |
| Microswitch (Optional) | 1 | Limit switch or endstop for the stabilizer_endstop mount. | Optional. The design has a "stabilizer_endstop" part to mount one, though a switch is optional. |
| Hookup Wires/Jumpers | As needed | For connecting motors and sensors. | |
| USB Cable | 1 | For programming the Arduino. | |

## Bearings and Other Mechanical Components

| Component | Quantity | Specifications | Description | Notes |
|-----------|----------|----------------|-------------|-------|
| 624ZZ Ball Bearings | 6 | 4 × 13 × 5 mm | Small double-shielded deep-groove ball bearings, used at joints and gear interfaces[[7]]. | A pack of 4 bearings (4 mm ID, 13 mm OD) is available[[8]]. |
| F686ZZ Flanged Ball Bearings | 10 | 6 × 13 × 5 mm | Flanged miniature bearings (flange ~15 mm) used in the arm's joints that require a flange to seat properly[[7]]. | These have 6 mm inner diameter and 13 mm outer, same 5 mm thickness, with a lip/flange. They are commonly sold in packs of 10[[9]], exactly the quantity needed. |
| 51105 Thrust Ball Bearing | 1 | 25 × 42 × 11 mm | A thrust bearing assembly to handle axial loads (25 mm bore, 42 mm outer diameter)[[10]]. | Used at the base rotation or major pivot to support the arm's weight. Example: SKF 51105 or equivalent thrust bearing[[11]]. Only one is needed. |
| M6 Threaded Rod | 1 | 80 mm length, M6 diameter | Metal threaded rod (stud) used as a shaft in one part of the arm (~3.15 inches). | You can purchase an M6 threaded rod and cut to length, or buy a pre-cut piece[[12]]. The original spec mentioned an M5 rod[[13]], but the updated count uses M6 hardware for robustness. |
| Shaft Couplers/Dowel Pins (if needed) | As needed | | For attaching the 28BYJ-48 motor or to align parts, if required. | The design primarily uses the above threaded rod and the motor shafts for rotation. In many cases, the 28BYJ-48 has a built-in geared shaft, and the NEMA17 motors will directly mount to printed gears. |

## Fasteners (Screws, Nuts, Washers, etc.)

A variety of metric screws, nuts, and washers are needed for assembly. The list below summarizes the quantities and types as given by the arm's designer[[14]][[15]]. It's wise to buy these in bulk or assortment packs (stainless steel or alloy steel preferred) rather than individually, to ensure you have extras and the proper lengths. For example, combination kits of M3/M4/M5 hardware are readily available[[16]], and small packs of M6 bolts can cover the larger pieces[[17]].

### M3 Fasteners

| Component | Quantity | Notes |
|-----------|----------|-------|
| M3 x 6 mm Screws | 16 | |
| M3 x 8 mm Screws | 21 | About 3 of these are used as set screws in gears[[18]] |
| M3 x 10 mm Screws | 4 | [[18]] |
| M3 Hex Nuts | 4 | [[14]] |
| M3 Washers (large OD) | 2 | Used in the gripper[[14]] |

### M4 Fasteners

| Component | Quantity | Notes |
|-----------|----------|-------|
| M4 x 10 mm Screws | 6 | [[19]] |
| M4 x 16 mm Screws | 11 | [[19]] |
| M4 x 25 mm Screws | 2 | [[19]] |
| M4 Hex Nuts | 8 | |
| M4 Washers | 14 | Use washers with small enough outer diameter to bear on the inner race of bearings[[20]] |

### M6 Fasteners

| Component | Quantity | Notes |
|-----------|----------|-------|
| M6 x 45 mm Bolts | 3 | Serve as pivot pins in some joints. Using locknuts or thread locker here is important for joints that rotate. If you cannot find 45 mm length easily, 50 mm could be used and cut down if needed.[[12]] |
| M6 Hex Nuts | 3 | |
| M6 Self-locking Nuts (nylon insert locknuts) | 3 | [[12]] |
| M6 Washers | 12 | Should have a small enough outer diameter to sit against the bearing's inner race when used as spacers/shims on the joints (to avoid clamping the outer race)[[21]] |

### Other Components

| Component | Quantity | Notes |
|-----------|----------|-------|
| Zip Ties | As needed | For cable management |
| Hookup Wire | As needed | For connecting motors, endstop, and power |
| Arduino/RAMPS Mounting Hardware | As needed | Spacers or standoffs if needed |
| 28BYJ-48 Motor Mounting Screws | As needed | Small screws for the 28BYJ-48 motor if it doesn't come with any |

### Buying Tips

For the smaller fasteners (M3, M4), consider an assorted kit that includes a range of lengths plus matching nuts and washers[[22]][[23]]. For example, a kit of M3/M4/M5 screws, nuts, and washers can cover most of these needs. The M6 hardware (bolts, rod, nuts) might not be in those kits, but you can purchase a set of M6 bolts which often include nuts and washers[[17]], or get them from a local hardware store if needed. Always get a few extra pieces beyond the exact count (in case of mistakes or if spares are needed). Washers are important to use as specified – especially wherever a bolt/nut tightens against a bearing, place the washer so it contacts only the inner race of the bearing (preventing it from binding the outer race)[[14]][[21]].

## Sources and References

- **Florin Tobler (2016), "RobotArm"** – Original project files and bill of materials. (Available via Thingiverse and documentation) [[24]][[10]]. This provided the basis for the parts list and printed components.
- **Demeter Project, Robotic Arm Unit Documentation** – Assembly guide referencing Florin Tobler's robot arm. Includes a detailed fastener list[[14]][[25]] and assembly tips.
- **Example product listings (Amazon)** for various components: 624ZZ bearings (4×13×5mm)[[8]], F686ZZ flanged bearings[[9]], Thrust bearing 51105[[11]], NEMA17 stepper motors (pack)[[4]], 28BYJ-48 stepper motor kit[[5]], Arduino Mega + RAMPS + drivers kit[[6]], Metric nuts and bolts assortment[[16]], M6 bolt set[[17]]. These are representative links for convenience; equivalent components from other US-based suppliers can also be used.

## Reference Links

[[1]] [[2]] [[3]] [[7]] [[10]] [[13]] [[24]] Robot Geometry | PDF | Equipment | Machines  
https://www.scribd.com/document/401588256/Robot-Geometry

[[4]] 3pcs Nema 17 Bipolar Stepper Motor Kit 92oz.in 2.1a 4-lead 60mm ...  
https://www.amazon.com/Bipolar-Stepper-Motor-92oz-4-lead/dp/B00QGBUO1C

[[5]] Amazon.com : GeeekPi 5 Pack Geared Stepper Motor 28BYJ-48 5V ...  
https://www.amazon.com/GeeekPi-Stepper-28BYJ-48-Uln2003-Compatible/dp/B087B5NWY4

[[6]] 3D Printer Controller DIY Kit, RAMPS 1.4 + 2560 R3 Board + 5pcs ...  
https://www.amazon.com/Printer-Controller-Stepper-Heatsink-Arduino/dp/B08JM562FW

[[8]] Shielded Miniature Bearings - VXB Bearings: Amazon.com: Industrial & Scientific  
https://www.amazon.com/Bearing-Shielded-Miniature-Bearings-VXB/dp/B0045DUYVS

[[9]] 10pcs F686ZZ Mini Steel Ball Bearings Double Shielded Flange 3D Printer Model 6x13x5mm  
https://www.amazon.com/F686ZZ-Bearings-Double-Shielded-Printer-6x13x5mm/dp/B07CH3XB6B

[[11]] SKF 51105 Single Direction Thrust Bearing, 3 Piece, Grooved Race ...  
https://www.amazon.com/SKF-51105-Direction-Precision-Capacity/dp/B007VHGOF0

[[12]] [[14]] [[15]] [[18]] [[19]] [[20]] [[21]] [[25]] ROBOTIC ARM UNIT  
https://www.thematic-learning.com/wp-content/uploads/2022/05/ROBOTIC-ARM-UNIT-1.pdf

[[16]] [[22]] [[23]] 720 Pcs Nuts and Bolts Assortment Kit, M3 M4 M5 Carbon Steel Screws Bolts and Nuts and Washers Assortment Set, Assorted Cross Pan Head Machine Screws Set, with Storage Case: Amazon.com: Industrial & Scientific  
https://www.amazon.com/Assortment-Stainless-Washers-Assorted-Machine/dp/B0BC24J6SS

[[17]] uxcell M6 x 45mm 304 Stainless Steel Phillips Hex Head Bolts Nuts ...  
https://www.amazon.com/uxcell-Stainless-Steel-Phillips-Washers/dp/B01N5CRV6U
