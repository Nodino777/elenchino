import streamlit as st
import pandas as pd
import io
import numpy as np

st.title("Editor di file CSV")

# Funzioni di supporto
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

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
        
        # Salva il dataframe originale nella sessione se non esiste già
        if 'original_df' not in st.session_state:
            st.session_state.original_df = df.copy()
        
        # Salva il dataframe di lavoro nella sessione se non esiste già
        if 'working_df' not in st.session_state:
            st.session_state.working_df = df.copy()
        
        # Mostra informazioni sul dataset
        st.subheader("Informazioni sul dataset")
        st.write(f"Numero di righe: {st.session_state.working_df.shape[0]}")
        st.write(f"Numero di colonne: {st.session_state.working_df.shape[1]}")
        
        # Filtraggio colonne
        st.subheader("Filtraggio colonne")
        all_columns = st.session_state.working_df.columns.tolist()
        selected_columns = st.multiselect(
            "Seleziona le colonne da visualizzare/modificare",
            all_columns,
            default=all_columns
        )
        
        # Se non è selezionata nessuna colonna, usa tutte le colonne
        if not selected_columns:
            st.warning("Nessuna colonna selezionata. Verranno mostrate tutte le colonne.")
            selected_columns = all_columns
            
        # Filtra il dataframe per mostrare solo le colonne selezionate
        display_df = st.session_state.working_df[selected_columns]
        
        # Opzioni per filtrare anche le righe
        st.subheader("Filtraggio righe")
        
        # Selezione della colonna e del valore per il filtro
        if selected_columns:
            filter_col = st.selectbox("Seleziona colonna per filtrare", selected_columns)
            
            # Ottieni valori unici dalla colonna selezionata
            unique_values = st.session_state.working_df[filter_col].astype(str).unique().tolist()
            filter_value = st.selectbox("Filtra per valore", ["Tutti"] + unique_values)
            
            # Applica il filtro
            if filter_value != "Tutti":
                filtered_df = display_df[st.session_state.working_df[filter_col].astype(str) == filter_value]
            else:
                filtered_df = display_df
            
            st.write(f"Righe visibili dopo il filtro: {len(filtered_df)}")
        else:
            filtered_df = display_df
        
        # Tabs per modifica e visualizzazione
        edit_tab, view_tab = st.tabs(["Modifica", "Visualizza"])
        
        with edit_tab:
            # Seleziona riga da modificare
            if not filtered_df.empty:
                # Ottieni gli indici originali delle righe filtrate
                filtered_indices = filtered_df.index.tolist()
                
                # Selettore di riga con indici visibili
                if filtered_indices:
                    row_idx = st.selectbox(
                        "Seleziona riga da modificare",
                        range(len(filtered_indices)),
                        format_func=lambda x: f"Riga {filtered_indices[x]}"
                    )
                    
                    # Converti in indice effettivo
                    row_to_edit = filtered_indices[row_idx]
                    
                    st.write(f"Modifica i valori della riga {row_to_edit}:")
                    
                    # Crea un form per l'editing
                    with st.form(key="edit_form"):
                        edited_row = {}
                        for col in selected_columns:
                            # Ottieni il valore corrente
                            current_value = st.session_state.working_df.at[row_to_edit, col]
                            
                            # Gestisci diversi tipi di dati
                            if pd.isna(current_value):
                                current_value = ""
                            
                            # Crea un input per ogni colonna
                            edited_row[col] = st.text_input(f"{col}", value=str(current_value))
                        
                        # Bottone per salvare le modifiche
                        submit_button = st.form_submit_button(label="Salva modifiche")
                        
                    if submit_button:
                        # Aggiorna il dataframe con i valori modificati
                        for col, value in edited_row.items():
                            st.session_state.working_df.at[row_to_edit, col] = value
                        
                        st.success(f"Riga {row_to_edit} aggiornata con successo!")
                
            # Opzione per aggiungere una nuova riga
            st.subheader("Aggiungi nuova riga")
            with st.form(key="add_row_form"):
                new_row = {}
                for col in selected_columns:
                    new_row[col] = st.text_input(f"Nuovo valore per {col}", value="")
                
                # Per le colonne non selezionate, aggiungi valori vuoti
                for col in all_columns:
                    if col not in selected_columns:
                        new_row[col] = ""
                
                add_button = st.form_submit_button(label="Aggiungi riga")
            
            if add_button:
                # Aggiungi la nuova riga al dataframe
                st.session_state.working_df = pd.concat([st.session_state.working_df, 
                                                       pd.DataFrame([new_row])], 
                                                       ignore_index=True)
                st.success("Nuova riga aggiunta con successo!")
                st.experimental_rerun()
        
        with view_tab:
            # Mostra l'anteprima del dataframe filtrato
            st.dataframe(filtered_df)
            
            # Opzione per visualizzare statistiche sulle colonne filtrate
            if st.checkbox("Mostra statistiche delle colonne filtrate"):
                st.write(filtered_df.describe())
        
        # Azioni sul dataset
        st.subheader("Azioni sul dataset")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Ripristina dati originali"):
                st.session_state.working_df = st.session_state.original_df.copy()
                st.success("Dati ripristinati all'originale!")
                st.experimental_rerun()
        
        with col2:
            # Opzione per scaricare il dataframe completo modificato
            csv_full = convert_df_to_csv(st.session_state.working_df)
            st.download_button(
                label="Scarica dataset completo",
                data=csv_full,
                file_name="dataset_completo.csv",
                mime="text/csv"
            )
        
        with col3:
            # Opzione per scaricare solo le colonne filtrate
            csv_filtered = convert_df_to_csv(filtered_df)
            st.download_button(
                label="Scarica dati filtrati",
                data=csv_filtered,
                file_name="dati_filtrati.csv",
                mime="text/csv"
            )
        
        # Ricerca nel dataset
        st.subheader("Ricerca nel dataset")
        search_term = st.text_input("Cerca nel dataset")
        if search_term:
            # Cerca solo nelle colonne selezionate
            mask = np.column_stack([st.session_state.working_df[col].astype(str).str.contains(search_term, na=False, case=False) 
                                   for col in selected_columns])
            search_results = st.session_state.working_df.loc[mask.any(axis=1), selected_columns]
            
            st.write(f"Risultati trovati: {len(search_results)} righe")
            st.dataframe(search_results)
        
    except Exception as e:
        st.error(f"Si è verificato un errore: {e}")
else:
    st.info("Carica un file CSV per visualizzare e modificare i dati")
    
    # Esempio
    st.subheader("Esempio di utilizzo:")
    st.markdown("""
    1. Clicca sul pulsante 'Carica un file CSV'
    2. Seleziona il tuo file CSV dal computer
    3. Configura le opzioni di lettura se necessario
    4. Seleziona le colonne che desideri visualizzare/modificare
    5. Utilizza i filtri per restringere la visualizzazione
    6. Vai alla scheda 'Modifica' per modificare i dati riga per riga
    7. Aggiungi nuove righe se necessario
    8. Scarica il file modificato o filtrato quando hai finito
    """)
