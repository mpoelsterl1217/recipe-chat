cooking_verbs = [
    "Chop", "Slice", "Dice", "Mince", "Peel", "Grate", "Shred", "Crush", "Mash", "Tenderize",
    "Stir", "Whisk", "Beat", "Knead", "Mix",
    "Bake", "Broil", "Roast", "Grill", "Fry", "Deep-fry", "Sauté", "Steam", "Boil", "Simmer", 
    "Poach", "Blanch", "Slow-cook", "Pressure-cook",
    "Deglaze", "Flambé", "Braise", "Poach", "Marinate", "Infuse", "Caramelize", "Clarify", 
    "En Papillote", "Sous-vide",
    "Plate", "Garnish", "Drizzle", "Sprinkle", "Glaze", "Toast",
    "Melt", "Set", "Reduce", "Thicken", "Zest",
    "Smoke", "Cure", "Dry", "Freeze", "Shake", "Refrigerate", "Squeeze",
    "Heat", "Microwave"
]
cooking_verbs = [item.lower() for item in cooking_verbs]

cooking_tools = [
    "Knife", "Fork", "Spoon", "Spatula", "Whisk", "Tongs", "Ladle", "Slotted spoon", "Peeler", 
    "Grater", "Pestle", "Mortar", "Mandoline", "Rolling pin", "Strainer", "Colander", "Corkscrew", 
    "Can opener", "Sieve", "Measuring cup", "Measuring spoon", "Basting brush", "Basting spoon", 
    "Scissors", "Funnel", "Zester", "Tongs", "Tong spatula", "Pastry brush",
    "Pan", "Frying pan", "Saucepan", "Skillet", "Wok", "Dutch oven", "Stock pot", "Roasting pan", 
    "Casserole dish", "Grill pan", "Baking dish", "Pie dish", "Baking sheet", "Muffin tin", 
    "Cake pan", "Springform pan", "Pizza stone", "Cookie sheet", "Loaf pan", "Bundt pan", 
    "Ramekin", "Crockpot", "Pressure cooker", "Slow cooker", "Steamer", "Tagine",
    "Blender", "Food processor", "Stand mixer", "Hand mixer", "Microwave", "Toaster", "Toaster oven", 
    "Coffee maker", "Espresso machine", "Grinder", "Rice cooker", "Bread maker", "Juicer", 
    "Electric grill", "Induction cooker", "Air fryer", "Dehydrator", "Immersion blender",
    "Pastry cutter", "Rolling pin", "Dough scraper", "Cookie cutter", "Baking mat", "Piping bag", 
    "Cooling rack", "Sifter", "Cake tester", "Rolling board", "Bench scraper", "Cake stand",
    "Kitchen scale", "Thermometer", "Timer", "Oven thermometer", "Candy thermometer", 
    "Liquid measuring cup", "Dry measuring cup", "Bowl",
    "Cutting board", "Mixing bowl", "Spoon rest", "Chopping block", "Trivet", "Towel", "Pot holder", 
    "Oven mitt", "Casserole carrier", "Breadbox", "Baking stone", "Cling film", "Aluminum foil", 
    "Wax paper", "Parchment paper", "Silicone mat", "Vacuum sealer", "Food storage container", 
    "Salt shaker", "Pepper grinder", "Spice rack", "Stove", "Burner", "Oven"
]
cooking_tools = [item.lower() for item in cooking_tools]

def in_verbs_list(word):
    return word in cooking_verbs
def in_tools_list(word):
    return word in cooking_tools