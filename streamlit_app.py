import streamlit as st
import pandas as pd
from datetime import datetime, date


# =========================================================
# PAGE
# =========================================================

st.set_page_config(
    page_title="Energy",
    layout="wide"
)


# =========================================================
# STYLE
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 1.5rem !important;
    max-width: 1500px;
}

/* Section heading */
.section-title {
    font-size: 16px;
    font-weight: 700;
    margin-top: 18px;
    margin-bottom: 12px;
    line-height: 1.2;
}

/* Card */
.energy-card {
    border: 1px solid #d9d9d9;
    border-radius: 9px;
    padding: 12px 16px;
    background: transparent;
    min-height: 92px;
    box-sizing: border-box;
}

/* Current cards slightly taller */
.current-card {
    min-height: 122px;
}

/* Card heading */
.card-title {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 2px;
    line-height: 1.2;
}

/* Meter type */
.card-subtitle {
    font-size: 13px;
    opacity: 0.60;
    margin-bottom: 12px;
}

/* Two-column information */
.card-grid {
    display: grid;
    grid-template-columns: auto auto;
    justify-content: space-between;
    align-items: start;
    column-gap: 20px;
}

/* Normal label */
.card-label {
    font-size: 14px;
    margin-bottom: 3px;
    opacity: 0.82;
}

/* Main value */
.card-value {
    font-size: 18px;
    font-weight: 700;
    line-height: 1.15;
}

/* Small rate */
.card-rate {
    font-size: 13px;
    opacity: 0.58;
    margin-top: 5px;
}

/* Thin divider */
.card-divider {
    border-top: 1px solid #dddddd;
    margin: 10px 0 8px 0;
}

/* Streamlit column spacing */
div[data-testid="stHorizontalBlock"] {
    gap: 10px !important;
}

/* Reduce general Streamlit vertical spacing */
div[data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
}

/* Table headings above dataframes */
.table-title {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 1px;
}

.table-subtitle {
    font-size: 13px;
    opacity: 0.60;
    margin-bottom: 8px;
}

/* Table font */
div[data-testid="stDataFrame"] {
    font-size: 14px !important;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# BILLING CYCLE
# =========================================================

CYCLE_START = date(2026, 9, 5)
CYCLE_END = date(2026, 10, 4)

CYCLE_LABEL = "05 Sep – 04 Oct 2026"

CYCLE_DAYS = (
    CYCLE_END - CYCLE_START
).days + 1


# =========================================================
# PREVIOUS KE BILL BASELINES
# Reading Date: 04-Sep-2026
# =========================================================

# Ground Floor - 3 Phase TOU
GROUND_OFF_START = 5281
GROUND_PEAK_START = 723

GROUND_LAST_UNITS = 37
GROUND_LAST_BILL = 3790.27


# First Floor - Single Phase
FIRST_START = 4757

FIRST_LAST_UNITS = 262
FIRST_LAST_BILL = 14482.29


# Second Floor - Single Phase
SECOND_START = 2111

SECOND_LAST_UNITS = 110
SECOND_LAST_BILL = 5708.64


# =========================================================
# READINGS
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

]


# =========================================================
# TARIFFS
# =========================================================

PHL_RATE = 3.23

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
# SINGLE PHASE BILL
# =========================================================

def single_phase_bill(units, load_kw):

    rate, fixed_rate, muct = single_phase_tariff(units)

    energy = units * rate
    fixed = load_kw * fixed_rate
    phl = units * PHL_RATE

    electricity_duty = (
        energy + fixed
    ) * ELECTRICITY_DUTY_RATE

    sales_tax = (
        energy
        + fixed
        + phl
        + electricity_duty
    ) * SALES_TAX_RATE

    total = (
        energy
        + fixed
        + phl
        + electricity_duty
        + sales_tax
        + muct
    )

    return {
        "total": total,
        "rate": rate
    }


# =========================================================
# GROUND FLOOR BILL
# =========================================================

def ground_bill(off_units, peak_units):

    off_energy = (
        off_units * GROUND_OFF_RATE
    )

    peak_energy = (
        peak_units * GROUND_PEAK_RATE
    )

    energy = (
        off_energy + peak_energy
    )

    total_units = (
        off_units + peak_units
    )

    fixed = (
        GROUND_FIXED_BILLING_KW
        * GROUND_FIXED_RATE
    )

    phl = (
        total_units * PHL_RATE
    )

    electricity_duty = (
        energy + fixed
    ) * ELECTRICITY_DUTY_RATE

    sales_tax = (
        energy
        + fixed
        + phl
        + electricity_duty
    ) * SALES_TAX_RATE

    total = (
        energy
        + fixed
        + phl
        + electricity_duty
        + sales_tax
    )

    return total


# =========================================================
# CURRENT VALUES
# =========================================================

latest = READINGS[-1]

latest_date = latest["datetime"].date()

days_passed = (
    latest_date - CYCLE_START
).days + 1

days_passed = max(
    1,
    min(days_passed, CYCLE_DAYS)
)


first_units = (
    latest["first"]
    - FIRST_START
)

second_units = (
    latest["second"]
    - SECOND_START
)

