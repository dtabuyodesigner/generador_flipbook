#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creador de Flipbooks desde PDF - v4 FINAL
Fixes:
- Navegación al final y vuelta atrás
- Pantalla completa funciona en cualquier momento
- Guarda HTML original para restaurar tras destroy
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import webbrowser
from datetime import datetime

try:
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError:
    print("Falta instalar: pip install pdf2image pillow")
    exit(1)


def generar_html(titulo, num_pages):
    """Genera el HTML del flipbook con StPageFlip y fixes de navegación"""
    
    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__TITULO__</title>
    <script src="https://cdn.jsdelivr.net/npm/page-flip@2.0.7/dist/js/page-flip.browser.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
            overflow-x: hidden;
        }
        
        .header {
            color: white;
            text-align: center;
            margin-bottom: 20px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            font-size: 2em;
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 5px;
        }
        
        .header p {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        #flipbook-container {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        #flipbook {
            box-shadow: 0 30px 80px rgba(0,0,0,0.5);
        }
        
        .page {
            background: white;
            overflow: hidden;
            position: relative;
        }
        
        .page-cover {
            background: white;
            box-shadow: inset -10px 0 30px -10px rgba(0,0,0,0.4);
        }
        
        .page-cover-back {
            background: white;
            box-shadow: inset 10px 0 30px -10px rgba(0,0,0,0.4);
        }
        
        .page img {
            width: 100%;
            height: 100%;
            display: block;
            object-fit: contain;
            background: white;
        }
        
        .page-number {
            position: absolute;
            bottom: 12px;
            background: rgba(102, 126, 234, 0.85);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.75em;
            font-weight: bold;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            letter-spacing: 1px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            pointer-events: none;
            z-index: 10;
        }
        
        /* Páginas izquierdas: número en esquina inferior IZQUIERDA (exterior) */
        .page-left-side .page-number {
            left: 12px;
        }
        
        /* Páginas derechas: número en esquina inferior DERECHA (exterior) */
        .page-right-side .page-number {
            right: 12px;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            margin-top: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        button {
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            border: none;
            padding: 12px 24px;
            border-radius: 30px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.2s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .fullscreen-btn {
            background: #ff6b6b;
            color: white;
        }
        
        .reset-btn {
            background: #4caf50;
            color: white;
        }
        
        .page-info {
            background: rgba(255, 255, 255, 0.95);
            padding: 12px 24px;
            border-radius: 30px;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            min-width: 130px;
            text-align: center;
        }
        
        /* Modo fullscreen */
        body.fs-mode {
            padding: 10px;
            justify-content: space-between;
        }
        
        body.fs-mode .header {
            display: none;
        }
        
        body.fs-mode #flipbook-container {
            flex: 1;
        }
        
        body.fs-mode .controls {
            margin-top: 10px;
            margin-bottom: 10px;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.3em; }
            button { padding: 10px 18px; font-size: 0.9em; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>__TITULO__</h1>
        <p>📰 Periódico Digital Interactivo</p>
    </div>
    
    <div id="flipbook-container">
        <div id="flipbook"></div>
    </div>
    
    <div class="controls">
        <button id="prev-btn">← Anterior</button>
        <div class="page-info">
            <span id="current-page">1</span> / <span id="total-pages">__NUM_PAGES__</span>
        </div>
        <button id="next-btn">Siguiente →</button>
        <button class="fullscreen-btn" id="fullscreen-btn">⛶ Pantalla Completa</button>
        <button class="reset-btn" id="reset-btn">↺ Reiniciar</button>
    </div>
    
    <script>
        const totalPages = __NUM_PAGES__;
        let pageFlip = null;
        let currentPageIndex = 0;
        
        function calcSize() {
            const isMobile = window.innerWidth < 768;
            const isFs = document.body.classList.contains('fs-mode');
            
            let availW, availH;
            if (isFs) {
                availW = window.innerWidth - 30;
                availH = window.innerHeight - 120;
            } else {
                availW = Math.min(window.innerWidth - 60, 1100);
                availH = window.innerHeight - 280;
            }
            
            let width, height;
            const aspectRatio = 1.414;
            
            if (isMobile) {
                width = Math.min(availW, 400);
                height = width * aspectRatio;
                if (height > availH) {
                    height = availH;
                    width = height / aspectRatio;
                }
            } else {
                width = Math.min(availW / 2, 500);
                height = width * aspectRatio;
                if (height > availH) {
                    height = availH;
                    width = height / aspectRatio;
                }
            }
            
            return { 
                width: Math.floor(width), 
                height: Math.floor(height), 
                isMobile: isMobile 
            };
        }
        
        function buildPagesHTML() {
            // IMPORTANTE: recrear el div#flipbook desde cero
            // porque StPageFlip.destroy() puede haberlo eliminado/modificado
            const container = document.getElementById('flipbook-container');
            container.innerHTML = '<div id="flipbook"></div>';
            
            const fb = document.getElementById('flipbook');
            for (let i = 1; i <= totalPages; i++) {
                const div = document.createElement('div');
                div.className = 'page';
                
                // Marcar la primera como portada (sin número)
                if (i === 1) {
                    div.className = 'page page-cover';
                }
                // Marcar la última como contraportada
                if (i === totalPages) {
                    div.className = 'page page-cover-back';
                }
                
                const img = document.createElement('img');
                img.src = 'pages/page_' + String(i).padStart(3, '0') + '.png';
                img.alt = 'Página ' + i;
                div.appendChild(img);
                
                // Número de página (excepto en portada y contraportada)
                if (i !== 1 && i !== totalPages) {
                    // Páginas pares (2, 4, 6...) van a la IZQUIERDA del libro
                    // Páginas impares (3, 5, 7...) van a la DERECHA del libro
                    if (i % 2 === 0) {
                        div.classList.add('page-left-side');
                    } else {
                        div.classList.add('page-right-side');
                    }
                    
                    const num = document.createElement('div');
                    num.className = 'page-number';
                    num.textContent = i - 1;
                    div.appendChild(num);
                }
                
                fb.appendChild(div);
            }
        }
        
        function initFlipbook(goToPage) {
            const size = calcSize();
            
            // Reconstruir el HTML original de las páginas
            buildPagesHTML();
            
            pageFlip = new St.PageFlip(document.getElementById('flipbook'), {
                width: size.width,
                height: size.height,
                size: 'fixed',
                drawShadow: true,
                flippingTime: 700,
                usePortrait: size.isMobile,
                showCover: true,
                mobileScrollSupport: false,
                maxShadowOpacity: 0.5,
                useMouseEvents: true,
                swipeDistance: 30
            });
            
            pageFlip.loadFromHTML(document.querySelectorAll('.page'));
            
            pageFlip.on('flip', function(e) {
                const idx = e.data;
                currentPageIndex = idx;
                document.getElementById('current-page').textContent = idx + 1;
                document.getElementById('prev-btn').disabled = idx === 0;
                document.getElementById('next-btn').disabled = idx >= totalPages - 1;
            });
            
            // Ir a la página guardada si se especifica
            if (goToPage && goToPage > 0) {
                setTimeout(function() {
                    if (pageFlip) {
                        pageFlip.flip(goToPage, 'top');
                    }
                }, 150);
            } else {
                // Inicializar estado botones
                document.getElementById('prev-btn').disabled = true;
                document.getElementById('next-btn').disabled = totalPages <= 1;
            }
        }
        
        function reinitFlipbook(keepPage) {
            const savedPage = keepPage ? currentPageIndex : 0;
            
            if (pageFlip) {
                try {
                    pageFlip.destroy();
                } catch (e) {
                    console.log('Error al destruir:', e);
                }
                pageFlip = null;
            }
            
            // Pequeña espera para que el DOM se limpie
            setTimeout(function() {
                initFlipbook(savedPage);
            }, 50);
        }
        
        // Botón anterior
        document.getElementById('prev-btn').addEventListener('click', function() {
            if (pageFlip) pageFlip.flipPrev();
        });
        
        // Botón siguiente
        document.getElementById('next-btn').addEventListener('click', function() {
            if (pageFlip) pageFlip.flipNext();
        });
        
        // Botón reiniciar (vuelve al principio sin recrear)
        document.getElementById('reset-btn').addEventListener('click', function() {
            reinitFlipbook(false);
        });
        
        // Botón pantalla completa
        document.getElementById('fullscreen-btn').addEventListener('click', async function() {
            const isFs = document.body.classList.contains('fs-mode');
            
            if (!isFs) {
                // Entrar fullscreen
                try {
                    if (document.documentElement.requestFullscreen) {
                        await document.documentElement.requestFullscreen();
                    } else if (document.documentElement.webkitRequestFullscreen) {
                        await document.documentElement.webkitRequestFullscreen();
                    }
                } catch (e) {
                    console.log('Sin API fullscreen, modo CSS solo');
                }
                document.body.classList.add('fs-mode');
                setTimeout(function() { reinitFlipbook(true); }, 200);
            } else {
                // Salir fullscreen
                try {
                    if (document.exitFullscreen) {
                        await document.exitFullscreen();
                    } else if (document.webkitExitFullscreen) {
                        await document.webkitExitFullscreen();
                    }
                } catch (e) {}
                document.body.classList.remove('fs-mode');
                setTimeout(function() { reinitFlipbook(true); }, 200);
            }
        });
        
        // Detectar salida de fullscreen por ESC
        document.addEventListener('fullscreenchange', function() {
            if (!document.fullscreenElement && document.body.classList.contains('fs-mode')) {
                document.body.classList.remove('fs-mode');
                setTimeout(function() { reinitFlipbook(true); }, 200);
            }
        });
        
        // Teclado
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowRight' && pageFlip) pageFlip.flipNext();
            if (e.key === 'ArrowLeft' && pageFlip) pageFlip.flipPrev();
        });
        
        // Resize con debounce
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() { reinitFlipbook(true); }, 400);
        });
        
        // Inicializar
        window.addEventListener('load', function() {
            initFlipbook(0);
        });
    </script>
