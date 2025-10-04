# 🌸 Instagram Prompt Generator per Moellhausen

Sistema RAG (Retrieval-Augmented Generation) che utilizza **Ollama + ChromaDB + Gradio** per generare prompt ottimali per post Instagram mantenendo il brand voice di Moellhausen.

## 🎯 Caratteristiche Principali

- **📚 Indicizzazione Post:** Carica e indicizza i post Instagram esistenti uno alla volta
- **🧠 Analisi Brand Voice:** Utilizza Ollama per analizzare tone of voice e stile
- **🔍 Ricerca Semantica:** Trova post simili tramite ChromaDB embeddings
- **✨ Generazione Prompt:** Crea prompt ottimizzati per LLM commerciali (GPT-4, Claude, etc.)
- **🌐 Interfaccia Web:** Due pagine Gradio intuitive per gestione e utilizzo

## 🏗️ Architettura

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Gradio    │ -> │ ChromaDB     │ -> │   Ollama    │
│ (Interface) │    │ (Embeddings) │    │ (Analysis)  │
└─────────────┘    └──────────────┘    └─────────────┘
       │                    │                   │
       v                    v                   v
   Input Form      Semantic Search      Brand Voice
   Management        Similarity         Analysis &
                                      Prompt Gen
```

## 📋 Prerequisiti

### 1. Server Ollama
Installa e configura Ollama con i modelli necessari:

```bash
# Installa Ollama (https://ollama.ai)
curl https://ollama.ai/install.sh | sh

# Scarica i modelli necessari
ollama pull llama3.1
ollama pull mxbai-embed-large

# Verifica installazione
ollama list
```

### 2. Python 3.8+
Assicurati di avere Python 3.8 o superiore installato.

## 🚀 Installazione

### 1. Clona/Scarica il progetto
```bash
# Se hai git
git clone <repository-url>
cd instagram-prompt-generator

# Oppure scarica i file manualmente
```

### 2. Installa le dipendenze
```bash
pip install -r requirements.txt
```

### 3. Verifica il sistema
```bash
python test_system.py
```

## ⚙️ Configurazione

Modifica il file `config.py` per adattare il sistema alle tue necessità:

```python
# Host Ollama (modifica se usi server remoto)
OLLAMA_HOST = "http://localhost:11434"

# Modelli da utilizzare
ANALYSIS_MODEL = "llama3.1"
EMBEDDING_MODEL = "mxbai-embed-large"

# Porta interfaccia web
GRADIO_PORT = 7860
```

## 🖥️ Utilizzo

### 1. Avvia l'applicazione
```bash
python gradio_app.py
```

L'interfaccia sarà disponibile su: `http://localhost:7860`

### 2. Carica i Post Esistenti (Pagina 1)

1. **Vai alla tab "📚 Caricamento Documenti"**
2. **Carica i file:** Utilizza il file uploader per file .txt o .md
3. **Nome post:** Assegna un nome identificativo (opzionale)
4. **Aggiungi al database:** Clicca "➕ Aggiungi al Database"
5. **Ripeti:** Carica tutti i post esistenti (almeno 3-5 consigliati)

### 3. Genera Prompt Ottimizzati (Pagina 2)

1. **Vai alla tab "✨ Generazione Prompt"**
2. **Compila i campi obbligatori:**
   - Nome Prodotto (es: "GOLDEN SUNSET BY AURORA")
   - Valori Brand (es: "craftsmanship, luxury, innovation")
   - Descrizione Prodotto (descrizione grezza del profumo)

3. **Campi opzionali:**
   - Nome Profumiere
   - Piramide Olfattiva
   - Parole Chiave

4. **Genera:** Clicca "🚀 Genera Prompt Ottimizzato"
5. **Copia il risultato:** Usa il prompt generato con il tuo LLM commerciale preferito

## 📁 Struttura File

```
instagram-prompt-generator/
├── requirements.txt          # Dipendenze Python
├── config.py                # Configurazioni del sistema
├── instagram_rag_system.py  # Classe principale RAG
├── gradio_app.py            # Interfaccia Gradio
├── test_system.py           # Script di test
├── example_post_1.txt       # Esempio post Moellhausen
├── chroma_db/              # Database ChromaDB (creato automaticamente)
└── README.md               # Questa documentazione
```

## 🔧 Risoluzione Problemi

### Errore: "Connection Error" con Ollama
- Verifica che Ollama sia in esecuzione: `ollama serve`
- Controlla l'host in `config.py`
- Per server remoti, modifica `OLLAMA_HOST`

### Errore: Modello non disponibile
```bash
# Scarica i modelli mancanti
ollama pull llama3.1
ollama pull mxbai-embed-large
```

### Database vuoto
- Carica almeno un post nella sezione "Caricamento Documenti"
- Verifica che i post abbiano la struttura corretta (con header markdown)

### Prompt non generato
- Verifica tutti i campi obbligatori (*)
- Controlla i log della console per errori dettagliati
- Assicurati che ci siano post nel database

## 📊 Esempio d'Uso Completo

### 1. Post di esempio da caricare:
```markdown
# UNIQUE, ONE OF A KIND WITH MOELLHAUSEN: KING NARMAR BY NILAFAR

## Brand Values
Moellhausen masterfully combines craftsmanship, scientific precision...

## Introduction
In KING NARMAR by NILAFAR DU NIL, our perfumer Anna Chiara Di Trolio...

[... resto del post ...]
```

### 2. Input per nuovo prodotto:
- **Nome:** "OCEAN BREEZE BY MARINA"
- **Profumiere:** "Luca Rossi"
- **Valori Brand:** "elegance, innovation, Mediterranean spirit"
- **Descrizione:** "A fresh marine fragrance inspired by Italian coastlines..."
- **Piramide:** "Top: Sea Salt, Lemon\nHeart: Marine Accord\nBase: Ambergris"

### 3. Output del sistema:
Un prompt dettagliato pronto per GPT-4/Claude che genererà un post Instagram perfettamente allineato al brand voice Moellhausen.

## 🚀 Server Remoto Ollama

Per utilizzare un server Ollama remoto:

1. **Modifica config.py:**
```python
OLLAMA_HOST = "http://IP_SERVER:11434"
```

2. **Oppure usa variabile d'ambiente:**
```bash
export OLLAMA_HOST="http://IP_SERVER:11434"
python gradio_app.py
```

## 🔒 Privacy e Sicurezza

- **100% Locale:** Tutti i dati rimangono nel tuo ambiente
- **Nessun invio cloud:** I post non vengono mai inviati a servizi esterni
- **Controllo completo:** Gestisci i tuoi dati e modelli in autonomia

## 🤖 Modelli Supportati

### Analisi e Generazione:
- `llama3.1` (consigliato)
- `llama3`
- `mistral`
- `codellama`

### Embeddings:
- `mxbai-embed-large` (consigliato)
- `nomic-embed-text`
- `all-minilm`

## 📈 Performance e Ottimizzazione

- **RAM consigliata:** 8GB+ per modelli 7B
- **Storage:** ~10GB per modelli + database
- **CPU:** Beneficia di CPU multi-core
- **GPU:** Opzionale ma accelera significativamente l'elaborazione

## 🆘 Supporto

Per problemi o domande:

1. **Controlla i logs** della console per errori dettagliati
2. **Esegui il test:** `python test_system.py`
3. **Verifica configurazione:** Controlla `config.py`
4. **Documenta l'errore** con output completo per assistenza

## 📄 Licenza

Sviluppato per Moellhausen - Sistema proprietario per uso interno.

---

**🌸 Made with ❤️ for Moellhausen's Instagram Content Excellence**