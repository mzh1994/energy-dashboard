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
# BILLING CYCLE
# Previous KE reading date: 04-Sep-2026
# Current provisional cycle: 05-Sep-2026 to 04-Oct-2026
# =========================================================

CYCLE_START = date(2026, 9, 5)
CYCLE_END = date(2026, 10, 4)

CYCLE_LABEL = "05 Sep – 04 Oct 2026"

CYCLE_DAYS = (CYCLE_END - CYCLE_START).days + 1


# =========================================================
# METERS
# =========================================================

# Ground Floor
# 3 Phase / Peak + Off-Peak
GROUND_METER = "TP66310"

# First Floor
FIRST_METER = "SFS23934"

# Second Floor
SECOND_METER = "SFS82166"


# =========================================================
# PREVIOUS ACTUAL BILL
# KE reading date: 04-Sep-2026
# =========================================================

# Ground Floor - TP66310
GROUND_OFF_START = 5281
GROUND_PEAK_START = 723
GROUND_TOTAL_START = 6004

GROUND_LAST_UNITS = 37
GROUND_LAST_BILL = 3790.27


# First Floor - SFS23934
FIRST_START = 4757

FIRST_LAST_UNITS = 262
FIRST_LAST_BILL = 14482.29


# Second Floor - SFS82166
SECOND_START = 2111

SECOND_LAST_UNITS = 110
SECOND_LAST_BILL = 5708.64


# =========================================================
# READINGS
#
# Add every new reading at the bottom of this list.
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

]


# =========================================================
# TARIFFS
# =========================================================

PHL_RATE = 3.23
ELECTRICITY_DUTY_RATE = 0.015
SALES_TAX_RATE = 0.18

GROUND_OFF_RATE = 34.53
GROUND_PEAK_RATE = 46.85

# Previous actual bill charged 2.5 x Rs 675 fixed charge
GROUND_FIXED_BILLING_KW = 2.5
GROUND_FIXED_RATE = 675


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
# ACCUMULATED BILL ESTIMATION
#
# This includes:
# - Variable energy
# - Fixed charges
# - PHL surcharge
# - Estimated electricity duty
# - Estimated sales tax
# - MUCT where applicable
#
# FCA / quarterly adjustments are NOT predictable before
# the actual KE bill arrives.
# =========================================================

def single_phase_bill(units, load_kw):

    rate, fixed_rate, muct = single_phase_tariff(units)

    energy = units * rate
    fixed = load_kw * fixed_rate
    phl = units * PHL_RATE

    duty = (
        energy + fixed
    ) * ELECTRICITY_DUTY_RATE

    sales_tax = (
        energy +
        fixed +
        phl +
        duty
    ) * SALES_TAX_RATE

    total = (
        energy +
        fixed +
        phl +
        duty +
        sales_tax +
        muct
    )

    return {
        "total": total,
        "rate": rate,
        "energy": energy,
        "fixed": fixed,
    }


def ground_bill(off_units, peak_units):

    off_energy = off_units * GROUND_OFF_RATE
    peak_energy = peak_units * GROUND_PEAK_RATE

    energy = off_energy + peak_energy

    total_units = off_units + peak_units

    fixed = (
        GROUND_FIXED_BILLING_KW *
        GROUND_FIXED_RATE
    )

    phl = total_units * PHL_RATE

    duty = (
        energy + fixed
    ) * ELECTRICITY_DUTY_RATE

    sales_tax = (
        energy +
        fixed +
        phl +
        duty
    ) * SALES_TAX_RATE

    total = (
        energy +
        fixed +
        phl +
        duty +
        sales_tax
    )

    return {
        "total": total,
        "off_energy": off_energy,
        "peak_energy": peak_energy,
    }


# =========================================================
# CURRENT READING
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


# =========================================================
# CURRENT CONSUMPTION
# =========================================================

first_units = (
    latest["first"] -
    FIRST_START
)

second_units = (
    latest["second"] -
    SECOND_START
)

ground_off_units = (
    latest["ground_off"] -
    GROUND_OFF_START
)

ground_peak_units = (
    latest["ground_peak"] -
    GROUND_PEAK_START
)

ground_total_units = (
    ground_off_units +
    ground_peak_units
)


# =========================================================
# CURRENT BILL ESTIMATES
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
# PREVIOUS ACTUAL BILL
# =========================================================

st.subheader("Sep 2026 Actual")

c1, c2, c3 = st.columns(3)


with c1:

    with st.container(border=True):

        st.markdown(
            "**Ground Floor · TP66310**"
        )

        st.metric(
            "Closing",
            f"{GROUND_TOTAL_START:,} kWh"
        )

        st.metric(
            "Actual Bill",
            f"Rs {GROUND_LAST_BILL:,.0f}"
        )


with c2:

    with st.container(border=True):

        st.markdown(
            "**First Floor · SFS23934**"
        )

        st.metric(
            "Closing",
            f"{FIRST_START:,} kWh"
        )

        st.metric(
            "Actual Bill",
            f"Rs {FIRST_LAST_BILL:,.0f}"
        )


with c3:

    with st.container(border=True):

        st.markdown(
            "**Second Floor · SFS82166**"
        )

        st.metric(
            "Closing",
            f"{SECOND_START:,} kWh"
        )

        st.metric(
            "Actual Bill",
            f"Rs {SECOND_LAST_BILL:,.0f}"
        )


