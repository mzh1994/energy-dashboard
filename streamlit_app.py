
import streamlit as st
import pandas as pd
from datetime import datetime, date


# =========================================================
# PAGE
# =========================================================

st.set_page_config(page_title="Energy", layout="wide")


# =========================================================
# STYLE
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 3.0rem !important;
    padding-bottom: 1.5rem !important;
    max-width: 1550px;
}

.section-title {
    font-size: 16px;
    font-weight: 700;
    margin-top: 18px;
    margin-bottom: 10px;
    line-height: 1.2;
}

.energy-card {
    border: 1px solid rgba(128,128,128,0.30);
    border-radius: 8px;
    padding: 11px 14px;
    min-height: 108px;
    box-sizing: border-box;
}

.ground-card {
    min-height: 142px;
}

.compare-card {
    min-height: 142px;
}

.card-title {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 2px;
    line-height: 1.2;
}

.card-subtitle {
    font-size: 13px;
    opacity: 0.55;
    margin-bottom: 10px;
}

.card-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.card-label {
    font-size: 14px;
    line-height: 1.15;
    opacity: 0.80;
    margin-bottom: 4px;
}

.card-value {
    font-size: 18px;
    font-weight: 700;
    line-height: 1.15;
}

.card-small-value {
    font-size: 16px;
    font-weight: 700;
    line-height: 1.15;
}

.card-rate {
    font-size: 13px;
    opacity: 0.55;
    margin-top: 5px;
}

.card-divider {
    border-top: 1px solid rgba(128,128,128,0.30);
    margin: 10px 0;
}

div[data-testid="stHorizontalBlock"] {
    gap: 10px !important;
}

div[data-testid="stVerticalBlock"] {
    gap: 0.25rem !important;
}

.table-title {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 1px;
}

.table-subtitle {
    font-size: 13px;
    opacity: 0.55;
    margin-bottom: 7px;
}

