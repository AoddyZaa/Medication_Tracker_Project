import io
import datetime
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIG PAGE ---
st.set_page_config(
    page_title="ระบบติดตามการจัดยาและวันนัดแพทย์ 2026",
    page_icon="💊",
    layout="wide"
)

# --- CONFIGURATION ---
SPREADSHEET_NAME = "Medication_Tracker_Data"
SHEET_NAME = "Medication_List"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

default_visit_date = "2026-10-26"
default_appt_date = "2026-12-07" # กำหนดเริ่มต้นตามที่แจ้งไว้

DEFAULT_MEDICATIONS = [
    {"แพทย์ผู้สั่งจ่าย": "หมอจุมพล", "ชื่อยา": "Less-K 5 g", "จำนวนต่อครั้ง": 1.0, "จำนวนครั้งต่อวัน": 2, "ยาคงเหลือเดิม": 0, "วันที่พบแพทย์ล่าสุด": default_visit_date, "วันที่นัดถัดไป": default_appt_date, "จำนวนที่ได้รับจริง": 0},
    {"แพทย์ผู้สั่งจ่าย": "หมอจุมพล", "ชื่อยา": "Furosemide 40 mg", "จำนวนต่อครั้ง": 2.0, "จำนวนครั้งต่อวัน": 1, "ยาคงเหลือเดิม": 0, "วันที่พบแพทย์ล่าสุด": default_visit_date, "วันที่นัดถัดไป": default_appt_date, "จำนวนที่ได้รับจริง": 0},
    {"แพทย์ผู้สั่งจ่าย": "หมอจุมพล", "ชื่อยา": "Sodamint 300 mg", "จำนวนต่อครั้ง": 1.0, "จำนวนครั้งต่อวัน": 3, "ยาคงเหลือเดิม": 0, "วันที่พบแพทย์ล่าสุด": default_visit_date, "วันที่นัดถัดไป": default_appt_date, "จำนวนที่ได้รับจริง": 0},
    {"แพทย์ผู้สั่งจ่าย": "หมอจุมพล", "ชื่อยา": "Amlodipine 5 mg", "จำนวนต่อครั้ง": 1.0, "จำนวนครั้งต่อวัน": 2, "ยาคงเหลือเดิม": 0, "วันที่พบแพทย์ล่าสุด": default_visit_date, "วันที่นัดถัดไป": default_appt_date, "จำนวนที่ได้รับจริง": 0},
    {"แพทย์ผู้สั่งจ่าย": "หมอจุมพล", "ชื่อยา": "Simvastatin 20 mg", "จำนวนต่อครั้ง": 0.5, "จำนวนครั้งต่อวัน": 1, "ยาคงเหลือเดิม": 0, "วันที่พบแพทย์ล่าสุด": default_visit_date, "วันที่นัดถัดไป": default_appt_date, "จำนวนที่ได้รับจริง": 0},
    {"แพทย์ผู้สั่งจ่าย": "หมอจุมพล", "ชื่อยา": "Doxazosin 2 mg", "จำนวนต่อครั้ง": 1.0, "จำนวนครั้งต่อวัน": 1, "ยาคงเหลือเดิม": 0, "วันที่พบแพทย์ล่าสุด": default_visit_date, "วันที่นัดถัดไป": default_appt_date, "จำนวนที่ได้รับจริง": 0},
    {"แพทย์ผู้สั่งจ่าย": "หมอจุมพล", "ชื่อยา": "Insulin 30/70 (เช้า 28 / เย็น 14 ยูนิต)", "จำนวนต่อครั้ง": 42.0, "จำนวนครั้งต่อวัน": 1, "ยาคงเหลือเดิม": 0, "วันที่พบแพทย์ล่าสุด": default_visit_date, "วันที่นัดถัดไป": default_appt_date, "จำนวนที่ได้รับจริง": 0},
    {"แพทย์ผู้สั่งจ่าย": "คุณหมอกิตติคุณ", "ชื่อยา": "Vit B. Complex", "จำนวนต่อครั้ง": 1.0, "จำนวนครั้งต่อวัน": 2, "ยาคงเหลือเดิม": 0, "วันที่พบแพทย์ล่าสุด": default_visit_date, "วันที่นัดถัดไป": default_appt_date, "จำนวนที่ได้รับจริง": 0},
]