ground_off_units = (
    latest["ground_off"]
    - GROUND_OFF_START
)

ground_peak_units = (
    latest["ground_peak"]
    - GROUND_PEAK_START
)

ground_total_units = (
    ground_off_units
    + ground_peak_units
)


# =========================================================
# BILLS
# =========================================================

first_bill = single_phase_bill(
    first_units,
    5
)

second_bill = single_phase_bill(
    second_units,
    3
)

ground_estimated_bill = ground_bill(
    ground_off_units,
    ground_peak_units
)


# =========================================================
# TOTALS
# =========================================================

previous_total_units = (
    GROUND_LAST_UNITS
    + FIRST_LAST_UNITS
    + SECOND_LAST_UNITS
)

previous_total_bill = (
    GROUND_LAST_BILL
    + FIRST_LAST_BILL
    + SECOND_LAST_BILL
)

current_total_units = (
    ground_total_units
    + first_units
    + second_units
)

current_total_bill = (
    ground_estimated_bill
    + first_bill["total"]
    + second_bill["total"]
)


# =========================================================
# PREVIOUS MONTH
# =========================================================

st.html(
    '<div class="section-title">September 2026 Actual</div>'
)

c1, c2, c3, c4 = st.columns(
    4,
    gap="small"
)


with c1:

    st.html(f"""
<div class="energy-card">
    <div class="card-title">Ground Floor · TP66310</div>
    <div class="card-subtitle">3 Phase TOU</div>

    <div class="card-grid">
        <div>
            <div class="card-label">Units</div>
            <div class="card-value">{GROUND_LAST_UNITS} kWh</div>
        </div>

        <div>
            <div class="card-label">Bill</div>
            <div class="card-value">Rs {GROUND_LAST_BILL:,.0f}</div>
        </div>
    </div>
</div>
""")


with c2:

    st.html(f"""
<div class="energy-card">
    <div class="card-title">First Floor · SFS23934</div>
    <div class="card-subtitle">Single Phase</div>

    <div class="card-grid">
        <div>
            <div class="card-label">Units</div>
            <div class="card-value">{FIRST_LAST_UNITS} kWh</div>
        </div>

        <div>
            <div class="card-label">Bill</div>
            <div class="card-value">Rs {FIRST_LAST_BILL:,.0f}</div>
        </div>
    </div>
</div>
""")


with c3:

    st.html(f"""
<div class="energy-card">
    <div class="card-title">Second Floor · SFS82166</div>
    <div class="card-subtitle">Single Phase</div>

    <div class="card-grid">
        <div>
            <div class="card-label">Units</div>
            <div class="card-value">{SECOND_LAST_UNITS} kWh</div>
        </div>

        <div>
            <div class="card-label">Bill</div>
            <div class="card-value">Rs {SECOND_LAST_BILL:,.0f}</div>
        </div>
    </div>
</div>
""")


with c4:

    st.html(f"""
<div class="energy-card">
    <div class="card-title">TOTAL · All Floors</div>
    <div class="card-subtitle">Actual</div>

    <div class="card-grid">
        <div>
            <div class="card-label">Units</div>
            <div class="card-value">{previous_total_units} kWh</div>
        </div>

        <div>
            <div class="card-label">Bill</div>
            <div class="card-value">Rs {previous_total_bill:,.0f}</div>
        </div>
    </div>
</div>
""")


# =========================================================
# CURRENT CYCLE
# =========================================================

st.html(
    f'''
<div class="section-title">
    {CYCLE_LABEL} (Day {days_passed} of {CYCLE_DAYS})
</div>
'''
)

c1, c2, c3, c4 = st.columns(
    4,
    gap="small"
)


# Ground Floor

with c1:

    st.html(f"""
<div class="energy-card current-card">

    <div class="card-title">
        Ground Floor · TP66310
    </div>

    <div class="card-subtitle">
        3 Phase TOU
    </div>

    <div class="card-grid">

        <div>
            <div class="card-label">
                Off-Peak
            </div>

            <div class="card-value">
                {ground_off_units} kWh
            </div>

            <div class="card-rate">
                Rs {GROUND_OFF_RATE:.2f}/unit
            </div>
        </div>

        <div>
            <div class="card-label">
                Peak
            </div>

            <div class="card-value">
                {ground_peak_units} kWh
            </div>

            <div class="card-rate">
                Rs {GROUND_PEAK_RATE:.2f}/unit
            </div>
        </div>

    </div>

    <div class="card-divider"></div>

    <div class="card-grid">

        <div>
            <div class="card-label">
                Total
            </div>

            <div class="card-value">
                {ground_total_units} kWh
            </div>
        </div>

        <div>
            <div class="card-label">
                Est. Bill
            </div>

            <div class="card-value">
                Rs {ground_estimated_bill:,.0f}
            </div>
        </div>

    </div>

</div>
""")


# First Floor

