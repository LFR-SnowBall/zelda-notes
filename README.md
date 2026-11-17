# 🗡️ Zelda Notes Local — Purah Pad Companion

Companion web local en tiempo real para el port nativo de PC:
- **The Legend of Zelda: Ocarina of Time Remake (`NX2navi` / `ocarina.exe`)**

Inspirado en el Purah Pad Sheikah y en el atlas interactivo cartográfico de **Nintendúo**, ejecutándose de forma 100% local, ligera, sin dependencias externas (`pip`).

---

## 🚀 Instalación y Puesta en Marcha

### Requisitos y Zero-Install (Sin Instalar Nada)
- **Sistema Operativo:** Windows 10 o Windows 11 (también compatible en Linux / Steam Deck).
- **Zero-Install (Cero Instalación):** **No necesitas instalar Python ni configurar variables de entorno.** El archivo `start-zelda-notes.bat` utiliza un entorno portable embebido oficial (10 MB) que se configura automáticamente con un solo clic.
- **Sin dependencias externas:** Corre 100% con la librería estándar de Python (`ctypes`, `http.server`, `json`, `struct`, etc.). Cero comandos `pip install`.

### Inicio Rápido (1 Clic)
1. **Descargar o Clonar:**
   - Descarga el `.zip` desde [Releases](https://github.com/tu-usuario/zelda-notes/releases) o clona el repositorio.
2. **Ejecutar:**
   - **En Windows (Recomendado):** Haz doble clic en **`ZeldaNotes.exe`**. 
     - Se abrirá como una aplicación nativa de escritorio independiente (sin consola negra de fondo, con icono en la bandeja del sistema y aceleración por GPU).
     - *(Alternativa en Windows)*: También puedes hacer doble clic en `start-zelda-notes.bat`.
   - **En Linux / Steam Deck:** Ejecuta `python3 server.py`.
3. **Disfrutar:**
   - **Pantalla Principal (Purah Pad):** [http://localhost:8080](http://localhost:8080)
   - **Ventana Flotante / Segundo Monitor:** [http://localhost:8080/popout](http://localhost:8080/popout)
   - **Desde tu Móvil o Tablet (misma red WiFi):** `http://<IP-DE-TU-PC>:8080` (o clic derecho en el icono de la bandeja del sistema ➔ *Copiar Enlace LAN*).

### Detección de Partidas y Guardados
- **Automático:** Si tienes instalado *The Legend of Zelda: Ocarina of Time* (`NX2navi`), el servidor detecta automáticamente tu carpeta de guardados en:
  `%LOCALAPPDATA%\Programs\NX2navi\game\profile\save`
- **Ruta Personalizada:** Si juegas en Steam Deck o tienes los saves en otra carpeta, puedes configurarlo directamente desde la web pulsando el botón `[ ⚙️ Partida ]` en el encabezado.

---

## 🧭 Filosofía de Diseño: Modo Explorador Anti-Spoilers
Diseñado para enriquecer la aventura sin arruinar la magia del descubrimiento:
- **Detección Automática de Época Temporal (Link Niño vs Link Adulto):**
  - El motor lee en tiempo real el contexto de edad del savegame (`caption.sav` / `progress.sav`).
  - **Filtrado Temporal Inteligente:** Si juegas como Link Niño, el mapa y el checklist **SOLO te muestran los coleccionables y pines alcanzables como Niño** (ocultando los que requieren armas o eventos de Adulto para evitar spoilers y pérdidas de tiempo).
  - Al cambiar de época, el mapa conmuta automáticamente entre los planos de Niño y Adulto (ej. Fuente Zora líquida vs congelada, Kakariko, Ciudadela).
  - Selector manual `[ 🧒 Solo Niño ]` `[ 🗡️ Solo Adulto ]` `[ 🌐 Ver Ambos ]` disponible en cualquier momento con badge `👑 En juego: Link Niño / Adulto`.
- **Bitácora Regional de Telemetría:** Al entrar a cualquier región o mazmorra, el HUD superior muestra cuántas Skulltulas y Corazones existen en esa zona y cuántos llevas recolectados (ej: `Fuente Zora — 🕷️ 1 / 3 | ❤️ 0 / 2 | ✨ 1 / 1`).
- **Plano de Planta Limpio (Sin Spoilers Visuales):** Por defecto, el plano de la zona muestra la baliza en vivo de Link donde estás parado, pero mantiene ocultos los pines de los coleccionables (`[ 👁️ Mostrar Pines en el Plano ]` disponible solo si el jugador decide revelar la ubicación exacta).
- **Pistas Sheikah Colapsables ("Gossip Stones"):** Cada coleccionable en la lista tiene un botón `[ 🔮 Pista de la Piedra Sheikah ]` que despliega el acertijo y la guía paso a paso solo cuando el jugador lo solicita.
- **Checklist Interactivo Persistente:** Casillas de verificación para marcar objetos conseguidos directamente en la interfaz, actualizando en tiempo real los contadores regionales y guardándose en `localStorage`.

---

## 📦 Base de Datos 100% Auto-contenida ("Zero-Setup")
Toda la información del juego ya vive integrada dentro de la herramienta:
- **Base de Datos 100% Auto-contenida ("Zero-Setup")**
Toda la información del juego ya vive integrada dentro de la herramienta:
- **Motor de Calibración Global Automatizada (`static/map_transforms.json`):**
  - Se extrajeron de los archivos originales del juego (`romfs.bin`) los 160 archivos de escenas (`.bcett.byml.zs`) descomprimidos con `libzstd.dll` y el diccionario nativo `bcett.byml.zsdic`.
  - Mapeo 100% automático para las 32 zonas y mazmorras del juego con transformaciones afines continuas `[scale_x, offset_x, scale_z, offset_z]`.
  - Detección espacial 3D instantánea (`detect_place_by_3d`): conmuta de inmediato a la mazmorra al cruzar la puerta sin esperar a guardar en disco.
  - Detección vertical de pisos en tiempo real (`detect_floor_id`): cambia entre `1F`, `2F`, `S1`, etc. según la elevación $Y$ del actor en RAM.
- **Seguimiento en Vivo de RAM a 10 Hz (20 µs de latencia):**
  - Lectura directa de la memoria de `ocarina.exe` mediante `ReadProcessMemory` Win32.
  - La baliza de Link se desliza con transiciones CSS continuas en tiempo real sin recargar la página.
- **184 Coleccionables Oficiales Extraídos y Mapeados:**
  - **100 Skulltulas Doradas** (con condiciones de noche, armas requeridas y piso).
  - **36 Fragmentos de Corazón** (para los 9 contenedores adicionales).
  - **48 Secretos, Grandes Hadas y Recompensas Clave.**
- **Portabilidad Universal:**
  - Autodetecta la carpeta de guardados de NX2navi en cualquier PC usando `%LOCALAPPDATA%\Programs\NX2navi\game\profile\save`.
  - Botón `[ ⚙️ Partida ]` en el encabezado con modal para ingresar una ruta personalizada si el usuario juega en Steam Deck, ROG Ally o una carpeta personalizada.

---

## 🗺️ Doble Vista Cartográfica & Navegación Inmersiva por Planos
1. **Plano de la Zona (Mazmorras e Interiores):**
   - Vistas por plantas (`P1`, `PB`, `S1` o `Niño / Adulto`) sincronizadas automáticamente con la altura $Y$ y la edad de Link en el savegame.
   - **Zoom & Paneo Interactivo Vectorial:**
     - Acercamiento fluido de `0.6x` hasta `4.0x` (400%) con la rueda del ratón (`wheel`), botones flotantes `[ ➕ ]` `[ ➖ ]` `[ 🔄 Reset ]` o gestos táctiles (`pinch-to-zoom`).
     - Arrastre suave con el ratón (`click & drag`) para inspeccionar habitaciones y recovecos al detalle.
     - Doble clic para acercar o restablecer al 100%.
     - Al ser mapas vectoriales SVG, no sufren pixelado a ningún nivel de aumento.
   - Baliza Sheikah de Link con radar pulsante, foco radial y flecha indicadora dorada.
   - Botón `[ 🎯 Centrar y Resaltar a Link ]` y botón flotante `[ 👑 Regresar a Link ]` (tecla `L`).
   - Botón `[ ⛶ Enfocar en Grande ]` (Modo Teatro a pantalla completa con tecla `F` o `Esc`).
   - Botón `[ ↗ Ventana Aparte ]` (Popout flotante multi-monitor en [popout.html](file:///C:/Users/luisi/.brain/contexts/personal/projects/zelda-notes/static/popout.html) con sincronización bidireccional en tiempo real).
2. **Navegación Modular por Tarjetas ("Adentrarse en Planos de <Zona>"):**
   - Tarjetas ricas e individuales para cada una de las 32 zonas y estancias cartografiadas.
   - Cada tarjeta muestra icono temático, tipo de zona, barra de progreso individual, contadores reales de telemetría (`🕷️ SKULLTULAS`, `❤️ CORAZONES`, `✨ SECRETOS`) y botón directo `[ 🌊 Adentrarse en Planos de <Zona> ➔ ]`.
   - Permite profundizar paso a paso desde el reino hacia cualquiera de sus zonas hermanas (ej: de Reino Zora ➔ Río Zora, Dominio Zora, Fuente Zora, Tripa de Jabu-Jabu, Caverna de Hielo).
3. **Reino de Hyrule (General):**
   - Ilustración cartográfica de alta fidelidad `hyrule.webp`.
   - Niebla de guerra Sheikah dinámica sobre regiones no visitadas.
   - 32 puntos geográficos inspeccionables con filtros por región y cuadrícula interactiva de reinos.
