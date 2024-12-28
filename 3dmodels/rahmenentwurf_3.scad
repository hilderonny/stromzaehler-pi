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
    //translate([-1, stuetzendicke, bodenstaerke])
        //cube([breite+2, laenge-2*stuetzendicke, hoehe]);
    // Querbox
    //translate([stuetzendicke, -1, bodenstaerke])
        //cube([breite-2*stuetzendicke, laenge+2, hoehe]);
    // Bodenaussparung
    translate([stuetzendicke, stuetzendicke, -1])
        cube([breite-2*stuetzendicke, laenge-2*stuetzendicke, bodenstaerke+2]);
}

// Kamerahalterung
translate([27.5 - 2.5, laenge-31, 0]) difference() {
    union() {
        translate([0, 7.5, 0]) cube([25, 20, 1]);
        translate([2, 22, 0]) cylinder(2.6+bodenstaerke, 3, 3);
        translate([23, 22, 0]) cylinder(2.6+bodenstaerke, 3, 3);
        translate([2, 9.5, 0]) cylinder(2.6+bodenstaerke, 3, 3);
        translate([23, 9.5, 0]) cylinder(2.6+bodenstaerke, 3, 3);
    }
        translate([2, 22, -bodenstaerke-1]) cylinder(2.6+bodenstaerke+3, 1, 1);
        translate([23, 22, -bodenstaerke-1]) cylinder(2.6+bodenstaerke+3, 1, 1);
        translate([2, 9.5, -bodenstaerke-1]) cylinder(2.6+bodenstaerke+3, 1, 1);
        translate([23, 9.5, -bodenstaerke-1]) cylinder(2.6+bodenstaerke+3, 1, 1);
}
// Kamera
//translate([27.5, laenge-31, bodenstaerke+2.6]) PiCamera_1_3();
