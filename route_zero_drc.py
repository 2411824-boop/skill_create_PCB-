import pcbnew, shutil

def p2i(mm):
    return int(round(mm * 1e6))

def v2i(x_mm, y_mm):
    return pcbnew.VECTOR2I(p2i(x_mm), p2i(y_mm))

# 0. Copy fresh board
shutil.copyfile('KiCad_Project/WaterSensor.kicad_pcb', 'KiCad_Project/WaterSensor_test.kicad_pcb')
b = pcbnew.LoadBoard('KiCad_Project/WaterSensor_test.kicad_pcb')

# 1. MOVE FOOTPRINTS
# U7 (DS3231) -> (103.0, 72.0), rot=0, B.Cu
u7 = b.FindFootprintByReference('U7')
u7.SetPosition(v2i(103.0, 72.0))
u7.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))

# C_RTC_VCC -> (98.35, 79.5), rot=270, B.Cu
c_rtc = b.FindFootprintByReference('C_RTC_VCC')
c_rtc.SetPosition(v2i(98.35, 79.5))
c_rtc.SetOrientation(pcbnew.EDA_ANGLE(270, pcbnew.DEGREES_T))

# U_GPS (NEO-M8N) -> (110.0, 114.2), rot=180, B.Cu
ugps = b.FindFootprintByReference('U_GPS')
ugps.SetPosition(v2i(110.0, 114.2))
ugps.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))

# J_ANT (IPEX) -> (121.0, 116.95), rot=0, B.Cu
jant = b.FindFootprintByReference('J_ANT')
jant.SetPosition(v2i(121.0, 116.95))
jant.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))

# C_GPS1 -> (101.30, 119.5), rot=180, B.Cu
cg1 = b.FindFootprintByReference('C_GPS1')
cg1.SetPosition(v2i(101.30, 119.5))
cg1.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))

# C_GPS2 -> (101.30, 121.8), rot=180, B.Cu
cg2 = b.FindFootprintByReference('C_GPS2')
cg2.SetPosition(v2i(101.30, 121.8))
cg2.SetOrientation(pcbnew.EDA_ANGLE(180, pcbnew.DEGREES_T))

print('Step 1: Footprints moved.')

# 2. SELECTIVE DELETION OF OBSOLETE TRACKS/VIAS
tracks_to_delete = []

