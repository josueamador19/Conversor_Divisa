"""
Cliente API para obtener tasas de cambio en tiempo real
"""

import requests
from datetime import datetime, timedelta
from grammar import MAPEO_DIVISAS


class APITasasCambio:
    """Cliente para obtener tasas de cambio en tiempo real"""
    
    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"
        self.base_url_historico = "https://api.exchangerate.host"
        self.base_url_crypto = "https://api.coingecko.com/api/v3"
        self.tasas_cache = None
        self.tasas_crypto_cache = None
        self.ultima_actualizacion = None
        
        # Mapeo de códigos a IDs de CoinGecko
        self.crypto_ids = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDT': 'tether',
            'BNB': 'binancecoin',
            'ADA': 'cardano',
            'XRP': 'ripple',
            'SOL': 'solana',
            'DOGE': 'dogecoin'
        }
    
    def obtener_tasas(self, moneda_base='USD'):
        """Obtiene las tasas de cambio desde la API"""
        try:
            url = f"{self.base_url}{moneda_base}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.tasas_cache = data['rates']
                self.ultima_actualizacion = datetime.now()
                
                # Obtener tasas de criptomonedas
                self._obtener_tasas_crypto()
                
                return self.tasas_cache, None
            else:
                return None, f"Error al obtener tasas: Status {response.status_code}"
        except requests.RequestException as e:
            return self._tasas_respaldo(), f"Error de conexión: {e}"
        except Exception as e:
            return self._tasas_respaldo(), f"Error inesperado: {e}"
    
    def _obtener_tasas_crypto(self):
        """Obtiene las tasas de criptomonedas desde CoinGecko"""
        try:
            # Obtener precios en USD
            ids = ','.join(self.crypto_ids.values())
            url = f"{self.base_url_crypto}/simple/price"
            params = {
                'ids': ids,
                'vs_currencies': 'usd'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Convertir a formato de tasas (cantidad de USD por 1 unidad de crypto)
                if not self.tasas_crypto_cache:
                    self.tasas_crypto_cache = {}
                
                for code, coin_id in self.crypto_ids.items():
                    if coin_id in data and 'usd' in data[coin_id]:
                        # Precio en USD por unidad de crypto
                        self.tasas_crypto_cache[code] = data[coin_id]['usd']
        except:
            # Si falla, usar tasas de respaldo
            self.tasas_crypto_cache = self._tasas_crypto_respaldo()
    
    def _tasas_respaldo(self):
        """Tasas de respaldo en caso de fallo de la API"""
        return {
            'USD': 1.0, # Dolar EstadoUnidense
            'HNL': 26.23, # Lempira Hondureño
            'EUR': 0.86, #Euro
            'GBP': 0.79, # Libra Esterlina
            'GTQ': 7.80 # Quetzal Guatemalteco
        }
    
    def _tasas_crypto_respaldo(self):
        """Tasas de criptomonedas de respaldo"""
        return {
            'BTC': 45000.0, #Bitcoin
            'ETH': 2500.0, # Ethereum
            'USDT': 1.0,  #Tether 
            'BNB': 320.0, # BinanceCoin
            'ADA': 0.45, # Cardano
            'XRP': 0.55, #Ripple
            'SOL': 100.0, # Solana
            'DOGE': 0.08  #DogeCoin
        }
    
    def convertir(self, cantidad, desde, hacia):
        """Convierte una cantidad de una divisa a otra"""
        if not self.tasas_cache:
            self.obtener_tasas()
        
        if not self.tasas_crypto_cache:
            self.tasas_crypto_cache = self._tasas_crypto_respaldo()
        
        codigo_desde = MAPEO_DIVISAS[desde]['code']
        codigo_hacia = MAPEO_DIVISAS[hacia]['code']
        tipo_desde = MAPEO_DIVISAS[desde]['tipo']
        tipo_hacia = MAPEO_DIVISAS[hacia]['tipo']
        
        # Determinar la cantidad en USD primero
        if tipo_desde == 'crypto':
            # De crypto a USD
            precio_usd = self.tasas_crypto_cache.get(codigo_desde, 0)
            cantidad_usd = cantidad * precio_usd
        elif codigo_desde != 'USD':
            # De fiat (no USD) a USD
            cantidad_usd = cantidad / self.tasas_cache[codigo_desde]
        else:
            # Ya está en USD
            cantidad_usd = cantidad
        
        # Convertir de USD a la moneda destino
        if tipo_hacia == 'crypto':
            # De USD a crypto
            precio_usd = self.tasas_crypto_cache.get(codigo_hacia, 1)
            resultado = cantidad_usd / precio_usd if precio_usd > 0 else 0
        elif codigo_hacia != 'USD':
            # De USD a fiat (no USD)
            resultado = cantidad_usd * self.tasas_cache[codigo_hacia]
        else:
            # Ya está en USD
            resultado = cantidad_usd
        
        # Calcular tasa directa
        if tipo_desde == 'crypto' and tipo_hacia == 'crypto':
            # Crypto a Crypto
            precio_desde = self.tasas_crypto_cache.get(codigo_desde, 1)
            precio_hacia = self.tasas_crypto_cache.get(codigo_hacia, 1)
            tasa_directa = precio_desde / precio_hacia if precio_hacia > 0 else 0
        elif tipo_desde == 'crypto':
            # Crypto a Fiat
            precio_crypto = self.tasas_crypto_cache.get(codigo_desde, 0)
            if codigo_hacia == 'USD':
                tasa_directa = precio_crypto
            else:
                tasa_directa = precio_crypto * self.tasas_cache[codigo_hacia]
        elif tipo_hacia == 'crypto':
            # Fiat a Crypto
            precio_crypto = self.tasas_crypto_cache.get(codigo_hacia, 1)
            if codigo_desde == 'USD':
                tasa_directa = 1 / precio_crypto if precio_crypto > 0 else 0
            else:
                tasa_usd_desde = 1 / self.tasas_cache[codigo_desde]
                tasa_directa = tasa_usd_desde / precio_crypto if precio_crypto > 0 else 0
        else:
            # Fiat a Fiat
            tasa_directa = self.tasas_cache[codigo_hacia] / self.tasas_cache[codigo_desde]
        
        return {
            'resultado': resultado,
            'tasa': tasa_directa,
            'tasas_usadas': {
                codigo_desde: self.tasas_crypto_cache.get(codigo_desde) if tipo_desde == 'crypto' else self.tasas_cache.get(codigo_desde, 1),
                codigo_hacia: self.tasas_crypto_cache.get(codigo_hacia) if tipo_hacia == 'crypto' else self.tasas_cache.get(codigo_hacia, 1)
            }
        }
    
    def obtener_historico(self, desde, hacia, dias=30):
        """Obtiene el histórico de tasas de cambio para graficar"""
        codigo_desde = MAPEO_DIVISAS[desde]['code']
        codigo_hacia = MAPEO_DIVISAS[hacia]['code']
        
        datos_historicos = []
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=dias)
        
        try:
            # Usar API de exchangerate.host para datos históricos
            url = f"{self.base_url_historico}/timeseries"
            params = {
                'start_date': fecha_inicio.strftime('%Y-%m-%d'),
                'end_date': fecha_fin.strftime('%Y-%m-%d'),
                'base': codigo_desde,
                'symbols': codigo_hacia
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'rates' in data:
                    for fecha_str, tasas in sorted(data['rates'].items()):
                        if codigo_hacia in tasas:
                            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
                            datos_historicos.append({
                                'fecha': fecha_obj,
                                'fecha_str': fecha_str,
                                'tasa': tasas[codigo_hacia]
                            })
                    return datos_historicos, None
            
            # Si falla, generar datos simulados
            return self._generar_datos_simulados(dias), "Usando datos simulados (API no disponible)"
            
        except Exception as e:
            return self._generar_datos_simulados(dias), f"Error: {str(e)}"
    
    def _generar_datos_simulados(self, dias):
        """Genera datos históricos simulados con variación realista"""
        import random
        
        datos = []
        fecha_actual = datetime.now()
        
        # Obtener tasa base actual
        if not self.tasas_cache:
            self.obtener_tasas()
        
        # Generar variaciones aleatorias realistas
        tasa_base = 1.0
        for i in range(dias, -1, -1):
            fecha = fecha_actual - timedelta(days=i)
            # Variación aleatoria de ±2%
            variacion = random.uniform(-0.02, 0.02)
            tasa_base = tasa_base * (1 + variacion)
            
            datos.append({
                'fecha': fecha,
                'fecha_str': fecha.strftime('%Y-%m-%d'),
                'tasa': tasa_base
            })
        
        return datos