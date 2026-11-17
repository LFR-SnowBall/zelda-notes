import os
import sys
import glob
import json
import time
import re
import struct
import socket
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from live_tracker import get_tracker
STATIC_DIR = os.path.join(BASE_DIR, "static")

LOCAL_APP = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
DEFAULT_NX2NAVI_SAVE = os.path.join(LOCAL_APP, "Programs", "NX2navi", "game", "profile", "save")
CONFIG_FILE = os.path.join(BASE_DIR, "user_config.json")

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.2)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

def get_base_save_path(game_key="nx2navi"):
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                custom = cfg.get("nx2navi_save_path")
                if custom and os.path.exists(custom):
                    return custom
        except Exception:
            pass
    return DEFAULT_NX2NAVI_SAVE

BASE_PATHS = {
    "nx2navi": DEFAULT_NX2NAVI_SAVE
}

try:
    from canonical_db import ITEMS_CATALOG
    OOT_TRANSLATIONS = {k: {"name": v["name"], "category": v["category"], "icon": v.get("icon", "box")} for k, v in ITEMS_CATALOG.items()}
    # Add legacy / alias keys for backward compatibility
    OOT_TRANSLATIONS.update({
        "Item_BombBag_Small": {"name": "Saco de Bombas", "category": "bag", "icon": "bomb"},
        "Item_BombBag_Medium": {"name": "Saco de Bombas Grande", "category": "bag", "icon": "bomb"},
        "Item_BulletBag_Small": {"name": "Bolsa de Semillas", "category": "bag", "icon": "slingshot"},
        "Item_BulletBag_Medium": {"name": "Bolsa de Semillas Grande", "category": "bag", "icon": "slingshot"},
        "Item_StickBag_Small": {"name": "Palos Deku", "category": "item", "icon": "stick"},
        "Item_NutBag_Small": {"name": "Nueces Deku", "category": "item", "icon": "nut"},
        "Item_Wallet_Medium": {"name": "Billetera de Adulto (200)", "category": "bag", "icon": "rupee"},
        "Item_Wallet_Large": {"name": "Billetera Gigante (500)", "category": "bag", "icon": "rupee"},
        "Item_Token_Gold": {"name": "Sello Skulltula Dorada", "category": "collectible", "icon": "skulltula"},
        "Item_Stone_Fire": {"name": "Rubí Goron (Fuego)", "category": "stone", "icon": "gem-red"},
        "Item_Stone_Kokiri": {"name": "Esmeralda Kokiri (Bosque)", "category": "stone", "icon": "gem-green"},
        "Get_StoneOfWater": {"name": "Zafiro Zora (Agua)", "category": "stone", "icon": "gem-blue"},
        "Item_Medallion_Light": {"name": "Medallón de la Luz", "category": "medallion", "icon": "medallion-light"},
        "Item_Medallion_Forest": {"name": "Medallón del Bosque", "category": "medallion", "icon": "medallion-forest"},
        "Item_Medallion_Fire": {"name": "Medallón del Fuego", "category": "medallion", "icon": "medallion-fire"},
        "Item_Medallion_Water": {"name": "Medallón del Agua", "category": "medallion", "icon": "medallion-water"},
        "Item_Medallion_Shadow": {"name": "Medallón de las Sombras", "category": "medallion", "icon": "medallion-shadow"},
        "Item_Medallion_Spirit": {"name": "Medallón del Espíritu", "category": "medallion", "icon": "medallion-spirit"}
    })
except Exception:
    OOT_TRANSLATIONS = {
        "Weapon_Sword_Kokiri": {"name": "Espada Kokiri", "category": "weapon", "icon": "sword"},
        "Weapon_Sword_Master": {"name": "Espada Maestra", "category": "weapon", "icon": "sword-gold"},
        "Weapon_Sword_Biggoron": {"name": "Espada Biggoron", "category": "weapon", "icon": "sword-heavy"},
        "Weapon_Shield_Deku": {"name": "Escudo Deku", "category": "shield", "icon": "shield-wood"},
        "Weapon_Shield_Hylian": {"name": "Escudo Hyliano", "category": "shield", "icon": "shield"},
        "Weapon_Shield_Mirror": {"name": "Escudo Espejo", "category": "shield", "icon": "shield"},
        "Item_Ocarina_Fairy": {"name": "Ocarina del Hada", "category": "key", "icon": "ocarina"},
        "Item_Ocarina_Time": {"name": "Ocarina del Tiempo", "category": "key", "icon": "ocarina-gold"},
        "Item_Hookshot": {"name": "Hookshot (Gancho)", "category": "tool", "icon": "hook"},
        "Item_Longshot": {"name": "Longshot (Supergancho)", "category": "tool", "icon": "hook"},
        "Item_Boomerang": {"name": "Bumerán", "category": "tool", "icon": "boomerang"},
        "Item_Bow": {"name": "Arco de las Hadas", "category": "bow", "icon": "bow"},
        "Item_Lens": {"name": "Lente de la Verdad", "category": "tool", "icon": "eye"},
        "Item_Hammer": {"name": "Martillo Megatón", "category": "tool", "icon": "hammer"},
        "Item_Boots_Iron": {"name": "Botas de Hierro", "category": "boots", "icon": "boots"},
        "Item_Boots_Hover": {"name": "Botas Flotantes", "category": "boots", "icon": "boots"},
        "Item_Tunic_Goron": {"name": "Túnica Goron", "category": "armor", "icon": "tunic-red"},
        "Item_Tunic_Zora": {"name": "Túnica Zora", "category": "armor", "icon": "tunic-blue"}
    }

