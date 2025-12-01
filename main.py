
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
import json
import atexit 

class CommandNode:
    """Représente un élément (une commande) dans la liste chaînée."""
    def __init__(self, command_name, timestamp):
        self.command = command_name 
        self.timestamp = timestamp 
        self.next = None

class CommandHistoryList:
    """Représente la Liste Chaînée d'historique de commandes."""
    def __init__(self, initial_data=None):
        self.head = None
        self.tail = None 
        self.size = 0
        if initial_data:
            for item in initial_data:
                self.add_command(item['command'], item['timestamp'])

    def add_command(self, command_name, timestamp):
        """Ajoute une nouvelle commande à la fin de la liste."""
        new_node = CommandNode(command_name, timestamp)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node 
        self.size += 1

    def get_last_command(self):
        """Retourne la dernière commande rentrée (via la queue)."""
        if self.tail:
            return self.tail.command
        return "Historique vide."

    def get_all_commands(self):
        """Retourne toutes les commandes sous forme de liste Python."""
        commands = []
        current = self.head
        while current:
            commands.append(f"{current.command} ({current.timestamp})")
            current = current.next
        return commands
    
    def to_serializable(self):
        """Convertit la liste chaînée en une liste Python standard pour la sauvegarde."""
        data = []
        current = self.head
        while current:
            data.append({"command": current.command, "timestamp": current.timestamp})
            current = current.next
        return data

    def clear(self):
        """Vide l'historique."""
        self.head = None
        self.tail = None
        self.size = 0


class TreeNode:
    """Représente un nœud dans notre arbre de conversation."""
    def __init__(self, question_id, text, conclusion=False):
        self.id = question_id
        self.text = text
        self.children = {} 
        self.is_conclusion = conclusion

    def add_child(self, user_response, next_node):
        """Ajoute un chemin de réponse au nœud suivant."""
        self.children[user_response.lower()] = next_node

class ConversationTree:
    """Gère la structure de l'arbre et le parcours."""
    def __init__(self):
        self.root = self._build_tree()

    def _build_tree(self):
        """Construit l'arbre de conversation sur l'exemple Cinéma/Genre."""
        

        conclusion_action = TreeNode("C3", "L'Action, c'est votre truc, donc vous aimez les films avec de l'énergie et de belles scènes !", conclusion=True)
        conclusion_comedie = TreeNode("C4", "Votre choix de la Comédie indique que vous recherchez la légèreté et l'humour.", conclusion=True)
        conclusion_horreur = TreeNode("C5", "Votre choix de l'Horreur montre un intérêt pour le suspense et les sensations fortes.", conclusion=True)
        conclusion_default = TreeNode("C6", "Si vous n'avez pas de genre préféré, vous êtes probablement ouvert à tout type de film !", conclusion=True)
        
        q_genre = TreeNode("Q2", "Parfait ! Quel est votre genre de film préféré ? (Action, Comédie, Horreur, Autre)")
        q_genre.add_child("Action", conclusion_action)
        q_genre.add_child("Comédie", conclusion_comedie)
        q_genre.add_child("Horreur", conclusion_horreur)
        q_genre.add_child("Autre", conclusion_default)

        q_interet = TreeNode("Q1", "Bien reçu. Voulez-vous que l'on discute de cinéma ou de musique ? (Cinéma/Musique)")
        q_interet.add_child("Cinéma", q_genre)
        q_interet.add_child("Musique", conclusion_default)

        root = TreeNode("R0", "Bienvenue dans le questionnaire ! Êtes-vous prêt ? (Oui/Non)")
        root.add_child("oui", q_interet)
        root.add_child("non", conclusion_default)

        return root

    def find_subject(self, subject):
        """Parcours l'arbre (DFS) pour trouver un sujet dans le texte ou les réponses."""
        stack = [self.root]
        while stack:
            current_node = stack.pop()
            
            if subject.lower() in current_node.text.lower():
                return True
            
            for key in current_node.children.keys():
                if subject.lower() == key:
                    return True

            for child in current_node.children.values():
                stack.append(child)
                
        return False

load_dotenv() 
TOKEN = os.getenv('BOT_TOKEN') 
DATA_FILE = 'bot_data.json' 

intents = discord.Intents.default()
intents.message_content = True 
intents.presences = True      

bot = commands.Bot(command_prefix='!', intents=intents)

user_histories = {} 
conversation_tree = ConversationTree()
user_conversation_states = {} 

def load_data():
    """Charge les données de l'historique depuis le fichier JSON."""
    global user_histories
    if os.path.exists(DATA_FILE):
        print("Chargement des données de l'historique...")
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            
            for user_id_str, history_data in data.items():
                user_id = int(user_id_str)
                user_histories[user_id] = CommandHistoryList(history_data)
        print(f"Historiques chargés pour {len(user_histories)} utilisateurs.")
    else:
        print("Aucun fichier de sauvegarde trouvé. Démarrage à neuf.")

def save_data():
    """Sauvegarde les données de l'historique dans le fichier JSON."""
    if user_histories:
        serializable_data = {}
        for user_id, history in user_histories.items():
            serializable_data[str(user_id)] = history.to_serializable() 
            
        with open(DATA_FILE, 'w') as f:
            json.dump(serializable_data, f, indent=4)
        print("Données de l'historique sauvegardées.")
    else:
        print("Aucun historique à sauvegarder.")

atexit.register(save_data) 

