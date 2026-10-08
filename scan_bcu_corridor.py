import sys, re
sys.path.insert(0, r'A:\DEVICE\data_traning pcb\scripts')
import all_routes_v2

with open(r'A:\DEVICE\KiCad_Project\WaterSensor.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb = f.read()

all_r = (
    all_routes_v2.get_fanout_routes() + all_routes_v2.get_group_a_routes() +
    all_routes_v2.get_group_b_routes() + all_routes_v2.get_group_c_routes() +
    all_routes_v2.get_group_d_routes() + all_routes_v2.get_group_e_routes() +
    all_routes_v2.get_group_f_routes()
)

print('=== Scanning B.Cu obstacles in X in [86.0, 90.0], Y in [69.0, 115.0] ===')

# PCB pads on B.Cu
fps = pcb.split('(footprint ')
for fp in fps[1:]:
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', fp)
    at_m = re.search(r'\(at ([\d\.-]+) ([\d\.-]+)(?: ([\d\.-]+))?\)', fp)
    ref = ref_m.group(1) if ref_m else '?'
    fx, fy = (float(at_m.group(1)), float(at_m.group(2))) if at_m else (0, 0)
    rot = float(at_m.group(3)) if (at_m and at_m.group(3)) else 0.0
    import math
    rad = math.radians(rot)

    for pad_block in fp.split('(pad '):
        if 'B.Cu' in pad_block or '*.Cu' in pad_block:
            p_at = re.search(r'\(at ([\d\.-]+) ([\d\.-]+)', pad_block)
            p_sz = re.search(r'\(size ([\d\.-]+) ([\d\.-]+)', pad_block)
            p_net = re.search(r'\(net "([^"]+)"\)', pad_block)
            p_num = pad_block.split()[0].replace('"', '') if pad_block else '?'
            if p_at and p_sz:
                px, py = float(p_at.group(1)), float(p_at.group(2))
                sx, sy = float(p_sz.group(1)), float(p_sz.group(2))
                ax = fx + px * math.cos(rad) - py * math.sin(rad)
                ay = fy + px * math.sin(rad) + py * math.cos(rad)
                if (85.0 <= ax <= 91.0) and (68.0 <= ay <= 116.0):
                    net = p_net.group(1) if p_net else 'NO_NET'
                    print(f'PAD: {ref}.{p_num:3} at ({ax:6.2f},{ay:6.2f}) sz=({sx:4.2f},{sy:4.2f}) net={net}')

# Routes on B.Cu
seg_pattern = re.compile(r'\(segment\s*\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s*\(end\s+([\d\.-]+)\s+([\d\.-]+)\)\s*\(width\s+([\d\.-]+)\)\s*\(layer\s+\"B.Cu\"\)\s*\(net\s+\"([^\"]+)\"\)', re.DOTALL)
via_pattern = re.compile(r'\(via\s*\(at\s+([\d\.-]+)\s+([\d\.-]+)\)\s*\(size\s+([\d\.-]+)\)\s*\(drill\s+([\d\.-]+)\)\s*\(layers\s+"([^"]+)"\s+"([^"]+)"\)\s*\(net\s+"([^"]+)"\)', re.DOTALL)

for m in seg_pattern.finditer(all_r):
    x1, y1, x2, y2, w, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)), m.group(6)
    if (min(x1, x2) <= 91.0 and max(x1, x2) >= 85.0) and (min(y1, y2) <= 116.0 and max(y1, y2) >= 68.0):
        print(f'SEG: {net:15} ({x1:6.2f},{y1:6.2f}) -> ({x2:6.2f},{y2:6.2f}) w={w}')

for m in via_pattern.finditer(all_r):
    x, y, sz, dr, l1, l2, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5), m.group(6), m.group(7)
    if (85.0 <= x <= 91.0) and (68.0 <= y <= 116.0):
        print(f'VIA: {net:15} at ({x:6.2f},{y:6.2f}) sz={sz}')
