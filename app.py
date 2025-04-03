import streamlit as st
import pandas as pd
import plotly.express as px

# Title of the app
st.title("Excel Dashboard Tool")

# Sidebar for inputs
st.sidebar.header("Options")

# File uploader (multiple files allowed)
uploaded_files = st.sidebar.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    # Combine all uploaded files into one DataFrame
    all_dfs = [pd.read_excel(file) for file in uploaded_files]
    df = pd.concat(all_dfs, ignore_index=True)
    st.write("Preview of your combined data:")
    st.dataframe(df)

    # Let user select columns and aggregation for relationships
    st.subheader("Define Relationships")
    col1 = st.sidebar.selectbox("Select first column", df.columns)
    col2 = st.sidebar.selectbox("Select second column", df.columns)
    agg_type = st.sidebar.selectbox("Aggregation type", ["sum", "mean", "count"])
    
    # Group data based on selected columns and aggregation
    grouped_data = df.groupby(col1)[col2].agg(agg_type).reset_index()

    # Chart type selection
    chart_type = st.sidebar.selectbox("Choose chart type", ["Bar", "Line", "Scatter", "Pie"])

    # Generate chart
    st.subheader("Visualization")
    if chart_type == "Bar":
        fig = px.bar(grouped_data, x=col1, y=col2, title=f"{col1} vs {col2} ({agg_type})")
    elif chart_type == "Line":
        fig = px.line(grouped_data, x=col1, y=col2, title=f"{col1} vs {col2} ({agg_type})")
    elif chart_type == "Scatter":
        fig = px.scatter(grouped_data, x=col1, y=col2, title=f"{col1} vs {col2} ({agg_type})")
    elif chart_type == "Pie":
        fig = px.pie(grouped_data, names=col1, values=col2, title=f"{col1} vs {col2} ({agg_type})")

    st.plotly_chart(fig)

else:
    st.write("Please upload one or more Excel files to get started.")