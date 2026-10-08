import pcbnew, shutil

def p2i(mm):
    return int(round(mm * 1e6))

def v2i(x_mm, y_mm):
    return pcbnew.VECTOR2I(p2i(x_mm), p2i(y_mm))

shutil.copyfile('KiCad_Project/WaterSensor.kicad_pcb', 'KiCad_Project/WaterSensor_test.kicad_pcb')
b = pcbnew.LoadBoard('KiCad_Project/WaterSensor_test.kicad_pcb')

# 1. MOVE FOOTPRINTS
# U7 (DS3231) -> (103.0, 72.0) rot=0
u7 = b.FindFootprintByReference('U7')
u7.SetPosition(v2i(103.0, 72.0))
u7.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))

# C_RTC_VCC -> (98.35, 79.5) rot=0
c_rtc = b.FindFootprintByReference('C_RTC_VCC')
c_rtc.SetPosition(v2i(98.35, 79.5))
c_rtc.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))

# U_GPS (NEO-M8N) -> (110.0, 114.2) rot=180
ugps = b.FindFootprintByReference('U_GPS')
ugps.SetPosition(v2i(110.0, 114.2))
ugps.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))

# J_ANT (IPEX) -> (121.0, 116.95) rot=0
jant = b.FindFootprintByReference('J_ANT')
jant.SetPosition(v2i(121.0, 116.95))
jant.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))

# C_GPS1 -> (101.5, 119.15) rot=0
cg1 = b.FindFootprintByReference('C_GPS1')
cg1.SetPosition(v2i(101.5, 119.15))
cg1.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))

# C_GPS2 -> (98.0, 119.15) rot=180
cg2 = b.FindFootprintByReference('C_GPS2')
cg2.SetPosition(v2i(98.0, 119.15))
cg2.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))

print('Footprints moved.')

# 2. DELETE OLD TRACKS/VIAS OF RELOCATED NETS
nets_to_clean_entirely = {
    'GPS_ANT', 'GPS_RX', 'GPS_TX',
    'I2C_SDA', 'I2C_SCL', 'RTC_INT',
    'VBAT_RTC', 'LCD_GATE', 'LCD_BL_PWM'
}

tracks_to_delete = []

for t in b.GetTracks():
    netname = t.GetNetname()
    if netname in nets_to_clean_entirely:
        tracks_to_delete.append(t)
    elif netname == '+3V3':
        s = (t.GetStart().x/1e6, t.GetStart().y/1e6)
        e = (t.GetEnd().x/1e6, t.GetEnd().y/1e6)
        if t.GetLayerName() == 'B.Cu':
            # Old tracks feeding U_GPS (+3V3 pad 23) in North
            if min(s[0], e[0]) >= 104.0 and max(s[0], e[0]) <= 110.0 and min(s[1], e[1]) >= 64.0 and max(s[1], e[1]) <= 68.0:
                tracks_to_delete.append(t)
            # Old tracks feeding U7 (+3V3 pad 2) in South (keep (104.85..107.0, 115.67) and via at 107.0 for Q1/R_TDS_PD)
            elif min(s[0], e[0]) >= 101.0 and max(s[0], e[0]) <= 104.0 and min(s[1], e[1]) >= 115.0 and max(s[1], e[1]) <= 116.5:
                tracks_to_delete.append(t)
        elif t.GetClass() == 'PCB_VIA':
            pos = (t.GetPosition().x/1e6, t.GetPosition().y/1e6)
            if abs(pos[0]-105.0) < 0.1 and abs(pos[1]-65.0) < 0.1:
                tracks_to_delete.append(t)
    elif netname == 'GND':
        s = (t.GetStart().x/1e6, t.GetStart().y/1e6)
        e = (t.GetEnd().x/1e6, t.GetEnd().y/1e6)
        if t.GetLayerName() == 'B.Cu':
            # Delete old tracks at U7 GND pins in South
            if min(s[0], e[0]) >= 96.0 and max(s[0], e[0]) <= 99.0 and abs(s[1]-76.95) < 0.2:
                tracks_to_delete.append(t)
        elif t.GetClass() == 'PCB_VIA':
            pos = (t.GetPosition().x/1e6, t.GetPosition().y/1e6)
            if abs(pos[0]-98.80) < 0.1 and abs(pos[1]-76.95) < 0.1:
                tracks_to_delete.append(t)

