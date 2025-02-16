# Pokémon Team Playstyle Classifier

A machine learning system that analyzes Pokémon teams and classifies their playstyle based on team composition and statistics.

## Description
This program uses a Random Forest Classifier to analyze Pokémon teams and predict their playstyle based on various team attributes including:
- Team HP
- Offensive capabilities
- Defensive stats
- Speed
- Recovery moves
- Defensive items

## Getting Started

### Prerequisites
- Python 3.x
- MySQL database
- Required Python packages (install via `pip install -r requirements.txt`):
  - SQLAlchemy
  - scikit-learn
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - python-dotenv
  - joblib

### Initial Setup
1. Create a `.env` file with your database credentials:
```
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database_name
```
2. Run the initial setup script:
```
python initial_startup.py
```
This will:
- Set up the database tables
- Populate Pokémon data
- Populate items and moves
- Build the initial classifier

### Rebuilding the Classifier
To retrain the classifier with new team data:
```
python rebuild_classifier.py
```

## Features
- Database storage for Pokémon, moves, items, and team compositions
- Automated data visualization of team statistics
- Machine learning-based playstyle classification
- Feature importance analysis
- Performance metrics for classification accuracy

## Project Structure
- `database.py` - Database models and connection setup using SQLAlchemy
- `train_classifier.py` - Machine learning model training and evaluation
- `initial_startup.py` - First-time setup script
- `rebuild_classifier.py` - Script for retraining the classifier

## License
MIT