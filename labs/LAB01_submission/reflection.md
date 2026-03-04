# Reflection: OOP Design Decisions

Write 2-3 paragraphs reflecting on your object-oriented design. Some questions to consider:

- Why did you structure your classes the way you did?
- What inheritance relationships did you use and why?
- What was challenging about managing multiple interacting objects?
- If you had more time, what would you refactor or add?
- How does this experience connect to working with OOP in analytics/ML codebases?

---

I structured the game around a few core classes because it made the whole project way easier to reason about and expand. I largly followed the structure that you gave us in the lab_01 file because in the begining I felt super overwhelmed and I thought it was very helpful to have an outline of what to do. So, I used Character as the base for anything that can fight (health, strength, defense, attack logic), then built Player and Enemy on top of that so they share the same combat “rules” without me rewriting code twice. That inheritance setup felt clean because the player and enemies are basically the same type of object in combat — the only real difference is the player has extra stuff like an inventory and item interactions.

The hardest part was honestly just keeping track of how everything interacts at once: locations contain enemies and items, the player moves between locations, combat temporarily takes over the input loop, and the game state has to switch correctly between exploring, combat, victory, and game over. Little logic issues show up fast (like trying to fight a defeated enemy, or forgetting to update the turn timer after certain actions), so it forced me to be consistent about where state updates happen. If I had more time, I’d refactor items into real Item objects instead of strings, so each item could have its own use() method and effect without needing a big mapping inside the Game class. I’d also add more NPC interactions (like the old man) and maybe a simple quest log so it feels more like an actual “mission” rather than just collecting things.

This connects a lot to OOP in analytics/ML codebases because the same design patterns show up all the time: you’ll have a base model class and then subclasses for different algorithms, shared utilities for preprocessing, and separate objects for data loading, evaluation, and metrics. The biggest similarity is that when multiple objects depend on each other (data objects, model objects, config objects, pipelines), things can get confusing fast unless you keep responsibilities clean and predictable. Building the game made it obvious why good class boundaries matter, it’s the difference between being able to add features quickly vs. breaking everything every time you change one thing. (which I did an embarrasing amount of times)