print(f'Deleting {len(tracks_to_delete)} tracks/vias...')
for t in tracks_to_delete:
    b.Delete(t)

# Helper functions
def add_track(netname, layer, start_xy, end_xy, width_mm=0.20):
    t = pcbnew.PCB_TRACK(b)
    net = b.FindNet(netname)
    t.SetNet(net)
    t.SetLayer(layer)
    t.SetStart(v2i(start_xy[0], start_xy[1]))
    t.SetEnd(v2i(end_xy[0], end_xy[1]))
    t.SetWidth(p2i(width_mm))
    b.Add(t)
    return t

def add_via(netname, pos_xy, drill_mm=0.3, size_mm=0.6, top_layer=pcbnew.F_Cu, bottom_layer=pcbnew.B_Cu):
    v = pcbnew.PCB_VIA(b)
    net = b.FindNet(netname)
    v.SetNet(net)
    v.SetPosition(v2i(pos_xy[0], pos_xy[1]))
    v.SetDrill(p2i(drill_mm))
    v.SetWidth(p2i(size_mm))
    v.SetTopLayer(top_layer)
    v.SetBottomLayer(bottom_layer)
    v.SetViaType(pcbnew.VIATYPE_THROUGH if (top_layer==pcbnew.F_Cu and bottom_layer==pcbnew.B_Cu) else pcbnew.VIATYPE_BLIND)
    b.Add(v)
    return v

# 3. ROUTE ALL RELOCATED NETS

# === 3.1. GPS_ANT (0.40mm on B.Cu, 50-ohm, 0 via) ===
# From J_ANT.1 (121.0, 116.95) to U_GPS.4 (115.90, 116.95)
add_track('GPS_ANT', pcbnew.B_Cu, (121.00, 116.95), (115.90, 116.95), 0.40)

# === 3.2. LCD_GATE (100% on F.Cu, 0 via) ===
# From Q2.1 (112.5625, 113.55) to R_LCD_GATE.2 (117.325, 117.20)
add_track('LCD_GATE', pcbnew.F_Cu, (112.5625, 113.55), (112.5625, 113.00), 0.20)
add_track('LCD_GATE', pcbnew.F_Cu, (112.5625, 113.00), (117.325, 113.00), 0.20)
add_track('LCD_GATE', pcbnew.F_Cu, (117.325, 113.00), (117.325, 117.20), 0.20)
# R_LCD_GATE.2 to R_LCD_PD.1 (118.675, 119.40)
add_track('LCD_GATE', pcbnew.F_Cu, (117.325, 117.20), (118.675, 117.20), 0.20)
add_track('LCD_GATE', pcbnew.F_Cu, (118.675, 117.20), (118.675, 119.40), 0.20)

# === 3.3. LCD_BL_PWM ===
# From ESP32 Pin 10 (91.25, 66.64) to R_LCD_GATE.1 (115.675, 117.20)
# F.Cu: (91.25, 66.64) -> (93.8, 66.64) -> (93.8, 62.3) -> (103.5, 62.3)
add_track('LCD_BL_PWM', pcbnew.F_Cu, (91.25, 66.64), (93.80, 66.64), 0.20)
add_track('LCD_BL_PWM', pcbnew.F_Cu, (93.80, 66.64), (93.80, 62.30), 0.20)
add_track('LCD_BL_PWM', pcbnew.F_Cu, (93.80, 62.30), (103.50, 62.30), 0.20)
add_via('LCD_BL_PWM', (103.50, 62.30), 0.3, 0.6, pcbnew.F_Cu, pcbnew.B_Cu)
# B.Cu: (103.5, 62.30) -> (104.5, 60.50) -> (116.8, 60.50) -> (116.8, 62.50) -> (122.7, 62.50)
add_track('LCD_BL_PWM', pcbnew.B_Cu, (103.50, 62.30), (104.50, 60.50), 0.20)
add_track('LCD_BL_PWM', pcbnew.B_Cu, (104.50, 60.50), (116.80, 60.50), 0.20)
add_track('LCD_BL_PWM', pcbnew.B_Cu, (116.80, 60.50), (116.80, 62.50), 0.20)
add_track('LCD_BL_PWM', pcbnew.B_Cu, (116.80, 62.50), (122.70, 62.50), 0.20)
# Down East edge on B.Cu:
add_track('LCD_BL_PWM', pcbnew.B_Cu, (122.70, 62.50), (122.70, 114.50), 0.20)
add_track('LCD_BL_PWM', pcbnew.B_Cu, (122.70, 114.50), (118.00, 114.50), 0.20)
add_via('LCD_BL_PWM', (118.00, 114.50), 0.3, 0.6, pcbnew.F_Cu, pcbnew.B_Cu)
add_track('LCD_BL_PWM', pcbnew.F_Cu, (118.00, 114.50), (115.675, 114.50), 0.20)
add_track('LCD_BL_PWM', pcbnew.F_Cu, (115.675, 114.50), (115.675, 117.20), 0.20)

