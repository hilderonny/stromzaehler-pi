use <PiCamera_1_3.scad>;
use <hex_grid.scad>;

$fn = 360;

breite = 80;
laenge = 80;
hoehe = 39;

bodenstaerke = 1;
wandstaerke = 2;
stuetzendicke = 7;

// Rahmen
difference() {
    // Rahmenbox
    cube([breite, laenge, hoehe]);
    // Innere Box
    translate([wandstaerke, wandstaerke, bodenstaerke])
        cube([breite - wandstaerke * 2, laenge - wandstaerke * 2, hoehe]);
    // Längsbox
    translate([-1, stuetzendicke, bodenstaerke])
        cube([breite+2, laenge-2*stuetzendicke, hoehe]);
    // Querbox
    translate([stuetzendicke, -1, bodenstaerke])
        cube([breite-2*stuetzendicke, laenge+2, hoehe]);
    // Bodenaussparung
    translate([stuetzendicke, stuetzendicke, -1])
        cube([breite-2*stuetzendicke, laenge-2*stuetzendicke, bodenstaerke+2]);
}

// Kamerahalterung
translate([27.5 - 5, laenge-31, 0]) difference() {
    union() {
        translate([0, 7.5, 0]) cube([25, 20, 1]);
        translate([2, 22, 0]) cylinder(2.6+bodenstaerke, 2, 2);
        translate([23, 22, 0]) cylinder(2.6+bodenstaerke, 2, 2);
        translate([2, 9.5, 0]) cylinder(2.6+bodenstaerke, 2, 2);
        translate([23, 9.5, 0]) cylinder(2.6+bodenstaerke, 2, 2);
    }
        translate([2, 22, -bodenstaerke-1]) cylinder(2.6+bodenstaerke+3, 1, 1);
        translate([23, 22, -bodenstaerke-1]) cylinder(2.6+bodenstaerke+3, 1, 1);
        translate([2, 9.5, -bodenstaerke-1]) cylinder(2.6+bodenstaerke+3, 1, 1);
        translate([23, 9.5, -bodenstaerke-1]) cylinder(2.6+bodenstaerke+3, 1, 1);
    /*
    translate([2, 22, 0]) difference() {
        cylinder(2.6, 2, 2);
        cylinder(2.7, 1, 1);
    }
    translate([23, 22, 0]) difference() {
        cylinder(2.6, 2, 2);
        cylinder(2.7, 1, 1);
    }
    translate([2, 9.5, 0]) difference() {
        cylinder(2.6, 2, 2);
        cylinder(2.7, 1, 1);
    }
    translate([23, 9.5, 0]) difference() {
        cylinder(2.6, 2, 2);
        cylinder(2.7, 1, 1);
    }
    */
}
// Kamera
//translate([27.5, laenge-31, bodenstaerke+2.6]) PiCamera_1_3();

// Bodengitter
intersection() {
    cube([breite, laenge, bodenstaerke]);
    translate([-8, 0, 0]) scale([2, 2, bodenstaerke]) hex_grid(cx = 6, cy = 10);
}
// Hinteres Gitter
translate([0, laenge, hoehe]) rotate([90, 90, 0]) intersection() {
    cube([hoehe, breite, bodenstaerke]);
    translate([-3, 0, 0]) scale([2, 2, bodenstaerke]) hex_grid(cx = 6, cy = 10);
}
// Vorderes Gitter
translate([0, bodenstaerke, hoehe]) rotate([90, 90, 0]) intersection() {
    cube([hoehe, breite, bodenstaerke]);
    translate([-3, 0, 0]) scale([2, 2, bodenstaerke]) hex_grid(cx = 6, cy = 10);
}
// Linkes Gitter
translate([0, 0, hoehe]) rotate([90, 90, 90]) intersection() {
    cube([hoehe, laenge, bodenstaerke]);
    translate([-3, 0, 0]) scale([2, 2, bodenstaerke]) hex_grid(cx = 6, cy = 10);
}
// Rechtes Gitter
translate([breite-bodenstaerke, 0, hoehe]) rotate([90, 90, 90]) intersection() {
    cube([hoehe, laenge, bodenstaerke]);
    translate([-3, 0, 0]) scale([2, 2, bodenstaerke]) hex_grid(cx = 6, cy = 10);
}
