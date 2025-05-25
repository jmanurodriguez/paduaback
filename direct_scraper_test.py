from app.scraper.voley_scraper import VoleyScraper

def test_local_scraper():
    print("Testing Primera División scraper directly...")
    primera_scraper = VoleyScraper("https://metrovoley.com.ar/tournament/188/standings")
    
    print("Getting standings...")
    result = primera_scraper.get_standings()
    
    if result["error"]:
        print(f"Error: {result['error']}")
    else:
        print(f"Success! Found {len(result['standings'])} teams")
        for i, team in enumerate(result["standings"]):
            print(f"{i+1}. {team['equipo']} - {team.get('puntos', 'N/A')} pts")

if __name__ == "__main__":
    test_local_scraper()
