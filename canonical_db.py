"""
================================================================================
🗡️ ZELDA NOTES — CANONICAL GAME DATABASE & COMPREHENSIVE LOOKUP TABLE
================================================================================
Single Source of Truth for The Legend of Zelda: Ocarina of Time (NX2navi / PC Recomp)
Consolidates all static game constants, tables, entities, collectibles, maps,
time states, and memory schemas into a unified matching engine.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# ==============================================================================
# 1. COMPREHENSIVE ITEMS & EQUIPMENT CATALOG
# ==============================================================================
ITEMS_CATALOG = {
    # Swords
    "Weapon_Sword_Kokiri": {"id": "Weapon_Sword_Kokiri", "name": "Espada Kokiri", "category": "weapon", "slot": "sword", "icon": "sword", "age": "child", "attack": 1},
    "Weapon_Sword_Master": {"id": "Weapon_Sword_Master", "name": "Espada Maestra", "category": "weapon", "slot": "sword", "icon": "sword-gold", "age": "adult", "attack": 2},
    "Weapon_Sword_Biggoron": {"id": "Weapon_Sword_Biggoron", "name": "Espada Biggoron", "category": "weapon", "slot": "sword", "icon": "sword-heavy", "age": "adult", "attack": 4},
    "Weapon_Sword_GiantsKnife": {"id": "Weapon_Sword_GiantsKnife", "name": "Cuchillo de Gigante", "category": "weapon", "slot": "sword", "icon": "sword-heavy", "age": "adult", "attack": 4},
    
    # Shields
    "Weapon_Shield_Deku": {"id": "Weapon_Shield_Deku", "name": "Escudo Deku", "category": "shield", "slot": "shield", "icon": "shield-wood", "age": "child", "burnable": True},
    "Weapon_Shield_Hylian": {"id": "Weapon_Shield_Hylian", "name": "Escudo Hyliano", "category": "shield", "slot": "shield", "icon": "shield", "age": "both", "burnable": False},
    "Weapon_Shield_Mirror": {"id": "Weapon_Shield_Mirror", "name": "Escudo Espejo", "category": "shield", "slot": "shield", "icon": "shield", "age": "adult", "burnable": False},

    # Tunics
    "Armor_Tunic_Kokiri": {"id": "Armor_Tunic_Kokiri", "name": "Túnica Kokiri (Verde)", "category": "armor", "slot": "tunic", "icon": "tunic-green", "age": "both"},
    "Armor_Tunic_Goron": {"id": "Armor_Tunic_Goron", "name": "Túnica Goron (Roja)", "category": "armor", "slot": "tunic", "icon": "tunic-red", "age": "adult", "effect": "heat_resistance"},
    "Armor_Tunic_Zora": {"id": "Armor_Tunic_Zora", "name": "Túnica Zora (Azul)", "category": "armor", "slot": "tunic", "icon": "tunic-blue", "age": "adult", "effect": "water_breathing"},

    # Boots
    "Armor_Boots_Kokiri": {"id": "Armor_Boots_Kokiri", "name": "Botas Kokiri", "category": "boots", "slot": "boots", "icon": "boots", "age": "both"},
    "Armor_Boots_Iron": {"id": "Armor_Boots_Iron", "name": "Botas de Hierro", "category": "boots", "slot": "boots", "icon": "boots", "age": "adult", "effect": "sink_heavy"},
    "Armor_Boots_Hover": {"id": "Armor_Boots_Hover", "name": "Botas Flotantes", "category": "boots", "slot": "boots", "icon": "boots", "age": "adult", "effect": "hover"},

    # 24 Inventory C-Items
    "Item_Stick": {"id": "Item_Stick", "name": "Palos Deku", "category": "item", "c_slot": 0, "icon": "stick", "age": "child"},
    "Item_Nut": {"id": "Item_Nut", "name": "Nueces Deku", "category": "item", "c_slot": 1, "icon": "nut", "age": "both"},
    "Item_Bomb": {"id": "Item_Bomb", "name": "Bombas", "category": "item", "c_slot": 2, "icon": "bomb", "age": "both"},
    "Item_Bow": {"id": "Item_Bow", "name": "Arco de las Hadas", "category": "bow", "c_slot": 3, "icon": "bow", "age": "adult"},
    "Item_Arrow_Fire": {"id": "Item_Arrow_Fire", "name": "Flechas de Fuego", "category": "magic_arrow", "c_slot": 4, "icon": "arrow-fire", "age": "adult", "magic_cost": 2},
    "Item_Dins_Fire": {"id": "Item_Dins_Fire", "name": "Fuego de Din", "category": "spell", "c_slot": 5, "icon": "spell-fire", "age": "both", "magic_cost": 6},
    "Item_Slingshot": {"id": "Item_Slingshot", "name": "Tirachinas de las Hadas", "category": "tool", "c_slot": 6, "icon": "slingshot", "age": "child"},
    "Item_Ocarina_Fairy": {"id": "Item_Ocarina_Fairy", "name": "Ocarina del Hada", "category": "key", "c_slot": 7, "icon": "ocarina", "age": "child"},
    "Item_Ocarina_Time": {"id": "Item_Ocarina_Time", "name": "Ocarina del Tiempo", "category": "key", "c_slot": 7, "icon": "ocarina-gold", "age": "both"},
    "Item_Bombchu": {"id": "Item_Bombchu", "name": "Bombchus", "category": "item", "c_slot": 8, "icon": "bombchu", "age": "both"},
    "Item_Hookshot": {"id": "Item_Hookshot", "name": "Gancho (Hookshot)", "category": "tool", "c_slot": 9, "icon": "hook", "age": "adult"},
    "Item_Longshot": {"id": "Item_Longshot", "name": "Supergancho (Longshot)", "category": "tool", "c_slot": 9, "icon": "hook", "age": "adult"},
    "Item_Arrow_Ice": {"id": "Item_Arrow_Ice", "name": "Flechas de Hielo", "category": "magic_arrow", "c_slot": 10, "icon": "arrow-ice", "age": "adult", "magic_cost": 2},
    "Item_Farores_Wind": {"id": "Item_Farores_Wind", "name": "Viento de Farore", "category": "spell", "c_slot": 11, "icon": "spell-wind", "age": "both", "magic_cost": 6},
    "Item_Boomerang": {"id": "Item_Boomerang", "name": "Bumerán", "category": "tool", "c_slot": 12, "icon": "boomerang", "age": "child"},
    "Item_Lens": {"id": "Item_Lens", "name": "Lente de la Verdad", "category": "tool", "c_slot": 13, "icon": "eye", "age": "both", "magic_drain": True},
    "Item_Beans": {"id": "Item_Beans", "name": "Judías Mágicas", "category": "item", "c_slot": 14, "icon": "bean", "age": "child"},
    "Item_Hammer": {"id": "Item_Hammer", "name": "Martillo Megatón", "category": "tool", "c_slot": 15, "icon": "hammer", "age": "adult"},
    "Item_Arrow_Light": {"id": "Item_Arrow_Light", "name": "Flechas de Luz", "category": "magic_arrow", "c_slot": 16, "icon": "arrow-light", "age": "adult", "magic_cost": 4},
    "Item_Nayrus_Love": {"id": "Item_Nayrus_Love", "name": "Amor de Nayru", "category": "spell", "c_slot": 17, "icon": "spell-shield", "age": "both", "magic_cost": 12},

    # Bottles (Slots 18 to 21)
    "Item_Bottle_Empty": {"id": "Item_Bottle_Empty", "name": "Botella Vacía", "category": "bottle", "icon": "bottle"},
    "Item_Bottle_Red_Potion": {"id": "Item_Bottle_Red_Potion", "name": "Poción Roja (Vida)", "category": "bottle", "icon": "potion-red"},
    "Item_Bottle_Green_Potion": {"id": "Item_Bottle_Green_Potion", "name": "Poción Verde (Magia)", "category": "bottle", "icon": "potion-green"},
    "Item_Bottle_Blue_Potion": {"id": "Item_Bottle_Blue_Potion", "name": "Poción Azul (Vida + Magia)", "category": "bottle", "icon": "potion-blue"},
    "Item_Bottle_Fairy": {"id": "Item_Bottle_Fairy", "name": "Hada en Botella", "category": "bottle", "icon": "fairy"},
    "Item_Bottle_Fish": {"id": "Item_Bottle_Fish", "name": "Pescado", "category": "bottle", "icon": "fish"},
    "Item_Bottle_Milk": {"id": "Item_Bottle_Milk", "name": "Leche Lon Lon", "category": "bottle", "icon": "milk"},
    "Item_Bottle_Rutos_Letter": {"id": "Item_Bottle_Rutos_Letter", "name": "Carta de la Princesa Ruto", "category": "bottle", "icon": "letter"},
    "Item_Bottle_Blue_Fire": {"id": "Item_Bottle_Blue_Fire", "name": "Fuego Azul", "category": "bottle", "icon": "fire-blue"},
    "Item_Bottle_Bug": {"id": "Item_Bottle_Bug", "name": "Bichos en Botella", "category": "bottle", "icon": "bug"},
    "Item_Bottle_Big_Poe": {"id": "Item_Bottle_Big_Poe", "name": "Gran Poe", "category": "bottle", "icon": "poe-gold"},
    "Item_Bottle_Poe": {"id": "Item_Bottle_Poe", "name": "Espíritu Poe", "category": "bottle", "icon": "poe"},

    # Child Trade Sequence (Slot 22)
    "Trade_Child_Weird_Egg": {"id": "Trade_Child_Weird_Egg", "name": "Huevo Extraño", "category": "trade_child", "c_slot": 22},
    "Trade_Child_Chicken": {"id": "Trade_Child_Chicken", "name": "Cuco", "category": "trade_child", "c_slot": 22},
    "Trade_Child_Zeldas_Letter": {"id": "Trade_Child_Zeldas_Letter", "name": "Carta de Zelda", "category": "trade_child", "c_slot": 22},
    "Trade_Child_Keaton_Mask": {"id": "Trade_Child_Keaton_Mask", "name": "Máscara Keaton", "category": "mask", "c_slot": 22},
    "Trade_Child_Skull_Mask": {"id": "Trade_Child_Skull_Mask", "name": "Máscara Calavera", "category": "mask", "c_slot": 22},
    "Trade_Child_Spooky_Mask": {"id": "Trade_Child_Spooky_Mask", "name": "Máscara Espeluznante", "category": "mask", "c_slot": 22},
    "Trade_Child_Bunny_Hood": {"id": "Trade_Child_Bunny_Hood", "name": "Capucha de Conejo", "category": "mask", "c_slot": 22},
    "Trade_Child_Mask_Of_Truth": {"id": "Trade_Child_Mask_Of_Truth", "name": "Máscara de la Verdad", "category": "mask", "c_slot": 22},

    # Adult Trade Sequence (Slot 23)
    "Trade_Adult_Pocket_Egg": {"id": "Trade_Adult_Pocket_Egg", "name": "Huevo de Bolsillo", "category": "trade_adult", "c_slot": 23},
    "Trade_Adult_Pocket_Cucco": {"id": "Trade_Adult_Pocket_Cucco", "name": "Cuco de Bolsillo", "category": "trade_adult", "c_slot": 23},
    "Trade_Adult_Cojiro": {"id": "Trade_Adult_Cojiro", "name": "Cojiro (Cuco Azul)", "category": "trade_adult", "c_slot": 23},
    "Trade_Adult_Odd_Mushroom": {"id": "Trade_Adult_Odd_Mushroom", "name": "Seta Extraña", "category": "trade_adult", "c_slot": 23},
    "Trade_Adult_Odd_Potion": {"id": "Trade_Adult_Odd_Potion", "name": "Poción Extraña", "category": "trade_adult", "c_slot": 23},
    "Trade_Adult_Poachers_Saw": {"id": "Trade_Adult_Poachers_Saw", "name": "Sierra del Furtivo", "category": "trade_adult", "c_slot": 23},
    "Trade_Adult_Broken_Sword": {"id": "Trade_Adult_Broken_Sword", "name": "Espada de Goron Rota", "category": "trade_adult", "c_slot": 23},
    "Trade_Adult_Prescription": {"id": "Trade_Adult_Prescription", "name": "Prescripción Médica", "category": "trade_adult", "c_slot": 23},
    "Trade_Adult_Eyeball_Frog": {"id": "Trade_Adult_Eyeball_Frog", "name": "Rana de Ojos Saltones", "category": "trade_adult", "c_slot": 23},
    "Trade_Adult_Eye_Drops": {"id": "Trade_Adult_Eye_Drops", "name": "Gotas Oculares", "category": "trade_adult", "c_slot": 23},
    "Trade_Adult_Claim_Check": {"id": "Trade_Adult_Claim_Check", "name": "Comprobante de Reclamación", "category": "trade_adult", "c_slot": 23}
}

# ==============================================================================
# 2. UPGRADES CATALOG (Capacities & Equipment Tiers)
# ==============================================================================
UPGRADES_CATALOG = {
    "Wallet": [
        {"tier": 0, "name": "Billetera Infantil", "capacity": 99},
        {"tier": 1, "name": "Billetera de Adulto", "capacity": 200, "requirement": "10 Skulltulas"},
        {"tier": 2, "name": "Billetera Gigante", "capacity": 500, "requirement": "30 Skulltulas"}
    ],
    "BombBag": [
        {"tier": 1, "name": "Saco de Bombas", "capacity": 20},
        {"tier": 2, "name": "Saco de Bombas Grande", "capacity": 30, "location": "Goron City / Bolera Bombchu"},
        {"tier": 3, "name": "Saco de Bombas Gigante", "capacity": 40, "location": "Goron City / Bolera Bombchu"}
    ],
    "Quiver": [
        {"tier": 1, "name": "Carcaj de Hadas", "capacity": 30},
        {"tier": 2, "name": "Carcaj Grande", "capacity": 40, "location": "Tiro al blanco Kakariko"},
        {"tier": 3, "name": "Carcaj Gigante", "capacity": 50, "location": "Tiro con arco a caballo Gerudo"}
    ],
    "BulletBag": [
        {"tier": 1, "name": "Bolsa de Semillas", "capacity": 30},
        {"tier": 2, "name": "Bolsa de Semillas Mediana", "capacity": 40, "location": "Bosque Perdido (tiro al blanco)"},
        {"tier": 3, "name": "Bolsa de Semillas Grande", "capacity": 50, "location": "Plaza del Mercado"}
    ],
    "Strength": [
        {"tier": 1, "name": "Brazalete de Goron", "effect": "Levantar flores bomba", "age": "child"},
        {"tier": 2, "name": "Guanteletes de Plata", "effect": "Mover bloques de plata pesados", "age": "adult"},
        {"tier": 3, "name": "Guanteletes de Oro", "effect": "Levantar monolitos colosales", "age": "adult"}
    ],
    "DivingScale": [
        {"tier": 1, "name": "Escama de Plata", "depth": "6 metros", "location": "Juego de buceo en Dominio Zora"},
        {"tier": 2, "name": "Escama de Oro", "depth": "9 metros", "location": "Estanque de pesca (Lago Hylia)"}
    ],
    "MagicMeter": [
        {"tier": 1, "name": "Barra de Magia", "points": 24, "location": "Cima de la Montaña de la Muerte"},
        {"tier": 2, "name": "Barra de Magia Doble", "points": 48, "location": "Cráter de la Montaña de la Muerte"}
    ],
    "Defense": [
        {"tier": 1, "name": "Defensa Normal", "border": "red"},
        {"tier": 2, "name": "Doble Defensa", "border": "gold", "location": "Castillo de Ganondorf (Gran Hada)"}
    ]
}

# ==============================================================================
# 3. SONGS OF THE OCARINA (12 Melodies)
# ==============================================================================
SONGS_CATALOG = {
    "Zeldas_Lullaby": {"name": "Nana de Zelda", "notes": ["Left", "Up", "Right", "Left", "Up", "Right"], "type": "event", "effect": "Activar interruptores de la Familia Real y fuentes de hadas"},
    "Eponas_Song": {"name": "Canción de Epona", "notes": ["Up", "Left", "Right", "Up", "Left", "Right"], "type": "event", "effect": "Llamar a Epona y ordeñar vacas"},
    "Sarias_Song": {"name": "Canción de Saria", "notes": ["Down", "Right", "Left", "Down", "Right", "Left"], "type": "event", "effect": "Hablar con Saria y alegrar a Darunia"},
    "Suns_Song": {"name": "Canción del Sol", "notes": ["Right", "Down", "Up", "Right", "Down", "Up"], "type": "time", "effect": "Avanzar inmediatamente al amanecer (6:45 AM) o noche (8:22 PM), paralizar ReDeads"},
    "Song_of_Time": {"name": "Canción del Tiempo", "notes": ["Right", "A", "Down", "Right", "A", "Down"], "type": "event", "effect": "Abrir la Puerta del Tiempo y mover bloques del tiempo"},
    "Song_of_Storms": {"name": "Canción de las Tormentas", "notes": ["A", "Down", "Up", "A", "Down", "Up"], "type": "event", "effect": "Invocar lluvia y tormentas, vaciar el pozo de Kakariko"},
    "Minuet_of_Forest": {"name": "Minueto del Bosque", "notes": ["A", "Up", "Left", "Right", "Left", "Right"], "type": "warp", "warp_target": "prado", "location": "Prado Sagrado del Bosque"},
    "Bolero_of_Fire": {"name": "Bolero de Fuego", "notes": ["Down", "A", "Down", "A", "Right", "Down", "Right", "Down"], "type": "warp", "warp_target": "crater", "location": "Cráter de la Montaña de la Muerte"},
    "Serenade_of_Water": {"name": "Serenata del Agua", "notes": ["A", "Down", "Right", "Right", "Left"], "type": "warp", "warp_target": "lago", "location": "Lago Hylia"},
    "Nocturne_of_Shadow": {"name": "Nocturno de las Sombras", "notes": ["Left", "Right", "Right", "A", "Left", "Right", "Down"], "type": "warp", "warp_target": "cementerio", "location": "Cementerio de Kakariko"},
    "Requiem_of_Spirit": {"name": "Réquiem del Espíritu", "notes": ["A", "Down", "A", "Right", "Down", "A"], "type": "warp", "warp_target": "coloso", "location": "Coloso del Desierto"},
    "Prelude_of_Light": {"name": "Preludio de la Luz", "notes": ["Up", "Right", "Up", "Right", "Left", "Up"], "type": "warp", "warp_target": "ciudadela", "location": "Templo del Tiempo"}
}

# ==============================================================================
# 4. QUEST ITEMS: SPIRITUAL STONES & SAGE MEDALLIONS
# ==============================================================================
QUEST_ITEMS_CATALOG = {
    "Stones": {
        "Kokiri_Emerald": {"name": "Esmeralda Kokiri", "element": "Bosque", "guardian": "Gran Árbol Deku", "pedestal": "left"},
        "Goron_Ruby": {"name": "Rubí Goron", "element": "Fuego", "guardian": "Rey Darunia", "pedestal": "center"},
        "Zora_Sapphire": {"name": "Zafiro Zora", "element": "Agua", "guardian": "Princesa Ruto", "pedestal": "right"}
    },
    "Medallions": {
        "Light_Medallion": {"name": "Medallón de la Luz", "sage": "Rauru", "temple": "Templo de la Luz", "color": "#ffe600"},
        "Forest_Medallion": {"name": "Medallón del Bosque", "sage": "Saria", "temple": "Templo del Bosque", "color": "#00ff66"},
        "Fire_Medallion": {"name": "Medallón del Fuego", "sage": "Darunia", "temple": "Templo del Fuego", "color": "#ff3300"},
        "Water_Medallion": {"name": "Medallón del Agua", "sage": "Ruto", "temple": "Templo del Agua", "color": "#0099ff"},
        "Shadow_Medallion": {"name": "Medallón de las Sombras", "sage": "Impa", "temple": "Templo de las Sombras", "color": "#aa00ff"},
        "Spirit_Medallion": {"name": "Medallón del Espíritu", "sage": "Nabooru", "temple": "Templo del Espíritu", "color": "#ff9900"}
    }
}

# ==============================================================================
# 5. MASTER CELESTIAL CLOCK & DAY-NIGHT STATE ENGINE
# ==============================================================================
OOT_TIME_ENGINE_CONSTANTS = {
    "engine_rates": {
        "total_units_per_day": 65536,
        "seconds_per_day": 86400,
        "raw_ticks_per_second": 9.85,
        "real_seconds_per_game_minute": 45.5,
        "real_minutes_per_game_day": 18.2
    },
    "canonical_song_events": [
        {
            "id": "suns_song_dawn",
            "name": "Canción del Sol (Amanecer)",
            "raw_min": 0x47A0,
            "raw_max": 0x4880,
            "canonical_hex": 0x4800,
            "hour": 6,
            "minute": 45,
            "phase": "dawn",
            "icon": "🌅",
            "label": "Amanecer (Canción del Sol)",
            "ambient_color": "linear-gradient(135deg, rgba(255, 130, 45, 0.30) 0%, rgba(255, 75, 110, 0.22) 50%, rgba(35, 15, 65, 0.38) 100%)",
            "filter": "sepia(0.35) saturate(1.35) hue-rotate(-15deg) brightness(1.02)"
        },
        {
            "id": "suns_song_night",
            "name": "Canción del Sol (Noche)",
            "raw_min": 0xD900,
            "raw_max": 0xD990,
            "canonical_hex": 0xD940,
            "hour": 20,
            "minute": 22,
            "phase": "night",
            "icon": "🌙",
            "label": "Noche (Canción del Sol)",
            "ambient_color": "radial-gradient(circle at 50% 35%, rgba(15, 30, 80, 0.45) 0%, rgba(5, 10, 25, 0.7) 65%, rgba(2, 3, 10, 0.88) 100%)",
            "filter": "hue-rotate(190deg) saturate(1.15) brightness(0.78) contrast(1.15)"
        }
    ],
    "day_phases": [
        {
            "phase": "dawn",
            "hour_min": 5,
            "hour_max": 7,
            "icon": "🌅",
            "label": "Amanecer (Alba)",
            "ambient_color": "linear-gradient(135deg, rgba(255, 130, 45, 0.30) 0%, rgba(255, 75, 110, 0.22) 50%, rgba(35, 15, 65, 0.38) 100%)",
            "filter": "sepia(0.35) saturate(1.35) hue-rotate(-15deg) brightness(1.02)"
        },
        {
            "phase": "day",
            "hour_min": 7,
            "hour_max": 11,
            "icon": "☀️",
            "label": "Día (Mañana)",
            "ambient_color": "rgba(255, 240, 180, 0.08)",
            "filter": "none"
        },
        {
            "phase": "day",
            "hour_min": 11,
            "hour_max": 17,
            "icon": "☀️",
            "label": "Pleno Día",
            "ambient_color": "transparent",
            "filter": "none"
        },
        {
            "phase": "dusk",
            "hour_min": 17,
            "hour_max": 20,
            "icon": "🌆",
            "label": "Atardecer (Puesta de sol)",
            "ambient_color": "linear-gradient(135deg, rgba(255, 110, 30, 0.28) 0%, rgba(180, 40, 80, 0.2) 50%, rgba(15, 10, 40, 0.4) 100%)",
            "filter": "sepia(0.35) saturate(1.35) hue-rotate(-25deg)"
        },
        {
            "phase": "night",
            "hour_min": 20,
            "hour_max": 24,
            "icon": "🌙",
            "label": "Noche (Oscuridad)",
            "ambient_color": "radial-gradient(circle at 50% 35%, rgba(15, 30, 80, 0.45) 0%, rgba(5, 10, 25, 0.7) 65%, rgba(2, 3, 10, 0.88) 100%)",
            "filter": "hue-rotate(190deg) saturate(1.15) brightness(0.78) contrast(1.15)"
        },
        {
            "phase": "night",
            "hour_min": 0,
            "hour_max": 5,
            "icon": "🌙",
            "label": "Madrugada (Noche)",
            "ambient_color": "radial-gradient(circle at 50% 35%, rgba(15, 30, 80, 0.45) 0%, rgba(5, 10, 25, 0.7) 65%, rgba(2, 3, 10, 0.88) 100%)",
            "filter": "hue-rotate(190deg) saturate(1.15) brightness(0.78) contrast(1.15)"
        }
    ]
}

def export_canonical_json():
    """Generates static/canonical_game_db.json consolidating all modules"""
    # Load Places
    places_path = os.path.join(STATIC_DIR, "places_data.json")
    places_data = []
    if os.path.exists(places_path):
        with open(places_path, "r", encoding="utf-8") as f:
            places_data = json.load(f)

    # Load Transforms
    transforms_path = os.path.join(STATIC_DIR, "map_transforms.json")
    transforms_data = {}
    if os.path.exists(transforms_path):
        with open(transforms_path, "r", encoding="utf-8") as f:
            transforms_data = json.load(f)

    # Load Collectibles
    collectibles_path = os.path.join(STATIC_DIR, "nintenduo_content.json")
    collectibles_items = []
    collectibles_categories = []
    if os.path.exists(collectibles_path):
        with open(collectibles_path, "r", encoding="utf-8") as f:
            n_raw = json.load(f)
            collectibles_items = n_raw.get("items", [])
            collectibles_categories = n_raw.get("categories", [])

    full_db = {
        "metadata": {
            "title": "Zelda Notes Canonical Database",
            "game": "The Legend of Zelda: Ocarina of Time (NX2navi / Recomp)",
            "version": "1.0.0",
            "architecture": "Single Source of Truth / Contract-Driven Lookup Engine"
        },
        "items": ITEMS_CATALOG,
        "upgrades": UPGRADES_CATALOG,
        "songs": SONGS_CATALOG,
        "quest_items": QUEST_ITEMS_CATALOG,
        "time_engine": OOT_TIME_ENGINE_CONSTANTS,
        "places": places_data,
        "map_transforms": transforms_data,
        "collectibles": {
            "total_count": len(collectibles_items),
            "categories": collectibles_categories,
            "items": collectibles_items
        }
    }

    out_file = os.path.join(STATIC_DIR, "canonical_game_db.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(full_db, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Canonical database exported successfully to {out_file}")
    print(f"   • Total Items in Catalog: {len(ITEMS_CATALOG)}")
    print(f"   • Total Collectibles: {len(collectibles_items)}")
    print(f"   • Total Places: {len(places_data)}")
    print(f"   • Total Songs: {len(SONGS_CATALOG)}")
    return full_db

if __name__ == "__main__":
    export_canonical_json()
