from app.scraper.voley_scraper import VoleyScraper
import json

def main():
    print("Iniciando test de VoleyScraper para Primera División...")
    
    # Crear instancia con la URL correcta
    primera_scraper = VoleyScraper("https://metrovoley.com.ar/tournament/188/standings")
    
    print("Obteniendo tabla de posiciones...")
    standings_result = primera_scraper.get_standings()
    print(f"Resultado tabla: {'Error: ' + standings_result['error'] if standings_result['error'] else 'OK'}")
    print(f"Datos obtenidos: {len(standings_result['standings']) if standings_result['standings'] else 0} equipos")
    print("Resultado completo:")
    print(json.dumps(standings_result, indent=2, default=str))
    
    print("\nObteniendo fixture...")
    fixtures_result = primera_scraper.get_fixtures()
    print(f"Resultado fixture: {'Error: ' + fixtures_result['error'] if fixtures_result['error'] else 'OK'}")
    print(f"Datos obtenidos: {len(fixtures_result['fixtures']) if fixtures_result['fixtures'] else 0} partidos")
    print("Resultado completo:")
    print(json.dumps(fixtures_result, indent=2, default=str))

if __name__ == "__main__":
    main()
