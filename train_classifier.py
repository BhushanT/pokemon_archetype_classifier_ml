from databases.database import Session, Team
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

def load_team_data():
    """Load team data from database and prepare for classification"""
    session = Session()
    
    teams = session.query(Team).filter(Team.playstyle.isnot(None)).all()
    
    features = []
    targets = []
    
    playstyle_counts = {}
    for team in teams:
        if team.playstyle not in playstyle_counts:
            playstyle_counts[team.playstyle] = 0
        playstyle_counts[team.playstyle] += 1
    
    for team in teams:
        if playstyle_counts[team.playstyle] >= 2:
            features.append([
                team.team_hp,
                team.team_offense,
                team.team_defense,
                team.team_spdef,
                team.team_speed,
                team.recovery_moves,
                team.defensive_items
            ])
            targets.append(team.playstyle)
    
    session.close()
    
    return np.array(features), np.array(targets)

def visualize_features(X, y):
    """Create visualizations of the features across different playstyles"""
    feature_names = [
        'HP', 'Offense', 'Defense', 'Sp.Defense', 
        'Speed', 'Recovery Moves', 'Defensive Items'
    ]
    df = pd.DataFrame(X, columns=feature_names)
    df['Playstyle'] = y

    plt.style.use('seaborn')
    
    # Create violin plots for each feature
    fig, axes = plt.subplots(3, 3, figsize=(15, 15))
    axes = axes.ravel()
    
    for idx, feature in enumerate(feature_names):
        sns.violinplot(data=df, x='Playstyle', y=feature, ax=axes[idx])
        axes[idx].set_xticklabels(axes[idx].get_xticklabels(), rotation=45, ha='right')
        axes[idx].set_title(f'{feature} Distribution by Playstyle')
    

    if len(feature_names) < 9:
        fig.delaxes(axes[-1])
    
    plt.tight_layout()
    plt.show()
    

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='HP', y='Offense', hue='Playstyle', alpha=0.7)
    plt.title('Team Offense vs HP by Playstyle')
    plt.xlabel('HP')
    plt.ylabel('Offense')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
    
    plt.figure(figsize=(10, 8))
    correlation_matrix = df[feature_names].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Feature Correlation Heatmap')
    plt.tight_layout()
    plt.show()

def train_classifier():

    X, y = load_team_data()
    

    visualize_features(X, y)

    unique, counts = np.unique(y, return_counts=True)
    print("\nClass distribution:")
    for class_name, count in zip(unique, counts):
        print(f"{class_name}: {count} samples")
    
    if len(X) < 10:  # arbitrary minimum, adjust as needed
        raise ValueError("Not enough samples for training. Need at least 10 teams with playstyles.")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    

    clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    clf.fit(X_train_scaled, y_train)
    

    y_pred = clf.predict(X_test_scaled)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Print feature importance
    feature_names = [
        'HP', 'Offense', 'Defense', 'Sp.Defense', 
        'Speed', 'Recovery Moves', 'Defensive Items'
    ]
    
    importance = pd.DataFrame({
        'feature': feature_names,
        'importance': clf.feature_importances_
    })
    print("\nFeature Importance:")
    print(importance.sort_values('importance', ascending=False))
    
    # Save the trained models
    joblib.dump(clf, 'models/random_forest_classifier.joblib')
    joblib.dump(scaler, 'models/scaler.joblib')
    
    '''To use the models,import joblib
       clf = joblib.load('models/random_forest_classifier.joblib')
       scaler = joblib.load('models/scaler.joblib')'''
    return clf, scaler

if __name__ == "__main__":
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    clf, scaler = train_classifier() 