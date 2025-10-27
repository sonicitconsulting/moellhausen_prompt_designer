#!/usr/bin/env python3
"""
Script di test per verificare il funzionamento del sistema RAG Instagram
"""

import os
import sys
from mpd_rag_system import InstagramPromptGenerator

def test_system():
    """
    Test completo del sistema RAG
    """
    print("🧪 Test del Sistema RAG Instagram Prompt Generator")
    print("=" * 50)

    try:
        # 1. Inizializza il sistema
        print("\n1. 🚀 Inizializzazione sistema...")
        rag = InstagramPromptGenerator(
            chroma_path="./test_chroma_db",
            collection_name="test_posts"
        )
        print("✅ Sistema inizializzato")

        # 2. Carica il post di esempio
        print("\n2. 📚 Caricamento post di esempio...")

        # Leggi il post di esempio
        with open("example_post_1.txt", "r", encoding="utf-8") as f:
            example_post = f.read()

        result = rag.add_post_to_database(example_post, "King_Narmar_Example")
        print(f"Risultato: {result}")

        # 3. Test statistiche database
        print("\n3. 📊 Statistiche database...")
        stats = rag.get_collection_stats()
        print(stats)

        # 4. Test ricerca similarità
        print("\n4. 🔍 Test ricerca post simili...")
        similar = rag.get_similar_posts("luxury fragrance woody spicy", n_results=1)
        if similar:
            print(f"✅ Trovato {len(similar)} post simile")
            print(f"Score similarità: {similar[0]['similarity_score']:.3f}")
        else:
            print("❌ Nessun post simile trovato")

        # 5. Test analisi brand voice
        print("\n5. 🧠 Test analisi brand voice...")
        if similar:
            analysis = rag.analyze_brand_voice(similar)
            print(f"✅ Analisi completata: {len(analysis)} caratteri")
            print(f"Anteprima: {analysis[:200]}...")
        else:
            print("⚠️ Saltato - nessun post per l'analisi")

        # 6. Test generazione prompt
        print("\n6. ✨ Test generazione prompt...")
        prompt = rag.generate_optimized_prompt(
            product_name="OCEAN BREEZE BY MARINA",
            perfumer_name="Luca Rossi",
            brand_values="elegance, innovation, Mediterranean spirit",
            product_description="A fresh marine fragrance inspired by Italian coastlines",
            olfactory_pyramid="Top: Sea Salt, Lemon\nHeart: Marine Accord, Lavender\nBase: Ambergris, Cedar",
            keywords="freschezza, Mediterraneo, eleganza"
        )

        if "❌" not in prompt:
            print("✅ Prompt generato con successo")
            print(f"Lunghezza: {len(prompt)} caratteri")
        else:
            print("❌ Errore nella generazione del prompt")
            print(prompt)

        print("\n🎉 Test completato con successo!")
        return True

    except Exception as e:
        print(f"\n❌ Errore durante il test: {str(e)}")
        print("\n🔧 Verifica che:")
        print("- Ollama sia in esecuzione")
        print("- I modelli necessari siano disponibili")
        print("- Le dipendenze siano installate")
        return False

def check_dependencies():
    """
    Verifica le dipendenze necessarie
    """
    print("🔍 Verifica dipendenze...")

    missing_deps = []

    try:
        import gradio
        print("✅ Gradio disponibile")
    except ImportError:
        missing_deps.append("gradio")

    try:
        import chromadb  
        print("✅ ChromaDB disponibile")
    except ImportError:
        missing_deps.append("chromadb")

    try:
        import ollama
        print("✅ Ollama client disponibile")
    except ImportError:
        missing_deps.append("ollama")

    if missing_deps:
        print(f"\n❌ Dipendenze mancanti: {', '.join(missing_deps)}")
        print("Installa con: pip install -r requirements.txt")
        return False

    print("✅ Tutte le dipendenze sono disponibili")
    return True

if __name__ == "__main__":
    print("Instagram Prompt Generator - Test Suite")
    print("=" * 50)

    # Verifica dipendenze
    if not check_dependencies():
        sys.exit(1)

    # Verifica file di esempio
    if not os.path.exists("example_post_1.txt"):
        print("❌ File example_post_1.txt non trovato")
        sys.exit(1)

    # Esegui test
    success = test_system()

    if success:
        print("\n🚀 Il sistema è pronto per l'uso!")
        print("Esegui: python gradio_app.py")
    else:
        sys.exit(1)
