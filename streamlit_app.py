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
    padding-top: 3.2rem !important;
    padding-bottom: 1.5rem !important;
    max-width: 1550px;
}

/* SECTION HEADINGS */
.section-title {
    font-size: 16px;
    font-weight: 700;
    margin-top: 18px;
    margin-bottom: 10px;
    line-height: 1.2;
}

/* CARDS */
.energy-card {
    border: 1px solid rgba(128,128,128,0.30);
    border-radius: 8px;
    padding: 11px 14px;
    min-height: 105px;
    box-sizing: border-box;
}

/* CURRENT GROUND CARD */
.ground-card {
    min-height: 142px;
}

/* CARD TITLE */
.card-title {
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 2px;
    line-height: 1.2;
}

/* SUBTITLE */
.card-subtitle {
    font-size: 13px;
    opacity: 0.55;
    margin-bottom: 10px;
}

/* TWO COLUMN CARD GRID */
.card-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

/* LABEL */
.card-label {
    font-size: 14px;
    line-height: 1.15;
    opacity: 0.80;
    margin-bottom: 4px;
}

/* VALUE */
.card-value {
    font-size: 18px;
    font-weight: 700;
    line-height: 1.15;
}

/* RATE */
.card-rate {
    font-size: 13px;
    opacity: 0.55;
    margin-top: 5px;
}

/* DIVIDER */
.card-divider {
    border-top: 1px solid rgba(128,128,128,0.30);
    margin: 10px 0;
}

/* STREAMLIT COLUMNS */
div[data-testid="stHorizontalBlock"] {
    gap: 10px !important;
}

/* GENERAL VERTICAL SPACING */
div[data-testid="stVerticalBlock"] {
    gap: 0.25rem !important;
}

/* TABLE TITLES */
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