def get_gcp_client():
    if "gcp_service_account" not in st.secrets:
        return None
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        credentials = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(credentials)
    except Exception:
        return None

def get_sheet_data():
    client = get_gcp_client()
    if not client:
        return None, DEFAULT_MEDICATIONS
    try:
        sh = client.open(SPREADSHEET_NAME)
        sheet = sh.worksheet(SHEET_NAME)
        all_values = sheet.get_all_values()
        records = []
        if len(all_values) > 1:
            headers = [str(h).strip() for h in all_values[0]]
            for row in all_values[1:]:
                padded_row = row + [""] * (len(headers) - len(row))
                records.append(dict(zip(headers, [str(v).strip() for v in padded_row])))
            return sheet, records if records else DEFAULT_MEDICATIONS
        else:
            return sheet, DEFAULT_MEDICATIONS
    except Exception:
        return None, DEFAULT_MEDICATIONS

sheet, records = get_sheet_data()

if "df_med" not in st.session_state:
    st.session_state["df_med"] = pd.DataFrame(records if records else DEFAULT_MEDICATIONS)

df_all = st.session_state["df_med"]

if "วันที่พบแพทย์ล่าสุด" not in df_all.columns:
    df_all["วันที่พบแพทย์ล่าสุด"] = default_visit_date
    st.session_state["df_med"] = df_all

