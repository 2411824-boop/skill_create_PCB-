import sys

with open(r'A:\DEVICE\KiCad_Project\WaterSensor.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect everything on B.Cu and F.Cu with X >= 115 and Y between 65 and 125
lines = text.split('\n')
for i, l in enumerate(lines):
    if '(segment ' in l or '(via ' in l or '(pad ' in l:
        # check if line or next lines contain coordinates
        block = '\n'.join(lines[i:min(len(lines), i+15)])
        # look for X >= 115
        import re
        nums = [float(n) for n in re.findall(r'[-+]?\d*\.\d+|\d+', block)]
        # quick print of segments in this region
        if '(segment ' in l:
            m = re.search(r'\(start ([\d\.-]+) ([\d\.-]+)\) \(end ([\d\.-]+) ([\d\.-]+)\).*\(layer "([^"]+)"\).*\(net "([^"]+)"\)', l)
            if m:
                x1, y1, x2, y2, layer, net = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5), m.group(6)
                if (x1 >= 114 or x2 >= 114) and min(y1, y2) >= 60 and max(y1, y2) <= 126:
                    print(f'SEG: {net:15} {layer:5} ({x1:.2f},{y1:.2f}) -> ({x2:.2f},{y2:.2f})')
        elif '(via ' in l:
            m = re.search(r'\(at ([\d\.-]+) ([\d\.-]+)\).*\(net "([^"]+)"\)', l)
            if m:
                x, y, net = float(m.group(1)), float(m.group(2)), float(m.group(3))
                if x >= 114 and 60 <= y <= 126:
                    print(f'VIA: {net:15} at ({x:.2f},{y:.2f})')