LOCATION_MAPPING = {
    "insidejabujabubelly": ("jabu", "Tripa de Jabu-Jabu", 76.7, 45.1, "Zora", "1F", 49.1, 94.6),
    "jabujabu": ("jabu", "Tripa de Jabu-Jabu", 76.7, 45.1, "Zora", "1F", 49.1, 94.6),
    "zorafountain": ("fuente", "Fuente Zora", 80.3, 52.2, "Zora", "nino", 51.8, 51.5),
    "zorasdomain": ("dominio", "Región de los Zora", 68.6, 47.5, "Zora", "principal", 50.0, 50.0),
    "zorariver": ("rio", "Río Zora", 58.0, 52.4, "Zora", "principal", 50.0, 50.0),
    "kokiriforest": ("kokiri", "Bosque Kokiri", 59.1, 67.4, "Bosques", "principal", 55.0, 60.0),
    "dekutree": ("deku", "Gran Árbol Deku", 68.3, 76.6, "Bosques", "PB", 50.0, 50.0),
    "lostwoods": ("perdido", "Bosque Perdido", 69.5, 63.9, "Bosques", None, 50.0, 50.0),
    "sacredforestmeadow": ("prado", "Santuario del Bosque", 77.7, 67.5, "Bosques", "principal", 50.0, 50.0),
    "deathmountain": ("sendero", "Montaña de la Muerte", 57.7, 30.1, "Montaña", "principal", 50.0, 50.0),
    "deathmountaintrail": ("sendero", "Montaña de la Muerte", 57.7, 30.1, "Montaña", "principal", 50.0, 50.0),
    "deathmountaincrater": ("crater", "Cráter de la Montaña", 65.6, 12.4, "Montaña", "principal", 50.0, 50.0),
    "goroncity": ("goron", "Ciudad Goron", 70.0, 30.1, "Montaña", "principal", 50.0, 50.0),
    "dodongoscavern": ("dodongos", "Cueva de los Dodongos", 52.5, 22.1, "Montaña", "PB", 50.0, 50.0),
    "kakarikovillage": ("kakariko", "Aldea Kakariko", 58.1, 44.3, "Kakariko", "nino", 50.0, 50.0),
    "graveyard": ("cementerio", "Cementerio de Kakariko", 74.0, 38.7, "Kakariko", "nino", 50.0, 50.0),
    "bottomofthewell": ("pozo", "Fondo del Pozo", 66.1, 37.4, "Kakariko", "S1", 50.0, 50.0),
    "hyrulefield": ("llanura", "Llanura de Hyrule", 44.8, 62.7, "Centro", "principal", 50.0, 50.0),
    "lonlonranch": ("lonlon", "Rancho Lon Lon", 38.2, 57.3, "Centro", "principal", 50.0, 50.0),
    "market": ("ciudadela", "Ciudadela de Hyrule", 43.3, 38.5, "Castillo", "nino", 50.0, 50.0),
    "templeoftime": ("ciudadela", "Templo del Tiempo", 43.3, 38.5, "Castillo", "nino", 50.0, 50.0),
    "hyrulecastle": ("castillo", "Castillo de Hyrule", 42.6, 31.3, "Castillo", "nino", 50.0, 50.0),
    "lakehylia": ("lago", "Lago Hylia", 42.7, 77.1, "Lago", "principal", 50.0, 50.0),
    "watertemple": ("agua", "Templo del Agua", 40.5, 91.0, "Lago", "PB", 50.0, 50.0),
    "gerudovalley": ("valle", "Valle Gerudo", 22.3, 56.2, "Oeste", "principal", 50.0, 50.0),
    "gerudofortress": ("fortaleza", "Fortaleza Gerudo", 20.7, 40.8, "Oeste", "principal", 50.0, 50.0),
    "hauntedwasteland": ("desierto", "Desierto Encantado", 15.5, 34.7, "Oeste", None, 50.0, 50.0),
    "colossus": ("coloso", "Coloso del Desierto", 23.1, 28.7, "Oeste", "principal", 50.0, 50.0),
    "spirittemple": ("espiritu", "Templo del Espíritu", 15.6, 24.0, "Oeste", "PB", 50.0, 50.0),
    "foresttemple": ("bosque", "Templo del Bosque", 86.6, 60.4, "Bosques", "PB", 50.0, 50.0),
    "firetemple": ("fuego", "Templo del Fuego", 62.5, 19.5, "Montaña", "PB", 50.0, 50.0),
    "shadowtemple": ("sombra", "Templo de las Sombras", 80.1, 31.8, "Kakariko", "S1", 50.0, 50.0),
    "icecavern": ("hielo", "Caverna de Hielo", 86.4, 45.4, "Zora", "principal", 50.0, 50.0)
}

PLACES_DATA_PATH = os.path.join(STATIC_DIR, "places_data.json")
try:
    with open(PLACES_DATA_PATH, "r", encoding="utf-8") as f:
        ALL_PLACES = json.load(f)
except Exception:
    ALL_PLACES = []

MAP_TRANSFORMS_PATH = os.path.join(STATIC_DIR, "map_transforms.json")
_MAP_TRANSFORMS_CACHE = {}
_MAP_TRANSFORMS_MTIME = 0

