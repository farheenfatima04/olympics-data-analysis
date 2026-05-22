import streamlit as st
import pandas as pd
import preprocessor
import helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------- LOAD DATA ---------------- #
df = pd.read_csv("athlete_events.csv")
region_df = pd.read_csv("noc_regions.csv")

df = preprocessor.preprocess(df, region_df)

# ---------------- SIDEBAR ---------------- #
st.sidebar.title("Olympics Analysis")

st.sidebar.image(
    "https://e7.pngegg.com/pngimages/1020/402/png-clipart-2024-summer-olympics-brand-circle-area-olympic-rings-olympics-logo-text-sport.png"
)

user_menu = st.sidebar.radio(
    "Select Option",
    ["Medal Tally", "Overall Analysis", "Country-wise Analysis", "Athlete wise Analysis"]
)

# ---------------- MEDAL TALLY ---------------- #
if user_menu == "Medal Tally":

    st.title("Medal Tally")

    years, country = helper.country_year_list(df)

    selected_year = st.selectbox("Select Year", years)
    selected_country = st.selectbox("Select Country", country)

    st.table(helper.fetch_medal_tally(df, selected_year, selected_country))

# ---------------- OVERALL ANALYSIS ---------------- #
elif user_menu == "Overall Analysis":

    st.title("Top Statistics")

    st.write("Editions:", df['Year'].nunique() - 1)
    st.write("Cities:", df['City'].nunique())
    st.write("Sports:", df['Sport'].nunique())
    st.write("Events:", df['Event'].nunique())
    st.write("Athletes:", df['Name'].nunique())
    st.write("Nations:", df['region'].nunique())

    # ---- OVER TIME ---- #
    for col in ["region", "Event", "Name"]:
        data = helper.data_over_time(df, col)
        fig = px.line(data, x="Edition", y=col)
        st.plotly_chart(fig)

    # ---- HEATMAP SAFE ---- #
    st.subheader("Events Over Time by Sport")

    pivot = df.drop_duplicates(['Year', 'Sport', 'Event']).pivot_table(
        index='Sport',
        columns='Year',
        values='Event',
        aggfunc='count',
        fill_value=0
    )

    if pivot.empty:
        st.warning("No data available")
    else:
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(pivot.astype(float), ax=ax, annot=False)
        st.pyplot(fig)

    # ---- MOST SUCCESSFUL ATHLETES ---- #
    sport_list = df['Sport'].dropna().unique().tolist()
    sport_list.sort()
    sport_list.insert(0, "Overall")

    selected_sport = st.selectbox("Select Sport", sport_list)

    st.table(helper.most_successful(df, selected_sport))

# ---------------- COUNTRY ANALYSIS ---------------- #
elif user_menu == "Country-wise Analysis":

    st.title("Country Analysis")

    country_list = df['region'].dropna().unique().tolist()
    country_list.sort()

    selected_country = st.selectbox("Select Country", country_list)

    # ---- MEDAL TREND ---- #
    country_df = helper.yearwise_medal_tally(df, selected_country)

    fig = px.line(country_df, x="Year", y="Medal")
    st.plotly_chart(fig)

    # ---- HEATMAP SAFE FIX (MAIN ERROR FIX) ---- #
    st.subheader("Sport-wise Performance")

    pt = helper.country_event_heatmap(df, selected_country)

    if pt is None or pt.empty or pt.shape[0] == 0 or pt.shape[1] == 0:
        st.warning("No medal data available for this country")
    else:
        pt = pt.fillna(0).astype(float)

        if pt.to_numpy().sum() == 0:
            st.warning("No medal records found for this country")
        else:
            fig, ax = plt.subplots(figsize=(12, 8))
            sns.heatmap(pt, ax=ax, annot=False)
            st.pyplot(fig)

    # ---- TOP ATHLETES ---- #
    st.table(helper.most_successful_countrywise(df, selected_country))

# ---------------- ATHLETE ANALYSIS ---------------- #
elif user_menu == "Athlete wise Analysis":

    st.title("Athlete Analysis")

    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    # ---- AGE DISTRIBUTION ---- #
    st.subheader("Age Distribution")

    fig, ax = plt.subplots()
    sns.histplot(athlete_df['Age'].dropna(), kde=True, ax=ax)
    st.pyplot(fig)

    # ---- HEIGHT VS WEIGHT ---- #
    st.subheader("Height vs Weight")

    sport_list = df['Sport'].dropna().unique().tolist()
    sport_list.sort()
    sport_list.insert(0, "Overall")

    selected_sport = st.selectbox("Select Sport", sport_list)

    temp_df = helper.weight_v_height(df, selected_sport)

    fig, ax = plt.subplots()
    sns.scatterplot(
        x=temp_df['Weight'],
        y=temp_df['Height'],
        hue=temp_df['Medal'],
        style=temp_df['Sex'],
        ax=ax
    )

    st.pyplot(fig)

    # ---- MEN VS WOMEN ---- #
    st.subheader("Men vs Women Participation")

    final = helper.men_vs_women(df)

    fig = px.line(final, x="Year", y=["Male", "Female"])
    st.plotly_chart(fig)
