# Interfaccia Gradio per il Sistema RAG Instagram Prompt Generator
# Due pagine: 1) Caricamento Documenti  2) Generazione Prompt

import gradio as gr
import os
from mpd_rag_system import InstagramPromptGenerator
from mpd_config import Config

class GradioInterface:
    """
    Interfaccia utente Gradio per il sistema RAG Instagram
    """

    def __init__(self, ollama_host=Config.OLLAMA_HOST):
        self.rag_system = InstagramPromptGenerator(
            chroma_path=Config.CHROMA_DB_PATH,
            collection_name=Config.COLLECTION_NAME,
            embedding_model=Config.EMBEDDING_MODEL,
            analysis_model=Config.ANALYSIS_MODEL,
            ollama_host=ollama_host
        )

    def process_uploaded_file(self, file, post_name):
        """
        Processa un file caricato ed estrae il contenuto
        """
        if file is None:
            return "❌ No file selected", "", ""

        try:
            # Leggi il contenuto del file
            if hasattr(file, 'name'):
                filepath = file.name
            else:
                filepath = file

            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                return "❌ File is empty", "", ""

            # Mostra anteprima del contenuto
            preview = content[:500] + "..." if len(content) > 500 else content
            return f"✅ File loaded: {len(content)} characters", preview, content

        except Exception as e:
            return f"❌ Errore loading file: {str(e)}", ""

    def add_document_to_db(self, content, post_name):
        """
        Aggiunge un documento al database ChromaDB
        """
        if not content.strip():
            return "❌ Empty file - Type or load an Instagram post", self.rag_system.get_collection_stats()

        if not post_name.strip():
            post_name = f"Post_{len(content)//100}"

        result = self.rag_system.add_post_to_database(content, post_name)
        stats = self.rag_system.get_collection_stats()

        return result, stats

    def generate_prompt(self, product_name, perfumer_name, brand_values, 
                       product_description, olfactory_pyramid, keywords):
        """
        Genera il prompt ottimizzato per LLM commerciale
        """
        # Validazione input
        if not all([product_name.strip(), brand_values.strip(), product_description.strip()]):
            return "❌ **Error:** Product Name, Brand Values and Description are mandatory"

        # Genera il prompt ottimizzato
        result = self.rag_system.generate_optimized_prompt(
            product_name=product_name,
            perfumer_name=perfumer_name or "Not specified",
            brand_values=brand_values,
            product_description=product_description,
            olfactory_pyramid=olfactory_pyramid or "To be defined",
            keywords=keywords or ""
        )

        return result

    def on_file_upload(self, file, post_name):
        status, preview, full_content = self.process_uploaded_file(file, post_name)
        return status, preview, full_content  # Il campo manuale ora riceve il testo INTEGRALE

    def create_interface(self):
        """
        Crea l'interfaccia Gradio con due pagine
        """
        # Stili CSS personalizzati
        custom_css = """
        .main-header { text-align: center; color: #2C3E50; margin: 20px 0; }
        .section-header { color: #34495E; border-bottom: 2px solid #E74C3C; padding-bottom: 10px; }
        .success-text { color: #27AE60; font-weight: bold; }
        .error-text { color: #E74C3C; font-weight: bold; }
        .info-box { background: #F8F9FA; padding: 15px; border-radius: 8px; margin: 10px 0; }
        """

        with gr.Blocks(css=custom_css, title="Moellhausen Instagram Prompt Generator") as interface:

            gr.HTML("""
            <div class="main-header">
                <h1>🌸 Moellhausen Instagram Prompt Generator</h1>
                <p><em>RAG System for Prompt Generation</em></p>
            </div>
            """)

            # === PAGINA 1: CARICAMENTO DOCUMENTI ===
            with gr.Tab("📚 Document Loading"):
                gr.HTML('<h2 class="section-header">📚 Instagram Posts Database Management</h2>')

                gr.HTML("""
                <div class="info-box">
                    <strong>📋 Instructions:</strong><br>
                    1. Upload existing Instagram posts one at a time<br>
                    2. Posts must be in text/markdown format.<br>
                    3. Each post will be indexed in the database for brand voice analysis.<br>
                    4. At least 3-5 posts are recommended for optimal results.
                </div>
                """)

                with gr.Row():
                    with gr.Column(scale=2):
                        gr.HTML('<h3>📄 File Loading</h3>')

                        file_upload = gr.File(
                            label="Select Instagram post file (.txt, .md)",
                            file_types=[".txt", ".md"],
                            file_count="single"
                        )

                        post_name_input = gr.Textbox(
                            label="Post name (optional)",
                            placeholder="es: King_Narmar_Nilafar",
                            lines=1
                        )

                        file_status = gr.Textbox(
                            label="Status File", 
                            interactive=False,
                            lines=2
                        )

                    with gr.Column(scale=3):
                        gr.HTML('<h3>👁️ Content Preview</h3>')

                        content_preview = gr.Textbox(
                            label="Preview of loaded content",
                            lines=10,
                            interactive=False
                        )

                        content_manual = gr.Textbox(
                            label="Or paste the content manually",
                            lines=10,
                            placeholder="Paste the text of your Instagram post here..."
                        )

                with gr.Row():
                    add_button = gr.Button("➕ Add to Database", variant="primary", size="large")
                    clear_button = gr.Button("🗑️ Clear", variant="secondary")

                with gr.Row():
                    with gr.Column():
                        add_status = gr.Textbox(
                            label="Result",
                            interactive=False,
                            lines=2
                        )

                    with gr.Column():
                        db_stats = gr.Textbox(
                            label="Database statistics",
                            interactive=False, 
                            lines=4,
                            value=self.rag_system.get_collection_stats()
                        )

                # Eventi pagina 1
                file_upload.change(
                    fn=self.on_file_upload,
                    inputs=[file_upload, post_name_input],
                    outputs=[file_status, content_preview, content_manual]
                )

                add_button.click(
                    fn=self.add_document_to_db,
                    inputs=[content_manual, post_name_input],
                    outputs=[add_status, db_stats]
                )

                clear_button.click(
                    fn=lambda: ("", "", "", "", None, ""),
                    outputs=[content_manual, post_name_input, file_status, content_preview, file_upload, add_status]
                )

            # === PAGINA 2: GENERAZIONE PROMPT ===
            with gr.Tab("✨ Generazione Prompt"):
                gr.HTML('<h2 class="section-header">✨ Generatore Prompt Ottimizzato</h2>')

                gr.HTML("""
                <div class="info-box">
                    <strong>🎯 Funzionalità:</strong><br>
                    Inserisci i dettagli del nuovo prodotto e ottieni un prompt perfetto per LLM commerciali 
                    (GPT-4, Claude, etc.) che genererà un post Instagram nel perfetto stile Moellhausen.
                </div>
                """)

                with gr.Row():
                    with gr.Column():
                        gr.HTML('<h3>🏷️ Informazioni Prodotto</h3>')

                        product_name = gr.Textbox(
                            label="Nome Prodotto *",
                            placeholder="es: GOLDEN SUNSET BY AURORA",
                            lines=1
                        )

                        perfumer_name = gr.Textbox(
                            label="Nome Profumiere",
                            placeholder="es: Anna Chiara Di Trolio",
                            lines=1
                        )

                        brand_values = gr.Textbox(
                            label="Valori Brand da Evidenziare *", 
                            placeholder="es: craftsmanship, scientific precision, contemporary luxury",
                            lines=2
                        )

                        keywords = gr.Textbox(
                            label="Parole Chiave Obbligatorie",
                            placeholder="es: eleganza, raffinatezza, unicità",
                            lines=2
                        )

                    with gr.Column():
                        gr.HTML('<h3>🌺 Descrizione Prodotto</h3>')

                        product_description = gr.Textbox(
                            label="Descrizione Grezza del Profumo *",
                            placeholder="Descrivi il profumo, l'ispirazione, la storia...",
                            lines=6
                        )

                        olfactory_pyramid = gr.Textbox(
                            label="Piramide Olfattiva",
                            placeholder="Top: ... \nHeart: ... \nBase: ...",
                            lines=4
                        )

                generate_button = gr.Button("🚀 Genera Prompt Ottimizzato", variant="primary", size="large")

                gr.HTML('<h3>📋 Prompt Generato</h3>')
                prompt_output = gr.Textbox(
                    label="Prompt ottimizzato per LLM commerciale",
                    lines=20,
                    interactive=True,  # Permette di copiare facilmente
                    show_copy_button=True
                )

                # Eventi pagina 2
                generate_button.click(
                    fn=self.generate_prompt,
                    inputs=[product_name, perfumer_name, brand_values, 
                           product_description, olfactory_pyramid, keywords],
                    outputs=prompt_output
                )

            # Footer
            gr.HTML("""
            <div style="text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid #ddd;">
                <p><em>🤖 Powered by SoNicITConsulting | Made for Moellhausen</em></p>
            </div>
            """)

        return interface

