import math

# Pad offsets in SOT-23-6 for U3:
# Pad 1: (-1.1375, -0.950)
# Pad 2: (-1.1375, 0.000)
# Pad 3: (-1.1375, +0.950)
# Pad 4: (+1.1375, +0.950)
# Pad 5: (+1.1375, 0.000)
# Pad 6: (+1.1375, -0.950)

def get_pads(xc, yc, rot_deg):
    rad = math.radians(rot_deg)
    cos_r = math.cos(rad)
    sin_r = math.sin(rad)
    base_pads = {
        1: (-1.1375, -0.950),
        2: (-1.1375, 0.000),
        3: (-1.1375, +0.950),
        4: (+1.1375, +0.950),
        5: (+1.1375, 0.000),
        6: (+1.1375, -0.950),
    }
    res = {}
    for num, (dx, dy) in base_pads.items():
        # KiCad rotation: x' = dx*cos - dy*sin, y' = dx*sin + dy*cos
        px = xc + (dx * cos_r - dy * sin_r)
        py = yc + (dx * sin_r + dy * cos_r)
        res[num] = (round(px, 3), round(py, 3))
    return res

for rot in [0, 90, 180, 270]:
    print(f"\n--- Rot = {rot} deg at (83.5, 91.5) ---")
    pads = get_pads(83.5, 91.5, rot)
    for p, coord in pads.items():
        print(f"  Pad {p}: {coord}")
