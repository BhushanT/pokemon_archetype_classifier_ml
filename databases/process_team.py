from database import Session, Team, Pokemon, TeamPokemon, Move, Item
import re

def calculate_stat(base, ev, iv=31, level=100, nature_mod=1.0):
    return int(((2 * base + iv + (ev/4)) * level / 100 + 5) * nature_mod)

def calculate_hp(base, ev, iv=31, level=100):
    return int((2 * base + iv + (ev/4)) * level / 100 + level + 10)

# Nature modifiers table
NATURE_MODIFIERS = {
    'Lonely': {'increased': 'attack', 'decreased': 'defense'},
    'Brave': {'increased': 'attack', 'decreased': 'speed'},
    'Adamant': {'increased': 'attack', 'decreased': 'sp_attack'},
    'Naughty': {'increased': 'attack', 'decreased': 'sp_defense'},
    'Bold': {'increased': 'defense', 'decreased': 'attack'},
    'Relaxed': {'increased': 'defense', 'decreased': 'speed'},
    'Impish': {'increased': 'defense', 'decreased': 'sp_attack'},
    'Lax': {'increased': 'defense', 'decreased': 'sp_defense'},
    'Timid': {'increased': 'speed', 'decreased': 'attack'},
    'Hasty': {'increased': 'speed', 'decreased': 'defense'},
    'Jolly': {'increased': 'speed', 'decreased': 'sp_attack'},
    'Naive': {'increased': 'speed', 'decreased': 'sp_defense'},
    'Modest': {'increased': 'sp_attack', 'decreased': 'attack'},
    'Mild': {'increased': 'sp_attack', 'decreased': 'defense'},
    'Quiet': {'increased': 'sp_attack', 'decreased': 'speed'},
    'Rash': {'increased': 'sp_attack', 'decreased': 'sp_defense'},
    'Calm': {'increased': 'sp_defense', 'decreased': 'attack'},
    'Gentle': {'increased': 'sp_defense', 'decreased': 'defense'},
    'Sassy': {'increased': 'sp_defense', 'decreased': 'speed'},
    'Careful': {'increased': 'sp_defense', 'decreased': 'sp_attack'}
}

def parse_evs(ev_string):
    """Parse EV string like '252 SpA / 4 SpD / 252 Spe' into a dict"""
    ev_dict = {'hp': 0, 'attack': 0, 'defense': 0, 
               'sp_attack': 0, 'sp_defense': 0, 'speed': 0}
    
    if not ev_string:
        return ev_dict
        
    parts = ev_string.split('/')
    for part in parts:
        value, stat = part.strip().split()
        stat_mapping = {
            'HP': 'hp',
            'Atk': 'attack',
            'Def': 'defense',
            'SpA': 'sp_attack',
            'SpD': 'sp_defense',
            'Spe': 'speed'
        }
        ev_dict[stat_mapping[stat]] = int(value)
    
    return ev_dict

def parse_ivs(iv_string):
    """Parse IV string like 'IVs: 0 Atk / 0 Spe' into a dict"""
    iv_dict = {'hp': 31, 'attack': 31, 'defense': 31, 
               'sp_attack': 31, 'sp_defense': 31, 'speed': 31}
    
    if not iv_string:
        return iv_dict
        
    # Remove 'IVs:' prefix
    iv_string = iv_string.replace('IVs:', '').strip()
    
    # Split by slashes if multiple IVs
    parts = [p.strip() for p in iv_string.split('/')]
    
    stat_mapping = {
        'HP': 'hp',
        'Atk': 'attack',
        'Def': 'defense',
        'SpA': 'sp_attack',
        'SpD': 'sp_defense',
        'Spe': 'speed'
    }
    
    for part in parts:
        value, stat = part.strip().split()
        stat = stat.strip()
        iv_dict[stat_mapping[stat]] = int(value)
    
    return iv_dict

