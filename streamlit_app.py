import streamlit as st
import pandas as pd

from datetime import datetime, date
from zoneinfo import ZoneInfo
from textwrap import dedent


st.set_page_config(
    page_title="Energy",
    layout="wide"
)


# =========================================================
# BILLING CYCLE
# =========================================================

CYCLE_START = date(2026, 9, 5)
CYCLE_END = date(2026, 10, 4)

MONTH_LABEL = CYCLE_END.strftime("%B %Y")
LAST_MONTH_LABEL = "September 2026"

today = datetime.now(ZoneInfo("Asia/Karachi")).date()

cycle_days = (CYCLE_END - CYCLE_START).days + 1
days_passed = (today - CYCLE_START).days + 1
days_passed = max(1, min(days_passed, cycle_days))


# =========================================================
# LAST ACTUAL BILL / STARTING READINGS
# =========================================================

# Ground Floor - TP66310 - 3 Phase
TP_OFF_START = 5281
TP_PEAK_START = 723
TP_TOTAL_START = 6004

TP_LAST_UNITS = 37
TP_LAST_BILL = 3790.27


# First Floor - SFS23934
FIRST_START = 4757

FIRST_LAST_UNITS = 262
FIRST_LAST_BILL = 14482.29


# Second Floor - SFS82166
SECOND_START = 2111

SECOND_LAST_UNITS = 110
SECOND_LAST_BILL = 5708.64


# =========================================================
# METER READINGS
#
# Add every new reading here.
# =========================================================

READINGS = [

    {
        "datetime": datetime(2026, 9, 28, 9, 0),
        "first": 5046,
        "second": 2118,
        "tp_off": 5303,
        "tp_peak": 732,
    },

    {
        "datetime": datetime(2026, 9, 29, 8, 15),
        "first": 5062,
        "second": 2118,
        "tp_off": 5303,
        "tp_peak": 733,
    },

]


# =========================================================
# BILL CALCULATIONS
# =========================================================

def single_phase_bill(units, load):

    if units <= 100:
        rate = 22.44
        fixed_rate = 275
        muct = 0

    elif units <= 200:
        rate = 28.91
        fixed_rate = 300
        muct = 20

    elif units <= 300:
        rate = 33.10
        fixed_rate = 350
        muct = 40

    elif units <= 400:
        rate = 36.46
        fixed_rate = 400
        muct = 100

    elif units <= 500:
        rate = 38.95
        fixed_rate = 500
        muct = 125

    elif units <= 600:
        rate = 40.22
        fixed_rate = 675
        muct = 150

    elif units <= 700:
        rate = 41.85
        fixed_rate = 675
        muct = 175

    else:
        rate = 47.20
        fixed_rate = 675
        muct = 300

    variable = units * rate
    fixed = load * fixed_rate
    phl = units * 3.23

    subtotal = variable + fixed + phl + muct

    estimated_bill = subtotal * 1.1985

    return estimated_bill, rate


def three_phase_bill(off_peak, peak):

    off_rate = 34.53
    peak_rate = 46.85

    off_energy = off_peak * off_rate
    peak_energy = peak * peak_rate

    total_units = off_peak + peak

    fixed = 2.5 * 675
    phl = total_units * 3.23

    subtotal = off_energy + peak_energy + fixed + phl

    total_bill = subtotal * 1.1883

    energy_total = off_energy + peak_energy

    if energy_total > 0:

        off_bill = total_bill * (
            off_energy / energy_total
        )

        peak_bill = total_bill * (
            peak_energy / energy_total
        )

    else:

        off_bill = 0
        peak_bill = 0

    if total_units > 0:

        average_rate = (
            off_energy + peak_energy
        ) / total_units

    else:

        average_rate = 0

    return (
        off_bill,
        peak_bill,
        total_bill,
        off_rate,
        peak_rate,
        average_rate
    )


# =========================================================
# CURRENT VALUES
# =========================================================

latest = READINGS[-1]

first_units = latest["first"] - FIRST_START
second_units = latest["second"] - SECOND_START

