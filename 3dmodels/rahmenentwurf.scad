breite = 80;
laenge = 80;
hoehe = 39;

wandstaerke = 1.5;

difference() {
    // Rahmenbox
    cube([breite,80,39]);
    // Innere Box
    translate([wandstaerke, wandstaerke, 1]) cube([breite - wandstaerke * 2,laenge - wandstaerke * 2, hoehe]);
    // Längsbox
    translate([-1, 10, 1]) cube([breite+2,laenge-20,hoehe]);
    // Querbox
    translate([10, -1, 1]) cube([breite-20,laenge+2,hoehe]);
    // Bodenaussparung
    translate([10, 10, -1]) cube([breite-20,laenge/2-10,4]);
}