# =========================================================
# CURRENT CYCLE
# =========================================================

st.subheader(
    f"{CYCLE_LABEL} "
    f"(Day {days_passed} of {CYCLE_DAYS})"
)


c1, c2, c3 = st.columns(3)


# =========================================================
# GROUND FLOOR
# =========================================================

with c1:

    with st.container(border=True):

        st.markdown(
            "**Ground Floor · TP66310**"
        )

        a, b = st.columns(2)

        with a:

            st.metric(
                "Off-Peak",
                f"{ground_off_units} kWh"
            )

            st.caption(
                f"Rs {GROUND_OFF_RATE:.2f}/kWh"
            )

            st.caption(
                f"Energy Rs "
                f"{ground_bill_data['off_energy']:,.0f}"
            )

        with b:

            st.metric(
                "Peak",
                f"{ground_peak_units} kWh"
            )

            st.caption(
                f"Rs {GROUND_PEAK_RATE:.2f}/kWh"
            )

            st.caption(
                f"Energy Rs "
                f"{ground_bill_data['peak_energy']:,.0f}"
            )

        st.divider()

        st.metric(
            "Total",
            f"{ground_total_units} kWh"
        )

        st.metric(
            "Estimated Bill",
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

        st.metric(
            "Consumption",
            f"{first_units} kWh"
        )

        st.metric(
            "Estimated Bill",
            f"Rs {first_bill['total']:,.0f}"
        )

        st.caption(
            f"Tariff Rs "
            f"{first_bill['rate']:.2f}/kWh"
        )


# =========================================================
# SECOND FLOOR
# =========================================================

with c3:

    with st.container(border=True):

        st.markdown(
            "**Second Floor · SFS82166**"
        )

        st.metric(
            "Consumption",
            f"{second_units} kWh"
        )

        st.metric(
            "Estimated Bill",
            f"Rs {second_bill['total']:,.0f}"
        )

        st.caption(
            f"Tariff Rs "
            f"{second_bill['rate']:.2f}/kWh"
        )


# =========================================================
# READINGS TABLE
# =========================================================

st.subheader("Readings")

rows = []


for i in range(
    len(READINGS) - 1,
    -1,
    -1
):

    reading = READINGS[i]

    date_text = (
        reading["datetime"]
        .strftime(
            "%d-%b-%Y %I:%M %p"
        )
    )


    # -----------------------------------------------------
    # NO EARLIER PHOTO AVAILABLE
    # -----------------------------------------------------

    if i == 0:

        rows.append(
            {
                "Date": date_text,
                "Meter":
                    "Ground Floor · TP66310",
                "Consumption":
                    "—",
                "Estimated Daily Cost":
                    "—"
            }
        )

        rows.append(
            {
                "Date": date_text,
                "Meter":
                    "First Floor · SFS23934",
                "Consumption":
                    "—",
                "Estimated Daily Cost":
                    "—"
            }
        )

        rows.append(
            {
                "Date": date_text,
                "Meter":
                    "Second Floor · SFS82166",
                "Consumption":
                    "—",
                "Estimated Daily Cost":
                    "—"
            }
        )

        continue


    previous = READINGS[i - 1]


    # =====================================================
    # GROUND FLOOR INTERVAL
    # =====================================================

    ground_off_delta = (
        reading["ground_off"] -
        previous["ground_off"]
    )

    ground_peak_delta = (
        reading["ground_peak"] -
        previous["ground_peak"]
    )

    ground_delta = (
        ground_off_delta +
        ground_peak_delta
    )

    ground_daily_cost = (
        ground_off_delta *
        GROUND_OFF_RATE
        +
        ground_peak_delta *
        GROUND_PEAK_RATE
    )


    rows.append(
        {
            "Date": date_text,

            "Meter":
                "Ground Floor · TP66310",

            "Consumption":
                f"{ground_delta} kWh",

            "Estimated Daily Cost":
                f"Rs {ground_daily_cost:,.0f}"
        }
    )


    # =====================================================
    # FIRST FLOOR INTERVAL
    # =====================================================

    first_delta = (
        reading["first"] -
        previous["first"]
    )

    first_accumulated = (
        reading["first"] -
        FIRST_START
    )

    first_daily_rate, _, _ = (
        single_phase_tariff(
            first_accumulated
        )
    )

    first_daily_cost = (
        first_delta *
        first_daily_rate
    )


    rows.append(
        {
            "Date": date_text,

            "Meter":
                "First Floor · SFS23934",

            "Consumption":
                f"{first_delta} kWh",

            "Estimated Daily Cost":
                f"Rs {first_daily_cost:,.0f}"
        }
    )


    # =====================================================
    # SECOND FLOOR INTERVAL
    # =====================================================

    second_delta = (
        reading["second"] -
        previous["second"]
    )

    second_accumulated = (
        reading["second"] -
        SECOND_START
    )

    second_daily_rate, _, _ = (
        single_phase_tariff(
            second_accumulated
        )
    )

    second_daily_cost = (
        second_delta *
        second_daily_rate
    )


    rows.append(
        {
            "Date": date_text,

            "Meter":
                "Second Floor · SFS82166",

            "Consumption":
                f"{second_delta} kWh",

            "Estimated Daily Cost":
                f"Rs {second_daily_cost:,.0f}"
        }
    )


# =========================================================
# DISPLAY TABLE
# =========================================================

df = pd.DataFrame(rows)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
