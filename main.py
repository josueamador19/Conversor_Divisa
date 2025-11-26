"""
Conversor de Divisas con Análisis Léxico y Sintáctico
Archivo Principal - Punto de entrada de la aplicación
Autor: Sistema de Traducción
Descripción: Traductor con interfaz gráfica para conversión de divisas en tiempo real
"""

import sys
import tkinter as tk
from gui import ConversorGUI


def main():
    """Función principal que inicia la aplicación"""
    root = tk.Tk()
    app = ConversorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma interrumpido .")
        sys.exit(0)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)