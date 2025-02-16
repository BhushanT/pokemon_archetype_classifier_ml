import requests
from database import Session, Item

def fetch_items():
    # PokeAPI endpoint for items
    url = "https://pokeapi.co/api/v2/item?limit=2000"  # Large limit to get all items
    
    # Defensive items list
    defensive_items = [
        "heavy-duty-boots",
        "rocky-helmet",
        "shed-shell",
        "leftovers",
        "black-sludge",
        "eviolite"
    ]
    
    try:
        # Get the list of all items
        response = requests.get(url)
        response.raise_for_status()
        items_data = response.json()
        
        # Create a database session
        session = Session()
        
        # Process each item
        for item in items_data['results']:
            item_name = item['name']
            
            # Create new item entry
            new_item = Item(
                item_name=item_name,
                is_defensive=(item_name in defensive_items)
            )
            
            session.add(new_item)
        
        # Commit all changes
        session.commit()
        print("Successfully populated items table!")
        
    except requests.RequestException as e:
        print(f"Error fetching data from PokeAPI: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    fetch_items()