# === 3.4. I2C_SDA to U7.15 (107.65, 75.175) and header J_BOOT (121.0, 70.80) ===
# From ESP32 Pin 33 (108.75, 64.10) to U7.15 and J_BOOT
add_track('I2C_SDA', pcbnew.F_Cu, (108.75, 64.10), (111.50, 64.10), 0.20)
add_track('I2C_SDA', pcbnew.F_Cu, (111.50, 64.10), (111.50, 70.80), 0.20)
add_track('I2C_SDA', pcbnew.F_Cu, (111.50, 70.80), (121.00, 70.80), 0.20)
# Via to B.Cu at (110.0, 70.80) for U7.15:
add_track('I2C_SDA', pcbnew.F_Cu, (111.50, 70.80), (110.00, 70.80), 0.20)
add_via('I2C_SDA', (110.00, 70.80), 0.3, 0.6, pcbnew.F_Cu, pcbnew.B_Cu)
add_track('I2C_SDA', pcbnew.B_Cu, (110.00, 70.80), (110.00, 75.175), 0.20)
add_track('I2C_SDA', pcbnew.B_Cu, (110.00, 75.175), (107.65, 75.175), 0.20)

# === 3.5. I2C_SCL to U7.16 (107.65, 76.445) and header J_BOOT (121.0, 65.00) ===
# From ESP32 Pin 36 (108.75, 60.29) to U7.16 and J_BOOT
add_track('I2C_SCL', pcbnew.F_Cu, (108.75, 60.29), (113.175, 60.29), 0.20)
add_track('I2C_SCL', pcbnew.F_Cu, (113.175, 60.29), (113.175, 65.00), 0.20)
add_track('I2C_SCL', pcbnew.F_Cu, (113.175, 65.00), (121.00, 65.00), 0.20)
# Via to B.Cu at (111.50, 65.00) for U7.16:
add_track('I2C_SCL', pcbnew.F_Cu, (113.175, 65.00), (111.50, 65.00), 0.20)
add_via('I2C_SCL', (111.50, 65.00), 0.3, 0.6, pcbnew.F_Cu, pcbnew.B_Cu)
add_track('I2C_SCL', pcbnew.B_Cu, (111.50, 65.00), (111.50, 76.445), 0.20)
add_track('I2C_SCL', pcbnew.B_Cu, (111.50, 76.445), (107.65, 76.445), 0.20)

# === 3.6. RTC_INT to U7.3 (98.35, 73.905) ===
# From ESP32 Pin 9 (91.25, 67.91)
add_track('RTC_INT', pcbnew.F_Cu, (91.25, 67.91), (88.00, 67.91), 0.20)
add_track('RTC_INT', pcbnew.F_Cu, (88.00, 67.91), (88.00, 73.905), 0.20)
add_via('RTC_INT', (88.00, 73.905), 0.3, 0.6, pcbnew.F_Cu, pcbnew.B_Cu)
add_track('RTC_INT', pcbnew.B_Cu, (88.00, 73.905), (98.35, 73.905), 0.20)

