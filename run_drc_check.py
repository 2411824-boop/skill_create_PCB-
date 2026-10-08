import subprocess, os, shutil, sys, re

PCB_SRC = r"A:\DEVICE\KiCad_Project\WaterSensor.kicad_pcb"
PCB_TMP = r"A:\DEVICE\KiCad_Project\temp_test_all_ag_v9.kicad_pcb"
PRO_SRC = r"A:\DEVICE\KiCad_Project\WaterSensor.kicad_pro"
PRO_TMP = r"A:\DEVICE\KiCad_Project\temp_test_all_ag_v9.kicad_pro"
DRC_RPT_NZ = r"A:\DEVICE\drc_test_all_ag_v9_nozones.rpt"
KICAD_CLI = r"E:\KidCad\bin\kicad-cli.exe"

sys.path.insert(0, r"A:\DEVICE\data_traning pcb\scripts")
import all_routes_v2

def strip_zones(text):
    result = []
    lines = text.split('\n')
    skip_depth = 0
    in_zone = False
    for line in lines:
        s = line.strip()
        if not in_zone and (s == '(zone' or s.startswith('(zone ')):
            in_zone = True
            skip_depth = line.count('(') - line.count(')')
            if skip_depth <= 0:
                in_zone = False
            continue
        if in_zone:
            skip_depth += line.count('(') - line.count(')')
            if skip_depth <= 0:
                in_zone = False
            continue
        result.append(line)
    return '\n'.join(result)

def main():
    import importlib
    importlib.reload(all_routes_v2)

    with open(PCB_SRC, "r", encoding="utf-8") as f:
        text = f.read()

    groups = {
        "Fanout": all_routes_v2.get_fanout_routes,
        "A": all_routes_v2.get_group_a_routes,
        "B": all_routes_v2.get_group_b_routes,
        "C": all_routes_v2.get_group_c_routes,
        "D": all_routes_v2.get_group_d_routes,
        "E": all_routes_v2.get_group_e_routes,
        "F": all_routes_v2.get_group_f_routes,
        "G": all_routes_v2.get_group_g_routes,
    }

    all_routes = ""
    for name, fn in groups.items():
        r = fn()
        all_routes += r

    marker = "\t(embedded_fonts no)\n)"
    idx = text.rfind(marker)
    if idx < 0:
        idx = text.rfind("\n)")
        idx += 1

    new_text = text[:idx] + all_routes + text[idx:]
    pcb_nz = PCB_TMP.replace(".kicad_pcb", "_nz.kicad_pcb")
    with open(pcb_nz, "w", encoding="utf-8") as f:
        f.write(strip_zones(new_text))
    pro_nz = pcb_nz.replace(".kicad_pcb", ".kicad_pro")
    if os.path.exists(PRO_SRC):
        shutil.copy2(PRO_SRC, pro_nz)

    cmd = [KICAD_CLI, "pcb", "drc", "--output", DRC_RPT_NZ, "--severity-all", pcb_nz]
    subprocess.run(cmd, capture_output=True, text=True)

    with open(DRC_RPT_NZ, "r", encoding="utf-8") as f:
        drc_txt = f.read()

    blocks = drc_txt.split('\n[')
    viols = []
    unconnected = []
    for b in blocks[1:]:
        header = '[' + b.split('\n')[0]
        if 'unconnected_items' in header:
            unconnected.append(header)
        else:
            lines = [l.strip() for l in b.split('\n') if l.strip()]
            items = [l for l in lines if l.startswith('@(')]
            nets = set(re.findall(r'\[(.*?)\]', ' '.join(items)))
            viols.append({
                'vtype': lines[0].split(':')[0].strip('[]'),
                'nets': tuple(sorted(nets)),
                'desc': ' | '.join(items[:2])
            })

    print(f"Total Violations: {len(viols)} | Unconnected: {len(unconnected)}")
    by_nets = {}
    for v in viols:
        by_nets.setdefault(v['nets'], []).append(v)

    for nets, items in sorted(by_nets.items(), key=lambda x: -len(x[1])):
        types = [it['vtype'] for it in items]
        print(f"  {nets} ({len(items)}): {types}")

if __name__ == "__main__":
    main()