</body>
</html>
"""
    
    # Reemplazar placeholders
    html = html.replace("__TITULO__", titulo)
    html = html.replace("__NUM_PAGES__", str(num_pages))
    
    return html


class CreadorFlipbook:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Periódicos Digitales")
        self.root.geometry("550x510")
        self.root.resizable(False, False)
        
        self.pdf_path = tk.StringVar()
        self.output_folder = None
        self.flipbook_html = None
        self.instrucciones_html = None
        
        style = ttk.Style()
        style.theme_use('clam')
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title = ttk.Label(main_frame, text="📰 Generador de Periódicos Digitales", 
                         font=("Arial", 14, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(main_frame, text="1. Selecciona el PDF:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=10)
        
        pdf_frame = ttk.Frame(main_frame)
        pdf_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(pdf_frame, textvariable=self.pdf_path, state="readonly", width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(pdf_frame, text="Examinar...", command=self.seleccionar_pdf).pack(side=tk.LEFT)
        
        ttk.Label(main_frame, text="2. Nombre de la carpeta:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, pady=10)
        self.nombre_output = ttk.Entry(main_frame, width=40)
        self.nombre_output.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.nombre_output.insert(0, f"periodico_{datetime.now().strftime('%d_%m_%Y').lower()}")
        
        ttk.Button(main_frame, text="3. Generar Flipbook", command=self.generar_flipbook).grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.status_label = ttk.Label(main_frame, text="Listo para empezar", foreground="blue")
        self.status_label.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.btn_abrir = ttk.Button(button_frame, text="📂 Abrir Flipbook", command=self.abrir_flipbook, state=tk.DISABLED)
        self.btn_abrir.pack(side=tk.LEFT, padx=5)
        
        self.btn_carpeta = ttk.Button(button_frame, text="📁 Ver Carpeta", command=self.abrir_carpeta, state=tk.DISABLED)
        self.btn_carpeta.pack(side=tk.LEFT, padx=5)
        
        self.btn_instrucciones = ttk.Button(button_frame, text="📋 Instrucciones", command=self.abrir_instrucciones, state=tk.DISABLED)
        self.btn_instrucciones.pack(side=tk.LEFT, padx=5)
    
    def seleccionar_pdf(self):
        pdf = filedialog.askopenfilename(
            title="Selecciona el PDF",
            filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")]
        )
        if pdf:
            self.pdf_path.set(pdf)
            self.status_label.config(text=f"PDF: {os.path.basename(pdf)}", foreground="green")
    
    def generar_flipbook(self):
        if not self.pdf_path.get():
            messagebox.showerror("Error", "Selecciona un PDF primero")
            return
        
        if not os.path.exists(self.pdf_path.get()):
            messagebox.showerror("Error", "El PDF no existe")
            return
        
        self.progress.start()
        self.status_label.config(text="Procesando...", foreground="orange")
        self.root.update()
        
        try:
            nombre = self.nombre_output.get().strip() or "periodico_digital"
            output_dir = os.path.expanduser(f"~/Descargas/{nombre}")
            output_dir = os.path.abspath(output_dir)
            
            if os.path.exists(output_dir):
                output_dir = f"{output_dir}_{datetime.now().strftime('%H%M%S')}"
            
            os.makedirs(output_dir, exist_ok=True)
            pages_dir = os.path.join(output_dir, "pages")
            os.makedirs(pages_dir, exist_ok=True)
            
            self.status_label.config(text="Extrayendo páginas...", foreground="orange")
            self.root.update()
            
            images = convert_from_path(self.pdf_path.get(), dpi=150)
            
            for i, image in enumerate(images, 1):
                page_path = os.path.join(pages_dir, f"page_{i:03d}.png")
                image.thumbnail((1200, 1600), Image.Resampling.LANCZOS)
                image.save(page_path, "PNG", optimize=True)
            
            self.status_label.config(text="Creando HTML...", foreground="orange")
            self.root.update()
            
            html_content = generar_html(nombre, len(images))
            html_path = os.path.join(output_dir, "index.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            instr_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Instrucciones - {nombre}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 30px 20px;
    display: flex;
    justify-content: center;
}}
.container {{
    background: white;
    border-radius: 20px;
    padding: 40px;
    max-width: 700px;
    width: 100%;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}}
h1 {{
    color: #667eea;
    text-align: center;
    margin-bottom: 10px;
    font-size: 1.8em;
}}
.subtitle {{
    text-align: center;
    color: #666;
    margin-bottom: 30px;
}}
.step {{
    display: flex;
    gap: 20px;
    margin-bottom: 25px;
    padding: 20px;
    background: #f7f8fc;
    border-radius: 15px;
    border-left: 5px solid #667eea;
}}
.step-number {{
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    width: 45px;
    height: 45px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5em;
    font-weight: bold;
    flex-shrink: 0;
}}
.step-content h3 {{
    color: #333;
    margin-bottom: 8px;
}}
.step-content p {{
    color: #555;
    line-height: 1.5;
}}
.highlight {{
    background: #fff3cd;
    border-left-color: #ffc107;
    margin-top: 30px;
}}
.highlight .step-number {{
    background: linear-gradient(135deg, #ffc107, #ff9800);
}}
code {{
    background: #e8eaf6;
    padding: 2px 8px;
    border-radius: 5px;
    font-family: monospace;
    color: #5c6bc0;
    font-size: 0.9em;
}}
.footer {{
    text-align: center;
    margin-top: 30px;
    color: #999;
    font-size: 0.85em;
}}
</style>
</head>
<body>
<div class="container">
    <h1>📰 ¡Tu periódico está listo!</h1>
    <p class="subtitle">3 pasos para compartirlo con los padres</p>
    
    <div class="step">
        <div class="step-number">1</div>
        <div class="step-content">
            <h3>Comprime la carpeta</h3>
            <p>Haz <strong>clic derecho</strong> sobre la carpeta <code>{nombre}</code> y selecciona <strong>"Comprimir"</strong> o <strong>"Enviar a → Carpeta ZIP"</strong>.</p>
        </div>
    </div>
    
    <div class="step">
        <div class="step-number">2</div>
        <div class="step-content">
            <h3>Sube a WordPress</h3>
            <p>En el WordPress del colegio: <strong>Medios → Añadir nuevo</strong>. Sube el archivo ZIP o pide ayuda al coordinador TIC.</p>
        </div>
    </div>
    
    <div class="step">
        <div class="step-number">3</div>
        <div class="step-content">
            <h3>Comparte el enlace</h3>
            <p>Copia el enlace generado y envíalo por <strong>email, WhatsApp</strong> o publícalo en la web del colegio.</p>
        </div>
    </div>
    
    <div class="step highlight">
        <div class="step-number">💡</div>
        <div class="step-content">
            <h3>Alternativa rápida y gratis</h3>
            <p>Si prefieres no usar WordPress, arrastra la carpeta a <strong><a href="https://app.netlify.com/drop" target="_blank">Netlify Drop</a></strong> y consigue un enlace en 30 segundos.</p>
        </div>
    </div>
    
    <div class="footer">
        Generado el {datetime.now().strftime('%d/%m/%Y')}
    </div>
</div>
</body>
</html>
"""
            instr_path = os.path.join(output_dir, "INSTRUCCIONES.html")
            with open(instr_path, "w", encoding="utf-8") as f:
                f.write(instr_html)
            self.instrucciones_html = instr_path
            
            self.output_folder = output_dir
            self.flipbook_html = html_path
            
            self.progress.stop()
            self.status_label.config(text=f"✅ ¡Listo! ({len(images)} páginas)", foreground="green")
            self.btn_abrir.config(state=tk.NORMAL)
            self.btn_carpeta.config(state=tk.NORMAL)
            self.btn_instrucciones.config(state=tk.NORMAL)
            
            webbrowser.open(f"file://{html_path}")
            messagebox.showinfo("✅ Éxito", f"Flipbook creado con {len(images)} páginas.\n\nCarpeta: {output_dir}")
            
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text="❌ Error", foreground="red")
            messagebox.showerror("Error", f"Error: {str(e)}")
    
    def abrir_flipbook(self):
        if self.flipbook_html and os.path.exists(self.flipbook_html):
            webbrowser.open(f"file://{self.flipbook_html}")
    
    def abrir_carpeta(self):
        if self.output_folder and os.path.exists(self.output_folder):
            subprocess.Popen(["xdg-open", self.output_folder])
    
    def abrir_instrucciones(self):
        if self.instrucciones_html and os.path.exists(self.instrucciones_html):
            webbrowser.open(f"file://{self.instrucciones_html}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CreadorFlipbook(root)
    root.mainloop()
