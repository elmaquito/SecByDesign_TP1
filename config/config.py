import os

class Config:
    """Configuration de base de l'application Flask."""
    # Clé secrète pour JWT, à charger depuis une variable d'environnement en production
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'votre-clé-secrète-très-difficile-à-deviner')
    
    # Configuration de la base de données
    # On utilise un chemin relatif pour que la BDD soit créée dans un dossier 'instance'
    # à la racine du projet, ce qui est une bonne pratique avec Flask.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///../instance/notes.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
