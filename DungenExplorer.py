import os
import random
import sys

# Helper function to clear the terminal screen
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def add_item(player, item, qty=1):
    player["inv"][item] = player["inv"].get(item, 0) + qty

# --- COMBAT SYSTEM ---
def combat(player, enemy):
    while player["hp"] > 0 and enemy["hp"] > 0:
        clear()
        print("=== BATTLE vs " + enemy["name"] + " ===")
        print("Your HP: " + str(player["hp"]) + "/" + str(player["max_hp"]) + " | Enemy HP: " + str(enemy["hp"]))
        if player["magic"]:
            print("Your TP: " + str(player["tp"]) + "/" + str(player["max_tp"]))
        print("------------------------------")
        
        # Display available options depending on if magic is unlocked
        print("1. FIGHT")
        if player["magic"]:
            print("2. DEFEND (Gain 30 TP)")
            print("3. ITEM")
            print("4. MAGIC")
        else:
            print("2. ITEM")
        
        choice = input("Action: ").strip()
        is_defending = False
        action_valid = False
        
        if choice == "1":
            print("\nStyles: 1. SAFE  2. MODERN  3. RISK")
            style = input("Select style: ").strip()
            if style == "3":
                if random.random() < 0.6:
                    dmg = int(player["atk"] * 1.8)
                else:
                    dmg = int(player["atk"] * 0.5)
            elif style == "2":
                dmg = random.randint(int(player["atk"] * 0.9), int(player["atk"] * 1.3))
            else:
                dmg = int(player["atk"] * 0.8)
            
            enemy["hp"] -= dmg
            print("\nYou dealt " + str(dmg) + " damage!")
            
            # Gain TP from attacking ONLY if magic is unlocked
            if player["magic"]:
                player["tp"] = min(player["max_tp"], player["tp"] + 10)
                print("Gained 10 TP from attacking!")
            action_valid = True
                
        elif choice == "2" and player["magic"]:
            # DEFEND option (Only available after magic is unlocked)
            is_defending = True
            player["tp"] = min(player["max_tp"], player["tp"] + 30)
            print("\nYou take a defensive stance to block damage and gain 30 TP!")
            action_valid = True

        elif (choice == "2" and not player["magic"]) or (choice == "3" and player["magic"]):
            # ITEM option
            if not player["inv"]:
                print("\nInventory is empty! You lost your turn.")
                action_valid = True
            else:
                print("\n=== INVENTORY ===")
                for k, v in player["inv"].items():
                    print("- " + k + ": " + str(v))
                if input("Use Potion? (y/n): ").lower() == 'y':
                    if player["inv"].get("Potion", 0) > 0:
                        player["inv"]["Potion"] -= 1
                        if player["inv"]["Potion"] == 0:
                            del player["inv"]["Potion"]
                        heal = random.randint(20, 35)
                        player["hp"] = min(player["max_hp"], player["hp"] + heal)
                        print("\nRestored " + str(heal) + " HP!")
                        action_valid = True
                    else:
                        print("\nYou don't have any Potions!")

        elif choice == "4" and player["magic"]:
            # MAGIC option
            print("\n=== SPELLS ===")
            spells_list = player["spells"]
            costs = {
                "Spark": (15, 22), 
                "Heal": (20, 30), 
                "Blast": (35, 48), 
                "Storm": (55, 75)
            }
            
            for i, sp in enumerate(spells_list, 1):
                cost, power = costs[sp]
                if sp == "Heal":
                    print(str(i) + ". " + sp + " (Cost: " + str(cost) + " TP | Restores up to " + str(power) + " HP)")
                else:
                    print(str(i) + ". " + sp + " (Cost: " + str(cost) + " TP | Deals " + str(power) + " Damage)")
            
            sp_choice = input("Select spell number (or Enter to cancel): ").strip()
            try:
                idx = int(sp_choice) - 1
                if 0 <= idx < len(spells_list):
                    spell = spells_list[idx]
                    cost, val = costs[spell]
                    if player["tp"] >= cost:
                        player["tp"] -= cost
                        if spell == "Heal":
                            player["hp"] = min(player["max_hp"], player["hp"] + val)
                            print("\nCast Heal! Restored " + str(val) + " HP!")
                        else:
                            enemy["hp"] -= val
                            print("\nCast " + spell + " for " + str(val) + " damage!")
                        action_valid = True
                    else:
                        print("\nNot enough TP to cast " + spell + "!")
            except ValueError:
                print("\nCancelled spell selection.")

        # Victory check
        if enemy["hp"] <= 0:
            print("\nVictory! Defeated " + enemy["name"] + "!")
            player["gold"] += enemy.get("gold", 10)
            print("Gained " + str(enemy.get("gold", 10)) + " gold!")
            if random.random() < 0.5: 
                add_item(player, "Potion")
                print("Found a Potion!")
            if random.random() < 0.4: 
                add_item(player, "TP Crystal")
                print("Found a TP Crystal!")
            input("\nPress Enter to continue...")
            break
            
        # Enemy counterattack phase
        if action_valid:
            raw_dmg = random.randint(enemy["mind"], enemy["maxd"])
            current_def = player["def"] * 2 if is_defending else player["def"]
            edmg = max(1, raw_dmg - current_def)
            player["hp"] = max(0, player["hp"] - edmg)
            print(enemy["name"] + " hits you for " + str(edmg) + " damage!")
            input("\nPress Enter to continue...")

