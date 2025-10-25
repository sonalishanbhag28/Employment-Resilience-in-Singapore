import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Importing data
df_rel_change = pd.read_csv("data//ChangesInEmploymentBySectorRelative.csv")
df_recovery_time = pd.read_csv("data//RecoveryTimeBySector.csv")
df_yearly_employment = pd.read_csv("data//AbsoluteEmploymentYearly.csv")
df_recovery_gender = pd.read_csv("data//RecoveryByGender.csv")
df_employment_age = pd.read_csv("data//EmploymentByAge.csv")
df_pre_during_post = pd.read_csv("data//PreDuringPost.csv")

# Dashboard Setup
st.set_page_config(page_title="Employment Resilience in Singapore", layout="wide")
st.header("Employment Resilience in Singapore")
st.markdown("#### Industry-wise Analysis of COVID-19's Impact on the Workforce")
tab1, tab2 = st.tabs(["Overview of Key Resilience Metrics", "Detailed Analysis of Recovery, Age, and Gender"])

# Session State
if "fig1_mode" not in st.session_state:
    st.session_state.fig1_mode = "selected"
if "fig2_mode" not in st.session_state:
    st.session_state.fig2_mode = "selected"

# Sidebar Filter
st.sidebar.image("https://www.mom.gov.sg/html/mom/images/branding/mom-logo-white.svg", width=300)
st.sidebar.header("Filter")

sector_list = []
for col in df_rel_change.columns:
    if col != "Quarter":
        sector_list.append(col)

selected_sector = st.sidebar.selectbox("Pick a sector:", sector_list)
total = "All Sectors"

if selected_sector != total:
    sectors = [total, selected_sector]
else:
    sectors = [selected_sector]

# Colour Scheme for Graphs
custom_colours = ["#F79256", "#1D4E98", "#7DCFB6", "#FBD1A2", "#00B2CA"]

