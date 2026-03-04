"""
Lab 1: Text-Based Adventure RPG
================================
Amelia Hammer 

Build your game here! This file contains all the starter code from the lab notebook.
Fill in the TODOs, add your own classes, and make it your own.

Run with: python game.py
"""

import random


# =============================================================================
# Dice Utilities
# =============================================================================

def roll_d20():
    return random.randint(1, 20)

def roll_dice(num_dice, sides):
    """Roll multiple dice and return the total. E.g., roll_dice(2, 6) for 2d6."""
    return sum(random.randint(1, sides) for _ in range(num_dice))


# =============================================================================
# Character Classes
# =============================================================================

# YOUR CODE: Build your Character base class here
import random

def roll_d20():
    """Roll a 20-sided die."""
    return random.randint(1, 20)

def roll_dice(num_dice, sides):
    """Roll multiple dice and return the total. E.g., roll_dice(2, 6) for 2d6."""
    return sum(random.randint(1, sides) for _ in range(num_dice))


class Character:
    """Base class for all characters in the game."""
    
    def __init__(self, name, health, strength, defense):
        # Initialize attributes
        self.name = name
        self.max_health = int(health)
        self.health = int(health)
        self.strength = int(strength)
        self.defense = int(defense)
    
    def is_alive(self):
        # Return True if health > 0
        return self.health > 0
    
    def take_damage(self, amount):
        amount = max(0, int(amount))
        self.health = max(0, self.health - amount)
        print(f"💥 Oh no! {self.name} takes {amount} damage! (HP: {self.health}/{self.max_health})")
    
    
    def attack(self, target):
        roll = roll_d20()
        attack_total = roll + self.strength
        
        print(f"🎲 {self.name} attacks! Roll: {roll} + STR({self.strength}) = {attack_total}")
        if attack_total > target.defense:
            damage = self.strength
            print(f"✅ Hit! {self.name} deals {damage} damage to {target.name}.")
            target.take_damage(damage)
        else:
            print(f"❌ Miss! {target.name}'s DEF({target.defense}) blocks the attack.")
    
    def __str__(self):
        return f"{self.name} (HP: {self.health}/{self.max_health})"

# YOUR CODE: Build Player and Enemy classes here

class Player(Character):
    """The player character."""
    
    def __init__(self, name):
        super().__init__(name=name, health=40, strength=6, defense=12)
        self.inventory = []
    
    def pick_up(self, item):
        self.inventory.append(item)
        print(f"{self.name} picked up: {item}")
    
    def show_inventory(self):
        if not self.inventory:
            print("Inventory is empty. )")
            return
        print("Inventory:")
        for i, item in enumerate(self.inventory, start=1):
            print(f"  {i}. {item}")
    
    def heal(self, amount):
        amount = int(amount)
        old_hp = self.health
        self.health = min(self.max_health, self.health + amount)
        gained = self.health - old_hp
        print(f"💚 {self.name} heals {gained} HP! (HP: {self.health}/{self.max_health})")

    def boost_strength(self, amount):
        amount = int(amount)
        self.strength += amount
        print(f"💪 {self.name}'s STR increased by {amount}! (STR: {self.strength})")

    def boost_defense(self, amount):
        amount = int(amount)
        self.defense += amount
        print(f"🛡️ {self.name}'s DEF increased by {amount}! (DEF: {self.defense})")

class Enemy(Character):
    """Base class for enemies."""
    
    def __init__(self, name, health, strength, defense):
        super().__init__(name=name, health=health, strength=strength, defense=defense)

class LittleKid(Enemy):
    def __init__(self):
        super().__init__(name="Overexcited Kid", health=10, strength=2, defense=9)
    
    def attack(self, target):
        print("🧃 The kid shrieks: 'DUCKYYYYY!'")
        print("👟 Tiny sneakers charge toward you at full speed!")
        super().attack(target)
        