def parse_team_text(team_text):
    """Parse the team format text into a structured dictionary"""
    # Add list of Pokémon where gender matters for form
    GENDERED_POKEMON = {
        'meowstic': {'M': '-male', 'F': '-female'},
        'indeedee': {'M': '-male', 'F': '-female'},
        'basculegion': {'M': '-male', 'F': '-female'},
        'oinkologne': {'M': '-male', 'F': '-female'}
    }
    
    lines = team_text.strip().split('\n')
    playstyle = lines[0].split(': ')[1]
    
    pokemon_list = []
    current_pokemon = None
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
            
        if any(char in line for char in ['@', '(']) or re.match(r'^[\w-]+$', line.strip()):
            if current_pokemon:
                pokemon_list.append(current_pokemon)
                
            if '@' in line:
                parts = line.split('@')
                name = parts[0].strip()
                item = parts[1].strip()
            else:
                name = line.strip()
                item = None
            
            # Handle gender-specific forms
            gender_match = re.search(r'\s*\((M|F)\)', name)
            base_name = re.sub(r'\s*\([MF]\)', '', name).lower()
            
            # Handle nicknames
            nickname_match = re.search(r'\(([\w\s-]+)\)', base_name)
            if nickname_match:
                base_name = nickname_match.group(1).strip().lower()
            
            # Apply gender suffix if it's a gendered Pokémon
            if base_name in GENDERED_POKEMON and gender_match:
                gender = gender_match.group(1)
                base_name += GENDERED_POKEMON[base_name][gender]
            
            current_pokemon = {
                'name': base_name,
                'item': item,
                'moves': [],
                'evs': {},
                'ivs': {},
                'nature': 'Serious'
            }
        elif 'Nature' in line:
            current_pokemon['nature'] = line.split('Nature')[0].strip()
        elif line.startswith('EVs:'):
            current_pokemon['evs'] = parse_evs(line.replace('EVs:', '').strip())
        elif line.startswith('IVs:'):
            current_pokemon['ivs'] = parse_ivs(line)
        elif line.startswith('-'):
            current_pokemon['moves'].append(line.strip())
    
    if current_pokemon:
        pokemon_list.append(current_pokemon)
    
    return {
        'playstyle': playstyle,
        'pokemon': pokemon_list
    }

