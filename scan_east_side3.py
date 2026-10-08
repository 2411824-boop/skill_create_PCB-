import sys, re
sys.path.insert(0, r'A:\DEVICE\data_traning pcb\scripts')
import all_routes_v2

all_r = (
    all_routes_v2.get_fanout_routes() + all_routes_v2.get_group_a_routes() +
    all_routes_v2.get_group_b_routes() + all_routes_v2.get_group_c_routes() +
    all_routes_v2.get_group_d_routes() + all_routes_v2.get_group_e_routes() +
    all_routes_v2.get_group_f_routes()
)

print('--- ROUTED SEGMENTS X >= 114 ---')
# parse segments
seg_pattern = re.compile(r'\(segment\s*\(start\s+([\d\.-]+)\s+([\d\.-]+)\)\s*\(end\s+([\d\.-]+)\s+([\d\.-]+)\)\s*\(width\s+([\d\.-]+)\)\s*\(layer\s+"([^"]+)"\)\s*\(net\s+"([^"]+)"\)', re.DOTALL)
for m in seg_pattern.finditer(all_r):
    x1, y1, x2, y2, w, layer, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)), m.group(6), m.group(7)
    if (x1 >= 114 or x2 >= 114) and min(y1, y2) >= 55 and max(y1, y2) <= 126:
        print(f'SEG: {net:15} {layer:5} ({x1:6.2f},{y1:6.2f}) -> ({x2:6.2f},{y2:6.2f}) w={w}')

# parse vias
via_pattern = re.compile(r'\(via\s*\(at\s+([\d\.-]+)\s+([\d\.-]+)\)\s*\(size\s+([\d\.-]+)\)\s*\(drill\s+([\d\.-]+)\)\s*\(layers\s+"([^"]+)"\s+"([^"]+)"\)\s*\(net\s+"([^"]+)"\)', re.DOTALL)
for m in via_pattern.finditer(all_r):
    x, y, sz, dr, l1, l2, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5), m.group(6), m.group(7)
    if x >= 114 and 55 <= y <= 126:
        print(f'VIA: {net:15} at ({x:6.2f},{y:6.2f}) sz={sz}')