class Raccoon(Enemy):
    def __init__(self):
        super().__init__(name="Raccoon", health=16, strength=3, defense=11)
    
    def attack(self, target):
        print("🦝 The raccoon hisses and lunges from the shadows!")
        print("🗑️ It swings a mysterious trash item at you!")
        super().attack(target)

class OffLeashDog(Enemy):
    def __init__(self):
        super().__init__(name="Off Leash Dog", health=22, strength=4, defense=12)
    
    def attack(self, target):
        print("🐶 The dog barks aggressively!")
        print("💨 It sprints at you with unstoppable zoomies!")
        super().attack(target)

class SnappingTurtle(Enemy):
    def __init__(self):
        super().__init__(name="Snapping Turtle", health=28, strength=5, defense=13)
    
    def attack(self, target):
        print("🐢 The turtle slowly opens its jaws...")
        print("⚠️ CHOMP!!!")
        super().attack(target)

# =============================================================================
# Location Class
# =============================================================================
# YOUR CODE: Build the Location class

class Location:
    """A location in the game world."""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.connections = {}  # {"north": Location, "south": Location, etc.}
        self.enemies = []      # List of enemies in this location
        self.items = []        # List of items in this location
    
    def describe(self):
        """Print a full description of the location."""
        print(f"\n{'='*50}")
        print(f"📍 {self.name}")
        print(f"{'='*50}")
        print(self.description)
        
        if self.items:
            print("\n✨ You see:")
            for item in self.items:
                print(f"  - {item}")
        
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        if alive_enemies:
            print("\n👀 Threats nearby:")
            for e in alive_enemies:
                print(f"  - {e.name} (HP {e.health}/{e.max_health}, DEF {e.defense})")
        
        exits = self.get_exits()
        if exits:
            print("\n🚪 Exits:", ", ".join(exits))
            
    def get_exits(self):
        """Return a list of available directions."""
        return list(self.connections.keys())
    
    def add_connection(self, direction, location):
        """Connect this location to another."""
        self.connections[direction] = location


# =============================================================================
# World Builder
# =============================================================================

# YOUR CODE: Create your game world

def create_world():
    # --- Locations ---
    home = Location(
        "Quacks-a-Lot Home",
        "Your cozy home. One second you blinked and your ducklings vanished. "
        "Find Pip, Mip, and Sip before Quackie O gets home!"
    )

    pond = Location(
        "The Pond",
        "The water is calm… too calm. A turtle is posted up like security."
    )

    hotdog = Location(
        "Hot Dog Stand",
        "It smells incredible. Pigeons are lurking. A dog is watching you like you owe it lunch."
    )

    playground = Location(
        "Playground",
        "Absolute chaos. Tiny humans sprint in random directions. One kid points and yells 'DUCK!!!'"
    )

    castle = Location(
        "Belvedere Castle",
        "A mini castle with haunting energy. Echoes bounce off the stone walls."
    )

    cherry_hill = Location(
        "Cherry Hill",
        "A peaceful hill with benches and trees. You swear you hear faint peeping nearby."
    )

    strawberry_fields = Location(
        "Strawberry Fields",
        "Quiet and calm. A place where you can think… but don’t think too long."
    )

    # --- Connections (simple, readable map) ---
    home.add_connection("north", playground)
    playground.add_connection("south", home)

    playground.add_connection("east", hotdog)
    hotdog.add_connection("west", playground)

    playground.add_connection("north", pond)
    pond.add_connection("south", playground)

    pond.add_connection("east", castle)
    castle.add_connection("west", pond)

    pond.add_connection("west", cherry_hill)
    cherry_hill.add_connection("east", pond)

    cherry_hill.add_connection("north", strawberry_fields)
    strawberry_fields.add_connection("south", cherry_hill)

    # --- Enemies (use your enemy classes) ---
    # If your class names differ, just swap these
    playground.enemies.append(LittleKid())
    cherry_hill.enemies.append(Raccoon())
    hotdog.enemies.append(OffLeashDog())
    pond.enemies.append(SnappingTurtle())

    # --- Ducklings as items to pick up ---
    # Treat them as items so your inventory can track them
    castle.items.append("Duckling: Pip")
    strawberry_fields.items.append("Duckling: Mip")
    hotdog.items.append("Duckling: Sip")

    #fun/utility items
    home.items.append("Bread Crumbs")
    playground.items.append("Band-Aid")
    pond.items.append("Shiny Pebble")
    hotdog.items.append("Protein Hot Dog")         # +2 STR
    pond.items.append("Pond Water Espresso")       # +12 HP
    cherry_hill.items.append("Old Man")

    # Starting location
    return home

