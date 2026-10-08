---
name: design_and_route_kicad_pcb
description: Khảo sát dự án, đề xuất linh kiện, thẩm định nguyên lý phần cứng, và tự động đi dây mạch in KiCad 4 lớp đạt chuẩn Zero-DRC tuyệt đối (IPC-2221 Class 2). Tích hợp toàn diện các bài học chống nổ lỗi DRC, chống cô lập đảo đồng (Zone Choking), so le via vi sai, chống crash Python pcbnew và quy trình 7 bước xuất xưởng DFM.
parameters:
  type: object
  properties:
    action:
      type: string
      description: Hành động kỹ thuật cụ thể cần thực hiện trong chu trình thiết kế mạch in.
      enum:
        - intake_and_recommend
        - audit_schematic_erc
        - audit_hardware_circuit
        - auto_route_and_drc
        - compact_and_flip_bcu
        - export_manufacturing_dfm
    pcb_path:
      type: string
      description: Đường dẫn tới file bo mạch KiCad (.kicad_pcb). Bắt buộc đối với layout và DRC.
    sch_path:
      type: string
      description: Đường dẫn tới file sơ đồ nguyên lý KiCad (.kicad_sch). Bắt buộc đối với audit_schematic_erc.
    project_goal:
      type: string
      description: Mục tiêu, yêu cầu ứng dụng, môi trường hoạt động và nguồn nuôi của bo mạch.
    target_layer_count:
      type: integer
      description: Số lớp đồng thiết kế của bo mạch (mặc định 4 lớp).
      enum: [2, 4, 6]
      default: 4
    routing_layers_allowed:
      type: string
      description: Phạm vi các lớp đồng được phép đi dây tín hiệu.
      enum:
        - outer_only
        - all_layers
      default: outer_only
  required:
    - action
---

# `design_and_route_kicad_pcb` Master Skill

> **Đúc kết từ chu trình thực chiến:** Tối ưu bo mạch từ 215 lỗi DRC về chuẩn tuyệt đối **0 DRC Violations - 0 Unconnected Items - 0 Footprint Errors** theo chuẩn IPC-2221 Class 2 trên KiCad 10.

---

## GIAI ĐOẠN 0: KHẢO SÁT & CHỐT LINH KIỆN CÔNG THÁI HỌC (`intake_and_recommend`)
Khi bắt đầu dự án mới, **bắt buộc khảo sát người dùng trước khi vẽ hoặc đi dây:**
1. **Mục tiêu ứng dụng:** Thiết bị IoT quan trắc, sạc pin thông minh, mạch điều khiển hay RF cao tần.
2. **Khảo sát & Đề xuất BOM tối ưu:**
   - Đề xuất trọn bộ linh kiện công nghiệp phổ biến, chi phí thấp, footprint chuẩn SMD (0603/0805, QFN, SOIC).
   - Cảnh báo sớm rủi ro phần cứng: Dòng rò Op-Amp, quá áp ADC, tản nhiệt nguồn xung, chuẩn sạc Type-C PD.
3. **Phân bố 2 mặt bo mạch:**
   - `F.Cu`: Linh kiện to cao, cổng cắm hướng ra mép viền, nút nhấn, LED.
   - `B.Cu`: Linh kiện mỏng phẳng (GPS, pin RTC, IC RTC, điện trở/tụ phụ trợ). Tránh cấn lỗ ốc cơ khí.

---

## GIAI ĐOẠN 1: THIẾT KẾ NGUYÊN LÝ & ERC KHÔNG THIẾU THƯ VIỆN (`audit_schematic_erc`)
- **Tự trị thư viện (Zero Missing Symbol):** Script Python sinh `.kicad_sch` phải nhúng trực tiếp symbol vào khối `lib_symbols` nội bộ. Mở trên máy tính bất kỳ không bị dấu hỏi chấm (?).
- **Khung bản vẽ A3 & Net Label:** Kết nối toàn bộ tín hiệu bằng Net Label và Power Port (`+3V3`, `+5V`, `GND`, `VBUS`, `VBAT_SW`), không vẽ dây chéo rối.
- **PWR_FLAG:** Đặt `PWR_FLAG` tại các điểm cấp nguồn ngoài (`VBUS`, `VBAT_RAW`).
- **Lệnh kiểm tra ERC CLI:**
  ```bash
  kicad-cli sch erc --format json -o erc_report.json <sch_path>
  ```

---

## GIAI ĐOẠN 2: THẨM ĐỊNH 8 NHƯỢC ĐIỂM PHẦN CỨNG CHẾT NGƯỜI (`audit_hardware_circuit`)

