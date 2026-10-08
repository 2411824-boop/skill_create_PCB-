import sys, re
sys.path.insert(0, r'A:\DEVICE\data_traning pcb\scripts')
import all_routes_v2

# 1. Routes in all_routes_v2
all_r = (
    all_routes_v2.get_fanout_routes() + all_routes_v2.get_group_a_routes() +
    all_routes_v2.get_group_b_routes() + all_routes_v2.get_group_c_routes() +
    all_routes_v2.get_group_d_routes() + all_routes_v2.get_group_e_routes() +
    all_routes_v2.get_group_f_routes()
)

print('--- ROUTED SEGMENTS X >= 114 ---')
for line in all_r.split('\n'):
    if '(segment ' in line:
        m = re.search(r'\(start ([\d\.-]+) ([\d\.-]+)\) \(end ([\d\.-]+) ([\d\.-]+)\).*\(layer "([^"]+)"\).*\(net "([^"]+)"\)', line)
        if m:
            x1, y1, x2, y2, layer, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5), m.group(6)
            if (x1 >= 114 or x2 >= 114) and min(y1, y2) >= 55 and max(y1, y2) <= 126:
                print(f'SEG: {net:15} {layer:5} ({x1:6.2f},{y1:6.2f}) -> ({x2:6.2f},{y2:6.2f})')
    elif '(via ' in line:
        m = re.search(r'\(at ([\d\.-]+) ([\d\.-]+)\).*\(net "([^"]+)"\)', line)
        if m:
            x, y, net = float(m.group(1)), float(m.group(2)), float(m.group(3))
            if x >= 114 and 55 <= y <= 126:
                print(f'VIA: {net:15} at ({x:6.2f},{y:6.2f})')

# 2. Footprint pads in WaterSensor.kicad_pcb
with open(r'A:\DEVICE\KiCad_Project\WaterSensor.kicad_pcb', 'r', encoding='utf-8') as f:
    pcb_text = f.read()

# find footprints with X >= 114
print('\n--- FOOTPRINTS X >= 114 ---')
fps = pcb_text.split('(footprint ')
for fp in fps[1:]:
    ref_m = re.search(r'\(property "Reference" "([^"]+)"', fp)
    at_m = re.search(r'\(at ([\d\.-]+) ([\d\.-]+)(?: ([\d\.-]+))?\)', fp)
    layer_m = re.search(r'\(layer "([^"]+)"\)', fp)
    if ref_m and at_m:
        ref = ref_m.group(1)
        fx, fy = float(at_m.group(1)), float(at_m.group(2))
        layer = layer_m.group(1) if layer_m else '?'
        if fx >= 112 and 55 <= fy <= 126:
            print(f'FP: {ref:15} {layer:5} at ({fx:6.2f},{fy:6.2f})')
