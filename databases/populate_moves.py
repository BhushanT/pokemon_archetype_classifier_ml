import requests
from database import Session, Move, engine
from sqlalchemy.exc import SQLAlchemyError

def get_all_move_urls():
    """Get list of all move URLs"""
    url = "https://pokeapi.co/api/v2/move?limit=2000"  # Large limit to get all moves
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Filter moves after ID 826
        return [(item['name'], item['url']) for item in data['results'] if int(item['url'].split('/')[-2]) > 826]
    return []

def get_move_data(url):
    """Fetch move data from PokeAPI using full URL"""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def populate_moves_table():
    session = Session()
    
    # Define hazard moves
    hazard_moves = {"stealth-rock", "sticky-web", "spikes", "toxic-spikes", "stone-axe", "ceaseless-edge"}
    
    # Get all move URLs
    move_list = get_all_move_urls()
    total_moves = len(move_list)
    print(f"Found {total_moves} moves in total")
    
    for name, url in move_list:
        try:
            print(f"Fetching move {name}...")
            move_data = get_move_data(url)
            
            if move_data:
                # Get healing value safely, default to 0 if meta doesn't exist
                healing = move_data.get('meta', {}).get('healing', 0) if move_data.get('meta') else 0
                
                # Create or update move
                existing_move = session.query(Move).filter_by(name=name).first()
                
                move_dict = {
                    'name': name,
                    'type': move_data['type']['name'],
                    'category': move_data['damage_class']['name'],
                    'power': move_data['power'],
                    'accuracy': move_data['accuracy'],
                    'pp': move_data['pp'],
                    'is_recovery': healing > 0,
                    'is_hazard': name.replace(' ', '-').lower() in hazard_moves
                }
                
                if existing_move:
                    print(f"Updating {name}...")
                    for key, value in move_dict.items():
                        setattr(existing_move, key, value)
                else:
                    print(f"Adding {name}...")
                    new_move = Move(**move_dict)
                    session.add(new_move)
                
                session.commit()
                
        except SQLAlchemyError as e:
            print(f"Database error for move {name}: {str(e)}")
            session.rollback()
        except Exception as e:
            print(f"Error processing move {name}: {str(e)}")
            session.rollback()
            
    session.close()

if __name__ == "__main__":
    populate_moves_table()