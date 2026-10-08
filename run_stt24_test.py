import pcbnew
import shutil

src = 'KiCad_Project/WaterSensor.kicad_pcb'
dst = 'KiCad_Project/WaterSensor_test_stt24.kicad_pcb'
shutil.copyfile(src, dst)
shutil.copyfile('KiCad_Project/WaterSensor.kicad_pro', 'KiCad_Project/WaterSensor_test_stt24.kicad_pro')

b = pcbnew.LoadBoard(dst)

# Ensure net GPS_RESET_N
net_rst = b.FindNet('GPS_RESET_N')
if not net_rst:
    net_rst = pcbnew.NETINFO_ITEM(b, 'GPS_RESET_N')
    b.Add(net_rst)
    net_rst = b.FindNet('GPS_RESET_N')

net_gnd = b.FindNet('GND')
net_3v3 = b.FindNet('+3V3')
net_rx = b.FindNet('GPS_RX')
net_tx = b.FindNet('GPS_TX')
net_vbat = b.FindNet('VBAT_RTC')

# CLEAN PHASE:
to_remove_tracks = []
for t in b.Tracks():
    nn = t.GetNetname()
    s, e = t.GetStart(), t.GetEnd()
    sx, sy, ex, ey = s.x/1e6, s.y/1e6, e.x/1e6, e.y/1e6
    if nn == 'GPS_RESET_N':
        to_remove_tracks.append(t)
    elif nn == 'GPS_RX':
        # Remove via and tracks between (106.0, 108.5) and U_GPS
        if t.GetClass() == 'PCB_VIA' and sx > 103.0 and sx < 108.0 and sy > 105.0 and sy < 112.0:
            to_remove_tracks.append(t)
        elif t.GetLayer() == pcbnew.B_Cu and max(sx, ex) > 103.0 and min(sx, ex) < 108.0 and max(sy, ey) > 106.0:
            to_remove_tracks.append(t)
    elif nn == 'GPS_TX' and t.GetLayer() == pcbnew.B_Cu:
        # Remove from (117.1, 96.8) westwards and down to U_GPS
        if abs(sy - 96.80) < 0.05 and abs(ey - 96.80) < 0.05 and min(sx, ex) < 117.2 and max(sx, ex) > 104.0:
            to_remove_tracks.append(t)
        elif min(sy, ey) >= 96.75 and max(sx, ex) > 103.5 and min(sx, ex) < 108.0:
            to_remove_tracks.append(t)
    elif nn == 'VBAT_RTC' and t.GetLayer() == pcbnew.B_Cu:
        if min(sy, ey) >= 103.5 and max(sx, ex) > 83.5:
            to_remove_tracks.append(t)
    # Also remove any leftover test vias at (101.7, 111.725) and (101.7, 115.825)
    elif t.GetClass() == 'PCB_VIA':
        if abs(sx - 101.70) < 0.1 and (abs(sy - 111.725) < 0.1 or abs(sy - 115.825) < 0.1):
            to_remove_tracks.append(t)

for t in to_remove_tracks:
    b.Remove(t)

to_remove_fps = []
for fp in b.Footprints():
    if fp.GetReference() in ['C_GPS_RST', 'R_GPS_RST']:
        to_remove_fps.append(fp)
for fp in to_remove_fps:
    b.Remove(fp)

print(f'Clean phase done, removed {len(to_remove_tracks)} tracks/vias and {len(to_remove_fps)} footprints.')

# BUILD PHASE:
# 1. Update U_GPS Pin 18 net
for fp in b.Footprints():
    if fp.GetReference() == 'U_GPS':
        for p in fp.Pads():
            if p.GetNumber() == '18':
                p.SetNet(net_rst)

# 2. Check and restore VBAT_RTC at Y=80 if missing: (101.20, 80.00) -> (101.20, 80.20)
has_80 = False
for t in b.Tracks():
    if t.GetNetname() == 'VBAT_RTC' and t.GetLayer() == pcbnew.B_Cu:
        s, e = t.GetStart(), t.GetEnd()
        sx, sy, ex, ey = s.x/1e6, s.y/1e6, e.x/1e6, e.y/1e6
        if abs(sx - 101.20) < 0.05 and abs(ex - 101.20) < 0.05 and abs(sy - 80.00) < 0.1:
            has_80 = True
if not has_80:
    t80 = pcbnew.PCB_TRACK(b)
    t80.SetStart(pcbnew.VECTOR2I(int(101.20*1e6), int(80.00*1e6)))
    t80.SetEnd(pcbnew.VECTOR2I(int(101.20*1e6), int(80.20*1e6)))
    t80.SetWidth(int(0.15*1e6)); t80.SetLayer(pcbnew.B_Cu); t80.SetNet(net_vbat); b.Add(t80)