# --- SIDEBAR ---
with st.sidebar:
    st.header("🩺 เลือกแพทย์ & จัดการยา")
    
    existing_doctors = df_all["แพทย์ผู้สั่งจ่าย"].dropna().unique().tolist() if not df_all.empty else ["หมอจุมพล", "คุณหมอกิตติคุณ"]
    doctor_options = existing_doctors + ["➕ เพิ่มแพทย์ใหม่..."]
    
    selected_doc_option = st.selectbox("เลือกแพทย์ผู้สั่งจ่าย:", doctor_options)
    
    if selected_doc_option == "➕ เพิ่มแพทย์ใหม่...":
        doc_name = st.text_input("ระบุชื่อแพทย์ท่านใหม่:", value="")
    else:
        doc_name = selected_doc_option

    st.markdown("---")
    st.subheader("📅 บันทึกวันนัดหมาย & คำนวณยา")
    visit_date = st.date_input("วันที่พบแพทย์ล่าสุด", value=datetime.date(2026, 10, 27))
    next_appt_date = st.date_input("วันที่แพทย์นัดครั้งต่อไป", value=datetime.date(2026, 12, 7))

    # --- ปุ่มสำหรับอัปเดตวันนัดและคำนวณจำนวนยาอัตโนมัติ ---
    if st.button("💾 บันทึก & อัปเดตวันนัดและจำนวนยา (แพทย์ท่านนี้)", use_container_width=True, type="primary"):
        if doc_name and doc_name in df_all["แพทย์ผู้สั่งจ่าย"].values:
            days = (next_appt_date - visit_date).days
            days = max(0, days)
            
            def calc_rec(row):
                if row["แพทย์ผู้สั่งจ่าย"] == doc_name:
                    try:
                        dose = float(row["จำนวนต่อครั้ง"])
                        times = int(row["จำนวนครั้งต่อวัน"])
                        remain = float(row["ยาคงเหลือเดิม"])
                        needed = max(0.0, round((dose * times * days) - remain, 1))
                        return needed
                    except Exception:
                        return row["จำนวนที่ได้รับจริง"]
                return row["จำนวนที่ได้รับจริง"]

            # อัปเดต วันที่ และ คำนวณจำนวนที่ได้รับจริง
            st.session_state["df_med"].loc[st.session_state["df_med"]["แพทย์ผู้สั่งจ่าย"] == doc_name, "วันที่พบแพทย์ล่าสุด"] = visit_date.strftime("%Y-%m-%d")
            st.session_state["df_med"].loc[st.session_state["df_med"]["แพทย์ผู้สั่งจ่าย"] == doc_name, "วันที่นัดถัดไป"] = next_appt_date.strftime("%Y-%m-%d")
            st.session_state["df_med"]["จำนวนที่ได้รับจริง"] = st.session_state["df_med"].apply(calc_rec, axis=1)

            st.success(f"🎉 อัปเดตวันนัดและคำนวณยาของ {doc_name} เรียบร้อยแล้ว! ({days} วัน)")
            st.rerun()

    if st.button("🔄 อัปเดตวันนัดและจำนวนยาให้แพทย์ทุกท่าน", use_container_width=True):
        days = (next_appt_date - visit_date).days
        days = max(0, days)

        def calc_all(row):
            try:
                dose = float(row["จำนวนต่อครั้ง"])
                times = int(row["จำนวนครั้งต่อวัน"])
                remain = float(row["ยาคงเหลือเดิม"])
                return max(0.0, round((dose * times * days) - remain, 1))
            except Exception:
                return row["จำนวนที่ได้รับจริง"]

        st.session_state["df_med"]["วันที่พบแพทย์ล่าสุด"] = visit_date.strftime("%Y-%m-%d")
        st.session_state["df_med"]["วันที่นัดถัดไป"] = next_appt_date.strftime("%Y-%m-%d")
        st.session_state["df_med"]["จำนวนที่ได้รับจริง"] = st.session_state["df_med"].apply(calc_all, axis=1)

        st.success(f"🎉 อัปเดตวันนัดและคำนวณยาของแพทย์ทุกท่านเรียบร้อยแล้ว! ({days} วัน)")
        st.rerun()

    st.markdown("---")
    st.subheader("💊 เพิ่มยาใหม่ในสังกัดแพทย์นี้")
    
    with st.form("add_med_form"):
        med_name = st.text_input("ชื่อยาใหม่", value="")
        dose_val = st.number_input("จำนวนต่อครั้ง", min_value=0.1, value=1.0, step=0.5, format="%.1f")
        times_val = st.number_input("จำนวนครั้งต่อวัน", min_value=1, value=1, step=1)
        remain_val = st.number_input("ยาคงเหลือเดิม", min_value=0.0, value=0.0, step=0.5, format="%.1f")
        
        # คำนวณยอดเริ่มต้นอัตโนมัติ
        calc_days = (next_appt_date - visit_date).days
        default_rec = max(0.0, round((dose_val * times_val * max(0, calc_days)) - remain_val, 1))
        
        received_val = st.number_input("จำนวนที่ได้รับจริง", min_value=0.0, value=default_rec, step=0.5, format="%.1f")

        submitted = st.form_submit_button("➕ เพิ่มยาเข้าระบบ", use_container_width=True)
        if submitted:
            if not doc_name.strip() or med_name.strip() == "":
                st.warning("⚠️ กรุณาระบุชื่อแพทย์และชื่อยาให้ครบถ้วนครับ")
            else:
                new_item = {
                    "แพทย์ผู้สั่งจ่าย": doc_name.strip(),
                    "ชื่อยา": med_name.strip(),
                    "จำนวนต่อครั้ง": dose_val,
                    "จำนวนครั้งต่อวัน": times_val,
                    "ยาคงเหลือเดิม": remain_val,
                    "วันที่พบแพทย์ล่าสุด": visit_date.strftime("%Y-%m-%d"),
                    "วันที่นัดถัดไป": next_appt_date.strftime("%Y-%m-%d"),
                    "จำนวนที่ได้รับจริง": received_val
                }
                st.session_state["df_med"] = pd.concat([st.session_state["df_med"], pd.DataFrame([new_item])], ignore_index=True)
                st.success("🎉 เพิ่มรายการยาสำเร็จ!")
                st.rerun()

    st.markdown("---")
    if not df_all.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_all.to_excel(writer, index=False, sheet_name='Medication')
        excel_data = output.getvalue()
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์สำรอง (.xlsx)",
            data=excel_data,
            file_name=f"med_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# --- MAIN LAYOUT ---
st.title("💊 ระบบติดตามการจัดยาและวันนัดแพทย์ 2026 ❤️")
st.markdown("---")

