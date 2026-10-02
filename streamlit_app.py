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
# COMPACT PROFESSIONAL STYLE
# =========================================================

st.markdown("""
<style>

/* Give enough room below Streamlit toolbar */
.block-container {
    padding-top: 4rem !important;
    padding-bottom: 1rem !important;
    max-width: 1500px;
}

/* Reduce general spacing */
div[data-testid="stVerticalBlock"] {
    gap: 0.30rem !important;
}

div[data-testid="stHorizontalBlock"] {
    gap: 0.45rem !important;
}

/* Section headings */
.section-title {
    font-size: 14px !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
    margin-top: 8px !important;
    margin-bottom: 6px !important;
}

/* Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 8px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] > div {
    padding: 0.38rem 0.55rem !important;
}

/* Normal markdown */
div[data-testid="stMarkdownContainer"] p {
    font-size: 10px !important;
    line-height: 1.20 !important;
    margin-top: 0 !important;
    margin-bottom: 1px !important;
}

/* Bold meter/card title */
div[data-testid="stMarkdownContainer"] strong {
    font-size: 12px !important;
    font-weight: 700 !important;
}

/* Caption */
div[data-testid="stCaptionContainer"] {
    font-size: 9px !important;
    line-height: 1.15 !important;
    margin-top: -2px !important;
    margin-bottom: 1px !important;
}

/* Metrics */
div[data-testid="stMetric"] {
    padding: 0 !important;
    margin: 0 !important;
}

/* Metric label */
div[data-testid="stMetricLabel"] p {
    font-size: 10px !important;
    line-height: 1.1 !important;
    margin: 0 !important;
}

/* Metric value */
div[data-testid="stMetricValue"] {
    font-size: 17px !important;
    line-height: 1.05 !important;
    font-weight: 700 !important;
}

/* Divider */
hr {
    margin-top: 3px !important;
    margin-bottom: 3px !important;
}

/* Table text */
div[data-testid="stDataFrame"] {
    font-size: 10px !important;
}

/* Reduce unnecessary dataframe gap */
div[data-testid="stDataFrameResizable"] {
    min-height: 0 !important;
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
# Add each new reading at the bottom
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
# TARIFF SETTINGS
# =========================================================

PHL_RATE = 3.23

ELECTRICITY_DUTY_RATE = 0.015
SALES_TAX_RATE = 0.18


# Ground Floor TOU
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
# SINGLE PHASE BILL ESTIMATE
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
        "rate": rate,
        "energy": energy,
        "fixed": fixed,
    }


# =========================================================
# GROUND FLOOR 3-PHASE TOU BILL
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

    return {
        "total": total,
        "off_energy": off_energy,
        "peak_energy": peak_energy,
    }


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
    min(
        days_passed,
        CYCLE_DAYS
    )
)


# =========================================================
# CURRENT UNITS
# =========================================================

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
# BILL ESTIMATES
# =========================================================

first_bill = single_phase_bill(
    first_units,
    5
)

second_bill = single_phase_bill(
    second_units,
    3
)

ground_bill_data = ground_bill(
    ground_off_units,
    ground_peak_units
)


# =========================================================
# TOTALS
# =========================================================

total_current_units = (
    ground_total_units
    + first_units
    + second_units
)

total_estimated_bill = (
    ground_bill_data["total"]
    + first_bill["total"]
    + second_bill["total"]
)

total_previous_units = (
    GROUND_LAST_UNITS
    + FIRST_LAST_UNITS
    + SECOND_LAST_UNITS
)

total_previous_bill = (
    GROUND_LAST_BILL
    + FIRST_LAST_BILL
    + SECOND_LAST_BILL
)


# =========================================================
# PREVIOUS MONTH ACTUAL
# =========================================================

st.markdown(
    '<div class="section-title">September 2026 Actual</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(
    4,
    gap="small"
)


# Ground Floor

with c1:

    with st.container(border=True):

        st.markdown(
            "**Ground Floor · TP66310**"
        )

        st.caption("3 Phase TOU")

        a, b = st.columns(
            2,
            gap="small"
        )

        with a:

            st.metric(
                "Units",
                f"{GROUND_LAST_UNITS} kWh"
            )

        with b:

            st.metric(
                "Bill",
                f"Rs {GROUND_LAST_BILL:,.0f}"
            )


# First Floor

with c2:

    with st.container(border=True):

        st.markdown(
            "**First Floor · SFS23934**"
        )

        st.caption("Single Phase")

        a, b = st.columns(
            2,
            gap="small"
        )

        with a:

            st.metric(
                "Units",
                f"{FIRST_LAST_UNITS} kWh"
            )

        with b:

            st.metric(
                "Bill",
                f"Rs {FIRST_LAST_BILL:,.0f}"
            )


# Second Floor

with c3:

    with st.container(border=True):

        st.markdown(
            "**Second Floor · SFS82166**"
        )

        st.caption("Single Phase")

        a, b = st.columns(
            2,
            gap="small"
        )

        with a:

            st.metric(
                "Units",
                f"{SECOND_LAST_UNITS} kWh"
            )

        with b:

            st.metric(
                "Bill",
                f"Rs {SECOND_LAST_BILL:,.0f}"
            )


# Previous Month Total

with c4:

    with st.container(border=True):

        st.markdown(
            "**TOTAL · All Floors**"
        )

        st.caption("Actual")

        a, b = st.columns(
            2,
            gap="small"
        )

        with a:

            st.metric(
                "Units",
                f"{total_previous_units} kWh"
            )

        with b:

            st.metric(
                "Bill",
                f"Rs {total_previous_bill:,.0f}"
            )


# =========================================================
# CURRENT BILLING CYCLE
# =========================================================

st.markdown(
    f'''
    <div class="section-title">
        {CYCLE_LABEL} (Day {days_passed} of {CYCLE_DAYS})
    </div>
    ''',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(
    4,
    gap="small"
)


# =========================================================
# GROUND FLOOR
# =========================================================

with c1:

    with st.container(border=True):

        st.markdown(
            "**Ground Floor · TP66310**"
        )

        st.caption("3 Phase TOU")

        a, b = st.columns(
            2,
            gap="small"
        )

        with a:

            st.metric(
                "Off-Peak",
                f"{ground_off_units} kWh"
            )

            st.caption(
                f"Rs {GROUND_OFF_RATE:.2f}/unit"
            )

        with b:

            st.metric(
                "Peak",
                f"{ground_peak_units} kWh"
            )

            st.caption(
                f"Rs {GROUND_PEAK_RATE:.2f}/unit"
            )

        st.divider()

        a, b = st.columns(
            2,
            gap="small"
        )

        with a:

            st.metric(
                "Total",
                f"{ground_total_units} kWh"
            )

        with b:

            st.metric(
                "Est. Bill",
                f"Rs {ground_bill_data['total']:,.0f}"
            )


# =========================================================
# FIRST FLOOR
# =========================================================

with c2:

    with st.container(border=True):

        st.markdown(
            "**First Floor · SFS23934**"
        )

        st.caption("Single Phase")

        a, b = st.columns(
            2,
            gap="small"
        )

        with a:

            st.metric(
                "Units",
                f"{first_units} kWh"
            )

            st.caption(
                f"Rs {first_bill['rate']:.2f}/unit"
            )

        with b:

            st.metric(
                "Est. Bill",
                f"Rs {first_bill['total']:,.0f}"
            )


# =========================================================
# SECOND FLOOR
# =========================================================

with c3:

    with st.container(border=True):

        st.markdown(
            "**Second Floor · SFS82166**"
        )

        st.caption("Single Phase")

        a, b = st.columns(
            2,
            gap="small"
        )

        with a:

            st.metric(
                "Units",
                f"{second_units} kWh"
            )

            st.caption(
                f"Rs {second_bill['rate']:.2f}/unit"
            )

        with b:

            st.metric(
                "Est. Bill",
                f"Rs {second_bill['total']:,.0f}"
            )


# =========================================================
# TOTAL CARD
# =========================================================

with c4:

    with st.container(border=True):

        st.markdown(
            "**TOTAL · All Floors**"
        )

        st.caption("Current Cycle")

        a, b = st.columns(
            2,
            gap="small"
        )

        with a:

            st.metric(
                "Total kWh",
                f"{total_current_units} kWh"
            )

        with b:

            st.metric(
                "Est. Bill",
                f"Rs {total_estimated_bill:,.0f}"
            )


# =========================================================
# DAILY CONSUMPTION
# =========================================================

st.markdown(
    '<div class="section-title">Daily Consumption</div>',
    unsafe_allow_html=True
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


# =========================================================
# BUILD TABLE DATA
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


    # =====================================================
    # GROUND FLOOR
    # =====================================================

    ground_off_delta = (
        reading["ground_off"]
        - previous["ground_off"]
    )

    ground_peak_delta = (
        reading["ground_peak"]
        - previous["ground_peak"]
    )

    ground_delta = (
        ground_off_delta
        + ground_peak_delta
    )

    ground_cost = (
        ground_off_delta
        * GROUND_OFF_RATE
        +
        ground_peak_delta
        * GROUND_PEAK_RATE
    )

    ground_table_units += ground_delta
    ground_table_cost += ground_cost

    ground_rows.append({
        "Date": date_text,
        "Units": f"{ground_delta} kWh",
        "Est. Cost": f"Rs {ground_cost:,.0f}"
    })


    # =====================================================
    # FIRST FLOOR
    # =====================================================

    first_delta = (
        reading["first"]
        - previous["first"]
    )

    first_accumulated = (
        reading["first"]
        - FIRST_START
    )

    first_rate, _, _ = (
        single_phase_tariff(
            first_accumulated
        )
    )

    first_cost = (
        first_delta
        * first_rate
    )

    first_table_units += first_delta
    first_table_cost += first_cost

    first_rows.append({
        "Date": date_text,
        "Units": f"{first_delta} kWh",
        "Est. Cost": f"Rs {first_cost:,.0f}"
    })


    # =====================================================
    # SECOND FLOOR
    # =====================================================

    second_delta = (
        reading["second"]
        - previous["second"]
    )

    second_accumulated = (
        reading["second"]
        - SECOND_START
    )

    second_rate, _, _ = (
        single_phase_tariff(
            second_accumulated
        )
    )

    second_cost = (
        second_delta
        * second_rate
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
# THREE TABLES
# =========================================================

t1, t2, t3 = st.columns(
    3,
    gap="small"
)


with t1:

    st.markdown(
        "**Ground Floor · TP66310**"
    )

    st.caption("3 Phase TOU")

    ground_df = pd.DataFrame(
        ground_rows
    )

    st.dataframe(
        ground_df,
        use_container_width=True,
        hide_index=True,
        height=190
    )


with t2:

    st.markdown(
        "**First Floor · SFS23934**"
    )

    st.caption("Single Phase")

    first_df = pd.DataFrame(
        first_rows
    )

    st.dataframe(
        first_df,
        use_container_width=True,
        hide_index=True,
        height=190
    )


with t3:

    st.markdown(
        "**Second Floor · SFS82166**"
    )

    st.caption("Single Phase")

    second_df = pd.DataFrame(
        second_rows
    )

    st.dataframe(
        second_df,
        use_container_width=True,
        hide_index=True,
        height=190
    )
