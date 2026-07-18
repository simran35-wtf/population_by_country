import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="🌍 Population Analysis Dashboard",
    page_icon="🌍",
    layout="wide"
)

sns.set_style("whitegrid")

# -----------------------------
# Load Data
# -----------------------------
DATA_PATH = "population_by_country_2020.csv"

@st.cache_data
def load_data():

    df = pd.read_csv(DATA_PATH, encoding="latin1")

    # Rename corrupted column names
    df.rename(columns={
        "Land Area (KmÂ²)": "Land Area (Km²)",
        "Density (P/KmÂ²)": "Density (P/Km²)"
    }, inplace=True)

    # Percentage columns
    percentage_cols = [
        "Yearly Change",
        "Urban Pop %",
        "World Share"
    ]

    for col in percentage_cols:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace("%", "", regex=False),
            errors="coerce"
        )

    numeric_cols = [
        "Population (2020)",
        "Density (P/Km²)",
        "Land Area (Km²)",
        "Migrants (net)",
        "Fert. Rate",
        "Med. Age"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Fill Missing Values
    df["Med. Age"] = df["Med. Age"].fillna(df["Med. Age"].median())
    df["Migrants (net)"] = df["Migrants (net)"].fillna(df["Migrants (net)"].median())
    df["Fert. Rate"] = df["Fert. Rate"].fillna(df["Fert. Rate"].median())

    # Density Category
    df["Population Density Category"] = pd.cut(
        df["Density (P/Km²)"],
        bins=[0,100,500,1000,float("inf")],
        labels=["Low","Medium","High","Very High"]
    )

    # Urban Category
    df["Urban Category"] = np.where(
        df["Urban Pop %"]>50,
        "Above 50%",
        "Below 50%"
    )

    return df

df = load_data()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("🌍 Population Dashboard")

country = st.sidebar.multiselect(
    "Select Country",
    options=sorted(df["Country (or dependency)"].unique()),
    default=sorted(df["Country (or dependency)"].unique())
)

density = st.sidebar.multiselect(
    "Density Category",
    options=df["Population Density Category"].dropna().unique(),
    default=df["Population Density Category"].dropna().unique()
)

filtered = df[
    (df["Country (or dependency)"].isin(country)) &
    (df["Population Density Category"].isin(density))
]

# -----------------------------
# Title
# -----------------------------
st.title("🌍 Population Analysis Dashboard")

st.markdown(
"""
Interactive dashboard for exploring global population,
density, fertility rate and migration statistics.
"""
)

# -----------------------------
# KPI Cards
# -----------------------------
col1,col2,col3,col4 = st.columns(4)

col1.metric(
    "Countries",
    filtered["Country (or dependency)"].nunique()
)

col2.metric(
    "Total Population",
    f"{filtered['Population (2020)'].sum():,.0f}"
)

col3.metric(
    "Average Density",
    f"{filtered['Density (P/Km²)'].mean():.2f}"
)

col4.metric(
    "Average Fertility",
    f"{filtered['Fert. Rate'].mean():.2f}"
)

st.markdown("---")

# -----------------------------
# Dataset Overview
# -----------------------------
with st.expander("📄 Dataset Overview"):

    st.write(filtered.head())

    st.write("Shape :", filtered.shape)

    st.write("Missing Values")

    st.dataframe(filtered.isnull().sum())



    # ==========================================================
# VISUALIZATIONS
# ==========================================================

row1_col1, row1_col2 = st.columns(2)

# ----------------------------------------------------------
# Population Distribution
# ----------------------------------------------------------
with row1_col1:

    st.subheader("📈 Population Distribution")

    fig, ax = plt.subplots(figsize=(6,4))

    sns.histplot(
        data=filtered,
        x="Population (2020)",
        log_scale=True,
        kde=True,
        color="royalblue",
        ax=ax
    )

    st.pyplot(fig)

# ----------------------------------------------------------
# Fertility vs Median Age
# ----------------------------------------------------------
with row1_col2:

    st.subheader("🌱 Fertility Rate vs Median Age")

    fig, ax = plt.subplots(figsize=(6,4))

    sns.scatterplot(
        data=filtered,
        x="Fert. Rate",
        y="Med. Age",
        hue="Urban Category",
        ax=ax
    )

    st.pyplot(fig)

st.markdown("---")

# ==========================================================
# Row 2
# ==========================================================

row2_col1, row2_col2 = st.columns(2)

# ----------------------------------------------------------
# Correlation Heatmap
# ----------------------------------------------------------
with row2_col1:

    st.subheader("🔥 Correlation Heatmap")

    corr = filtered.corr(numeric_only=True)

    fig, ax = plt.subplots(figsize=(7,5))

    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        ax=ax
    )

    st.pyplot(fig)

# ----------------------------------------------------------
# Density Box Plot
# ----------------------------------------------------------
with row2_col2:

    st.subheader("📦 Density Category")

    fig, ax = plt.subplots(figsize=(6,4))

    sns.boxplot(
        data=filtered,
        x="Population Density Category",
        y="Density (P/Km²)",
        ax=ax
    )

    ax.set_yscale("log")

    st.pyplot(fig)

st.markdown("---")

# ==========================================================
# Row 3
# ==========================================================

row3_col1, row3_col2 = st.columns(2)

