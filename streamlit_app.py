import streamlit as st

st.set_page_config(page_title="Energy", layout="wide")

# -----------------------------
# CURRENT METER READINGS
# -----------------------------

# Meter 1 - SFS23934
m1_start = 4757
m1_current = 5062
m1_load = 5

# Meter 2 - SFS82166
m2_start = 2111
m2_current = 2118
m2_load = 3

# Meter 3 - TP66310
tp_off_start = 5281
tp_off_current = 5303

tp_peak_start = 723
tp_peak_current = 733

tp_load = 5


# -----------------------------
# BILL CALCULATIONS
# -----------------------------

def non_tou_bill(units, load):

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

    # approximate taxes/duties using recent bill ratio
    estimated_bill = subtotal * 1.1985

    return estimated_bill


def tou_bill(off_peak, peak, load):

    off_charge = off_peak * 34.53
    peak_charge = peak * 46.85

    total_units = off_peak + peak

    fixed = (load * 0.5) * 675
    phl = total_units * 3.23

    subtotal = off_charge + peak_charge + fixed + phl

    total_bill = subtotal * 1.1883

    energy_total = off_charge + peak_charge

    if energy_total > 0:
        off_bill = total_bill * (off_charge / energy_total)
        peak_bill = total_bill * (peak_charge / energy_total)
    else:
        off_bill = 0
        peak_bill = 0

    return off_bill, peak_bill, total_bill


# -----------------------------
# CONSUMPTION
# -----------------------------

m1_units = m1_current - m1_start
m2_units = m2_current - m2_start

tp_off_units = tp_off_current - tp_off_start
tp_peak_units = tp_peak_current - tp_peak_start
tp_total_units = tp_off_units + tp_peak_units


m1_bill = non_tou_bill(m1_units, m1_load)
m2_bill = non_tou_bill(m2_units, m2_load)

tp_off_bill, tp_peak_bill, tp_total_bill = tou_bill(
    tp_off_units,
    tp_peak_units,
    tp_load
)


# -----------------------------
# STYLE
# -----------------------------

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
}

.card {
    border: 1px solid #dddddd;
    border-radius: 14px;
    padding: 24px;
    text-align: center;
    min-height: 210px;
}

.meter {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 25px;
}

.units {
    font-size: 36px;
    font-weight: 700;
}

.bill {
    font-size: 24px;
    margin-top: 12px;
}

.tp-row {
    margin-top: 13px;
    font-size: 20px;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# CARDS
# -----------------------------

c1, c2, c3 = st.columns(3)

with c1:

    st.markdown(
        f"""
        <div class="card">
            <div class="meter">SFS23934</div>
            <div class="units">{m1_units} kWh</div>
            <div class="bill">Rs {m1_bill:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c2:

    st.markdown(
        f"""
        <div class="card">
            <div class="meter">SFS82166</div>
            <div class="units">{m2_units} kWh</div>
            <div class="bill">Rs {m2_bill:,.0f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with c3:

    st.markdown(
        f"""
        <div class="card">
            <div class="meter">TP66310</div>

            <div class="tp-row">
                Off-Peak: <b>{tp_off_units} kWh</b>
                &nbsp; Rs {tp_off_bill:,.0f}
            </div>

            <div class="tp-row">
                Peak: <b>{tp_peak_units} kWh</b>
                &nbsp; Rs {tp_peak_bill:,.0f}
            </div>

            <div class="tp-row">
                Total: <b>{tp_total_units} kWh</b>
                &nbsp; Rs {tp_total_bill:,.0f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
