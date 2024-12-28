
module hex_grid(cx = 5, cy = 5, diameter = 5) {
    difference() {
        cube([cx * diameter * 1.7, (cy-1) * diameter, 1]);
        for (y = [0:1:cy*2-1]) {
            for (x = [0:1:cx]) {
                dx = (x + (y%2)/2) * diameter * 1.7;
                dy = y * diameter / 2;
                translate([dx, dy, -1])
                    cylinder(h = 3, d = diameter, $fn = 6);
            }
        }
    }
}

hex_grid();