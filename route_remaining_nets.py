import pcbnew, shutil
from collections import deque
import numpy as np

# Load fresh base from test_zero
shutil.copyfile('KiCad_Project/test_zero.kicad_pcb', 'KiCad_Project/test_phase1.kicad_pcb')
shutil.copyfile('KiCad_Project/test_zero.kicad_pro', 'KiCad_Project/test_phase1.kicad_pro')
b = pcbnew.LoadBoard('KiCad_Project/test_phase1.kicad_pcb')

def p2i(mm): return int(round(mm * 1e6))
def v2i(x, y): return pcbnew.VECTOR2I(p2i(x), p2i(y))

def add_track(netname, layer, s_xy, e_xy, w_mm=0.15):
    t = pcbnew.PCB_TRACK(b)
    t.SetNet(b.FindNet(netname))
    t.SetLayer(layer)
    t.SetStart(v2i(s_xy[0], s_xy[1]))
    t.SetEnd(v2i(e_xy[0], e_xy[1]))
    t.SetWidth(p2i(w_mm))
    b.Add(t)
    return t

def add_via(netname, pos_xy, drill_mm=0.3, size_mm=0.6):
    v = pcbnew.PCB_VIA(b)
    v.SetNet(b.FindNet(netname))
    v.SetPosition(v2i(pos_xy[0], pos_xy[1]))
    v.SetDrill(p2i(drill_mm))
    v.SetWidth(p2i(size_mm))
    v.SetTopLayer(pcbnew.F_Cu)
    v.SetBottomLayer(pcbnew.B_Cu)
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    b.Add(v)
    return v

# --- 1. Shift C_GPS1 and C_GPS2 South to free Y=115..118.5 ---
c1 = b.FindFootprintByReference('C_GPS1')
c1.SetPosition(v2i(101.300, 119.500))
c2 = b.FindFootprintByReference('C_GPS2')
c2.SetPosition(v2i(101.300, 121.500))

# --- 2. GPS_ANT (0.40mm, B.Cu, 0 via, 5.1mm straight line) ---
add_track('GPS_ANT', pcbnew.B_Cu, (121.0, 116.95), (115.9, 116.95), 0.40)

# --- 3. Rule Area keepout on In2.Cu ---
for z in b.Zones():
    if z.GetIsRuleArea() and z.GetFirstLayer() == pcbnew.In2_Cu:
        poly = z.Outline()
        poly.RemoveAllContours()
        poly.NewOutline()
        poly.Append(v2i(115.0, 115.8))
        poly.Append(v2i(122.0, 115.8))
        poly.Append(v2i(122.0, 118.1))
        poly.Append(v2i(115.0, 118.1))

# --- 4. TDS_ADC detour below U_GPS.1 ---
add_track('TDS_ADC', pcbnew.B_Cu, (123.8, 120.5), (123.8, 121.3), 0.20)
add_track('TDS_ADC', pcbnew.B_Cu, (123.8, 121.3), (111.325, 121.3), 0.20)
add_track('TDS_ADC', pcbnew.B_Cu, (111.325, 121.3), (111.325, 120.5), 0.20)

# --- 5. LCD_GATE (100% on F.Cu, 0 via) ---
add_track('LCD_GATE', pcbnew.F_Cu, (112.5625, 113.55), (112.5625, 112.60), 0.15)
add_track('LCD_GATE', pcbnew.F_Cu, (112.5625, 112.60), (117.325, 112.60), 0.15)
add_track('LCD_GATE', pcbnew.F_Cu, (117.325, 112.60), (117.325, 117.20), 0.15)
add_track('LCD_GATE', pcbnew.F_Cu, (117.325, 117.20), (118.675, 117.20), 0.15)
add_track('LCD_GATE', pcbnew.F_Cu, (118.675, 117.20), (118.675, 119.40), 0.15)

