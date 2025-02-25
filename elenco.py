import streamlit as st
import pandas as pd
import io
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

st.title("Editor di file CSV")

# Caricamento del file
uploaded_file = st.file_uploader("Carica un file CSV", type="csv")

if uploaded_file is not None:
    # Opzioni per la lettura del file
    st.subheader("Opzioni di lettura")
    
    col1, col2 = st.columns(2)
    with col1:
        delimiter = st.text_input("Delimitatore", ",")
    with col2:
        encoding = st.selectbox("Encoding", ["utf-8", "latin1", "iso-8859-1", "cp1252"])
    
    header_option = st.checkbox("Il file ha intestazioni", value=True)
    
    try:
        # Leggi i dati
        if header_option:
            df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding=encoding)
        else:
            df = pd.read_csv(uploaded_file, delimiter=delimiter, encoding=encoding, header=None)
        
        # Salva il dataframe originale nella sessione
        if 'original_df' not in st.session_state:
            st.session_state.original_df = df.copy()
        
        # Mostra informazioni sul dataset
        st.subheader("Informazioni sul dataset")
        st.write(f"Numero di righe: {df.shape[0]}")
        st.write(f"Numero di colonne: {df.shape[1]}")
        
        # Mostra i dati con AgGrid per editing
        st.subheader("Modifica dei dati")
        st.write("Puoi modificare direttamente i dati nella tabella sottostante. Clicca su una cella per modificarla.")
        
        # Configurazione per AgGrid
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
        gb.configure_default_column(editable=True, groupable=True, value=True, enableRowGroup=True, enablePivot=True)
        gridOptions = gb.build()
        
        # Visualizza la grid con AgGrid
        grid_response = AgGrid(
            df,
            gridOptions=gridOptions,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            fit_columns_on_grid_load=True,
            data_return_mode=DataReturnMode.AS_INPUT,
            height=400
        )
        
        # Ottieni il dataframe aggiornato
        updated_df = grid_response['data']
        
        # Aggiungi pulsanti per ripristinare e scaricare
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Ripristina dati originali"):
                updated_df = st.session_state.original_df.copy()
                st.experimental_rerun()
        
        with col2:
            # Opzione per scaricare il dataframe modificato
            if st.button("Scarica dati modificati"):
                csv = updated_df.to_csv(index=False)
                b64 = io.StringIO()
                b64.write(csv)
                b64.seek(0)
                st.download_button(
                    label="Scarica CSV modificato",
                    data=b64,
                    file_name="dati_modificati.csv",
                    mime="text/csv"
                )
        
        with col3:
            # Aggiungi riga vuota
            if st.button("Aggiungi riga vuota"):
                empty_row = pd.DataFrame({col: [""] for col in updated_df.columns}, index=[0])
                updated_df = pd.concat([updated_df, empty_row], ignore_index=True)
                st.experimental_rerun()
        
        # Opzioni di ricerca e filtraggio
        st.subheader("Ricerca e filtraggio")
        search_term = st.text_input("Termine di ricerca")
        
        if search_term:
            # Cerca in tutte le colonne
            filtered_df = updated_df[updated_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]
            st.write(f"Risultati trovati: {filtered_df.shape[0]}")
            
            # Visualizza i risultati filtrati
            gb_filtered = GridOptionsBuilder.from_dataframe(filtered_df)
            gb_filtered.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
            gb_filtered.configure_default_column(editable=True)
            gridOptions_filtered = gb_filtered.build()
            
            filtered_grid = AgGrid(
                filtered_df,
                gridOptions=gridOptions_filtered,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                fit_columns_on_grid_load=True,
                key="filtered_grid"
            )
        
        # Statistiche di base
        if st.checkbox("Mostra statistiche"):
            st.subheader("Statistiche descrittive")
            st.write(updated_df.describe())

    except Exception as e:
        st.error(f"Si è verificato un errore nella lettura o modifica del file: {e}")
else:
    st.info("Carica un file CSV per visualizzare e modificare i dati")
    
    # Esempio
    st.subheader("Esempio di utilizzo:")
    st.markdown("""
    1. Clicca sul pulsante 'Carica un file CSV'
    2. Seleziona il tuo file CSV dal computer
    3. Configura le opzioni di lettura se necessario
    4. Modifica i dati direttamente nella tabella
    5. Scarica il file modificato quando hai finito
    """)
    
    st.warning("Nota: Per utilizzare questa applicazione è necessario installare la libreria streamlit-aggrid con il comando: `pip install streamlit-aggrid`")
