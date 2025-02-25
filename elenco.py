import streamlit as st
import pandas as pd
import io

st.title("Visualizzatore di file CSV")

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
        
        # Mostra informazioni sul dataset
        st.subheader("Informazioni sul dataset")
        st.write(f"Numero di righe: {df.shape[0]}")
        st.write(f"Numero di colonne: {df.shape[1]}")
        
        # Mostra i dati
        st.subheader("Anteprima dei dati")
        st.dataframe(df.head(10))
        
        # Opzioni di visualizzazione avanzate
        st.subheader("Visualizzazione avanzata")
        
        # Selezione colonne
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect("Seleziona colonne da visualizzare", all_columns, default=all_columns[:5] if len(all_columns) > 5 else all_columns)
        
        if selected_columns:
            st.dataframe(df[selected_columns])
        
        # Opzione per scaricare il dataframe filtrato
        if st.button("Scarica dati filtrati come CSV"):
            csv = df[selected_columns].to_csv(index=False)
            b64 = io.StringIO()
            b64.write(csv)
            b64.seek(0)
            st.download_button(
                label="Scarica CSV",
                data=b64,
                file_name="dati_filtrati.csv",
                mime="text/csv"
            )
        
        # Statistiche di base
        if st.checkbox("Mostra statistiche"):
            st.subheader("Statistiche descrittive")
            st.write(df.describe())
            
        # Ricerca nel dataset
        st.subheader("Ricerca nel dataset")
        search_term = st.text_input("Termine di ricerca")
        
        if search_term:
            # Cerca in tutte le colonne
            filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)]
            st.write(f"Risultati trovati: {filtered_df.shape[0]}")
            st.dataframe(filtered_df)
    
    except Exception as e:
        st.error(f"Si è verificato un errore nella lettura del file: {e}")
else:
    st.info("Carica un file CSV per visualizzare i dati")
    
    # Esempio
    st.subheader("Esempio di utilizzo:")
    st.markdown("""
    1. Clicca sul pulsante 'Carica un file CSV'
    2. Seleziona il tuo file CSV dal computer
    3. Configura le opzioni di lettura se necessario
    4. Esplora i tuoi dati!
    """)