# --- 6. +3V3 and GND for U_GPS, C_GPS1, C_GPS2 in South ---
add_track('+3V3', pcbnew.B_Cu, (104.100, 119.150), (102.075, 119.150), 0.25)
add_track('+3V3', pcbnew.B_Cu, (102.075, 119.150), (102.075, 119.500), 0.25)
add_track('+3V3', pcbnew.B_Cu, (102.075, 119.500), (102.075, 121.500), 0.25)
add_via('+3V3', (102.075, 120.500), 0.3, 0.6)

add_track('GND', pcbnew.B_Cu, (100.525, 119.500), (100.525, 121.500), 0.25)
add_via('GND', (100.525, 120.500), 0.3, 0.6)

# --- 7. +3V3 and GND for U7 and C_RTC_VCC in North ---
add_track('+3V3', pcbnew.B_Cu, (98.350, 75.175), (96.500, 75.175), 0.25)
add_track('+3V3', pcbnew.B_Cu, (96.500, 75.175), (96.500, 78.500), 0.25)
add_track('+3V3', pcbnew.B_Cu, (96.500, 78.500), (97.575, 78.500), 0.25)
add_track('+3V3', pcbnew.B_Cu, (97.575, 78.500), (97.575, 80.000), 0.25)
add_via('+3V3', (97.575, 80.000), 0.3, 0.6)

add_track('GND', pcbnew.B_Cu, (99.125, 78.500), (99.125, 80.000), 0.25)
add_via('GND', (99.125, 80.000), 0.3, 0.6)

# --- 8. RTC_INT ---
add_track('RTC_INT', pcbnew.F_Cu, (91.250, 67.910), (88.825, 67.910), 0.15)
add_track('RTC_INT', pcbnew.F_Cu, (91.250, 67.910), (92.500, 67.910), 0.15)
add_via('RTC_INT', (92.500, 67.910), 0.3, 0.6)
add_track('RTC_INT', pcbnew.B_Cu, (92.500, 67.910), (96.500, 67.910), 0.15)
add_track('RTC_INT', pcbnew.B_Cu, (96.500, 67.910), (96.500, 73.905), 0.15)
add_track('RTC_INT', pcbnew.B_Cu, (96.500, 73.905), (98.350, 73.905), 0.15)

# --- 9. I2C_SDA and I2C_SCL ---
add_track('I2C_SDA', pcbnew.F_Cu, (108.75, 64.10), (110.80, 64.10), 0.15)
add_track('I2C_SDA', pcbnew.F_Cu, (110.80, 64.10), (110.80, 70.10), 0.15)
add_track('I2C_SDA', pcbnew.F_Cu, (110.80, 70.10), (113.175, 70.10), 0.15)
add_via('I2C_SDA', (110.80, 70.10), 0.3, 0.6)
add_track('I2C_SDA', pcbnew.B_Cu, (110.80, 70.10), (110.80, 75.175), 0.15)
add_track('I2C_SDA', pcbnew.B_Cu, (110.80, 75.175), (107.65, 75.175), 0.15)

add_track('I2C_SCL', pcbnew.F_Cu, (108.75, 60.29), (113.175, 60.29), 0.15)
add_track('I2C_SCL', pcbnew.F_Cu, (113.175, 60.29), (113.175, 66.29), 0.15)
add_track('I2C_SCL', pcbnew.F_Cu, (113.175, 66.29), (112.00, 66.29), 0.15)
add_via('I2C_SCL', (112.00, 66.29), 0.3, 0.6)
add_track('I2C_SCL', pcbnew.B_Cu, (112.00, 66.29), (112.00, 76.445), 0.15)
add_track('I2C_SCL', pcbnew.B_Cu, (112.00, 76.445), (107.65, 76.445), 0.15)

