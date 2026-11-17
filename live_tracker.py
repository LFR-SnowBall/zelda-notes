import ctypes
from ctypes import wintypes
import struct
import time
import math

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
TH32CS_SNAPPROCESS = 0x00000002

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('cntUsage', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD),
        ('th32DefaultHeapID', ctypes.c_size_t),
        ('th32ModuleID', wintypes.DWORD),
        ('cntThreads', wintypes.DWORD),
        ('th32ParentProcessID', wintypes.DWORD),
        ('pcPriClassBase', wintypes.LONG),
        ('dwFlags', wintypes.DWORD),
        ('szExeFile', wintypes.WCHAR * 260)
    ]

class MEMORY_BASIC_INFORMATION64(ctypes.Structure):
    _fields_ = [
        ('BaseAddress', ctypes.c_uint64),
        ('AllocationBase', ctypes.c_uint64),
        ('AllocationProtect', wintypes.DWORD),
        ('Alignment1', wintypes.DWORD),
        ('RegionSize', ctypes.c_uint64),
        ('State', wintypes.DWORD),
        ('Protect', wintypes.DWORD),
        ('Type', wintypes.DWORD),
        ('Alignment2', wintypes.DWORD),
    ]

# ==============================================================================
# CANONICAL OOT ENGINE TIME & EVENT LOOKUP TABLES (Matches static game code)
# ==============================================================================
OOT_CANONICAL_TIME_EVENTS = [
    {
        "id": "natural_dawn",
        "name": "Amanecer Natural (Canto del Gallo)",
        "raw_min": 0x3F00,
        "raw_max": 0x4100,
        "canonical_hex": 0x4000,
        "default_hour": 6,
        "default_minute": 0,
        "phase": "dawn",
        "icon": "🐓",
        "label": "Amanecer (Canto del Gallo)",
        "ambient_color": "linear-gradient(135deg, rgba(255, 145, 50, 0.35) 0%, rgba(255, 100, 120, 0.25) 50%, rgba(40, 20, 70, 0.40) 100%)",
        "filter": "sepia(0.35) saturate(1.35) hue-rotate(-15deg) brightness(1.02)",
        "lore": "El gallo Cucco canta y el sol se eleva sobre las montañas de Hyrule."
    },
    {
        "id": "suns_song_dawn",
        "name": "Canción del Sol (Amanecer)",
        "raw_min": 0x47A0,
        "raw_max": 0x4880,
        "canonical_hex": 0x4800,
        "default_hour": 6,
        "default_minute": 45,
        "phase": "dawn",
        "icon": "🌅",
        "label": "Amanecer (Canción del Sol)",
        "ambient_color": "linear-gradient(135deg, rgba(255, 130, 45, 0.30) 0%, rgba(255, 75, 110, 0.22) 50%, rgba(35, 15, 65, 0.38) 100%)",
        "filter": "sepia(0.35) saturate(1.35) hue-rotate(-15deg) brightness(1.02)",
        "lore": "Invocación del sol con la melodía sagrada."
    },
    {
        "id": "market_gate_open",
        "name": "Apertura de la Ciudadela",
        "raw_min": 0x4980,
        "raw_max": 0x4B00,
        "canonical_hex": 0x4A00,
        "default_hour": 7,
        "default_minute": 0,
        "phase": "day",
        "icon": "🏰",
        "label": "Apertura de la Ciudadela",
        "ambient_color": "rgba(255, 240, 180, 0.08)",
        "filter": "none",
        "lore": "Baja el puente levadizo de la Ciudadela y el mercado cobra vida."
    },
    {
        "id": "natural_noon",
        "name": "Pleno Mediodía (Cénit Solar)",
        "raw_min": 0x7E00,
        "raw_max": 0x8200,
        "canonical_hex": 0x8000,
        "default_hour": 12,
        "default_minute": 0,
        "phase": "day",
        "icon": "☀️",
        "label": "Pleno Mediodía",
        "ambient_color": "transparent",
        "filter": "none",
        "lore": "El sol alcanza su punto más alto sobre la Pradera de Hyrule."
    },
    {
        "id": "natural_dusk",
        "name": "Atardecer (Aullido del Lobo)",
        "raw_min": 0xBE00,
        "raw_max": 0xC100,
        "canonical_hex": 0xC000,
        "default_hour": 18,
        "default_minute": 0,
        "phase": "dusk",
        "icon": "🐺",
        "label": "Atardecer (Aullido del Lobo)",
        "ambient_color": "linear-gradient(135deg, rgba(255, 110, 30, 0.32) 0%, rgba(180, 40, 80, 0.25) 50%, rgba(15, 10, 40, 0.45) 100%)",
        "filter": "sepia(0.35) saturate(1.35) hue-rotate(-25deg)",
        "lore": "Se escucha el aullido del lobo en la distancia mientras el sol se oculta tras el Valle Gerudo."
    },
    {
        "id": "market_gate_close",
        "name": "Cierre del Puente / Stalchildren",
        "raw_min": 0xC400,
        "raw_max": 0xC700,
        "canonical_hex": 0xC555,
        "default_hour": 18,
        "default_minute": 30,
        "phase": "dusk",
        "icon": "💀",
        "label": "Cierre del Puente / Stalchildren",
        "ambient_color": "linear-gradient(135deg, rgba(180, 50, 40, 0.35) 0%, rgba(50, 20, 60, 0.45) 60%, rgba(10, 5, 20, 0.70) 100%)",
        "filter": "sepia(0.3) saturate(1.2) hue-rotate(-30deg)",
        "lore": "Sube el puente levadizo de la Ciudadela y los esqueletos Stalchildren emergen del suelo."
    },
    {
        "id": "suns_song_night",
        "name": "Canción del Sol (Noche Cerrada)",
        "raw_min": 0xD000,
        "raw_max": 0xE200,
        "canonical_hex": 0xD940,
        "default_hour": 20,
        "default_minute": 22,
        "phase": "night",
        "icon": "🌙",
        "label": "Noche (Canción del Sol)",
        "ambient_color": "radial-gradient(circle at 50% 35%, rgba(15, 30, 80, 0.45) 0%, rgba(5, 10, 25, 0.7) 65%, rgba(2, 3, 10, 0.88) 100%)",
        "filter": "hue-rotate(190deg) saturate(1.15) brightness(0.78) contrast(1.15)",
        "lore": "Invocación nocturna con la melodía sagrada; paraliza a los ReDeads y momias Gibdos."
    },
    {
        "id": "dampe_tour",
        "name": "Tour de Excavación de Dampé",
        "raw_min": 0xDFC0,
        "raw_max": 0xE200,
        "canonical_hex": 0xE000,
        "default_hour": 21,
        "default_minute": 0,
        "phase": "night",
        "icon": "⚰️",
        "label": "Tour de Dampé (Cementerio)",
        "ambient_color": "radial-gradient(circle at 50% 35%, rgba(30, 15, 60, 0.50) 0%, rgba(10, 5, 25, 0.75) 65%, rgba(2, 1, 10, 0.90) 100%)",
        "filter": "hue-rotate(210deg) saturate(1.1) brightness(0.72) contrast(1.2)",
        "lore": "Dampé el sepulturero sale a cavar tumbas en el cementerio de Kakariko buscando tesoros."
    },
    {
        "id": "natural_midnight",
        "name": "Medianoche Espectral (Hora de los Poes)",
        "raw_min": 0xFF50,
        "raw_max": 0xFFFF,
        "canonical_hex": 0x0000,
        "default_hour": 0,
        "default_minute": 0,
        "phase": "night",
        "icon": "👻",
        "label": "Medianoche (Hora Espectral)",
        "ambient_color": "radial-gradient(circle at 50% 35%, rgba(10, 25, 70, 0.55) 0%, rgba(3, 8, 20, 0.80) 65%, rgba(1, 2, 8, 0.95) 100%)",
        "filter": "hue-rotate(195deg) saturate(1.2) brightness(0.70) contrast(1.25)",
        "lore": "Las ánimas Poes flotan sobre las lápidas y las Skulltulas doradas emiten su sonido característico."
    },
    {
        "id": "deep_night",
        "name": "Madrugada Silenciosa",
        "raw_min": 0x2A00,
        "raw_max": 0x2C00,
        "canonical_hex": 0x2AAA,
        "default_hour": 4,
        "default_minute": 0,
        "phase": "night",
        "icon": "🌌",
        "label": "Madrugada Silenciosa",
        "ambient_color": "radial-gradient(circle at 50% 35%, rgba(18, 20, 50, 0.50) 0%, rgba(5, 8, 20, 0.75) 65%, rgba(2, 3, 10, 0.90) 100%)",
        "filter": "hue-rotate(190deg) saturate(1.15) brightness(0.75) contrast(1.15)",
        "lore": "La noche más oscura antes de la primera luz del alba en Hyrule."
    }
]

