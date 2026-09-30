# =========================================================
# DAILY CONSUMPTION TABLES
# =========================================================

st.subheader("Daily Consumption")

ground_rows = []
first_rows = []
second_rows = []


# Running totals for table
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


    # =====================================================
    # FIRST PHOTO HAS NO PREVIOUS PHOTO
    # =====================================================

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
        ground_off_delta * GROUND_OFF_RATE
        +
        ground_peak_delta * GROUND_PEAK_RATE
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
# THREE SIDE-BY-SIDE TABLES
# =========================================================

t1, t2, t3 = st.columns(3)


with t1:

    st.markdown(
        "**Ground Floor · TP66310**"
    )

    st.caption(
        "3 Phase TOU"
    )

    ground_df = pd.DataFrame(
        ground_rows
    )

    st.dataframe(
        ground_df,
        use_container_width=True,
        hide_index=True
    )


with t2:

    st.markdown(
        "**First Floor · SFS23934**"
    )

    st.caption(
        "Single Phase"
    )

    first_df = pd.DataFrame(
        first_rows
    )

    st.dataframe(
        first_df,
        use_container_width=True,
        hide_index=True
    )


with t3:

    st.markdown(
        "**Second Floor · SFS82166**"
    )

    st.caption(
        "Single Phase"
    )

    second_df = pd.DataFrame(
        second_rows
    )

    st.dataframe(
        second_df,
        use_container_width=True,
        hide_index=True
    )