# --- 10. VBAT_RTC Base (BT1.1 to U_GPS.22) ---
add_track('VBAT_RTC', pcbnew.B_Cu, (85.350, 94.500), (84.000, 94.500), 0.15)
add_track('VBAT_RTC', pcbnew.B_Cu, (84.000, 94.500), (84.000, 104.000), 0.15)
add_track('VBAT_RTC', pcbnew.B_Cu, (84.000, 104.000), (102.200, 104.000), 0.15)
add_track('VBAT_RTC', pcbnew.B_Cu, (102.200, 104.000), (102.200, 118.050), 0.15)
add_track('VBAT_RTC', pcbnew.B_Cu, (102.200, 118.050), (104.100, 118.050), 0.15)

print('Phase 1 core applied. Initializing 3D Router...')

# --- 3D Grid Router ---
X_MIN, X_MAX = 73.0, 125.0
Y_MIN, Y_MAX = 53.0, 128.0
RES = 0.25 # mm for fast convergence

nx = int(round((X_MAX - X_MIN) / RES)) + 1
ny = int(round((Y_MAX - Y_MIN) / RES)) + 1

grid = np.zeros((2, nx, ny), dtype=bool)

def x2idx(x): return int(round((x - X_MIN) / RES))
def y2idx(y): return int(round((y - Y_MIN) / RES))
def idx2x(ix): return X_MIN + ix * RES
def idx2y(iy): return Y_MIN + iy * RES

CLEARANCE = 0.15
TRACE_W = 0.15
MARGIN = CLEARANCE + TRACE_W / 2.0

# Mark board edges
edge_margin = 0.4
for ix in range(nx):
    x = idx2x(ix)
    for iy in range(ny):
        y = idx2y(iy)
        if x < 73.0 + edge_margin or x > 125.0 - edge_margin or y < 53.0 + edge_margin or y > 128.0 - edge_margin:
            grid[0, ix, iy] = True
            grid[1, ix, iy] = True

def mark_track(layer_idx, sx, sy, ex, ey, w, clearance=0.15):
    r = w/2.0 + clearance + TRACE_W/2.0
    min_x, max_x = max(X_MIN, min(sx, ex) - r), min(X_MAX, max(sx, ex) + r)
    min_y, max_y = max(Y_MIN, min(sy, ey) - r), min(Y_MAX, max(sy, ey) + r)
    ix1, ix2 = max(0, x2idx(min_x)), min(nx-1, x2idx(max_x))
    iy1, iy2 = max(0, y2idx(min_y)), min(ny-1, y2idx(max_y))
    dx, dy = ex - sx, ey - sy
    l2 = dx*dx + dy*dy
    for ix in range(ix1, ix2+1):
        px = idx2x(ix)
        for iy in range(iy1, iy2+1):
            py = idx2y(iy)
            if l2 == 0:
                d2 = (px-sx)**2 + (py-sy)**2
            else:
                u = max(0.0, min(1.0, ((px-sx)*dx + (py-sy)*dy) / l2))
                d2 = (px - (sx + u*dx))**2 + (py - (sy + u*dy))**2
            if d2 <= r*r:
                grid[layer_idx, ix, iy] = True

def mark_via(vx, vy, size=0.6, clearance=0.15):
    r = size/2.0 + clearance + TRACE_W/2.0
    min_x, max_x = max(X_MIN, vx - r), min(X_MAX, vx + r)
    min_y, max_y = max(Y_MIN, vy - r), min(Y_MAX, vy + r)
    ix1, ix2 = max(0, x2idx(min_x)), min(nx-1, x2idx(max_x))
    iy1, iy2 = max(0, y2idx(min_y)), min(ny-1, y2idx(max_y))
    for ix in range(ix1, ix2+1):
        px = idx2x(ix)
        for iy in range(iy1, iy2+1):
            py = idx2y(iy)
            if (px-vx)**2 + (py-vy)**2 <= r*r:
                grid[0, ix, iy] = True
                grid[1, ix, iy] = True

