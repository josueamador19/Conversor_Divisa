# Conversor de Divisas con Análisis Léxico y Sintáctico

Sistema de conversión de divisas en tiempo real con análisis léxico y sintáctico completo.

## 🚀 Instalación

### 1. Clonar o descargar el proyecto


### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Activar
venv\Scripts\activate



### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```


## 🛠️ Dependencias

- **lark-parser**: Parser de gramáticas
- **tabulate**: Generación de tablas formateadas
- **requests**: Cliente HTTP para API

## 📝 Notas

- Las tasas de cambio se obtienen en tiempo real de la API de ExchangeRate
- Si la API no está disponible, se utilizan tasas de respaldo
- Todos los análisis (léxico y sintáctico) se muestran en tiempo real en la interfaz