# Tab 1: Overview of Key Resilience Metrics
with tab1:
    # First Row
    with st.container():
        col1, col2 = st.columns(2)
        # Chart 1: Line Chart for Yearly Employment with 2020 as Baseline
        with col1:
            st.subheader("Yearly Employment by Sector")
            st.write("Relative Employment Compared to 2020 (2020 = 1.0)")

            df_yearly_employment.set_index("Industry", inplace=True)
            base_year = "2020"
            df_ratio_rel = df_yearly_employment.div(df_yearly_employment[base_year], axis=0)

            latest_year = df_ratio_rel.columns[-1]
            top5 = df_ratio_rel[latest_year].sort_values(ascending=False).head(5).index
            bottom5 = df_ratio_rel[latest_year].sort_values(ascending=True).head(5).index

            colA, colB, colC = st.columns(3)
            show_top5 = colA.button(f"Top 5 (as of {latest_year}) ↑")
            show_bottom5 = colB.button(f"Bottom 5 (as of {latest_year}) ↓")
            show_selected = colC.button("Selected Sector")

            if show_top5:
                st.session_state.fig1_mode = "top"
            elif show_bottom5:
                st.session_state.fig1_mode = "bot"
            elif show_selected:
                st.session_state.fig1_mode = "selected"

            if st.session_state.fig1_mode == "top":
                df_ratio_rel_display = df_ratio_rel.loc[top5]
                order = top5
            elif st.session_state.fig1_mode == "bot":
                df_ratio_rel_display = df_ratio_rel.loc[bottom5]
                order = bottom5
            else:
                fig1_sectors = st.multiselect("Select additional sectors for comparison:", sector_list, default=selected_sector)
                if total not in fig1_sectors:
                    fig1_sectors.append(total)
                df_ratio_rel_display = df_ratio_rel.loc[fig1_sectors]
                order = fig1_sectors

            df_long = df_ratio_rel_display.T.reset_index().melt(id_vars="index", var_name="Industry", value_name="Ratio")
            df_long.rename(columns={"index": "Year"}, inplace=True)

            fig1 = px.line(
                df_long,
                x="Year",
                y="Ratio",
                color="Industry",
                markers=True,
                color_discrete_sequence=custom_colours
            )
            fig1.update_traces(hovertemplate="<br>Ratio: %{y:.3f}")
            fig1.update_layout(
                yaxis=dict(range=[0.7, 1.3], title="Relative Index"),
                legend_title_text="Industry",
                hovermode="x unified",
                width=700,
                height=400
            )
            st.plotly_chart(fig1, use_container_width=True)

        # Chart 2: Bar Chart for Pre-, During, and Post-COVID
        with col2:
            st.subheader("Average Employment by Sector and Time Period")
            st.write("Comparison of Pre-, During and Post-COVID Employment")
            fig2_col1, fig2_col2, fig2_col3 = st.columns(3)
            fig2_show_top5 = fig2_col1.button(f"Top 5 (as of 2024) ↑", key="fig2button1")
            fig2_show_bottom5 = fig2_col2.button(f"Bottom 5 (as of 2024) ↓", key="fig2button2")
            fig2_show_selected = fig2_col3.button("Selected Sector", key="fig2button3")

            if fig2_show_top5:
                st.session_state.fig2_mode = "top"
            elif fig2_show_bottom5:
                st.session_state.fig2_mode = "bot"
            elif fig2_show_selected:
                st.session_state.fig2_mode = "selected"

            if st.session_state.fig2_mode == "top":
                top5 = (df_pre_during_post
                        .sort_values('Pct Change 2022-2024', ascending=False)
                        .head(5)['Data Series'].tolist())
                fig2_sectors = top5
            elif st.session_state.fig2_mode == "bot":
                bottom5 = (df_pre_during_post
                           .sort_values('Pct Change 2022-2024', ascending=True)
                           .head(5)['Data Series'].tolist())
                fig2_sectors = bottom5
            else:
                fig2_sectors = st.multiselect("Select additional sectors for comparison:", sector_list, default=selected_sector, key="fig2multiselect")

            filtered_data = df_pre_during_post[df_pre_during_post['Data Series'].isin(fig2_sectors)].copy()

            fig = go.Figure()

            # Bar 1 for 2017-2019: Pre-COVID period
            fig.add_trace(go.Bar(
                x=filtered_data['Avg 2017-2019'],
                y=filtered_data['Data Series'],
                name='2017-2019: Pre-COVID',
                marker_color=custom_colours[4],
                orientation='h',
                text=[f"{v:.0f}K" for v in filtered_data['Avg 2017-2019']],
                textposition='outside',
                cliponaxis=False
            ))

            # Bar 2 for 2020-2021: During COVID period
            fig.add_trace(go.Bar(
                x=filtered_data['Avg 2020-2021'],
                y=filtered_data['Data Series'],
                name='2020-2021: During COVID',
                marker_color=custom_colours[0],
                orientation='h',
                text=[f"{v:.0f}K ({p:+.1f}%)" for v, p in
                      zip(filtered_data['Avg 2020-2021'], filtered_data['Pct Change 2020-2021'])],
                textposition='outside',
                cliponaxis=False
            ))

            # Bar 3 for 2022-2024: Post-COVID period
            fig.add_trace(go.Bar(
                x=filtered_data['Avg 2022-2024'],
                y=filtered_data['Data Series'],
                name='2022-2024: Post-COVID',
                marker_color=custom_colours[1],
                orientation='h',
                text=[f"{v:.0f}K ({p:+.1f}%)" for v, p in
                      zip(filtered_data['Avg 2022-2024'], filtered_data['Pct Change 2022-2024'])],
                textposition='outside',
                cliponaxis=False
            ))

            # Labels and Sizing
            fig.update_layout(
                barmode='group',
                xaxis_title='Average Employed Residents (Thousands)',
                yaxis_title='Industry',
                height=600,
                width=1100,
                margin=dict(t=60, l=100, b=60, r=250),
                legend=dict(orientation="v", x=6, y=1, xanchor="right", yanchor="top")
            )

            fig.update_yaxes(autorange="reversed")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Second Row
    with st.container():
        col1, col2 = st.columns(2)
        # Chart 3: Line Chart for Quarterly Employment Change
        with col1:
            st.subheader("Quarter-on-Quarter Relative Change in Employment")
            st.write("Compared to the Previous Quarter, in Percent")
            fig3 = px.line(df_rel_change, x="Quarter", y=sectors, height=500, width=1000, template="gridon", color_discrete_sequence=[custom_colours[2], custom_colours[0]])
            fig3.add_hline(y=0, line_width=2, line_dash="dash", line_color="red")
            fig3.update_layout(yaxis_title="% Change in Employment", yaxis_tickformat=".0%", legend_title_text="Sectors")
            for sec in sectors:
                max_value = df_rel_change[sec].max()
                max_quarter = df_rel_change.index[df_rel_change[sec] == max_value].values[0]
                max_quarter_name = df_rel_change["Quarter"].iloc[max_quarter]
                min_value = df_rel_change[sec].min()
                min_quarter = df_rel_change.index[df_rel_change[sec] == min_value].values[0]
                min_quarter_name = df_rel_change["Quarter"].iloc[min_quarter]
                fig3.add_annotation(x=max_quarter + 0.3, y=max_value + 0.001, text=f"{max_quarter_name}:<br>{max_value:.1%}",
                                    font=dict(size=14, weight="bold", color=custom_colours[2] if sec == total else custom_colours[0]),
                                    arrowcolor="white", arrowhead=4, ax=50)
                fig3.add_annotation(x=min_quarter - 0.3, y=min_value - 0.001, text=f"{min_quarter_name}:<br>{min_value:.1%}",
                                    font=dict(size=14, weight="bold", color=custom_colours[2] if sec == total else custom_colours[0]),
                                    arrowcolor="white", arrowhead=4, ax=-50)
            st.plotly_chart(fig3, use_container_width=True, height=200)

        # Chart 4: Heatmap for Quarterly Employment Change
        with col2:
            st.subheader("Employment Change by Year and Quarter")
            st.write("Compared to the Previous Quarter, in Percent")
            df_rel_change["Year"] = df_rel_change["Quarter"].str[0:4]
            df_rel_change["Quarter"] = df_rel_change["Quarter"].str[5:7]

            df_rel_change_selected = df_rel_change[[selected_sector, "Year", "Quarter"]]
            df_rel_change_pivot = df_rel_change_selected.pivot(columns="Quarter", index="Year", values=selected_sector)

            fig4 = px.imshow(df_rel_change_pivot, text_auto=".2%", color_continuous_scale=[custom_colours[0], "#ffffff", custom_colours[1]], zmin=df_rel_change_pivot.min().min(),
                             zmax=df_rel_change_pivot.max().max(), aspect="auto", template="gridon", height=500, width=1000)
            fig4.update_layout(coloraxis_colorbar_tickformat=".0%")
            st.plotly_chart(fig4, use_container_width=True, height=200)