for t in b.GetTracks():
    net = t.GetNetname()
    if t.GetClass() == 'PCB_VIA':
        v = pcbnew.Cast_to_PCB_VIA(t)
        pos = (round(v.GetPosition().x/1e6, 3), round(v.GetPosition().y/1e6, 3))
        # Delete old I2C South vias
        if (abs(pos[0]-121.5) < 0.15 and abs(pos[1]-112.0) < 0.15) or \
           (abs(pos[0]-120.5) < 0.15 and abs(pos[1]-113.0) < 0.15):
            tracks_to_delete.append(t)
        # Delete old LCD_GATE vias
        elif (abs(pos[0]-112.562) < 0.15 and abs(pos[1]-112.6) < 0.15) or \
             (abs(pos[0]-117.325) < 0.15 and abs(pos[1]-116.0) < 0.15):
            tracks_to_delete.append(t)
        # Delete old LCD_BL_PWM South via
        elif abs(pos[0]-115.675) < 0.15 and abs(pos[1]-118.5) < 0.15:
            tracks_to_delete.append(t)
        # Delete old North GPS +3V3 via
        elif abs(pos[0]-105.0) < 0.15 and abs(pos[1]-65.0) < 0.15:
            tracks_to_delete.append(t)
        # Delete old North GPS GND via
        elif abs(pos[0]-98.8) < 0.15 and abs(pos[1]-76.95) < 0.15:
            tracks_to_delete.append(t)
        # Delete old South VBAT_RTC vias at U7
        elif (abs(pos[0]-106.5) < 0.15 and abs(pos[1]-110.0) < 0.15) or \
             (abs(pos[0]-109.2) < 0.15 and abs(pos[1]-110.0) < 0.15):
            tracks_to_delete.append(t)
    else:
        layer = b.GetLayerName(t.GetLayer())
        s = (round(t.GetStart().x/1e6, 3), round(t.GetStart().y/1e6, 3))
        e = (round(t.GetEnd().x/1e6, 3), round(t.GetEnd().y/1e6, 3))
        # 2.1. GPS_ANT: delete old North track
        if net == 'GPS_ANT':
            tracks_to_delete.append(t)
        # 2.2. GPS_RX & GPS_TX: delete old tracks heading into old U_GPS
        elif net == 'GPS_RX':
            if layer == 'B.Cu' and abs(s[1]-70.35) < 0.1 and abs(e[1]-70.35) < 0.1 and max(s[0], e[0]) >= 106.0:
                tracks_to_delete.append(t)
        elif net == 'GPS_TX':
            if layer == 'B.Cu' and abs(s[1]-69.25) < 0.1 and abs(e[1]-69.25) < 0.1 and max(s[0], e[0]) >= 106.0:
                tracks_to_delete.append(t)
        # 2.3. I2C South tracks: delete tracks running south from Y=71
        elif net == 'I2C_SDA':
            if min(s[1], e[1]) >= 71.0 and (layer == 'B.Cu' or max(s[0], e[0]) >= 121.0):
                tracks_to_delete.append(t)
        elif net == 'I2C_SCL':
            if min(s[1], e[1]) >= 66.0 and (layer == 'B.Cu' or max(s[0], e[0]) >= 120.0):
                tracks_to_delete.append(t)
        # 2.4. RTC_INT: delete old B.Cu tracks running South from Y=75.5
        elif net == 'RTC_INT':
            if layer == 'B.Cu':
                tracks_to_delete.append(t)
        # 2.5. VBAT_RTC: delete old branch to U7 in South, and old stub to U_GPS in North
        elif net == 'VBAT_RTC':
            if layer == 'B.Cu':
                # Old stub to U_GPS North
                if abs(s[1]-68.15) < 0.1 and abs(e[1]-68.15) < 0.1 and min(s[0], e[0]) <= 110.0:
                    tracks_to_delete.append(t)
                # Old branch to U7 South
                elif min(s[1], e[1]) >= 105.0:
                    tracks_to_delete.append(t)
            elif layer == 'F.Cu':
                if min(s[1], e[1]) >= 105.0:
                    tracks_to_delete.append(t)
        # 2.6. LCD_GATE: delete old B.Cu tracks and F.Cu stubs to deleted vias
        elif net == 'LCD_GATE':
            if layer == 'B.Cu':
                tracks_to_delete.append(t)
            elif layer == 'F.Cu':
                if (abs(s[1]-112.6) < 0.1 or abs(e[1]-112.6) < 0.1) or \
                   (abs(s[1]-116.0) < 0.1 or abs(e[1]-116.0) < 0.1):
                    tracks_to_delete.append(t)
        # 2.7. LCD_BL_PWM: delete South stub from Y=113
        elif net == 'LCD_BL_PWM':
            if layer == 'B.Cu' and min(s[1], e[1]) >= 113.0:
                tracks_to_delete.append(t)
            elif layer == 'F.Cu' and min(s[1], e[1]) >= 117.0:
                tracks_to_delete.append(t)
        # 2.8. TDS_ADC: delete horizontal track at Y=120.5
        elif net == 'TDS_ADC':
            if layer == 'B.Cu' and abs(s[1]-120.5) < 0.1 and abs(e[1]-120.5) < 0.1 and min(s[0], e[0]) >= 111.0:
                tracks_to_delete.append(t)
        # 2.9. +3V3: delete old North U_GPS tracks and South U7 track
        elif net == '+3V3':
            if layer == 'B.Cu':
                if abs(s[1]-67.05) < 0.1 or abs(e[1]-67.05) < 0.1:
                    tracks_to_delete.append(t)
                elif abs(s[0]-105.0) < 0.1 and min(s[1], e[1]) >= 65.0 and max(s[1], e[1]) <= 68.0:
                    tracks_to_delete.append(t)
                elif abs(s[1]-115.675) < 0.1 and abs(e[1]-115.675) < 0.1 and min(s[0], e[0]) <= 104.0:
                    tracks_to_delete.append(t)
        # 2.10. GND: delete old North U_GPS GND track
        elif net == 'GND':
            if layer == 'B.Cu' and abs(s[1]-76.95) < 0.1 and abs(e[1]-76.95) < 0.1:
                tracks_to_delete.append(t)

print(f'Step 2: Found {len(tracks_to_delete)} tracks/vias to delete.')
for t in tracks_to_delete:
    b.Delete(t)

# Helper functions
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

# 3. ROUTE ALL CONNECTIONS

# 3.1. GPS_ANT (0.40mm, B.Cu, 0 via, straight line 5.1mm)
add_track('GPS_ANT', pcbnew.B_Cu, (121.0, 116.95), (115.9, 116.95), 0.40)

# 3.2. TDS_ADC: detour below Pad 1 of U_GPS
add_track('TDS_ADC', pcbnew.B_Cu, (123.8, 120.5), (123.8, 121.3), 0.20)
add_track('TDS_ADC', pcbnew.B_Cu, (123.8, 121.3), (111.325, 121.3), 0.20)
add_track('TDS_ADC', pcbnew.B_Cu, (111.325, 121.3), (111.325, 120.5), 0.20)

