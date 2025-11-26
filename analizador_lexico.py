"""
Analizador Léxico - Tokenización de la entrada
"""

from tabulate import tabulate
from grammar import MAPEO_DIVISAS


class AnalizadorLexico:
    """Realiza el análisis léxico de la entrada"""
    
    def __init__(self, entrada):
        self.entrada = entrada
        self.tokens = []
        
    def analizar(self):
        """Tokeniza la entrada y genera tabla de tokens"""
        palabras = self.entrada.strip().split()
        linea = 1
        
        for posicion, palabra in enumerate(palabras, 1):
            if palabra == '$':
                self.tokens.append({
                    'linea': linea,
                    'posicion': posicion,
                    'tipo': 'FIN_CADENA',
                    'valor': '$',
                    'descripcion': 'Marcador de fin de entrada'
                })
            elif palabra.lower() == 'convertir':
                self.tokens.append({
                    'linea': linea,
                    'posicion': posicion,
                    'tipo': 'PALABRA_CLAVE',
                    'valor': palabra,
                    'descripcion': 'Comando de conversión'
                })
            elif self._es_numero(palabra):
                self.tokens.append({
                    'linea': linea,
                    'posicion': posicion,
                    'tipo': 'NUMERO',
                    'valor': palabra,
                    'descripcion': 'Cantidad a convertir'
                })
            elif palabra.lower() == 'a':
                self.tokens.append({
                    'linea': linea,
                    'posicion': posicion,
                    'tipo': 'PREPOSICION',
                    'valor': palabra,
                    'descripcion': 'Indicador de conversión'
                })
            elif palabra in MAPEO_DIVISAS:
                self.tokens.append({
                    'linea': linea,
                    'posicion': posicion,
                    'tipo': 'DIVISA',
                    'valor': palabra,
                    'descripcion': f'Moneda: {MAPEO_DIVISAS[palabra]["nombre"]}'
                })
            else:
                self.tokens.append({
                    'linea': linea,
                    'posicion': posicion,
                    'tipo': 'DESCONOCIDO',
                    'valor': palabra,
                    'descripcion': 'Token no reconocido'
                })
        
        return self.tokens
    
    def _es_numero(self, cadena):
        """Verifica si una cadena es un número"""
        try:
            float(cadena)
            return True
        except ValueError:
            return False
    
    def obtener_tabla_texto(self):
        """Retorna la tabla de análisis léxico como texto"""
        tabla = [[t['linea'], t['posicion'], t['tipo'], t['valor'], t['descripcion']] 
                 for t in self.tokens]
        headers = ['Línea', 'Posición', 'Tipo Token', 'Valor', 'Descripción']
        return tabulate(tabla, headers=headers, tablefmt='grid')