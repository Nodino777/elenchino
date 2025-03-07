import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os
import chardet

# Set page configuration
st.set_page_config(
    page_title="CSV Data Viewer & Analyzer",
    page_icon="📊",
    layout="wide"
)

# Function to detect encoding and read CSV properly
@st.cache_data
def load_data(file_path):
    # Detect encoding if file exists
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            rawdata = f.read()
            result = chardet.detect(rawdata)
            encoding = result['encoding']
        
        # Try different delimiters
        for delimiter in [';', ',', '\t', '|']:
            try:
                df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
                # If successful and has data, return the dataframe
                if not df.empty and len(df.columns) > 1:
                    return df, None
            except Exception as e:
                pass
                
        # If all delimiters fail, try with default
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            return df, None
        except Exception as e:
            return None, f"Error reading CSV: {str(e)}"
    else:
        return None, f"File {file_path} not found."

# Initialize session state for filter if not already done
if 'filter_value' not in st.session_state:
    st.session_state.filter_value = None

# Main app title
st.title("CSV Data Viewer & Analyzer")

# Load data
file_path = "DOMANDE_2025.CSV"  # Replace with the actual path if different
data, error = load_data(file_path)

# Create tabs
tab1, tab2 = st.tabs(["Data Table", "Filtered Report"])

# Tab 1: Data Table
with tab1:
    if error:
        st.error(error)
    elif data is not None:
        st.subheader("CSV Data Table")
        
        # Display basic info
        st.write(f"Total rows: {len(data)}")
        st.write(f"Total columns: {len(data.columns)}")
        
        # Display all data with pagination
        st.dataframe(data, use_container_width=True)
        
        # Display column information
        st.subheader("Column Information")
        for i, col in enumerate(data.columns):
            st.write(f"Column {i+1}: {col} - Type: {data[col].dtype}")
    else:
        st.warning("No data available. Please check the file path.")

# Tab 2: Filtered Report
with tab2:
    if error:
        st.error(error)
    elif data is not None:
        st.subheader("Filtered Data Report")
        
        # Check if we have at least 3 columns
        if len(data.columns) >= 3:
            # Get the name of the third column
            third_column = data.columns[2]
            
            # Get unique values from the third column
            unique_values = data[third_column].unique()
            
            # Create filter in sidebar
            st.sidebar.header("Filter Options")
            selected_value = st.sidebar.selectbox(
                f"Select a value from {third_column}",
                options=unique_values,
                key="filter_selectbox"
            )
            
            # Filter the dataframe based on selection
            filtered_data = data[data[third_column] == selected_value]
            
            # Show filtered data
            st.write(f"Showing data for {third_column} = {selected_value}")
            st.write(f"Number of records: {len(filtered_data)}")
            
            # Display the filtered table
            st.dataframe(filtered_data, use_container_width=True)
            
            # Create visualizations
            st.subheader("Visualizations")
            
            # Only proceed if we have filtered data
            if not filtered_data.empty:
                # Create columns for charts
                col1, col2 = st.columns(2)
                
                with col1:
                    try:
                        # Try to create a bar chart of counts by another column
                        # Find a categorical column to plot
                        categorical_cols = filtered_data.select_dtypes(include=['object', 'category']).columns
                        numeric_cols = filtered_data.select_dtypes(include=['number']).columns
                        
                        if len(categorical_cols) > 0 and categorical_cols[0] != third_column:
                            plot_col = categorical_cols[0]
                            fig = px.histogram(filtered_data, x=plot_col, title=f"Count by {plot_col}")
                            st.plotly_chart(fig, use_container_width=True)
                        elif len(categorical_cols) > 1:
                            plot_col = categorical_cols[1]
                            fig = px.histogram(filtered_data, x=plot_col, title=f"Count by {plot_col}")
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error creating bar chart: {str(e)}")
                
                with col2:
                    try:
                        # If we have numeric columns, create a boxplot
                        if len(numeric_cols) > 0:
                            fig = px.box(filtered_data, y=numeric_cols[0], title=f"Distribution of {numeric_cols[0]}")
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error creating box plot: {str(e)}")
                
                # Create a third visualization - scatter plot if possible
                try:
                    if len(numeric_cols) >= 2:
                        fig = px.scatter(filtered_data, x=numeric_cols[0], y=numeric_cols[1], 
                                         title=f"Scatter plot: {numeric_cols[0]} vs {numeric_cols[1]}")
                        st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error creating scatter plot: {str(e)}")
                
                # Summary statistics
                st.subheader("Summary Statistics")
                try:
                    st.write(filtered_data.describe())
                except Exception as e:
                    st.error(f"Error generating summary statistics: {str(e)}")
            else:
                st.warning("No data matches the selected filter.")
        else:
            st.warning("The CSV file has fewer than 3 columns. Please select a different file.")
    else:
        st.warning("No data available. Please check the file path.")

# Footer
st.markdown("---")
st.markdown("CSV Data Viewer & Analyzer | Built with Streamlit")
