#!/usr/bin/with-contenv bashio

bashio::log.info "Démarrage Traffic Map Generator..."

# Récupérer la config depuis l'addon
LAT=$(bashio::config 'latitude')
LON=$(bashio::config 'longitude')
ZOOM=$(bashio::config 'zoom')
WIDTH=$(bashio::config 'width')
HEIGHT=$(bashio::config 'height')
INTERVAL=$(bashio::config 'update_interval')
AZURE_KEY=$(bashio::config 'azure_key')

bashio::log.info "Config: Lat=$LAT, Lon=$LON, Zoom=$ZOOM, Interval=${INTERVAL}s"

# Boucle infinie de génération
while true; do
    bashio::log.info "Génération de la carte..."
    
    python3 << EOF
import math, random, time, requests, os
from io import BytesIO
from PIL import Image

# Config depuis les variables d'environnement
LAT, LON = float("$LAT"), float("$LON")
ZOOM = int("$ZOOM")
WIDTH, HEIGHT = int("$WIDTH"), int("$HEIGHT")
AZURE_KEY = "$AZURE_KEY"
TILE = 256

CARTO_SUBDOMAINS = ["a", "b", "c", "d"]
BASE_URL_TMPL = "https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}.png"

def latlon_to_pixel(lat, lon, z):
    n = 2 ** z
    sinlat = math.sin(math.radians(lat))
    x = (lon + 180.0) / 360.0 * n * TILE
    y = (1 - math.log((1 + sinlat) / (1 - sinlat)) / (2 * math.pi)) / 2 * n * TILE
    return x, y

def fetch_tile(url, headers=None, retries=2, timeout=8):
    headers = headers or {}
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return Image.open(BytesIO(r.content)).convert("RGBA")
        except Exception:
            pass
        if attempt < retries:
            time.sleep(0.3 * (attempt + 1))
    return None

px_c, py_c = latlon_to_pixel(LAT, LON, ZOOM)
px0, py0 = px_c - WIDTH/2, py_c - HEIGHT/2
px1, py1 = px0 + WIDTH, py0 + HEIGHT

tx0 = int(math.floor(px0 / TILE))
ty0 = int(math.floor(py0 / TILE))
tx1 = int(math.floor((px1 - 1) / TILE))
ty1 = int(math.floor((py1 - 1) / TILE))

canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
ua = {"User-Agent": "HomeAssistant-TrafficMap/1.0"}

for tx in range(tx0, tx1 + 1):
    for ty in range(ty0, ty1 + 1):
        subdomain = random.choice(CARTO_SUBDOMAINS)
        base_url = BASE_URL_TMPL.format(s=subdomain, z=ZOOM, x=tx, y=ty)
        
        base = fetch_tile(base_url, headers=ua)
        if base is None:
            base = Image.new("RGBA", (TILE, TILE), (40, 40, 40, 255))
        
        traffic_url = (
            f"https://atlas.microsoft.com/traffic/flow/tile/png"
            f"?api-version=1.0&style=relative&zoom={ZOOM}&x={tx}&y={ty}"
            f"&subscription-key={AZURE_KEY}"
        )
        
        traffic = fetch_tile(traffic_url)
        if traffic is not None:
            base.alpha_composite(traffic)
        
        x_pix = int(round(tx * TILE - px0))
        y_pix = int(round(ty * TILE - py0))
        canvas.alpha_composite(base, (x_pix, y_pix))

output_dir = "/config/www"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "traffic_overlay.png")
canvas.save(output_path)
print(f"✅ Carte sauvegardée: {output_path}")
EOF

    if [ $? -eq 0 ]; then
        bashio::log.info "✅ Carte générée avec succès"
    else
        bashio::log.error "❌ Erreur lors de la génération"
    fi
    
    # Attendre avant la prochaine génération
    sleep $INTERVAL
done