def get_map_transforms():
    global _MAP_TRANSFORMS_CACHE, _MAP_TRANSFORMS_MTIME
    if os.path.exists(MAP_TRANSFORMS_PATH):
        try:
            mt = os.path.getmtime(MAP_TRANSFORMS_PATH)
            if mt != _MAP_TRANSFORMS_MTIME or not _MAP_TRANSFORMS_CACHE:
                with open(MAP_TRANSFORMS_PATH, "r", encoding="utf-8") as f:
                    _MAP_TRANSFORMS_CACHE = json.load(f)
                _MAP_TRANSFORMS_MTIME = mt
        except Exception:
            pass
    return _MAP_TRANSFORMS_CACHE

MAP_TRANSFORMS = get_map_transforms()


def find_latest_save(game_key):
    root = get_base_save_path(game_key)
    if not root or not os.path.exists(root):
        return None
        
    # Check if root itself directly contains slot_* folders
    direct_slots = []
    if os.path.isdir(root):
        for s in os.listdir(root):
            sp = os.path.join(root, s)
            if os.path.isdir(sp) and s.startswith("slot_"):
                cap = os.path.join(sp, "caption.sav")
                if os.path.exists(cap):
                    direct_slots.append((sp, s, os.path.getmtime(cap)))
                    
    if direct_slots:
        direct_slots.sort(key=lambda x: x[2], reverse=True)
        return {
            "profile_dir": root,
            "slot_path": direct_slots[0][0],
            "slot_name": direct_slots[0][1],
            "mtime": direct_slots[0][2],
            "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(direct_slots[0][2]))
        }

    candidates = []
    for entry in os.listdir(root):
        full = os.path.join(root, entry)
        if os.path.isdir(full) and not entry.startswith("save-"):
            candidates.append(full)
    if not candidates:
        return None
    profile_dir = max(candidates, key=os.path.getmtime)
    
    slots = []
    for s in os.listdir(profile_dir):
        sp = os.path.join(profile_dir, s)
        if os.path.isdir(sp) and s.startswith("slot_"):
            cap = os.path.join(sp, "caption.sav")
            if os.path.exists(cap):
                slots.append((sp, s, os.path.getmtime(cap)))
    if not slots:
        return None
    slots.sort(key=lambda x: x[2], reverse=True)
    return {
        "profile_dir": profile_dir,
        "slot_path": slots[0][0],
        "slot_name": slots[0][1],
        "mtime": slots[0][2],
        "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(slots[0][2]))
    }


def extract_jpeg(caption_path):
    if not os.path.exists(caption_path):
        return None
    with open(caption_path, "rb") as f:
        data = f.read()
    start = data.find(b"\xff\xd8\xff")
    if start != -1:
        end = data.find(b"\xff\xd9", start)
        if end != -1:
            return data[start:end + 2]
    return None


def get_all_visited_locations_in_profile(profile_dir):
    visited = set()
    for s in glob.glob(os.path.join(profile_dir, "slot_*")):
        cap = os.path.join(s, "caption.sav")
        if os.path.exists(cap):
            with open(cap, "rb") as f:
                d = f.read()
            # Read null-terminated string at 684
            if len(d) >= 700:
                loc_c = d[684:684+64].split(b"\x00")[0].decode("latin1", "ignore")
                if loc_c:
                    visited.add(loc_c)
            strs = re.findall(b"[a-zA-Z0-9_]{4,}", d[:1396])
            for item in strs:
                dec = item.decode("latin1", "ignore")
                if not dec.startswith("JFIF"):
                    visited.add(dec)
    return visited


