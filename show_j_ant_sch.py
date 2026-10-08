with open('KiCad_Project/WaterSensor.kicad_sch', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'J_ANT' in line:
        for j in range(max(0, i-15), min(len(lines), i+30)):
            print(f"{j+1}: {lines[j].rstrip()}")
        break
