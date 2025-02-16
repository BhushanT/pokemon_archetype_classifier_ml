import subprocess
from databases.database import Session
from sqlalchemy import text

def clear_tables():
    """Clear the team_pokemon and teams tables"""
    session = Session()
    try:
        session.execute(text("DELETE FROM team_pokemon"))
        session.execute(text("DELETE FROM teams"))
        session.commit()
        print("Successfully cleared team_pokemon and teams tables")
    except Exception as e:
        session.rollback()
        print(f"Error clearing tables: {e}")
        raise
    finally:
        session.close()

def run_script(script_name):
    """Run a Python script and check for successful execution"""
    try:
        subprocess.run(['python', script_name], check=True)
        print(f"Successfully completed {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        raise

def main():
    print("Starting classifier rebuild process...")
    
    # Step 1: Clear the database tables
    clear_tables()
    
    # Step 2: Run the processing scripts in sequence
    scripts = [
        'databases/process_teams_batch.py',
        'databases/aggregate_stats.py',
        'train_classifier.py'
    ]
    
    for script in scripts:
        print(f"\nRunning {script}...")
        run_script(script)
    
    print("\nClassifier rebuild process completed successfully!")

if __name__ == "__main__":
    main() 