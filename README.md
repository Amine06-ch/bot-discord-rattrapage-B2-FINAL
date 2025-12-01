Projet de Rattrapage : ACH-Bot 

Ce projet consiste en un bot Discord construit en Python pour le rattrapage B2. L'objectif était de créer un bot capable de gérer des données complexes (historique, conversation) en utilisant des structures de données codées à la main (Listes chaînées, Arbres).

Mise en Route du Bot
1. Préparation 
J'ai utilisé un fichier .env pour masquer ma clé secrète (le Token Discord) des yeux de GitHub et du public.

Assurez-vous d'avoir installé les dépendances : pip install discord.py python-dotenv.

Mon Token est dans le fichier .env (qui est ignoré par Git).

2. Démarrage
Pour lancer le bot, il suffit d'être dans l'environnement virtuel et de taper :

python main.py


Structures de Données Manuelles
J'ai codé moi-même ces structures pour le projet :

1. Le Carnet de Commandes (Liste Chaînée)
Structure : J'ai créé la classe CommandHistoryList (une Liste Chaînée simple) et la classe CommandNode. Chaque commande est ajoutée à la fin, comme un ticket à la queue.
 Elle sert à enregistrer chaque commande utilisateur (nom et heure) pour qu'elle puisse survivre au redémarrage du bot.

Commande	
!last	Montre la dernière commande que l'utilisateur a tapée.

!history	Affiche l'intégralité du carnet de commandes de l'utilisateur.

!clear_history	Efface toutes les commandes de l'utilisateur dans le carnet.



2. Le Petit Psy (Arbre de Conversation)
Structure : J'ai utilisé un Arbre Non Binaire (avec les classes TreeNode et ConversationTree). Chaque nœud est une question, et les réponses de l'utilisateur mènent aux nœuds enfants suivants.

Thème : La conversation porte sur les préférences Cinéma/Genre.

Commande	
!help_me	Démarre le questionnaire à la racine de l'arbre.

[Réponse]	L'utilisateur répond directement (sans !) pour avancer dans les questions.

!reset	Permet de recommencer le questionnaire à zéro.

!speak_about X	Le bot utilise un parcours en profondeur (DFS) pour vérifier si le sujet X (ex: Action, Musique) fait partie de l'arbre de discussion.



Sauvegarde (Persistance des Données)

Pour que l'historique des commandes survive si le bot s'éteint, j'ai implémenté un système de sauvegarde.

Méthode : J'utilise le format JSON (fichier bot_data.json) qui est facile à lire et à écrire.

Fonctionnement : La fonction save_data() est appelée automatiquement à l'extinction du bot (atexit.register). Elle convertit mes Listes Chaînées en listes Python que JSON peut comprendre.

 3 Fonctionnalités Supplémentaires :
 
J'ai ajouté ces petites commandes pour rendre le bot plus vivant :

Commande	
!joke	Raconte une blague très drôle de la rue (souvent sur les lapins).

!roll [nombre]	Lance un dé (par défaut un D6).

!echo [message]	Répète simplement le message de l'utilisateur.
