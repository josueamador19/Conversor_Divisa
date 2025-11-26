"""
Analizador Sintáctico - Construcción del árbol sintáctico
"""

from lark import Lark
from grammar import GRAMMAR


class AnalizadorSintactico:
    """Realiza el análisis sintáctico y construye el árbol"""
    
    def __init__(self, entrada):
        self.entrada = entrada
        self.parser = Lark(GRAMMAR, start='start')
        self.arbol = None
        self.error = None
        
    def analizar(self):
        """Parsea la entrada y genera el AST"""
        try:
            self.arbol = self.parser.parse(self.entrada)
            return True
        except Exception as e:
            self.error = str(e)
            return False
    
    def obtener_arbol_texto(self):
        """Retorna el árbol sintáctico como texto"""
        if not self.arbol:
            return "No hay árbol sintáctico disponible"
        return self.arbol.pretty()
        
    def obtener_datos(self):
        """Extrae los datos del árbol para la conversión"""
        if not self.arbol:
            return None
        
        hijos = list(self.arbol.children)
        cantidad = float(hijos[0].value)
        origen = hijos[1].value
        destino = hijos[2].value
        
        return {
            'cantidad': cantidad,
            'origen': origen,
            'destino': destino
        }