from process_team import process_team
import re
from tqdm import tqdm

def split_teams(content):
    """Split content into individual teams based on === headers"""
    # Split on the === headers
    teams = re.split(r'===\s*\[([^\]]+)\]\s*([^=]+?)\s*===', content)
    
    # Remove the first empty element and process in groups of 3
    teams = teams[1:]
    processed_teams = []
    
    for i in range(0, len(teams), 3):
        if i + 2 >= len(teams):
            break
            
        format_name = teams[i]      # gen4ou
        team_info = teams[i + 1]    # Azelf~Hyper Offense
        team_content = teams[i + 2].strip()  # The actual team content
        # Split team name and playstyle
        name_parts = team_info.strip().split('~')
        team_name = name_parts[0]
        playstyle = name_parts[1] if len(name_parts) > 1 else "Unknown"
        
        # Construct the team text in the format expected by process_team
        team_text = f"Playstyle: {playstyle}\n{team_content}"
        processed_teams.append({
            'format': format_name,
            'team_name': team_name,
            'team_text': team_text
        })
    
    return processed_teams

def process_teams_from_file(filepath):
    """Process multiple teams from a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    
    teams = split_teams(content)
    
    print(f"\nProcessing {len(teams)} teams...")
    for team in tqdm(teams):
        try:
            print(f"\nProcessing: [{team['format']}] {team['team_name']}")
            process_team(team['team_text'])
        except Exception as e:
            print(f"Failed to process team: {team['team_name']}")
            print(f"Error: {str(e)}\n")

if __name__ == "__main__":
    # Example usage:
    process_teams_from_file("databases/teams.txt") 