# === 3.7. VBAT_RTC ===
# BT1.1 (85.35, 94.50) on B.Cu to U_GPS.22 (104.10, 118.05) on B.Cu:
add_track('VBAT_RTC', pcbnew.B_Cu, (85.35, 94.50), (84.00, 94.50), 0.20)
add_track('VBAT_RTC', pcbnew.B_Cu, (84.00, 94.50), (84.00, 101.80), 0.20)
add_track('VBAT_RTC', pcbnew.B_Cu, (84.00, 101.80), (104.10, 101.80), 0.20)
add_track('VBAT_RTC', pcbnew.B_Cu, (104.10, 101.80), (104.10, 118.05), 0.20)
# BT1.1 to U7.14 (107.65, 73.905) on B.Cu:
# From (84.00, 94.50) go North on B.Cu outside keepout:
add_track('VBAT_RTC', pcbnew.B_Cu, (84.00, 94.50), (84.00, 81.00), 0.20)
add_via('VBAT_RTC', (84.00, 81.00), 0.3, 0.6, pcbnew.F_Cu, pcbnew.B_Cu)
add_track('VBAT_RTC', pcbnew.F_Cu, (84.00, 81.00), (87.00, 81.00), 0.20)
add_track('VBAT_RTC', pcbnew.F_Cu, (87.00, 81.00), (87.00, 76.50), 0.20)
add_track('VBAT_RTC', pcbnew.F_Cu, (87.00, 76.50), (105.00, 76.50), 0.20)
add_via('VBAT_RTC', (105.00, 76.50), 0.3, 0.6, pcbnew.F_Cu, pcbnew.B_Cu)
add_track('VBAT_RTC', pcbnew.B_Cu, (105.00, 76.50), (107.65, 76.50), 0.20)
add_track('VBAT_RTC', pcbnew.B_Cu, (107.65, 76.50), (107.65, 73.905), 0.20)

# === 3.8. GPS_RX & GPS_TX (East corridor via B.Cu) ===
# GPS_RX from U6.13 (91.25, 72.99) to U_GPS.20 (104.10, 115.85)
add_track('GPS_RX', pcbnew.F_Cu, (91.25, 72.99), (94.00, 72.99), 0.20)
add_track('GPS_RX', pcbnew.F_Cu, (94.00, 72.99), (94.00, 61.20), 0.20)
add_track('GPS_RX', pcbnew.F_Cu, (94.00, 61.20), (104.50, 61.20), 0.20)
add_via('GPS_RX', (104.50, 61.20), 0.3, 0.6, pcbnew.F_Cu, pcbnew.B_Cu)
add_track('GPS_RX', pcbnew.B_Cu, (104.50, 61.20), (117.00, 61.20), 0.20)
add_track('GPS_RX', pcbnew.B_Cu, (117.00, 61.20), (117.00, 63.50), 0.20)
add_track('GPS_RX', pcbnew.B_Cu, (117.00, 63.50), (123.40, 63.50), 0.20)
add_track('GPS_RX', pcbnew.B_Cu, (123.40, 63.50), (123.40, 113.50), 0.20)
add_track('GPS_RX', pcbnew.B_Cu, (123.40, 113.50), (106.00, 113.50), 0.20)
add_track('GPS_RX', pcbnew.B_Cu, (106.00, 113.50), (106.00, 115.85), 0.20)
add_track('GPS_RX', pcbnew.B_Cu, (106.00, 115.85), (104.10, 115.85), 0.20)

# GPS_TX from U6.16 (95.56, 75.51) to U_GPS.21 (104.10, 116.95)
add_track('GPS_TX', pcbnew.F_Cu, (95.56, 75.51), (95.56, 60.50), 0.20)
add_track('GPS_TX', pcbnew.F_Cu, (95.56, 60.50), (105.50, 60.50), 0.20)
add_via('GPS_TX', (105.50, 60.50), 0.3, 0.6, pcbnew.F_Cu, pcbnew.B_Cu)
add_track('GPS_TX', pcbnew.B_Cu, (105.50, 60.50), (118.00, 60.50), 0.20)
add_track('GPS_TX', pcbnew.B_Cu, (118.00, 60.50), (118.00, 64.20), 0.20)
add_track('GPS_TX', pcbnew.B_Cu, (118.00, 64.20), (124.00, 64.20), 0.20)
add_track('GPS_TX', pcbnew.B_Cu, (124.00, 64.20), (124.00, 112.50), 0.20)
add_track('GPS_TX', pcbnew.B_Cu, (124.00, 112.50), (107.00, 112.50), 0.20)
add_track('GPS_TX', pcbnew.B_Cu, (107.00, 112.50), (107.00, 116.95), 0.20)
add_track('GPS_TX', pcbnew.B_Cu, (107.00, 116.95), (104.10, 116.95), 0.20)

