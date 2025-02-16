import os
import sys
import subprocess

def run_script(script_name):
    """Run a Python script and check for successful execution."""
    print(f"Running {script_name}...")
    try:
        subprocess.run([sys.executable, script_name], check=True)
        print(f"Successfully completed {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        sys.exit(1)

def main():
    # List of scripts to run in order
    setup_scripts = [
        "database.py",
        "populate_pokemon.py",
        "populate_items.py",
        "populate_moves.py",
        "rebuild_classifier.py"
    ]

    print("Starting initial setup...")
    
    # Check if all scripts exist
    for script in setup_scripts:
        if not os.path.exists(script):
            print(f"Error: {script} not found!")
            sys.exit(1)

    # Run each script in sequence
    for script in setup_scripts:
        run_script(script)

    print("\nInitial setup completed successfully!")

if __name__ == "__main__":
    main()
