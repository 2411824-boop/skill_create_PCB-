import pcbnew, subprocess, shutil
from collections import deque
import numpy as np

def p2i(mm): return int(round(mm * 1e6))
def v2i(x, y): return pcbnew.VECTOR2I(p2i(x), p2i(y))
def add_track(b, netname, layer, s_xy, e_xy, w_mm=0.15):
    t = pcbnew.PCB_TRACK(b); t.SetNet(b.FindNet(netname)); t.SetLayer(layer)
    t.SetStart(v2i(s_xy[0], s_xy[1])); t.SetEnd(v2i(e_xy[0], e_xy[1])); t.SetWidth(p2i(w_mm)); b.Add(t); return t
def add_via(b, netname, pos_xy, drill_mm=0.3, size_mm=0.6):
    v = pcbnew.PCB_VIA(b); v.SetNet(b.FindNet(netname)); v.SetPosition(v2i(pos_xy[0], pos_xy[1]))
    v.SetDrill(p2i(drill_mm)); v.SetWidth(p2i(size_mm)); v.SetTopLayer(pcbnew.F_Cu); v.SetBottomLayer(pcbnew.B_Cu); v.SetViaType(pcbnew.VIATYPE_THROUGH); b.Add(v); return v

def run_full():
    shutil.copyfile('KiCad_Project/test_zero.kicad_pcb', 'KiCad_Project/test_step.kicad_pcb')
    shutil.copyfile('KiCad_Project/test_zero.kicad_pro', 'KiCad_Project/test_step.kicad_pcb.kicad_pro')
    shutil.copyfile('KiCad_Project/test_zero.kicad_pro', 'KiCad_Project/test_step.kicad_pro')
    b = pcbnew.LoadBoard('KiCad_Project/test_step.kicad_pcb')
    c1 = b.FindFootprintByReference('C_GPS1'); c1.SetPosition(v2i(101.300, 119.500))
    c2 = b.FindFootprintByReference('C_GPS2'); c2.SetPosition(v2i(101.300, 121.500))
    for z in b.Zones():
        if z.GetIsRuleArea() and z.GetFirstLayer() == pcbnew.In2_Cu:
            poly = z.Outline(); poly.RemoveAllContours(); poly.NewOutline()
            poly.Append(v2i(115.0, 115.8)); poly.Append(v2i(122.0, 115.8)); poly.Append(v2i(122.0, 118.1)); poly.Append(v2i(115.0, 118.1))
    add_track(b,'GPS_ANT', pcbnew.B_Cu, (121.0, 116.95), (115.9, 116.95), 0.40)
    add_track(b,'TDS_ADC', pcbnew.B_Cu, (123.8, 120.5), (123.8, 121.3), 0.20)
    add_track(b,'TDS_ADC', pcbnew.B_Cu, (123.8, 121.3), (111.325, 121.3), 0.20)
    add_track(b,'TDS_ADC', pcbnew.B_Cu, (111.325, 121.3), (111.325, 120.5), 0.20)
    add_track(b,'LCD_GATE', pcbnew.F_Cu, (112.5625, 113.55), (112.5625, 112.60), 0.15)
    add_track(b,'LCD_GATE', pcbnew.F_Cu, (112.5625, 112.60), (117.325, 112.60), 0.15)
    add_track(b,'LCD_GATE', pcbnew.F_Cu, (117.325, 112.60), (117.325, 117.20), 0.15)
    add_track(b,'LCD_GATE', pcbnew.F_Cu, (117.325, 117.20), (118.675, 117.20), 0.15)
    add_track(b,'LCD_GATE', pcbnew.F_Cu, (118.675, 117.20), (118.675, 119.40), 0.15)
    add_track(b,'+3V3', pcbnew.B_Cu, (104.100, 119.150), (102.075, 119.150), 0.25)
    add_track(b,'+3V3', pcbnew.B_Cu, (102.075, 119.150), (102.075, 119.500), 0.25)
    add_track(b,'+3V3', pcbnew.B_Cu, (102.075, 119.500), (102.075, 121.500), 0.25)
    add_via(b,'+3V3', (102.075, 120.500), 0.3, 0.6)
    add_track(b,'GND', pcbnew.B_Cu, (100.525, 119.500), (100.525, 121.500), 0.25)
    add_via(b,'GND', (100.525, 120.500), 0.3, 0.6)
    add_track(b,'+3V3', pcbnew.B_Cu, (98.350, 75.175), (96.500, 75.175), 0.25)
    add_track(b,'+3V3', pcbnew.B_Cu, (96.500, 75.175), (96.500, 78.500), 0.25)
    add_track(b,'+3V3', pcbnew.B_Cu, (96.500, 78.500), (97.575, 78.500), 0.25)
    add_track(b,'+3V3', pcbnew.B_Cu, (97.575, 78.500), (97.575, 80.000), 0.25)
    add_via(b,'+3V3', (97.575, 80.000), 0.3, 0.6)
    add_track(b,'GND', pcbnew.B_Cu, (99.125, 78.500), (99.125, 80.000), 0.25)
    add_via(b,'GND', (99.125, 80.000), 0.3, 0.6)
    add_track(b,'RTC_INT', pcbnew.F_Cu, (91.250, 67.910), (88.825, 67.910), 0.15)
    add_track(b,'RTC_INT', pcbnew.F_Cu, (91.250, 67.910), (92.500, 67.910), 0.15)
    add_via(b,'RTC_INT', (92.500, 67.910), 0.3, 0.6)
    add_track(b,'RTC_INT', pcbnew.B_Cu, (92.500, 67.910), (96.500, 67.910), 0.15)
    add_track(b,'RTC_INT', pcbnew.B_Cu, (96.500, 67.910), (96.500, 73.905), 0.15)
    add_track(b,'RTC_INT', pcbnew.B_Cu, (96.500, 73.905), (98.350, 73.905), 0.15)
    add_track(b,'I2C_SDA', pcbnew.F_Cu, (108.75, 64.10), (110.80, 64.10), 0.15)
    add_track(b,'I2C_SDA', pcbnew.F_Cu, (110.80, 64.10), (110.80, 70.10), 0.15)
    add_track(b,'I2C_SDA', pcbnew.F_Cu, (110.80, 70.10), (113.175, 70.10), 0.15)
    add_via(b,'I2C_SDA', (110.80, 70.10), 0.3, 0.6)
    add_track(b,'I2C_SDA', pcbnew.B_Cu, (110.80, 70.10), (110.80, 75.175), 0.15)
    add_track(b,'I2C_SDA', pcbnew.B_Cu, (110.80, 75.175), (107.65, 75.175), 0.15)
    add_track(b,'I2C_SCL', pcbnew.F_Cu, (108.75, 60.29), (113.175, 60.29), 0.15)
    add_track(b,'I2C_SCL', pcbnew.F_Cu, (113.175, 60.29), (113.175, 66.29), 0.15)
    add_track(b,'I2C_SCL', pcbnew.F_Cu, (113.175, 66.29), (112.00, 66.29), 0.15)
    add_via(b,'I2C_SCL', (112.00, 66.29), 0.3, 0.6)
    add_track(b,'I2C_SCL', pcbnew.B_Cu, (112.00, 66.29), (112.00, 76.445), 0.15)
    add_track(b,'I2C_SCL', pcbnew.B_Cu, (112.00, 76.445), (107.65, 76.445), 0.15)
    add_track(b,'+3V3', pcbnew.F_Cu, (103.675, 117.200), (103.675, 115.450), 0.20)
    add_track(b,'+3V3', pcbnew.F_Cu, (103.675, 115.450), (104.562, 115.450), 0.20)

    # Grid build
    X_MIN,X_MAX,Y_MIN,Y_MAX=73.0,125.0,53.0,128.0
    RES=0.10
    nx=int(round((X_MAX-X_MIN)/RES))+1
    ny=int(round((Y_MAX-Y_MIN)/RES))+1
    grid_f=np.zeros((nx,ny),dtype=bool)
    grid_b=np.zeros((nx,ny),dtype=bool)
    def x2idx(x): return int(round((x-X_MIN)/RES))
    def y2idx(y): return int(round((y-Y_MIN)/RES))
    def idx2x(ix): return X_MIN+ix*RES
    def idx2y(iy): return Y_MIN+iy*RES
    CLEARANCE=0.16; TRACE_W=0.15; edge_margin=0.4
    for ix in range(nx):
        x=idx2x(ix)
        for iy in range(ny):
            y=idx2y(iy)
            if x<73.0+edge_margin or x>125.0-edge_margin or y<53.0+edge_margin or y>128.0-edge_margin:
                grid_f[ix,iy]=True; grid_b[ix,iy]=True
    def mark_track(grid,sx,sy,ex,ey,w,clr=CLEARANCE):
        r=w/2.0+clr+TRACE_W/2.0
        min_x,max_x=max(X_MIN,min(sx,ex)-r),min(X_MAX,max(sx,ex)+r)
        min_y,max_y=max(Y_MIN,min(sy,ey)-r),min(Y_MAX,max(sy,ey)+r)
        ix1,ix2=max(0,x2idx(min_x)),min(nx-1,x2idx(max_x))
        iy1,iy2=max(0,y2idx(min_y)),min(ny-1,y2idx(max_y))
        dx,dy=ex-sx,ey-sy; l2=dx*dx+dy*dy
        for ix in range(ix1,ix2+1):
            px=idx2x(ix)
            for iy in range(iy1,iy2+1):
                py=idx2y(iy)
                u=0.0 if l2==0 else max(0.0,min(1.0,((px-sx)*dx+(py-sy)*dy)/l2))
                if (px-(sx+u*dx))**2+(py-(sy+u*dy))**2<=r*r: grid[ix,iy]=True
    def mark_via_2d(vx,vy,size=0.6,clr=CLEARANCE):
        r=size/2.0+clr+TRACE_W/2.0
        for ix in range(max(0,x2idx(vx-r)),min(nx-1,x2idx(vx+r))+1):
            px=idx2x(ix)
            for iy in range(max(0,y2idx(vy-r)),min(ny-1,y2idx(vy+r))+1):
                py=idx2y(iy)
                if (px-vx)**2+(py-vy)**2<=r*r: grid_f[ix,iy]=True; grid_b[ix,iy]=True
    for t in b.GetTracks():
        if t.GetNetname() in ['VBAT_RTC','LCD_BL_PWM','GPS_RX','GPS_TX']: continue
        if t.GetClass()=='PCB_TRACK':
            l=t.GetLayer(); s,e=t.GetStart(),t.GetEnd(); sx,sy,ex,ey=s.x/1e6,s.y/1e6,e.x/1e6,e.y/1e6; w=t.GetWidth()/1e6
            if l==pcbnew.F_Cu: mark_track(grid_f,sx,sy,ex,ey,w)
            elif l==pcbnew.B_Cu: mark_track(grid_b,sx,sy,ex,ey,w)
        elif t.GetClass()=='PCB_VIA':
            pos=t.GetPosition(); mark_via_2d(pos.x/1e6,pos.y/1e6,0.6)
    for fp in b.Footprints():
        is_fid='FID' in fp.GetReference(); clr=0.65 if is_fid else CLEARANCE
        for p in fp.Pads():
            if p.GetNetname() in ['VBAT_RTC','LCD_BL_PWM','GPS_RX','GPS_TX']: continue
            bb=p.GetBoundingBox(); bx,by=bb.GetX()/1e6,bb.GetY()/1e6; bw,bh=bb.GetWidth()/1e6,bb.GetHeight()/1e6
            if p.IsOnLayer(pcbnew.F_Cu):
                r=clr+TRACE_W/2.0
                for ix in range(max(0,x2idx(bx-r)),min(nx-1,x2idx(bx+bw+r))+1):
                    for iy in range(max(0,y2idx(by-r)),min(ny-1,y2idx(by+bh+r))+1): grid_f[ix,iy]=True
            if p.IsOnLayer(pcbnew.B_Cu):
                bclr=0.40 if (fp.GetReference()=='BT1' and p.GetName()=='2') else CLEARANCE; r=bclr+TRACE_W/2.0
                for ix in range(max(0,x2idx(bx-r)),min(nx-1,x2idx(bx+bw+r))+1):
                    for iy in range(max(0,y2idx(by-r)),min(ny-1,y2idx(by+bh+r))+1): grid_b[ix,iy]=True
    mark_track(grid_f,103.675,117.200,103.675,115.450,0.20)
    mark_track(grid_f,103.675,115.450,104.562,115.450,0.20)
    def find_2d_route(grid,s_xy,t_xy):
        sx,sy=x2idx(s_xy[0]),y2idx(s_xy[1]); tx,ty=x2idx(t_xy[0]),y2idx(t_xy[1])
        saved_s=grid[sx,sy]; saved_t=grid[tx,ty]; grid[sx,sy]=False; grid[tx,ty]=False
        q=deque([(sx,sy)]); vis={(sx,sy):None}; found=None
        while q:
            curr=q.popleft()
            if curr==(tx,ty): found=curr; break
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                nc=(curr[0]+dx,curr[1]+dy)
                if 0<=nc[0]<nx and 0<=nc[1]<ny and not grid[nc[0],nc[1]]:
                    if nc not in vis: vis[nc]=curr; q.append(nc)
        grid[sx,sy]=saved_s; grid[tx,ty]=saved_t
        if not found: return None
        path=[]; c=found
        while c is not None: path.append(c); c=vis[c]
        path.reverse()
        wps=[(round(idx2x(p[0]),3),round(idx2y(p[1]),3)) for p in path]
        wps[0]=s_xy; wps[-1]=t_xy
        comp=[wps[0]]
        for i in range(1,len(wps)-1):
            prev,cur,nxt=comp[-1],wps[i],wps[i+1]
            dx1,dy1=round(cur[0]-prev[0],3),round(cur[1]-prev[1],3)
            dx2,dy2=round(nxt[0]-cur[0],3),round(nxt[1]-cur[1],3)
            if (dx1!=0 and dy2!=0) or (dy1!=0 and dx2!=0): comp.append(cur)
        comp.append(wps[-1]); return comp
    def add_route_tracks(netname,layer,wps,w_mm=0.15):
        grid=grid_f if layer==pcbnew.F_Cu else grid_b
        for i in range(len(wps)-1): add_track(b,netname,layer,wps[i],wps[i+1],w_mm); mark_track(grid,wps[i][0],wps[i][1],wps[i+1][0],wps[i+1][1],w_mm)

    # VBAT only
    p_vbat=find_2d_route(grid_b,(107.650,73.905),(85.350,94.500))
    print("VBAT path:", p_vbat)
    add_route_tracks('VBAT_RTC',pcbnew.B_Cu,p_vbat,0.15)
    add_track(b,'VBAT_RTC',pcbnew.B_Cu,(85.350,94.500),(84.000,94.500),0.15)
    add_track(b,'VBAT_RTC',pcbnew.B_Cu,(84.000,94.500),(84.000,104.000),0.15)
    add_track(b,'VBAT_RTC',pcbnew.B_Cu,(84.000,104.000),(101.200,104.000),0.15)
    add_track(b,'VBAT_RTC',pcbnew.B_Cu,(101.200,104.000),(101.200,118.050),0.15)
    add_track(b,'VBAT_RTC',pcbnew.B_Cu,(101.200,118.050),(104.100,118.050),0.15)
    b.Save('KiCad_Project/test_vbat_only.kicad_pcb')
    shutil.copyfile('KiCad_Project/test_zero.kicad_pro', 'KiCad_Project/test_vbat_only.kicad_pcb.kicad_pro')

run_full()