def parse_progress(progress_path, game_key):
    entries = {}
    found_keys = set()
    gs_count = 0

    # 1. Intentar lectura viva desde RAM si ocarina.exe está en ejecución
    try:
        tracker = get_tracker()
        live_prog = tracker.read_live_progress() if tracker else None
        if live_prog and live_prog.get("entries"):
            entries = live_prog["entries"]
            found_keys = live_prog.get("found_keys", set())
            gs_count = live_prog.get("gs_count", 0)
    except Exception:
        pass

    # 2. Fallback al archivo en disco si ocarina.exe no está corriendo
    if not entries and progress_path and os.path.exists(progress_path):
        with open(progress_path, "rb") as f:
            data = f.read()
        
        if len(data) >= 0x175d8:
            for i in range(0x28, 0x175d8, 8):
                k, v = struct.unpack('<II', data[i:i+8])
                if v != 0:
                    entries[k] = v

        strings = re.findall(b"[a-zA-Z0-9_-]{4,}", data)
        found_keys = set(s.decode("latin1", "ignore") for s in strings)
        gs_count = entries.get(0x3874fcc4, entries.get(0x7d59d22a, 0))

    if not entries and not found_keys:
        return {"items": [], "raw_count": 0, "found_keys": set(), "collected_item_ids": [], "gs_count": 0}
    
    dict_map = OOT_TRANSLATIONS
    matched = []
    
    for k, info in dict_map.items():
        if k in found_keys:
            matched.append({
                "id": k,
                "name": info["name"],
                "category": info["category"],
                "icon": info["icon"]
            })
            
    other_items = []
    for k in sorted(found_keys):
        if any(prefix in k for prefix in ["Weapon_", "Armor_", "Item_", "Get_"]) and k not in dict_map:
            clean_name = k.replace("Weapon_", "").replace("Armor_", "").replace("Item_", "").replace("Get_", "").replace("_", " ")
            other_items.append({"id": k, "name": clean_name, "category": "other", "icon": "box"})
            
    # Collectibles telemetry extraction
    collected_item_ids = []
    
    # Check Fuente Zora Skulltula
    fuente_flags = [0xa49cb68c, 0x2ac69e28, 0x8e4ca728, 0x3cf55b36]
    has_fuente_gs = any(entries.get(f) == 1 for f in fuente_flags)
    if has_fuente_gs or ("ZoraFountain" in found_keys and "Item_Token_Gold" in found_keys):
        collected_item_ids.append("fuente-gs-02")
        
    if "Item_Token_Gold" in found_keys:
        collected_item_ids.append("kokiri-gs-01")
        if gs_count >= 2:
            collected_item_ids.append("deku-gs-01")

    # Jabu-Jabu Skulltulas (hash 0x2a8c3cf1 bitmask: bits 0..3)
    jabu_gs_mask = entries.get(0x2a8c3cf1, 0)
    if jabu_gs_mask & 1:
        collected_item_ids.append("jabu-gs-01")
    if jabu_gs_mask & 2:
        collected_item_ids.append("jabu-gs-02")
    if jabu_gs_mask & 4:
        collected_item_ids.append("jabu-gs-03")
    if jabu_gs_mask & 8:
        collected_item_ids.append("jabu-gs-04")

    # Jabu-Jabu & Dodongo Heart Containers
    if "Get_StoneOfWater" in found_keys:
        collected_item_ids.append("jabu-heart-01")
    if "Item_Stone_Fire" in found_keys:
        collected_item_ids.append("dodongos-heart-01")

    return {
        "items": matched + other_items[:20],
        "total_unique_flags": len(found_keys),
        "found_keys": found_keys,
        "collected_item_ids": collected_item_ids,
        "gs_count": gs_count
    }


def resolve_active_place(x, y, z, scene_name="", client_place="", cap_place=""):
    mt = get_map_transforms()
    if scene_name:
        s_clean = scene_name.lower().replace("_", "").replace("-", "")
        for loc_key, val in LOCATION_MAPPING.items():
            if loc_key == s_clean or s_clean.startswith(loc_key) or loc_key in s_clean:
                return val[0]

    if client_place and client_place in mt:
        b = mt[client_place].get("bounds_3d")
        if b and (b["min_x"] - 12.0 <= x <= b["max_x"] + 12.0 and
                  b["min_y"] - 15.0 <= y <= b["max_y"] + 15.0 and
                  b["min_z"] - 12.0 <= z <= b["max_z"] + 12.0):
            return client_place

    if cap_place and cap_place in mt:
        b = mt[cap_place].get("bounds_3d")
        if b and (b["min_x"] - 12.0 <= x <= b["max_x"] + 12.0 and
                  b["min_y"] - 15.0 <= y <= b["max_y"] + 15.0 and
                  b["min_z"] - 12.0 <= z <= b["max_z"] + 12.0):
            return cap_place

    d_p = detect_place_by_3d(x, y, z)
    if d_p:
        return d_p

    return client_place or cap_place or "fuente"


def detect_place_by_3d(x, y, z):
    mt = get_map_transforms()
    if not mt:
        return None
    candidates = []
    for p_id, p_info in mt.items():
        b = p_info.get("bounds_3d", {})
        if not b:
            continue
        if (b["min_x"] - 12.0 <= x <= b["max_x"] + 12.0 and
            b["min_y"] - 15.0 <= y <= b["max_y"] + 15.0 and
            b["min_z"] - 12.0 <= z <= b["max_z"] + 12.0):
            vol = (b["max_x"] - b["min_x"]) * (b["max_z"] - b["min_z"])
            candidates.append((p_id, vol))
    if candidates:
        candidates.sort(key=lambda c: c[1])  # prioritize smaller dungeon bounding boxes
        return candidates[0][0]
    return None


def detect_floor_id(place_id, y):
    mt = get_map_transforms()
    if not mt or place_id not in mt:
        return None
    floors = mt[place_id].get("floors", {})
    for f_id, f_data in floors.items():
        yr = f_data.get("y_range")
        if yr and len(yr) == 2:
            if yr[0] <= y <= yr[1]:
                return f_id
    if "1F" in floors:
        return "1F"
    if "principal" in floors:
        return "principal"
    return list(floors.keys())[0] if floors else None


def project_dungeon_coords(place_id, x, y, z):
    mt = get_map_transforms()
    if not mt or place_id not in mt:
        if place_id == "fuente":
            dx = round(0.8878 * x + 19.79, 1)
            dy = round(0.8365 * z + 55.72, 1)
            return max(4.0, min(96.0, dx)), max(4.0, min(96.0, dy))
        return 51.8, 51.5

    pl_data = mt[place_id]
    floors = pl_data.get("floors", {})

    calib = None
    for f_id, f_data in floors.items():
        yr = f_data.get("y_range")
        if yr and len(yr) == 2:
            if yr[0] <= y <= yr[1]:
                calib = f_data
                break

    if not calib:
        for fallback_k in ["default", "1F", "principal"]:
            if fallback_k in floors:
                calib = floors[fallback_k]
                break
        if not calib and floors:
            calib = list(floors.values())[0]

    if not calib:
        return 51.8, 51.5

    sx = calib.get("scale_x", 1.0)
    ox = calib.get("offset_x", 0.0)
    sz = calib.get("scale_z", 1.0)
    oz = calib.get("offset_z", 0.0)

    dx = round(sx * x + ox, 1)
    dy = round(sz * z + oz, 1)
    return max(4.0, min(96.0, dx)), max(4.0, min(96.0, dy))


