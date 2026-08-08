
import json
import os
from datetime import datetime, timedelta
import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import streamlit as st

st.set_page_config(
    page_title="UHS Bhawal - Teacher Adjustment",
    page_icon="🏫",
    layout="centered",
)

HISTORY_FILE = "adjustment_history.json"

all_teachers = [
    "SAURABH KUMAR",
    "ARCHANA KUMARI",
    "KRISHNAMOHAN KAJI",
    "MD MAROOF",
    "AYODHYA DUBEY",
    "NEERAJ KUMAR",
    "INDAL KUMAR",
    "DINESH KUMAR",
    "PINTU KUMAR",
    "PRASHANT KU OJHA",
    "SNEHA SINGH",
    "SANDHYA KUMARI",
    "SARWAT SIDDIQUI",
    "VIPIN KUMAR RANJAN",
    "SADHNA KUMARI",
    "GARIMA",
    "DR MUKESH KU RAI",
]

master_schedule = {
    "CLASS 8TH": {
        1: "SANDHYA KUMARI",
        2: "SADHNA KUMARI",
        3: "SNEHA SINGH",
        4: "SARWAT SIDDIQUI",
        5: "PRASHANT KU OJHA",
        6: "NEERAJ KUMAR",
        7: "AYODHYA DUBEY",
        8: "PLAY ACTIVITY",
    },
    "MODEL CLASS IX": {
        1: "SAURABH KUMAR",
        2: "NEERAJ KUMAR",
        3: "KRISHNAMOHAN KAJI",
        4: "AYODHYA DUBEY",
        5: "VIPIN KUMAR RANJAN",
        6: "SNEHA SINGH",
        7: "GARIMA / SADHNA KUMARI",
    },
    "CLASS IX A": {
        1: "ARCHANA KUMARI",
        2: "DINESH KUMAR / INDAL KUMAR",
        3: "SANDHYA KUMARI",
        4: "SAURABH KUMAR",
        5: "AYODHYA DUBEY / MD MAROOF",
        6: "INDAL KUMAR",
        7: "SNEHA SINGH",
    },
    "CLASS IX B": {
        1: "KRISHNAMOHAN KAJI",
        2: "SNEHA SINGH",
        3: "NEERAJ KUMAR",
        4: "DINESH KUMAR / PRASHANT KU OJHA",
        5: "SADHNA KUMARI",
        6: "AYODHYA DUBEY / MD MAROOF",
        7: "SAURABH KUMAR",
    },
    "CLASS X A": {
        1: "AYODHYA DUBEY / MD MAROOF",
        2: "KRISHNAMOHAN KAJI",
        3: "SARWAT SIDDIQUI",
        4: "SNEHA SINGH",
        5: "DINESH KUMAR / SANDHYA KUMARI",
        6: "SANDHYA KUMARI",
        7: "ARCHANA KUMARI",
    },
    "CLASS X B": {
        1: "NEERAJ KUMAR",
        2: "SAURABH KUMAR",
        3: "AYODHYA DUBEY / MD MAROOF",
        4: "KRISHNAMOHAN KAJI",
        5: "SNEHA SINGH",
        6: "DINESH KUMAR / NEERAJ KUMAR",
        7: "SANDHYA KUMARI",
    },
    "CLASS XI ART'S": {
        1: "INDAL KUMAR",
        2: "PRASHANT KU OJHA / PINTU KUMAR",
        3: "VIPIN KUMAR RANJAN",
        4: "PINTU KUMAR",
        5: "GARIMA",
        6: "PINTU KUMAR",
        7: "DINESH KUMAR / MD MAROOF",
    },
    "CLASS XI SCIENCE": {
        1: "SADHNA KUMARI",
        2: "SARWAT SIDDIQUI",
        3: "DR MUKESH KU RAI / ARCHANA KUMARI",
        4: "VIPIN KUMAR RANJAN",
        5: "GARIMA",
        6: "KRISHNAMOHAN KAJI",
        7: "SADHNA KUMARI / GARIMA",
    },
    "CLASS XII ART'S": {
        1: "PRASHANT KU OJHA / VIPIN KUMAR RANJAN",
        2: "VIPIN KUMAR RANJAN / MD MAROOF",
        3: "PINTU KUMAR",
        4: "INDAL KUMAR",
        5: "NEERAJ KUMAR",
        6: "ARCHANA KUMARI",
        7: "INDAL KUMAR",
    },
    "CLASS XII SCIENCE": {
        1: "SARWAT SIDDIQUI",
        2: "DR MUKESH KU RAI / ARCHANA KUMARI",
        3: "SADHNA KUMARI",
        4: "GARIMA",
        5: "VIPIN KUMAR RANJAN",
        6: "ARCHANA KUMARI",
        7: "SARWAT SIDDIQUI",
    },
}

# DR MUKESH KU RAI removed from STRICT_FREE_MATRIX to prevent substitute assignment
STRICT_FREE_MATRIX = {
    1: ["DINESH KUMAR", "PINTU KUMAR", "GARIMA"],
    2: ["AYODHYA DUBEY", "DINESH KUMAR", "PINTU KUMAR", "GARIMA"],
    3: [
        "SAURABH KUMAR",
        "ARCHANA KUMARI",
        "INDAL KUMAR",
        "DINESH KUMAR",
        "GARIMA",
    ],
    4: ["ARCHANA KUMARI", "MD MAROOF", "SADHNA KUMARI"],
    5: [
        "SAURABH KUMAR",
        "ARCHANA KUMARI",
        "KRISHNAMOHAN KAJI",
        "INDAL KUMAR",
        "PINTU KUMAR",
    ],
    6: [
        "SAURABH KUMAR",
        "GARIMA",
        "SARWAT SIDDIQUI",
        "VIPIN KUMAR RANJAN",
    ],
    7: ["NEERAJ KUMAR", "PRASHANT KU OJHA", "VIPIN KUMAR RANJAN"],
    8: [],
}


