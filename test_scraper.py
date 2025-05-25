from app.scraper.voley_scraper import VoleyScraper
scraperPrimera = VoleyScraper('https://metrovoley.com.ar/tournament/188/standings')
result = scraperPrimera.get_standings()
print(f'Error: {result["error"]}')
print(f'Standings: {result["standings"]}')