def parse_caption(caption_path):
    default_res = {
        "location": "Fuente Zora",
        "place_id": "fuente",
        "x": 80.3,
        "y": 52.2,
        "region": "Zora",
        "dungeon_floor": "nino",
        "dungeon_x": 51.8,
        "dungeon_y": 51.5,
        "coords_3d": {"x": 10.24, "y": 102.98, "z": -24.48},
        "has_thumb": False
    }
    if not os.path.exists(caption_path):
        return default_res
        
    with open(caption_path, "rb") as f:
        data = f.read()
    
    # 1. Read EXACT null-terminated location string from offset 684
    loc_c_str = ""
    subloc_c_str = ""
    if len(data) >= 700:
        loc_c_str = data[684:684+64].split(b"\x00")[0].decode("latin1", "ignore").strip()
    if len(data) >= 800:
        subloc_c_str = data[748:748+64].split(b"\x00")[0].decode("latin1", "ignore").strip()
        
    # Read 3D float coordinates from offset 672 (12 bytes: X, Y, Z float32 LE)
    raw_coords = None
    try:
        if len(data) >= 684:
            x, y, z = struct.unpack("<fff", data[672:684])
            raw_coords = {"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)}
    except Exception:
        raw_coords = None
        
    p_id = "fuente"
    loc_name = "Fuente Zora"
    px = 80.3
    py = 52.2
    reg_name = "Zora"
    d_floor = "nino"
    dx = 51.0
    dy = 52.0
    
    # Exact match from offset 684 null-terminated string
    matched = False
    if loc_c_str:
        loc_clean = loc_c_str.lower()
        for loc_key, val in LOCATION_MAPPING.items():
            if loc_key == loc_clean or loc_clean.startswith(loc_key):
                p_id, loc_name, px, py, reg_name, d_floor, dx, dy = val
                matched = True
                break
                
    if not matched:
        # Fallback to subloc or header search
        header = data[:1396]
        strings = re.findall(b"[a-zA-Z0-9_]{4,}", header)
        for s in strings:
            s_clean = s.decode("latin1", "ignore").lower()
            if s_clean in LOCATION_MAPPING:
                p_id, loc_name, px, py, reg_name, d_floor, dx, dy = LOCATION_MAPPING[s_clean]
                matched = True
                break

    # Age check (child vs adult)
    hero_age = "child"
    sub_lower = subloc_c_str.lower()
    loc_lower = loc_c_str.lower()
    
    if "adult" in sub_lower or "adult" in loc_lower:
        hero_age = "adult"
    elif "child" in sub_lower or "child" in loc_lower:
        hero_age = "child"
    elif p_id in ["bosque", "fuego", "agua", "sombra", "hielo"]:
        hero_age = "adult"
    elif p_id in ["deku", "jabu", "pozo"]:
        hero_age = "child"
        
    hero_age_label = "Link Adulto" if hero_age == "adult" else "Link Niño"

    if d_floor in ["adulto", "nino"] or p_id in ["fuente", "kakariko", "ciudadela", "cementerio", "castillo"]:
        d_floor = "adulto" if hero_age == "adult" else "nino"
        if p_id == "fuente":
            if raw_coords and "x" in raw_coords and "z" in raw_coords:
                dx, dy = project_dungeon_coords("fuente", raw_coords["x"], raw_coords["y"], raw_coords["z"])
            else:
                dx = 51.8
                dy = 51.5

    # In-dungeon floor and coordinate detection
    if raw_coords and "x" in raw_coords and "z" in raw_coords:
        det_f = detect_floor_id(p_id, raw_coords.get("y", 0))
        if det_f and det_f != "default":
            d_floor = det_f
        dx, dy = project_dungeon_coords(p_id, raw_coords["x"], raw_coords.get("y", 0), raw_coords["z"])

    has_thumb = (data.find(b"\xff\xd8\xff") != -1)
    return {
        "location": loc_name,
        "place_id": p_id,
        "x": px,
        "y": py,
        "region": reg_name,
        "dungeon_floor": d_floor,
        "dungeon_x": dx,
        "dungeon_y": dy,
        "coords_3d": raw_coords or {"x": px, "y": py, "z": 0},
        "has_thumb": has_thumb,
        "hero_age": hero_age,
        "hero_age_label": hero_age_label
    }


def calculate_map_state(game_key, save_info, cap, prog):
    profile_dir = save_info.get("profile_dir", "")
    visited_tokens = get_all_visited_locations_in_profile(profile_dir) if profile_dir else set()
    found_keys = prog.get("found_keys", set())
    
    discovered_regions = {"Bosques", "Centro"}
    discovered_places = {"kokiri", "llanura", "deku"}
    
    if "Weapon_Shield_Hylian" in found_keys or any("castle" in v.lower() or "market" in v.lower() for v in visited_tokens):
        discovered_regions.add("Castillo")
        discovered_regions.add("Kakariko")
        discovered_places.update(["ciudadela", "castillo", "lonlon", "kakariko"])
        
    if "Item_Stone_Fire" in found_keys or "Item_BombBag_Small" in found_keys or any("death" in v.lower() or "goron" in v.lower() for v in visited_tokens):
        discovered_regions.add("Montaña")
        discovered_places.update(["sendero", "goron", "dodongos", "crater"])
        
    if "Get_StoneOfWater" in found_keys or any("zora" in v.lower() or "jabu" in v.lower() for v in visited_tokens):
        discovered_regions.add("Zora")
        discovered_places.update(["rio", "dominio", "fuente", "jabu"])
        
    for tok in visited_tokens:
        tok_l = tok.lower()
        if "lake" in tok_l or "water" in tok_l:
            discovered_regions.add("Lago")
            discovered_places.update(["lago", "agua"])
        if "gerudo" in tok_l:
            discovered_regions.add("Oeste")
            discovered_places.update(["valle", "fortaleza"])
        if "coloss" in tok_l or "wasteland" in tok_l or "desierto" in tok_l:
            discovered_regions.add("Oeste")
            discovered_places.update(["desierto", "coloso", "espiritu"])
        if "lostwoods" in tok_l or "meadow" in tok_l:
            discovered_places.update(["perdido", "prado"])
            
    discovered_places.add(cap["place_id"])
    discovered_regions.add(cap["region"])
    
    # Reload places if needed
    current_places = ALL_PLACES
    if not current_places and os.path.exists(PLACES_DATA_PATH):
        try:
            with open(PLACES_DATA_PATH, "r", encoding="utf-8") as f:
                current_places = json.load(f)
        except Exception:
            current_places = []

    cur_pid = cap["place_id"]
    current_totals = {"gs": 0, "hearts": 0, "fairies": 0, "total": 0}
    for p in current_places:
        if p["id"] == cur_pid:
            current_totals = p.get("totals", current_totals)
            break

    places_output = []
    total_disc = 0
    for p in current_places:
        is_disc = (p["id"] in discovered_places) or (p["region"] in discovered_regions and not p.get("kind") == "dungeon")
        if is_disc:
            total_disc += 1
        places_output.append({
            "id": p["id"],
            "name": p["name"],
            "region": p["region"],
            "x": p["x"],
            "y": p["y"],
            "intro": p["intro"],
            "totals": p.get("totals", {"gs": 0, "hearts": 0, "fairies": 0, "total": 0}),
            "discovered": is_disc,
            "status": "Descubierta" if is_disc else "Niebla de Guerra (Inexplorada)"
        })
        
    disc_pct = int((total_disc / max(1, len(current_places))) * 100)
    c3d = cap.get("coords_3d", {})
    coords_label = f"[X: {c3d.get('x', cap['x'])}, Y: {c3d.get('y', cap['y'])}, Z: {c3d.get('z', 0)}]"
    
    return {
        "map_image": "/static/hyrule.webp",
        "hero_pin": {
            "x": cap["x"],
            "y": cap["y"],
            "location_name": cap["location"],
            "place_id": cap["place_id"],
            "region": cap["region"],
            "dungeon_floor": cap.get("dungeon_floor", "nino"),
            "dungeon_x": cap.get("dungeon_x", 51.0),
            "dungeon_y": cap.get("dungeon_y", 52.0),
            "coords_display": coords_label,
            "coords_3d": c3d,
            "hero_age": cap.get("hero_age", "child"),
            "hero_age_label": cap.get("hero_age_label", "Link Niño")
        },
        "discovered_regions": list(discovered_regions),
        "places": places_output,
        "current_place_totals": current_totals,
        "total_discovered": total_disc,
        "total_places": len(current_places),
        "discovery_percentage": disc_pct
    }


class ZeldaNotesHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        if path == "/":
            self.serve_file(os.path.join(STATIC_DIR, "index.html"), "text/html; charset=utf-8")
        elif path == "/popout" or path == "/map":
            self.serve_file(os.path.join(STATIC_DIR, "popout.html"), "text/html; charset=utf-8")
        elif path.startswith("/static/"):
            rel = path[len("/static/"):]
            target = os.path.join(STATIC_DIR, rel)
            mime = "text/plain"
            if target.endswith(".css"): mime = "text/css"
            elif target.endswith(".js"): mime = "application/javascript"
            elif target.endswith(".html"): mime = "text/html; charset=utf-8"
            elif target.endswith(".png"): mime = "image/png"
            elif target.endswith(".jpg") or target.endswith(".jpeg"): mime = "image/jpeg"
            elif target.endswith(".webp"): mime = "image/webp"
            elif target.endswith(".svg"): mime = "image/svg+xml"
            elif target.endswith(".json"): mime = "application/json"
            self.serve_file(target, mime)
        elif path == "/api/status":
            self.handle_api_status(query)
        elif path == "/api/lan_info":
            self.handle_api_lan_info()
        elif path == "/api/stream":
            self.handle_api_stream(query)
        elif path == "/api/live_coords":
            self.handle_api_live_coords(query)
        elif path == "/api/canonical_db":
            self.serve_file(os.path.join(STATIC_DIR, "canonical_game_db.json"), "application/json; charset=utf-8")
        elif path == "/api/config":
            self.handle_api_config()
        elif path == "/api/thumbnail":
            self.handle_api_thumbnail(query)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/config":
            self.handle_api_config_save()
        else:
            self.send_error(404, "Not Found")

    def handle_api_lan_info(self):
        lan_ip = get_lan_ip()
        resp = {
            "ip": lan_ip,
            "port": 8080,
            "url": f"http://{lan_ip}:8080",
            "popout_url": f"http://{lan_ip}:8080/popout"
        }
        body = json.dumps(resp, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def handle_api_config(self):
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception:
                cfg = {}
        resp = {
            "nx2navi_save_path": cfg.get("nx2navi_save_path", DEFAULT_NX2NAVI_SAVE),
            "detected_default": DEFAULT_NX2NAVI_SAVE,
            "is_custom": bool(cfg.get("nx2navi_save_path")),
            "active_exists": os.path.exists(get_base_save_path("nx2navi"))
        }
        body = json.dumps(resp, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def handle_api_config_save(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
            custom_path = data.get("nx2navi_save_path", "").strip()
            
            cfg = {}
            if os.path.exists(CONFIG_FILE):
                try:
                    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                        cfg = json.load(f)
                except Exception:
                    pass
            if custom_path:
                cfg["nx2navi_save_path"] = custom_path
            else:
                cfg.pop("nx2navi_save_path", None)
                
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
                
            resp = {"status": "ok", "nx2navi_save_path": get_base_save_path("nx2navi")}
        except Exception as e:
            resp = {"status": "error", "message": str(e)}
            
        body = json.dumps(resp, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def serve_file(self, full_path, content_type):
        if not os.path.exists(full_path):
            self.send_error(404, "File Not Found")
            return
        with open(full_path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.end_headers()
        self.wfile.write(data)

    def handle_api_status(self, query):
        game = query.get("game", ["nx2navi"])[0]
        if game not in BASE_PATHS:
            game = "nx2navi"
            
        lan_ip = get_lan_ip()
        lan_data = {
            "ip": lan_ip,
            "port": 8080,
            "url": f"http://{lan_ip}:8080",
            "popout_url": f"http://{lan_ip}:8080/popout"
        }

        save_info = find_latest_save(game)
        if not save_info:
            resp = {
                "active_game": game,
                "game_title": "Ocarina of Time Remake (NX2navi)",
                "status": "NO_SAVE_FOUND",
                "message": "Aún no hay archivos de guardado generados para este juego.",
                "network": lan_data
            }
        else:
            slot_dir = save_info["slot_path"]
            cap = parse_caption(os.path.join(slot_dir, "caption.sav"))
            prog = parse_progress(os.path.join(slot_dir, "progress.sav"), game)
            map_data = calculate_map_state(game, save_info, cap, prog)
            
            # If live RAM tracker is online, overlay live coordinates on hero_pin
            try:
                tracker = get_tracker()
                live = tracker.read_live_coords()
                if live.get("online") and map_data.get("hero_pin"):
                    hp = map_data["hero_pin"]
                    lx, ly, lz = live["x"], live["y"], live["z"]
                    sc_name = live.get("scene_name", "")
                    hp["coords_3d"] = {"x": lx, "y": ly, "z": lz}
                    p_id = resolve_active_place(lx, ly, lz, scene_name=sc_name, cap_place=cap.get("place_id", ""))
                    hp["place_id"] = p_id
                    det_fl = detect_floor_id(p_id, ly)
                    if det_fl:
                        hp["dungeon_floor"] = det_fl
                    dx, dy = project_dungeon_coords(p_id, lx, ly, lz)
                    hp["dungeon_x"] = dx
                    hp["dungeon_y"] = dy
                    hp["coords_display"] = f"[X: {lx:.2f}, Y: {ly:.2f}, Z: {lz:.2f}]"
                    hp["is_live"] = True
            except Exception:
                pass
            
            resp = {
                "active_game": game,
                "game_title": "The Legend of Zelda: Ocarina of Time Remake (NX2navi)",
                "status": "ONLINE",
                "slot": save_info["slot_name"],
                "last_saved": save_info["formatted_time"],
                "last_saved_timestamp": save_info["mtime"],
                "location": cap["location"],
                "hero_age": cap.get("hero_age", "child"),
                "hero_age_label": cap.get("hero_age_label", "Link Niño"),
                "has_thumbnail": cap["has_thumb"],
                "thumbnail_url": f"/api/thumbnail?game={game}&t={int(save_info['mtime'])}",
                "inventory": prog["items"],
                "total_flags": prog["total_unique_flags"],
                "collected_item_ids": prog.get("collected_item_ids", []),
                "gs_token_count": prog.get("gs_count", 0),
                "hero_vitals": live.get("hero_vitals", {}) if 'live' in locals() and live else {},
                "map": map_data,
                "network": lan_data
            }
            
        body = json.dumps(resp, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def build_telemetry_payload(self, tracker, client_place=""):
        res = tracker.read_live_coords()
        if not res.get("online"):
            return {
                "topic": "TELEMETRY_FRAME",
                "online": False,
                "reason": res.get("reason", "offline"),
                "read_us": res.get("read_us", 0)
            }

        x = res["x"]
        y = res["y"]
        z = res["z"]
        sc_name = res.get("scene_name", "")
        
        active_place = resolve_active_place(x, y, z, scene_name=sc_name, client_place=client_place)
        detected_floor = detect_floor_id(active_place, y)
        dx, dy = project_dungeon_coords(active_place, x, y, z)

        # 1. Canonical Live Age Detection
        sc_lower = sc_name.lower()
        live_age = "adult" if ("_adult" in sc_lower or "adult" in sc_lower) else ("child" if ("_child" in sc_lower or "child" in sc_lower) else None)

        # 2. Canonical Proximity Detection for Collectibles
        nearby_items = []
        try:
            cat_items = CANONICAL_DB.get("collectibles", {}).get("items", []) if 'CANONICAL_DB' in globals() else []
            if not cat_items and os.path.exists(os.path.join(STATIC_DIR, "canonical_game_db.json")):
                with open(os.path.join(STATIC_DIR, "canonical_game_db.json"), "r", encoding="utf-8") as f:
                    globals()['CANONICAL_DB'] = json.load(f)
                cat_items = CANONICAL_DB.get("collectibles", {}).get("items", [])

            for it in cat_items:
                if it.get("place") == active_place:
                    at = it.get("at", {})
                    ix = at.get("x", 0) * 100.0
                    iy = at.get("y", 0) * 100.0
                    dist = math.sqrt((dx - ix) ** 2 + (dy - iy) ** 2)
                    if dist <= 12.0:
                        nearby_items.append({
                            "id": it["id"],
                            "name": it["name"],
                            "cat": it.get("cat", "gs"),
                            "dist_pct": round(dist, 1),
                            "night": it.get("night", False),
                            "age": it.get("age", "both")
                        })
            nearby_items.sort(key=lambda x: x["dist_pct"])
        except Exception:
            pass

        # 3. Live Inventory Matching
        live_inv_raw = res.get("live_inventory", [])
        mapped_live_inv = []
        try:
            canon_items = CANONICAL_DB.get("items", {}) if 'CANONICAL_DB' in globals() else {}
            for item_ref in live_inv_raw:
                cid = item_ref.get("id")
                raw_tok = item_ref.get("raw", cid)
                item_info = canon_items.get(cid, {})
                mapped_live_inv.append({
                    "raw": raw_tok,
                    "id": cid,
                    "name": item_info.get("name", cid),
                    "icon": item_info.get("icon", "item"),
                    "category": item_info.get("category", "item")
                })
        except Exception:
            pass

        hero_vitals = res.get("hero_vitals", {})

        # Live Progress & Collectibles telemetry
        prog = parse_progress("", "nx2navi")
        live_collected = prog.get("collected_item_ids", [])
        gs_token_count = prog.get("gs_count", hero_vitals.get("skulls", 0))

        return {
            "topic": "TELEMETRY_FRAME",
            "online": True,
            "in_game": True,
            "events": {
                "scene": {
                    "raw": sc_name,
                    "place_id": active_place,
                    "floor": detected_floor,
                    "hero_age": live_age
                },
                "position": {
                    "raw_3d": {"x": x, "y": y, "z": z},
                    "dungeon_x": dx,
                    "dungeon_y": dy,
                    "display": f"[X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}]"
                },
                "inventory": mapped_live_inv,
                "nearby": nearby_items,
                "vitals": hero_vitals,
                "collected": live_collected,
                "gs_count": gs_token_count
            },
            # Backwards compatibility flat fields
            "coords_3d": {"x": x, "y": y, "z": z},
            "place_id": active_place,
            "detected_place": active_place,
            "detected_floor": detected_floor,
            "scene_name": sc_name,
            "hero_age": live_age,
            "dungeon_x": dx,
            "dungeon_y": dy,
            "nearby_collectibles": nearby_items,
            "live_inventory": mapped_live_inv,
            "hero_vitals": hero_vitals,
            "collected_item_ids": live_collected,
            "gs_token_count": gs_token_count,
            "coords_display": f"[X: {x:.2f}, Y: {y:.2f}, Z: {z:.2f}]",
            "read_us": res.get("read_us", 0)
        }

    def handle_api_stream(self, query):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        
        tracker = get_tracker()
        client_place = query.get("place", [""])[0]

        try:
            while True:
                payload = self.build_telemetry_payload(tracker, client_place)
                data_str = json.dumps(payload, ensure_ascii=False)
                self.wfile.write(f"data: {data_str}\n\n".encode("utf-8"))
                self.wfile.flush()
                time.sleep(0.1)  # 10Hz pub-sub stream
        except (BrokenPipeError, ConnectionResetError, Exception):
            pass

    def handle_api_live_coords(self, query):
        tracker = get_tracker()
        client_place = query.get("place", [""])[0]
        resp = self.build_telemetry_payload(tracker, client_place)

        body = json.dumps(resp, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def handle_api_thumbnail(self, query):
        game = query.get("game", ["nx2navi"])[0]
        save_info = find_latest_save(game)
        if not save_info:
            self.send_error(404, "No save found")
            return
        cap_file = os.path.join(save_info["slot_path"], "caption.sav")
        jpg = extract_jpeg(cap_file)
        if not jpg:
            self.send_error(404, "No thumbnail in save")
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(jpg)))
        self.send_header("Cache-Control", "public, max-age=60")
        self.end_headers()
        self.wfile.write(jpg)


def run(port=8080):
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, ZeldaNotesHandler)
    hostname = socket.gethostname()
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass
        
    print(f"============================================================")
    print(f"🗡️  ZELDA NOTES LOCAL — Purah Pad Companion Active")
    print(f"   PC Local Access:   http://localhost:{port}")
    print(f"   Mobile / S24 LAN:  http://{local_ip}:{port}")
    print(f"============================================================")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