| Khối chức năng | Lỗi nghiêm trọng thường gặp | Giải pháp kỹ thuật chuẩn xác |
| :--- | :--- | :--- |
| **Op-Amp pH** | Bipolar Op-Amp (TL072, LM358) dòng rò lớn làm sai que đo trở kháng cao ($100\text{ M}\Omega$). | Dùng CMOS/JFET Op-Amp $I_b < 1\text{ pA}$ (LMC6001, LMC6482, OPA333) nguồn đơn 5V. Đi 100% trên `F.Cu`, **0 via**. |
| **Mạch Offset pH** | Bơm áp offset vào que đo nóng BNC gây sai số. | Bơm offset vào chân vỏ que đo BNC (Pin 2 Reference). Cô lập đường que đo nóng, bọc Guard Ring. |
| **Mạch đo TDS** | Cấp nguồn liên tục làm điện phân nước, trôi pH; quá áp chân ADC MCU. | Dùng N-MOSFET (2N7002) kích xung khi đo và ngắt khi nghỉ. Thêm cầu phân áp trước ADC ($V_{ADC} \le 3.3\text{V}$). |
| **Mạch đo Pin** | Cầu chia áp nối trước switch (`VBAT_RAW`), gây rò dòng kiệt pin khi tắt nguồn. | Chuyển điểm lấy nguồn sang sau công tắc (`VBAT_SW`). Tắt máy dòng rò bằng $0\mu\text{A}$. |
| **USB Type-C** | Nối chung CC1/CC2 hoặc thiếu trở kéo mass, củ sạc PD ngắt nguồn. | Đấu 2 trở $5.1\text{ k}\Omega$ độc lập từ CC1 và CC2 xuống GND. |
| **Bảo vệ Pin DW01A** | Nối nhầm chân 4 GND của DW01A vào System GND; sai chân Drain FS8205A. | Pin 1 & 6 FS8205A nối chung thành Drain. Chân 4 DW01A nối cực âm pin (`BAT-`), cách ly với System GND $\ge 2.0\text{ mm}$. |
| **Nguồn Boost MT3608** | Vòng lặp $di/dt$ lớn, node SW đi via phát xạ EMI cao tần $1.2\text{ MHz}$. | Đặt tụ $C_{OUT}$ sát Diode $D_1$. Node SW cực ngắn bản rộng $0.40\text{ mm}$, **0 via**. Đường hồi tiếp FB đi xa cuộn cảm trên `B.Cu`. |
| **Anten RF (ESP32/GPS)** | Đồng/silkscreen nằm dưới anten làm tụt sóng; đường GPS bị nhiễu xung TDS. | Khoét thủng RF Keepout cả 4 lớp dưới anten ESP32. Đường GPS chạy vi dải 50-ohm trên `B.Cu` cách xa xung TDS $\ge 3.0\text{ mm}$. |

---

## GIAI ĐOẠN 3: KIẾN TRÚC STACKUP 4 LỚP & QUY TẮC NETCLASS IPC-2221 CLASS 2

### 1. Phân tầng 4 lớp chuẩn:
- **`F.Cu` (Top):** Tín hiệu vi sai, analog nhạy cảm, linh kiện mặt trên + phủ đồng GND tản nhiệt có chấu hoa thị ($0.25\text{ mm}$ gap, $0.35\text{ mm}$ spoke).
- **`In1.Cu` (Inner 1 - Solid GND Plane):** Mặt phẳng tiếp địa liên tục 100%, tuyệt đối không xẻ rãnh làm đứt return path.
- **`In2.Cu` (Inner 2 - Split Power Plane):** Chia đôi điện áp nội tầng (`+3V3` nửa Bắc, `+5V` nửa Nam). Cách ly ranh giới $\ge 0.5\text{ mm}$.
- **`B.Cu` (Bottom):** Linh kiện đáy, chùm bus tốc độ cao, vi dải RF 50-ohm + phủ đồng GND toàn diện.

### 2. Kích thước hình học & Netclass (Cực kỳ quan trọng để không nổ lỗi DRC):
- Clearance đồng - đồng (Trace-Trace, Trace-Pad): $\ge 0.15\text{ mm}$.
- Clearance lỗ khoan (Hole-Hole, Hole-Pad): $\ge 0.25\text{ mm}$.
- Clearance mép bo mạch (Board Edge): $\ge 0.30\text{ mm}$.
- Via chuẩn tín hiệu: Đường kính $0.60\text{ mm}$, khoan $0.30\text{ mm}$.
- Via nguồn công suất: Đường kính $0.80\text{ mm}$, khoan $0.40\text{ mm}$ hoặc 2-3 via $0.6/0.3\text{ mm}$ song song.
- **Lưu ý sống còn về `.kicad_pro`:** Bắt buộc đồng bộ file `.kicad_pro` với quy tắc `classes[0].clearance: 0.15`. Nếu thiếu, KiCad sẽ fallback về $0.20\text{ mm}$ và báo giả hàng trăm lỗi clearance.

---