tp_off_units = latest["tp_off"] - TP_OFF_START
tp_peak_units = latest["tp_peak"] - TP_PEAK_START

tp_total_units = tp_off_units + tp_peak_units


first_bill, first_rate = single_phase_bill(
    first_units,
    5
)

second_bill, second_rate = single_phase_bill(
    second_units,
    3
)

(
    tp_off_bill,
    tp_peak_bill,
    tp_total_bill,
    tp_off_rate,
    tp_peak_rate,
    tp_average_rate
) = three_phase_bill(
    tp_off_units,
    tp_peak_units
)


# =========================================================
# STYLE
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }

    .section {
        font-size: 22px;
        font-weight: 700;
        margin-top: 12px;
        margin-bottom: 12px;
    }

    .small-card {
        border: 1px solid #dddddd;
        border-radius: 14px;
        padding: 14px 18px;
        min-height: 120px;
    }

    .main-card {
        border: 1px solid #dddddd;
        border-radius: 14px;
        padding: 18px;
        min-height: 205px;
    }

    .card-title {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .small-number {
        font-size: 18px;
        font-weight: 600;
        margin: 4px 0;
    }

    .big-number {
        font-size: 32px;
        font-weight: 700;
        margin: 12px 0 3px 0;
    }

    .bill-number {
        font-size: 22px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .rate {
        font-size: 14px;
        opacity: 0.72;
    }

    .tp-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        margin-top: 12px;
    }

    .tp-box {
        border: 1px solid #e5e5e5;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
    }

    .tp-title {
        font-size: 14px;
        font-weight: 700;
    }

    .tp-units {
        font-size: 22px;
        font-weight: 700;
        margin-top: 6px;
    }

    .tp-bill {
        font-size: 15px;
        margin-top: 4px;
    }

    .tp-rate {
        font-size: 12px;
        opacity: 0.7;
        margin-top: 4px;
    }

    @media (max-width: 700px) {
        .tp-grid {
            grid-template-columns: 1fr;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LAST MONTH ACTUAL
# =========================================================

st.markdown(
    f'<div class="section">{LAST_MONTH_LABEL} — Actual</div>',
    unsafe_allow_html=True
)


c1, c2, c3 = st.columns(3)


with c1:

    st.markdown(
        dedent(
            f"""
            <div class="small-card">
                <div class="card-title">Ground Floor · TP66310</div>
                <div class="small-number">{TP_TOTAL_START:,} kWh closing</div>
                <div>{TP_LAST_UNITS} kWh billed</div>
                <div class="small-number">Rs {TP_LAST_BILL:,.0f}</div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )


with c2:

    st.markdown(
        dedent(
            f"""
            <div class="small-card">
                <div class="card-title">First Floor · SFS23934</div>
                <div class="small-number">{FIRST_START:,} kWh closing</div>
                <div>{FIRST_LAST_UNITS} kWh billed</div>
                <div class="small-number">Rs {FIRST_LAST_BILL:,.0f}</div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )


with c3:

    st.markdown(
        dedent(
            f"""
            <div class="small-card">
                <div class="card-title">Second Floor · SFS82166</div>
                <div class="small-number">{SECOND_START:,} kWh closing</div>
                <div>{SECOND_LAST_UNITS} kWh billed</div>
                <div class="small-number">Rs {SECOND_LAST_BILL:,.0f}</div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )


# =========================================================
# CURRENT MONTH
# =========================================================

st.markdown(
    f'<div class="section">{MONTH_LABEL} (Day {days_passed} of {cycle_days})</div>',
    unsafe_allow_html=True
)


c1, c2, c3 = st.columns(3)


# Ground Floor - 3 Phase

with c1:

    st.markdown(
        dedent(
            f"""
            <div class="main-card">

                <div class="card-title">
                    Ground Floor · TP66310
                </div>

                <div class="tp-grid">

                    <div class="tp-box">
                        <div class="tp-title">Off-Peak</div>
                        <div class="tp-units">{tp_off_units} kWh</div>
                        <div class="tp-bill">Rs {tp_off_bill:,.0f}</div>
                        <div class="tp-rate">Rs {tp_off_rate:.2f}/kWh</div>
                    </div>

                    <div class="tp-box">
                        <div class="tp-title">Peak</div>
                        <div class="tp-units">{tp_peak_units} kWh</div>
                        <div class="tp-bill">Rs {tp_peak_bill:,.0f}</div>
                        <div class="tp-rate">Rs {tp_peak_rate:.2f}/kWh</div>
                    </div>

                    <div class="tp-box">
                        <div class="tp-title">Total</div>
                        <div class="tp-units">{tp_total_units} kWh</div>
                        <div class="tp-bill">Rs {tp_total_bill:,.0f}</div>
                        <div class="tp-rate">Avg Rs {tp_average_rate:.2f}/kWh</div>
                    </div>

                </div>

            </div>
            """
        ),
        unsafe_allow_html=True
    )


# First Floor

with c2:

    st.markdown(
        dedent(
            f"""
            <div class="main-card">

                <div class="card-title">
                    First Floor · SFS23934
                </div>

                <div class="big-number">
                    {first_units} kWh
                </div>

                <div class="bill-number">
                    Rs {first_bill:,.0f}
                </div>

                <div class="rate">
                    Rs {first_rate:.2f}/kWh
                </div>

            </div>
            """
        ),
        unsafe_allow_html=True
    )


# Second Floor

with c3:

    st.markdown(
        dedent(
            f"""
            <div class="main-card">

                <div class="card-title">
                    Second Floor · SFS82166
                </div>

                <div class="big-number">
                    {second_units} kWh
                </div>

                <div class="bill-number">
                    Rs {second_bill:,.0f}
                </div>

                <div class="rate">
                    Rs {second_rate:.2f}/kWh
                </div>

            </div>
            """
        ),
        unsafe_allow_html=True
    )


# =========================================================
# TABLE
# =========================================================

rows = []


for i in range(len(READINGS) - 1, -1, -1):

    reading = READINGS[i]

    if i > 0:
        previous = READINGS[i - 1]

        first_daily = (
            reading["first"] -
            previous["first"]
        )

        second_daily = (
            reading["second"] -
            previous["second"]
        )

        tp_daily = (
            reading["tp_off"] +
            reading["tp_peak"]
            -
            previous["tp_off"]
            -
            previous["tp_peak"]
        )

    else:

        first_daily = None
        second_daily = None
        tp_daily = None


    # Accumulated units at this reading

    first_acc = (
        reading["first"] -
        FIRST_START
    )

    second_acc = (
        reading["second"] -
        SECOND_START
    )

    tp_off_acc = (
        reading["tp_off"] -
        TP_OFF_START
    )

    tp_peak_acc = (
        reading["tp_peak"] -
        TP_PEAK_START
    )


    first_estimate, _ = single_phase_bill(
        first_acc,
        5
    )

    second_estimate, _ = single_phase_bill(
        second_acc,
        3
    )

    _, _, tp_estimate, _, _, _ = three_phase_bill(
        tp_off_acc,
        tp_peak_acc
    )


    date_text = reading["datetime"].strftime(
        "%d-%b-%Y %I:%M %p"
    )


    rows.append(
        {
            "Date": date_text,
            "Meter": "Ground Floor · TP66310",
            "Daily Consumption":
                "—"
                if tp_daily is None
                else f"{tp_daily} kWh",
            "Estimated Bill":
                f"Rs {tp_estimate:,.0f}"
        }
    )


    rows.append(
        {
            "Date": date_text,
            "Meter": "First Floor · SFS23934",
            "Daily Consumption":
                "—"
                if first_daily is None
                else f"{first_daily} kWh",
            "Estimated Bill":
                f"Rs {first_estimate:,.0f}"
        }
    )


    rows.append(
        {
            "Date": date_text,
            "Meter": "Second Floor · SFS82166",
            "Daily Consumption":
                "—"
                if second_daily is None
                else f"{second_daily} kWh",
            "Estimated Bill":
                f"Rs {second_estimate:,.0f}"
        }
    )


st.markdown(
    '<div class="section">Readings</div>',
    unsafe_allow_html=True
)


df = pd.DataFrame(rows)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