filter_doc = st.selectbox("🔍 กรองแสดงรายการยาตามแพทย์:", ["แสดงทั้งหมด"] + existing_doctors)

editor_df = st.session_state["df_med"].copy()
if filter_doc != "แสดงทั้งหมด":
    editor_df = editor_df[editor_df["แพทย์ผู้สั่งจ่าย"] == filter_doc]

for col in ["จำนวนต่อครั้ง", "ยาคงเหลือเดิม", "จำนวนที่ได้รับจริง"]:
    if col in editor_df.columns:
        editor_df[col] = pd.to_numeric(editor_df[col], errors='coerce').fillna(0.0)

if "จำนวนครั้งต่อวัน" in editor_df.columns:
    editor_df["จำนวนครั้งต่อวัน"] = pd.to_numeric(editor_df["จำนวนครั้งต่อวัน"], errors='coerce').fillna(1).astype(int)

st.subheader(f"📋 ตารางรายการยา (แพทย์: {filter_doc}) — สามารถแก้ไขหรือลบแถวเพื่องดยาได้โดยตรง")

edited_df = st.data_editor(
    editor_df,
    num_rows="dynamic",
    use_container_width=True,
    key="main_med_editor"
)

if st.button("💾 บันทึกการแก้ไขข้อมูลทั้งหมด", use_container_width=True):
    st.session_state["df_med"] = edited_df
    st.success("🎉 บันทึกข้อมูลเรียบร้อยแล้ว!")
    st.rerun()

st.markdown("---")
st.subheader("🔍 ตารางสรุปรายละเอียด & ตรวจสอบการจ่ายยาอัตโนมัติ")

if not edited_df.empty:
    summary_rows = []

    for _, row in edited_df.iterrows():
        doctor = str(row.get("แพทย์ผู้สั่งจ่าย", ""))
        med_name = str(row.get("ชื่อยา", ""))
        
        unit_label = "ยูนิต" if "Insulin" in med_name or "อินซูลิน" in med_name else "เม็ด"

        try:
            dose = float(row.get("จำนวนต่อครั้ง", 0))
        except Exception:
            dose = 0.0
        try:
            times = int(row.get("จำนวนครั้งต่อวัน", 0))
        except Exception:
            times = 0
        try:
            remaining = float(row.get("ยาคงเหลือเดิม", 0))
        except Exception:
            remaining = 0.0
        
        visit_str = str(row.get("วันที่พบแพทย์ล่าสุด", default_visit_date))
        appt_str = str(row.get("วันที่นัดถัดไป", default_appt_date))
        
        try:
            v_date = datetime.datetime.strptime(visit_str, "%Y-%m-%d").date()
            a_date = datetime.datetime.strptime(appt_str, "%Y-%m-%d").date()
            days_interval = (a_date - v_date).days
            if days_interval < 0:
                days_interval = 0
        except Exception:
            days_interval = 41

        try:
            received = float(row.get("จำนวนที่ได้รับจริง", 0))
        except Exception:
            received = 0.0

        total_needed = round(dose * times * days_interval, 1)
        net_needed = max(0.0, round(total_needed - remaining, 1))

        if received == 0:
            status = "รอเช็คยา ⏳"
        elif received >= net_needed:
            status = "ครบถ้วน ✅"
        else:
            diff = round(net_needed - received, 1)
            status = f"ขาด {diff} {unit_label} ⚠️"

        summary_rows.append({
            "แพทย์ผู้สั่งจ่าย": doctor,
            "ชื่อยา": med_name,
            "วันที่พบแพทย์": visit_str,
            "วันที่นัดถัดไป": appt_str,
            "จำนวนวันนัด": f"{days_interval} วัน",
            "รวมยาที่ต้องใช้": f"{total_needed} {unit_label}",
            "ยาคงเหลือเดิม": f"{remaining} {unit_label}",
            "ยาที่ต้องขอเพิ่มรอบนี้": f"{net_needed} {unit_label}",
            "ได้รับจริง": f"{received} {unit_label}",
            "สถานะเช็คยา": status
        })

    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)