## GIAI ĐOẠN 4: 4 ĐỊNH LÝ HÌNH HỌC ĐỊNH TUYẾN & CHỐNG CÔ LẬP ĐẢO ĐỒNG (`auto_route_and_drc`)

### 1. Định Lý Lồng Ghép Hình Học Phẳng (Planar Topology Embedding)
- Khi định tuyến chùm bus $N$ đường song song (SPI, LCD bus):
- Thứ tự phân bổ tọa độ hành lang dây phải là một hàm đơn điệu đồng biến với thứ tự chân cắm:
  $$\text{Index}(S_i) < \text{Index}(S_j) \iff X_{\text{channel}}(S_i) < X_{\text{channel}}(S_j)$$
- **Triệt tiêu 100% điểm cắt chéo** mà không cần via đảo tầng.

### 2. Hầm Chui So Le Trục Dọc (Staggered Underpass)
- Dành cho cặp tín hiệu vi sai (USB D+/D-) hoặc dây cắt ngang đại lộ bus:
- 1 dây đi thẳng trên `F.Cu`, dây còn lại hạ via chui qua hầm ngang trên `B.Cu` rồi trồi lên lại.
- Trục via chuyển tầng phải so le dọc trục:
  $$\Delta X = |X_{\text{via1}} - X_{\text{via2}}| \ge 2.0\text{ mm} \gg \text{Min Clearance}$$
- Tuyệt đối không đặt via cạnh nhau song song gây nghẽn via-to-via clearance.

### 3. Kỹ Thuật Giải Phóng Hành Lang Đảo Đồng (Zone Corridor Liberation)
- **Hiện tượng Zone Choking:** Một pad GND trông chờ vào lớp phủ đồng mặt ngoài nhưng bị một đường track nguồn/tín hiệu chạy ngang tạo "đê chắn", biến thành đảo cô lập sinh lỗi `unconnected_items`.
- **Giải pháp:** Cấm chạy track ngang dài cấp nguồn trên mặt ngoài. Thay thế bằng **via độc lập cắm trực tiếp từ plane nội hoặc mặt đối diện**, giải phóng hành lang trống $\ge 2.0\text{ mm}$ cho đồng mass tự do tràn vào pad.

### 4. Quy Tắc Tránh Xung Đột Via Với Chân Xuyên Lỗ (PTH Collision Audit)
- Chân xuyên lỗ (PTH pad) nối GND đã tự động ăn thông vào plane `In1.Cu`.
- **Cấm đặt thêm via GND phụ sát chân PTH** (vi phạm hole-to-hole $< 0.25\text{ mm}$).
- Bắt buộc lọc trùng tọa độ via trước khi add: $|X_1 - X_2| < 0.1 \land |Y_1 - Y_2| < 0.1 \implies$ Bỏ qua.

---

## GIAI ĐOẠN 5: CẨM NANG PYTHON PCBNEW TRÁNH CRASH & VÒNG LẶP DRC

### 1. Quy tắc an toàn bộ nhớ C++ trong KiCad 10 Python API
```python
# 1. Tránh Segfault 139: Gom danh sách trước, xóa sau (không xóa khi đang lặp container)
tracks_to_remove = [t for t in board.GetTracks() if condition(t)]
for t in tracks_to_remove:
    board.Remove(t)

# 2. Truy xuất Footprint trong KiCad 10:
pad.GetParentFootprint().GetReference()  # KHÔNG dùng pad.GetParent().GetReference()

# 3. Fill zone an toàn:
zone.GetFilledPolysList(zone.GetLayer()) # Bắt buộc truyền tham số layer
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
```

### 2. Vòng lặp kiểm tra DRC CLI chuẩn
```bash
& "E:\KidCad\bin\kicad-cli.exe" pcb drc --severity-all --refill-zones -o drc_report.rpt <pcb_path>
```
Tiêu chí nghiệm thu tuyệt đối:
```text
Total Violations: 0
Total Unconnected: 0
Total Footprint Errors: 0
```

---

## GIAI ĐOẠN 6: DFM & XUẤT XƯỞNG SẢN XUẤT (`export_manufacturing_dfm`)
- Bo tròn 4 góc viền bo (`Edge.Cuts`) $R = 2.0\text{ mm}$ chống sứt mẻ khi cắt CNC.
- Đặt 4 lỗ ốc M3 cách mép $\ge 4.0\text{ mm}$, vùng cấm đi dây quanh lỗ ốc $\ge 1.0\text{ mm}$.
- Đặt 3 điểm định vị quang học (Fiducials: FID1, FID2, FID3) so le tại 3 góc.
- Lệnh xuất bộ tệp sản xuất Gerber & Drill:
  ```bash
  kicad-cli pcb export gerbers -o gerber/ <pcb_path>
  kicad-cli pcb export drill -o gerber/ <pcb_path>
  ```
