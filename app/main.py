from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from .scraper.basketball_scraper import BasketballScraper
from .scraper.voley_scraper import VoleyScraper
import logging

# Configurar el logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configurar CORS de manera más específica
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "https://casa-de-padua.web.app",  # Dominio de Firebase
        "https://casa-de-padua.firebaseapp.com",  # Dominio alternativo de Firebase
        "https://casa-de-padua-d3552.web.app",
        "https://casa-de-padua-d3552.firebaseapp.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],
)

# Instanciar el scraper
basketball_scraper = BasketballScraper()

# Instanciar scrapers de voley para cada tira
voley_tira_a_scraper = VoleyScraper("https://metrovoley.com.ar/tournament/75/standings?group=482")
voley_tira_b_scraper = VoleyScraper("https://metrovoley.com.ar/tournament/129/standings?group=497")

# Función que ejecutará el scraper y registrará cuándo se realizó la actualización
def update_basketball_data():
    logger.info("Ejecutando actualización programada del scraper de baloncesto")
    result = basketball_scraper.get_standings()
    logger.info(f"Actualización completada. Resultado: {result['error'] if 'error' in result and result['error'] else 'Exitosa'}")
    return result

# Configurar el scheduler para actualizar los datos los lunes y miércoles a las 9:00 AM
scheduler = BackgroundScheduler()
scheduler.add_job(
    update_basketball_data, 
    'cron', 
    day_of_week='mon,wed', 
    hour=9, 
    minute=0,
    misfire_grace_time=3600,  # Permitir hasta 1 hora de retraso si el servidor estaba apagado
    id='basketball_update_job'
)

# Solo iniciar el scheduler en producción, no durante el desarrollo/pruebas
import os
if os.environ.get('ENVIRONMENT') != 'development':
    scheduler.start()
    logger.info("Scheduler iniciado: Actualizaciones programadas para lunes y miércoles a las 9:00 AM")
else:
    logger.info("Entorno de desarrollo detectado: Scheduler no iniciado")

@app.get("/")
async def root():
    return {"message": "API de CASA de Padua"}

@app.get("/api/standings/basquet")
async def get_basketball_standings():
    """
    Obtiene la tabla de posiciones de básquet.
    Retorna los datos en caché si están disponibles, o realiza un nuevo scraping si es necesario.
    """
    return basketball_scraper.get_cached_standings()

@app.get("/api/standings/basquet/update")
async def update_basketball_standings():
    """
    Fuerza una actualización de los datos de la tabla de posiciones de básquet
    """
    return update_basketball_data()

@app.get("/api/standings/voley/tira-a")
async def get_voley_tira_a_standings():
    """
    Obtiene la tabla de posiciones de voley Tira A.
    """
    return voley_tira_a_scraper.get_cached_standings()

@app.get("/api/standings/voley/tira-b")
async def get_voley_tira_b_standings():
    """
    Obtiene la tabla de posiciones de voley Tira B.
    """
    return voley_tira_b_scraper.get_cached_standings()

# Nuevos endpoints para obtener fixtures
@app.get("/api/fixtures/basquet")
async def get_basketball_fixtures():
    """
    Obtiene los próximos partidos del fixture de básquet.
    """
    return basketball_scraper.get_cached_fixtures()

@app.get("/api/fixtures/basquet/update")
async def update_basketball_fixtures():
    """
    Fuerza una actualización de los datos del fixture de básquet
    """
    return basketball_scraper.get_fixtures()

@app.get("/api/fixtures/voley/tira-a")
async def get_voley_tira_a_fixtures():
    """
    Obtiene los próximos partidos del fixture de voley Tira A.
    """
    return voley_tira_a_scraper.get_cached_fixtures()

@app.get("/api/fixtures/voley/tira-b")
async def get_voley_tira_b_fixtures():
    """
    Obtiene los próximos partidos del fixture de voley Tira B.
    """
    return voley_tira_b_scraper.get_cached_fixtures()

# Event handler para limpiar el scheduler cuando se apaga la aplicación
@app.on_event("shutdown")
def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler detenido correctamente")