# ----------------------------------------------------------
# Top 15 Countries
# ----------------------------------------------------------
with row3_col1:

    st.subheader("🌍 Top 15 Most Populous Countries")

    top15 = filtered.nlargest(15, "Population (2020)")

    fig, ax = plt.subplots(figsize=(8,6))

    ax.barh(
        top15["Country (or dependency)"],
        top15["Population (2020)"],
        color="steelblue"
    )

    ax.invert_yaxis()

    st.pyplot(fig)

# ----------------------------------------------------------
# Pie Chart
# ----------------------------------------------------------
with row3_col2:

    st.subheader("🥧 World Share")

    top10 = filtered.nlargest(10, "Population (2020)")

    others = filtered["World Share"].sum() - top10["World Share"].sum()

    labels = list(top10["Country (or dependency)"])
    labels.append("Others")

    sizes = list(top10["World Share"])
    sizes.append(others)

    fig, ax = plt.subplots(figsize=(6,6))

    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90
    )

    st.pyplot(fig)

st.markdown("---")

# ==========================================================
# Row 4
# ==========================================================

row4_col1, row4_col2 = st.columns(2)

# ----------------------------------------------------------
# Population vs Yearly Change
# ----------------------------------------------------------
with row4_col1:

    st.subheader("📊 Population vs Yearly Change")

    top10 = filtered.nlargest(10, "Population (2020)")

    fig, ax1 = plt.subplots(figsize=(8,5))

    ax1.bar(
        top10["Country (or dependency)"],
        top10["Population (2020)"],
        color="skyblue"
    )

    ax2 = ax1.twinx()

    ax2.plot(
        top10["Country (or dependency)"],
        top10["Yearly Change"],
        color="red",
        marker="o"
    )

    plt.xticks(rotation=45)

    st.pyplot(fig)

# ----------------------------------------------------------
# Bubble Chart
# ----------------------------------------------------------
with row4_col2:

    st.subheader("🌎 Land Area vs Population")

    fig, ax = plt.subplots(figsize=(7,5))

    ax.scatter(
        filtered["Land Area (Km²)"],
        filtered["Population (2020)"],
        s=filtered["Density (P/Km²)"]/10,
        alpha=0.6,
        color="green"
    )

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlabel("Land Area (Km²)")
    ax.set_ylabel("Population")

    st.pyplot(fig)

st.markdown("---")



# ==========================================================
# TOP & BOTTOM COUNTRIES
# ==========================================================

st.subheader("🌍 Top 10 & Bottom 10 Countries by Population")

col1, col2 = st.columns(2)

with col1:

    st.markdown("### 🔝 Top 10 Countries")

    top10 = filtered.nlargest(
        10,
        "Population (2020)"
    )[
        [
            "Country (or dependency)",
            "Population (2020)"
        ]
    ]

    st.dataframe(top10, use_container_width=True)

with col2:

    st.markdown("### 🔻 Bottom 10 Countries")

    bottom10 = filtered.nsmallest(
        10,
        "Population (2020)"
    )[
        [
            "Country (or dependency)",
            "Population (2020)"
        ]
    ]

    st.dataframe(bottom10, use_container_width=True)

st.markdown("---")

# ==========================================================
# KEY INSIGHTS
# ==========================================================

st.subheader("💡 Key Insights")

highest_population = filtered.loc[
    filtered["Population (2020)"].idxmax()
]

highest_density = filtered.loc[
    filtered["Density (P/Km²)"].idxmax()
]

highest_fertility = filtered.loc[
    filtered["Fert. Rate"].idxmax()
]

highest_age = filtered.loc[
    filtered["Med. Age"].idxmax()
]

negative = filtered[
    filtered["Migrants (net)"] < 0
].shape[0]

positive = filtered[
    filtered["Migrants (net)"] > 0
].shape[0]

c1, c2 = st.columns(2)

with c1:

    st.success(
        f"🌍 Highest Population : "
        f"{highest_population['Country (or dependency)']}"
    )

    st.success(
        f"📍 Highest Density : "
        f"{highest_density['Country (or dependency)']}"
    )

    st.success(
        f"👶 Highest Fertility : "
        f"{highest_fertility['Country (or dependency)']}"
    )

with c2:

    st.info(
        f"👴 Highest Median Age : "
        f"{highest_age['Country (or dependency)']}"
    )

    st.info(
        f"📈 Positive Migration Countries : {positive}"
    )

    st.info(
        f"📉 Negative Migration Countries : {negative}"
    )

st.markdown("---")

# ==========================================================
# NUMERICAL SUMMARY
# ==========================================================

st.subheader("📊 Statistical Summary")

st.dataframe(
    filtered.describe(),
    use_container_width=True
)

st.markdown("---")

# ==========================================================
# CORRELATION VALUE
# ==========================================================

corr = np.corrcoef(
    filtered["Fert. Rate"],
    filtered["Med. Age"]
)[0,1]

st.metric(
    "Correlation (Fertility vs Median Age)",
    f"{corr:.2f}"
)

st.markdown("---")

# ==========================================================
# RAW DATA
# ==========================================================

with st.expander("📄 View Raw Dataset"):

    st.dataframe(
        filtered,
        use_container_width=True
    )

st.markdown("---")

# ==========================================================
# FOOTER
# ==========================================================

st.markdown(
"""
---
### 📌 Project Summary

**Population Analysis Dashboard**

**Technology Used**

- Python
- Streamlit
- NumPy
- Pandas
- Matplotlib
- Seaborn

This dashboard provides interactive analysis of world population,
fertility, migration, urbanization and population density statistics.
"""
)