# 3.3. LCD_GATE (100% on F.Cu, 0 via)
add_track('LCD_GATE', pcbnew.F_Cu, (112.562, 113.55), (112.562, 112.60), 0.15)
add_track('LCD_GATE', pcbnew.F_Cu, (112.562, 112.60), (117.325, 112.60), 0.15)
add_track('LCD_GATE', pcbnew.F_Cu, (117.325, 112.60), (117.325, 117.20), 0.15)
add_track('LCD_GATE', pcbnew.F_Cu, (117.325, 117.20), (118.675, 117.20), 0.15)
add_track('LCD_GATE', pcbnew.F_Cu, (118.675, 117.20), (118.675, 119.40), 0.15)

# 3.4. LCD_BL_PWM: South route on B.Cu, via to F.Cu at Y=122.20
add_track('LCD_BL_PWM', pcbnew.B_Cu, (122.70, 113.00), (122.70, 122.20), 0.20)
add_track('LCD_BL_PWM', pcbnew.B_Cu, (122.70, 122.20), (115.675, 122.20), 0.20)
add_via('LCD_BL_PWM', (115.675, 122.20), 0.3, 0.6)
add_track('LCD_BL_PWM', pcbnew.F_Cu, (115.675, 122.20), (115.675, 117.20), 0.15)

# 3.5. RTC_INT: ESP32 Pin 9 (91.25, 67.91) -> via -> B.Cu -> U7.3 (98.35, 73.905)
add_track('RTC_INT', pcbnew.F_Cu, (91.25, 67.91), (92.50, 67.91), 0.15)
add_via('RTC_INT', (92.50, 67.91), 0.3, 0.6)
add_track('RTC_INT', pcbnew.B_Cu, (92.50, 67.91), (98.35, 67.91), 0.15)
add_track('RTC_INT', pcbnew.B_Cu, (98.35, 67.91), (98.35, 73.905), 0.15)

# 3.6. I2C_SDA for U7 (Pad 15 at 107.65, 75.175)
add_via('I2C_SDA', (110.00, 70.80), 0.3, 0.6)
add_track('I2C_SDA', pcbnew.B_Cu, (110.00, 70.80), (110.00, 75.175), 0.15)
add_track('I2C_SDA', pcbnew.B_Cu, (110.00, 75.175), (107.65, 75.175), 0.15)

# 3.7. I2C_SCL for U7 (Pad 16 at 107.65, 76.445)
add_via('I2C_SCL', (112.50, 65.00), 0.3, 0.6)
add_track('I2C_SCL', pcbnew.B_Cu, (112.50, 65.00), (112.50, 76.445), 0.15)
add_track('I2C_SCL', pcbnew.B_Cu, (112.50, 76.445), (107.65, 76.445), 0.15)

# 3.8. VBAT_RTC for U7 (Pad 14 at 107.65, 73.905)
# Tap from existing B.Cu line at (111.0, 73.905)
add_track('VBAT_RTC', pcbnew.B_Cu, (111.00, 73.905), (107.65, 73.905), 0.15)

# 3.9. +3V3 and GND for U7 and C_RTC_VCC
# U7.2 is at (98.35, 75.175), C_RTC_VCC.1 is at (98.35, 78.725)
add_track('+3V3', pcbnew.B_Cu, (98.35, 75.175), (98.35, 78.725), 0.25)
add_via('+3V3', (98.35, 77.00), 0.3, 0.6)
# C_RTC_VCC.2 is at (98.35, 80.275), via GND
add_track('GND', pcbnew.B_Cu, (98.35, 80.275), (98.35, 81.30), 0.25)
add_via('GND', (98.35, 81.30), 0.3, 0.6)
# U7.13 GND pad at (107.65, 72.635)
add_track('GND', pcbnew.B_Cu, (107.65, 72.635), (109.50, 72.635), 0.25)
add_via('GND', (109.50, 72.635), 0.3, 0.6)

# 3.10. VBAT_RTC for U_GPS (Pad 22 at 104.10, 118.05)
# Tap from existing B.Cu line at (103.20, 101.80)
add_track('VBAT_RTC', pcbnew.B_Cu, (103.20, 101.80), (103.20, 118.05), 0.15)
add_track('VBAT_RTC', pcbnew.B_Cu, (103.20, 118.05), (104.10, 118.05), 0.15)