# 3. Restore VBAT_RTC original route along X=101.20:
tv1 = pcbnew.PCB_TRACK(b)
tv1.SetStart(pcbnew.VECTOR2I(int(84.00*1e6), int(104.00*1e6)))
tv1.SetEnd(pcbnew.VECTOR2I(int(101.20*1e6), int(104.00*1e6)))
tv1.SetWidth(int(0.15*1e6)); tv1.SetLayer(pcbnew.B_Cu); tv1.SetNet(net_vbat); b.Add(tv1)

tv2 = pcbnew.PCB_TRACK(b)
tv2.SetStart(pcbnew.VECTOR2I(int(101.20*1e6), int(104.00*1e6)))
tv2.SetEnd(pcbnew.VECTOR2I(int(101.20*1e6), int(118.05*1e6)))
tv2.SetWidth(int(0.15*1e6)); tv2.SetLayer(pcbnew.B_Cu); tv2.SetNet(net_vbat); b.Add(tv2)

tv3 = pcbnew.PCB_TRACK(b)
tv3.SetStart(pcbnew.VECTOR2I(int(101.20*1e6), int(118.05*1e6)))
tv3.SetEnd(pcbnew.VECTOR2I(int(104.10*1e6), int(118.05*1e6)))
tv3.SetWidth(int(0.15*1e6)); tv3.SetLayer(pcbnew.B_Cu); tv3.SetNet(net_vbat); b.Add(tv3)

# 4. Route GPS_TX along X=106.30 on B.Cu (width=0.15):
tx1 = pcbnew.PCB_TRACK(b)
tx1.SetStart(pcbnew.VECTOR2I(int(117.10*1e6), int(96.80*1e6)))
tx1.SetEnd(pcbnew.VECTOR2I(int(106.30*1e6), int(96.80*1e6)))
tx1.SetWidth(int(0.15*1e6)); tx1.SetLayer(pcbnew.B_Cu); tx1.SetNet(net_tx); b.Add(tx1)

tx2 = pcbnew.PCB_TRACK(b)
tx2.SetStart(pcbnew.VECTOR2I(int(106.30*1e6), int(96.80*1e6)))
tx2.SetEnd(pcbnew.VECTOR2I(int(106.30*1e6), int(116.95*1e6)))
tx2.SetWidth(int(0.15*1e6)); tx2.SetLayer(pcbnew.B_Cu); tx2.SetNet(net_tx); b.Add(tx2)

tx3 = pcbnew.PCB_TRACK(b)
tx3.SetStart(pcbnew.VECTOR2I(int(106.30*1e6), int(116.95*1e6)))
tx3.SetEnd(pcbnew.VECTOR2I(int(104.10*1e6), int(116.95*1e6)))
tx3.SetWidth(int(0.15*1e6)); tx3.SetLayer(pcbnew.B_Cu); tx3.SetNet(net_tx); b.Add(tx3)

# 5. Route GPS_RX on F.Cu to (105.60, 107.00) and B.Cu along X=105.40 (width=0.15):
# F.Cu track from (106.00, 108.50) to (105.60, 107.00)
rxf = pcbnew.PCB_TRACK(b)
rxf.SetStart(pcbnew.VECTOR2I(int(106.00*1e6), int(108.50*1e6)))
rxf.SetEnd(pcbnew.VECTOR2I(int(105.60*1e6), int(107.00*1e6)))
rxf.SetWidth(int(0.15*1e6)); rxf.SetLayer(pcbnew.F_Cu); rxf.SetNet(net_rx); b.Add(rxf)

# Via at (105.60, 107.00)
via_rx = pcbnew.PCB_VIA(b)
via_rx.SetPosition(pcbnew.VECTOR2I(int(105.60*1e6), int(107.00*1e6)))
via_rx.SetWidth(int(0.60*1e6)); via_rx.SetDrill(int(0.30*1e6)); via_rx.SetNet(net_rx); b.Add(via_rx)

# B.Cu jog to X=105.40: (105.60, 107.00) -> (105.40, 107.20)
rx1 = pcbnew.PCB_TRACK(b)
rx1.SetStart(pcbnew.VECTOR2I(int(105.60*1e6), int(107.00*1e6)))
rx1.SetEnd(pcbnew.VECTOR2I(int(105.40*1e6), int(107.20*1e6)))
rx1.SetWidth(int(0.15*1e6)); rx1.SetLayer(pcbnew.B_Cu); rx1.SetNet(net_rx); b.Add(rx1)

# B.Cu vertical down X=105.40: (105.40, 107.20) -> (105.40, 115.85)
rx2 = pcbnew.PCB_TRACK(b)
rx2.SetStart(pcbnew.VECTOR2I(int(105.40*1e6), int(107.20*1e6)))
rx2.SetEnd(pcbnew.VECTOR2I(int(105.40*1e6), int(115.85*1e6)))
rx2.SetWidth(int(0.15*1e6)); rx2.SetLayer(pcbnew.B_Cu); rx2.SetNet(net_rx); b.Add(rx2)

