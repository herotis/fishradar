import flet as ft
import requests


def main(page: ft.Page):
    page.title = "FishRadar Pro - Desktop Grid Dashboard (48 Hours)"
    page.bgcolor = "#0f2541"
    page.scroll = ft.ScrollMode.AUTO  # เปิด Scroll หน้าจอแนวตั้งเพื่อให้เลื่อนดูภาพรวมทั้งหมดได้สะดวก
    page.window_width = 1300
    page.window_height = 750
    page.window_maximized = True  # ขยายหน้าต่างเต็มจออัตโนมัติ

    LAT, LON = 7.4400, 98.2800
    W_URL = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&hourly=temperature_2m,wind_speed_10m,wind_direction_10m,precipitation,cloud_cover,pressure_msl&timezone=Asia%2FBangkok"
    M_URL = f"https://marine-api.open-meteo.com/v1/marine?latitude={LAT}&longitude={LON}&hourly=wave_height,wave_period,sea_level_height_msl&timezone=Asia%2FBangkok"

    # ใช้ ft.Row แบบ wrap=True เพื่อให้การ์ดเรียงต่อกันเป็นแถว และขึ้นบรรทัดใหม่อัตโนมัติเต็มหน้าจอ
    grid_row = ft.Row(
        spacing=12,
        run_spacing=12,
        wrap=True,
        alignment=ft.MainAxisAlignment.START,
    )

    msg = ft.Text(
        "✅ โหลดข้อมูลครบถ้วน 48 ชั่วโมงในหน้าเดียว",
        color="#00e676",
        size=14,
        weight="bold",
    )

    def load_data(e):
        try:
            w = requests.get(W_URL, timeout=10).json().get("hourly", {})
            m = requests.get(M_URL, timeout=10).json().get("hourly", {})

            grid_row.controls.clear()
            times = w.get("time", [])

            for i in range(min(48, len(times))):
                full_t = times[i].replace("T", " ")
                date_part, time_part = full_t.split(" ")

                temp = w["temperature_2m"][i]
                wind = w["wind_speed_10m"][i]
                rain = w["precipitation"][i] or 0.0
                cloud = w.get("cloud_cover", [0] * len(times))[i] or 0
                pressure = (
                    w.get("pressure_msl", [1013.0] * len(times))[i] or 1013.0
                )
                wave = m.get("wave_height", [0] * len(times))[i] or 0.3
                period = m.get("wave_period", [5] * len(times))[i] or 5.0
                sea_level = (
                    m.get("sea_level_height_msl", [0.0] * len(times))[i] or 0.0
                )
                knots = wind * 0.539957

                # แปลงค่าฝนเป็นข้อความลักษณะฝนตามเกณฑ์
                if rain == 0.0:
                    rain_desc = "ฟ้าโปร่ง / ไม่มีฝน"
                elif rain <= 0.5:
                    rain_desc = "ฟ้าครึ้ม / ละอองฝน"
                elif rain <= 2.0:
                    rain_desc = "ฝนตกเล็กน้อย"
                elif rain <= 5.0:
                    rain_desc = "ฝนตกปานกลาง"
                elif rain <= 10.0:
                    rain_desc = "ฝนตกหนัก"
                else:
                    rain_desc = "ฝนตกหนักมาก"

                # 🌊 🚨 ระบบประเมินระดับน้ำท่วมและภัยพิบัติ (Multi-Level)
                if (
                    rain > 20.0
                    or (sea_level >= 1.2 and rain > 10.0)
                    or (pressure < 1005.0 and wave > 1.5)
                    or wave > 2.0
                    or knots > 30
                ):
                    cond, bg, txt = (
                        "🚨 วิกฤตสูงสุด",
                        "#4c1d95",
                        "#e9d5ff",
                    )
                elif (
                    (rain > 10.0 and sea_level >= 1.0)
                    or rain > 15.0
                    or (sea_level >= 1.2 and rain > 2.0)
                ):
                    cond, bg, txt = (
                        "⚠️ เสี่ยงน้ำท่วม",
                        "#991b1b",
                        "#fca5a5",
                    )
                elif wave > 1.5 or knots > 25 or rain > 5.0:
                    cond, bg, txt = (
                        "⚠️ คลื่นลมแรง/ฝน",
                        "#991b1b",
                        "#fca5a5",
                    )
                elif sea_level >= 1.0 and rain > 2.0:
                    cond, bg, txt = (
                        "⚠️ น้ำหนุน/ท่วมขัง",
                        "#b45309",
                        "#fde68a",
                    )
                elif pressure < 1008.0:
                    cond, bg, txt = (
                        "⚠️ ความกดต่ำ",
                        "#b45309",
                        "#fde68a",
                    )
                elif cloud >= 85 and pressure <= 1010.0 and rain <= 0.5:
                    cond, bg, txt = (
                        "☁️ ฟ้าปิด/เมฆมาก",
                        "#b45309",
                        "#fde68a",
                    )
                elif period > 11.5:
                    cond, bg, txt = (
                        "🌊 คาบคลื่นยาว",
                        "#b45309",
                        "#fde68a",
                    )
                elif sea_level >= 1.0:
                    cond, bg, txt = (
                        "🌊 น้ำหนุนสูง",
                        "#b45309",
                        "#fde68a",
                    )
                elif rain > 0.5 or wave > 0.7 or knots > 15:
                    cond, bg, txt = (
                        "⚡ ลม/ฝนเล็กน้อย",
                        "#b45309",
                        "#fde68a",
                    )
                else:
                    cond, bg, txt = "🟢 ปลอดภัย", "#1b4332", "#69f0ae"

                # การ์ดแสดงผลขนาดกะทัดรัด จัดเรียงเป็นกริดเต็มหน้าจอ
                card = ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(
                                f"📅 {date_part}",
                                color="white70",
                                size=11,
                                weight="bold",
                            ),
                        ], alignment="spaceBetween"),
                        ft.Row([
                            ft.Text(
                                f"⏰ {time_part}",
                                weight="bold",
                                color="white",
                                size=14,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    cond, weight="bold", color=txt, size=11
                                ),
                                bgcolor="black38",
                                padding=4,
                                border_radius=4,
                            ),
                        ], alignment="spaceBetween"),
                        ft.Divider(height=2, color="white24"),
                        ft.Text(
                            f"🌡️ อากาศ: {temp}°C", color="white70", size=12
                        ),
                        ft.Text(
                            f"💨 ลม: {wind:.1f} กม./ชม. ({knots:.1f} นอต)",
                            color="white70",
                            size=12,
                        ),
                        ft.Text(
                            f"🌊 คลื่น: {wave}ม. (คาบ {period}s)",
                            color="white70",
                            size=12,
                        ),
                        ft.Text(
                            f"☁️ เมฆ: {cloud}%", color="white70", size=12
                        ),
                        ft.Text(
                            f"🌧️ ฝน: {rain} มม. ({rain_desc})",
                            color="white70",
                            size=12,
                        ),
                        ft.Text(
                            f"⏱️ ความกด: {pressure:.1f} hPa",
                            color="#ffcc80",
                            size=12,
                        ),
                        ft.Text(
                            f"🌊 ระดับน้ำ: {sea_level:+.2f} ม. (MSL)",
                            color="#90caf9",
                            size=12,
                            weight="bold",
                        ),
                    ], spacing=4),
                    bgcolor=bg,
                    padding=10,
                    border_radius=8,
                    width=225,  # กำหนดความกว้างการ์ดให้เรียงต่อกันได้ราวๆ 4-5 การ์ดต่อแถว
                )
                grid_row.controls.append(card)

        except Exception as ex:
            msg.value = f"❌ เกิดข้อผิดพลาด: {ex}"
            msg.color = "red"
            print(ex)
        page.update()

    btn = ft.Container(
        content=ft.Row([
            ft.Text("🔄 โหลดข้อมูลใหม่", color="white", weight="bold")
        ], alignment="center"),
        bgcolor="#1565C0",
        padding=8,
        border_radius=8,
        on_click=load_data,
    )

    header = ft.Row([
        ft.Text(
            "FishRadar Pro - แดชบอร์ดความปลอดภัย เกาะราชาฯ (48 ชั่วโมง) สร้างโดย Hero Tis",
            size=18,
            weight="bold",
            color="white",
        ),
        btn,
    ], alignment="spaceBetween")

    page.add(header, msg, grid_row)
    load_data(None)


if __name__ == "__main__":
    ft.run(main)