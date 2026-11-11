from src.loaders.creature_loader import load_creature
for n in ["hobbit", "uruk", "ent", "dwarf"]:
    print(load_creature(f"data/creatures/{n}.ins"))