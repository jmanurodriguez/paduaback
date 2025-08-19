# BACKEND CASA DE PADUA - GUÍA DE USO

## 🚀 Cómo levantar el backend

### 1. Activar el entorno virtual
```powershell
cd "c:\Users\USUARIO\Desktop\CASA Temporal\casa-de-padua-backend"
.\env\Scripts\Activate.ps1
```

### 2. Levantar el servidor
```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Verificar que funciona
- Abrir: http://127.0.0.1:8000
- Documentación: http://127.0.0.1:8000/docs

## 📋 Endpoints disponibles

### Básquet
- `GET /api/standings/basquet` - Posiciones de básquet (con caché)
- `GET /api/standings/basquet/update` - Forzar actualización de posiciones
- `GET /api/fixtures/basquet` - Próximos partidos de básquet
- `GET /api/fixtures/basquet/update` - Forzar actualización de fixtures

### Voley
**Posiciones:**
- `GET /api/standings/voley/tira-a` - Posiciones Tira A
- `GET /api/standings/voley/tira-b` - Posiciones Tira B  
- `GET /api/standings/voley/primera` - Posiciones Primera División

**Fixtures:**
- `GET /api/fixtures/voley/tira-a` - Próximos partidos Tira A
- `GET /api/fixtures/voley/tira-b` - Próximos partidos Tira B
- `GET /api/fixtures/voley/primera` - Próximos partidos Primera División

## 🔧 Configuración CORS

El backend está configurado para aceptar requests desde:
- localhost:* (cualquier puerto)
- 127.0.0.1:* (cualquier puerto)
- Dominios de producción específicos

## ⚙️ Tecnologías utilizadas

- **FastAPI** - Framework web
- **Uvicorn** - Servidor ASGI
- **Selenium** - Para scraping de páginas dinámicas (voley)
- **BeautifulSoup** - Para scraping de HTML estático (básquet)
- **APScheduler** - Para actualizaciones automáticas
- **ChromeDriver** - Para Selenium (se instala automáticamente)

## 📅 Actualizaciones automáticas

- Las posiciones de básquet se actualizan automáticamente los **lunes y miércoles a las 9:00 AM**
- Los datos de voley se actualizan bajo demanda (cuando se soliciten)
- Todos los datos se mantienen en caché para mejorar el rendimiento

## 🐛 Solución de problemas

### Error "No module named 'app'"
- Asegúrate de estar en la carpeta `casa-de-padua-backend` antes de ejecutar uvicorn
- Usa `python -m uvicorn app.main:app` en lugar de solo `uvicorn app.main:app`

### Error de ChromeDriver
- El ChromeDriver se instala automáticamente con webdriver-manager
- Asegúrate de que Google Chrome esté instalado en el sistema

### Puertos en uso
- Si el puerto 8000 está ocupado, cambia a otro: `--port 8001`
- El frontend React está configurado para usar el puerto 8000 por defecto

## 🔗 Conexión con el frontend

El frontend React (puerto 5173/5174) se conecta automáticamente al backend en el puerto 8000.
Los endpoints están configurados en `src/config/api.js` del proyecto React.

## 📊 Datos de respuesta

Todos los endpoints retornan un formato similar:
```json
{
  "error": null,
  "last_update": "2025-06-03T11:34:48.762115",
  "standings": [...] // o "fixtures": [...]
}
```

- `error`: null si todo está bien, string con el error si algo falló
- `last_update`: timestamp de la última actualización exitosa
- `standings`/`fixtures`: array con los datos solicitados