# --- PROGRESSION ---
def check_unlocks(player):
    r = player["rooms"]
    if r >= 5 and not player["magic"]:
        player["magic"] = True
        player["spells"].append("Spark")
        print("\n*** MAGICAL AWAKENING! TP BAR AND SPARK UNLOCKED ***")
    if r >= 8 and "Heal" not in player["spells"]: 
        player["spells"].append("Heal")
        print("\n*** UNLOCKED SPELL: HEAL ***")
    if r >= 12 and "Blast" not in player["spells"]: 
        player["spells"].append("Blast")
        print("\n*** UNLOCKED SPELL: BLAST ***")
    if r >= 16 and "Storm" not in player["spells"]: 
        player["spells"].append("Storm")
        print("\n*** UNLOCKED SPELL: STORM ***")

def explore(player, streak):
    # Reset TP to 0 at the start of every room
    player["tp"] = 0
    
    chances = [0.5, 0.65, 0.8, 0.95]
    if streak < 4:
        item_chance = chances[streak]
    else:
        item_chance = 1.0
    
    clear()
    if random.random() < item_chance:
        print("=== ITEM ROOM ===")
        gold = random.randint(10, 30)
        player["gold"] += gold
        print("Found " + str(gold) + " gold!")
        if random.random() < 0.6: 
            add_item(player, "Potion")
            print("Found a Potion!")
        streak = 0
    else:
        streak += 1
        r = player["rooms"]
        if r > 0 and r % 5 == 0:
            e = {"name": "Dungeon Boss", "hp": 130, "mind": 15, "maxd": 25, "gold": 50}
        else:
            types = [
                {"name": "Slime", "hp": random.randint(20, 35), "mind": 3, "maxd": 7, "gold": 10},
                {"name": "Goblin", "hp": random.randint(30, 50), "mind": 6, "maxd": 12, "gold": 18},
                {"name": "Dark Knight", "hp": random.randint(55, 85), "mind": 10, "maxd": 18, "gold": 30}
            ]
            if r < 3:
                e = random.choice(types[:2])
            else:
                e = random.choice(types)
        combat(player, e)
        
    player["rooms"] += 1
    check_unlocks(player)
    input("\nPress Enter to return to menu...")
    return streak

# --- MAIN GAME LOOP ---
def start_game():
    while True:
        clear()
        print("========================================")
        print("      WELCOME TO DUNGEON EXPLORER!      ")
        print("========================================")
        name = input("Enter your hero's name: ").strip()
        if name == "":
            name = "Hero"

        player = {
            "name": name, "hp": 100, "max_hp": 100, "atk": 10, "def": 2, 
            "gold": 0, "inv": {}, "rooms": 0, "tp": 0, "max_tp": 100, 
            "magic": False, "spells": []
        }
        streak = 0

        # Exploration and Menu loop
        while player["hp"] > 0:
            clear()
            print("========================================")
            print(" DUNGEON EXPLORER | Hero: " + player["name"])
            print("========================================")
            print("HP: " + str(player["hp"]) + "/" + str(player["max_hp"]) + " | Gold: " + str(player["gold"]) + " | Rooms: " + str(player["rooms"]))
            if player["magic"]:
                print("TP: " + str(player["tp"]) + "/" + str(player["max_tp"]))
            print("----------------------------------------")
            print("1. Explore Next Room")
            print("2. Check Inventory")
            print("3. Quit")
            
            choice = input("Option (1-3): ").strip()
            if choice == "1":
                streak = explore(player, streak)
            elif choice == "2":
                clear()
                print("=== INVENTORY ===")
                if not player["inv"]:
                    print("Inventory is empty.")
                else:
                    for k, v in player["inv"].items():
                        print("- " + k + ": " + str(v))
                input("\nPress Enter to return...")
            elif choice == "3":
                sys.exit()

        # Game Over Prompt
        clear()
        print("GAME OVER! You cleared " + str(player["rooms"]) + " rooms.")
        retry = input("Try again? (y/n): ").strip().lower()
        if retry != "y":
            print("\nThanks for playing! Safe travels.")
            sys.exit()

if __name__ == "__main__":
    start_game()