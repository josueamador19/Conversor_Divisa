"""
Definición de la gramática para el conversor de divisas
"""

GRAMMAR = """
    start: "convertir" NUMERO DIVISA "a" DIVISA "$"
    
    DIVISA: "DolarEstadounidense" 
          | "LempiraHondureño" 
          | "Euro" 
          | "LibraEsterlina"
          | "Quetzal"
          | "Bitcoin"
          | "Ethereum"
          | "Tether"
          | "BinanceCoin"
          | "Cardano"
          | "Ripple"
          | "Solana"
          | "Dogecoin"
    
    NUMERO: /[0-9]+\.?[0-9]*/
    
    %import common.WS
    %ignore WS
"""

# Mapeo de divisas a códigos ISO y símbolos
MAPEO_DIVISAS = {
    # Divisas tradicionales
    'DolarEstadounidense': {'code': 'USD', 'symbol': 'USD', 'nombre': 'Dólar Estadounidense', 'tipo': 'fiat'},
    'LempiraHondureño': {'code': 'HNL', 'symbol': 'L', 'nombre': 'Lempira Hondureño', 'tipo': 'fiat'},
    'Euro': {'code': 'EUR', 'symbol': '€', 'nombre': 'Euro', 'tipo': 'fiat'},
    'LibraEsterlina': {'code': 'GBP', 'symbol': '£', 'nombre': 'Libra Esterlina', 'tipo': 'fiat'},
    'Quetzal': {'code': 'GTQ', 'symbol': 'Q', 'nombre': 'Quetzal Guatemalteco', 'tipo': 'fiat'},
    
    # Criptomonedas
    'Bitcoin': {'code': 'BTC', 'symbol': '₿', 'nombre': 'Bitcoin', 'tipo': 'crypto'},
    'Ethereum': {'code': 'ETH', 'symbol': 'Ξ', 'nombre': 'Ethereum', 'tipo': 'crypto'},
    'Tether': {'code': 'USDT', 'symbol': '₮', 'nombre': 'Tether', 'tipo': 'crypto'},
    'BinanceCoin': {'code': 'BNB', 'symbol': 'BNB', 'nombre': 'Binance Coin', 'tipo': 'crypto'},
    'Cardano': {'code': 'ADA', 'symbol': '₳', 'nombre': 'Cardano', 'tipo': 'crypto'},
    'Ripple': {'code': 'XRP', 'symbol': 'XRP', 'nombre': 'Ripple', 'tipo': 'crypto'},
    'Solana': {'code': 'SOL', 'symbol': 'SOL', 'nombre': 'Solana', 'tipo': 'crypto'},
    'Dogecoin': {'code': 'DOGE', 'symbol': 'Ð', 'nombre': 'Dogecoin', 'tipo': 'crypto'}
}