# B.Cu to Pad 20: (105.40, 115.85) -> (104.10, 115.85)
rx3 = pcbnew.PCB_TRACK(b)
rx3.SetStart(pcbnew.VECTOR2I(int(105.40*1e6), int(115.85*1e6)))
rx3.SetEnd(pcbnew.VECTOR2I(int(104.10*1e6), int(115.85*1e6)))
rx3.SetWidth(int(0.15*1e6)); rx3.SetLayer(pcbnew.B_Cu); rx3.SetNet(net_rx); b.Add(rx3)

# 6. Add C_GPS_RST at (102.00, 112.50), rot=90 on B.Cu
c_ref = None
r_ref = None
for fp in b.Footprints():
    if fp.GetReference() == 'C_GPS1':
        c_ref = fp
    elif fp.GetReference() == 'R_LCD_CS':
        r_ref = fp

c_rst = pcbnew.Cast_to_FOOTPRINT(c_ref.Duplicate(False))
c_rst.SetReference('C_GPS_RST')
c_rst.SetValue('100nF')
c_rst.SetOrientation(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
c_rst.SetPosition(pcbnew.VECTOR2I(int(102.00*1e6), int(112.50*1e6)))
cp1 = c_rst.FindPadByNumber('1')
cp2 = c_rst.FindPadByNumber('2')
cp_rst = cp1 if cp1.GetPosition().y > cp2.GetPosition().y else cp2
cp_gnd = cp2 if cp1.GetPosition().y > cp2.GetPosition().y else cp1
cp_rst.SetNet(net_rst)
cp_gnd.SetNet(net_gnd)
b.Add(c_rst)

via_gnd = pcbnew.PCB_VIA(b)
via_gnd.SetPosition(cp_gnd.GetPosition())
via_gnd.SetWidth(int(0.60*1e6)); via_gnd.SetDrill(int(0.30*1e6)); via_gnd.SetNet(net_gnd)
b.Add(via_gnd)

# 7. Add R_GPS_RST at (102.00, 115.80), rot=90 on B.Cu
r_rst = pcbnew.Cast_to_FOOTPRINT(r_ref.Duplicate(False))
r_rst.SetReference('R_GPS_RST')
r_rst.SetValue('10k')
r_rst.SetOrientation(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
r_rst.SetPosition(pcbnew.VECTOR2I(int(102.00*1e6), int(115.80*1e6)))
rp1 = r_rst.FindPadByNumber('1')
rp2 = r_rst.FindPadByNumber('2')
rp_rst = rp1 if rp1.GetPosition().y < rp2.GetPosition().y else rp2
rp_3v3 = rp2 if rp1.GetPosition().y < rp2.GetPosition().y else rp1
rp_rst.SetNet(net_rst)
rp_3v3.SetNet(net_3v3)
b.Add(r_rst)

via_3v3 = pcbnew.PCB_VIA(b)
via_3v3.SetPosition(rp_3v3.GetPosition())
via_3v3.SetWidth(int(0.60*1e6)); via_3v3.SetDrill(int(0.30*1e6)); via_3v3.SetNet(net_3v3)
b.Add(via_3v3)

# 8. Route GPS_RESET_N (width=0.15):
# U_GPS Pad 18 (104.10, 113.65) -> (102.00, 113.65)
rst1 = pcbnew.PCB_TRACK(b)
rst1.SetStart(pcbnew.VECTOR2I(int(104.10*1e6), int(113.65*1e6)))
rst1.SetEnd(pcbnew.VECTOR2I(int(102.00*1e6), int(113.65*1e6)))
rst1.SetWidth(int(0.15*1e6)); rst1.SetLayer(pcbnew.B_Cu); rst1.SetNet(net_rst); b.Add(rst1)

rst2 = pcbnew.PCB_TRACK(b)
rst2.SetStart(pcbnew.VECTOR2I(int(102.00*1e6), int(113.65*1e6)))
rst2.SetEnd(cp_rst.GetPosition())
rst2.SetWidth(int(0.15*1e6)); rst2.SetLayer(pcbnew.B_Cu); rst2.SetNet(net_rst); b.Add(rst2)

rst3 = pcbnew.PCB_TRACK(b)
rst3.SetStart(pcbnew.VECTOR2I(int(102.00*1e6), int(113.65*1e6)))
rst3.SetEnd(rp_rst.GetPosition())
rst3.SetWidth(int(0.15*1e6)); rst3.SetLayer(pcbnew.B_Cu); rst3.SetNet(net_rst); b.Add(rst3)

b.Save(dst)
print('Complete build finished and saved.')
