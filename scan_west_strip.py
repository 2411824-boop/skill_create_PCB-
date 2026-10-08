import sys, re
PCB_SRC = r'A:\DEVICE\KiCad_Project\WaterSensor.kicad_pcb'

with open(PCB_SRC, 'r', encoding='utf-8') as f:
    text = f.read()

print('=== Scanning X in [72.5, 75.0], Y in [53, 128] in PCB ===')

# Check all footprint pads
fps = text.split('(footprint ')
for fp in fps[1:]:
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', fp)
    at_m = re.search(r'\(at ([\d\.-]+) ([\d\.-]+)(?: ([\d\.-]+))?\)', fp)
    ref = ref_m.group(1) if ref_m else '?'
    fx, fy = (float(at_m.group(1)), float(at_m.group(2))) if at_m else (0, 0)

    # check pads
    for pad_block in fp.split('(pad '):
        p_at = re.search(r'\(at ([\d\.-]+) ([\d\.-]+)', pad_block)
        p_sz = re.search(r'\(size ([\d\.-]+) ([\d\.-]+)', pad_block)
        p_layers = re.search(r'\(layers ([^\)]+)\)', pad_block)
        p_num = pad_block.split()[0].replace('"', '') if pad_block else '?'
        if p_at and p_sz:
            px, py = float(p_at.group(1)), float(p_at.group(2))
            sx, sy = float(p_sz.group(1)), float(p_sz.group(2))
            # compute absolute position
            # Note: need footprint rotation!
            rot = float(at_m.group(3)) if (at_m and at_m.group(3)) else 0.0
            import math
            rad = math.radians(rot)
            ax = fx + px * math.cos(rad) - py * math.sin(rad)
            ay = fy + px * math.sin(rad) + py * math.cos(rad)

            if 72.5 <= ax - sx/2 <= 75.0 or 72.5 <= ax + sx/2 <= 75.0:
                lyrs = p_layers.group(1) if p_layers else '?'
                print(f'PAD: {ref}.{p_num:3} at ({ax:6.2f}, {ay:6.2f}) sz=({sx:4.2f},{sy:4.2f}) layers={lyrs}')

# Check all routes from all_routes_v2
sys.path.insert(0, r'A:\DEVICE\data_traning pcb\scripts')
import all_routes_v2
all_r = (
    all_routes_v2.get_fanout_routes() + all_routes_v2.get_group_a_routes() +
    all_routes_v2.get_group_b_routes() + all_routes_v2.get_group_c_routes() +
    all_routes_v2.get_group_d_routes() + all_routes_v2.get_group_e_routes() +
    all_routes_v2.get_group_f_routes()
)

print('\n=== Scanning routes in X in [72.5, 75.0] ===')
seg_pattern = re.compile(r'\(segment\s*\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s*\(end\s+([\d\.-]+)\s+([\d\.-]+)\)\s*\(width\s+([\d\.-]+)\)\s*\(layer\s+\"([^\"]+)\"\)\s*\(net\s+\"([^\"]+)\"\)', re.DOTALL)
for m in seg_pattern.finditer(all_r):
    x1, y1, x2, y2, w, layer, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)), m.group(6), m.group(7)
    if (72.5 <= x1 <= 75.0 or 72.5 <= x2 <= 75.0) and min(y1, y2) >= 53 and max(y1, y2) <= 128:
        print(f'SEG: {net:15} {layer:5} ({x1:6.2f},{y1:6.2f}) -> ({x2:6.2f},{y2:6.2f}) w={w}')

via_pattern = re.compile(r'\(via\s*\(at\s+([\d\.-]+)\s+([\d\.-]+)\)\s*\(size\s+([\d\.-]+)\)\s*\(drill\s+([\d\.-]+)\)\s*\(layers\s+"([^"]+)"\s+"([^"]+)"\)\s*\(net\s+"([^"]+)"\)', re.DOTALL)
for m in via_pattern.finditer(all_r):
    x, y, sz, dr, l1, l2, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5), m.group(6), m.group(7)
    if 72.5 <= x <= 75.0 and 53 <= y <= 128:
        print(f'VIA: {net:15} at ({x:6.2f},{y:6.2f}) sz={sz}')
