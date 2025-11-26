"""
Interfaz Gráfica del Conversor de Divisas
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime

from grammar import MAPEO_DIVISAS
from api_client import APITasasCambio
from analizador_lexico import AnalizadorLexico
from analizador_sintactico import AnalizadorSintactico


class ConversorGUI:
    """Interfaz gráfica del conversor de divisas"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Divisas con Analisis Lexico y Sintactico")
        self.root.geometry("1100x900")
        self.root.resizable(True, True)
        
        self.api = APITasasCambio()
        self.figura_grafico = None
        self.canvas_grafico = None
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.crear_interfaz()
        self.cargar_tasas_iniciales()
    
    def crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = tk.Label(main_frame, text="CONVERSOR DE DIVISAS", 
                               font=("Arial", 16, "bold"), fg="#2c3e50")
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        subtitle_label = tk.Label(main_frame, text="Con Análisis Léxico y Sintáctico z", 
                                 font=("Arial", 10), fg="#7f8c8d")
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # ===== CONTENEDOR PARA ENTRADA Y RESULTADO (LADO A LADO) =====
        entrada_resultado_frame = ttk.Frame(main_frame)
        entrada_resultado_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        entrada_resultado_frame.columnconfigure(0, weight=1)
        entrada_resultado_frame.columnconfigure(1, weight=1)
        
        # ===== SECCIÓN DE ENTRADA (IZQUIERDA) =====
        input_frame = ttk.LabelFrame(entrada_resultado_frame, text="Entrada de Conversión", padding="15")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Cantidad
        tk.Label(input_frame, text="Cantidad:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cantidad_entry = ttk.Entry(input_frame, font=("Arial", 12), width=20)
        self.cantidad_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        self.cantidad_entry.insert(0, "100")
        
        # Divisa Origen
        tk.Label(input_frame, text="De:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.divisa_origen = ttk.Combobox(input_frame, font=("Arial", 11), width=30, state="readonly")
        
        # Separar divisas fiat y crypto para mejor organización
        divisas_lista = []
        divisas_lista.append("--- DIVISAS TRADICIONALES ---")
        for key, info in MAPEO_DIVISAS.items():
            if info['tipo'] == 'fiat':
                divisas_lista.append(f"{info['nombre']} ({key})")
        
        divisas_lista.append("--- CRIPTOMONEDAS ---")
        for key, info in MAPEO_DIVISAS.items():
            if info['tipo'] == 'crypto':
                divisas_lista.append(f"{info['nombre']} ({key})")
        
        self.divisa_origen['values'] = divisas_lista
        self.divisa_origen.current(1)  # Selecciona el primer ítem después del separador
        self.divisa_origen.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Prevenir selección de separadores
        self.divisa_origen.bind('<<ComboboxSelected>>', self._validar_seleccion_origen)
        
        # Divisa Destino
        tk.Label(input_frame, text="A:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.divisa_destino = ttk.Combobox(input_frame, font=("Arial", 11), width=30, state="readonly")
        self.divisa_destino['values'] = divisas_lista
        self.divisa_destino.current(2)
        self.divisa_destino.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Prevenir selección de separadores
        self.divisa_destino.bind('<<ComboboxSelected>>', self._validar_seleccion_destino)
        
        # Cadena generada
        tk.Label(input_frame, text="Cadena:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.cadena_label = tk.Label(input_frame, text="", font=("Arial", 10), 
                                     bg="#ecf0f1", relief=tk.SUNKEN, anchor=tk.W, padx=5)
        self.cadena_label.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Botones
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        self.btn_convertir = tk.Button(button_frame, text="CONVERTIR", 
                                       command=self.convertir, bg="#27ae60", fg="white",
                                       font=("Arial", 11, "bold"), padx=20, pady=10)
        self.btn_convertir.pack(side=tk.LEFT, padx=5)
        
        self.btn_actualizar = tk.Button(button_frame, text="Actualizar Tasas", 
                                        command=self.actualizar_tasas, bg="#3498db", fg="white",
                                        font=("Arial", 10), padx=15, pady=10)
        self.btn_actualizar.pack(side=tk.LEFT, padx=5)
        
        self.btn_limpiar = tk.Button(button_frame, text="Limpiar", 
                                     command=self.limpiar, bg="#95a5a6", fg="white",
                                     font=("Arial", 10), padx=15, pady=10)
        self.btn_limpiar.pack(side=tk.LEFT, padx=5)
        
        # ===== RESULTADO (DERECHA) =====
        resultado_frame = ttk.LabelFrame(entrada_resultado_frame, text="Resultado", padding="15")
        resultado_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Contenedor para centrar verticalmente
        resultado_content = ttk.Frame(resultado_frame)
        resultado_content.pack(expand=True, fill=tk.BOTH)
        
        self.resultado_text = tk.Label(resultado_content, text="Ingrese los datos\ny presione Convertir", 
                                       font=("Arial", 16, "bold"), fg="#2c3e50", pady=20,
                                       wraplength=300, justify=tk.CENTER)
        self.resultado_text.pack(expand=True)
        
        self.tasa_label = tk.Label(resultado_content, text="", font=("Arial", 11), fg="#7f8c8d",
                                   wraplength=300, justify=tk.CENTER)
        self.tasa_label.pack()
        
        # Frame para mostrar la conversión inversa
        self.tasa_inversa_label = tk.Label(resultado_content, text="", font=("Arial", 10), 
                                           fg="#95a5a6", wraplength=300, justify=tk.CENTER)
        self.tasa_inversa_label.pack(pady=(5, 0))
        
        # Estado de la API
        self.estado_label = tk.Label(main_frame, text="", font=("Arial", 9), fg="#7f8c8d")
        self.estado_label.grid(row=3, column=0, columnspan=3, pady=5)
        
        # ===== ANÁLISIS Y GRÁFICO (PESTAÑAS) =====
        analisis_frame = ttk.LabelFrame(main_frame, text="Análisis y Visualización", padding="10")
        analisis_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(analisis_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña Léxico
        lexico_frame = ttk.Frame(self.notebook)
        self.notebook.add(lexico_frame, text="Analisis Lexico")
        
        self.lexico_text = scrolledtext.ScrolledText(lexico_frame, wrap=tk.WORD, 
                                                     font=("Courier", 9), height=15)
        self.lexico_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña Sintáctico
        sintactico_frame = ttk.Frame(self.notebook)
        self.notebook.add(sintactico_frame, text="Arbol Sintáctico")
        
        self.sintactico_text = scrolledtext.ScrolledText(sintactico_frame, wrap=tk.WORD, 
                                                         font=("Courier", 9), height=15)
        self.sintactico_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña Gráfico Histórico
        self.grafico_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.grafico_tab, text="Gráfico Histórico")
        
        # Controles del gráfico
        control_grafico_frame = ttk.Frame(self.grafico_tab)
        control_grafico_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(control_grafico_frame, text="Periodo:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.periodo_var = tk.StringVar(value="30")
        periodos = [
            ("7 días", "7"),
            ("30 días", "30"),
            ("90 días", "90"),
            ("180 días", "180"),
            ("365 días", "365")
        ]
        
        for texto, valor in periodos:
            rb = ttk.Radiobutton(control_grafico_frame, text=texto, 
                                variable=self.periodo_var, value=valor)
            rb.pack(side=tk.LEFT, padx=5)
        
        self.btn_graficar = tk.Button(control_grafico_frame, text="Generar Gráfico", 
                                      command=self.generar_grafico, bg="#9b59b6", fg="white",
                                      font=("Arial", 10, "bold"), padx=15, pady=8)
        self.btn_graficar.pack(side=tk.LEFT, padx=10)
        
        # Canvas para el gráfico
        self.grafico_container = ttk.Frame(self.grafico_tab)
        self.grafico_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Mensaje inicial
        self.mensaje_grafico = tk.Label(self.grafico_container, 
                                        text="Seleccione un periodo y presione 'Generar Gráfico'",
                                        font=("Arial", 12), fg="#7f8c8d", pady=30)
        self.mensaje_grafico.pack()
        
        # Configurar peso de filas y columnas para redimensionamiento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Eventos
        self.cantidad_entry.bind('<KeyRelease>', self.actualizar_cadena)
        
        # Actualizar cadena inicial
        self.actualizar_cadena()
    
    def _validar_seleccion_origen(self, event=None):
        """Valida que no se seleccione un separador en el origen"""
        seleccion = self.divisa_origen.get()
        if seleccion.startswith("---"):
            # Si es un separador, volver a la selección anterior
            self.divisa_origen.current(1)
        self.actualizar_cadena()
    
    def _validar_seleccion_destino(self, event=None):
        """Valida que no se seleccione un separador en el destino"""
        seleccion = self.divisa_destino.get()
        if seleccion.startswith("---"):
            # Si es un separador, volver a la selección anterior
            self.divisa_destino.current(2)
        self.actualizar_cadena()
    
    def actualizar_cadena(self, event=None):
        """Actualiza la cadena mostrada basada en la selección"""
        try:
            cantidad = self.cantidad_entry.get()
            origen_sel = self.divisa_origen.get()
            destino_sel = self.divisa_destino.get()
            
            # Extraer clave entre paréntesis
            origen = origen_sel.split('(')[1].split(')')[0] if '(' in origen_sel else ""
            destino = destino_sel.split('(')[1].split(')')[0] if '(' in destino_sel else ""
            
            cadena = f"convertir {cantidad} {origen} a {destino} $"
            self.cadena_label.config(text=cadena)
        except:
            self.cadena_label.config(text="Error generando cadena")
    
    def cargar_tasas_iniciales(self):
        """Carga las tasas iniciales en un hilo separado"""
        def cargar():
            self.estado_label.config(text="Cargando tasas de cambio...", fg="#3498db")
            self.btn_convertir.config(state=tk.DISABLED)
            
            tasas, error = self.api.obtener_tasas()
            
            if error:
                mensaje = f"{error} (usando tasas de respaldo)"
                self.estado_label.config(text=mensaje, fg="#e67e22")
            else:
                fecha = self.api.ultima_actualizacion.strftime('%Y-%m-%d %H:%M:%S')
                self.estado_label.config(text=f"Tasas actualizadas: {fecha}", fg="#27ae60")
            
            self.btn_convertir.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=cargar, daemon=True)
        thread.start()
    
    def actualizar_tasas(self):
        """Actualiza las tasas de cambio"""
        self.cargar_tasas_iniciales()
    
    def convertir(self):
        """Ejecuta el proceso completo de conversión"""
        try:
            # Obtener cadena
            cadena = self.cadena_label.cget("text")
            
            if not cadena or cadena == "Error generando cadena":
                messagebox.showerror("Error", "Cadena de entrada inválida")
                return
            
            # Validar cantidad
            try:
                cantidad = float(self.cantidad_entry.get())
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor a 0")
            except ValueError as e:
                messagebox.showerror("Error", f"Cantidad inválida: {e}")
                return
            
            # PASO 1: Análisis Léxico
            lexico = AnalizadorLexico(cadena)
            tokens = lexico.analizar()
            tabla_lexico = lexico.obtener_tabla_texto()
            
            self.lexico_text.delete(1.0, tk.END)
            self.lexico_text.insert(tk.END, "="*80 + "\n")
            self.lexico_text.insert(tk.END, "ANÁLISIS LÉXICO\n")
            self.lexico_text.insert(tk.END, "="*80 + "\n\n")
            self.lexico_text.insert(tk.END, tabla_lexico)
            
            # PASO 2: Análisis Sintáctico
            sintactico = AnalizadorSintactico(cadena)
            
            if not sintactico.analizar():
                messagebox.showerror("Error Sintáctico", 
                                   f"La entrada no cumple con la gramática:\n{sintactico.error}")
                return
            
            arbol_texto = sintactico.obtener_arbol_texto()
            
            self.sintactico_text.delete(1.0, tk.END)
            self.sintactico_text.insert(tk.END, "="*80 + "\n")
            self.sintactico_text.insert(tk.END, "ÁRBOL SINTÁCTICO ABSTRACTO (AST)\n")
            self.sintactico_text.insert(tk.END, "="*80 + "\n\n")
            self.sintactico_text.insert(tk.END, arbol_texto)
            
            # PASO 3: Conversión
            datos = sintactico.obtener_datos()
            resultado_api = self.api.convertir(datos['cantidad'], datos['origen'], datos['destino'])
            
            # Mostrar resultado
            origen_info = MAPEO_DIVISAS[datos['origen']]
            destino_info = MAPEO_DIVISAS[datos['destino']]
            
            # Formatear resultado según el tipo de moneda
            if destino_info['tipo'] == 'crypto':
                # Para crypto, mostrar más decimales
                resultado_texto = f"{resultado_api['resultado']:.8f} {destino_info['symbol']}"
            else:
                # Para fiat, 2 decimales
                resultado_texto = f"{resultado_api['resultado']:.2f} {destino_info['symbol']}"
            
            self.resultado_text.config(text=resultado_texto, fg="#27ae60")
            
            # Formatear tasa según los tipos
            if origen_info['tipo'] == 'crypto' or destino_info['tipo'] == 'crypto':
                tasa_texto = f"Tasa: 1 {origen_info['symbol']} = {resultado_api['tasa']:.8f} {destino_info['symbol']}"
            else:
                tasa_texto = f"Tasa: 1 {origen_info['symbol']} = {resultado_api['tasa']:.4f} {destino_info['symbol']}"
            
            self.tasa_label.config(text=tasa_texto)
            
            # Mostrar también la tasa inversa
            tasa_inversa = 1 / resultado_api['tasa'] if resultado_api['tasa'] > 0 else 0
            
            if origen_info['tipo'] == 'crypto' or destino_info['tipo'] == 'crypto':
                tasa_inversa_texto = f"Inversa: 1 {destino_info['symbol']} = {tasa_inversa:.8f} {origen_info['symbol']}"
            else:
                tasa_inversa_texto = f"Inversa: 1 {destino_info['symbol']} = {tasa_inversa:.4f} {origen_info['symbol']}"
            
            self.tasa_inversa_label.config(text=tasa_inversa_texto)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la conversión:\n{str(e)}")
    
    def limpiar(self):
        """Limpia todos los campos"""
        self.cantidad_entry.delete(0, tk.END)
        self.cantidad_entry.insert(0, "100")
        self.divisa_origen.current(1)  # Primera divisa fiat
        self.divisa_destino.current(2)  # Segunda divisa fiat
        self.resultado_text.config(text="Ingrese los datos\ny presione Convertir", fg="#2c3e50")
        self.tasa_label.config(text="")
        self.tasa_inversa_label.config(text="")
        self.lexico_text.delete(1.0, tk.END)
        self.sintactico_text.delete(1.0, tk.END)
        self.actualizar_cadena()
        
        # Limpiar el gráfico
        self._limpiar_grafico()
    
    def generar_grafico(self):
        """Genera el gráfico histórico de tasas de cambio"""
        try:
            # Validar que haya divisas seleccionadas
            origen_sel = self.divisa_origen.get()
            destino_sel = self.divisa_destino.get()
            
            if not origen_sel or not destino_sel:
                messagebox.showwarning("Advertencia", "Seleccione las divisas para graficar")
                return
            
            # Extraer claves de divisas
            origen = origen_sel.split('(')[1].split(')')[0] if '(' in origen_sel else ""
            destino = destino_sel.split('(')[1].split(')')[0] if '(' in destino_sel else ""
            
            if not origen or not destino:
                messagebox.showerror("Error", "No se pudieron identificar las divisas")
                return
            
            # Obtener periodo seleccionado
            dias = int(self.periodo_var.get())
            
            # Deshabilitar botón mientras carga
            self.btn_graficar.config(state=tk.DISABLED, text="Cargando datos...")
            
            # Limpiar mensaje inicial si existe
            if hasattr(self, 'mensaje_grafico') and self.mensaje_grafico.winfo_exists():
                self.mensaje_grafico.config(text="Obteniendo datos históricos...")
            
            # Cargar datos en hilo separado
            def cargar_y_graficar():
                # Obtener datos históricos
                datos, error = self.api.obtener_historico(origen, destino, dias)
                
                # Actualizar UI en el hilo principal
                self.root.after(0, lambda: self._mostrar_grafico(datos, error, origen, destino, dias))
            
            thread = threading.Thread(target=cargar_y_graficar, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar gráfico:\n{str(e)}")
            self.btn_graficar.config(state=tk.NORMAL, text="Generar Gráfico")
    
    def _mostrar_grafico(self, datos, error, origen, destino, dias):
        """Muestra el gráfico con los datos históricos"""
        try:
            # Cerrar figura anterior si existe
            if self.figura_grafico is not None:
                plt.close(self.figura_grafico)
                self.figura_grafico = None
            
            # Destruir canvas anterior si existe
            if self.canvas_grafico is not None:
                try:
                    widget = self.canvas_grafico.get_tk_widget()
                    if widget.winfo_exists():
                        widget.destroy()
                except:
                    pass
                self.canvas_grafico = None
            
            # Limpiar todos los widgets del contenedor
            for widget in list(self.grafico_container.winfo_children()):
                try:
                    widget.destroy()
                except:
                    pass
            
            if not datos:
                mensaje_error = tk.Label(self.grafico_container, 
                                        text="No se pudieron obtener datos históricos",
                                        font=("Arial", 11), fg="#e74c3c")
                mensaje_error.pack(pady=30)
                self.btn_graficar.config(state=tk.NORMAL, text="📈 Generar Gráfico")
                return
            
            # Extraer datos para graficar
            fechas = [d['fecha'] for d in datos]
            tasas = [d['tasa'] for d in datos]
            
            # Crear figura de matplotlib más grande
            self.figura_grafico = Figure(figsize=(12, 6), dpi=100)
            ax = self.figura_grafico.add_subplot(111)
            
            # Graficar
            ax.plot(fechas, tasas, marker='o', markersize=4, linewidth=2.5, 
                   color='#3498db', label=f'{origen} → {destino}')
            
            # Configurar gráfico
            origen_info = MAPEO_DIVISAS[origen]
            destino_info = MAPEO_DIVISAS[destino]
            
            ax.set_title(f'Histórico de Tasa de Cambio: {origen_info["nombre"]} → {destino_info["nombre"]}\n'
                        f'Periodo: {dias} días', fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Fecha', fontsize=12, fontweight='bold')
            ax.set_ylabel(f'Tasa ({origen_info["symbol"]} → {destino_info["symbol"]})', 
                         fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(fontsize=11, loc='best')
            
            # Rotar etiquetas de fecha
            self.figura_grafico.autofmt_xdate()
            
            # Ajustar layout
            self.figura_grafico.tight_layout()
            
            # Crear nuevo canvas
            self.canvas_grafico = FigureCanvasTkAgg(self.figura_grafico, master=self.grafico_container)
            self.canvas_grafico.draw()
            
            # Empaquetar el widget
            canvas_widget = self.canvas_grafico.get_tk_widget()
            canvas_widget.pack(fill=tk.BOTH, expand=True)
            
            # Forzar actualización
            self.grafico_container.update()
            
            # Mostrar mensaje si hay error
            if error:
                mensaje_error = tk.Label(self.grafico_container, 
                                        text=f"{error}",
                                        font=("Arial", 9), fg="#e67e22")
                mensaje_error.pack(pady=5)
            
            # Mostrar estadísticas
            tasa_min = min(tasas)
            tasa_max = max(tasas)
            tasa_promedio = sum(tasas) / len(tasas)
            tasa_actual = tasas[-1]
            
            stats_text = (f"Estadísticas del periodo: "
                         f"Mínimo: {tasa_min:.4f} | "
                         f"Máximo: {tasa_max:.4f} | "
                         f"Promedio: {tasa_promedio:.4f} | "
                         f"Actual: {tasa_actual:.4f}")
            
            stats_label = tk.Label(self.grafico_container, text=stats_text,
                                  font=("Arial", 10, "bold"), fg="#2c3e50", bg="#ecf0f1", 
                                  pady=10, padx=10, relief=tk.RIDGE)
            stats_label.pack(pady=10, fill=tk.X, padx=20)
            
            # Cambiar a la pestaña del gráfico
            self.notebook.select(self.grafico_tab)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar gráfico:\n{str(e)}")
            # Limpiar en caso de error
            for widget in list(self.grafico_container.winfo_children()):
                try:
                    widget.destroy()
                except:
                    pass
        
        finally:
            self.btn_graficar.config(state=tk.NORMAL, text="Generar Gráfico")
    
    def _limpiar_grafico(self):
        """Limpia el gráfico y restaura el mensaje inicial"""
        try:
            # Cerrar figura anterior si existe
            if self.figura_grafico is not None:
                plt.close(self.figura_grafico)
                self.figura_grafico = None
            
            # Destruir canvas anterior si existe
            if self.canvas_grafico is not None:
                try:
                    widget = self.canvas_grafico.get_tk_widget()
                    if widget.winfo_exists():
                        widget.destroy()
                except:
                    pass
                self.canvas_grafico = None
            
            # Limpiar todos los widgets del contenedor
            for widget in list(self.grafico_container.winfo_children()):
                try:
                    widget.destroy()
                except:
                    pass
            
            # Restaurar mensaje inicial
            self.mensaje_grafico = tk.Label(self.grafico_container, 
                                            text="Seleccione un periodo y presione 'Generar Gráfico'",
                                            font=("Arial", 12), fg="#7f8c8d", pady=30)
            self.mensaje_grafico.pack()
            
            # Resetear periodo a 30 días
            self.periodo_var.set("30")
            
        except Exception as e:
            print(f"Error al limpiar gráfico: {e}")