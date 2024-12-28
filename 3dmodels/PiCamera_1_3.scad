
module PiCamera_1_3() {
    // Leiterplatte
    difference() {
        // Grundplatte
        cube([25, 24, 1]);
        // Löcher
        translate([2, 22, -1]) cylinder(3, 1, 1);
        translate([23, 22, -1]) cylinder(3, 1, 1);
        translate([2, 9.5, -1]) cylinder(3, 1, 1);
        translate([23, 9.5, -1]) cylinder(3, 1, 1);
    }

    // Kamerabox
    translate([8.5, 5.5, 1]) cube([8, 8, 3.8]);

    // Objektivhalter
    translate([12.5, 9.5, 4.8]) cylinder(1, 4, 4);

    // Objektiv
    difference() {
        translate([12.5, 9.5, 5.8]) cylinder(1, 2.7, 2.7);
        translate([12.5, 9.5, 6]) cylinder(1, 1, 1);
    }

    // Objektivanschluss
    translate([8.5, 17.5, 1]) cube([8, 5, 1.5]);

    // Kabelanschluss
    translate([2, 0, -2.6]) cube([21, 5.7, 2.6]);
}

PiCamera_1_3();