def mark_pad(layer_idx, px, py, sx, sy, clearance=0.15):
    rx, ry = sx/2.0 + clearance + TRACE_W/2.0, sy/2.0 + clearance + TRACE_W/2.0
    min_x, max_x = max(X_MIN, px - rx), min(X_MAX, px + rx)
    min_y, max_y = max(Y_MIN, py - ry), min(Y_MAX, py + ry)
    ix1, ix2 = max(0, x2idx(min_x)), min(nx-1, x2idx(max_x))
    iy1, iy2 = max(0, y2idx(min_y)), min(ny-1, y2idx(max_y))
    for ix in range(ix1, ix2+1):
        for iy in range(iy1, iy2+1):
            grid[layer_idx, ix, iy] = True

# Mark existing tracks & vias
for t in b.GetTracks():
    if t.GetNetname() in ['VBAT_RTC', 'LCD_BL_PWM', 'GPS_RX', 'GPS_TX']: continue
    if t.GetClass() == 'PCB_TRACK':
        l = 0 if t.GetLayer() == pcbnew.F_Cu else (1 if t.GetLayer() == pcbnew.B_Cu else -1)
        if l >= 0:
            s, e = t.GetStart(), t.GetEnd()
            mark_track(l, s.x/1e6, s.y/1e6, e.x/1e6, e.y/1e6, t.GetWidth()/1e6)
    elif t.GetClass() == 'PCB_VIA':
        pos = t.GetPosition()
        mark_via(pos.x/1e6, pos.y/1e6, 0.6)

# Mark pads
for fp in b.Footprints():
    for p in fp.Pads():
        if p.GetNetname() in ['VBAT_RTC', 'LCD_BL_PWM', 'GPS_RX', 'GPS_TX']: continue
        pos = p.GetPosition()
        px, py = pos.x/1e6, pos.y/1e6
        sx, sy = p.GetSize().x/1e6, p.GetSize().y/1e6
        if p.IsOnLayer(pcbnew.F_Cu): mark_pad(0, px, py, sx, sy)
        if p.IsOnLayer(pcbnew.B_Cu): mark_pad(1, px, py, sx, sy)

print('Static obstacles rasterized.')

via_r_cells = int(round(0.45 / RES))
def can_via(ix, iy):
    if ix - via_r_cells < 0 or ix + via_r_cells >= nx or iy - via_r_cells < 0 or iy + via_r_cells >= ny:
        return False
    for dx in range(-via_r_cells, via_r_cells + 1):
        for dy in range(-via_r_cells, via_r_cells + 1):
            if dx*dx + dy*dy <= via_r_cells*via_r_cells:
                if grid[0, ix+dx, iy+dy] or grid[1, ix+dx, iy+dy]:
                    return False
    return True