/* TABLE FONT */
div[data-testid="stDataFrame"] {
    font-size: 14px !important;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# TARIFF SETTINGS
# =========================================================

PHL_RATE = 3.23
ELECTRICITY_DUTY_RATE = 0.015
SALES_TAX_RATE = 0.18

GROUND_OFF_RATE = 34.53
GROUND_PEAK_RATE = 46.85

GROUND_FIXED_BILLING_KW = 2.5
GROUND_FIXED_RATE = 675


# =========================================================
# BILL FUNCTIONS
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


def single_phase_bill(units, load_kw):

    rate, fixed_rate, muct = single_phase_tariff(units)

    energy = units * rate
    fixed = load_kw * fixed_rate
    phl = units * PHL_RATE

    duty = (
        energy + fixed
    ) * ELECTRICITY_DUTY_RATE

    sales_tax = (
        energy
        + fixed
        + phl
        + duty
    ) * SALES_TAX_RATE

    total = (
        energy
        + fixed
        + phl
        + duty
        + sales_tax
        + muct
    )

    return {
        "total": total,
        "rate": rate
    }


def ground_bill(off_units, peak_units):

    energy = (
        off_units * GROUND_OFF_RATE
        +
        peak_units * GROUND_PEAK_RATE
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

    duty = (
        energy + fixed
    ) * ELECTRICITY_DUTY_RATE

    sales_tax = (
        energy
        + fixed
        + phl
        + duty
    ) * SALES_TAX_RATE

    return (
        energy
        + fixed
        + phl
        + duty
        + sales_tax
    )


# =========================================================
# SEPTEMBER ACTUAL KE BILL
# =========================================================

SEP_GROUND_UNITS = 37
SEP_GROUND_BILL = 3790.27

SEP_FIRST_UNITS = 262
SEP_FIRST_BILL = 14482.29

SEP_SECOND_UNITS = 110
SEP_SECOND_BILL = 5708.64


# =========================================================
# SEPTEMBER BILL CLOSING READINGS
# OFFICIAL KE READING DATE: 04-SEP-2026
# =========================================================

OLD_GROUND_OFF_START = 5281
OLD_GROUND_PEAK_START = 723

OLD_FIRST_START = 4757
OLD_SECOND_START = 2111


# =========================================================
# COMPLETED 05-SEP TO 04-OCT CYCLE
# Closing readings taken 04-Oct
# =========================================================

OCT_GROUND_OFF_END = 5307
OCT_GROUND_PEAK_END = 735

OCT_FIRST_END = 5121
OCT_SECOND_END = 2178


OCT_GROUND_OFF_UNITS = (
    OCT_GROUND_OFF_END
    - OLD_GROUND_OFF_START
)

OCT_GROUND_PEAK_UNITS = (
    OCT_GROUND_PEAK_END
    - OLD_GROUND_PEAK_START
)

OCT_GROUND_UNITS = (
    OCT_GROUND_OFF_UNITS
    + OCT_GROUND_PEAK_UNITS
)

OCT_FIRST_UNITS = (
    OCT_FIRST_END
    - OLD_FIRST_START
)

OCT_SECOND_UNITS = (
    OCT_SECOND_END
    - OLD_SECOND_START
)


OCT_GROUND_BILL = ground_bill(
    OCT_GROUND_OFF_UNITS,
    OCT_GROUND_PEAK_UNITS
)

OCT_FIRST_BILL_DATA = single_phase_bill(
    OCT_FIRST_UNITS,
    5
)

OCT_SECOND_BILL_DATA = single_phase_bill(
    OCT_SECOND_UNITS,
    3
)

OCT_FIRST_BILL = OCT_FIRST_BILL_DATA["total"]
OCT_SECOND_BILL = OCT_SECOND_BILL_DATA["total"]


# =========================================================
# CURRENT CYCLE
# 05-OCT TO 04-NOV
# =========================================================

CURRENT_START = date(2026, 10, 5)
CURRENT_END = date(2026, 11, 4)

CURRENT_LABEL = "05 Oct – 04 Nov 2026"

CURRENT_DAYS = (
    CURRENT_END - CURRENT_START
).days + 1


# Opening readings = 04-Oct closing readings

CURRENT_GROUND_OFF_START = 5307
CURRENT_GROUND_PEAK_START = 735

CURRENT_FIRST_START = 5121
CURRENT_SECOND_START = 2178


# =========================================================
# ALL RECORDED READINGS
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

]


# =========================================================
# CURRENT VALUES
# =========================================================

latest = READINGS[-1]

latest_date = latest["datetime"].date()

days_passed = (
    latest_date - CURRENT_START
).days + 1

days_passed = max(
    1,
    min(days_passed, CURRENT_DAYS)
)


current_ground_off_units = (
    latest["ground_off"]
    - CURRENT_GROUND_OFF_START
)

current_ground_peak_units = (
    latest["ground_peak"]
    - CURRENT_GROUND_PEAK_START
)

current_ground_units = (
    current_ground_off_units
    + current_ground_peak_units
)

current_first_units = (
    latest["first"]
    - CURRENT_FIRST_START
)

current_second_units = (
    latest["second"]
    - CURRENT_SECOND_START
)


current_ground_bill = ground_bill(
    current_ground_off_units,
    current_ground_peak_units
)

current_first_bill_data = single_phase_bill(
    current_first_units,
    5
)

current_second_bill_data = single_phase_bill(
    current_second_units,
    3
)

current_first_bill = (
    current_first_bill_data["total"]
)

current_second_bill = (
    current_second_bill_data["total"]
)


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


oct_total_units = (
    OCT_GROUND_UNITS
    + OCT_FIRST_UNITS
    + OCT_SECOND_UNITS
)

oct_total_bill = (
    OCT_GROUND_BILL
    + OCT_FIRST_BILL
    + OCT_SECOND_BILL
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
# CARD FUNCTION
# =========================================================

def simple_card(
    title,
    subtitle,
    units,
    bill
):

    return f"""
<div class="energy-card">

    <div class="card-title">
        {title}
    </div>

    <div class="card-subtitle">
        {subtitle}
    </div>

    <div class="card-grid">

        <div>
            <div class="card-label">
                Units
            </div>

            <div class="card-value">
                {units:,} kWh
            </div>
        </div>

        <div>
            <div class="card-label">
                Bill
            </div>

            <div class="card-value">
                Rs {bill:,.0f}
            </div>
        </div>

    </div>

</div>
"""


# =========================================================
# SEPTEMBER ACTUAL SUMMARY
# =========================================================

st.html(
    '<div class="section-title">September 2026 Actual</div>'
)

c1, c2, c3, c4 = st.columns(
    4,
    gap="small"
)


with c1:
    st.html(
        simple_card(
            "Ground Floor · TP66310",
            "3 Phase TOU",
            SEP_GROUND_UNITS,
            SEP_GROUND_BILL
        )
    )


with c2:
    st.html(
        simple_card(
            "First Floor · SFS23934",
            "Single Phase",
            SEP_FIRST_UNITS,
            SEP_FIRST_BILL
        )
    )


with c3:
    st.html(
        simple_card(
            "Second Floor · SFS82166",
            "Single Phase",
            SEP_SECOND_UNITS,
            SEP_SECOND_BILL
        )
    )


with c4:
    st.html(
        simple_card(
            "TOTAL · All Floors",
            "Actual",
            sep_total_units,
            sep_total_bill
        )
    )


# =========================================================
# OCTOBER COMPLETED CYCLE SUMMARY
# =========================================================

st.html(
    '<div class="section-title">October 2026 Estimated</div>'
)

c1, c2, c3, c4 = st.columns(
    4,
    gap="small"
)


with c1:

    st.html(
        simple_card(
            "Ground Floor · TP66310",
            "05 Sep – 04 Oct",
            OCT_GROUND_UNITS,
            OCT_GROUND_BILL
        )
    )


with c2:

    st.html(
        simple_card(
            "First Floor · SFS23934",
            "05 Sep – 04 Oct",
            OCT_FIRST_UNITS,
            OCT_FIRST_BILL
        )
    )


with c3:

    st.html(
        simple_card(
            "Second Floor · SFS82166",
            "05 Sep – 04 Oct",
            OCT_SECOND_UNITS,
            OCT_SECOND_BILL
        )
    )


with c4:

    st.html(
        simple_card(
            "TOTAL · All Floors",
            "05 Sep – 04 Oct",
            oct_total_units,
            oct_total_bill
        )
    )


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

c1, c2, c3, c4 = st.columns(
    4,
    gap="small"
)


# =========================================================
# CURRENT GROUND FLOOR
# =========================================================

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
            <div class="card-label">
                Off-Peak
            </div>

            <div class="card-value">
                {current_ground_off_units} kWh
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
            <div class="card-label">
                Total
            </div>

            <div class="card-value">
                {current_ground_units} kWh
            </div>
        </div>

        <div>
            <div class="card-label">
                Est. Bill
            </div>

            <div class="card-value">
                Rs {current_ground_bill:,.0f}
            </div>
        </div>

    </div>

</div>
""")


# =========================================================
# CURRENT FIRST FLOOR
# =========================================================

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

            <div class="card-label">
                Units
            </div>

            <div class="card-value">
                {current_first_units} kWh
            </div>

            <div class="card-rate">
                Rs {current_first_bill_data["rate"]:.2f}/unit
            </div>

        </div>

        <div>

            <div class="card-label">
                Est. Bill
            </div>

            <div class="card-value">
                Rs {current_first_bill:,.0f}
            </div>

        </div>

    </div>

</div>
""")


# =========================================================
# CURRENT SECOND FLOOR
# =========================================================

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

            <div class="card-label">
                Units
            </div>

            <div class="card-value">
                {current_second_units} kWh
            </div>

            <div class="card-rate">
                Rs {current_second_bill_data["rate"]:.2f}/unit
            </div>

        </div>

        <div>

            <div class="card-label">
                Est. Bill
            </div>

            <div class="card-value">
                Rs {current_second_bill:,.0f}
            </div>

        </div>

    </div>

</div>
""")


# =========================================================
# CURRENT TOTAL
# =========================================================

with c4:

    st.html(
        simple_card(
            "TOTAL · All Floors",
            "Current Cycle",
            current_total_units,
            current_total_bill
        )
    )


# =========================================================
# DAILY CONSUMPTION TABLES
# =========================================================

st.html(
    '<div class="section-title">Daily Consumption</div>'
)


ground_rows = []
first_rows = []
second_rows = []


ground_logged_units = 0
ground_logged_cost = 0

first_logged_units = 0
first_logged_cost = 0

second_logged_units = 0
second_logged_cost = 0


# =========================================================
# HELPER FOR SINGLE PHASE DAILY RATE
# =========================================================

def cycle_start_for_reading(reading):

    reading_date = reading["datetime"].date()

    if reading_date >= CURRENT_START:

        return {
            "first": CURRENT_FIRST_START,
            "second": CURRENT_SECOND_START
        }

    return {
        "first": OLD_FIRST_START,
        "second": OLD_SECOND_START
    }


# =========================================================
# BUILD DAILY DATA
# Each reading difference is treated as one day's usage
# =========================================================

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
            "Daily kWh": "—",
            "Est. Cost": "—"
        })

        first_rows.append({
            "Date": date_text,
            "Daily kWh": "—",
            "Est. Cost": "—"
        })

        second_rows.append({
            "Date": date_text,
            "Daily kWh": "—",
            "Est. Cost": "—"
        })

        continue


    previous = READINGS[i - 1]


    # =====================================================
    # GROUND FLOOR DAILY
    # =====================================================

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

    ground_daily_cost = (
        off_delta * GROUND_OFF_RATE
        +
        peak_delta * GROUND_PEAK_RATE
    )

    ground_logged_units += ground_delta
    ground_logged_cost += ground_daily_cost


    ground_rows.append({
        "Date": date_text,
        "Daily kWh": f"{ground_delta} kWh",
        "Est. Cost": f"Rs {ground_daily_cost:,.0f}"
    })


    # =====================================================
    # FIRST FLOOR DAILY
    # =====================================================

    baselines = cycle_start_for_reading(
        reading
    )

    first_delta = (
        reading["first"]
        - previous["first"]
    )

    first_cycle_units = (
        reading["first"]
        - baselines["first"]
    )

    first_daily_rate, _, _ = (
        single_phase_tariff(
            max(first_cycle_units, 0)
        )
    )

    first_daily_cost = (
        first_delta
        * first_daily_rate
    )

    first_logged_units += first_delta
    first_logged_cost += first_daily_cost


    first_rows.append({
        "Date": date_text,
        "Daily kWh": f"{first_delta} kWh",
        "Est. Cost": f"Rs {first_daily_cost:,.0f}"
    })


    # =====================================================
    # SECOND FLOOR DAILY
    # =====================================================

    second_delta = (
        reading["second"]
        - previous["second"]
    )

    second_cycle_units = (
        reading["second"]
        - baselines["second"]
    )

    second_daily_rate, _, _ = (
        single_phase_tariff(
            max(second_cycle_units, 0)
        )
    )

    second_daily_cost = (
        second_delta
        * second_daily_rate
    )

    second_logged_units += second_delta
    second_logged_cost += second_daily_cost


    second_rows.append({
        "Date": date_text,
        "Daily kWh": f"{second_delta} kWh",
        "Est. Cost": f"Rs {second_daily_cost:,.0f}"
    })


# =========================================================
# TABLE TOTALS
# =========================================================

ground_rows.append({
    "Date": "LOGGED TOTAL",
    "Daily kWh": f"{ground_logged_units} kWh",
    "Est. Cost": f"Rs {ground_logged_cost:,.0f}"
})

first_rows.append({
    "Date": "LOGGED TOTAL",
    "Daily kWh": f"{first_logged_units} kWh",
    "Est. Cost": f"Rs {first_logged_cost:,.0f}"
})

second_rows.append({
    "Date": "LOGGED TOTAL",
    "Daily kWh": f"{second_logged_units} kWh",
    "Est. Cost": f"Rs {second_logged_cost:,.0f}"
})


# =========================================================
# DISPLAY TABLES
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
        height=350
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
        height=350
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
        height=350
    )
