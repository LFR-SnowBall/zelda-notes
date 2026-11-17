let currentActiveGame = "nx2navi";
let lastSavedTimestamp = 0;
let refreshInterval = null;
let currentMapData = null;
let activeFilter = "all";
let canonicalDatabase = null;

// Dungeon / Regional Submap State
let currentMapMode = "dungeon"; // "dungeon" or "overworld"
let dungeonDatabase = null;
let selectedPlaceId = "jabu";
let activeFloorId = "1F";
let lastRenderedPlaceId = null;
let lastRenderedFloorId = null;
let floorCandidate = null;
let floorCandidateCount = 0;
let isMapPinsVisible = true; // SIEMPRE MUESTRA LOS PINES EN EL PLANO EN TRUE
let lastHeroPlaceId = null;
let isUserBrowsing = false;
let serverCollectedIds = new Set();
let lastPhysicalDetectedPlace = null;
let lastPhysicalDetectedFloor = null;
let liveCoordsInterval = null;
let lastLiveX = null;
let lastLiveY = null;
let isLiveTracking = false;
let telemetryEventSource = null;

const ICONS_MAP = {
  sword: "🗡️",
  "sword-gold": "⚔️",
  "sword-heavy": "🗡️",
  shield: "🛡️",
  "shield-wood": "🛡️",
  ocarina: "🎶",
  "ocarina-gold": "🎵",
  hook: "⚓",
  boomerang: "🪃",
  bow: "🏹",
  bomb: "💣",
  slingshot: "🎯",
  stick: "🪵",
  nut: "🌰",
  rupee: "💎",
  skulltula: "🕷️",
  "gem-green": "🟢",
  "gem-red": "🔴",
  "gem-blue": "🔵",
  eye: "👁️",
  hammer: "🔨",
  boots: "👢",
  korok: "🍃",
  battery: "🔋",
  orb: "✨",
  box: "📦"
};

const REGION_ICONS = {
  Zora: "💧",
  Montaña: "🌋",
  Bosques: "🌲",
  Centro: "🌿",
  Castillo: "🏰",
  Lago: "⛵",
  Kakariko: "🏘️",
  Oeste: "🏜️"
};

const PLACE_ICONS = {
  rio: "🌊",
  dominio: "💧",
  fuente: "🧊",
  jabu: "🐋",
  hielo: "❄️",
  kokiri: "🏡",
  deku: "🌳",
  perdido: "🌲",
  prado: "🏛️",
  bosque: "🏰",
  sendero: "🪨",
  goron: "🌋",
  dodongos: "🦎",
  crater: "🔥",
  fuego: "🗝️",
  kakariko: "🏘️",
  cementerio: "🪦",
  pozo: "🕳️",
  sombra: "👁️",
  sombras: "👁️",
  ciudadela: "🏰",
  tiempo: "⏳",
  castillo: "👑",
  ganon: "⚔️",
  llanura: "🌾",
  lonlon: "🐎",
  lago: "⛵",
  agua: "🌊",
  valle: "🌉",
  fortaleza: "🏹",
  desierto: "🏜️",
  coloso: "🗿",
  espiritu: "✨",
  gerudo: "🎯"
};

const REGION_TITLES = {
  Zora: "Región de los Zora",
  Montaña: "Montaña de la Muerte & Goron",
  Bosques: "Grandes Bosques Kokiri & Saria",
  Centro: "Llanura de Hyrule & Lon Lon",
  Castillo: "Castillo de Hyrule & Ciudadela",
  Lago: "Lago Hylia & Cuenca Acuática",
  Kakariko: "Pueblo Kakariko & Cementerio",
  Oeste: "Tierras Gerudo & Gran Desierto"
};

const REGION_KEYS = ["Zora", "Bosques", "Montaña", "Castillo", "Kakariko", "Lago", "Oeste", "Centro"];

const REGION_PRIMARY_PLACES = {
  Bosques: "kokiri",
  Zora: "fuente",
  Montaña: "sendero",
  Kakariko: "kakariko",
  Castillo: "ciudadela",
  Lago: "lago",
  Oeste: "valle",
  Centro: "llanura"
};

const PLACE_CONNECTIONS = {
  kokiri: [
    { target: "deku", label: "Adentrarse en: Gran Árbol Deku", type: "dungeon", icon: "🌳" },
    { target: "perdido", label: "Camino a Bosque Perdido", type: "region", icon: "🌲" },
    { target: "llanura", label: "Salida a Llanura de Hyrule", type: "world", icon: "🌾" }
  ],
  deku: [
    { target: "kokiri", label: "Salir a Bosque Kokiri", type: "exit", icon: "⬅️" }
  ],
  perdido: [
    { target: "prado", label: "Santuario del Bosque", type: "region", icon: "🏛️" },
    { target: "kokiri", label: "Regresar a Bosque Kokiri", type: "exit", icon: "⬅️" },
    { target: "goron", label: "Atajo a Ciudad Goron", type: "region", icon: "🌋" },
    { target: "dominio", label: "Atajo a Dominio Zora", type: "region", icon: "💧" }
  ],
  prado: [
    { target: "bosque", label: "Adentrarse en: Templo del Bosque", type: "dungeon", icon: "🏰" },
    { target: "perdido", label: "Regresar a Bosque Perdido", type: "exit", icon: "⬅️" }
  ],
  bosque: [
    { target: "prado", label: "Salir al Santuario del Bosque", type: "exit", icon: "⬅️" }
  ],
  rio: [
    { target: "dominio", label: "Entrar a Región de los Zora", type: "region", icon: "💧" },
    { target: "llanura", label: "Salir a Llanura de Hyrule", type: "world", icon: "🌾" }
  ],
  dominio: [
    { target: "fuente", label: "Trono del Rey ➔ Fuente Zora", type: "region", icon: "🧊" },
    { target: "rio", label: "Salir hacia Río Zora", type: "exit", icon: "⬅️" }
  ],
  fuente: [
    { target: "jabu", label: "Adentrarse en: Tripa de Jabu-Jabu", type: "dungeon", icon: "🐋" },
    { target: "hielo", label: "Adentrarse en: Caverna de Hielo", type: "dungeon", icon: "❄️" },
    { target: "dominio", label: "Regresar a Región de los Zora", type: "exit", icon: "⬅️" }
  ],
  jabu: [
    { target: "fuente", label: "Salir a Fuente Zora", type: "exit", icon: "⬅️" }
  ],
  hielo: [
    { target: "fuente", label: "Salir a Fuente Zora", type: "exit", icon: "⬅️" }
  ],
  sendero: [
    { target: "goron", label: "Entrar a Ciudad Goron", type: "region", icon: "🪨" },
    { target: "dodongos", label: "Adentrarse en: Cueva de los Dodongos", type: "dungeon", icon: "🦎" },
    { target: "crater", label: "Subir al Cráter de la Montaña", type: "region", icon: "🌋" },
    { target: "kakariko", label: "Bajar a Aldea Kakariko", type: "exit", icon: "⬅️" }
  ],
  goron: [
    { target: "crater", label: "Acceso secreto al Cráter", type: "region", icon: "🌋" },
    { target: "sendero", label: "Salir a Sendero de la Montaña", type: "exit", icon: "⬅️" }
  ],
  dodongos: [
    { target: "sendero", label: "Salir al Sendero de la Montaña", type: "exit", icon: "⬅️" }
  ],
  crater: [
    { target: "fuego", label: "Adentrarse en: Templo del Fuego", type: "dungeon", icon: "🔥" },
    { target: "sendero", label: "Bajar a Sendero de la Montaña", type: "exit", icon: "⬅️" },
    { target: "goron", label: "Bajar a Ciudad Goron", type: "exit", icon: "⬅️" }
  ],
  fuego: [
    { target: "crater", label: "Salir al Cráter de la Montaña", type: "exit", icon: "⬅️" }
  ],
  kakariko: [
    { target: "pozo", label: "Descender a: Fondo del Pozo", type: "dungeon", icon: "🕳️" },
    { target: "cementerio", label: "Entrar al Cementerio", type: "region", icon: "🪦" },
    { target: "sendero", label: "Subir a Montaña de la Muerte", type: "region", icon: "🌋" },
    { target: "llanura", label: "Salir a Llanura de Hyrule", type: "world", icon: "🌾" }
  ],
  cementerio: [
    { target: "sombra", label: "Adentrarse en: Templo de las Sombras", type: "dungeon", icon: "👁️" },
    { target: "kakariko", label: "Regresar a Aldea Kakariko", type: "exit", icon: "⬅️" }
  ],
  sombra: [
    { target: "cementerio", label: "Salir al Cementerio", type: "exit", icon: "⬅️" }
  ],
  pozo: [
    { target: "kakariko", label: "Subir a Aldea Kakariko", type: "exit", icon: "⬅️" }
  ],
  lago: [
    { target: "agua", label: "Sumergirse en: Templo del Agua", type: "dungeon", icon: "💧" },
    { target: "llanura", label: "Salir a Llanura de Hyrule", type: "world", icon: "🌾" }
  ],
  agua: [
    { target: "lago", label: "Emerger hacia Lago Hylia", type: "exit", icon: "⬅️" }
  ],
  ciudadela: [
    { target: "castillo", label: "Subir al Castillo de Hyrule", type: "region", icon: "👑" },
    { target: "llanura", label: "Salir a Llanura de Hyrule", type: "world", icon: "🌾" }
  ],
  castillo: [
    { target: "ciudadela", label: "Regresar a Ciudadela de Hyrule", type: "exit", icon: "⬅️" }
  ],
  valle: [
    { target: "fortaleza", label: "Cruzar hacia Fortaleza Gerudo", type: "region", icon: "🏰" },
    { target: "llanura", label: "Salir a Llanura de Hyrule", type: "world", icon: "🌾" }
  ],
  fortaleza: [
    { target: "coloso", label: "Cruzar el Desierto hacia el Coloso", type: "region", icon: "🌪️" },
    { target: "valle", label: "Regresar a Valle Gerudo", type: "exit", icon: "⬅️" }
  ],
  coloso: [
    { target: "espiritu", label: "Adentrarse en: Templo del Espíritu", type: "dungeon", icon: "🏛️" },
    { target: "fortaleza", label: "Regresar a Fortaleza Gerudo", type: "exit", icon: "⬅️" }
  ],
  espiritu: [
    { target: "coloso", label: "Salir al Coloso del Desierto", type: "exit", icon: "⬅️" }
  ],
  llanura: [
    { target: "lonlon", label: "Entrar al Rancho Lon Lon", type: "region", icon: "🐴" },
    { target: "ciudadela", label: "Hacia Ciudadela de Hyrule", type: "region", icon: "🏰" },
    { target: "kakariko", label: "Hacia Aldea Kakariko", type: "region", icon: "🏘️" },
    { target: "rio", label: "Hacia Río Zora", type: "region", icon: "💧" },
    { target: "kokiri", label: "Hacia Bosque Kokiri", type: "region", icon: "🌲" },
    { target: "lago", label: "Hacia Lago Hylia", type: "region", icon: "⛵" },
    { target: "valle", label: "Hacia Valle Gerudo", type: "region", icon: "🏜️" }
  ],
  lonlon: [
    { target: "llanura", label: "Salir a Llanura de Hyrule", type: "exit", icon: "⬅️" }
  ]
};