def is_teacher_busy_in_schedule(teacher, period):
    for cls, periods in master_schedule.items():
        assigned = str(periods.get(period, "")).upper()
        teacher_list = [t.strip() for t in assigned.split("/")]
        if teacher in teacher_list:
            return True
    return False


def generate_adjustments(absent_teachers):
    absent_teachers = [a.strip().upper() for a in absent_teachers]
    adjustments = []
    today_counts = {t: 0 for t in all_teachers}

    for period in range(1, 8):
        assigned_today_in_period = set()

        for cls, periods in master_schedule.items():
            assigned_teacher_str = str(periods.get(period, "")).upper()

            if "PLAY ACTIVITY" in assigned_teacher_str:
                continue

            period_teachers = [
                t.strip() for t in assigned_teacher_str.split("/")
            ]
            absent_in_this_class = [
                t for t in period_teachers if t in absent_teachers
            ]

            if absent_in_this_class:
                partner_assigned = False
                present_partners = [
                    t for t in period_teachers if t not in absent_teachers
                ]

                # Prevent assigning DR MUKESH KU RAI even as co-teacher substitute
                for partner in present_partners:
                    if partner == "DR MUKESH KU RAI":
                        continue
                    if (
                        partner not in assigned_today_in_period
                        and today_counts.get(partner, 0) < 2
                    ):
                        adjustments.append(
                            {
                                "Period": f"Period {period}",
                                "Class": cls,
                                "Absent Teacher": ", ".join(
                                    absent_in_this_class
                                ),
                                "Substitute Assigned": f"{partner} (Co-Teacher Present)",
                            }
                        )
                        assigned_today_in_period.add(partner)
                        today_counts[partner] += 1
                        partner_assigned = True
                        break

                if not partner_assigned:
                    valid_candidates = []
                    for t in STRICT_FREE_MATRIX.get(period, []):
                        if (
                            t not in absent_teachers
                            and t not in assigned_today_in_period
                            and today_counts.get(t, 0) < 2
                            and not is_teacher_busy_in_schedule(t, period)
                        ):
                            valid_candidates.append(t)

                    if valid_candidates:
                        selected_teacher = min(
                            valid_candidates, key=lambda t: today_counts[t]
                        )
                        adjustments.append(
                            {
                                "Period": f"Period {period}",
                                "Class": cls,
                                "Absent Teacher": ", ".join(
                                    absent_in_this_class
                                ),
                                "Substitute Assigned": selected_teacher,
                            }
                        )
                        assigned_today_in_period.add(selected_teacher)
                        today_counts[selected_teacher] += 1
                    else:
                        adjustments.append(
                            {
                                "Period": f"Period {period}",
                                "Class": cls,
                                "Absent Teacher": ", ".join(
                                    absent_in_this_class
                                ),
                                "Substitute Assigned": "NO TEACHER FREE",
                            }
                        )

    return adjustments


def generate_pdf(adjustments, absent_list):
    current_date_str = datetime.now().strftime("%d-%m-%Y")
    pdf_path = f"Adjustment_Chart_{current_date_str}.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Heading1"], fontSize=16, alignment=1
    )
    subtitle_style = ParagraphStyle(
        "SubTitleStyle", parent=styles["Normal"], fontSize=10, alignment=1
    )

    elements.append(
        Paragraph(
            "<b>राजकीय उत्क्रमित उच्च माध्यमिक विद्यालय, भावल (रामनगर)</b>",
            title_style,
        )
    )
    elements.append(Spacer(1, 4))
    elements.append(
        Paragraph(
            f"<b>DAILY TEACHER ADJUSTMENT CHART</b><br/><b>Date:</b> {current_date_str} | <b>Absent Teachers:</b> {', '.join(absent_list)}",
            subtitle_style,
        )
    )
    elements.append(Spacer(1, 10))

    table_data = [
        [
            "S.No.",
            "Period",
            "Class / Section",
            "Absent Teacher",
            "Assigned Substitute Teacher",
        ]
    ]
    for idx, adj in enumerate(adjustments, 1):
        table_data.append(
            [
                str(idx),
                adj["Period"],
                adj["Class"],
                adj["Absent Teacher"],
                adj["Substitute Assigned"],
            ]
        )

    t = Table(table_data, colWidths=[40, 80, 130, 240, 240])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ]
        )
    )

    elements.append(t)
    doc.build(elements)
    return pdf_path


# ==================== STREAMLIT USER INTERFACE ====================
st.title("🏫 UHS Bhawal - Daily Adjustment")
st.write("Aaj jo teachers absent hain, unhe select karein:")

absent_today = st.multiselect("Select Absent Teachers", all_teachers)

if st.button("Generate Adjustment Chart", type="primary"):
    if not absent_today:
        st.warning("Kripya kam se kam ek absent teacher select karein.")
    else:
        results = generate_adjustments(absent_today)
        st.success("Adjustment Chart Tayar Ho Gaya Hai!")

        st.dataframe(results, use_container_width=True)

        pdf_file = generate_pdf(results, absent_today)
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="📥 Download Adjustment PDF",
                data=f,
                file_name=os.path.basename(pdf_file),
                mime="application/pdf",
            )