OOT_DAY_PHASES = [
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

class LiveTracker:
    def __init__(self):
        self.pid = None
        self.handle = None
        self.actor_addr = 0x13836cc80  # Live Link Player coordinate address
        self.scene_addr = 0x1383084f4  # Active scene string address in heap
        self.last_scan_time = 0
        self.last_coords = None
        self.read_buf = ctypes.create_string_buffer(12)
        self.read_bytes = ctypes.c_size_t()
        
        # Reloj vivo dinámico continuo (segundero y minutero activos)
        # Inicia canónicamente a las 6:00 AM (Amanecer en Hyrule)
        self.base_time_sec = 6 * 3600
        self.start_wall_time = time.time()
        self.last_matched_code = None
        self.time_addr = None
        self.time_sig = b'\xFF\xFF\xFF\xFF\x18\x42'
        self.time_hash_addr = 0x191a21850
        self.time_hash_key = struct.pack('<I', 0xe573f564)

    def read_ptr(self, addr):
        """Lee un puntero de 64 bits en el espacio de memoria del juego"""
        if not self.handle or not addr:
            return 0
        buf = ctypes.c_uint64()
        rb = ctypes.c_size_t()
        if kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(addr), ctypes.byref(buf), 8, ctypes.byref(rb)):
            return buf.value
        return 0

    def read_u32(self, addr):
        """Lee un entero de 32 bits sin signo"""
        if not self.handle or not addr:
            return 0
        buf = ctypes.c_uint32()
        rb = ctypes.c_size_t()
        if kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(addr), ctypes.byref(buf), 4, ctypes.byref(rb)):
            return buf.value
        return 0

    def read_u16(self, addr):
        """Lee un entero de 16 bits sin signo"""
        if not self.handle or not addr:
            return 0
        buf = ctypes.c_uint16()
        rb = ctypes.c_size_t()
        if kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(addr), ctypes.byref(buf), 2, ctypes.byref(rb)):
            return buf.value
        return 0

    def read_mem_bytes(self, addr, length):
        """Lee un buffer de bytes de la memoria del proceso"""
        if not self.handle or not addr or length <= 0:
            return b""
        buf = ctypes.create_string_buffer(length)
        rb = ctypes.c_size_t()
        if kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(addr), buf, length, ctypes.byref(rb)):
            return bytes(buf.raw[:rb.value])
        return b""

    def read_time_from_memory(self):
        """Lee el tiempo canónico exacto del juego en vivo (Time Manager Object / GameData)"""
        if not self.handle:
            return None

        # 1. Puntero estático canónico del Time Manager Object (p_stage2 + 0x2: reloj celestial dinámico)
        p_root = self.read_ptr(0x7004C7E890)
        if p_root:
            p_stage2 = self.read_ptr(p_root)
            if p_stage2:
                val = self.read_u16(p_stage2 + 0x2)
                if val and 0 < val <= 0xFFFF:
                    return val

        # 2. Verificación ultra-rápida de la dirección de hash cacheada (<1 microsegundo)
        if self.time_hash_addr:
            raw = self.read_mem_bytes(self.time_hash_addr, 8)
            if len(raw) == 8 and raw[:4] == self.time_hash_key:
                val = struct.unpack('<I', raw[4:8])[0] & 0xFFFF
                return val
            self.time_hash_addr = None

        # 2. Escaneo específico del bloque GameData (0x180000000 - 0x1A8000000)
        mbi = MEMORY_BASIC_INFORMATION64()
        addr = 0x180000000
        rb = ctypes.c_size_t()
        while addr < 0x1A8000000:
            if not kernel32.VirtualQueryEx(self.handle, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
                break
            if mbi.State == 0x1000 and (mbi.Protect & 0x04) and not (mbi.Protect & 0x100):
                chunk = min(mbi.RegionSize, 16 * 1024 * 1024)
                chunk_buf = ctypes.create_string_buffer(chunk)
                if kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(mbi.BaseAddress), chunk_buf, chunk, ctypes.byref(rb)):
                    raw = bytes(chunk_buf.raw[:rb.value])
                    idx = raw.find(self.time_hash_key)
                    if idx != -1:
                        target = mbi.BaseAddress + idx
                        self.time_hash_addr = target
                        val = struct.unpack('<I', raw[idx+4:idx+8])[0] & 0xFFFF
                        return val
            addr = mbi.BaseAddress + mbi.RegionSize

        # 3. Fallback de firma antigua si existiese
        if self.time_addr:
            buf = ctypes.create_string_buffer(8)
            rb = ctypes.c_size_t()
            if kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(self.time_addr - 6), buf, 8, ctypes.byref(rb)):
                if bytes(buf.raw[:6]) == self.time_sig:
                    return struct.unpack('<H', buf.raw[6:8])[0]
            self.time_addr = None

        return None

    def read_in_game_time(self, scene_name=""):
        now = time.time()

        # 1. Leer el tiempo directo y exacto de la memoria del juego
        raw_val = self.read_time_from_memory()
        if raw_val is not None:
            # Cálculo canónico exacto: 0x0000 = 00:00, 0x4000 = 06:00, 0x8000 = 12:00, 0xC000 = 18:00
            h = (raw_val * 24) // 65536
            m = ((raw_val * 24 * 60) // 65536) % 60
            s = 0
            time_24 = f"{h:02d}:{m:02d}"
            formatted = time_24
            raw_hex_str = hex(raw_val)

            # Buscar si coincide con un evento canónico (ej. Canción del Sol, amanecer, puertas)
            matched_ev = None
            for ev in OOT_CANONICAL_TIME_EVENTS:
                rmin = ev["raw_min"]
                rmax = ev["raw_max"]
                if rmin > rmax:
                    if raw_val >= rmin or raw_val <= rmax:
                        matched_ev = ev
                        break
                elif rmin <= raw_val <= rmax:
                    matched_ev = ev
                    break

            if matched_ev:
                self.last_matched_code = matched_ev["id"]
                self.last_matched_event = matched_ev
        else:
            # Fallback seguro en transiciones de carga
            elapsed_sec = int(now - self.start_wall_time)
            live_seconds = (self.base_time_sec + elapsed_sec) % 86400
            h = (live_seconds // 3600) % 24
            m = (live_seconds % 3600) // 60
            s = 0
            time_24 = f"{h:02d}:{m:02d}"
            formatted = time_24
            raw_val = int((live_seconds * 65536) / 86400)
            raw_hex_str = hex(raw_val)

        # 3. Determinar fase solar y estilos
        phase = "day"
        icon = "☀️"
        label = "Día"
        ambient_color = "transparent"
        filter_css = "none"

        for p_def in OOT_DAY_PHASES:
            if p_def["hour_min"] <= h < p_def["hour_max"]:
                phase = p_def["phase"]
                icon = p_def["icon"]
                label = p_def["label"]
                ambient_color = p_def["ambient_color"]
                filter_css = p_def["filter"]
                break

        # Si tenemos un evento canónico reciente, enriquecer con su icono, nombre y lore
        ev = getattr(self, 'last_matched_event', None)
        event_name = ev.get('name', '') if ev else ''
        event_lore = ev.get('lore', '') if ev else ''
        matched_code = self.last_matched_code
        if ev:
            icon = ev.get("icon", icon)
            label = ev.get("label", label)
            ambient_color = ev.get("ambient_color", ambient_color)
            filter_css = ev.get("filter", filter_css)

        return {
            "time_str": time_24,
            "time_str_24": time_24,
            "time_str_full": time_24,
            "formatted": time_24,
            "formatted_24": time_24,
            "hour": h,
            "minute": m,
            "second": s,
            "raw_hex": raw_hex_str,
            "phase": phase,
            "icon": icon,
            "label": label,
            "ambient_color": ambient_color,
            "filter": filter_css,
            "matched_event": matched_code,
            "event_name": event_name,
            "event_lore": event_lore
        }

    def read_scene_name(self):
        if not self.handle:
            return ""
        # 1. Cadena de punteros canónica vía Time Manager (PlayState offset: mgr - 0xF74)
        slot = self.read_ptr(0x7004C7E890)
        if slot:
            mgr = self.read_ptr(slot)
            if mgr:
                raw = self.read_mem_bytes(mgr - 0xF74, 64).split(b'\x00')[0]
                if len(raw) >= 3:
                    clean = "".join(chr(c) for c in raw if 32 <= c <= 126)
                    if clean:
                        self.scene_addr = mgr - 0xF74
                        return clean

        # 2. Cadena alternativa PlayState
        play_state = self.read_ptr(0x7004E371E8)
        if play_state:
            raw = self.read_mem_bytes(play_state + 0x4F4, 64).split(b'\x00')[0]
            if len(raw) >= 3:
                clean = "".join(chr(c) for c in raw if 32 <= c <= 126)
                if clean:
                    self.scene_addr = play_state + 0x4F4
                    return clean

        # 3. Dirección cacheada
        if self.scene_addr:
            raw = self.read_mem_bytes(self.scene_addr, 64).split(b'\x00')[0]
            if len(raw) >= 3:
                clean = "".join(chr(c) for c in raw if 32 <= c <= 126)
                if clean:
                    return clean
        return ""

    def get_ocarina_pid(self):
        hSnapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if hSnapshot == -1:
            return None
        pe = PROCESSENTRY32W()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        pid = None
        if kernel32.Process32FirstW(hSnapshot, ctypes.byref(pe)):
            while True:
                if pe.szExeFile.lower() == 'ocarina.exe':
                    pid = pe.th32ProcessID
                    break
                if not kernel32.Process32NextW(hSnapshot, ctypes.byref(pe)):
                    break
        kernel32.CloseHandle(hSnapshot)
        return pid

    def ensure_process(self):
        if self.handle and self.pid:
            exit_code = wintypes.DWORD()
            if kernel32.GetExitCodeProcess(self.handle, ctypes.byref(exit_code)):
                if exit_code.value == 259:  # STILL_ACTIVE
                    return True
            self.close()

        pid = self.get_ocarina_pid()
        if not pid:
            return False

        h = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if not h:
            return False

        self.pid = pid
        self.handle = h
        return True

    def close(self):
        if self.handle:
            try:
                kernel32.CloseHandle(self.handle)
            except Exception:
                pass
            self.handle = None
            self.pid = None

    def validate_actor(self, addr):
        if not addr:
            return None
        if not kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(addr), self.read_buf, 12, ctypes.byref(self.read_bytes)):
            return None
        x, y, z = struct.unpack('<fff', self.read_buf.raw)
        if math.isnan(x) or math.isnan(y) or math.isnan(z) or math.isinf(x) or math.isinf(y) or math.isinf(z):
            return None
        if x == 0.0 and y == 0.0 and z == 0.0:
            return None
        if abs(x) > 10000.0 or abs(y) > 10000.0 or abs(z) > 10000.0:
            return None
        return (x, y, z)

    def scan_for_actor(self):
        now = time.time()
        if now - self.last_scan_time < 1.0:
            return None
        self.last_scan_time = now

        sig = b"\x08\x08\x00\x00\x00\x00\x70\x43"
        mbi = MEMORY_BASIC_INFORMATION64()
        ranges = [(0x130000000, 0x140000000), (0x110000000, 0x130000000)]
        for start_addr, end_addr in ranges:
            addr = start_addr
            while addr < end_addr and kernel32.VirtualQueryEx(self.handle, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
                if mbi.State == 0x1000 and (mbi.Protect & (0x04 | 0x08 | 0x40)) and not (mbi.Protect & 0x100):
                    chunk = min(mbi.RegionSize, 16 * 1024 * 1024)
                    buf = ctypes.create_string_buffer(chunk)
                    rb = ctypes.c_size_t()
                    if kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(mbi.BaseAddress), buf, chunk, ctypes.byref(rb)):
                        raw = bytes(buf)[:rb.value]
                        pos = 0
                        while True:
                            idx = raw.find(sig, pos)
                            if idx == -1:
                                break
                            cand = mbi.BaseAddress + idx + 16
                            coords = self.validate_actor(cand)
                            if coords:
                                self.actor_addr = cand
                                return coords
                            pos = idx + 8
                addr = mbi.BaseAddress + mbi.RegionSize
        return None

    def get_player_coords(self):
        """Obtiene las coordenadas del jugador mediante la cadena de punteros estática oficial o fallback"""
        # 1. Cadena de punteros canónica de Link (1.1.1):
        # manager = [0x7004E371D0]
        # actor = [manager + 0x480]
        # coordenadas (X, Y, Z float32) en: actor + 0x31C
        mgr = self.read_ptr(0x7004E371D0)
        if mgr:
            actor = self.read_ptr(mgr + 0x480)
            if actor:
                coords = self.validate_actor(actor + 0x31C)
                if coords:
                    self.actor_addr = actor + 0x31C
                    return coords

        # 2. Dirección cacheada
        if self.actor_addr:
            coords = self.validate_actor(self.actor_addr)
            if coords:
                return coords

        # 3. Escaneo dinámico por firma si todo lo anterior falla
        return self.scan_for_actor()

    def read_live_inventory(self):
        if not self.handle:
            return []
        buf = ctypes.create_string_buffer(0x2000)
        rb = ctypes.c_size_t()
        if not kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(0x13B3F0000), buf, 0x2000, ctypes.byref(rb)):
            return []
        raw = bytes(buf.raw[:rb.value])
        import re
        pat = re.compile(rb'(?:Weapon_|Item_|Get_)[A-Za-z0-9_]+')
        raw_tokens = list(set(m.group(0).decode('latin1') for m in pat.finditer(raw)))
        alias_map = {
            "Item_DekuNut": "Item_Nut"
        }
        res = []
        for t in raw_tokens:
            canon_id = alias_map.get(t, t)
            res.append({"raw": t, "id": canon_id})
        return res

    def read_hero_vitals(self):
        """Lee en tiempo real el progreso de Skulltulas desde la memoria de ocarina.exe"""
        vitals = {
            "skulls": 0
        }
        if not self.ensure_process():
            return vitals

        # Skulltulas doradas totales desde GameData (0x191a1f000, hash 0x3874fcc4)
        buf_gd = ctypes.create_string_buffer(0x20000)
        rb_gd = ctypes.c_size_t()
        if kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(0x191a1f000), buf_gd, 0x20000, ctypes.byref(rb_gd)):
            raw_gd = bytes(buf_gd.raw[:rb_gd.value])
            idx_sk = raw_gd.find(struct.pack('<I', 0x3874fcc4))
            if idx_sk != -1 and idx_sk + 8 <= len(raw_gd):
                vitals["skulls"] = struct.unpack('<I', raw_gd[idx_sk+4:idx_sk+8])[0]
            else:
                idx_sk2 = raw_gd.find(struct.pack('<I', 0x7d59d22a))
                if idx_sk2 != -1 and idx_sk2 + 8 <= len(raw_gd):
                    vitals["skulls"] = struct.unpack('<I', raw_gd[idx_sk2+4:idx_sk2+8])[0]

        return vitals

    def read_live_progress(self):
        """Lee en tiempo real el bloque GameData (0x191a1f000) y tokens de inventario (0x1b6640000) de ocarina.exe"""
        if not self.ensure_process():
            return None

        # 1. Leer hash table de 0x191a1f000 (0x00 a 0x20000)
        buf_gd = ctypes.create_string_buffer(0x20000)
        rb = ctypes.c_size_t()
        entries = {}
        if kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(0x191a1f000), buf_gd, 0x20000, ctypes.byref(rb)):
            raw_gd = bytes(buf_gd.raw[:rb.value])
            for i in range(0, min(len(raw_gd) - 8, 0x20000), 8):
                k, v = struct.unpack('<II', raw_gd[i:i+8])
                if v != 0 and k != 0:
                    entries[k] = v

        # 2. Leer tokens de texto de 0x1b6640000
        buf_txt = ctypes.create_string_buffer(0x10000)
        found_keys = set()
        if kernel32.ReadProcessMemory(self.handle, ctypes.c_void_p(0x1b6640000), buf_txt, 0x10000, ctypes.byref(rb)):
            raw_txt = bytes(buf_txt.raw[:rb.value])
            import re
            strs = re.findall(rb'[A-Za-z0-9_-]{4,}', raw_txt)
            found_keys = set(s.decode('latin1', 'ignore') for s in strs)

        gs_count = entries.get(0x3874fcc4, entries.get(0x7d59d22a, 0))
        return {
            "entries": entries,
            "found_keys": found_keys,
            "gs_count": gs_count,
            "total_unique_flags": len(entries)
        }

    def read_live_coords(self):
        t0 = time.perf_counter()
        if not self.ensure_process():
            return {"online": False, "reason": "ocarina.exe not running"}

        coords = self.get_player_coords()

        dt_us = (time.perf_counter() - t0) * 1_000_000
        if not coords:
            if self.last_coords:
                coords = self.last_coords
            else:
                return {"online": False, "reason": "actor coordinates not found", "read_us": round(dt_us, 1)}

        self.last_coords = coords
        x, y, z = coords
        scene = self.read_scene_name()
        live_inv = self.read_live_inventory()
        vitals = self.read_hero_vitals()
        return {
            "online": True,
            "x": round(x, 2),
            "y": round(y, 2),
            "z": round(z, 2),
            "scene_name": scene,
            "live_inventory": live_inv,
            "hero_vitals": vitals,
            "read_us": round(dt_us, 1)
        }

# Global tracker instance
_tracker_instance = None

def get_tracker():
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = LiveTracker()
    return _tracker_instance