div[data-testid="stDataFrame"] {
    font-size: 14px !important;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LATEST KNOWN KE TARIFF / BILLING COMPONENTS
# Calibrated from October 2026 actual KE bills
# =========================================================

PHL_RATE = 3.23
UQA_RATE = 0.5194
FCA_RATE = 1.1086

ELECTRICITY_DUTY_RATE = 0.015
SALES_TAX_RATE = 0.18

GROUND_OFF_RATE = 34.53
GROUND_PEAK_RATE = 46.85

GROUND_FIXED_BILLING_KW = 2.5
GROUND_FIXED_RATE = 675


# =========================================================
# SINGLE PHASE TARIFF
# =========================================================

def single_phase_tariff(units):
    if units <= 100:
        return 22.44, 275, 0
    elif units <= 200:
        return 28.91, 300, 20
    elif units <= 300:
        return 33.10, 350, 40
    elif units <= 400:
        return 36.46, 400, 100
    elif units <= 500:
        return 38.95, 500, 125
    elif units <= 600:
        return 40.22, 675, 150
    elif units <= 700:
        return 41.85, 675, 175
    else:
        return 47.20, 675, 300


# =========================================================
# CORRECTED BILL FUNCTIONS
#
# KE October bills reconcile when:
# Electricity Charges =
#   Fixed + Variable + UQA + FCA + PHL
#
# Electricity Duty =
#   1.5% of (Variable + UQA + FCA + PHL)
#   i.e. fixed charges excluded from duty base
#
# Sales Tax =
#   18% of (Electricity Charges + Electricity Duty)
# =========================================================

def single_phase_bill(units, load_kw, fca_units=0, fca_rate=FCA_RATE):
    rate, fixed_rate, muct = single_phase_tariff(units)

    variable = units * rate
    fixed = load_kw * fixed_rate
    uqa = units * UQA_RATE
    fca = fca_units * fca_rate
    phl = units * PHL_RATE

    duty_base = variable + uqa + fca + phl
    electricity_charges = fixed + duty_base

    duty = duty_base * ELECTRICITY_DUTY_RATE
    sales_tax = (electricity_charges + duty) * SALES_TAX_RATE

    total = electricity_charges + duty + sales_tax + muct

    return {
        "total": total,
        "rate": rate,
        "fixed": fixed,
        "variable": variable,
        "uqa": uqa,
        "fca": fca,
        "phl": phl,
        "duty": duty,
        "sales_tax": sales_tax,
        "muct": muct,
    }


def ground_bill(off_units, peak_units, fca_units=0, fca_rate=FCA_RATE):
    total_units = off_units + peak_units

    variable = (
        off_units * GROUND_OFF_RATE
        + peak_units * GROUND_PEAK_RATE
    )

    fixed = GROUND_FIXED_BILLING_KW * GROUND_FIXED_RATE
    uqa = total_units * UQA_RATE
    fca = fca_units * fca_rate
    phl = total_units * PHL_RATE

    duty_base = variable + uqa + fca + phl
    electricity_charges = fixed + duty_base

    duty = duty_base * ELECTRICITY_DUTY_RATE
    sales_tax = (electricity_charges + duty) * SALES_TAX_RATE

    total = electricity_charges + duty + sales_tax

    return {
        "total": total,
        "variable": variable,
        "fixed": fixed,
        "uqa": uqa,
        "fca": fca,
        "phl": phl,
        "duty": duty,
        "sales_tax": sales_tax,
    }


# =========================================================
# SEPTEMBER 2026 ACTUAL KE BILLS
# =========================================================

SEP_GROUND_UNITS = 37
SEP_GROUND_BILL = 3790.27

SEP_FIRST_UNITS = 262
SEP_FIRST_BILL = 14482.29

SEP_SECOND_UNITS = 110
SEP_SECOND_BILL = 5708.64


# =========================================================
# OCTOBER 2026 - HISTORICAL ESTIMATE SNAPSHOT
# This preserves what the dashboard estimated BEFORE
# the October actual KE bills arrived.
# It is intentionally NOT recalculated with the new formula.
# =========================================================

OCT_EST_GROUND_UNITS = 38
OCT_EST_GROUND_BILL = 3914.57

OCT_EST_FIRST_UNITS = 364
OCT_EST_FIRST_BILL = 19777.95

OCT_EST_SECOND_UNITS = 67
OCT_EST_SECOND_BILL = 3044.18


# =========================================================
# OCTOBER 2026 ACTUAL KE BILLS
# Official KE reading date: 05-Oct-2026
# =========================================================

# Ground Floor · TP66310
OCT_ACT_GROUND_OFF_PREV = 5281
OCT_ACT_GROUND_OFF_CURR = 5308
OCT_ACT_GROUND_PEAK_PREV = 723
OCT_ACT_GROUND_PEAK_CURR = 735

OCT_ACT_GROUND_OFF_UNITS = (
    OCT_ACT_GROUND_OFF_CURR - OCT_ACT_GROUND_OFF_PREV
)
OCT_ACT_GROUND_PEAK_UNITS = (
    OCT_ACT_GROUND_PEAK_CURR - OCT_ACT_GROUND_PEAK_PREV
)
OCT_ACT_GROUND_UNITS = (
    OCT_ACT_GROUND_OFF_UNITS + OCT_ACT_GROUND_PEAK_UNITS
)
OCT_ACT_GROUND_BILL = 3998.84


# First Floor · SFS23934
OCT_ACT_FIRST_PREV = 4757
OCT_ACT_FIRST_CURR = 5130
OCT_ACT_FIRST_UNITS = OCT_ACT_FIRST_CURR - OCT_ACT_FIRST_PREV
OCT_ACT_FIRST_BILL = 20885.30


# Second Floor · SFS82166
OCT_ACT_SECOND_PREV = 2111
OCT_ACT_SECOND_CURR = 2178
OCT_ACT_SECOND_UNITS = OCT_ACT_SECOND_CURR - OCT_ACT_SECOND_PREV
OCT_ACT_SECOND_BILL = 3331.35


# October FCA units printed on actual KE bills
OCT_FCA_GROUND_UNITS = 32
OCT_FCA_FIRST_UNITS = 348
OCT_FCA_SECOND_UNITS = 193


# =========================================================
# OPTIONAL INTERNAL CHECK
# These should reproduce the October bills almost exactly.
# =========================================================

OCT_CHECK_GROUND = ground_bill(
    OCT_ACT_GROUND_OFF_UNITS,
    OCT_ACT_GROUND_PEAK_UNITS,
    OCT_FCA_GROUND_UNITS,
)["total"]

OCT_CHECK_FIRST = single_phase_bill(
    OCT_ACT_FIRST_UNITS,
    5,
    OCT_FCA_FIRST_UNITS,
)["total"]

OCT_CHECK_SECOND = single_phase_bill(
    OCT_ACT_SECOND_UNITS,
    3,
    OCT_FCA_SECOND_UNITS,
)["total"]


# =========================================================
# CURRENT BILLING CYCLE
#
# October KE reading was 05-Oct-2026,
# therefore current cycle starts 06-Oct-2026.
# =========================================================

CURRENT_START = date(2026, 10, 6)
CURRENT_END = date(2026, 11, 5)
CURRENT_LABEL = "06 Oct – 05 Nov 2026"

CURRENT_DAYS = (CURRENT_END - CURRENT_START).days + 1


# Official October bill closing readings become
# current-cycle opening readings.
CURRENT_GROUND_OFF_START = 5308
CURRENT_GROUND_PEAK_START = 735

CURRENT_FIRST_START = 5130
CURRENT_SECOND_START = 2178


# =========================================================
# FCA PROXY FOR CURRENT ESTIMATE
#
# FCA is lagged and the next FCA is not yet known.
# For a practical estimate, use latest FCA rate with the
# previous actual month's billed units as proxy FCA units.
# =========================================================

CURRENT_FCA_GROUND_UNITS = SEP_GROUND_UNITS
CURRENT_FCA_FIRST_UNITS = SEP_FIRST_UNITS
CURRENT_FCA_SECOND_UNITS = SEP_SECOND_UNITS


# =========================================================
# ALL PHOTO READINGS
#
# IMPORTANT:
# These remain untouched.
# They are the user's actual photo-to-photo observations.
# They are NOT forced to match KE's official reading timestamp.
# =========================================================

READINGS = [
    {
        "datetime": datetime(2026, 9, 28, 9, 0),
        "first": 5046,
        "second": 2118,
        "ground_off": 5303,
        "ground_peak": 732,
    },
    {
        "datetime": datetime(2026, 9, 29, 8, 15),
        "first": 5062,
        "second": 2118,
        "ground_off": 5303,
        "ground_peak": 733,
    },
    {
        "datetime": datetime(2026, 9, 30, 8, 7),
        "first": 5078,
        "second": 2118,
        "ground_off": 5304,
        "ground_peak": 733,
    },
    {
        "datetime": datetime(2026, 10, 2, 8, 18),
        "first": 5100,
        "second": 2178,
        "ground_off": 5305,
        "ground_peak": 734,
    },
    {
        "datetime": datetime(2026, 10, 3, 10, 33),
        "first": 5110,
        "second": 2178,
        "ground_off": 5306,
        "ground_peak": 734,
    },
    {
        "datetime": datetime(2026, 10, 4, 15, 18),
        "first": 5121,
        "second": 2178,
        "ground_off": 5307,
        "ground_peak": 735,
    },
    {
        "datetime": datetime(2026, 10, 5, 8, 4),
        "first": 5129,
        "second": 2178,
        "ground_off": 5308,
        "ground_peak": 735,
    },
    {
        "datetime": datetime(2026, 10, 6, 8, 23),
        "first": 5140,
        "second": 2178,
        "ground_off": 5309,
        "ground_peak": 736,
    },
    {
        "datetime": datetime(2026, 10, 7, 8, 24),
        "first": 5154,
        "second": 2178,
        "ground_off": 5310,
        "ground_peak": 736,
    },
    {
        "datetime": datetime(2026, 10, 8, 8, 24),
        "first": 5164,
        "second": 2178,
        "ground_off": 5311,
        "ground_peak": 737,
    },
    {
        "datetime": datetime(2026, 10, 9, 8, 24),
        "first": 5179,
        "second": 2178,
        "ground_off": 5312,
        "ground_peak": 737,
    },
    {
        "datetime": datetime(2026, 10, 10, 13, 50),
        "first": 5191,
        "second": 2178,
        "ground_off": 5313,
        "ground_peak": 738,
    },
    {
        "datetime": datetime(2026, 10, 11, 13, 50),
        "first": 5200,
        "second": 2182,
        "ground_off": 5315,
        "ground_peak": 739,
    },
    {
        "datetime": datetime(2026, 10, 12, 9, 8),
        "first": 5204,
        "second": 2187,
        "ground_off": 5316,
        "ground_peak": 739,
    },
    {
        "datetime": datetime(2026, 10, 13, 9, 8),
        "first": 5214,
        "second": 2195,
        "ground_off": 5317,
        "ground_peak": 740,
    },
    {
        "datetime": datetime(2026, 10, 15, 8, 0),
        "first": 5237,
        "second": 2205,
        "ground_off": 5319,
        "ground_peak": 741,
    },
    {
        "datetime": datetime(2026, 10, 16, 9, 0),
        "first": 5249,
        "second": 2212,
        "ground_off": 5321,
        "ground_peak": 742,
    },
    {
        "datetime": datetime(2026, 10, 17, 13, 0),
        "first": 5263,
        "second": 2213,
        "ground_off": 5322,
        "ground_peak": 742,
    },
    {
        "datetime": datetime(2026, 10, 18, 11, 0),
        "first": 5276,
        "second": 2216,
        "ground_off": 5324,
        "ground_peak": 743,
    },
{
        "datetime": datetime(2026, 10, 23, 7, 0),
        "first": 5337,
        "second": 2233,
        "ground_off": 5329,
        "ground_peak": 744,
    },
{
        "datetime": datetime(2026, 10, 27, 8, 30),
        "first": 5374,
        "second": 2251,
        "ground_off": 5335,
        "ground_peak": 746,
    },

]


# =========================================================
# CURRENT VALUES
# =========================================================

latest = READINGS[-1]
latest_date = latest["datetime"].date()

days_passed = (latest_date - CURRENT_START).days + 1
days_passed = max(1, min(days_passed, CURRENT_DAYS))


current_ground_off_units = max(
    0,
    latest["ground_off"] - CURRENT_GROUND_OFF_START,
)

current_ground_peak_units = max(
    0,
    latest["ground_peak"] - CURRENT_GROUND_PEAK_START,
)

current_ground_units = (
    current_ground_off_units + current_ground_peak_units
)

current_first_units = max(
    0,
    latest["first"] - CURRENT_FIRST_START,
)

current_second_units = max(
    0,
    latest["second"] - CURRENT_SECOND_START,
)


current_ground_bill_data = ground_bill(
    current_ground_off_units,
    current_ground_peak_units,
    CURRENT_FCA_GROUND_UNITS,
)

current_first_bill_data = single_phase_bill(
    current_first_units,
    5,
    CURRENT_FCA_FIRST_UNITS,
)

current_second_bill_data = single_phase_bill(
    current_second_units,
    3,
    CURRENT_FCA_SECOND_UNITS,
)


current_ground_bill = current_ground_bill_data["total"]
current_first_bill = current_first_bill_data["total"]
current_second_bill = current_second_bill_data["total"]


# =========================================================
# TOTALS
# =========================================================

sep_total_units = (
    SEP_GROUND_UNITS
    + SEP_FIRST_UNITS
    + SEP_SECOND_UNITS
)

sep_total_bill = (
    SEP_GROUND_BILL
    + SEP_FIRST_BILL
    + SEP_SECOND_BILL
)


oct_est_total_units = (
    OCT_EST_GROUND_UNITS
    + OCT_EST_FIRST_UNITS
    + OCT_EST_SECOND_UNITS
)

oct_est_total_bill = (
    OCT_EST_GROUND_BILL
    + OCT_EST_FIRST_BILL
    + OCT_EST_SECOND_BILL
)


oct_act_total_units = (
    OCT_ACT_GROUND_UNITS
    + OCT_ACT_FIRST_UNITS
    + OCT_ACT_SECOND_UNITS
)

oct_act_total_bill = (
    OCT_ACT_GROUND_BILL
    + OCT_ACT_FIRST_BILL
    + OCT_ACT_SECOND_BILL
)


current_total_units = (
    current_ground_units
    + current_first_units
    + current_second_units
)

current_total_bill = (
    current_ground_bill
    + current_first_bill
    + current_second_bill
)


# =========================================================
# CARD HELPERS
# =========================================================

def simple_card(title, subtitle, units, bill):
    return f"""
<div class="energy-card">
    <div class="card-title">{title}</div>
    <div class="card-subtitle">{subtitle}</div>

    <div class="card-grid">
        <div>
            <div class="card-label">Units</div>
            <div class="card-value">{units:,} kWh</div>
        </div>

        <div>
            <div class="card-label">Bill</div>
            <div class="card-value">Rs {bill:,.0f}</div>
        </div>
    </div>
</div>
"""


def compare_card(
    title,
    subtitle,
    est_units,
    act_units,
    est_bill,
    act_bill,
):
    return f"""
<div class="energy-card compare-card">
    <div class="card-title">{title}</div>
    <div class="card-subtitle">{subtitle}</div>

    <div class="card-grid">
        <div>
            <div class="card-label">Estimated Units</div>
            <div class="card-small-value">{est_units:,} kWh</div>
        </div>

        <div>
            <div class="card-label">Actual Units</div>
            <div class="card-small-value">{act_units:,} kWh</div>
        </div>
    </div>

    <div class="card-divider"></div>

    <div class="card-grid">
        <div>
            <div class="card-label">Estimated Bill</div>
            <div class="card-small-value">Rs {est_bill:,.0f}</div>
        </div>

        <div>
            <div class="card-label">Actual Bill</div>
            <div class="card-small-value">Rs {act_bill:,.0f}</div>
        </div>
    </div>
</div>
"""


# =========================================================
# SEPTEMBER ACTUAL SUMMARY
# =========================================================

st.html('<div class="section-title">September 2026 Actual</div>')

c1, c2, c3, c4 = st.columns(4, gap="small")

with c1:
    st.html(simple_card(
        "Ground Floor · TP66310",
        "3 Phase TOU",
        SEP_GROUND_UNITS,
        SEP_GROUND_BILL,
    ))

with c2:
    st.html(simple_card(
        "First Floor · SFS23934",
        "Single Phase",
        SEP_FIRST_UNITS,
        SEP_FIRST_BILL,
    ))

with c3:
    st.html(simple_card(
        "Second Floor · SFS82166",
        "Single Phase",
        SEP_SECOND_UNITS,
        SEP_SECOND_BILL,
    ))

with c4:
    st.html(simple_card(
        "TOTAL · All Floors",
        "Actual",
        sep_total_units,
        sep_total_bill,
    ))


# =========================================================
# OCTOBER ESTIMATED VS ACTUAL
# =========================================================

st.html(
    '<div class="section-title">'
    'October 2026 · Estimated vs Actual'
    '</div>'
)

c1, c2, c3, c4 = st.columns(4, gap="small")

with c1:
    st.html(compare_card(
        "Ground Floor · TP66310",
        "KE reading 05 Oct",
        OCT_EST_GROUND_UNITS,
        OCT_ACT_GROUND_UNITS,
        OCT_EST_GROUND_BILL,
        OCT_ACT_GROUND_BILL,
    ))

with c2:
    st.html(compare_card(
        "First Floor · SFS23934",
        "KE reading 05 Oct",
        OCT_EST_FIRST_UNITS,
        OCT_ACT_FIRST_UNITS,
        OCT_EST_FIRST_BILL,
        OCT_ACT_FIRST_BILL,
    ))

with c3:
    st.html(compare_card(
        "Second Floor · SFS82166",
        "KE reading 05 Oct",
        OCT_EST_SECOND_UNITS,
        OCT_ACT_SECOND_UNITS,
        OCT_EST_SECOND_BILL,
        OCT_ACT_SECOND_BILL,
    ))

with c4:
    st.html(compare_card(
        "TOTAL · All Floors",
        "October 2026",
        oct_est_total_units,
        oct_act_total_units,
        oct_est_total_bill,
        oct_act_total_bill,
    ))


# =========================================================
# CURRENT CYCLE
# =========================================================

st.html(
    f"""
<div class="section-title">
    {CURRENT_LABEL} · Day {days_passed} of {CURRENT_DAYS}
</div>
"""
)

c1, c2, c3, c4 = st.columns(4, gap="small")


with c1:
    st.html(f"""
<div class="energy-card ground-card">

    <div class="card-title">
        Ground Floor · TP66310
    </div>

    <div class="card-subtitle">
        3 Phase TOU
    </div>

    <div class="card-grid">
        <div>
            <div class="card-label">Off-Peak</div>
            <div class="card-value">
                {current_ground_off_units} kWh
            </div>
            <div class="card-rate">
                Rs {GROUND_OFF_RATE:.2f}/unit
            </div>
        </div>

        <div>
            <div class="card-label">Peak</div>
            <div class="card-value">
                {current_ground_peak_units} kWh
            </div>
            <div class="card-rate">
                Rs {GROUND_PEAK_RATE:.2f}/unit
            </div>
        </div>
    </div>

    <div class="card-divider"></div>

    <div class="card-grid">
        <div>
            <div class="card-label">Total</div>
            <div class="card-value">
                {current_ground_units} kWh
            </div>
        </div>

        <div>
            <div class="card-label">Est. Bill</div>
            <div class="card-value">
                Rs {current_ground_bill:,.0f}
            </div>
        </div>
    </div>

</div>
""")


with c2:
    st.html(f"""
<div class="energy-card">

    <div class="card-title">
        First Floor · SFS23934
    </div>

    <div class="card-subtitle">
        Single Phase
    </div>

    <div class="card-grid">
        <div>
            <div class="card-label">Units</div>
            <div class="card-value">
                {current_first_units} kWh
            </div>
            <div class="card-rate">
                Rs {current_first_bill_data["rate"]:.2f}/unit
            </div>
        </div>

        <div>
            <div class="card-label">Est. Bill</div>
            <div class="card-value">
                Rs {current_first_bill:,.0f}
            </div>
        </div>
    </div>

</div>
""")


with c3:
    st.html(f"""
<div class="energy-card">

    <div class="card-title">
        Second Floor · SFS82166
    </div>

    <div class="card-subtitle">
        Single Phase
    </div>

    <div class="card-grid">
        <div>
            <div class="card-label">Units</div>
            <div class="card-value">
                {current_second_units} kWh
            </div>
            <div class="card-rate">
                Rs {current_second_bill_data["rate"]:.2f}/unit
            </div>
        </div>

        <div>
            <div class="card-label">Est. Bill</div>
            <div class="card-value">
                Rs {current_second_bill:,.0f}
            </div>
        </div>
    </div>

</div>
""")


with c4:
    st.html(simple_card(
        "TOTAL · All Floors",
        "Current Cycle",
        current_total_units,
        current_total_bill,
    ))


# =========================================================
# DAILY CONSUMPTION TABLES
#
# These tables use ONLY consecutive user photo readings.
# No KE actual bill reading is inserted into this history.
# Therefore historical daily data remains unchanged.
# =========================================================

st.html('<div class="section-title">Daily Consumption</div>')

ground_rows = []
first_rows = []
second_rows = []

ground_logged_units = 0
ground_logged_cost = 0

first_logged_units = 0
first_logged_cost = 0

second_logged_units = 0
second_logged_cost = 0


def photo_cycle_baseline(reading_date):
    # 05-Oct photo was taken before the official KE close reading,
    # so current official cycle baseline is used from 06-Oct onward.
    if reading_date >= CURRENT_START:
        return {
            "first": CURRENT_FIRST_START,
            "second": CURRENT_SECOND_START,
        }

    return {
        "first": OCT_ACT_FIRST_PREV,
        "second": OCT_ACT_SECOND_PREV,
    }


for i in range(len(READINGS) - 1, -1, -1):
    reading = READINGS[i]

    date_text = (
        reading["datetime"]
        .strftime("%d-%b %I:%M %p")
    )

    if i == 0:
        ground_rows.append({
            "Date": date_text,
            "Daily kWh": "—",
            "Est. Cost": "—",
        })

        first_rows.append({
            "Date": date_text,
            "Daily kWh": "—",
            "Est. Cost": "—",
        })

        second_rows.append({
            "Date": date_text,
            "Daily kWh": "—",
            "Est. Cost": "—",
        })

        continue

    previous = READINGS[i - 1]


    # -------------------------
    # Ground Floor
    # -------------------------

    off_delta = (
        reading["ground_off"]
        - previous["ground_off"]
    )

    peak_delta = (
        reading["ground_peak"]
        - previous["ground_peak"]
    )

    ground_delta = off_delta + peak_delta

    ground_daily_cost = (
        off_delta * GROUND_OFF_RATE
        + peak_delta * GROUND_PEAK_RATE
    )

    ground_logged_units += ground_delta
    ground_logged_cost += ground_daily_cost

    ground_rows.append({
        "Date": date_text,
        "Daily kWh": f"{ground_delta} kWh",
        "Est. Cost": f"Rs {ground_daily_cost:,.0f}",
    })


    # -------------------------
    # First Floor
    # -------------------------

    first_delta = (
        reading["first"]
        - previous["first"]
    )

    baselines = photo_cycle_baseline(
        reading["datetime"].date()
    )

    first_cycle_units = max(
        0,
        reading["first"] - baselines["first"],
    )

    first_daily_rate, _, _ = single_phase_tariff(
        first_cycle_units
    )

    first_daily_cost = (
        first_delta * first_daily_rate
    )

    first_logged_units += first_delta
    first_logged_cost += first_daily_cost

    first_rows.append({
        "Date": date_text,
        "Daily kWh": f"{first_delta} kWh",
        "Est. Cost": f"Rs {first_daily_cost:,.0f}",
    })


    # -------------------------
    # Second Floor
    # -------------------------

    second_delta = (
        reading["second"]
        - previous["second"]
    )

    second_cycle_units = max(
        0,
        reading["second"] - baselines["second"],
    )

    second_daily_rate, _, _ = single_phase_tariff(
        second_cycle_units
    )

    second_daily_cost = (
        second_delta * second_daily_rate
    )

    second_logged_units += second_delta
    second_logged_cost += second_daily_cost

    second_rows.append({
        "Date": date_text,
        "Daily kWh": f"{second_delta} kWh",
        "Est. Cost": f"Rs {second_daily_cost:,.0f}",
    })


# =========================================================
# TABLE TOTALS
# =========================================================

ground_rows.append({
    "Date": "LOGGED TOTAL",
    "Daily kWh": f"{ground_logged_units} kWh",
    "Est. Cost": f"Rs {ground_logged_cost:,.0f}",
})

first_rows.append({
    "Date": "LOGGED TOTAL",
    "Daily kWh": f"{first_logged_units} kWh",
    "Est. Cost": f"Rs {first_logged_cost:,.0f}",
})

second_rows.append({
    "Date": "LOGGED TOTAL",
    "Daily kWh": f"{second_logged_units} kWh",
    "Est. Cost": f"Rs {second_logged_cost:,.0f}",
})


# =========================================================
# DISPLAY TABLES
# =========================================================

t1, t2, t3 = st.columns(3, gap="small")


with t1:
    st.html("""
<div class="table-title">
    Ground Floor · TP66310
</div>
<div class="table-subtitle">
    3 Phase TOU
</div>
""")

    st.dataframe(
        pd.DataFrame(ground_rows),
        use_container_width=True,
        hide_index=True,
        height=350,
    )


with t2:
    st.html("""
<div class="table-title">
    First Floor · SFS23934
</div>
<div class="table-subtitle">
    Single Phase
</div>
""")

    st.dataframe(
        pd.DataFrame(first_rows),
        use_container_width=True,
        hide_index=True,
        height=350,
    )


with t3:
    st.html("""
<div class="table-title">
    Second Floor · SFS82166
</div>
<div class="table-subtitle">
    Single Phase
</div>
""")

    st.dataframe(
        pd.DataFrame(second_rows),
        use_container_width=True,
        hide_index=True,
        height=350,
    )