# 3.11. +3V3 and GND for U_GPS, C_GPS1, C_GPS2
# U_GPS.23 (+3V3) at (104.10, 119.15)
# C_GPS1.1 (+3V3) at (102.075, 119.50)
# C_GPS2.1 (+3V3) at (102.075, 121.80)
add_track('+3V3', pcbnew.B_Cu, (104.10, 119.15), (102.075, 119.15), 0.30)
add_track('+3V3', pcbnew.B_Cu, (102.075, 119.15), (102.075, 119.50), 0.30)
add_track('+3V3', pcbnew.B_Cu, (102.075, 119.15), (102.075, 121.80), 0.30)
add_via('+3V3', (102.075, 119.15), 0.3, 0.6)

# GND for C_GPS1.2 (100.525, 119.50) and C_GPS2.2 (100.525, 121.80)
add_track('GND', pcbnew.B_Cu, (100.525, 119.50), (100.525, 118.50), 0.25)
add_via('GND', (100.525, 118.50), 0.3, 0.6)
add_track('GND', pcbnew.B_Cu, (100.525, 121.80), (100.525, 122.80), 0.25)
add_via('GND', (100.525, 122.80), 0.3, 0.6)

# J_ANT GND pads
add_track('GND', pcbnew.B_Cu, (121.00, 115.475), (122.50, 115.475), 0.30)
add_via('GND', (122.50, 115.475), 0.3, 0.6)
add_track('GND', pcbnew.B_Cu, (121.00, 118.425), (122.50, 118.425), 0.30)
add_via('GND', (122.50, 118.425), 0.3, 0.6)

# U_GPS GND pads fanout
add_track('GND', pcbnew.B_Cu, (115.90, 109.25), (114.20, 109.25), 0.25)
add_via('GND', (114.20, 109.25), 0.3, 0.6)
add_track('GND', pcbnew.B_Cu, (104.10, 108.15), (105.80, 108.15), 0.25)
add_via('GND', (105.80, 108.15), 0.3, 0.6)

# 3.12. GPS_RX & GPS_TX
# GPS_RX: ESP32.13 -> (105.50, 70.35) -> (123.60, 70.35) [B.Cu]
#       -> (123.60, 112.00) -> (121.00, 112.00) [F.Cu]
#       -> (106.00, 112.00) -> (106.00, 115.85) -> (104.10, 115.85) [B.Cu]
add_track('GPS_RX', pcbnew.B_Cu, (105.50, 70.35), (123.60, 70.35), 0.15)
add_via('GPS_RX', (123.60, 70.35), 0.3, 0.6)
add_track('GPS_RX', pcbnew.F_Cu, (123.60, 70.35), (123.60, 112.00), 0.15)
add_track('GPS_RX', pcbnew.F_Cu, (123.60, 112.00), (121.00, 112.00), 0.15)
add_via('GPS_RX', (121.00, 112.00), 0.3, 0.6)
add_track('GPS_RX', pcbnew.B_Cu, (121.00, 112.00), (106.00, 112.00), 0.15)
add_track('GPS_RX', pcbnew.B_Cu, (106.00, 112.00), (106.00, 115.85), 0.15)
add_track('GPS_RX', pcbnew.B_Cu, (106.00, 115.85), (104.10, 115.85), 0.15)

# GPS_TX: ESP32.16 -> (103.50, 69.25) -> (124.20, 69.25) [B.Cu]
#       -> (124.20, 112.80) -> (120.00, 112.80) [F.Cu]
#       -> (107.00, 112.80) -> (107.00, 116.95) -> (104.10, 116.95) [B.Cu]
add_track('GPS_TX', pcbnew.B_Cu, (103.50, 69.25), (124.20, 69.25), 0.15)
add_via('GPS_TX', (124.20, 69.25), 0.3, 0.6)
add_track('GPS_TX', pcbnew.F_Cu, (124.20, 69.25), (124.20, 112.80), 0.15)
add_track('GPS_TX', pcbnew.F_Cu, (124.20, 112.80), (120.00, 112.80), 0.15)
add_via('GPS_TX', (120.00, 112.80), 0.3, 0.6)
add_track('GPS_TX', pcbnew.B_Cu, (120.00, 112.80), (107.00, 112.80), 0.15)
add_track('GPS_TX', pcbnew.B_Cu, (107.00, 112.80), (107.00, 116.95), 0.15)
add_track('GPS_TX', pcbnew.B_Cu, (107.00, 116.95), (104.10, 116.95), 0.15)

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
        print('Step 4: Updated In2.Cu keepout to new GPS_ANT position.')

b.Save('KiCad_Project/WaterSensor_test.kicad_pcb')
print('Board saved to WaterSensor_test.kicad_pcb successfully!')