# =============================================================================
# Combat System
# =============================================================================

# YOUR CODE: Implement the combat system

class Combat:
    """Manages turn-based combat between player and enemy."""
    
    # Combat states
    PLAYER_TURN = "player_turn"
    ENEMY_TURN = "enemy_turn"
    COMBAT_END = "combat_end"
    
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.state = Combat.PLAYER_TURN
        self.combat_log = []
    
    def start(self):
        """Begin combat and run until someone wins/loses/flees."""
        print(f"\n⚔️ COMBAT BEGINS! ⚔️")
        print(f"{self.player.name} vs {self.enemy.name}!")
        
        while self.state != Combat.COMBAT_END:
            if self.state == Combat.PLAYER_TURN:
                self.player_turn()
            elif self.state == Combat.ENEMY_TURN:
                self.enemy_turn()
        
        return self.get_result()
    
    def player_turn(self):
        """Handle player's turn in combat."""
        print(f"\n{self.player} | {self.enemy}")
        print("What do you do? (attack / run)")
        
        action = input("> ").lower().strip()
        
        if action == "attack":
            self.player.attack(self.enemy)
            if not self.enemy.is_alive():
                print(f"\n🎉 {self.enemy.name} has been defeated!")
                self.state = Combat.COMBAT_END
            else:
                self.state = Combat.ENEMY_TURN
        
        elif action == "run":
            # 50% chance to escape
            if random.random() < 0.5:
                print("You successfully fled!")
                self.state = Combat.COMBAT_END
            else:
                print("Couldn't escape!")
                self.state = Combat.ENEMY_TURN
        
        else:
            print("Invalid action. Try 'attack' or 'run'.")
    
    def enemy_turn(self):
        """Handle enemy's turn in combat."""
        print(f"\n{self.enemy.name}'s turn...")
        self.enemy.attack(self.player)
        
        if not self.player.is_alive():
            print(f"\n💀 {self.player.name} has fallen!")
            self.state = Combat.COMBAT_END
        else:
            self.state = Combat.PLAYER_TURN
    
    def get_result(self):
        """Return the combat result: 'victory', 'defeat', or 'fled'."""
        if not self.enemy.is_alive():
            return "victory"
        elif not self.player.is_alive():
            return "defeat"
        else:
            return "fled"


# =============================================================================
# Main Game Class
# =============================================================================

# YOUR CODE: Build the main Game class