# === 3.9. +3V3 POWER FANOUT ===
# U7.2 (+3V3 at 98.35, 75.175) to C_RTC_VCC.1 (97.575, 79.5) and In2.Cu plane:
add_track('+3V3', pcbnew.B_Cu, (98.35, 75.175), (98.35, 78.00), 0.25)
add_track('+3V3', pcbnew.B_Cu, (98.35, 78.00), (97.575, 78.00), 0.25)
add_track('+3V3', pcbnew.B_Cu, (97.575, 78.00), (97.575, 79.50), 0.25)
add_via('+3V3', (97.575, 78.00), 0.3, 0.6, pcbnew.B_Cu, pcbnew.In2_Cu)

# U_GPS.23 (+3V3 at 104.10, 119.15) to C_GPS1.1 (100.725, 119.15) & C_GPS2.1 (98.95, 119.15):
add_track('+3V3', pcbnew.B_Cu, (104.10, 119.15), (100.725, 119.15), 0.30)
add_track('+3V3', pcbnew.B_Cu, (100.725, 119.15), (98.950, 119.15), 0.30)
add_track('+3V3', pcbnew.B_Cu, (98.950, 119.15), (96.500, 119.15), 0.30)
add_via('+3V3', (96.500, 119.15), 0.3, 0.6, pcbnew.B_Cu, pcbnew.In2_Cu)

# === 3.10. GND FANOUT ===
# C_RTC_VCC.2 (99.125, 79.5) to In1.Cu:
add_track('GND', pcbnew.B_Cu, (99.125, 79.50), (99.125, 81.00), 0.25)
add_via('GND', (99.125, 81.00), 0.3, 0.6, pcbnew.B_Cu, pcbnew.In1_Cu)

# U7.13 (GND at 107.65, 72.635) to In1.Cu:
add_track('GND', pcbnew.B_Cu, (107.65, 72.635), (109.50, 72.635), 0.25)
add_via('GND', (109.50, 72.635), 0.3, 0.6, pcbnew.B_Cu, pcbnew.In1_Cu)

# C_GPS1.2 (102.275, 119.15) & C_GPS2.2 (97.050, 119.15) to In1.Cu:
add_track('GND', pcbnew.B_Cu, (102.275, 119.15), (102.275, 117.80), 0.25)
add_via('GND', (102.275, 117.80), 0.3, 0.6, pcbnew.B_Cu, pcbnew.In1_Cu)
add_track('GND', pcbnew.B_Cu, (97.050, 119.15), (97.050, 117.80), 0.25)
add_via('GND', (97.050, 117.80), 0.3, 0.6, pcbnew.B_Cu, pcbnew.In1_Cu)

# J_ANT GND pads (121.0, 115.475) & (121.0, 118.425) to In1.Cu:
add_track('GND', pcbnew.B_Cu, (121.00, 115.475), (122.50, 115.475), 0.30)
add_via('GND', (122.50, 115.475), 0.3, 0.6, pcbnew.B_Cu, pcbnew.In1_Cu)
add_track('GND', pcbnew.B_Cu, (121.00, 118.425), (122.50, 118.425), 0.30)
add_via('GND', (122.50, 118.425), 0.3, 0.6, pcbnew.B_Cu, pcbnew.In1_Cu)

# U_GPS GND pads fanout to In1.Cu:
add_track('GND', pcbnew.B_Cu, (115.90, 109.25), (114.20, 109.25), 0.25)
add_via('GND', (114.20, 109.25), 0.3, 0.6, pcbnew.B_Cu, pcbnew.In1_Cu)
add_track('GND', pcbnew.B_Cu, (104.10, 108.15), (105.80, 108.15), 0.25)
add_via('GND', (105.80, 108.15), 0.3, 0.6, pcbnew.B_Cu, pcbnew.In1_Cu)

# 4. UPDATE RULE AREA KEEPOUT ON In2.Cu
for z in b.Zones():
    if z.GetIsRuleArea() and z.GetFirstLayer() == pcbnew.In2_Cu:
        poly = z.Outline()
        poly.RemoveAllContours()
        poly.NewOutline()
        poly.Append(v2i(115.0, 115.8))
        poly.Append(v2i(122.0, 115.8))
        poly.Append(v2i(122.0, 118.1))
        poly.Append(v2i(115.0, 118.1))
        print('Updated In2.Cu rule area keepout to new GPS_ANT position')

# 5. SAVE
b.Save('KiCad_Project/WaterSensor_test.kicad_pcb')
print('Board saved successfully to WaterSensor_test.kicad_pcb!')