def route_net(netname, start_lxy, target_lxys):
    print(f'Routing {netname}...')
    start = (start_lxy[0], x2idx(start_lxy[1]), y2idx(start_lxy[2]))
    # unblock start & targets
    grid[start[0], start[1], start[2]] = False
    targets = set()
    for tl, tx, ty in target_lxys:
        t_cell = (tl, x2idx(tx), y2idx(ty))
        targets.add(t_cell)
        grid[t_cell[0], t_cell[1], t_cell[2]] = False

    queue = deque([start])
    visited = {start: None}
    found = None
    while queue:
        curr = queue.popleft()
        if curr in targets:
            found = curr
            break
        l, ix, iy = curr
        for dl, dx, dy in [(0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]:
            nl, nx_cell, ny_cell = l + dl, ix + dx, iy + dy
            if 0 <= nx_cell < nx and 0 <= ny_cell < ny:
                if not grid[nl, nx_cell, ny_cell]:
                    neighbor = (nl, nx_cell, ny_cell)
                    if neighbor not in visited:
                        visited[neighbor] = curr
                        queue.append(neighbor)
        if can_via(ix, iy):
            other_l = 1 - l
            if not grid[other_l, ix, iy]:
                neighbor = (other_l, ix, iy)
                if neighbor not in visited:
                    visited[neighbor] = curr
                    queue.append(neighbor)

    if not found:
        print(f'ERROR: No route found for {netname}!')
        return False

    # Trace back
    path = []
    c = found
    while c is not None:
        path.append(c)
        c = visited[c]
    path.reverse()

    # Simplify
    waypoints = [(p[0], round(idx2x(p[1]), 3), round(idx2y(p[2]), 3)) for p in path]
    # Replace first and last with exact coordinates
    waypoints[0] = (start_lxy[0], start_lxy[1], start_lxy[2])
    # match target
    target_match = None
    for tl, tx, ty in target_lxys:
        if (tl, x2idx(tx), y2idx(ty)) == found:
            target_match = (tl, tx, ty)
            break
    if target_match:
        waypoints[-1] = target_match

    # Compress collinear segments
    compressed = [waypoints[0]]
    for i in range(1, len(waypoints)-1):
        prev = compressed[-1]
        curr = waypoints[i]
        nxt = waypoints[i+1]
        if curr[0] != prev[0] or curr[0] != nxt[0]:
            compressed.append(curr)
        else:
            dx1 = round(curr[1] - prev[1], 4)
            dy1 = round(curr[2] - prev[2], 4)
            dx2 = round(nxt[1] - curr[1], 4)
            dy2 = round(nxt[2] - curr[2], 4)
            if (dx1 > 0 and dx2 <= 0) or (dx1 < 0 and dx2 >= 0) or (dy1 > 0 and dy2 <= 0) or (dy1 < 0 and dy2 >= 0):
                compressed.append(curr)
            elif (dx1 != 0 and dy2 != 0) or (dy1 != 0 and dx2 != 0):
                compressed.append(curr)
    compressed.append(waypoints[-1])

    # Add tracks and vias to board and mark in grid
    for i in range(len(compressed)-1):
        p1 = compressed[i]
        p2 = compressed[i+1]
        if p1[0] == p2[0]:
            layer = pcbnew.F_Cu if p1[0] == 0 else pcbnew.B_Cu
            add_track(netname, layer, (p1[1], p1[2]), (p2[1], p2[2]), 0.15)
            mark_track(p1[0], p1[1], p1[2], p2[1], p2[2], 0.15)
        else:
            # via
            add_via(netname, (p1[1], p1[2]), 0.3, 0.6)
            mark_via(p1[1], p1[2], 0.6)

    print(f'Successfully routed {netname} with {len(compressed)} waypoints.')
    return True

# 1. Route VBAT_RTC from U7.14 (107.65, 73.905) to VBAT_RTC South track
vbat_targets = []
for y in np.arange(94.5, 118.0, 0.5):
    vbat_targets.append((1, 102.200, float(y)))
route_net('VBAT_RTC', (1, 107.650, 73.905), vbat_targets)

# 2. Route LCD_BL_PWM: U6.8 (91.250, 66.640) on F.Cu -> R_LCD_GATE.1 (115.675, 117.200) on F.Cu
route_net('LCD_BL_PWM', (0, 91.250, 66.640), [(0, 115.675, 117.200)])

# 3. Route GPS_RX: U6.13 (91.250, 72.990) on F.Cu -> U_GPS.20 (104.100, 115.850) on B.Cu
route_net('GPS_RX', (0, 91.250, 72.990), [(1, 104.100, 115.850)])

# 4. Route GPS_TX: U6.16 (95.560, 75.510) on F.Cu -> U_GPS.21 (104.100, 116.950) on B.Cu
route_net('GPS_TX', (0, 95.560, 75.510), [(1, 104.100, 116.950)])

b.Save('KiCad_Project/test_phase1.kicad_pcb')
print('ALL 4 NETS ROUTED AND SAVED TO test_phase1.kicad_pcb!')
