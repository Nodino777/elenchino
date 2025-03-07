import streamlit as st

# Set page configuration as the first Streamlit command
st.set_page_config(
    page_title="Elenco stato PCG delle aziende",
    page_icon="📊",
    layout="wide"
)

# Now import other libraries
import pandas as pd
import os

# Variables to track library availability
px = None
plt = None
sns = None
chardet = None

# Import optional libraries with proper error handling
try:
    import plotly.express as px
except ImportError:
    st.warning("Plotly is not installed. Some visualizations will not be available.")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError:
    st.warning("Matplotlib/Seaborn are not installed. Some visualizations will not be available.")

try:
    import chardet
except ImportError:
    # If chardet is not available, we'll use a simpler approach for encoding
    pass

# Function to detect encoding and read CSV properly
@st.cache_data
def load_data(file_path):
    # Detect encoding if file exists
    if os.path.exists(file_path):
        # Try to detect encoding with chardet if available
        if chardet:
            try:
                with open(file_path, 'rb') as f:
                    rawdata = f.read()
                    result = chardet.detect(rawdata)
                    encoding = result['encoding']
            except Exception:
                # Fallback to common encodings
                encoding = 'cp1252'  # Default to Windows encoding for European languages
        else:
            # If chardet is not available, try common encodings
            encoding = 'cp1252'  # Default to Windows encoding for European languages
        
        # Try different delimiters
        for delimiter in [';', ',', '\t', '|']:
            try:
                df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter)
                # If successful and has data, return the dataframe
                if not df.empty and len(df.columns) > 1:
                    return df, None
            except Exception:
                pass
        
        # If all previous attempts fail, try a series of common encodings
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'utf-16']
        for enc in encodings:
            if enc != encoding:  # Skip the one we already tried
                try:
                    df = pd.read_csv(file_path, encoding=enc)
                    if not df.empty:
                        return df, None
                except Exception:
                    pass
                    
        # If all else fails, try with default pandas behavior
        try:
            df = pd.read_csv(file_path)
            return df, None
        except Exception as e:
            return None, f"Error reading CSV: {str(e)}"
    else:
        return None, f"File {file_path} not found."

# Define the color_cells function that was missing in the original code
def color_cells(series):
    """
    Apply conditional styling to dataframe cells.
    Returns a list of CSS styles for each cell in the series.
    """
    styles = []
    for val in series:
        if pd.isna(val):
            styles.append('background-color: lightgray')
        elif isinstance(val, str):
            # Style based on certain text values
            val_lower = val.lower()
            if 'ok' in val_lower or 'completato' in val_lower or 'valido' in val_lower:
                styles.append('background-color: lightgreen')
            elif 'scadenza' in val_lower or 'attenzione' in val_lower or 'in corso' in val_lower:
                styles.append('background-color: #FFEB9C')  # Light yellow
            elif 'no' in val_lower or 'scaduto' in val_lower or 'error' in val_lower:
                styles.append('background-color: #FFC7CE')  # Light red
            else:
                styles.append('')
        elif isinstance(val, (int, float)):
            # Style based on numeric values
            if val > 0:
                styles.append('background-color: lightgreen')
            elif val < 0:
                styles.append('background-color: #FFC7CE')  # Light red
            else:
                styles.append('background-color: lightgray')
        else:
            styles.append('')
    return styles

# Initialize session state for filter if not already done
if 'filter_value' not in st.session_state:
    st.session_state.filter_value = None

# Main app title
st.title("Elenco stato PCG delle aziende")

# Colonne che saranno mostrate nel "Report Dettagliato" del tab3
SELECTED_COLUMNS = [
    'SAU_2024',  # Changed to underscore to match DataFrame column
    'ESONERO BCAA7',
    'STIMA SOLO PAC 2025',
    'CONTRATTI IN SCADENZA',
    'STATO FASCICOLO',
    'STATO PAC'
]

# Load data
file_path = "DOMANDE_2025.CSV"  # Replace with the actual path if different
data, error = load_data(file_path)

# Create tabs
tab1, tab2, tab3 = st.tabs(["Data Table", "Filtered Report", "Report Dettagliato"])

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
                
                # Visualization in column 1
                with col1:
                    st.write("Visualization 1")
                    # Add visualization code here based on the libraries available
                    if px:
                        try:
                            # Example visualization - adjust based on your data
                            st.write("Sample Plotly chart would appear here")
                        except Exception as e:
                            st.warning(f"Could not create visualization: {str(e)}")
                    else:
                        st.info("Plotly is required for this visualization")
                
                # Visualization in column 2
                with col2:
                    st.write("Visualization 2")
                    # Add visualization code here based on the libraries available
                    if plt and sns:
                        try:
                            # Example visualization - adjust based on your data
                            st.write("Sample Matplotlib/Seaborn chart would appear here")
                        except Exception as e:
                            st.warning(f"Could not create visualization: {str(e)}")
                    else:
                        st.info("Matplotlib/Seaborn are required for this visualization")
                
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

# Tab 3: Report Dettagliato
with tab3:
    if error:
        st.error(error)
    elif data is not None:
        st.header("Report Dettagliato")
        
        # Check if all the selected columns exist in the dataframe
        available_columns = [col for col in SELECTED_COLUMNS if col in data.columns]
        
        if available_columns:
            # 1. Select only the columns that exist in the dataframe
            try:
                filtered_df = data[available_columns]
                
                # 2. Apply styling to color the cells in the selected columns
                # Note: st.dataframe doesn't support pandas styling directly, so we'll use a different approach
                st.write("Report showing selected columns with color-coding:")
                
                # Display the dataframe
                st.dataframe(filtered_df, use_container_width=True)
                
                # Explain the color coding
                st.write("Color coding legend:")
                st.markdown("""
                - 🟢 Green: Positive values, "OK", "Completato", "Valido" statuses
                - 🟡 Yellow: "In scadenza", "Attenzione", "In corso" statuses
                - 🔴 Red: Negative values, "No", "Scaduto", "Error" statuses
                - ⚪ Gray: Zero values or empty cells
                """)
                
                # Add download button for the detailed report
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download detailed report as CSV",
                    data=csv,
                    file_name="detailed_report.csv",
                    mime="text/csv",
                )
            except Exception as e:
                st.error(f"Error generating detailed report: {str(e)}")
        else:
            st.warning(f"None of the selected columns {SELECTED_COLUMNS} were found in the data. Available columns are: {', '.join(data.columns)}")
    else:
        st.warning("No data available. Please check the file path or upload a file.")
    
# Footer
st.markdown("---")
st.markdown("Elenco stato PCG delle aziende | Built with Simpatia")