def process_team(team_text):
    """Process a team from text format into the database"""
    session = Session()
    try:
        team_data = parse_team_text(team_text)
        
        # Create new team with playstyle
        new_team = Team(
            team_name=f"Team {team_data['playstyle']}", 
            playstyle=team_data['playstyle']
        )
        session.add(new_team)
        session.flush()
        
        # Process each Pokemon
        for poke_data in team_data['pokemon']:
            # Convert Pokemon name to database format (replace space with hyphen)
            db_pokemon_name = poke_data['name'].lower().replace(' ', '-')
            
            # Special handling for specific Pokemon forms
            if db_pokemon_name in ['ogerpon-wellspring', 'ogerpon-hearthflame', 'ogerpon-cornerstone']:
                db_pokemon_name += '-mask'
            elif db_pokemon_name == 'keldeo':
                db_pokemon_name = 'keldeo-ordinary'
            elif db_pokemon_name in ['landorus', 'thundurus', 'tornadus', 'enamorus']:
                db_pokemon_name += '-incarnate'
            elif db_pokemon_name == 'sinistcha-masterpiece':
                db_pokemon_name = 'sinistcha'
            elif db_pokemon_name in ['gastrodon-east', 'gastrodon-west']:
                db_pokemon_name = 'gastrodon'
            elif db_pokemon_name == 'greninja-bond':
                db_pokemon_name = 'greninja'
            elif db_pokemon_name == 'maushold':
                db_pokemon_name = 'maushold-family-of-three'
            elif db_pokemon_name == 'mimikyu':
                db_pokemon_name = 'mimikyu-busted'
            elif db_pokemon_name == 'tauros-paldea-blaze':
                db_pokemon_name = 'tauros-paldea-blaze-breed'
            elif db_pokemon_name == 'tauros-paldea-aqua':
                db_pokemon_name = 'tauros-paldea-aqua-breed'
            elif db_pokemon_name == 'tauros-paldea-combat':
                db_pokemon_name = 'tauros-paldea-combat-breed'
            elif db_pokemon_name == 'meloetta':
                db_pokemon_name = 'meloetta-aria'
            elif db_pokemon_name == 'indeedee':
                db_pokemon_name = 'indeedee-male'
            elif db_pokemon_name == 'basculegion':
                db_pokemon_name = 'basculegion-male'
                
            # Get Pokemon base data
            base_pokemon = session.query(Pokemon).filter_by(name=db_pokemon_name).first()
            if not base_pokemon:
                print(f"Warning: Pokemon {poke_data['name']} not found in database")
                continue
            
            # Get nature modifiers
            nature = NATURE_MODIFIERS.get(poke_data['nature'], {})
            
            # Calculate stats
            stats = {}
            # Calculate HP
            stats['hp'] = calculate_hp(
                getattr(base_pokemon, 'base_hp'),
                poke_data['evs'].get('hp', 0),
                poke_data['ivs'].get('hp', 31)
            )
            
            # Calculate other stats with nature modifiers
            for stat in ['attack', 'defense', 'sp_attack', 'sp_defense', 'speed']:
                ev = poke_data['evs'].get(stat, 0)
                iv = poke_data['ivs'].get(stat, 31)
                base = getattr(base_pokemon, f'base_{stat}')
                
                # Apply nature modifier
                nature_mod = 1.0
                if nature:  # Only apply if it's not a neutral nature
                    if nature.get('increased') == stat:
                        nature_mod = 1.1
                    elif nature.get('decreased') == stat:
                        nature_mod = 0.9
                
                
                stats[stat] = calculate_stat(
                    base,
                    ev,
                    iv,
                    nature_mod=nature_mod
                )
            
            # Get item if present
            item = None
            if poke_data.get('item'):  # Use the stored item from parse_team_text
                item_name = poke_data['item'].lower().replace(' ', '-')
                item = session.query(Item).filter_by(item_name=item_name).first()
                # Silently handle missing items by using None/null
                # No warning message needed

            # Create TeamPokemon entry
            team_pokemon = TeamPokemon(
                team_id=new_team.team_id,
                pokemon_id=base_pokemon.pokemon_id,
                item_id=item.item_id if item else None,  # Will be None if item not found
                hp=stats['hp'],
                attack=stats['attack'],
                defense=stats['defense'],
                sp_attack=stats['sp_attack'],
                sp_defense=stats['sp_defense'],
                speed=stats['speed']
            )
            
            # Add moves
            for i, move_name in enumerate(poke_data['moves'], 1):
                # Remove leading dash and spaces
                db_move_name = move_name.lstrip('- ').lower()
                
                # Convert to database format (replace spaces with hyphens)
                db_move_name = db_move_name.replace(' ', '-')
                
                move = session.query(Move).filter_by(name=db_move_name).first()
                if move:
                    setattr(team_pokemon, f'move{i}_id', move.move_id)
                else:
                    print(f"Warning: Move {move_name} not found in database")
            
            session.add(team_pokemon)
        
        session.commit()
        print(f"Successfully processed team: Team {team_data['playstyle']}")
        
    except Exception as e:
        print(f"Error processing team: {str(e)}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    # Example usage
    example_team = """Playstyle: Offense
Gliscor (F) @ Toxic Orb  
Ability: Poison Heal  
Tera Type: Normal  
EVs: 244 HP / 88 Def / 176 Spe  
Impish Nature  
- Facade  
- Knock Off  
- Swords Dance  
- Protect  

Meowscarada (F) @ Heavy-Duty Boots  
Ability: Protean  
Tera Type: Ghost  
EVs: 252 Atk / 4 SpD / 252 Spe  
Jolly Nature  
- Knock Off  
- U-turn  
- Triple Axel  
- Spikes  

Ursaluna (F) @ Heavy-Duty Boots  
Ability: Bulletproof  
Tera Type: Steel  
EVs: 184 HP / 56 Atk / 208 SpD 
Adamant Nature  
- Headlong Rush  
- Ice Punch  
- Rest  
- Sleep Talk  

Skarmory (F) @ Rocky Helmet  
Ability: Sturdy  
Tera Type: Dragon  
EVs: 240 HP / 44 Atk / 216 Def
Impish Nature  
- Brave Bird  
- Stealth Rock  
- Roost  
- Whirlwind  

Landorus-Therian  
Ability: Intimidate  
Tera Type: Dragon  
EVs: 252 Atk / 4 Def / 252 Spe  
Jolly Nature  
- Stealth Rock  
- Earthquake  
- U-turn  
- Stone Edge

Slowking-Galar @ Heavy-Duty Boots  
Ability: Regenerator  
Tera Type: Water  
EVs: 248 HP / 8 Def / 252 SpD  
Sassy Nature  
IVs: 0 Atk / 0 Spe  
- Sludge Bomb  
- Psychic Noise  
- Thunder Wave  
- Chilly Reception"""
    
    process_team(example_team)