# Tab 2: Detailed Analysis of Recovery, Age, and Gender
with tab2:
    # First Row
    with st.container():
        col1, col2 = st.columns(2)
        # Chart 5: Bar Chart for Recovery by Gender
        with col1:
            st.subheader("Post-COVID Employment Change by Gender")
            st.write("Change in Average Employment from 2020-2021 to 2022-2024, in Percent")
            combined_gender = df_recovery_gender

            industry_df = combined_gender[combined_gender["Industries"] == selected_sector]
            all_df = combined_gender[combined_gender["Industries"] == "All Sectors"]

            comparison_df = pd.concat([industry_df, all_df], ignore_index=True)
            comparison_df["Type"] = np.where(comparison_df["Industries"] == selected_sector, selected_sector, "All Sectors")

            fig5 = px.bar(
                comparison_df,
                x="Gender",
                y="Recovery %",
                color="Type",
                color_discrete_sequence=[custom_colours[4], custom_colours[1]],
                barmode="group",
                text_auto=".2f"
            )

            fig5.update_layout(
                yaxis=dict(title="Recovery %", range=[-2, 20]),
                xaxis_title="Gender",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=40, r=40, t=60, b=40),
                width=600,
                height=450
            )

            st.plotly_chart(fig5, use_container_width=False)

    # Chart 6: Bar Chart for Recovery Speed
        with col2:
            st.subheader("Recovery Speed by Industry")
            st.write("Time in Quarters until Absolute Employment Reached Pre-COVID Levels (2020 Q1)")
            colours = [custom_colours[1] if sector == total else custom_colours[4] if sector == selected_sector else custom_colours[3] for sector in
                       df_recovery_time.sort_values(by="Recovery Time", ascending=False)["Sector"]]
            fig6 = px.bar(df_recovery_time.sort_values(by="Recovery Time", ascending=False), x="Recovery Time", y="Sector",
                          height=500, width=1000, template="gridon", text="Recovery Time")
            fig6.update_traces(marker_color=colours, texttemplate='%{text:.f} Quarters', textposition='outside')
            st.plotly_chart(fig6, use_container_width=True, height=200)

    # Chart 7: Line Chart for Employment by Age
    st.subheader("Employment Trends by Age Group")
    st.write("COVID Impact and Recovery Patterns (2016-2024)")
    df_long = df_employment_age

    # Filters for year and industry selection
    filter_mask = df_long['Year'] >= 2016

    if selected_sector != 'All Sectors':
        filter_mask &= (df_long['Data Series'] == selected_sector)

    filtered_df = df_long[filter_mask]
    chart_df = filtered_df.groupby(['Year', 'Age Band'], as_index=False)['Employment'].sum()

    fig = px.line(
        chart_df,
        x='Year',
        y='Employment',
        color='Age Band',
        markers=True,
        color_discrete_sequence=custom_colours,
    )

    # Highlighting the COVID-19 periods
    fig.add_vrect(x0=2016, x1=2019.9, line_width=0, annotation_text="Pre-COVID")
    fig.add_vrect(x0=2020, x1=2021.9, fillcolor="LightSalmon", opacity=0.3, line_width=0, annotation_text="COVID")
    fig.add_vrect(x0=2022, x1=2024.1, line_width=0, annotation_text="Post-COVID")

    # Updating axes labels
    fig.update_layout(
        xaxis=dict(dtick=1),
        yaxis_title='Employment (in Thousands)',
        legend_title_text='Age Band'
    )

    # Adding yearly % change annotations after 2019
    chart_df['Pct_Change'] = chart_df.groupby('Age Band')['Employment'].pct_change() * 100
    for band_idx, band in enumerate(chart_df['Age Band'].unique()):
        band_data = chart_df[chart_df['Age Band'] == band]
        for _, row in band_data.iterrows():
            year = row['Year']
            pct = row['Pct_Change']
            y_val = row['Employment']
            if year > 2019 and pd.notna(pct):
                fig.add_annotation(
                    x=year,
                    y=y_val * 1.03 if y_val != 0 else 15 * (band_idx + 1),
                    text=f"{pct:+.1f}%",
                    showarrow=False,
                    font=dict(size=10, color="green" if pct > 0 else "red"),
                    bgcolor="white",
                )

    fig.update_layout(width=2500, height=600)
    st.plotly_chart(fig, use_container_width=False)