const FOG_ZONES = [
  { region: "Oeste", name: "Desierto & Valle Gerudo", x: 19, y: 40, w: 32, h: 48 },
  { region: "Lago", name: "Cuenca del Lago Hylia", x: 42, y: 82, w: 28, h: 32 }
];

async function initDungeonDatabase() {
  try {
    const res = await fetch("/static/dungeon_maps_data.json");
    if (res.ok) {
      const data = await res.json();
      dungeonDatabase = data.places || {};
      console.log("Loaded dungeon database with", Object.keys(dungeonDatabase).length, "places");
    }
  } catch (err) {
    console.error("Failed to load dungeon database:", err);
  }
}

async function fetchGameStatus() {
  try {
    const res = await fetch(`/api/status?game=${currentActiveGame}`);
    if (!res.ok) throw new Error("Status fetch failed");
    const data = await res.json();
    if (Array.isArray(data.collected_item_ids)) {
      data.collected_item_ids.forEach(id => serverCollectedIds.add(id));
    }
    renderDashboard(data);
  } catch (err) {
    console.error("Sync error:", err);
    document.getElementById("sync-text").textContent = "DESCONECTADO";
    document.querySelector(".status-pill").style.borderColor = "var(--danger)";
    document.querySelector(".pulse-dot").style.background = "var(--danger)";
  }
}

function renderDashboard(data) {
  if (data.network) {
    currentLanInfo = data.network;
  }
  // Sync status
  document.getElementById("sync-text").textContent = "SINCRONIZADO";
  document.querySelector(".status-pill").style.borderColor = "rgba(0, 255, 170, 0.3)";
  document.querySelector(".pulse-dot").style.background = "var(--success)";

  if (data.status === "NO_SAVE_FOUND") {
    document.getElementById("current-location").textContent = "Partida no detectada";
    document.getElementById("last-saved-time").textContent = "--";
    document.getElementById("inventory-grid").innerHTML = `<div class="loading-state">${data.message}</div>`;
    return;
  }

  // Update Hero & Meta
  document.getElementById("current-location").textContent = data.location;
  document.getElementById("last-saved-time").textContent = data.last_saved;
  document.getElementById("save-slot-badge").textContent = (data.slot || "SLOT 00").toUpperCase();

  // Immediate Clock Update from Status
  if (data.time_info) {
    updateAtmosphericLighting(data.time_info);
  }

  // Update Hero Age Badge (Child vs Adult Link in Game)
  const ageBadge = document.getElementById("hero-age-badge");
  if (ageBadge) {
    const isAdult = (data.hero_age === "adult");
    ageBadge.textContent = isAdult ? "🗡️ LINK ADULTO" : "🧒 LINK NIÑO";
    ageBadge.classList.toggle("adult", isAdult);
  }

  const syncTag = document.getElementById("age-auto-sync-tag");
  if (syncTag && data.hero_age_label) {
    syncTag.textContent = `👑 En juego: ${data.hero_age_label}`;
  }

  // Update Screenshot only if timestamp changed
  if (data.last_saved_timestamp !== lastSavedTimestamp) {
    lastSavedTimestamp = data.last_saved_timestamp;
    const imgEl = document.getElementById("live-screenshot");
    imgEl.src = data.thumbnail_url;
  }

  // Render Map & Dungeon
  if (data.map) {
    currentMapData = data.map;
    const heroPlace = (data.map.hero_pin && data.map.hero_pin.place_id) ? data.map.hero_pin.place_id : null;
    const heroFloor = (data.map.hero_pin && data.map.hero_pin.dungeon_floor) ? data.map.hero_pin.dungeon_floor : null;

    // Detect if hero actually moved to a new zone in the game
    if (heroPlace && heroPlace !== lastHeroPlaceId) {
      lastHeroPlaceId = heroPlace;
      userFloorOverride = null;
      if (!isUserBrowsing || !selectedPlaceId) {
        selectedPlaceId = heroPlace;
      }
    }

    // Detect if hero physically moved floors in the game
    if (heroFloor && heroFloor !== lastHeroFloorId) {
      lastHeroFloorId = heroFloor;
      if (!isUserBrowsing) {
        userFloorOverride = null;
      }
    }

    if (!selectedPlaceId) {
      selectedPlaceId = heroPlace || "fuente";
    }

    renderOverworldMap(data.map);
    if (currentMapMode === "dungeon") {
      if (selectedPlaceId !== lastRenderedPlaceId || activeFloorId !== lastRenderedFloorId) {
        renderDungeonView(selectedPlaceId);
      }
    }
  }

  // Render Inventory
  renderInventory(data.inventory);
}

// ==========================================
// OVERWORLD MAP RENDERER (hyrule.webp)
// ==========================================
function renderOverworldMap(mapData) {
  const pct = mapData.discovery_percentage || 0;
  const pctEl = document.getElementById("discovery-pct");
  if (pctEl) pctEl.textContent = `${pct}%`;
  const fillEl = document.getElementById("discovery-progress-fill");
  if (fillEl) fillEl.style.width = `${pct}%`;

  // Hero Live Beacon position on Overworld
  const beacon = document.getElementById("live-hero-beacon");
  if (mapData.hero_pin && beacon) {
    beacon.style.display = "flex";
    beacon.style.left = `${mapData.hero_pin.x}%`;
    beacon.style.top = `${mapData.hero_pin.y}%`;
    const bZone = document.getElementById("beacon-zone-name");
    if (bZone) bZone.textContent = mapData.hero_pin.location_name;
    const hudSec = document.getElementById("hud-sector-text");
    if (hudSec) hudSec.textContent = `${mapData.hero_pin.location_name.toUpperCase()} (${mapData.hero_pin.region.toUpperCase()})`;
    const hudCoord = document.getElementById("hud-coords-text");
    if (hudCoord) hudCoord.textContent = mapData.hero_pin.coords_display;
  }

  // Fog of War Overlay Zones
  const fogLayer = document.getElementById("fog-overlay-layer");
  fogLayer.innerHTML = "";

  const discoveredRegs = new Set(mapData.discovered_regions || []);
  FOG_ZONES.forEach(fz => {
    if (!discoveredRegs.has(fz.region)) {
      const fogEl = document.createElement("div");
      fogEl.className = "fog-zone";
      fogEl.style.left = `${fz.x}%`;
      fogEl.style.top = `${fz.y}%`;
      fogEl.style.width = `${fz.w}%`;
      fogEl.style.height = `${fz.h}%`;
      fogEl.innerHTML = `
        <div class="fog-zone-label">
          <span>🔒</span>
          <span>${fz.name}</span>
          <span style="font-size: 0.6rem; color: #ff3366;">NIEBLA DE GUERRA</span>
        </div>
      `;
      fogLayer.appendChild(fogEl);
    }
  });

  // Render Markers
  renderOverworldMarkers(mapData.places);
  // Render Kingdoms Telemetry Dashboard
  renderKingdomsGrid();

  // If there is an active place selected, update its inspector
  if (mapData.places) {
    const currentPlaceObj = mapData.places.find(p => p.id === selectedPlaceId) || mapData.places[0];
    if (currentPlaceObj) {
      selectOverworldPlace(currentPlaceObj);
    }
  }
}

function renderOverworldMarkers(places) {
  const layer = document.getElementById("map-markers-layer");
  if (!layer) return;
  layer.innerHTML = "";

  const collected = getCollectedItems();

  places.forEach(p => {
    if (activeFilter === "discovered" && !p.discovered) return;
    if (activeFilter !== "all" && activeFilter !== "discovered" && p.region !== activeFilter) return;

    const isCurrent = currentMapData && currentMapData.hero_pin && currentMapData.hero_pin.place_id === p.id;
    const regIcon = REGION_ICONS[p.region] || "📍";

    // Compute collected vs total for this place
    let placeItems = [];
    if (dungeonDatabase && dungeonDatabase[p.id] && dungeonDatabase[p.id].items) {
      placeItems = dungeonDatabase[p.id].items;
    }
    const totGs = (p.totals && p.totals.gs !== undefined) ? p.totals.gs : placeItems.filter(it => it.cat === "gs").length;
    const doneGs = placeItems.filter(it => it.cat === "gs" && collected.has(it.id)).length;

    const totHearts = (p.totals && p.totals.hearts !== undefined) ? p.totals.hearts : placeItems.filter(it => it.cat === "heart").length;
    const doneHearts = placeItems.filter(it => it.cat === "heart" && collected.has(it.id)).length;

    const totAll = totGs + totHearts;
    const doneAll = doneGs + doneHearts;
    const isClean = totAll > 0 && doneAll === totAll;

    const el = document.createElement("div");
    el.className = `poi-marker ${p.discovered ? "discovered" : "fogged"} ${isCurrent ? "current" : ""}`;
    el.style.left = `${p.x}%`;
    el.style.top = `${p.y}%`;

    // Counts tags
    let countsHtml = "";
    if (isClean) {
      countsHtml = `<span class="poi-tag clean">✔ 100% LIMPIO</span>`;
    } else if (totAll > 0) {
      countsHtml = `
        <span class="poi-tag gs ${doneGs === totGs && totGs > 0 ? 'done' : ''}">🕷️ ${doneGs}/${totGs}</span>
        <span class="poi-tag heart ${doneHearts === totHearts && totHearts > 0 ? 'done' : ''}">❤️ ${doneHearts}/${totHearts}</span>
      `;
    }

    el.innerHTML = `
      <div class="poi-dot">${isCurrent ? "👑" : (p.discovered ? regIcon : "📍")}</div>
      <div class="poi-badge">
        <span class="poi-name-text">${p.name}</span>
        ${countsHtml ? `<div class="poi-counts-row">${countsHtml}</div>` : ''}
      </div>
    `;

    el.onclick = () => selectOverworldPlace(p);
    layer.appendChild(el);
  });
}

