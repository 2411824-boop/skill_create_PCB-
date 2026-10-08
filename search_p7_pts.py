import pcbnew
b = pcbnew.LoadBoard('KiCad_Project/test_phase1.kicad_pcb')

vr = 0.3
valid_pts = []
for ix in range(38): # 91.5 .. 95.2 step 0.1
    x = round(91.5 + ix*0.1, 2)
    for iy in range(18): # 69.7 .. 71.4 step 0.1
        y = round(69.7 + iy*0.1, 2)
        conflict = False
        for t in b.GetTracks():
            if t.GetNetname() == 'GND': continue
            s, e = t.GetStart(), t.GetEnd()
            sx, sy, ex, ey = s.x/1e6, s.y/1e6, e.x/1e6, e.y/1e6
            dx, dy = ex - sx, ey - sy; l2 = dx*dx + dy*dy
            u = 0.0 if l2 == 0 else max(0.0, min(1.0, ((x-sx)*dx + (y-sy)*dy)/l2))
            dist = ((x - (sx + u*dx))**2 + (y - (sy + u*dy))**2)**0.5
            tw = 0.6 if t.GetClass() == 'PCB_VIA' else t.GetWidth()/1e6
            if dist < vr + tw/2.0 + 0.16:
                conflict = True; break
        if conflict: continue
        for fp in b.Footprints():
            for p in fp.Pads():
                if p.GetNetname() == 'GND': continue
                pos = p.GetPosition(); px, py = pos.x/1e6, pos.y/1e6
                dist = ((x - px)**2 + (y - py)**2)**0.5
                pr = max(p.GetSize().x, p.GetSize().y)/2e6
                if dist < vr + pr + 0.16:
                    conflict = True; break
            if conflict: break
        if not conflict:
            valid_pts.append((x, y))

print(f"Valid points inside Poly 7: {len(valid_pts)}")
for pt in valid_pts:
    print(f"  {pt}")
