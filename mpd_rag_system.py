# Instagram Prompt Generator - Sistema RAG per Moellhausen
# Integra Ollama + ChromaDB + Gradio per generare prompt ottimali

import os
import gradio as gr
import chromadb
import ollama
import json
from typing import List, Dict, Optional
import re
from datetime import datetime
import pandas as pd

from  mpd_config import Config

class InstagramPromptGenerator:
    """
    Sistema RAG per generare prompt ottimali per post Instagram 
    mantenendo il tone of voice di Moellhausen
    """

    def __init__(
        self,
        chroma_path: str = Config.CHROMA_DB_PATH,
        collection_name: str = Config.COLLECTION_NAME,
        embedding_model: str = Config.EMBEDDING_MODEL,
        analysis_model: str = Config.ANALYSIS_MODEL,
        ollama_host: str = Config.OLLAMA_HOST
    ):

        self.chroma_path = chroma_path
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.analysis_model = analysis_model

        # Configura client Ollama (per server remoto)
        if ollama_host != "http://localhost:11434":
            os.environ['OLLAMA_HOST'] = ollama_host

        # Inizializza ChromaDB
        os.makedirs(chroma_path, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)

        # Crea o ottieni la collection
        try:
            self.collection = self.chroma_client.get_collection(
                name=collection_name
            )
            print(f"Collection '{collection_name}' caricata con successo")
        except:
            self.collection = self.chroma_client.create_collection(
                name=collection_name
            )
            print(f"Collection '{collection_name}' creata con successo")

    def extract_post_structure(self, post_text: str) -> Dict[str, str]:
        """
        Estrae la struttura del post Instagram utilizzando le sezioni markdown
        """
        sections = {
            'title': '',
            'brand_values': '',
            'introduction': '',
            'description': '',
            'closing': '',
            'olfactory_pyramid': '',
            'tags': ''
        }

        # Pattern per estrarre le sezioni
        current_section = None
        lines = post_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Identifica le sezioni basandosi sui header
            if line.startswith('# '):
                sections['title'] = line[2:].strip()
                current_section = 'title'
            elif 'Brand Values' in line and line.startswith('##'):
                current_section = 'brand_values'
            elif 'Introduction' in line and line.startswith('##'):
                current_section = 'introduction'  
            elif 'Description' in line and line.startswith('##'):
                current_section = 'description'
            elif 'Closing' in line and line.startswith('##'):
                current_section = 'closing'
            elif 'OLFACTORY PYRAMID' in line and line.startswith('##'):
                current_section = 'olfactory_pyramid'
            elif 'TAGS' in line and line.startswith('##'):
                current_section = 'tags'
            elif current_section and not line.startswith('#'):
                # Aggiungi contenuto alla sezione corrente
                if sections[current_section]:
                    sections[current_section] += ' ' + line
                else:
                    sections[current_section] = line

        return sections

    def add_post_to_database(self, post_text: str, post_name: str = "") -> str:
        """
        Aggiunge un singolo post al database ChromaDB
        """
        try:
            # Crea un ID univoco
            post_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if post_name:
                post_id = f"{post_name}_{post_id}"

            # Estrai la struttura del post
            structure = self.extract_post_structure(post_text)

            # Crea metadati con le informazioni estratte
            metadata = {
                'post_id': post_id,
                'title': structure['title'][:200] if structure['title'] else 'Untitled',
                'brand_values': structure['brand_values'][:300] if structure['brand_values'] else '',
                'date_added': datetime.now().isoformat(),
                'word_count': len(post_text.split()),
                'has_olfactory_pyramid': bool(structure['olfactory_pyramid']),
                'post_name': post_name or 'Unknown'
            }

            # Aggiungi alla collection ChromaDB
            self.collection.add(
                documents=[post_text],
                metadatas=[metadata],
                ids=[post_id]
            )

            return f"✅ Post '{structure['title'][:50]}...' aggiunto con successo (ID: {post_id})"

        except Exception as e:
            return f"❌ Errore nell'aggiungere il post: {str(e)}"

    def get_collection_stats(self) -> str:
        """
        Ottiene statistiche sulla collection
        """
        try:
            count = self.collection.count()
            if count == 0:
                return "📊 Database vuoto - nessun post indicizzato"

            # Prova a ottenere alcuni metadati per le statistiche
            sample = self.collection.get(limit=min(count, 5))
            titles = [meta.get('title', 'N/A')[:30] + '...' for meta in sample['metadatas']]

            stats = f"""📊 **Statistiche Database:**
- **Post indicizzati:** {count}
- **Esempi di post:** {', '.join(titles)}
- **Database path:** {self.chroma_path}
"""
            return stats

        except Exception as e:
            return f"❌ Errore nel calcolare le statistiche: {str(e)}"

    def get_similar_posts(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Recupera i post più simili dalla database
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count())
            )

            similar_posts = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    similar_posts.append({
                        'document': doc,
                        'metadata': metadata,
                        'similarity_score': 1 - distance  # Converti distanza in similarità
                    })

            return similar_posts

        except Exception as e:
            print(f"Errore nel recuperare post simili: {str(e)}")
            return []

    def analyze_brand_voice(self, posts: List[Dict]) -> str:
        """
        Analizza il tone of voice e le caratteristiche dei post usando Ollama
        """
        if not posts:
            return "Nessun post disponibile per l'analisi"

        # Combina tutti i post per l'analisi
        combined_text = "\n\n---POST SEPARATOR---\n\n".join([post['document'] for post in posts])

        analysis_prompt = f"""Sei un esperto di marketing e brand communication italiana. Analizza questi post Instagram di Moellhausen (brand di profumi luxury italiano) ed estrai:

1. **TONE OF VOICE:**
   - Registro linguistico (formale/informale)
   - Stile comunicativo
   - Personalità del brand

2. **STRUTTURA NARRATIVA:**
   - Schema compositivo ricorrente
   - Elementi sempre presenti  
   - Sequenza logica delle informazioni

3. **LESSICO E TERMINOLOGIA:**
   - Parole chiave ricorrenti
   - Terminologia tecnica specifica
   - Aggettivi caratteristici

4. **ELEMENTI STILISTICI:**
   - Uso di metafore o figure retoriche
   - Riferimenti culturali/storici
   - Approccio descrittivo

POST DA ANALIZZARE:
{combined_text[:3000]}

Rispondi in italiano con un'analisi dettagliata e strutturata, focalizzandoti sui pattern che si ripetono e che caratterizzano il brand."""

        try:
            response = ollama.generate(
                model=self.analysis_model,
                prompt=analysis_prompt,
                options={'temperature': 0.3}
            )

            return response['response']

        except Exception as e:
            return f"❌ Errore nell'analisi del brand voice: {str(e)}\n\nVerifica che Ollama sia in esecuzione e che il modello '{self.analysis_model}' sia disponibile."

    def generate_optimized_prompt(self, 
                                product_name: str,
                                perfumer_name: str, 
                                brand_values: str,
                                product_description: str,
                                olfactory_pyramid: str,
                                keywords: str) -> str:
        """
        Genera un prompt ottimizzato per LLM commerciale
        """
        try:
            # Verifica che ci siano dati nel database
            count = self.collection.count()
            if count == 0:
                return "❌ **Errore:** Nessun post nel database. Carica prima alcuni post di esempio nella sezione 'Caricamento Documenti'."

            # Recupera post simili basati su prodotto e valori
            query = f"{product_name} {brand_values} {product_description}"
            similar_posts = self.get_similar_posts(query, n_results=3)

            if not similar_posts:
                return "❌ **Errore:** Impossibile trovare post simili nel database."

            # Analizza il brand voice dei post simili
            brand_analysis = self.analyze_brand_voice(similar_posts)

            # Crea il prompt ottimizzato
            prompt_generation = f"""Sei un esperto prompt engineer specializzato in marketing luxury e comunicazione di brand. 

Devi creare un PROMPT PERFETTO per un LLM commerciale (come GPT-4, Claude, etc.) che generi un post Instagram per Moellhausen mantenendo ESATTAMENTE il loro stile unico.

**INFORMAZIONI SUL NUOVO PRODOTTO:**
- Nome prodotto: {product_name}
- Profumiere: {perfumer_name}
- Valori brand da evidenziare: {brand_values}
- Descrizione grezza del profumo: {product_description}
- Piramide olfattiva: {olfactory_pyramid}
- Parole chiave obbligatorie: {keywords}

**ANALISI DEL BRAND VOICE MOELLHAUSEN:**
{brand_analysis}

**POST DI RIFERIMENTO (esempi dello stile autentico):**
{chr(10).join([f"ESEMPIO {i+1}:{chr(10)}{post['document'][:1000]}..." for i, post in enumerate(similar_posts[:2])])}

**COMPITO:**
Crea un prompt dettagliato, strutturato e completo che, quando usato con un LLM commerciale, genererà un post Instagram che:
1. Sia TASSATIVAMENTE in lingua inglese
2. Rispetti PERFETTAMENTE la struttura markdown dei post esistenti
3. Mantenga il tone of voice sofisticato e poetico di Moellhausen
4. Integri tutte le informazioni del nuovo prodotto in modo organico
5. Sia indistinguibile dai post autentici del brand


Il prompt deve essere autosufficiente e includere:
- Definizione chiara del ruolo per l'LLM
- Struttura ESATTA da seguire (con markdown)
- Tone of voice specifico con esempi
- Template con placeholder
- Vincoli e requisiti stilistici
- Esempi di lessico appropriato

Genera SOLO il prompt ottimizzato, pronto per essere copiato e usato direttamente con un LLM commerciale."""

            response = ollama.generate(
                model=self.analysis_model,
                prompt=prompt_generation,
                options={'temperature': 0.4, 'num_predict': 2000}
            )

            return response['response']

        except Exception as e:
            return f"❌ **Errore nella generazione del prompt:** {str(e)}\n\nVerifica che Ollama sia in esecuzione e che il modello '{self.analysis_model}' sia disponibile."
