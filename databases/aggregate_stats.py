from sqlalchemy import func, case, select
from database import session, Team, TeamPokemon, Move, Item

def update_team_stats():
    # Get teams that haven't been aggregated yet (where stats are None)
    teams = session.query(Team).filter(
        (Team.team_hp == None) |
        (Team.team_offense == None) |
        (Team.team_defense == None) |
        (Team.team_spdef == None) |
        (Team.team_speed == None) |
        (Team.recovery_moves == None) |
        (Team.defensive_items == None)
    ).all()
    
    for team in teams:
        team_stats = session.query(
            func.sum(TeamPokemon.hp).label('total_hp'),
            func.sum(TeamPokemon.defense).label('total_defense'),
            func.sum(TeamPokemon.sp_defense).label('total_spdef'),
            func.sum(TeamPokemon.speed).label('total_speed'),
            func.sum(
                func.greatest(TeamPokemon.attack, TeamPokemon.sp_attack)
            ).label('total_offense')
        ).filter(TeamPokemon.team_id == team.team_id).first()

        recovery_moves_count = session.query(func.count(Move.move_id)).join(
            TeamPokemon, (Move.move_id == TeamPokemon.move1_id) |
                        (Move.move_id == TeamPokemon.move2_id) |
                        (Move.move_id == TeamPokemon.move3_id) |
                        (Move.move_id == TeamPokemon.move4_id)
        ).filter(
            TeamPokemon.team_id == team.team_id,
            Move.is_recovery == True
        ).scalar()

        defensive_items_count = session.query(func.count(Item.item_id)).join(
            TeamPokemon, TeamPokemon.item_id == Item.item_id
        ).filter(
            TeamPokemon.team_id == team.team_id,
            Item.is_defensive == True
        ).scalar()

        team.team_hp = team_stats.total_hp
        team.team_offense = team_stats.total_offense
        team.team_defense = team_stats.total_defense
        team.team_spdef = team_stats.total_spdef
        team.team_speed = team_stats.total_speed
        team.recovery_moves = recovery_moves_count
        team.defensive_items = defensive_items_count

    session.commit()

if __name__ == "__main__":
    update_team_stats()
