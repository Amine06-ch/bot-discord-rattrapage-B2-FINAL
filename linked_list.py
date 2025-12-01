# linked_list.py

class CommandNode:
    """Représente un élément (une commande) dans la liste chaînée."""
    def __init__(self, command_name, timestamp):
        self.command = command_name 
        self.timestamp = timestamp 
        self.next = None

class CommandHistoryList:
    """Représente la Liste Chaînée d'historique de commandes."""
    def __init__(self):
        self.head = None
        self.tail = None 
        self.size = 0

    def add_command(self, command_name, timestamp):
        """Ajoute une nouvelle commande à la fin de la liste (FIFO/File)."""
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

    def clear(self):
        """Vide l'historique (réinitialise la tête et la queue)."""
        self.head = None
        self.tail = None
        self.size = 0
        return "Historique vidé avec succès."