function selectOverworldPlace(p) {
  isUserBrowsing = true;
  selectedPlaceId = p.id;
  document.getElementById("insp-name").textContent = p.name;
  document.getElementById("insp-sub").textContent = `Región: ${p.region} // ${p.discovered ? 'DESCUBIERTA' : 'INEXPLORADA'}`;
  document.getElementById("insp-desc").textContent = p.intro || "Zona cartografiada en el reino de Hyrule.";
  document.getElementById("insp-status-icon").textContent = REGION_ICONS[p.region] || "📍";

  // Compute what you have and what is missing in this place
  const collected = getCollectedItems();
  let placeItems = [];
  if (dungeonDatabase && dungeonDatabase[p.id] && dungeonDatabase[p.id].items) {
    placeItems = dungeonDatabase[p.id].items;
  }
  const totGs = (p.totals && p.totals.gs !== undefined) ? p.totals.gs : placeItems.filter(it => it.cat === "gs").length;
  const doneGs = placeItems.filter(it => it.cat === "gs" && collected.has(it.id)).length;
  const missingGs = Math.max(0, totGs - doneGs);

  const totHearts = (p.totals && p.totals.hearts !== undefined) ? p.totals.hearts : placeItems.filter(it => it.cat === "heart").length;
  const doneHearts = placeItems.filter(it => it.cat === "heart" && collected.has(it.id)).length;
  const missingHearts = Math.max(0, totHearts - doneHearts);

  const totFairies = (p.totals && p.totals.fairies !== undefined) ? p.totals.fairies : placeItems.filter(it => it.cat === "fairy" || it.cat === "secret").length;
  const doneFairies = placeItems.filter(it => (it.cat === "fairy" || it.cat === "secret") && collected.has(it.id)).length;
  const missingFairies = Math.max(0, totFairies - doneFairies);

  const gsVal = document.getElementById("insp-gs-val");
  if (gsVal) gsVal.textContent = `${doneGs} / ${totGs}`;
  const gsRem = document.getElementById("insp-gs-rem");
  if (gsRem) gsRem.textContent = missingGs === 0 ? "¡Todas!" : `Faltan ${missingGs}`;

  const heartVal = document.getElementById("insp-heart-val");
  if (heartVal) heartVal.textContent = `${doneHearts} / ${totHearts}`;
  const heartRem = document.getElementById("insp-heart-rem");
  if (heartRem) heartRem.textContent = missingHearts === 0 ? "¡Todas!" : `Faltan ${missingHearts}`;

  const fairyVal = document.getElementById("insp-fairy-val");
  if (fairyVal) fairyVal.textContent = `${doneFairies} / ${totFairies || (totFairies === 0 ? 0 : 1)}`;
  const fairyRem = document.getElementById("insp-fairy-rem");
  if (fairyRem) fairyRem.textContent = missingFairies === 0 ? "¡Todas!" : `Faltan ${missingFairies}`;

  const btnOpen = document.getElementById("btn-open-dungeon");
  if (dungeonDatabase && dungeonDatabase[p.id] && dungeonDatabase[p.id].maps && dungeonDatabase[p.id].maps.length > 0) {
    btnOpen.style.display = "block";
    btnOpen.textContent = `🏰 Ver Plano Detallado de ${p.name}`;
  } else {
    btnOpen.style.display = "none";
  }

  // Update inspection badge
  const isCurrent = currentMapData && currentMapData.hero_pin && currentMapData.hero_pin.place_id === p.id;
  const badgeEl = document.getElementById("insp-badge");
  if (badgeEl) {
    badgeEl.textContent = isCurrent ? "👑 TÚ ESTÁS AQUÍ" : "ZONA SELECCIONADA";
  }
}

function openSelectedPlaceDungeon() {
  setMapMode("dungeon");
  renderDungeonView(selectedPlaceId);
}

function filterPlaces(filterKey) {
  activeFilter = filterKey;
  document.querySelectorAll("#filter-chips .chip").forEach(ch => {
    ch.classList.toggle("active", ch.getAttribute("data-filter") === filterKey);
  });
  if (currentMapData && currentMapData.places) {
    renderOverworldMarkers(currentMapData.places);
  }
  renderKingdomsGrid();
}

function filterKingdom(regKey) {
  if (activeFilter === regKey) {
    filterPlaces("all");
  } else {
    filterPlaces(regKey);
  }
}

function buildZoneCardHtml(p, isCurrentView = false) {
  const collected = getCollectedItems();
  const isHeroHere = (currentMapData && currentMapData.hero_pin && currentMapData.hero_pin.place_id === p.id);
  const pIcon = PLACE_ICONS[p.id] || "🗺️";
  const items = p.items || [];
  const maps = p.maps || [];

  const totGs = items.filter(it => it.cat === "gs").length;
  const doneGs = items.filter(it => it.cat === "gs" && collected.has(it.id)).length;
  const totHearts = items.filter(it => it.cat === "heart").length;
  const doneHearts = items.filter(it => it.cat === "heart" && collected.has(it.id)).length;
  const totSecrets = items.filter(it => it.cat === "fairy" || it.cat === "secret").length;
  const doneSecrets = items.filter(it => (it.cat === "fairy" || it.cat === "secret") && collected.has(it.id)).length;

  const totAll = totGs + totHearts + totSecrets;
  const doneAll = doneGs + doneHearts + doneSecrets;
  const pct = totAll > 0 ? Math.round((doneAll / totAll) * 100) : 100;
  const isClean = totAll > 0 && doneAll === totAll;

  const subType = maps.length > 1 ? `Mazmorra (${maps.length} Plantas)` : (maps.length === 1 ? 'Plano de Zona' : 'Zona de Tránsito');

  let statusPill = "";
  if (isHeroHere) {
    statusPill = `<span class="kingdom-pill hero-here">👑 TÚ ESTÁS AQUÍ</span>`;
  } else if (isCurrentView) {
    statusPill = `<span class="kingdom-pill viewing-pill">📍 PLANO EN PANTALLA</span>`;
  } else if (isClean) {
    statusPill = `<span class="kingdom-pill clean">✔ LIMPIO</span>`;
  } else if (totAll > 0) {
    statusPill = `<span class="kingdom-pill">⏳ FALTAN ${totAll - doneAll}</span>`;
  } else {
    statusPill = `<span class="kingdom-pill">EXPLORADA</span>`;
  }

  let buttonHtml = "";
  if (isCurrentView) {
    buttonHtml = `
      <button class="kingdom-enter-btn current-view-btn" disabled>
        📍 Viendo Plano Actual
      </button>
    `;
  } else {
    buttonHtml = `
      <button class="kingdom-enter-btn" onclick="drillDownToPlace('${p.id}', event)">
        ${pIcon} Adentrarse en Planos de ${p.name} ➔
      </button>
    `;
  }

  return `
    <div class="kingdom-card zone-card ${isCurrentView ? 'active current-view' : ''} ${isClean ? 'clean-card' : ''}" onclick="drillDownToPlace('${p.id}', event)">
      <div class="kingdom-card-header">
        <div class="kingdom-title-wrap">
          <span class="kingdom-icon">${pIcon}</span>
          <div>
            <h4 class="kingdom-name">${p.name}</h4>
            <span class="kingdom-places-tag">${subType}</span>
          </div>
        </div>
        ${statusPill}
      </div>

      <div class="kingdom-prog-bar">
        <div class="kingdom-prog-fill ${isClean ? 'clean' : ''}" style="width: ${pct}%;"></div>
      </div>
      <div class="kingdom-prog-label">
        <span>Progreso: ${pct}%</span>
        <span>${doneAll} / ${totAll} Conseguidos</span>
      </div>

      <div class="kingdom-stats-grid">
        <div class="k-stat-col" title="Skulltulas Doradas">
          <span class="k-lbl">🕷️ SKULLTULAS</span>
          <strong class="k-val">${doneGs} / ${totGs}</strong>
        </div>
        <div class="k-stat-col" title="Piezas de Corazón">
          <span class="k-lbl">❤️ CORAZONES</span>
          <strong class="k-val">${doneHearts} / ${totHearts}</strong>
        </div>
        <div class="k-stat-col" title="Grandes Hadas y Secretos">
          <span class="k-lbl">✨ SECRETOS</span>
          <strong class="k-val">${doneSecrets} / ${totSecrets || 1}</strong>
        </div>
      </div>

      ${buttonHtml}
    </div>
  `;
}

function renderRegionPlansCards(regionKey, currentPlaceId) {
  const mount = document.getElementById("region-plans-grid");
  if (!mount || !dungeonDatabase) return;

  const regTitle = REGION_TITLES[regionKey] || regionKey;
  const regIcon = REGION_ICONS[regionKey] || "💧";

  const headerIcon = document.getElementById("region-plans-icon");
  const headerTitle = document.getElementById("region-plans-title");
  if (headerIcon) headerIcon.textContent = regIcon;
  if (headerTitle) headerTitle.textContent = `PLANOS DE LA REGIÓN: ${regTitle.toUpperCase()}`;

  const placesInReg = Object.values(dungeonDatabase).filter(p => p.region === regionKey);
  mount.innerHTML = placesInReg.map(p => buildZoneCardHtml(p, p.id === currentPlaceId)).join("");
}

function renderKingdomsGrid() {
  const gridEl = document.getElementById("kingdoms-grid");
  if (!gridEl || !dungeonDatabase) return;

  const collected = getCollectedItems();

  // If a specific kingdom is selected/filtered, display its subzones cards directly!
  if (activeFilter !== "all" && activeFilter !== "discovered" && REGION_KEYS.includes(activeFilter)) {
    const regKey = activeFilter;
    const regTitle = REGION_TITLES[regKey] || regKey;
    const regIcon = REGION_ICONS[regKey] || "📍";
    const placesInReg = Object.values(dungeonDatabase).filter(p => p.region === regKey);

    const bannerHtml = `
      <div class="kingdom-focus-header">
        <div class="kingdom-focus-title">
          <span style="font-size: 1.6rem;">${regIcon}</span>
          <div>
            <div style="font-size: 1.15rem; color: #fff;">PLANOS DE LA REGIÓN: ${regTitle.toUpperCase()}</div>
            <div class="kingdom-focus-sub">${placesInReg.length} zonas y planos disponibles. Haz click en cualquier tarjeta para adentrarte:</div>
          </div>
        </div>
        <button class="back-to-hyrule-btn" onclick="filterPlaces('all')">
          <span>⬅</span> Ver Todos los Reinos de Hyrule
        </button>
      </div>
    `;

    const zoneCardsHtml = placesInReg.map(p => buildZoneCardHtml(p, false)).join("");
    gridEl.innerHTML = bannerHtml + zoneCardsHtml;
    return;
  }

  let grandTotal = 0;
  let grandDone = 0;

  const cardsHtml = REGION_KEYS.map(regKey => {
    const regTitle = REGION_TITLES[regKey] || regKey;
    const regIcon = REGION_ICONS[regKey] || "📍";

    // Gather all places in this region
    const placesInReg = Object.values(dungeonDatabase).filter(p => p.region === regKey);
    let totGs = 0, doneGs = 0;
    let totHearts = 0, doneHearts = 0;
    let totFairies = 0, doneFairies = 0;

    placesInReg.forEach(p => {
      const items = p.items || [];
      const gs = items.filter(it => it.cat === "gs");
      totGs += gs.length;
      doneGs += gs.filter(it => collected.has(it.id)).length;

      const hearts = items.filter(it => it.cat === "heart");
      totHearts += hearts.length;
      doneHearts += hearts.filter(it => collected.has(it.id)).length;

      const fairies = items.filter(it => it.cat === "fairy" || it.cat === "secret");
      totFairies += fairies.length;
      doneFairies += fairies.filter(it => collected.has(it.id)).length;
    });

    const regTotal = totGs + totHearts + totFairies;
    const regDone = doneGs + doneHearts + doneFairies;
    const regMissing = Math.max(0, regTotal - regDone);
    const regPct = regTotal > 0 ? Math.round((regDone / regTotal) * 100) : 100;
    const isClean = regTotal > 0 && regDone === regTotal;

    grandTotal += regTotal;
    grandDone += regDone;

    const isFiltered = (activeFilter === regKey);

    return `
      <div class="kingdom-card ${isFiltered ? 'active' : ''} ${isClean ? 'clean-card' : ''}" onclick="filterKingdom('${regKey}')">
        <div class="kingdom-card-header">
          <div class="kingdom-title-wrap">
            <span class="kingdom-icon">${regIcon}</span>
            <div>
              <h4 class="kingdom-name">${regTitle}</h4>
              <span class="kingdom-places-tag">${placesInReg.length} Zonas cartografiadas</span>
            </div>
          </div>
          <span class="kingdom-pill ${isClean ? 'clean' : ''}">
            ${isClean ? '✔ LIMPIO' : `⏳ FALTAN ${regMissing}`}
          </span>
        </div>

        <div class="kingdom-prog-bar">
          <div class="kingdom-prog-fill ${isClean ? 'clean' : ''}" style="width: ${regPct}%;"></div>
        </div>
        <div class="kingdom-prog-label">
          <span>Progreso: ${regPct}%</span>
          <span>${regDone} / ${regTotal} Descubiertos</span>
        </div>

        <div class="kingdom-stats-grid">
          <div class="k-stat-col" title="Skulltulas Doradas">
            <span class="k-lbl">🕷️ SKULLTULAS</span>
            <strong class="k-val">${doneGs} / ${totGs}</strong>
            <span class="k-sub">${totGs - doneGs > 0 ? `Faltan ${totGs - doneGs}` : '¡Todas!'}</span>
          </div>
          <div class="k-stat-col" title="Piezas de Corazón">
            <span class="k-lbl">❤️ CORAZONES</span>
            <strong class="k-val">${doneHearts} / ${totHearts}</strong>
            <span class="k-sub">${totHearts - doneHearts > 0 ? `Faltan ${totHearts - doneHearts}` : '¡Todos!'}</span>
          </div>
          <div class="k-stat-col" title="Grandes Hadas y Secretos">
            <span class="k-lbl">✨ SECRETOS</span>
            <strong class="k-val">${doneFairies} / ${totFairies}</strong>
            <span class="k-sub">${totFairies - doneFairies > 0 ? `Faltan ${totFairies - doneFairies}` : (totFairies === 0 ? 'Sin registros' : '¡Todas!')}</span>
          </div>
        </div>

        <button class="kingdom-enter-btn" onclick="drillIntoKingdom('${regKey}', event)">
          🏰 Ver Planos de ${regKey} (${placesInReg.length} zonas) ➔
        </button>
      </div>
    `;
  }).join("");

  gridEl.innerHTML = cardsHtml;

  const globalStat = document.getElementById("global-collected-count");
  if (globalStat) {
    globalStat.textContent = `${grandDone} / ${grandTotal} (${grandTotal > 0 ? Math.round((grandDone / grandTotal) * 100) : 0}%)`;
  }
}