@bot.event
async def on_ready():
    """Se déclenche lorsque le bot est connecté et prêt."""
    load_data() 
    print('-------------------------------------------')
    print(f'🤖 Bot prêt ! Connecté en tant que {bot.user}')
    print('-------------------------------------------')

@bot.event
async def on_command(ctx):
    """Enregistre chaque commande exécutée par un utilisateur dans la Liste Chaînée."""
    user_id = ctx.author.id
    command_name = ctx.command.name
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_id not in user_histories:
        user_histories[user_id] = CommandHistoryList()
        
    user_histories[user_id].add_command(command_name, timestamp)
    
    print(f"Commande '{command_name}' enregistrée pour l'utilisateur {user_id}")

@bot.event
async def on_message(message):
    """Gère les réponses à la conversation de l'Arbre."""
    if message.author.bot:
        return
    
    user_id = message.author.id
    content = message.content.lower().strip()

    if user_id in user_conversation_states:
        current_node = user_conversation_states[user_id]
        
        if content in current_node.children:
            next_node = current_node.children[content]
            user_conversation_states[user_id] = next_node
            
            if next_node.is_conclusion:
                await message.channel.send(f"🌟 **CONCLUSION :** {next_node.text}\n\n🤖 Discussion terminée. Tapez `!reset` pour recommencer.")
                del user_conversation_states[user_id]
            else:
                await message.channel.send(f"➡️ **Question suivante :** {next_node.text}")
            
        elif not message.content.startswith('!'):
            options = ", ".join(current_node.children.keys())
            await message.channel.send(f"❌ Réponse non valide. Options possibles : **{options}**.")
            
    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    """Envoie la latence (commande de test)."""
    latency_ms = round(bot.latency * 1000)
    await ctx.send(f'Pong! La vie est belle faut juste savoir profiter du moment  La latence est de **{latency_ms} ms**.')

@bot.command(name="last")
async def get_last(ctx):
    """Affiche la dernière commande que vous avez exécutée."""
    user_id = ctx.author.id
    history = user_histories.get(user_id)
    
    if history:
        last_command = history.get_last_command()
        await ctx.send(f"➡️ **Dernière commande :** `{last_command}`")
    else:
        await ctx.send("Vous n'avez pas encore d'historique de commandes.")

@bot.command(name="history")
async def show_history(ctx):
    """Affiche toutes les commandes rentrées par un utilisateur."""
    user_id = ctx.author.id
    history = user_histories.get(user_id)
    
    if history and history.size > 0:
        all_commands = history.get_all_commands()
        history_list = "\n".join([f"- {cmd}" for cmd in all_commands])
        await ctx.send(f"📜 **Votre Historique ({history.size} commandes) :**\n```\n{history_list}\n```")
    else:
        await ctx.send("Votre historique de commandes est vide.")

@bot.command(name="clear_history")
async def clear_history(ctx):
    """Vide l'historique des commandes de l'utilisateur."""
    user_id = ctx.author.id
    if user_id in user_histories:
        user_histories[user_id].clear()
        await ctx.send("✅ Votre historique de commandes a été effacé.")
    else:
        await ctx.send("Votre historique était déjà vide.")

@bot.command(name="help_me") 
async def start_conversation(ctx):
    """Commande help qui lance la conversation depuis la racine."""
    user_id = ctx.author.id
    root_node = conversation_tree.root
    
    user_conversation_states[user_id] = root_node
    
    await ctx.send(f"🤖 **Conversation démarrée !**\n\n{root_node.text}")

@bot.command(name="reset")
async def reset_conversation(ctx):
    """Recommence la discussion depuis la racine de l’arbre."""
    user_id = ctx.author.id
    user_conversation_states[user_id] = conversation_tree.root
    await ctx.send("🔄 **Discussion réinitialisée !** Veuillez taper une réponse pour recommencer : " + conversation_tree.root.text)

@bot.command(name="speak_about")
async def speak_about(ctx, *, subject: str):
    """Vérifie si le sujet X existe dans l'arbre (parcours de l'arbre)."""
    
    if conversation_tree.find_subject(subject):
        await ctx.send(f"✅ Oui, le sujet **'{subject}'** fait partie de mes domaines de discussion.")
    else:
        await ctx.send(f"❌ Non, je ne trouve pas de référence au sujet **'{subject}'** dans mon arbre de discussion.")


@bot.command(name="joke")
async def random_joke(ctx):
    """Fonctionnalité Supp. #1: Raconte une blague."""
    await ctx.send("Deux amis se promènent et l'un dit à l'autre : Tu savais que manger des carottes, c'est bon pour la vue ? Ah oui ? Et qu'est-ce qui te fait dire ça ? Tu as déjà vu un lapin avec des lunettes ? .")

@bot.command(name="roll")
async def dice_roll(ctx, sides: int=6):
    """Fonctionnalité Supp. #2: Lance un dé (par défaut 6 faces)."""
    import random
    result = random.randint(1, sides)
    await ctx.send(f"🎲 J'ai lancé un dé à {sides} faces. Résultat : **{result}**")

@bot.command(name="echo")
async def echo_message(ctx, *, message: str):
    """Fonctionnalité Supp. #3: Répète votre message."""
    await ctx.send(f"Vous avez dit : {message}")

if TOKEN:
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Une erreur s'est produite lors du lancement du bot : {e}")
else:
    print("ERREUR : Le token n'a pas été trouvé. Vérifiez votre fichier .env.")