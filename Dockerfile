# Usa un'immagine base di Python
FROM python:3.9-slim

RUN pip install --upgrade pip

# Imposta una directory di lavoro
WORKDIR /app

# Copia il file requirements.txt nella directory di lavoro corrente (/app)
COPY requirements.txt ./

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia il file genera_corsi.py nella directory di lavoro corrente (/app)
COPY genera_corsi.py ./

# Espone la porta 8501, la porta predefinita su cui Streamlit esegue l'applicazione
EXPOSE 8501

# Esegue l'applicazione Streamlit quando il container viene avviato
CMD ["streamlit", "run", "genera_corsi.py"]