class Game:
    """Main game controller."""
    
    # Game states
    EXPLORING = "exploring"
    IN_COMBAT = "in_combat"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    
    def __init__(self):
        self.player = None
        self.current_location = None
        self.state = Game.EXPLORING
        self.game_running = True
        
        # Timer + win condition
        self.turns_left = 35
        self.ducklings_needed = {"Duckling: Pip", "Duckling: Mip", "Duckling: Sip"}
    
    def start(self):
        """Initialize and start the game."""
        self.show_intro()
        self.create_player()
        self.current_location = create_world()  # Your function from earlier
        self.current_location.describe()
        
        # Main game loop
        while self.game_running:
            if self.state == Game.EXPLORING:
                self.exploration_loop()
            elif self.state == Game.GAME_OVER:
                self.show_game_over()
                break
            elif self.state == Game.VICTORY:
                self.show_victory()
                break
    
    def show_intro(self):
        """Display the game introduction."""
        print("\n" + "="*60)
        print("      🦆 SIR QUACKS-A-LOT: CENTRAL PARK RESCUE 🦆")
        print("="*60)
        print("\nQuackie O is on a much-needed vacation.")
        print("You had ONE JOB: watch Pip, Mip, and Sip.")
        print("You turned around for ONE SECOND… and the ducklings vanished into Central Park.")
        print("Find all three ducklings before Quackie O gets home!")
        print("\n" + "="*60)
    
    def create_player(self):
        """Create the player character."""
        # If you want to keep the prompt, you can—but your story is best fixed to Sir Quacks-a-Lot.
        self.player = Player("Sir Quacks-a-Lot")
        print("\nYou are Sir Quacks-a-Lot. Time to find your ducklings...")
    
    def exploration_loop(self):
        """Handle player input during exploration."""
        print("\nWhat do you do? (type 'help' for commands)")
        command = input("> ").lower().strip()
        
        # Parse the command
        parts = command.split()
        if not parts:
            return
        
        action = parts[0]
        
        if action == "help":
            self.show_help()
        
        elif action == "look":
            self.current_location.describe()
        
        elif action == "go" and len(parts) > 1:
            direction = parts[1]
            self.move(direction)
        
        elif action in ["north", "south", "east", "west", "up", "down"]:
            self.move(action)
        
        elif action in ["fight", "attack"]:
            self.initiate_combat()
        
        elif action in ["inventory", "i"]:
            self.player.show_inventory()
        
        elif action == "take" and len(parts) > 1:
            item_query = " ".join(parts[1:])
            self.take_item(item_query)
        
        elif action == "quit":
            print("Thanks for playing!")
            self.game_running = False
        
        elif action == "use" and len(parts) > 1:
            item_query = " ".join(parts[1:])
            self.use_item(item_query)
        
        elif action == "talk" and len(parts) > 1:
            who = " ".join(parts[1:])
            self.talk_to(who)
        
        else:
            print("I don't understand that command. Type 'help' for options.")
    
    def move(self, direction):
        """Move the player in the specified direction."""
        if direction in self.current_location.connections:
            self.current_location = self.current_location.connections[direction]
            self.current_location.describe()

            # Auto-trigger combat if a living enemy is here
            if any(e.is_alive() for e in self.current_location.enemies):
                print("\n⚠️ An enemy is here!")
                self.initiate_combat()
                if self.state != Game.EXPLORING:
                    return

            self.end_turn()
        else:
            print(f"You can't go {direction} from here.")
    
    def take_item(self, item_query):
        """Pick up an item by partial name match."""
        for item in list(self.current_location.items):
            if item_query.lower() in item.lower():
                self.player.pick_up(item)
                self.current_location.items.remove(item)

                if item.startswith("Duckling:"):
                    print("🦆 You found one of your ducklings!!")

                self.end_turn()
                return
        print("You don't see that here.")
    
    def talk_to(self, who_query):
        """Talk to an NPC in the current location (implemented as an item token)."""
        # Look for an NPC "item" in the room
        npc = None
        for thing in self.current_location.items:
            if who_query.lower() in thing.lower():
                npc = thing
                break

        if not npc:
            print("There’s no one like that here to talk to.")
            return

        # Old Man interaction
        if npc == "Old Man":
            print("\n👴 Old Man: 'Ahh… a hardworking duck dad. How nice!'")
            print("👴 Old Man: 'Here, take some bread. You look like you need it.'")
            print("🍞 You receive: Fresh Bread")

            # Give the player a usable item
            self.player.pick_up("Fresh Bread")

            # Optional: small heal right away (feels like he “feeds” you)
            if hasattr(self.player, "heal"):
                self.player.heal(5)

            # Remove the NPC so it only happens once
            self.current_location.items.remove("Old Man")

            self.end_turn()
            return

        print("They don’t have anything to say right now.")
    
    def initiate_combat(self):
        """Start combat with an enemy in the current location."""
        living_enemies = [e for e in self.current_location.enemies if e.is_alive()]
        if not living_enemies:
            print("There's nothing to fight here.")
            return
        
        enemy = living_enemies[0]  # Fight first living enemy
        battle = Combat(self.player, enemy)
        result = battle.start()
        
        if result == "victory":
            self.current_location.enemies.remove(enemy)
            self.end_turn()
        elif result == "defeat":
            self.state = Game.GAME_OVER
        else:  # fled
            # fleeing still costs time 
            self.end_turn()
    
    def check_victory(self):
        """Return True if player has all ducklings."""
        return self.ducklings_needed.issubset(set(self.player.inventory))
    
    def use_item(self, item_query):
        """Use an item from inventory by partial name match."""
        # Find item in inventory
        chosen = None
        for item in self.player.inventory:
            if item_query.lower() in item.lower():
                chosen = item
                break

        if not chosen:
            print("You don't have that item.")
            return

        # Item effects
        effects = {
            "Band-Aid": ("heal", 6),
            "Bread Crumbs": ("strength", 1),
            "Shiny Pebble": ("defense", 1),
            "Protein Hot Dog": ("strength", 2),
            "Pond Water Espresso": ("heal", 12),
            "Fresh Bread": ("strength", 2),
        }

        if chosen not in effects:
            print(f"{chosen} doesn't seem usable right now.")
            return

        effect_type, amount = effects[chosen]

        if effect_type == "heal":
            self.player.heal(amount)
        elif effect_type == "strength":
            self.player.boost_strength(amount)
        elif effect_type == "defense":
            self.player.boost_defense(amount)

        # Remove the item after using it 
        self.player.inventory.remove(chosen)
        print(f"✅ Used: {chosen}")

        self.end_turn()
    
    def end_turn(self):
        """After meaningful actions, reduce turns and check win/lose."""
        # Win check first so grabbing the last duckling wins instantly
        if self.check_victory():
            self.state = Game.VICTORY
            return
        
        self.turns_left -= 1
        print(f"⏳ Time left until Quackie O gets home: {self.turns_left} turns")
        
        if self.turns_left <= 0:
            self.state = Game.GAME_OVER
            print("\n🚨 QUACKIE O IS HOME.")
            print("She looks around… then looks at you.")
            print("😡 'Where. Are. The. Ducklings.'")
    
    def show_help(self):
        """Display available commands."""
        print("\n📜 AVAILABLE COMMANDS:")
        print("  go [direction] - Move (north, south, east, west)")
        print("  look          - Examine your surroundings")
        print("  take [item]   - Pick up an item (try: take pip)")
        print("  fight         - Start combat if an enemy is here")
        print("  inventory     - Check your inventory")
        print("  help          - Show this help message")
        print("  quit          - Exit the game")
        print("  use [item]    - Use an item from your inventory (try: use band-aid)")
        print("  talk [person] - Talk to someone nearby (try: talk old man)")
    
    def show_game_over(self):
        """Display game over message."""
        print("\n" + "="*60)
        print("                    GAME OVER")
        print("="*60)
        print("\nQuackie O is home… and the ducklings aren’t.")
        print("You are in HUGE trouble.")
        print("\n(But you can always try again!)")
    
    def show_victory(self):
        """Display victory message."""
        print("\n" + "="*60)
        print("                    🎉 VICTORY! 🎉")
        print("="*60)
        print("\nPip, Mip, and Sip are safe and accounted for.")
        print("Quackie O returns relaxed… and proud.")
        print("🦆 Family reunited. Parenting: SUCCESS.")

# =============================================================================
# Run the Game
# =============================================================================

if __name__ == "__main__":
    game = Game()
    game.start()
