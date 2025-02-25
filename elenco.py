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
        
        # Opzioni di modifica
        st.subheader("Modifica dei dati")
        
        edit_tab, view_tab = st.tabs(["Modifica", "Visualizza"])
        
        with edit_tab:
            # Seleziona riga da modificare
            if not st.session_state.working_df.empty:
                row_count = len(st.session_state.working_df)
                row_to_edit = st.number_input("Seleziona riga da modificare", 
                                            min_value=0, 
                                            max_value=row_count-1, 
                                            value=0,
                                            step=1)
                
                st.write("Modifica i valori della riga selezionata:")
                
                # Crea un form per l'editing
                with st.form(key="edit_form"):
                    edited_row = {}
                    for col in st.session_state.working_df.columns:
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
                for col in st.session_state.working_df.columns:
                    new_row[col] = st.text_input(f"Nuovo valore per {col}", value="")
                
                add_button = st.form_submit_button(label="Aggiungi riga")
            
            if add_button:
                # Aggiungi la nuova riga al dataframe
                st.session_state.working_df = pd.concat([st.session_state.working_df, 
                                                      pd.DataFrame([new_row])], 
                                                      ignore_index=True)
                st.success("Nuova riga aggiunta con successo!")
        
        with view_tab:
            # Mostra l'anteprima del dataframe
            st.dataframe(st.session_state.working_df)
        
        # Azioni sul dataset
        st.subheader("Azioni sul dataset")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Ripristina dati originali"):
                st.session_state.working_df = st.session_state.original_df.copy()
                st.success("Dati ripristinati all'originale!")
                st.experimental_rerun()
        
        with col2:
            # Opzione per scaricare il dataframe modificato
            csv = convert_df_to_csv(st.session_state.working_df)
            st.download_button(
                label="Scarica dati modificati",
                data=csv,
                file_name="dati_modificati.csv",
                mime="text/csv"
            )
        
        # Opzioni aggiuntive
        st.subheader("Opzioni aggiuntive")
        
        # Ricerca nel dataset
        search_term = st.text_input("Cerca nel dataset")
        if search_term:
            # Converti tutto in stringhe per la ricerca
            mask = np.column_stack([st.session_state.working_df[col].astype(str).str.contains(search_term, na=False, case=False) 
                                   for col in st.session_state.working_df.columns])
            filtered_df = st.session_state.working_df.loc[mask.any(axis=1)]
            
            st.write(f"Risultati trovati: {len(filtered_df)} righe")
            st.dataframe(filtered_df)
        
        # Statistiche di base
        if st.checkbox("Mostra statistiche"):
            st.subheader("Statistiche descrittive")
            st.write(st.session_state.working_df.describe())
            
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
    4. Vai alla scheda 'Modifica' per modificare i dati riga per riga
    5. Aggiungi nuove righe se necessario
    6. Scarica il file modificato quando hai finito
    """)
