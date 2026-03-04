# Game Design Document

## Theme / Setting
[What's your theme? Fantasy, sci-fi, horror, action movie, etc.?]
My theme is a family friendly action game. You play as a duck named Sir Quacks-a-Lot. Sir Quacks-a-Lot is a family man who has a wife named Quackie O and 3 beautiful ducklings named Pip, Mip, and Sip. Sir Quacks-a-Lot was in charge of watching the kids for a day while Quackie O gets a much neeeded vacation. Unfortunatley while Sir Quacks-a-Lot had his back turned for a second all of the little ducklings disapeared. Now Sir Quacks-a-Lot needs to venture through diffrent locations in central park to find his three missing ducklings before Quackie O gets back and he gets in huge trouble. 

## Player's Goal
[What does the player need to accomplish to win?]
The goal is to serch central park and try and find Pip, Mip, and Sip before the time runs out (aka Quackie O gets home and realizes the ducklings are missing). Also while collecting items and fighting off enemies. 

## Locations (4-6)
[List your locations and sketch how they connect]
The locations will be all in central park as a whole but the specific: 
    * the Quacks-a-Lot home 
    * a pond 
    * a hot dog stand 
    * a playground 
    * Belvedere Castle
    * Cherry Hill
    * Strawberry Fields

```
[Your map here]
                       [Strawberry Fields]
                               |
                               | south / north
                               |
                         [Cherry Hill] <----> [The Pond] <----> [Belvedere Castle]
                               |                 ^
                               |                 |
                               |                 | south / north
                               |                 |
                        (no other exits)     [Playground] <----> [Hot Dog Stand]
                                               |
                                               |
                                               | south / north
                                               |
                                         [Quacks-a-Lot Home]
```

## Enemies (2-4 types)
[Describe your enemy types and their stats/behaviors]
### Enemy Types

| Enemy | Health | Strength | Defense | Behavior |
|------|------|------|------|------|
| Overexcited Kid | 10 | 2 | 9 | Runs at Sir Quacks-a-Lot yelling “DUCKYYY!” Weak but annoying. |
| Raccoon | 16 | 3 | 11 | Scrappy park raccoon that attacks if you get near food areas. |
| Off-Leash Dog | 22 | 4 | 12 | Charges with full zoomies. Stronger and harder to beat. |
| Snapping Turtle | 28 | 5 | 13 | Mini-boss near the pond. Slow but very tough and dangerous. |

## Win Condition
[How does the player win?]
The player wins by finding all three missing ducklings (Pip, Mip, and Sip) somewhere around Central Park. Once all three ducklings are collected in Sir Quacks-a-Lot’s inventory, the game immediately ends in victory and the family is reunited before Quackie O gets home.

There is also a timer limiting how many turns the player has to explore the park. Every time the player moves, fights, or performs certain actions, a turn passes. If the timer runs out before all three ducklings are found, Quackie O returns home and the game ends in failure.

## Lose Condition
[How does the player lose?]
The player can lose in two ways. First, there is a turn timer representing how long Sir Quacks-a-Lot has before Quackie O gets home. Every time the player moves, fights, or performs certain actions, a turn passes. If the timer runs out before all three ducklings are found, Quackie O returns home and realizes the ducklings are missing, which ends the game.

The player can also lose if Sir Quacks-a-Lot is defeated during combat. Some enemies in the park, like raccoons, dogs, and snapping turtles, can deal damage during fights. If Sir Quacks-a-Lot’s health drops to zero, the game ends in defeat.

## Class Hierarchy
[Sketch your class design]

```
Character (base class)
├── Player
└── Enemy
    ├── ...
    └── ...

Location

Game

Character (base class)
├── Player
│   ├── inventory : list[str]
│   ├── pick_up(item)
│   ├── show_inventory()
│   ├── heal(amount)
│   ├── boost_strength(amount)
│   └── boost_defense(amount)
│
└── Enemy
    ├── LittleKid
    │   └── attack(target)  # custom flavor text + uses Character.attack
    ├── Raccoon
    │   └── attack(target)
    ├── OffLeashDog
    │   └── attack(target)
    └── SnappingTurtle
        └── attack(target)

Location
├── name : str
├── description : str
├── connections : dict[str, Location]   # directions -> other locations
├── enemies : list[Enemy]
├── items : list[str]
├── add_connection(direction, location)
├── get_exits()
└── describe()

Combat
├── player : Player
├── enemy : Enemy
├── state : {player_turn, enemy_turn, combat_end}
└── start()  # runs interactive combat loop (attack/run)

Game
├── player : Player
├── current_location : Location
├── state : {exploring, in_combat, game_over, victory}
├── turns_left : int
├── ducklings_needed : set[str]
├── start()
├── exploration_loop()
├── move(direction)
├── initiate_combat()
├── take_item(item_query)
├── use_item(item_query)
├── talk_to(who_query)
├── end_turn()
└── check_victory()
```

## Additional Notes
[Any other design decisions, ideas, or plans]