function drillIntoKingdom(regKey, ev) {
  if (ev) ev.stopPropagation();
  filterKingdom(regKey);
  const gridEl = document.getElementById("kingdoms-grid");
  if (gridEl) gridEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

function drillDownToPlace(targetPlaceId, ev) {
  if (ev) ev.stopPropagation();
  isUserBrowsing = true;
  selectedPlaceId = targetPlaceId;
  activeFloorId = null;
  resetZoomMap();
  setMapMode("dungeon");
  renderDungeonView(targetPlaceId);
  const wrapper = document.getElementById("dungeon-wrapper");
  if (wrapper) wrapper.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ==========================================
// AGE & FLOOR TEMPORAL FILTER (Niño vs Adulto)
// ==========================================
let userAgeOverride = null; // null (auto-sync), "child", "adult", "all"
let userFloorOverride = null; // null (auto-sync), or specific floorId chosen by user
let lastHeroFloorId = null;
let lastRenderedAgeFilter = null;

function getCurrentAge() {
  if (userAgeOverride && userAgeOverride !== "all") {
    return userAgeOverride;
  }
  if (activeFloorId === "adulto") return "adult";
  if (activeFloorId === "nino") return "child";
  if (currentMapData && currentMapData.hero_pin && currentMapData.hero_pin.hero_age) {
    return currentMapData.hero_pin.hero_age;
  }
  return "child";
}

function isItemMatchingAge(it, ageFilter) {
  if (ageFilter === "all") return true;
  const itemAge = it.age || "both";
  if (itemAge === "both") return true;
  return itemAge === ageFilter;
}

function setAgeFilter(ageKey) {
  userAgeOverride = ageKey;
  if (dungeonDatabase && dungeonDatabase[selectedPlaceId]) {
    const p = dungeonDatabase[selectedPlaceId];
    const maps = p.maps || [];
    if (ageKey === "child" && maps.some(m => m.id === "nino")) {
      activeFloorId = "nino";
      userFloorOverride = "nino";
    } else if (ageKey === "adult" && maps.some(m => m.id === "adulto")) {
      activeFloorId = "adulto";
      userFloorOverride = "adulto";
    }
  }
  renderDungeonView(selectedPlaceId, activeFloorId);
}

// ==========================================
// DUNGEON & REGIONAL FLOOR PLAN RENDERER
// ==========================================
function renderDungeonView(placeId, forcedFloor = null) {
  if (!dungeonDatabase || !dungeonDatabase[placeId]) return;

  const place = dungeonDatabase[placeId];
  const maps = place.maps || [];
  const regKey = place.region || "Bosques";
  const regTitle = REGION_TITLES[regKey] || regKey;
  const regIcon = REGION_ICONS[regKey] || "📍";

  document.getElementById("dungeon-btn-label").textContent = place.name;
  document.getElementById("map-header-title").textContent = `PLANO: ${place.name.toUpperCase()}`;
  document.getElementById("dungeon-hud-place").textContent = place.name.toUpperCase();

  // Determine active floor & active age
  const isHeroInThisPlace = (lastPhysicalDetectedPlace === placeId) || (currentMapData && currentMapData.hero_pin && currentMapData.hero_pin.place_id === placeId);
  const heroFloor = (lastPhysicalDetectedPlace === placeId && lastPhysicalDetectedFloor)
    ? lastPhysicalDetectedFloor
    : ((isHeroInThisPlace && currentMapData && currentMapData.hero_pin && currentMapData.hero_pin.dungeon_floor) ? currentMapData.hero_pin.dungeon_floor : null);

  const curAge = getCurrentAge();
  const effectiveAge = (userAgeOverride === "all") ? "all" : curAge;

  if (forcedFloor) {
    activeFloorId = forcedFloor;
    userFloorOverride = forcedFloor;
  } else if (userFloorOverride && maps.some(m => m.id === userFloorOverride)) {
    activeFloorId = userFloorOverride; // Keep user's chosen floor intact across 3s polls!
  } else if (activeFloorId && maps.some(m => m.id === activeFloorId)) {
    // Keep currently rendered floor!
  } else if (isHeroInThisPlace && heroFloor && maps.some(m => m.id === heroFloor)) {
    activeFloorId = heroFloor;
  } else {
    if (maps.some(m => m.id === "nino") && maps.some(m => m.id === "adulto")) {
      activeFloorId = (curAge === "adult") ? "adulto" : "nino";
    } else {
      activeFloorId = place.default_map || (maps[0] ? maps[0].id : null);
    }
  }

  const currentFloorMap = maps.find(m => m.id === activeFloorId) || maps[0];

  // 1. Render Breadcrumbs (Hyrule > Reino > Zona > Planta)
  const breadcrumbEl = document.getElementById("map-breadcrumbs");
  if (breadcrumbEl) {
    breadcrumbEl.innerHTML = `
      <button class="crumb-btn" onclick="setMapMode('overworld')" title="Volver al mapa general de Hyrule">
        <span>🗺️</span> Hyrule
      </button>
      <span class="crumb-sep">›</span>
      <button class="crumb-btn" onclick="drillIntoKingdom('${regKey}')" title="Ver reino ${regTitle}">
        <span>${regIcon}</span> ${regTitle}
      </button>
      <span class="crumb-sep">›</span>
      <span class="crumb-current">${place.name}</span>
      ${currentFloorMap ? `<span class="crumb-floor">(${currentFloorMap.label || activeFloorId})</span>` : ''}
    `;
  }

  // 2. Render Sub-Zones of this Region Ribbon
  const subzonesEl = document.getElementById("region-subzones-bar");
  if (subzonesEl && dungeonDatabase) {
    const placesInReg = Object.values(dungeonDatabase).filter(p => p.region === regKey);
    subzonesEl.innerHTML = placesInReg.map(pz => {
      const isSel = pz.id === placeId;
      const isHeroHere = (currentMapData && currentMapData.hero_pin && currentMapData.hero_pin.place_id === pz.id);
      return `
        <button class="subzone-chip ${isSel ? 'active' : ''}" onclick="drillDownToPlace('${pz.id}')">
          ${isHeroHere ? '👑 ' : ''}${pz.name}
        </button>
      `;
    }).join("");
  }

  // 3. Handle Case where place has no interior SVG (Transition Hub like Bosque Perdido)
  const imgEl = document.getElementById("dungeon-floor-svg");
  const tabsBar = document.getElementById("floor-tabs-bar");
  if (maps.length === 0) {
    if (tabsBar) {
      tabsBar.innerHTML = `<span style="color:var(--text-muted); font-size:0.8rem; padding:8px 14px;">Zona de nexo y tránsito sin plano interior. Selecciona un acceso arriba para adentrarte:</span>`;
    }
    if (imgEl) imgEl.style.display = "none";
    document.getElementById("dungeon-hud-floor").textContent = "ZONA DE TRÁNSITO";
    const beacon = document.getElementById("dungeon-hero-beacon");
    if (beacon) beacon.style.display = "none";
    renderRegionPlansCards(regKey, placeId);
    renderDungeonChecklist(place);
    if (isTheaterActive) syncTheaterHeader();
    return;
  }

  if (imgEl) imgEl.style.display = "block";

  // 5. Render Floor Tabs
  tabsBar.innerHTML = maps.map(m => {
    const isHeroFloor = (isHeroInThisPlace && heroFloor === m.id);
    return `
      <button class="floor-tab ${m.id === activeFloorId ? 'active' : ''}" onclick="changeFloor('${placeId}', '${m.id}')">
        ${isHeroFloor ? '📍 ' : ''}${m.label || m.id}
      </button>
    `;
  }).join("");

  lastRenderedPlaceId = placeId;
  lastRenderedFloorId = activeFloorId;

  // Set SVG Floor Image (only if source changed to avoid flicker/reload)
  const newSvgSrc = `/static/${currentFloorMap.image}`;
  if (imgEl.getAttribute("src") !== newSvgSrc) {
    imgEl.src = newSvgSrc;
  }
  document.getElementById("dungeon-hud-floor").textContent = (currentFloorMap.label || activeFloorId).toUpperCase();

  // Render Items pinned to this floor
  const itemsLayer = document.getElementById("dungeon-items-layer");
  itemsLayer.innerHTML = "";
  itemsLayer.classList.toggle("pins-hidden", !isMapPinsVisible);

  // Update Sheikah Regional Exploration Telemetry HUD (Filtered by current age)
  const collected = getCollectedItems();
  const allItems = (place.items || []).filter(it => isItemMatchingAge(it, effectiveAge));
  const totGs = allItems.filter(it => it.cat === "gs").length;
  const doneGs = allItems.filter(it => it.cat === "gs" && collected.has(it.id)).length;
  const totHearts = allItems.filter(it => it.cat === "heart").length;
  const doneHearts = allItems.filter(it => it.cat === "heart" && collected.has(it.id)).length;
  const totSecrets = allItems.filter(it => it.cat === "fairy" || it.cat === "secret").length;
  const doneSecrets = allItems.filter(it => (it.cat === "fairy" || it.cat === "secret") && collected.has(it.id)).length;

  const hudZone = document.getElementById("hud-zone-name");
  if (hudZone) hudZone.textContent = place.name.toUpperCase();
  const hudGs = document.getElementById("hud-gs-count");
  if (hudGs) hudGs.textContent = `${doneGs} / ${totGs}`;
  const hudH = document.getElementById("hud-hearts-count");
  if (hudH) hudH.textContent = `${doneHearts} / ${totHearts}`;
  const hudSec = document.getElementById("hud-secrets-count");
  if (hudSec) hudSec.textContent = `${doneSecrets} / ${totSecrets || 1}`;

  // Floor pins filtered by current floor AND active age
  const floorItems = allItems.filter(it => it.map_id === activeFloorId || maps.length === 1);
  floorItems.forEach(it => {
    const pinEl = document.createElement("div");
    const isDone = collected.has(it.id);
    pinEl.className = `dungeon-item-pin ${isDone ? 'collected' : ''}`;
    pinEl.style.left = `${it.x}%`;
    pinEl.style.top = `${it.y}%`;

    const icon = it.cat === "gs" ? "🕷️" : (it.cat === "heart" ? "❤️" : (it.cat === "fairy" ? "🧚" : "📦"));
    pinEl.innerHTML = `
      <div class="pin-icon ${it.cat}">${icon}</div>
      <div class="pin-label">${it.name}</div>
    `;

    pinEl.onclick = () => highlightChecklistItem(it.id);
    itemsLayer.appendChild(pinEl);
  });

  // Render Dungeon Hero Beacon
  const beacon = document.getElementById("dungeon-hero-beacon");
  const isHeroOnThisFloor = (isHeroInThisPlace || isLiveTracking) && (activeFloorId === heroFloor || maps.length === 1 || !heroFloor);

  if (isHeroOnThisFloor) {
    beacon.style.display = "flex";
    const bx = (lastLiveX !== null) ? lastLiveX : (currentMapData && currentMapData.hero_pin && currentMapData.hero_pin.dungeon_x || 51.8);
    const by = (lastLiveY !== null) ? lastLiveY : (currentMapData && currentMapData.hero_pin && currentMapData.hero_pin.dungeon_y || 51.5);
    beacon.style.left = `${bx}%`;
    beacon.style.top = `${by}%`;
    document.getElementById("dungeon-beacon-zone").textContent = `${place.name} (${currentFloorMap.label || activeFloorId})`;
  } else {
    beacon.style.display = "none";
  }

  // 6. Render sibling zone plan cards in this region ("Adentrarse en Planos de <Zona>")
  renderRegionPlansCards(regKey, placeId);

  // Render Collectibles Checklist Card
  renderDungeonChecklist(place);

  if (isTheaterActive) {
    syncTheaterHeader();
  }
}

function changeFloor(placeId, floorId) {
  resetZoomMap();
  userFloorOverride = floorId;
  if (floorId === "adulto") {
    userAgeOverride = "adult";
  } else if (floorId === "nino") {
    userAgeOverride = "child";
  }
  renderDungeonView(placeId, floorId);
}

const openedHints = new Set();
let lastRenderedChecklistPlaceId = null;

function renderDungeonChecklist(place, force = false) {
  const listEl = document.getElementById("dungeon-items-list");
  const summaryEl = document.getElementById("dungeon-items-summary");
  if (!listEl || !summaryEl) return;

  const curAge = getCurrentAge();
  const effectiveAge = (userAgeOverride === "all") ? "all" : curAge;
  const collected = getCollectedItems();

  // Sync Age ribbon UI buttons
  const btnChild = document.getElementById("btn-age-child");
  const btnAdult = document.getElementById("btn-age-adult");
  const btnAll = document.getElementById("btn-age-all");
  const pillAge = document.getElementById("checklist-age-pill");
  const syncTag = document.getElementById("age-auto-sync-tag");

  const liveHeroAge = (currentMapData && currentMapData.hero_pin && currentMapData.hero_pin.hero_age) || "child";
  const liveHeroLabel = (liveHeroAge === "adult") ? "Link Adulto" : "Link Niño";

  if (btnChild) btnChild.classList.toggle("active", effectiveAge === "child" && userAgeOverride !== "all");
  if (btnAdult) btnAdult.classList.toggle("active", effectiveAge === "adult" && userAgeOverride !== "all");
  if (btnAll) btnAll.classList.toggle("active", userAgeOverride === "all");

  if (pillAge) {
    if (userAgeOverride === "all") {
      pillAge.textContent = "🌐 AMBAS ÉPOCAS";
    } else {
      pillAge.textContent = (effectiveAge === "adult") ? "🗡️ ÉPOCA: LINK ADULTO" : "🧒 ÉPOCA: LINK NIÑO";
    }
  }

  if (syncTag) {
    syncTag.textContent = `👑 En juego: ${liveHeroLabel}`;
  }

  // Filter items matching effective age
  const visibleItems = (place.items || []).filter(it => isItemMatchingAge(it, effectiveAge));
  const totalCollectedInPlace = visibleItems.filter(it => collected.has(it.id)).length;
  summaryEl.textContent = `${totalCollectedInPlace} / ${visibleItems.length} Conseguidos`;

  if (visibleItems.length === 0) {
    const ageName = effectiveAge === 'child' ? 'Link Niño' : 'Link Adulto';
    const altAge = effectiveAge === 'child' ? 'adult' : 'child';
    const altAgeName = altAge === 'adult' ? '🗡️ Link Adulto' : '🧒 Link Niño';
    listEl.innerHTML = `
      <div class="loading-state" style="padding: 24px; text-align: center;">
        No hay coleccionables alcanzables como <strong>${ageName}</strong> en esta zona.<br>
        <button class="age-toggle-btn" style="margin-top: 12px;" onclick="setAgeFilter('${altAge}')">
          Cambiar a ${altAgeName} ➔
        </button>
      </div>
    `;
    lastRenderedChecklistPlaceId = place.id;
    lastRenderedAgeFilter = effectiveAge;
    return;
  }

  // Fast DOM reconciliation: if zone & age filter didn't change, sync checkbox states only
  if (!force && lastRenderedChecklistPlaceId === place.id && lastRenderedAgeFilter === effectiveAge) {
    const cards = listEl.querySelectorAll(".checklist-item-card");
    if (cards.length === visibleItems.length) {
      visibleItems.forEach(it => {
        const isDone = collected.has(it.id);
        const card = document.getElementById(`card-${it.id}`);
        if (card) {
          card.classList.toggle("collected", isDone);
          const cb = card.querySelector(".collect-checkbox");
          if (cb && cb.checked !== isDone) cb.checked = isDone;
        }
      });
      return;
    }
  }

  lastRenderedChecklistPlaceId = place.id;
  lastRenderedAgeFilter = effectiveAge;

  listEl.innerHTML = visibleItems.map(it => {
    const icon = it.cat === "gs" ? "🕷️" : (it.cat === "heart" ? "❤️" : (it.cat === "fairy" ? "🧚" : "📦"));
    const isDone = collected.has(it.id);
    const catLabel = it.cat === "gs" ? "Skulltula Dorada" : (it.cat === "heart" ? "Fragmento de Corazón" : "Secreto");
    const isExpanded = openedHints.has(`hint-${it.id}`);
    const ageBadge = it.age === "child" ? "🧒 Niño" : (it.age === "adult" ? "🗡️ Adulto" : "🌐 Ambos");

    return `
      <div class="checklist-item-card ${isDone ? 'collected' : ''}" id="card-${it.id}" onclick="jumpToItemFloor('${place.id}', '${it.map_id}', '${it.id}')">
        <div class="collect-checkbox-col" onclick="event.stopPropagation()">
          <input type="checkbox" class="collect-checkbox" ${isDone ? 'checked' : ''} onchange="toggleItemCollected('${it.id}', event)">
        </div>
        <div class="item-cat-icon">${icon}</div>
        <div class="item-content">
          <div class="item-name-row">
            <span class="item-name-text">${it.name}</span>
            <span class="item-floor-badge">${it.map_id || 'Zona'}</span>
            <span class="item-floor-badge" style="color: ${it.age === 'child' ? '#00ffaa' : (it.age === 'adult' ? '#00fff2' : '#ffd700')}">${ageBadge}</span>
          </div>
          <div class="item-sub-meta">
            <span style="font-size: 0.65rem; color: var(--text-muted);">${catLabel}</span>
            ${it.night ? '<span style="font-size: 0.65rem; color: #a0c4ff;">🌙 Solo de noche</span>' : ''}
          </div>
          <button class="hint-trigger-btn ${isExpanded ? 'active' : ''}" onclick="toggleHint('hint-${it.id}', event)">
            <span>🔮</span> ${isExpanded ? 'Ocultar Pista Sheikah' : 'Pista de la Piedra Sheikah'}
          </button>
          <div class="collapsible-body ${isExpanded ? 'expanded' : ''}" id="hint-${it.id}">
            ${it.hint ? `<div class="item-hint-text">💡 ${it.hint}</div>` : ''}
            <div class="item-desc-text">${(it.desc || "").split("\n").join("<br>")}</div>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

function jumpToItemFloor(placeId, mapId, itemId) {
  if (mapId && mapId !== activeFloorId) {
    changeFloor(placeId, mapId);
  }
  highlightChecklistItem(itemId);
}

function highlightChecklistItem(itemId) {
  document.querySelectorAll(".checklist-item-card").forEach(c => c.classList.remove("active"));
  const card = document.getElementById(`card-${itemId}`);
  if (card) {
    card.classList.add("active");
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

// Quick Locate & Center Action
function locateLink() {
  isUserBrowsing = false;
  userFloorOverride = null;
  userAgeOverride = null;

  const targetPlace = lastPhysicalDetectedPlace || (currentMapData && currentMapData.hero_pin && currentMapData.hero_pin.place_id);
  const targetFloor = lastPhysicalDetectedFloor || (currentMapData && currentMapData.hero_pin && currentMapData.hero_pin.dungeon_floor);

  if (currentMapMode === "overworld") {
    if (currentMapData) renderOverworldMap(currentMapData);
    const wrapper = document.getElementById("overworld-wrapper");
    const beacon = document.getElementById("live-hero-beacon");
    if (beacon && wrapper) {
      beacon.classList.remove("locate-highlight");
      void beacon.offsetWidth;
      beacon.classList.add("locate-highlight");
      wrapper.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  } else {
    if (targetPlace) {
      selectedPlaceId = targetPlace;
    }
    renderDungeonView(selectedPlaceId, targetFloor);
    const wrapper = document.getElementById("dungeon-wrapper");
    const beacon = document.getElementById("dungeon-hero-beacon");
    if (beacon && wrapper) {
      beacon.classList.remove("locate-highlight");
      void beacon.offsetWidth;
      beacon.classList.add("locate-highlight");
      wrapper.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }
}

// Mode Switcher: Dungeon vs Overworld
function setMapMode(mode) {
  currentMapMode = mode;
  document.getElementById("btn-mode-dungeon").classList.toggle("active", mode === "dungeon");
  document.getElementById("btn-mode-overworld").classList.toggle("active", mode === "overworld");

  document.getElementById("dungeon-view").style.display = mode === "dungeon" ? "block" : "none";
  document.getElementById("overworld-view").style.display = mode === "overworld" ? "block" : "none";

  if (isTheaterActive) {
    const dungeonWrap = document.getElementById("dungeon-wrapper");
    const overworldWrap = document.getElementById("overworld-wrapper");
    if (mode === "overworld") {
      if (dungeonWrap) dungeonWrap.classList.remove("theater-fullscreen");
      if (overworldWrap) overworldWrap.classList.add("theater-fullscreen");
    } else {
      if (overworldWrap) overworldWrap.classList.remove("theater-fullscreen");
      if (dungeonWrap) dungeonWrap.classList.add("theater-fullscreen");
      syncTheaterHeader();
    }
  }

  if (mode === "dungeon") {
    renderDungeonView(selectedPlaceId);
  } else if (mode === "overworld" && currentMapData) {
    renderOverworldMap(currentMapData);
  }
}

function switchGame(gameKey) {
  currentActiveGame = gameKey;
  lastSavedTimestamp = 0;
  fetchGameStatus();
}

function switchSection(secKey) {
  document.getElementById("tab-btn-map").classList.toggle("active", secKey === "map");
  document.getElementById("tab-btn-inventory").classList.toggle("active", secKey === "inventory");
  document.getElementById("tab-map").classList.toggle("active", secKey === "map");
  document.getElementById("tab-inventory").classList.toggle("active", secKey === "inventory");
}

function renderInventory(items) {
  const gridEl = document.getElementById("inventory-grid");
  document.getElementById("items-count-badge").textContent = `${items.length} Registros`;

  if (!items || items.length === 0) {
    gridEl.innerHTML = `<div class="loading-state">Sin objetos clave registrados aún en este slot.</div>`;
    return;
  }

  gridEl.innerHTML = items.map(item => {
    const canon = (canonicalDatabase && canonicalDatabase.items && canonicalDatabase.items[item.id]) ? canonicalDatabase.items[item.id] : item;
    const icon = ICONS_MAP[canon.icon] || ICONS_MAP[item.icon] || "✨";
    const name = canon.name || item.name;
    const cat = canon.category || item.category || "item";
    return `
      <div class="item-card ${cat}" data-id="${item.id}">
        <div class="item-icon-wrapper">${icon}</div>
        <div class="item-title">${name}</div>
        <div class="item-badge">${cat}</div>
      </div>
    `;
  }).join("");
}


// ==========================================
// ANTI-SPOILERS & COLLECTIBLE TRACKING
// ==========================================
function getCollectedItems() {
  const result = new Set(serverCollectedIds);
  try {
    const local = JSON.parse(localStorage.getItem("zelda_notes_collected") || "[]");
    local.forEach(id => result.add(id));
  } catch (e) {}
  try {
    const uncollected = JSON.parse(localStorage.getItem("zelda_notes_uncollected") || "[]");
    uncollected.forEach(id => result.delete(id));
  } catch (e) {}
  return result;
}

function toggleItemCollected(itemId, ev) {
  if (ev) ev.stopPropagation();
  const collected = getCollectedItems();
  const isCurrentlyDone = collected.has(itemId);

  let local = [];
  try { local = JSON.parse(localStorage.getItem("zelda_notes_collected") || "[]"); } catch (e) {}
  let uncollected = [];
  try { uncollected = JSON.parse(localStorage.getItem("zelda_notes_uncollected") || "[]"); } catch (e) {}

  let localSet = new Set(local);
  let uncollectedSet = new Set(uncollected);

  if (isCurrentlyDone) {
    localSet.delete(itemId);
    uncollectedSet.add(itemId);
  } else {
    localSet.add(itemId);
    uncollectedSet.delete(itemId);
  }

  localStorage.setItem("zelda_notes_collected", JSON.stringify([...localSet]));
  localStorage.setItem("zelda_notes_uncollected", JSON.stringify([...uncollectedSet]));

  renderDungeonView(selectedPlaceId);
  if (currentMapData && currentMapData.places) {
    renderOverworldMarkers(currentMapData.places);
  }
  renderKingdomsGrid();
}

function toggleHint(hintId, ev) {
  if (ev) ev.stopPropagation();
  const body = document.getElementById(hintId);
  const btn = ev && ev.currentTarget;
  if (openedHints.has(hintId)) {
    openedHints.delete(hintId);
    if (body) body.classList.remove("expanded");
    if (btn) {
      btn.classList.remove("active");
      btn.innerHTML = `<span>🔮</span> Pista de la Piedra Sheikah`;
    }
  } else {
    openedHints.add(hintId);
    if (body) body.classList.add("expanded");
    if (btn) {
      btn.classList.add("active");
      btn.innerHTML = `<span>🔮</span> Ocultar Pista Sheikah`;
    }
  }
}

function toggleMapPins() {
  isMapPinsVisible = !isMapPinsVisible;
  const layer = document.getElementById("dungeon-items-layer");
  if (layer) {
    layer.classList.toggle("pins-hidden", !isMapPinsVisible);
  }
  const btnLabel = document.getElementById("toggle-pins-label");
  const btnIcon = document.getElementById("toggle-pins-icon");
  if (btnLabel && btnIcon) {
    btnLabel.textContent = isMapPinsVisible ? "Ocultar Pines (Modo Explorador)" : "Mostrar Pines en el Plano";
    btnIcon.textContent = isMapPinsVisible ? "🙈" : "👁️";
  }

  // Also sync theater pins indicator if present
  const tLabel = document.getElementById("theater-pins-label");
  const tIcon = document.getElementById("theater-pins-icon");
  if (tLabel) tLabel.textContent = isMapPinsVisible ? "Ocultar Pines" : "Ver Pines";
  if (tIcon) tIcon.textContent = isMapPinsVisible ? "🙈" : "👁️";
}

// ==========================================
// THEATER MODE & FLOATING POPOUT CONTROLLERS
// ==========================================
let isTheaterActive = false;

function toggleTheaterMode() {
  isTheaterActive = !isTheaterActive;
  const dungeonWrap = document.getElementById("dungeon-wrapper");
  const overworldWrap = document.getElementById("overworld-wrapper");

  if (!isTheaterActive) {
    if (dungeonWrap) dungeonWrap.classList.remove("theater-fullscreen");
    if (overworldWrap) overworldWrap.classList.remove("theater-fullscreen");
    document.body.classList.remove("in-theater-mode");
    return;
  }

  document.body.classList.add("in-theater-mode");
  if (currentMapMode === "overworld") {
    if (dungeonWrap) dungeonWrap.classList.remove("theater-fullscreen");
    if (overworldWrap) overworldWrap.classList.add("theater-fullscreen");
  } else {
    if (overworldWrap) overworldWrap.classList.remove("theater-fullscreen");
    if (dungeonWrap) dungeonWrap.classList.add("theater-fullscreen");
  }
  syncTheaterHeader();
}

function syncTheaterHeader() {
  const collected = getCollectedItems();

  if (currentMapMode === "dungeon" && dungeonDatabase && dungeonDatabase[selectedPlaceId]) {
    const place = dungeonDatabase[selectedPlaceId];
    const tTitle = document.getElementById("theater-dungeon-title");
    if (tTitle) tTitle.textContent = place.name.toUpperCase();
    const tFloor = document.getElementById("theater-dungeon-floor");
    const currentFloor = (place.maps || []).find(m => m.id === activeFloorId);
    if (tFloor) tFloor.textContent = (currentFloor ? (currentFloor.label || currentFloor.id) : activeFloorId).toUpperCase();

    // Replicate tabs inside theater header
    const theaterTabsMount = document.getElementById("theater-floor-tabs");
    const mainTabsBar = document.getElementById("floor-tabs-bar");
    if (theaterTabsMount && mainTabsBar) {
      theaterTabsMount.innerHTML = mainTabsBar.innerHTML;
    }

    // Telemetry counts for theater dungeon view
    const allItems = place.items || [];
    const totGs = allItems.filter(it => it.cat === "gs").length;
    const doneGs = allItems.filter(it => it.cat === "gs" && collected.has(it.id)).length;
    const totHearts = allItems.filter(it => it.cat === "heart").length;
    const doneHearts = allItems.filter(it => it.cat === "heart" && collected.has(it.id)).length;
    const totSecrets = allItems.filter(it => it.cat === "fairy" || it.cat === "secret").length;
    const doneSecrets = allItems.filter(it => (it.cat === "fairy" || it.cat === "secret") && collected.has(it.id)).length;

    const tGs = document.getElementById("theater-gs-count");
    if (tGs) tGs.textContent = `${doneGs} / ${totGs}`;
    const tH = document.getElementById("theater-hearts-count");
    if (tH) tH.textContent = `${doneHearts} / ${totHearts}`;
    const tSec = document.getElementById("theater-secrets-count");
    if (tSec) tSec.textContent = `${doneSecrets} / ${totSecrets || 1}`;

    const tIcon = document.getElementById("theater-pins-icon");
    const tLabel = document.getElementById("theater-pins-label");
    if (tIcon && tLabel) {
      tIcon.textContent = isMapPinsVisible ? "🙈" : "👁️";
      tLabel.textContent = isMapPinsVisible ? "Ocultar Pines" : "Ver Pines";
    }
  } else if (currentMapMode === "overworld") {
    // Overworld global telemetry for theater header
    const ovPct = document.getElementById("theater-ov-pct");
    if (ovPct && currentMapData) {
      ovPct.textContent = `${currentMapData.discovery_percentage || 0}%`;
    }

    let globalTotGs = 0, globalDoneGs = 0;
    let globalTotH = 0, globalDoneH = 0;
    if (dungeonDatabase) {
      Object.values(dungeonDatabase).forEach(p => {
        (p.items || []).forEach(it => {
          if (it.cat === "gs") {
            globalTotGs++;
            if (collected.has(it.id)) globalDoneGs++;
          } else if (it.cat === "heart") {
            globalTotH++;
            if (collected.has(it.id)) globalDoneH++;
          }
        });
      });
    }

    const ovGs = document.getElementById("theater-ov-gs");
    if (ovGs) ovGs.textContent = `${globalDoneGs} / ${globalTotGs || 100}`;
    const ovH = document.getElementById("theater-ov-hearts");
    if (ovH) ovH.textContent = `${globalDoneH} / ${globalTotH || 36}`;
  }
}

// Live cross-window sync
window.addEventListener("storage", () => {
  renderDungeonView(selectedPlaceId);
  if (currentMapData && currentMapData.places) {
    renderOverworldMarkers(currentMapData.places);
  }
  renderKingdomsGrid();
  if (isTheaterActive) {
    syncTheaterHeader();
  }
});

function openMapPopout() {
  const w = 1240;
  const h = 860;
  const left = Math.max(0, Math.floor((window.screen.width - w) / 2));
  const top = Math.max(0, Math.floor((window.screen.height - h) / 2));
  const p = encodeURIComponent(selectedPlaceId || "fuente");
  const f = encodeURIComponent(activeFloorId || "");
  const m = encodeURIComponent(currentMapMode || "dungeon");
  window.open(
    `/static/popout.html?place=${p}&floor=${f}&mode=${m}`,
    "ZeldaNotesMapPopout",
    `width=${w},height=${h},top=${top},left=${left},resizable=yes,scrollbars=yes,status=no,toolbar=no,menubar=no`
  );
}

function showToastNotification(msg) {
  let toast = document.getElementById("purah-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "purah-toast";
    toast.className = "purah-toast";
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add("visible");
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.classList.remove("visible");
  }, 2200);
}

async function manualReloadData() {
  const btns = document.querySelectorAll(".header-refresh-btn, .theater-btn.refresh-btn");
  btns.forEach(b => b.classList.add("is-refreshing"));
  try {
    await fetchGameStatus();
    if (selectedPlaceId) {
      if (currentMapMode === "dungeon") {
        renderDungeonView(selectedPlaceId);
      } else if (currentMapData) {
        renderOverworldMap(currentMapData);
      }
    }
    showToastNotification("✨ Telemetría y mapas actualizados");
  } catch (err) {
    console.error("Error manual reloading:", err);
    showToastNotification("⚠️ Error al recargar telemetría");
  } finally {
    setTimeout(() => {
      btns.forEach(b => b.classList.remove("is-refreshing"));
    }, 600);
  }
}

// Global hotkeys (F to toggle theater, L to locate link, R to reload, Esc to exit)
document.addEventListener("keydown", (e) => {
  if (e.key === "f" || e.key === "F") {
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT")) return;
    toggleTheaterMode();
  } else if (e.key === "l" || e.key === "L") {
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT")) return;
    locateLink();
  } else if ((e.key === "r" || e.key === "R") && !e.ctrlKey && !e.metaKey) {
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT")) return;
    e.preventDefault();
    manualReloadData();
  } else if (e.key === "Escape" && isTheaterActive) {
    toggleTheaterMode();
  }
});

// ==========================================
// CONFIGURATION MODAL (Save Path Setup)
// ==========================================
async function openConfigModal() {
  const modal = document.getElementById("config-modal");
  if (!modal) return;
  modal.style.display = "flex";
  try {
    const res = await fetch("/api/config");
    if (res.ok) {
      const data = await res.json();
      const input = document.getElementById("cfg-save-path");
      if (input) input.value = data.nx2navi_save_path || "";
      const hint = document.getElementById("cfg-detected-hint");
      if (hint) {
        hint.textContent = `Detección automática: ${data.detected_default} (${data.active_exists ? 'ACTIVA' : 'NO DETECTADA'})`;
      }
    }
  } catch (err) {
    console.error("Config fetch error:", err);
  }
}

function closeConfigModal() {
  const modal = document.getElementById("config-modal");
  if (modal) modal.style.display = "none";
}

async function saveConfigPath() {
  const input = document.getElementById("cfg-save-path");
  const newPath = input ? input.value.trim() : "";
  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nx2navi_save_path: newPath })
    });
    if (res.ok) {
      closeConfigModal();
      lastSavedTimestamp = 0;
      fetchGameStatus();
    }
  } catch (err) {
    alert("Error guardando la ruta: " + err);
  }
}

async function resetConfigDefault() {
  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nx2navi_save_path: "" })
    });
    if (res.ok) {
      closeConfigModal();
      lastSavedTimestamp = 0;
      fetchGameStatus();
    }
  } catch (err) {
    alert("Error restableciendo: " + err);
  }
}

// ==========================================
// LAN / MOBILE ACCESS MODAL
// ==========================================
let currentLanInfo = null;

async function fetchLanInfo() {
  if (currentLanInfo) return currentLanInfo;
  try {
    const res = await fetch("/api/lan_info");
    if (res.ok) {
      currentLanInfo = await res.json();
    }
  } catch (err) {
    console.error("Error fetching LAN info:", err);
  }
  return currentLanInfo;
}

async function openLanModal() {
  const modal = document.getElementById("lan-modal");
  if (!modal) return;
  modal.style.display = "flex";

  const info = await fetchLanInfo();
  const lanUrl = info && info.url ? info.url : `http://${window.location.hostname}:8080`;
  const popoutUrl = info && info.popout_url ? info.popout_url : `http://${window.location.hostname}:8080/popout`;

  const disp = document.getElementById("lan-url-display");
  if (disp) disp.textContent = lanUrl;

  const popDisp = document.getElementById("popout-url-display");
  if (popDisp) popDisp.textContent = popoutUrl;

  const qrImg = document.getElementById("lan-qr-img");
  if (qrImg) {
    qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(lanUrl)}`;
  }
}

function closeLanModal() {
  const modal = document.getElementById("lan-modal");
  if (modal) modal.style.display = "none";
}

async function copyLanUrl(type) {
  const info = await fetchLanInfo();
  const url = (type === "popout") 
    ? (info && info.popout_url ? info.popout_url : `http://${window.location.hostname}:8080/popout`)
    : (info && info.url ? info.url : `http://${window.location.hostname}:8080`);

  const btnId = (type === "popout") ? "copy-popout-btn" : "copy-lan-btn";
  const btn = document.getElementById(btnId);

  try {
    await navigator.clipboard.writeText(url);
    if (btn) {
      const orig = btn.innerHTML;
      btn.innerHTML = "✅ ¡Copiado!";
      btn.style.color = "#00ffaa";
      setTimeout(() => {
        btn.innerHTML = orig;
        btn.style.color = "";
      }, 2000);
    }
  } catch (e) {
    prompt("Copia este enlace para tu móvil:", url);
  }
}

// ==========================================
// INTERACTIVE MAP ZOOM & PAN ENGINE
// ==========================================
class MapZoomController {
  constructor(canvasEl, stageEl, options = {}) {
    this.canvas = canvasEl;
    this.stage = stageEl;
    this.scale = 1.0;
    this.minScale = options.minScale || 0.6;
    this.maxScale = options.maxScale || 4.0;
    this.panX = 0;
    this.panY = 0;
    this.isDragging = false;
    this.startX = 0;
    this.startY = 0;
    this.onZoomChange = options.onZoomChange || null;

    this.init();
  }

  init() {
    this.stage.style.transformOrigin = "center center";

    // Disable native HTML5 element/image dragging
    this.canvas.addEventListener("dragstart", (e) => {
      e.preventDefault();
      return false;
    });

    // Mouse wheel zoom (centered at cursor)
    this.canvas.addEventListener("wheel", (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.18 : 0.85;
      this.zoomAt(zoomFactor, e.clientX, e.clientY);
    }, { passive: false });

    // Drag / Pan with mouse
    this.canvas.addEventListener("mousedown", (e) => {
      if (e.button !== 0) return;
      if (e.target.closest(".dungeon-item-pin, .poi-marker, button, .beacon-hud-card, .map-zoom-controls")) return;
      e.preventDefault(); // Stop native drag and text selection
      this.isDragging = true;
      this.startX = e.clientX - this.panX;
      this.startY = e.clientY - this.panY;
      this.canvas.classList.add("is-panning");
      document.body.style.userSelect = "none";
    });

    window.addEventListener("mousemove", (e) => {
      if (!this.isDragging) return;
      e.preventDefault();
      this.panX = e.clientX - this.startX;
      this.panY = e.clientY - this.startY;
      this.applyTransform(false);
    });

    window.addEventListener("mouseup", () => {
      if (this.isDragging) {
        this.isDragging = false;
        this.canvas.classList.remove("is-panning");
        document.body.style.userSelect = "";
      }
    });

    window.addEventListener("blur", () => {
      if (this.isDragging) {
        this.isDragging = false;
        this.canvas.classList.remove("is-panning");
        document.body.style.userSelect = "";
      }
    });

    // Touch events for mobile / tablets / Steam Deck
    let initialPinchDist = null;
    let initialPinchScale = 1.0;

    this.canvas.addEventListener("touchstart", (e) => {
      if (e.touches.length === 1) {
        if (e.target.closest(".dungeon-item-pin, .poi-marker, button, .beacon-hud-card, .map-zoom-controls")) return;
        this.isDragging = true;
        this.startX = e.touches[0].clientX - this.panX;
        this.startY = e.touches[0].clientY - this.panY;
      } else if (e.touches.length === 2) {
        this.isDragging = false;
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        initialPinchDist = Math.hypot(dx, dy);
        initialPinchScale = this.scale;
      }
    }, { passive: true });

    this.canvas.addEventListener("touchmove", (e) => {
      if (this.isDragging && e.touches.length === 1) {
        this.panX = e.touches[0].clientX - this.startX;
        this.panY = e.touches[0].clientY - this.startY;
        this.applyTransform(false);
      } else if (e.touches.length === 2 && initialPinchDist) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const dist = Math.hypot(dx, dy);
        const factor = dist / initialPinchDist;
        this.scale = Math.min(this.maxScale, Math.max(this.minScale, initialPinchScale * factor));
        this.applyTransform(false);
      }
    }, { passive: true });

    this.canvas.addEventListener("touchend", () => {
      this.isDragging = false;
      initialPinchDist = null;
    });

    // Double click to zoom in / reset
    this.canvas.addEventListener("dblclick", (e) => {
      if (e.target.closest(".dungeon-item-pin, .poi-marker, button, .map-zoom-controls")) return;
      if (this.scale > 1.25) {
        this.reset();
      } else {
        this.zoomAt(2.0, e.clientX, e.clientY);
      }
    });
  }

  zoomAt(factor, clientX, clientY) {
    const prevScale = this.scale;
    let newScale = prevScale * factor;
    newScale = Math.min(this.maxScale, Math.max(this.minScale, newScale));
    if (newScale === prevScale) return;

    if (clientX !== undefined && clientY !== undefined) {
      const rect = this.canvas.getBoundingClientRect();
      const ox = clientX - rect.left - rect.width / 2;
      const oy = clientY - rect.top - rect.height / 2;
      this.panX -= (ox - this.panX) * (newScale / prevScale - 1);
      this.panY -= (oy - this.panY) * (newScale / prevScale - 1);
    }

    this.scale = newScale;
    this.applyTransform(true);
  }

  zoomIn() {
    this.zoomAt(1.25);
  }

  zoomOut() {
    this.zoomAt(0.8);
  }

  reset() {
    this.scale = 1.0;
    this.panX = 0;
    this.panY = 0;
    this.applyTransform(true);
  }

  applyTransform(smooth = false) {
    this.stage.style.transition = smooth ? "transform 0.18s cubic-bezier(0.2, 0.8, 0.2, 1)" : "none";
    this.stage.style.transform = `translate(${this.panX}px, ${this.panY}px) scale(${this.scale})`;
    if (this.onZoomChange) {
      this.onZoomChange(this.scale);
    }
  }
}

let dungeonZoomController = null;
let overworldZoomController = null;

function initZoomControllers() {
  const dungeonCanvas = document.getElementById("dungeon-canvas");
  const dungeonStage = document.getElementById("dungeon-map-stage");
  if (dungeonCanvas && dungeonStage) {
    dungeonZoomController = new MapZoomController(dungeonCanvas, dungeonStage, {
      minScale: 0.7,
      maxScale: 4.0,
      onZoomChange: (scale) => {
        const pctEl = document.getElementById("dungeon-zoom-pct");
        if (pctEl) pctEl.textContent = `${Math.round(scale * 100)}%`;
      }
    });
  }

  const overworldCanvas = document.getElementById("map-canvas-container");
  const overworldStage = document.getElementById("overworld-map-stage");
  if (overworldCanvas && overworldStage) {
    overworldZoomController = new MapZoomController(overworldCanvas, overworldStage, {
      minScale: 0.6,
      maxScale: 3.5,
      onZoomChange: (scale) => {
        const pctEl = document.getElementById("overworld-zoom-pct");
        if (pctEl) pctEl.textContent = `${Math.round(scale * 100)}%`;
      }
    });
  }
}

function zoomInMap() {
  if (currentMapMode === "dungeon" && dungeonZoomController) {
    dungeonZoomController.zoomIn();
  } else if (overworldZoomController) {
    overworldZoomController.zoomIn();
  }
}

function zoomOutMap() {
  if (currentMapMode === "dungeon" && dungeonZoomController) {
    dungeonZoomController.zoomOut();
  } else if (overworldZoomController) {
    overworldZoomController.zoomOut();
  }
}

function resetZoomMap() {
  if (currentMapMode === "dungeon" && dungeonZoomController) {
    dungeonZoomController.reset();
  } else if (overworldZoomController) {
    overworldZoomController.reset();
  }
}

// ==========================================
// REACTIVE TELEMETRY SUBSCRIBER (PUB/SUB & SSE)
// ==========================================
let latestTimeInfo = null;
let latestTimeReceivedAt = 0;

function updateAtmosphericLighting(timeInfo) {
  // Funcionalidad de tiempo/luz ambiental descartada temporalmente
  const svgImg = document.getElementById("dungeon-floor-svg");
  if (svgImg) svgImg.style.filter = "none";
}

function renderTimeDisplays(timeInfo) {
  // Funcionalidad de reloj descartada temporalmente
}

function updateHeroVitalsDisplay(v) {
  if (!v) return;
  // Skulltulas totales en vivo
  if (v.skulls !== undefined) {
    const ovGs = document.getElementById("theater-ov-gs");
    if (ovGs) ovGs.textContent = `${v.skulls} / 100`;
  }
}

// Reactive Consumer / Dispatcher (Kafka-style listener)
function dispatchTelemetry(data) {
  if (!data || !data.online || !data.in_game) return;
  isLiveTracking = true;

  const events = data.events || {};

  // TOPIC: HERO VITALS (Rupias, Salud, Magia, Municiones en vivo)
  const vitals = events.vitals || data.hero_vitals;
  if (vitals) {
    updateHeroVitalsDisplay(vitals);
  }

  // TOPIC 2: SCENE / PLACE CHANGE EVENT
  const sceneEv = events.scene || {};
  const detectedPlace = sceneEv.place_id || data.detected_place;
  const detectedFloor = sceneEv.floor || data.detected_floor;

  if (detectedPlace && detectedPlace !== lastPhysicalDetectedPlace) {
    lastPhysicalDetectedPlace = detectedPlace;
    lastPhysicalDetectedFloor = detectedFloor;
    isUserBrowsing = false;
    userFloorOverride = null;
    selectedPlaceId = detectedPlace;
    activeFloorId = detectedFloor || null;
    lastRenderedPlaceId = null;
    if (currentMapMode === "dungeon") {
      renderDungeonView(selectedPlaceId, activeFloorId);
    }
  } else if (detectedPlace && detectedPlace !== selectedPlaceId && !isUserBrowsing) {
    selectedPlaceId = detectedPlace;
    userFloorOverride = null;
    if (currentMapMode === "dungeon") {
      renderDungeonView(selectedPlaceId);
    }
  }

  // Floor transition
  if (currentMapMode === "dungeon" && detectedFloor && detectedFloor !== activeFloorId && !userFloorOverride) {
    if (floorCandidate === detectedFloor) {
      floorCandidateCount++;
      if (floorCandidateCount >= 3) {
        activeFloorId = detectedFloor;
        floorCandidate = null;
        floorCandidateCount = 0;
        renderDungeonView(selectedPlaceId);
      }
    } else {
      floorCandidate = detectedFloor;
      floorCandidateCount = 1;
    }
  } else {
    floorCandidate = null;
    floorCandidateCount = 0;
  }

  // TOPIC 3: POSITION / HERO BEACON EVENT
  const posEv = events.position || {};
  const dx = (posEv.dungeon_x !== undefined) ? posEv.dungeon_x : data.dungeon_x;
  const dy = (posEv.dungeon_y !== undefined) ? posEv.dungeon_y : data.dungeon_y;
  const displayCoords = posEv.display || data.coords_display;

  const hudCoord = document.getElementById("hud-coords-text");
  if (hudCoord && displayCoords) {
    const flLabel = detectedFloor ? `[${detectedFloor}] ` : "";
    hudCoord.innerHTML = `<span style="color:#00ffff; font-size:10px; font-weight:bold; margin-right:4px; text-shadow:0 0 6px #00ffff;">● RAM LIVE</span> ${flLabel}${displayCoords}`;
  }

  if (currentMapMode === "dungeon") {
    const beacon = document.getElementById("dungeon-hero-beacon");
    if (beacon) {
      if (selectedPlaceId === detectedPlace && dx !== undefined && dy !== undefined) {
        beacon.style.display = "flex";
        lastLiveX = dx;
        lastLiveY = dy;
        beacon.style.left = `${dx}%`;
        beacon.style.top = `${dy}%`;
      } else {
        beacon.style.display = "none";
      }
    }
  }

  // TOPIC 4: INVENTORY / ACTIVE EQUIPPED EVENT
  const invItems = events.inventory || data.live_inventory;
  if (Array.isArray(invItems) && invItems.length > 0) {
    const activeIds = new Set(invItems.map(it => it.id));
    document.querySelectorAll(".item-card[data-id]").forEach(card => {
      const cardId = card.getAttribute("data-id");
      card.classList.toggle("live-equipped-pulse", activeIds.has(cardId));
    });
  }

  // TOPIC 5: NEARBY RADAR PROXIMITY EVENT
  const nearby = events.nearby || data.nearby_collectibles;
  const targetPill = document.getElementById("hud-target-proximity");
  if (Array.isArray(nearby) && nearby.length > 0) {
    const closest = nearby[0];
    const cIcon = closest.cat === "gs" ? "🕷️" : (closest.cat === "heart" ? "❤️" : (closest.cat === "fairy" ? "🧚" : "✨"));
    if (targetPill) {
      targetPill.style.display = "inline-flex";
      targetPill.innerHTML = `<span style="color:#ffcc00; font-weight:bold; margin-right:5px;">🎯 ${cIcon} CERCA:</span> <span style="color:#fff; font-weight:600;">${closest.name}</span> <span style="color:#aaa; font-size:10px; margin-left:6px;">(${closest.dist_pct}%)</span>`;
    }
    document.querySelectorAll(".dungeon-item-card").forEach(c => {
      c.classList.toggle("nearby-target-pulse", c.getAttribute("data-id") === closest.id);
    });
  } else {
    if (targetPill) targetPill.style.display = "none";
    document.querySelectorAll(".dungeon-item-card.nearby-target-pulse").forEach(c => c.classList.remove("nearby-target-pulse"));
  }

  // TOPIC 6: COLLECTED ITEMS / TOKENS EVENT
  const collectedIds = data.collected_item_ids || events.collected;
  if (Array.isArray(collectedIds) && collectedIds.length > 0) {
    let hasNew = false;
    collectedIds.forEach(id => {
      if (!serverCollectedIds.has(id)) {
        serverCollectedIds.add(id);
        hasNew = true;
      }
    });
    if (hasNew) {
      if (currentMapMode === "dungeon" && selectedPlaceId) {
        renderDungeonView(selectedPlaceId, activeFloorId);
      } else if (currentMapMode === "world") {
        renderPlacesList();
      }
    }
  }
}

// SSE Subscriber Stream
function subscribeTelemetry() {
  if (telemetryEventSource) {
    try { telemetryEventSource.close(); } catch (e) {}
    telemetryEventSource = null;
  }

  try {
    const streamUrl = `/api/stream?place=${encodeURIComponent(selectedPlaceId || "")}`;
    telemetryEventSource = new EventSource(streamUrl);

    telemetryEventSource.onmessage = (evt) => {
      try {
        const frame = JSON.parse(evt.data);
        dispatchTelemetry(frame);
      } catch (err) {}
    };

    telemetryEventSource.onerror = () => {
      try { telemetryEventSource.close(); } catch (e) {}
      telemetryEventSource = null;
      setTimeout(subscribeTelemetry, 2500);
    };
  } catch (e) {
    console.warn("EventSource not available, falling back to interval polling.");
  }
}

// High-frequency polling fallback
async function pollLiveCoords() {
  if (telemetryEventSource && telemetryEventSource.readyState === EventSource.OPEN) {
    return; // Stream is active, no need to poll
  }
  try {
    const res = await fetch(`/api/live_coords?place=${encodeURIComponent(selectedPlaceId)}`);
    if (!res.ok) return;
    const data = await res.json();
    dispatchTelemetry(data);
  } catch (e) {}
}

async function initCanonicalDatabase() {
  try {
    const res = await fetch("/api/canonical_db");
    if (res.ok) {
      canonicalDatabase = await res.json();
      window.CANONICAL_DB = canonicalDatabase;
      console.log("✅ Canonical Database Loaded:", Object.keys(canonicalDatabase.items || {}).length, "items,", (canonicalDatabase.collectibles && canonicalDatabase.collectibles.total_count) || 0, "collectibles");
    }
  } catch (err) {
    console.error("Failed to load canonical database:", err);
  }
}

// Init
document.addEventListener("DOMContentLoaded", async () => {
  await Promise.all([initDungeonDatabase(), initCanonicalDatabase()]);
  initZoomControllers();
  fetchGameStatus();
  subscribeTelemetry();
  refreshInterval = setInterval(fetchGameStatus, 3000);
  liveCoordsInterval = setInterval(pollLiveCoords, 500);
});
