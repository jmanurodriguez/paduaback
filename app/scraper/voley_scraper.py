from bs4 import BeautifulSoup
import requests
from datetime import datetime
from typing import Dict
import logging
import re
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoleyScraper:
    def __init__(self, url):
        self.url = url
        self.last_update = None
        self.standings = None
        self.fixtures = None
        self.fixtures_update = None

    def get_standings(self):
        try:            # Configurar Selenium en modo headless
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(self.url)
            time.sleep(2)  # Esperar a que cargue la página
            
            # Intentar extraer datos directamente de la página principal primero
            logger.info("Intentando extraer tabla de posiciones directamente de la página principal")
            table_html = driver.page_source
            soup = BeautifulSoup(table_html, 'html.parser')
            
            # Buscar tabla de posiciones en la página principal
            table = self._find_standings_table(soup)
            
            if not table:
                # Si no encontramos tabla en la página principal, intentamos con iframe si existe
                logger.info("No se encontró tabla en la página principal, buscando en iframes")
                try:
                    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                    logger.info(f"Se encontraron {len(iframes)} iframes")
                    
                    for i, iframe in enumerate(iframes):
                        try:
                            logger.info(f"Analizando iframe {i+1}/{len(iframes)}")
                            driver.switch_to.frame(iframe)
                            iframe_html = driver.page_source
                            iframe_soup = BeautifulSoup(iframe_html, 'html.parser')
                            iframe_table = self._find_standings_table(iframe_soup)
                            
                            if iframe_table:
                                logger.info(f"Tabla encontrada en iframe {i+1}")
                                table = iframe_table
                                break
                            
                            # Volver al contenido principal para revisar el siguiente iframe
                            driver.switch_to.default_content()
                        except Exception as e:
                            logger.warning(f"Error al procesar iframe {i+1}: {e}")
                            driver.switch_to.default_content()
                            continue
                except NoSuchElementException:
                    logger.warning("No se encontraron iframes en la página")
            
            driver.quit()
            
            if not table:
                return {"error": "No se encontró la tabla de posiciones", "last_update": self.last_update, "standings": self.standings}
                
            standings = self._extract_standings_data(table)
            self.last_update = datetime.now().isoformat()
            self.standings = standings
            return {"error": None, "last_update": self.last_update, "standings": standings}
        except Exception as e:
            logger.error(f"Error en get_standings: {str(e)}")
            if 'driver' in locals():
                driver.quit()
            return {"error": str(e), "last_update": self.last_update, "standings": self.standings}

    def _find_standings_table(self, soup):
        """Busca la tabla de posiciones en el HTML"""
        # Intenta diferentes estrategias para encontrar la tabla
        
        # 1. Buscar tablas con clases o IDs relacionados con posiciones
        for table in soup.find_all('table'):
            class_attr = table.get('class', '')
            if isinstance(class_attr, list):
                class_attr = ' '.join(class_attr)
                
            id_attr = table.get('id', '')
            table_attrs = f"{class_attr} {id_attr}".lower()
            
            if any(keyword in table_attrs for keyword in ['clasific', 'standing', 'posicion', 'tabla', 'torneo', 'ranking']):
                logger.info(f"Tabla encontrada por clase/ID: {table_attrs}")
                return table
        
        # 2. Buscar encabezados típicos de tablas de posiciones
        for table in soup.find_all('table'):
            headers = []
            header_row = table.find('tr')
            if header_row:
                headers = [th.text.strip().lower() for th in header_row.find_all(['th', 'td'], limit=10)]
                header_text = ' '.join(headers)
                
                if any(keyword in header_text for keyword in ['pos', 'equipo', 'pts', 'pj', 'pg', 'pp']):
                    logger.info(f"Tabla encontrada por encabezados: {header_text[:50]}")
                    return table
        
        # 3. Buscar divs que contengan tablas
        for div in soup.find_all('div', class_=lambda c: c and any(keyword in c.lower() for keyword in ['tabla', 'posiciones', 'standings'])):
            table = div.find('table')
            if table:
                logger.info(f"Tabla encontrada dentro de div: {div.get('class', '')}")
                return table
        
        return None

    def _extract_standings_data(self, table):
        standings = []
        rows = table.find_all('tr')
        if not rows or len(rows) < 2:
            return []
        
        # Determinar si la primera fila es encabezado
        has_header = len(rows[0].find_all('th')) > 0 or 'header' in str(rows[0]).lower()
        data_rows = rows[1:] if has_header else rows
        
        # Buscar patrones comunes en las columnas
        for row in data_rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) < 3:  # Necesitamos al menos posición, equipo y algunos datos
                continue
            
            # Determinar la estructura de la tabla
            # Normalmente: posición, equipo, PJ, PG, PP, y posiblemente puntos, sets, etc.
            try:
                # Intentar extraer los datos independientemente de la estructura exacta
                position = cols[0].text.strip()
                
                # El nombre del equipo suele estar en la segunda o tercera columna
                # (a veces hay columna de escudo/logo)
                team_name = ""
                if len(cols) > 2 and cols[2].text.strip() and not cols[2].text.strip().isdigit():
                    team_name = cols[2].text.strip()  # Columna 3 si hay logo en columna 2
                else:
                    team_name = cols[1].text.strip()  # Columna 2 normalmente
                
                # Tomar los datos numéricos de las siguientes columnas
                numeric_cols = []
                for i in range(3, min(len(cols), 10)):
                    numeric_cols.append(cols[i].text.strip())
                
                # Asignar los datos según la cantidad de columnas disponibles
                team_data = {
                    'posicion': position,
                    'equipo': team_name,
                }
                
                # Asignar datos numéricos según cantidad disponible
                if len(numeric_cols) >= 1: team_data['jugados'] = numeric_cols[0]
                if len(numeric_cols) >= 2: team_data['ganados'] = numeric_cols[1]
                if len(numeric_cols) >= 3: team_data['perdidos'] = numeric_cols[2]
                if len(numeric_cols) >= 4: team_data['favor'] = numeric_cols[3]
                if len(numeric_cols) >= 5: team_data['contra'] = numeric_cols[4]
                if len(numeric_cols) >= 6: team_data['puntos'] = numeric_cols[5]
                
                standings.append(team_data)
            except Exception as e:
                logger.warning(f"Error al procesar fila: {e}")
                continue
                
        return standings

    def get_cached_standings(self):
        if not self.standings:
            return self.get_standings()
        return {"error": None, "last_update": self.last_update, "standings": self.standings}

    def get_fixtures(self) -> Dict:
        """Obtiene los próximos partidos del fixture"""
        try:
            fixture_url = self.url.replace("standings", "schedule")
            logger.info(f"Obteniendo fixture de: {fixture_url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Referer': 'https://metrovoley.com.ar/'
            }
            
            response = requests.get(fixture_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar elementos de partido
            fixtures_data = []
            
            # Buscar todos los divs que puedan contener información de partidos
            schedule_section = soup.select_one('.itinerary-container')
            if not schedule_section:
                schedule_section = soup
                
            match_elements = schedule_section.select('.itinerary-match')
            
            if not match_elements:
                # Buscar más genéricamente
                match_elements = schedule_section.select('div[class*="match"]')
            
            for match_elem in match_elements:
                try:
                    # Extraer equipos (local y visitante)
                    local_team = None 
                    visitor_team = None
                    
                    team_elements = match_elem.select('.team-name')
                    if len(team_elements) >= 2:
                        local_team = team_elements[0].text.strip()
                        visitor_team = team_elements[1].text.strip()
                    else:
                        # Intentar buscar de otra manera
                        teams_container = match_elem.select_one('.teams-container')
                        if teams_container:
                            teams = teams_container.select('.team')
                            if len(teams) >= 2:
                                local_team = teams[0].text.strip()
                                visitor_team = teams[1].text.strip()
                    
                    # Si no encontramos los nombres de los equipos, saltar
                    if not local_team or not visitor_team:
                        continue
                    
                    # Extraer fecha y hora
                    match_date = ""
                    match_time = ""
                    
                    # Buscar fecha y hora directamente
                    date_elem = match_elem.select_one('.date')
                    if date_elem:
                        match_date = date_elem.text.strip()
                    
                    time_elem = match_elem.select_one('.hour')
                    if time_elem:
                        match_time = time_elem.text.strip()
                    
                    # Si no encontramos elementos específicos, buscar texto que se parezca a fechas/horas
                    if not match_date or not match_time:
                        for text in match_elem.stripped_strings:
                            # Buscar patrones de fecha (dd/mm/yyyy o dd-mm-yyyy)
                            if not match_date and re.search(r'\d{1,2}[/-]\d{1,2}([/-]\d{2,4})?', text):
                                match_date = text.strip()
                            
                            # Buscar patrones de hora (hh:mm)
                            elif not match_time and re.search(r'\d{1,2}:\d{2}', text):
                                match_time = text.strip()
                    
                    # Determinar si CASA es local o visitante
                    is_casa_local = 'casa' in local_team.lower() or 'padua' in local_team.lower()
                    
                    # Verificar estado del partido
                    match_status = ""
                    status_elem = match_elem.select_one('.match-status')
                    if status_elem:
                        match_status = status_elem.text.strip().lower()
                    
                    # Solo incluir partidos programados/pendientes
                    is_pending = True
                    if match_status and ('finalizado' in match_status or 'jugado' in match_status or 'terminado' in match_status):
                        is_pending = False
                    
                    if is_pending:
                        fixtures_data.append({
                            "local": local_team,
                            "visitante": visitor_team,
                            "fecha": match_date,
                            "hora": match_time,
                            "es_casa_local": is_casa_local
                        })
                
                except Exception as e:
                    logger.error(f"Error procesando partido: {str(e)}")
                    continue
            
            # Si encontramos datos, guardarlos en caché
            if fixtures_data:
                self.fixtures = fixtures_data
                self.fixtures_update = datetime.now().isoformat()
            
            return {
                "error": None if fixtures_data else "No se encontraron próximos partidos",
                "last_update": self.fixtures_update,
                "fixtures": fixtures_data
            }
                
        except Exception as e:
            error_msg = f"Error obteniendo fixture: {str(e)}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "last_update": self.fixtures_update,
                "fixtures": self.fixtures
            }
    
    def get_cached_fixtures(self) -> Dict:
        """Retorna los últimos datos de fixtures obtenidos sin hacer una nueva petición"""
        if not self.fixtures:
            return self.get_fixtures()
        return {
            "error": None,
            "last_update": self.fixtures_update,
            "fixtures": self.fixtures
        }
