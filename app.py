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
    # Detect common columns across all files
    first_df = pd.read_excel(uploaded_files[0])
    common_columns = [col for col in first_df.columns if all(col in pd.read_excel(f).columns for f in uploaded_files[1:])]
    
    # Relationship management section
    st.sidebar.subheader("Manage Relationships")
    if not common_columns:
        st.sidebar.warning("No common columns found across all files. Data will be stacked.")
        merge_columns = []
        merge_type = "outer"
    else:
        merge_columns = st.sidebar.multiselect("Select columns to merge on", common_columns, default=[common_columns[0]] if common_columns else [])
        merge_type = st.sidebar.selectbox("Merge type", ["outer", "inner", "left"], index=0)

    # Combine all uploaded files into one DataFrame
    if not merge_columns:
        all_dfs = [pd.read_excel(file) for file in uploaded_files]
        df = pd.concat(all_dfs, ignore_index=True)
    else:
        base_df = pd.read_excel(uploaded_files[0])
        df = base_df.copy()
        for file in uploaded_files[1:]:
            df = df.merge(pd.read_excel(file), on=merge_columns, how=merge_type, suffixes=("", "_dup"))
        
        # Remove duplicate columns (e.g., if suffixes were added)
        df = df.loc[:, ~df.columns.str.endswith("_dup")]

    st.write("Preview of your combined data:")
    st.dataframe(df)

    # Let user specify how many charts to create
    st.sidebar.subheader("Chart Configurations")
    num_charts = st.sidebar.slider("Number of charts to display", min_value=1, max_value=5, value=1)

    # Chart customization options
    st.sidebar.subheader("Chart Customization")
    chart_color = st.sidebar.color_picker("Select chart color", "#1f77b4")  # Default blue
    chart_width = st.sidebar.slider("Chart width (%)", min_value=50, max_value=100, value=100)

    # Define Relationships and Visualization
    st.subheader("Define Relationships")
    cols = st.columns(num_charts)

    # Loop through the number of charts
    for i in range(num_charts):
        with cols[i]:
            st.subheader(f"Visualization {i + 1}")
            col1 = st.sidebar.selectbox(f"Select first column (Chart {i + 1})", df.columns, key=f"col1_{i}")
            col2 = st.sidebar.selectbox(f"Select second column (Chart {i + 1})", df.columns, key=f"col2_{i}")
            agg_type = st.sidebar.selectbox(f"Aggregation type (Chart {i + 1})", ["sum", "mean", "count"], key=f"agg_{i}")
            chart_type = st.sidebar.selectbox(f"Choose chart type (Chart {i + 1})", ["Bar", "Line", "Scatter", "Pie"], key=f"chart_{i}")

            # Group data based on selected columns and aggregation
            try:
                grouped_data = df.groupby(col1)[col2].agg(agg_type).reset_index()
            except Exception as e:
                st.error(f"Error processing Chart {i + 1}: {str(e)}. Please check column types or selections.")
                continue

            # Error handling: Check if the second column is numeric for Pie charts
            if chart_type == "Pie" and not pd.api.types.is_numeric_dtype(grouped_data[col2]):
                st.error(f"Error: '{col2}' must be numeric for a Pie chart. Please select a different column or chart type.")
                continue

            # Generate chart
            if chart_type == "Bar":
                fig = px.bar(grouped_data, x=col1, y=col2, title=f"{col1} vs {col2} ({agg_type})")
            elif chart_type == "Line":
                fig = px.line(grouped_data, x=col1, y=col2, title=f"{col1} vs {col2} ({agg_type})")
            elif chart_type == "Scatter":
                fig = px.scatter(grouped_data, x=col1, y=col2, title=f"{col1} vs {col2} ({agg_type})")
            elif chart_type == "Pie":
                fig = px.pie(grouped_data, names=col1, values=col2, title=f"{col1} vs {col2} ({agg_type})")

            # Apply custom color and width
            fig.update_traces(marker=dict(color=chart_color))
            fig.update_layout(width=chart_width * 5)  # Convert percentage to pixels (approx. 500px max)

            st.plotly_chart(fig, use_container_width=True)

else:
    st.write("Please upload one or more Excel files to get started.")
