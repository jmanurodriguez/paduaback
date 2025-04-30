from bs4 import BeautifulSoup
import requests
from datetime import datetime
import logging
import re
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoleyScraper:
    def __init__(self, url):
        self.url = url
        self.last_update = None
        self.standings = None

    def get_standings(self):
        try:
            # Configurar Selenium en modo headless
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=options)
            driver.get(self.url)
            time.sleep(2)  # Esperar a que cargue el iframe
            iframe = driver.find_element(By.TAG_NAME, 'iframe')
            driver.switch_to.frame(iframe)
            time.sleep(2)  # Esperar a que cargue la tabla dentro del iframe
            table_html = driver.page_source
            driver.quit()
            soup = BeautifulSoup(table_html, 'html.parser')
            table = soup.find('table')
            if not table:
                return {"error": "No se encontró la tabla de posiciones", "last_update": self.last_update, "standings": self.standings}
            standings = self._extract_standings_data(table)
            self.last_update = datetime.now().isoformat()
            self.standings = standings
            return {"error": None, "last_update": self.last_update, "standings": standings}
        except Exception as e:
            logger.error(str(e))
            return {"error": str(e), "last_update": self.last_update, "standings": self.standings}

    def _extract_standings_data(self, table):
        standings = []
        rows = table.find_all('tr')
        if not rows or len(rows) < 2:
            return []
        # La estructura es: N°, escudo, Nombre, P.J, P.G, P.P, P.F, P.C, Puntos, % Victorias
        for row in rows[1:]:
            cols = row.find_all(['td', 'th'])
            if len(cols) < 10:
                continue
            team_data = {
                'posicion': cols[0].text.strip(),
                'equipo': cols[2].text.strip(),  # Nombre del equipo
                'jugados': cols[3].text.strip(),
                'ganados': cols[4].text.strip(),
                'perdidos': cols[5].text.strip(),
                'favor': cols[6].text.strip(),
                'contra': cols[7].text.strip(),
                'puntos': cols[8].text.strip(),
                'porcentaje_victorias': cols[9].text.strip(),
            }
            standings.append(team_data)
        return standings

    def get_cached_standings(self):
        if not self.standings:
            return self.get_standings()
        return {"error": None, "last_update": self.last_update, "standings": self.standings}
