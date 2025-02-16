import requests
from database import Session, Pokemon, engine
from sqlalchemy.exc import SQLAlchemyError

def get_all_pokemon_urls():
    """Get list of all Pokemon URLs including alternate forms"""
    pokemon_urls = []
    url = "https://pokeapi.co/api/v2/pokemon?limit=100000"  # Large limit to get all in one request
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return [(item['name'], item['url']) for item in data['results']]
    return []

def get_pokemon_data(url):
    """Fetch Pokemon data from PokeAPI using full URL"""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def populate_pokemon_table():
    session = Session()
    
    # Get all Pokemon URLs including forms
    pokemon_list = get_all_pokemon_urls()
    total_pokemon = len(pokemon_list)
    print(f"Found {total_pokemon} Pokemon forms in total")
    
    # Fetch all Pokemon
    for name, url in pokemon_list:
        try:
            print(f"Fetching Pokemon {name}...")
            pokemon_data = get_pokemon_data(url)
            
            if pokemon_data:
                # Get types (Pokemon can have 1 or 2 types)
                types = pokemon_data['types']
                type1 = types[0]['type']['name']
                type2 = types[1]['type']['name'] if len(types) > 1 else None
                
                # Get stats
                stats = {stat['stat']['name']: stat['base_stat'] 
                        for stat in pokemon_data['stats']}
                
                # Check if Pokemon exists and update or create new
                existing_pokemon = session.query(Pokemon).filter_by(name=name).first()
                if existing_pokemon:
                    print(f"Updating {name}...")
                    existing_pokemon.type1 = type1
                    existing_pokemon.type2 = type2
                    existing_pokemon.base_hp = stats['hp']
                    existing_pokemon.base_attack = stats['attack']
                    existing_pokemon.base_defense = stats['defense']
                    existing_pokemon.base_sp_attack = stats['special-attack']
                    existing_pokemon.base_sp_defense = stats['special-defense']
                    existing_pokemon.base_speed = stats['speed']
                else:
                    print(f"Adding {name}...")
                    new_pokemon = Pokemon(
                        name=name,
                        type1=type1,
                        type2=type2,
                        base_hp=stats['hp'],
                        base_attack=stats['attack'],
                        base_defense=stats['defense'],
                        base_sp_attack=stats['special-attack'],
                        base_sp_defense=stats['special-defense'],
                        base_speed=stats['speed']
                    )
                    session.add(new_pokemon)
                
                session.commit()
                
        except SQLAlchemyError as e:
            print(f"Database error for Pokemon {name}: {str(e)}")
            session.rollback()
        except Exception as e:
            print(f"Error processing Pokemon {name}: {str(e)}")
            session.rollback()
            
    session.close()

if __name__ == "__main__":
    populate_pokemon_table()
