from typing import Optional
from langchain.chains import LLMChain
from langchain.embeddings import OpenAIEmbeddings
import os
from langchain.docstore import InMemoryDocstore
from langchain.prompts import PromptTemplate
from langchain.vectorstores.faiss import FAISS
import faiss
from langchain_experimental.autonomous_agents import BabyAGI
from langchain.llms import OpenAI
os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "false"

import streamlit as st



def page_input_key():
    st.title("Inserisci la tua chiave API")

    # Inizializza la lista delle API keys se non esiste già
    if 'api_keys' not in st.session_state:
        st.session_state['api_keys'] = []

    # Campo di input per aggiungere una nuova API key
    new_api_key = st.text_input("Inserisci una nuova OPEN_API_KEY: ")

    if st.button("Salva nuova API key"):
        if new_api_key:  # Controlla che sia stata inserita una stringa non vuota
            # Aggiungi la nuova API key alla lista e aggiorna l'ambiente
            st.session_state['api_keys'].append(new_api_key)
            # Imposta la nuova API key come variabile d'ambiente
            os.environ["OPENAI_API_KEY"] = new_api_key
            # Pulisce il campo di input dopo il salvataggio
            st.session_state['new_api_key'] = ''

    # Dropdown per selezionare una API key salvata
    if st.session_state['api_keys']:
        selected_key = st.selectbox("Seleziona una OPEN_API_KEY salvata:", st.session_state['api_keys'])
        if st.button("Imposta OPEN_API_KEY selezionata"):
            os.environ["OPENAI_API_KEY"] = selected_key
def page_main_app():
    # Controllo se l'API key è stata impostata
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("Devi prima impostare l'API key.")
        return  # Interrompe l'esecuzione della funzione se non è stata impostata l'API key

    st.title('Genera slides')
    numero_slides = st.number_input('Seleziona un numero di slides:', min_value=1, max_value=100, value=1)

    embeddings_model = OpenAIEmbeddings()
    embedding_size = 1536
    index = faiss.IndexFlatL2(embedding_size)
    vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {})
    llm = OpenAI(temperature=0)

    # Logging of LLMChains
    verbose = False
    # If None, will keep on going forever
    max_iterations: Optional[int] = numero_slides
    baby_agi = BabyAGI.from_llm(
        llm=llm, vectorstore=vectorstore, verbose=verbose, max_iterations=numero_slides, numero_slides=20
    )

    prompt = PromptTemplate(
        input_variables=["request"],
        template="Avvogli il testo che ti viene passato con del HTML in modo che si veda un titolo e elenchi puntati, crea una gerarchia di elenchi puntati e sottolinea le parole chiave in grassetto o in corsivo: {request} . Ricorda di fare delle gerarchie del tipo <ol><li> <ol><li> <li> </li></li></ol> </li></ol> ?",
    )

    llm = OpenAI(temperature=0)

    llmchain = LLMChain(llm=llm, prompt=prompt)

    st.write('Il sistema funziona in modo che quando uno specifica un argomento o qualche informazione vengono generati 30 sotto spunti rispetto a ciò che è passato in input. Il sistema procederà a generare un numero di slide pari al numero selezionato nella cassella di input. Ricorda che più slides vuoi più è il tempo necessario.')

    # Crea un input testuale nell'app Streamlit
    input_utente = st.text_input("Inserisci qualcosa:")

    # Crea un bottone che, quando premuto, chiama la funzione definita sopra
    if st.button("Conferma"):
        with st.spinner('Attendere prego....'):
            baby_agi({"objective": input_utente})
            for element in baby_agi.task_list:
                task_name = element["task_name"]
                task_id = element["task_id"]
            for element in baby_agi.my_resutl_of_tasks:
                output = llmchain.run(element['result'])
                st.markdown(output, unsafe_allow_html=True)

if __name__ == "__main__":
    pages = {
        "Inserimento Chiave API": page_input_key,
        "App Principale": page_main_app
    }
    page = st.sidebar.radio("Scegli una pagina:", list(pages.keys()))
    pages[page]()