with c2:

    st.html(f"""
<div class="energy-card current-card">

    <div class="card-title">
        First Floor · SFS23934
    </div>

    <div class="card-subtitle">
        Single Phase
    </div>

    <div class="card-grid">

        <div>
            <div class="card-label">
                Units
            </div>

            <div class="card-value">
                {first_units} kWh
            </div>

            <div class="card-rate">
                Rs {first_bill["rate"]:.2f}/unit
            </div>
        </div>

        <div>
            <div class="card-label">
                Est. Bill
            </div>

            <div class="card-value">
                Rs {first_bill["total"]:,.0f}
            </div>
        </div>

    </div>

</div>
""")


# Second Floor

with c3:

    st.html(f"""
<div class="energy-card current-card">

    <div class="card-title">
        Second Floor · SFS82166
    </div>

    <div class="card-subtitle">
        Single Phase
    </div>

    <div class="card-grid">

        <div>
            <div class="card-label">
                Units
            </div>

            <div class="card-value">
                {second_units} kWh
            </div>

            <div class="card-rate">
                Rs {second_bill["rate"]:.2f}/unit
            </div>
        </div>

        <div>
            <div class="card-label">
                Est. Bill
            </div>

            <div class="card-value">
                Rs {second_bill["total"]:,.0f}
            </div>
        </div>

    </div>

</div>
""")


# Total

with c4:

    st.html(f"""
<div class="energy-card current-card">

    <div class="card-title">
        TOTAL · All Floors
    </div>

    <div class="card-subtitle">
        Current Cycle
    </div>

    <div class="card-grid">

        <div>
            <div class="card-label">
                Total kWh
            </div>

            <div class="card-value">
                {current_total_units} kWh
            </div>
        </div>

        <div>
            <div class="card-label">
                Est. Bill
            </div>

            <div class="card-value">
                Rs {current_total_bill:,.0f}
            </div>
        </div>

    </div>

</div>
""")


# =========================================================
# DAILY TABLES
# =========================================================

st.html(
    '<div class="section-title">Daily Consumption</div>'
)


ground_rows = []
first_rows = []
second_rows = []


ground_table_units = 0
ground_table_cost = 0

first_table_units = 0
first_table_cost = 0

second_table_units = 0
second_table_cost = 0


for i in range(
    len(READINGS) - 1,
    -1,
    -1
):

    reading = READINGS[i]

    date_text = (
        reading["datetime"]
        .strftime("%d-%b %I:%M %p")
    )


    if i == 0:

        ground_rows.append({
            "Date": date_text,
            "Units": "—",
            "Est. Cost": "—"
        })

        first_rows.append({
            "Date": date_text,
            "Units": "—",
            "Est. Cost": "—"
        })

        second_rows.append({
            "Date": date_text,
            "Units": "—",
            "Est. Cost": "—"
        })

        continue


    previous = READINGS[i - 1]


    # Ground

    off_delta = (
        reading["ground_off"]
        - previous["ground_off"]
    )

    peak_delta = (
        reading["ground_peak"]
        - previous["ground_peak"]
    )

    ground_delta = (
        off_delta + peak_delta
    )

    ground_cost = (
        off_delta * GROUND_OFF_RATE
        +
        peak_delta * GROUND_PEAK_RATE
    )

    ground_table_units += ground_delta
    ground_table_cost += ground_cost


    ground_rows.append({
        "Date": date_text,
        "Units": f"{ground_delta} kWh",
        "Est. Cost": f"Rs {ground_cost:,.0f}"
    })


    # First

    first_delta = (
        reading["first"]
        - previous["first"]
    )

    first_accumulated = (
        reading["first"]
        - FIRST_START
    )

    first_rate, _, _ = single_phase_tariff(
        first_accumulated
    )

    first_cost = (
        first_delta * first_rate
    )

    first_table_units += first_delta
    first_table_cost += first_cost


    first_rows.append({
        "Date": date_text,
        "Units": f"{first_delta} kWh",
        "Est. Cost": f"Rs {first_cost:,.0f}"
    })


    # Second

    second_delta = (
        reading["second"]
        - previous["second"]
    )

    second_accumulated = (
        reading["second"]
        - SECOND_START
    )

    second_rate, _, _ = single_phase_tariff(
        second_accumulated
    )

    second_cost = (
        second_delta * second_rate
    )

    second_table_units += second_delta
    second_table_cost += second_cost


    second_rows.append({
        "Date": date_text,
        "Units": f"{second_delta} kWh",
        "Est. Cost": f"Rs {second_cost:,.0f}"
    })


# =========================================================
# TOTAL ROWS
# =========================================================

ground_rows.append({
    "Date": "TOTAL",
    "Units": f"{ground_table_units} kWh",
    "Est. Cost": f"Rs {ground_table_cost:,.0f}"
})

first_rows.append({
    "Date": "TOTAL",
    "Units": f"{first_table_units} kWh",
    "Est. Cost": f"Rs {first_table_cost:,.0f}"
})

second_rows.append({
    "Date": "TOTAL",
    "Units": f"{second_table_units} kWh",
    "Est. Cost": f"Rs {second_table_cost:,.0f}"
})


# =========================================================
# TABLE DISPLAY
# =========================================================

t1, t2, t3 = st.columns(
    3,
    gap="small"
)


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
        height=220
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
        height=220
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
        height=220
    )