def launch_app(ollama_host="http://localhost:11434", share=False, port=7860):
    """
    Lancia l'applicazione Gradio
    """
    try:
        print("🚀 Inizializzazione Instagram Prompt Generator...")
        print(f"📡 Host Ollama: {ollama_host}")

        # Crea l'interfaccia
        app = GradioInterface(ollama_host=ollama_host)
        interface = app.create_interface()

        print("✅ Interfaccia creata con successo!")
        print(f"🌐 Avvio server su porta {port}...")

        # Lancia l'interfaccia
        interface.launch(
            share=share,
            server_port=port,
            server_name="0.0.0.0" if share else "127.0.0.1",
            show_api=False
        )

    except Exception as e:
        print(f"❌ Errore nell'avvio dell'applicazione: {str(e)}")
        print("\n🔧 Verifica che:")
        print("1. Ollama sia in esecuzione")
        print("2. Il modello llama3.1 sia disponibile") 
        print("3. Tutte le dipendenze siano installate")

if __name__ == "__main__":
    # Configurazione predefinita - modifica secondo necessità
    OLLAMA_HOST = Config.OLLAMA_HOST
    PORT = Config.GRADIO_PORT
    SHARE = Config.GRADIO_SHARE

    launch_app(
        ollama_host=OLLAMA_HOST,
        share=SHARE, 
        port=PORT
    )
