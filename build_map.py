#!/usr/bin/env python3
"""
Build ufo_map.html from cached ufo_data_export.json.
Run:  python3 build_map.py
No network requests, no API calls — instant rebuild from local data.
"""

import json
import os
import sys
from datetime import datetime
from constants import MISSING_SCIENTISTS as _MISSING_SCIENTISTS_LIVE

EXPORT_FILE = "ufo_data_export.json"
OUTPUT_MAP  = "index.html"

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def load_export(path=EXPORT_FILE):
    if not os.path.exists(path):
        print(f"❌  {path} not found. Run export_data.py first to generate it.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    counts = data.get("counts", {})
    print(f"📂  Loaded {path}  (exported {data.get('exported_at','?')})")
    for k, v in counts.items():
        print(f"    {k}: {v}")
    return data


# ---------------------------------------------------------------------------
# Build the HTML map
# ---------------------------------------------------------------------------

def build_map(sightings, abduction_sightings, military_bases, cog_sites, uso_sites,
              missing_411=None, reddit_missing=None, missing_scientists=None,
              parallel_33_sites=None, nuclear_sites=None,
              cattle_mutilation_sites=None, window_areas=None, ley_lines=None,
              water_anomaly_sites=None, local_news=None,
              nuforc_recent=None, seismic_activity=None, humanoid_encounters=None,
              asrs_reports=None, asa_reports=None):
    if missing_411 is None:
        missing_411 = []
    if reddit_missing is None:
        reddit_missing = []
    if missing_scientists is None:
        missing_scientists = []
    if nuforc_recent is None:
        nuforc_recent = []
    if seismic_activity is None:
        seismic_activity = []
    if humanoid_encounters is None:
        humanoid_encounters = []
    if parallel_33_sites is None:
        parallel_33_sites = []
    if nuclear_sites is None:
        nuclear_sites = []
    if cattle_mutilation_sites is None:
        cattle_mutilation_sites = []
    if window_areas is None:
        window_areas = []
    if ley_lines is None:
        ley_lines = []
    if water_anomaly_sites is None:
        water_anomaly_sites = []
    if local_news is None:
        local_news = []
    if asrs_reports is None:
        asrs_reports = []
    if asa_reports is None:
        asa_reports = []
    nuforc_count      = sum(1 for s in sightings if s["source"] == "NUFORC")
    reddit_count      = len(sightings) - nuforc_count
    abduction_count   = len(abduction_sightings)
    local_news_count  = len(local_news)

    print(f"\n🗺️   Building map …")
    print(f"     {len(sightings)} sightings  |  {abduction_count} abductions  "
          f"|  {len(military_bases)} bases  |  {len(cog_sites)} COG  "
          f"|  {len(uso_sites)} USO  |  {len(missing_411)} Missing 411  "
          f"|  {len(missing_scientists)} Missing Scientists")

    markers_json = json.dumps([{
        "lat":      s["lat"],
        "lon":      s["lon"],
        "source":   s["source"],
        "date":     s["date"],
        "location": s.get("location_label") or s.get("location") or "Unknown",
        "shape":    s.get("shape", "unknown"),
        "duration": s.get("duration", ""),
        "summary":  (s.get("summary") or "")[:200].replace('"', '&quot;').replace("'", "&#39;"),
        "url":      s.get("url", ""),
    } for s in sightings])

    abduction_json = json.dumps([{
        "lat":      s["lat"],
        "lon":      s["lon"],
        "source":   s["source"],
        "date":     s["date"],
        "location": s.get("location_label") or s.get("location") or "Unknown",
        "summary":  (s.get("summary") or "")[:200].replace('"', '&quot;').replace("'", "&#39;"),
        "url":      s.get("url", ""),
    } for s in abduction_sightings])

    bases_json      = json.dumps(military_bases)
    cog_json        = json.dumps(cog_sites)
    uso_json        = json.dumps(uso_sites)
    missing_json        = json.dumps(missing_411)
    reddit_missing_json = json.dumps(reddit_missing)
    scientists_json     = json.dumps(missing_scientists)
    p33_json        = json.dumps(parallel_33_sites)
    nuclear_json    = json.dumps(nuclear_sites)
    cattle_json     = json.dumps(cattle_mutilation_sites)
    windows_json    = json.dumps(window_areas)
    leylines_json   = json.dumps(ley_lines)
    water_json      = json.dumps(water_anomaly_sites)
    local_news_json      = json.dumps(local_news)
    nuforc_recent_json   = json.dumps(nuforc_recent)
    seismic_json         = json.dumps(seismic_activity)
    humanoid_json        = json.dumps(humanoid_encounters)
    asrs_json            = json.dumps(asrs_reports)
    asa_json             = json.dumps(asa_reports)

    # Hardcoded curated datasets — not fetched, not in export
    elongated_skulls = [
        {"name": "Paracas Peninsula", "lat": -13.8350, "lon": -76.2500, "country": "Peru", "status": "Confirmed - 300+ skulls, auburn hair, anomalous DNA", "notes": "Largest collection of elongated skulls worldwide. DNA testing showed unusual haplogroups. Infant skulls found elongated at birth before binding possible."},
        {"name": "Nazca", "lat": -14.8290, "lon": -74.9435, "country": "Peru", "status": "Confirmed", "notes": "Elongated skulls dated 200-100 BC found alongside famous geoglyphs"},
        {"name": "Tiwanaku", "lat": -16.5533, "lon": -68.6736, "country": "Bolivia", "status": "Confirmed", "notes": "Major elongated skull site along Path of Viracocha"},
        {"name": "Puma Punku", "lat": -16.5544, "lon": -68.6678, "country": "Bolivia", "status": "Confirmed", "notes": "Adjacent to Tiwanaku, precision stonework defying conventional explanation"},
        {"name": "Arica", "lat": -18.4783, "lon": -70.3126, "country": "Chile", "status": "Confirmed", "notes": "Chinchorro mummies - world's oldest at 7,000 years, predating Egypt by 4,000 years. Many elongated skulls."},
        {"name": "Iquique", "lat": -20.2208, "lon": -70.1431, "country": "Chile", "status": "Confirmed", "notes": "Chinchorro elongated skulls displayed in Museo Regional de Iquique"},
        {"name": "Cusco", "lat": -13.5320, "lon": -71.9675, "country": "Peru", "status": "Confirmed", "notes": "Multiple elongated skull specimens including Huayqui mummified child whose skull is nearly the size of its torso"},
        {"name": "Cajamarca", "lat": -7.1638, "lon": -78.5003, "country": "Peru", "status": "Confirmed", "notes": "Northern end of the Path of Viracocha elongated skull corridor"},
        {"name": "Potosi", "lat": -19.5836, "lon": -65.7531, "country": "Bolivia", "status": "Confirmed", "notes": "Casa de la Monedas museum contains elongated skulls from the region"},
        {"name": "Oruro", "lat": -17.9667, "lon": -67.1167, "country": "Bolivia", "status": "Confirmed", "notes": "Elongated skull specimens, part of broader Andean corridor"},
        {"name": "Volcan Tunupa", "lat": -19.6333, "lon": -67.9333, "country": "Bolivia", "status": "Confirmed", "notes": "Cave site with elongated skulls above Uyuni salt flats"},
        {"name": "Lima Museum of Anthropology", "lat": -12.0739, "lon": -77.0839, "country": "Peru", "status": "Confirmed", "notes": "Contains over 10,000 ancient skulls - possibly largest collection in the world. Hundreds of Paracas elongated specimens."},
        {"name": "Amarna", "lat": 27.6453, "lon": 30.9004, "country": "Egypt", "status": "Confirmed", "notes": "Elongated skulls from Akhenaten period. Royal family depicted with elongated heads in art."},
        {"name": "Colca Valley", "lat": -15.6333, "lon": -71.8333, "country": "Peru", "status": "Confirmed", "notes": "Collagua people elongated skulls dated 1100-1450 AD"},
    ]
    anomalous_spheres = [
        {"name": "Buga Sphere", "lat": 3.8990, "lon": -76.2986, "country": "Colombia", "status": "Under investigation 2025", "notes": "Metallic sphere landed March 2 2025. No welds or seams. Three concentric metal layers with 9 internal microspheres. Weight mysteriously increased from 2kg to 10kg. People touching it lost fingerprints temporarily. X-rays show complex internal structure inconsistent with known manufacturing."},
        {"name": "Betz Sphere", "lat": 30.3322, "lon": -81.6557, "country": "USA", "status": "Unexplained 1974", "notes": "Steel-like orb found in Florida after wildfire 1974. Exhibited autonomous movement, strange acoustic resonances, no seams or joints. Never fully explained."},
        {"name": "Klerksdorp Spheres", "lat": -26.8667, "lon": -26.6667, "country": "South Africa", "status": "Confirmed anomalous", "notes": "Pyrophyllite spheres dated 3 billion years old with perfect grooves and symmetry inconsistent with natural geological processes."},
    ]
    power_sites = [
        {"name": "Bohemian Grove", "lat": 38.5185, "lon": -123.0264, "location": "Monte Rio, California", "type": "Annual Retreat", "notes": "2,700-acre private redwood campground. Every July, ~200 of the world's most powerful men gather for 2 weeks. Members include presidents, CEOs, media chiefs, military leaders. Features the Cremation of Care ceremony before a 40-foot concrete owl. Strict no-press, no-phone policy. Reagan and Nixon photographed here 1967. Alex Jones infiltrated and filmed the owl ceremony in 2000. Motto: Weaving spiders come not here."},
        {"name": "Skull and Bones Tomb", "lat": 41.3112, "lon": -72.9246, "location": "Yale University, New Haven CT", "type": "Secret Society HQ", "notes": "The Tomb - windowless building constructed 1856. 15 Yale seniors tapped annually. Members include Presidents Bush Sr and Jr, John Kerry, William Taft. Allegedly houses stolen artifacts including Geronimo's skull. Underground tunnels rumored. Founded 1832."},
        {"name": "Bilderberg 2024 Location", "lat": 50.8503, "lon": 4.3517, "location": "Brussels, Belgium", "type": "Annual Meeting", "notes": "Annual closed-door meeting of ~130 North Atlantic elites from finance, government, intelligence, academia and media. No press allowed. No minutes published. Attendees include Kissinger, Rockefeller, Gates, European heads of state. Meeting location changes annually."},
        {"name": "Council on Foreign Relations", "lat": 40.7736, "lon": -73.9566, "location": "New York City, NY", "type": "Elite Think Tank", "notes": "Harold Pratt House, NYC. Founded 1921. 3,000+ elite members from government, military, banking, media. Publishes Foreign Affairs journal. Critics call it the shadow government. Members include almost every Secretary of State since 1945."},
        {"name": "Trilateral Commission HQ", "lat": 40.7580, "lon": -73.9855, "location": "New York City, NY", "type": "Elite Organization", "notes": "Founded 1973 by David Rockefeller and Zbigniew Brzezinski. Coordinates policy between North America, Europe and Japan. Many members overlap with Bilderberg and CFR. Critics allege it coordinates global economic policy outside democratic oversight."},
        {"name": "Jekyll Island Club", "lat": 31.0543, "lon": -81.4134, "location": "Jekyll Island, Georgia", "type": "Historic Secret Meeting", "notes": "Site of secret 1910 meeting where the Federal Reserve was designed. Seven men representing 1/4 of the world's wealth met in total secrecy for 9 days. Attendees included representatives of Rockefeller, Morgan and Rothschild banking interests. The meeting was kept secret for 20 years."},
        {"name": "Grove Hotel Bilderberg 1954", "lat": 51.8021, "lon": -0.3933, "location": "Hertfordshire, England", "type": "Historic Meeting", "notes": "Site of first ever Bilderberg meeting 1954. Organized by Prince Bernhard of Netherlands and Polish socialist Joseph Retinger. Brought together 50 prominent citizens from both sides of the Atlantic for secret discussions."},
        {"name": "Davos World Economic Forum", "lat": 46.8182, "lon": 9.8457, "location": "Davos, Switzerland", "type": "Annual Meeting", "notes": "Annual gathering of global elite in Swiss Alps. 2,500+ attendees including heads of state, billionaires, CEOs of largest corporations. Critics call it unelected global governance. Founded by Klaus Schwab 1971. Famous for Great Reset proposals."},
        {"name": "Club of Rome HQ", "lat": 46.9480, "lon": 7.4474, "location": "Bern, Switzerland", "type": "Elite Think Tank", "notes": "Founded 1968 by Aurelio Peccei and Alexander King. 100 full members - scientists, economists, business leaders. Published Limits to Growth 1972 predicting resource depletion. Critics allege it advocates global population reduction and one world government."},
        {"name": "Chatham House", "lat": 51.5074, "lon": -0.1394, "location": "London, England", "type": "Elite Think Tank", "notes": "Royal Institute of International Affairs. Founded 1920. Home of the Chatham House Rule - meetings held under condition that attendees cannot reveal who said what. Hugely influential on UK and global foreign policy. Regular attendees include royalty, prime ministers, intelligence chiefs."},
        {"name": "Tavistock Institute", "lat": 51.5228, "lon": -0.1307, "location": "London, England", "type": "Psychological Research", "notes": "Founded 1947 with Rockefeller funding. Specializes in human relations and group behavior. Critics allege it has been used to develop mass social engineering and psychological manipulation techniques. Connected to MKUltra research through funding networks."},
        {"name": "Esalen Institute", "lat": 36.1332, "lon": -121.6274, "location": "Big Sur, California", "type": "Influence Center", "notes": "Founded 1962. Known as the birthplace of the human potential movement. Hosted secret back-channel US-Soviet diplomacy during Cold War. Regular attendees included CIA figures, academic elites, and counterculture leaders simultaneously. Called a CIA social experiment by some researchers."},
        {"name": "Montauk Air Force Station", "lat": 41.0776, "lon": -71.8630, "location": "Montauk, New York", "type": "Alleged Black Site", "notes": "Decommissioned radar station allegedly site of Project Montauk - claimed continuation of Philadelphia Experiment involving time travel, teleportation and mind control experiments. No official confirmation. Underground facilities rumored. Inspired Stranger Things."},
        {"name": "Area 51 Groom Lake", "lat": 37.2350, "lon": -115.8111, "location": "Nevada", "type": "Classified Facility", "notes": "Officially the Nevada Test and Training Range. Classified USAF facility. Existence denied until 2013 CIA declassification. Alleged testing site for UAP reverse engineering programs. No fly zone. Deadly force authorized perimeter. Home of U-2 and SR-71 development programs."},
        {"name": "Pine Gap", "lat": -23.7987, "lon": 133.7370, "location": "Alice Springs, Australia", "type": "Joint Intelligence Facility", "notes": "Joint US-Australian intelligence facility. Officially a satellite control station. Allegedly key node in ECHELON global surveillance network. Processes signals intelligence from across Asia and Middle East. Australian politicians denied knowledge of its true function for decades."},
    ]
    power_json   = json.dumps(power_sites)
    skulls_json  = json.dumps(elongated_skulls)
    spheres_json = json.dumps(anomalous_spheres)
    alien_mummies = [
        {"name": "Maria", "lat": -14.8290, "lon": -74.9435, "location": "Nazca, Peru", "status": "CONTESTED", "description": "Three-fingered female mummy, elongated skull, 35-45 years old at death. Forensic archaeologist Flavio Estrada (Peru 2024): fabricated from animal bones and synthetic glue. Dr Jose Zalce (Mexican Navy): biological organism with human-like internal structures, shows major trauma wounds. Fingerprints found to be unlike any human pattern. DNA 30% unidentified per UNAM carbon dating."},
        {"name": "Wawita", "lat": -14.8290, "lon": -74.9535, "location": "Nazca, Peru", "status": "CONTESTED", "description": "Infant mummy (Wawita = baby in Quechua). Three fingers and feet, cranial volume 19% larger than human infant of same size. Age: 6-8 months. Studied by University of San Luis Gonzaga Ica. Russian radiologists confirmed authentic bone structure. Peru government: fabricated doll."},
        {"name": "Antonio", "lat": -14.8290, "lon": -74.9635, "location": "Nazca, Peru", "status": "CONTESTED", "description": "5.5-5.7ft tall, approximately 1,500 years old. Three fingers with extra joints. 28-32 teeth found discolored and worn. Amalgam dental fillings discovered inside mouth - impossible if pre-Columbian. Dr Zalce: aside from tridactylism, few differences from modern human."},
        {"name": "Montserrat", "lat": -14.8290, "lon": -74.9735, "location": "Nazca, Peru", "status": "CONTESTED", "description": "Female mummy, showed signs of major trauma. CT scans revealed internal trauma, blood clots, fractures. Studied alongside Maria by Dr Zalce team 2025."},
        {"name": "Victoria", "lat": -14.8290, "lon": -74.9835, "location": "Nazca, Peru", "status": "CONTESTED", "description": "Part of the University of Ica collection. Handed over to UNICA research team November 2019 alongside Maria, Wawita and Albert."},
        {"name": "Albert", "lat": -14.8290, "lon": -74.9935, "location": "Nazca, Peru", "status": "CONTESTED", "description": "Part of the University of Ica collection. Carbon dating suggests between 750-1800 years old. Studied by international team of specialists."},
        {"name": "Josefina / Luisa", "lat": -14.8190, "lon": -74.9435, "location": "Nazca, Peru", "status": "CONTESTED", "description": "Fifth body recovered by UNICA team early 2020, similar to Josefina. Part of ongoing study at San Luis Gonzaga National University of Ica."},
        {"name": "Mexico Congress Specimens", "lat": 19.4326, "lon": -99.1332, "location": "Mexico City, Mexico", "status": "CONTESTED - likely fake", "description": "Two mummified figures presented by Jaime Maussan to Mexican Congress September 2023. UNAM denied supporting authenticity claims. Peru forensic examiner Estrada: dolls made from human and animal bones with modern synthetic glue. However X-ray scans showed internal structures inconsistent with fabrication."},
        {"name": "DHL Airport Seizure", "lat": -12.0219, "lon": -77.1143, "location": "Lima, Peru", "status": "FAKE - confirmed", "description": "Two small mummies seized at Jorge Chavez International Airport in DHL packaging. Peru Institute of Forensic Legal Medicine examined them January 2023 and confirmed they were false - fabricated pieces designed to look alien. Dressed in traditional Peruvian outfits."},
        {"name": "Tridactyl Hands - Nazca", "lat": -14.7350, "lon": -75.1300, "location": "Nazca Region, Peru", "status": "CONTESTED", "description": "Giant three-fingered hands found in Nazca region. Carbon dated over 7,000 years old by two independent laboratories - predating known Andean civilizations. Distinct from the small mummies but related discovery."},
    ]
    mummies_json = json.dumps(alien_mummies)

    classic_cases = [
        {"name": "Roswell Crash", "lat": 33.3942, "lon": -105.0291, "date": "Jul 1947", "notes": "USAF initially announced recovery of flying disc. Retracted within 24hrs. Debris and alleged bodies recovered. Spawned modern UFO era."},
        {"name": "Rendlesham Forest", "lat": 52.0833, "lon": 1.4333, "date": "Dec 1980", "notes": "UK Bentwaters RAF base. Multiple USAF personnel witnessed landed craft for 3 nights. Deputy base commander Lt Col Halt recorded audio. Physical landing marks found. UK's most credible case."},
        {"name": "Nimitz Tic Tac", "lat": 32.5, "lon": -117.5, "date": "Nov 2004", "notes": "Cmdr David Fravor and wingman encountered white Tic Tac shaped craft off San Diego. No wings, no exhaust, matched F-18 maneuvers. Confirmed on multiple radar systems. Pentagon released video 2017."},
        {"name": "Phoenix Lights", "lat": 33.4484, "lon": -112.0740, "date": "Mar 1997", "notes": "Massive V-shaped craft witnessed by thousands across Arizona including governor Fife Symington. Mile-wide formation. Multiple videos. Governor later admitted it was not flares."},
        {"name": "Belgian UFO Wave", "lat": 50.5010, "lon": 4.4764, "date": "Nov 1989", "notes": "Series of sightings of large triangular craft over Belgium. Belgian Air Force scrambled F-16s which locked radar on target. Object performed impossible maneuvers. 13,500+ witnesses."},
        {"name": "O'Hare Airport Disc", "lat": 41.9742, "lon": -87.9073, "date": "Nov 2006", "notes": "United Airlines crew and ground staff saw metallic disc hovering under clouds at Gate C17. Punched hole through cloud cover when it departed. FAA initially denied then confirmed radar contact."},
        {"name": "Stephenville TX", "lat": 32.2207, "lon": -98.2025, "date": "Jan 2008", "notes": "Massive craft witnessed by 200+ including pilots and police. Estimated mile long. Tracked on MUFON radar data. Military initially denied jets were in area then admitted 10 F-16s were scrambled."},
        {"name": "Tehran UFO Incident", "lat": 35.6892, "lon": 51.3890, "date": "Sep 1976", "notes": "Iranian Air Force F-4 pilots scrambled to intercept unknown craft. Weapons systems malfunctioned when attempting to fire. Communications disrupted. Confirmed by US Defense Intelligence Agency documents."},
        {"name": "Levelland TX", "lat": 33.5873, "lon": -102.3779, "date": "Nov 1957", "notes": "15+ witnesses including police officers reported egg-shaped craft landing on roads. All nearby car engines stalled when craft was present. Multiple independent reports across 2 hours."},
        {"name": "Kecksburg Acorn", "lat": 40.1851, "lon": -79.4606, "date": "Dec 1965", "notes": "Acorn shaped object crashed in Pennsylvania woods. Military cordoned off area within hours. Witnesses reported object with hieroglyphic markings being loaded onto flatbed. NASA later admitted they had debris."},
        {"name": "Gimbal Video Location", "lat": 34.0, "lon": -76.0, "date": "Jan 2015", "notes": "USS Roosevelt F/A-18 pilots filmed rotating craft off East Coast. Pentagon confirmed authentic. Craft rotated against wind with no visible propulsion. One of three confirmed Navy UAP videos."},
        {"name": "Göbekli Tepe UAP Reports", "lat": 37.2231, "lon": 38.9225, "date": "Multiple", "notes": "Multiple modern UAP reports near world's oldest known temple complex (12,000 BC). Local shepherds and archaeologists have reported anomalous lights near excavation sites."},
        {"name": "Japan Airlines 1628", "lat": 64.0, "lon": -147.0, "date": "Nov 1986", "notes": "JAL cargo flight over Alaska tracked massive walnut-shaped craft for 50 minutes. Confirmed on FAA radar. Captain Kenju Terauchi reported craft was size of two aircraft carriers. FAA case file declassified."},
        {"name": "Shag Harbour", "lat": 43.4731, "lon": -65.7436, "date": "Oct 1967", "notes": "Multiple witnesses saw craft crash into Nova Scotia harbor. Canadian Coast Guard and RCMP investigated. Underwater search found no debris. Officially listed as UFO in Canadian government documents."},
        {"name": "RB-47 Encounter", "lat": 37.0, "lon": -96.0, "date": "Jul 1957", "notes": "USAF RB-47 reconnaissance aircraft tracked by UFO across 1000 miles over southern US. Both visual and electronic tracking confirmed. Multiple crew members witnessed object. Documented in USAF Project Blue Book."},
    ]
    classic_json = json.dumps(classic_cases)

    # Read Mapbox token
    _tok_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mapbox_token.txt')
    try:
        with open(_tok_path) as _tf:
            mapbox_token = _tf.read().strip()
        print(f"   Mapbox token: {mapbox_token[:16]}…")
    except FileNotFoundError:
        mapbox_token = ''
        print("   ⚠  mapbox_token.txt not found — globe will be disabled")

    built_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Weaving Spiders</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link  rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css"/>
<link  rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css"/>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
<link href="https://api.mapbox.com/mapbox-gl-js/v3.3.0/mapbox-gl.css" rel="stylesheet"/>
<script src="https://api.mapbox.com/mapbox-gl-js/v3.3.0/mapbox-gl.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ background:#040d14; color:#a0e8c8; font-family:'Rajdhani',sans-serif;
       height:100vh; display:flex; flex-direction:column; overflow:hidden; }}

/* ── header ─────────────────────────────────────────────── */
#header {{
  background:linear-gradient(180deg,#040d14 0%,rgba(4,13,20,.95) 100%);
  border-bottom:1px solid #0f4; padding:10px 20px;
  display:flex; align-items:center; justify-content:space-between;
  z-index:1000; flex-shrink:0;
}}
#header h1 {{ font-size:1.4rem; letter-spacing:.25em; color:#0f4;
              text-transform:uppercase; font-family:'Share Tech Mono',monospace; }}
#header h1 span {{ color:#fff; }}
#stats {{ font-size:.78rem; color:#5a9; letter-spacing:.1em;
          text-align:right; font-family:'Share Tech Mono',monospace; line-height:1.6; }}
#stats b {{ color:#0f4; }}

/* ── controls ────────────────────────────────────────────── */
#controls {{
  background:rgba(4,13,20,.97); border-bottom:1px solid #093;
  padding:8px 20px; display:flex; gap:16px; align-items:center;
  flex-wrap:wrap; flex-shrink:0; z-index:999;
}}
.filter-group {{ display:flex; align-items:center; gap:8px; }}
.filter-group label {{ font-size:.75rem; letter-spacing:.12em; color:#5a9; text-transform:uppercase; }}
select, input[type=text] {{
  background:#071a10; border:1px solid #0a3; color:#a0e8c8;
  padding:4px 10px; font-family:'Share Tech Mono',monospace; font-size:.8rem;
  border-radius:2px; outline:none; cursor:pointer;
}}
select:focus, input[type=text]:focus {{ border-color:#0f4; }}
#result-count {{ font-size:.75rem; color:#5a9; font-family:'Share Tech Mono',monospace; margin-left:auto; }}

/* ── map ─────────────────────────────────────────────────── */
#map {{ flex:1; }}

/* ── popups ──────────────────────────────────────────────── */
/* ── tap-to-read mobile hint ─────────────────────────────── */
#tap-hint {{
  display:none; position:absolute; bottom:70px; left:50%;
  transform:translateX(-50%); z-index:900; pointer-events:none;
  background:rgba(4,13,20,.88); border:1px solid #093;
  color:#5a9; font-family:'Share Tech Mono',monospace;
  font-size:.65rem; letter-spacing:.12em; padding:5px 12px;
  border-radius:2px; white-space:nowrap; opacity:.85;
  animation: fadeout 3.5s ease 3s forwards;
}}
@keyframes fadeout {{ to {{ opacity:0; }} }}
@keyframes pulse-ring {{
  0%   {{ transform:scale(1);   opacity:.9; }}
  70%  {{ transform:scale(1.6); opacity:.3; }}
  100% {{ transform:scale(2);   opacity:0;  }}
}}
@keyframes priority-glow {{
  0%, 100% {{ box-shadow:0 0 8px 3px rgba(255,255,255,.9),0 0 20px 8px rgba(255,255,255,.4); }}
  50%       {{ box-shadow:0 0 16px 6px rgba(255,255,255,1),0 0 35px 14px rgba(255,255,200,.6); }}
}}
@media (max-width:768px) {{ #tap-hint {{ display:block; }} }}

.leaflet-popup-content-wrapper {{
  background:#040d14; border:1px solid #0a3; border-radius:4px; color:#a0e8c8;
  font-family:'Rajdhani',sans-serif; box-shadow:0 0 20px rgba(0,255,68,.15);
}}
.leaflet-popup-tip {{ background:#040d14; }}
.leaflet-popup-content {{ margin:14px 18px; }}
.popup-source {{ font-size:.65rem; letter-spacing:.15em; text-transform:uppercase;
                 color:#0a3; font-family:'Share Tech Mono',monospace; margin-bottom:4px; }}
.popup-title  {{ font-size:1rem; font-weight:700; color:#0f4; margin-bottom:6px; line-height:1.3; }}
.popup-meta   {{ font-size:.78rem; color:#5a9; margin-bottom:8px; }}
.popup-summary {{ font-size:.82rem; color:#8cc; line-height:1.5; margin-bottom:8px; }}
.popup-link   {{ font-size:.75rem; color:#0a3; text-decoration:none; letter-spacing:.05em; }}
.popup-link:hover {{ color:#0f4; }}

/* ── custom layer panel ──────────────────────────────────── */
#layer-panel {{
  position:fixed; top:12px; right:12px; z-index:1000;
  width:210px; background:rgba(4,13,20,.97); border:1px solid #093;
  border-radius:3px; font-family:'Share Tech Mono',monospace;
  font-size:.72rem; display:flex; flex-direction:column;
  max-height:calc(100vh - 24px);
}}
#lp-header {{
  display:flex; align-items:center; justify-content:space-between;
  padding:7px 10px; border-bottom:1px solid #093; flex-shrink:0;
  cursor:default;
}}
#lp-title {{ color:#0f4; letter-spacing:.18em; text-transform:uppercase; font-size:.7rem; }}
#lp-collapse {{
  background:none; border:none; color:#5a9; cursor:pointer;
  font-size:11px; padding:0 2px; line-height:1;
  min-width:44px; min-height:44px; display:flex; align-items:center; justify-content:center;
}}
#lp-collapse:hover {{ color:#a0e8c8; }}
#lp-collapse-all {{
  width:100%; background:rgba(0,255,68,.07); border:none; border-bottom:1px solid #093;
  color:#5a9; cursor:pointer; font-family:'Share Tech Mono',monospace;
  font-size:.63rem; letter-spacing:.1em; padding:5px 10px; text-align:left;
  text-transform:uppercase; flex-shrink:0;
}}
#lp-collapse-all:hover {{ color:#a0e8c8; background:rgba(0,255,68,.12); }}
#lp-body {{
  overflow-y:auto; flex:1;
  -webkit-overflow-scrolling:touch;
}}
#lp-body:after {{
  content:''; display:block; position:sticky; bottom:0; left:0; right:0; height:20px;
  background:linear-gradient(transparent, rgba(4,13,20,.95));
  pointer-events:none;
}}
/* accordion group */
.lp-group {{ border-bottom:1px solid #052; }}
.lp-group-hdr {{
  display:flex; align-items:center; gap:6px; padding:6px 10px;
  cursor:pointer; color:#5a9; user-select:none;
  transition:color .15s, background .15s;
}}
.lp-group-hdr:hover {{ background:rgba(0,255,68,.06); color:#a0e8c8; }}
.lp-group-icon {{ font-size:12px; }}
.lp-group-name {{ flex:1; letter-spacing:.1em; font-size:.68rem; text-transform:uppercase; }}
.lp-chevron {{ font-size:10px; transition:transform .2s; color:#3a7; }}
.lp-group.open .lp-chevron {{ transform:rotate(180deg); }}
.lp-group-items {{ display:none; padding:3px 0 5px 0; background:rgba(0,255,68,.02); }}
.lp-group.open .lp-group-items {{ display:block; }}
/* individual layer row */
.lp-item {{
  display:flex; align-items:center; gap:7px;
  padding:4px 10px 4px 22px; cursor:pointer; color:#5a9;
  transition:color .12s;
}}
.lp-item:hover {{ color:#a0e8c8; }}
.lp-item input[type=checkbox] {{ accent-color:#0f4; cursor:pointer; flex-shrink:0; }}
.lp-dot {{
  width:8px; height:8px; border-radius:50%; flex-shrink:0;
}}
.lp-name {{ letter-spacing:.07em; }}
/* show button (when panel is collapsed) */
#lp-show {{
  position:fixed; top:12px; right:12px; z-index:1000; display:none;
  background:rgba(4,13,20,.95); border:1px solid #093; color:#5a9;
  font-family:'Share Tech Mono',monospace; font-size:.7rem;
  letter-spacing:.12em; padding:6px 10px; cursor:pointer;
  text-transform:uppercase; border-radius:3px;
}}
#lp-show:hover {{ color:#a0e8c8; border-color:#0a3; }}

/* ── cluster bubbles — override Leaflet defaults ─────────── */
.marker-cluster, .marker-cluster div,
.marker-cluster-small, .marker-cluster-medium, .marker-cluster-large {{
  background:transparent !important; box-shadow:none !important;
}}

/* ── legend (dynamic — shows only active layers) ─────────── */
#legend {{
  position:absolute; bottom:30px; left:10px; z-index:1000;
  background:rgba(4,13,20,.92); border:1px solid #093;
  padding:8px 12px; font-size:.72rem;
  font-family:'Share Tech Mono',monospace; border-radius:2px;
  display:none;
}}
.legend-item {{ display:flex; align-items:center; gap:7px; margin-bottom:4px; color:#5a9; }}
.legend-item:last-child {{ margin-bottom:0; }}

/* ── ley line labels ─────────────────────────────────────── */
.ley-label {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  pointer-events: none;
}}
.ley-label::before {{ display: none !important; }}

/* ── mode toggle button ──────────────────────────────────── */
#mode-toggle {{
  background: rgba(0,255,68,.08);
  border: 1px solid #0f4; color: #0f4;
  font-family: 'Share Tech Mono', monospace;
  font-size: .78rem; letter-spacing: .15em;
  padding: 6px 16px; cursor: pointer;
  text-transform: uppercase; white-space: nowrap;
  transition: background .2s, color .2s; flex-shrink:0;
  border-radius:2px;
}}
#mode-toggle:hover  {{ background: rgba(0,255,68,.22); color:#fff; }}
#mode-toggle.active {{ background: rgba(0,255,68,.3);  color:#fff; box-shadow:0 0 10px #0f430; }}

/* ── controls hamburger (mobile only) ───────────────────── */
#controls-toggle {{
  display:none;
  background: rgba(0,153,51,.1); border:1px solid #093; color:#5a9;
  font-family:'Share Tech Mono',monospace; font-size:.75rem;
  letter-spacing:.1em; padding:6px 14px; cursor:pointer;
  text-transform:uppercase; white-space:nowrap; border-radius:2px;
}}
#controls-toggle:hover {{ background:rgba(0,153,51,.25); color:#a0e8c8; }}

/* ── view wrapper: globe + map overlap ──────────────────── */
#view-wrapper {{ flex:1; position:relative; min-height:0; overflow:hidden; }}
#map {{
  position:absolute; top:0; left:0; width:100%; height:100%;
  transition: opacity .3s ease;
}}
/* Globe container — hidden until toggled; shown before Mapbox init
   so the canvas receives real pixel dimensions on first render. */
#globe-container {{
  position:absolute; top:0; left:0; width:100%; height:100%;
  display:none;
}}

/* ── Mapbox GL popup theming ─────────────────────────────── */
.mb-popup .mapboxgl-popup-content {{
  background:#040d14; border:1px solid #0a3; border-radius:4px;
  color:#a0e8c8; font-family:'Rajdhani',sans-serif;
  padding:10px 14px; box-shadow:0 0 20px rgba(0,255,68,.2);
  font-size:.88rem; line-height:1.5;
}}
.mb-popup .mapboxgl-popup-tip {{ border-top-color:#0a3 !important; border-bottom-color:#0a3 !important; }}
.mb-popup .mapboxgl-popup-close-button {{ color:#5a9; font-size:16px; }}
.mb-popup .mapboxgl-popup-close-button:hover {{ color:#0f4; background:none; }}

/* ── mobile responsive ───────────────────────────────────── */
@media (max-width:768px) {{
  #header {{
    padding:8px 12px; gap:8px; flex-wrap:wrap;
  }}
  #header h1 {{ font-size:1rem; letter-spacing:.1em; }}
  #stats {{
    font-size:.62rem; line-height:1.5; order:4;
    flex-basis:100%; border-top:1px solid #093; padding-top:6px; margin-top:2px;
  }}
  #controls {{ display:none; }}
  #controls.open {{ display:flex; flex-direction:column; align-items:flex-start; gap:10px; padding:10px 14px; }}
  #controls-toggle {{ display:inline-flex !important; }}
  #mode-toggle {{ font-size:.72rem; padding:6px 12px; }}
  #result-count {{ display:none; }}
  #legend {{ display:none; }}
  #built-at {{ display:none; }}
  /* Layer panel: fixed, scrollable on mobile */
  #layer-panel {{ width:185px; font-size:.68rem; max-height:70vh; top:8px; right:8px; }}
  #lp-show {{ min-width:44px; min-height:44px; top:8px; right:8px; }}
  /* Popups: larger text + wider box for mobile reading */
  .leaflet-popup-content-wrapper {{ min-width:270px !important; max-width:88vw !important; }}
  .leaflet-popup-content {{ margin:16px 18px !important; font-size:16px !important; }}
  .popup-source  {{ font-size:12px !important; }}
  .popup-title   {{ font-size:18px !important; }}
  .popup-meta    {{ font-size:16px !important; }}
  .popup-summary {{ font-size:16px !important; line-height:1.6 !important; }}
  .popup-link    {{ font-size:16px !important; }}
  /* Mapbox globe popup on mobile */
  .mb-popup .mapboxgl-popup-content {{
    min-width:240px !important; font-size:.95rem !important;
    padding:14px 16px !important;
  }}
}}
@media (min-width:769px) {{
  #controls-toggle {{ display:none !important; }}
}}

/* ── built-at watermark ──────────────────────────────────── */
#built-at {{
  position:absolute; bottom:8px; left:10px; z-index:1000;
  font-size:.6rem; color:#1a4; font-family:'Share Tech Mono',monospace; opacity:.6;
}}

/* ── about panel ─────────────────────────────────────────── */
#about-btn {{
  background: rgba(0,255,68,.06); border:1px solid #093; color:#5a9;
  font-family:'Share Tech Mono',monospace; font-size:.72rem;
  letter-spacing:.1em; padding:5px 12px; cursor:pointer;
  text-transform:uppercase; white-space:nowrap; border-radius:2px;
  transition: background .2s, color .2s;
}}
#about-btn:hover {{ background:rgba(0,255,68,.16); color:#a0e8c8; }}
#about-overlay {{
  display:none; position:fixed; inset:0; z-index:9000;
  background:rgba(0,0,0,.72); align-items:center; justify-content:center;
}}
#about-overlay.open {{ display:flex; }}
#about-modal {{
  background:#060f18; border:1px solid #0a3;
  border-radius:4px; max-width:640px; width:92%; max-height:85vh;
  overflow-y:auto; padding:28px 32px;
  font-family:'Rajdhani',sans-serif; color:#a0e8c8;
  box-shadow:0 0 40px rgba(0,255,68,.2);
}}
#about-modal h2 {{
  color:#0f4; font-family:'Share Tech Mono',monospace;
  font-size:1rem; letter-spacing:.22em; text-transform:uppercase;
  margin-bottom:20px; border-bottom:1px solid #093; padding-bottom:10px;
}}
#about-modal h3 {{
  color:#0f4; font-size:.82rem; letter-spacing:.15em;
  text-transform:uppercase; margin:18px 0 8px;
  font-family:'Share Tech Mono',monospace;
}}
#about-modal p, #about-modal li {{
  font-size:.9rem; color:#7aaf94; line-height:1.65; margin-bottom:6px;
}}
#about-modal ul {{ padding-left:18px; }}
#about-modal .stat {{ color:#0f4; font-weight:700; }}
#about-modal .hotspot {{ color:#ff8800; font-weight:700; }}
#about-close {{
  float:right; background:none; border:1px solid #0a3; color:#5a9;
  font-family:'Share Tech Mono',monospace; font-size:.72rem;
  padding:4px 12px; cursor:pointer; border-radius:2px;
  letter-spacing:.1em; text-transform:uppercase;
}}
#about-close:hover {{ color:#a0e8c8; border-color:#0f4; }}

/* ── search clear button ─────────────────────────────────── */
.search-wrap {{ position:relative; display:flex; align-items:center; }}
.search-wrap input {{ padding-right:24px; }}
#clear-search {{
  position:absolute; right:6px; background:none; border:none;
  color:#5a9; cursor:pointer; font-size:14px; line-height:1;
  padding:0; display:none;
}}
#clear-search:hover {{ color:#a0e8c8; }}

/* ── globe hint overlay ──────────────────────────────────── */
#globe-hint {{
  position:absolute; bottom:18px; left:50%; transform:translateX(-50%);
  z-index:500; display:none;
  color:#3a7; font-family:'Share Tech Mono',monospace; font-size:.72rem;
  letter-spacing:.12em; opacity:.7; pointer-events:none;
  text-shadow:0 0 8px #0f4;
}}
</style>
</head>
<body>

<div id="header">
  <h1>WEAVING <span>SPIDERS</span></h1>
  <button id="controls-toggle" aria-label="Toggle filters">☰&nbsp;FILTERS</button>
  <button id="about-btn">ℹ About</button>
  <button id="mode-toggle">🗺️&nbsp;2D MAP</button>
  <div id="stats">
    NUFORC <b>{nuforc_count:,}</b> &nbsp;|&nbsp;
    REDDIT <b>{reddit_count:,}</b> &nbsp;|&nbsp;
    ABDUCTIONS <b>{abduction_count:,}</b> &nbsp;|&nbsp;
    BASES <b>{len(military_bases):,}</b> &nbsp;|&nbsp;
    MISSING 411 <b>{len(missing_411):,}</b> &nbsp;|&nbsp;
    SCIENTISTS <b>{len(missing_scientists):,}</b> &nbsp;|&nbsp;
    NUCLEAR <b>{len(nuclear_sites):,}</b> &nbsp;|&nbsp;
    WINDOWS <b>{len(window_areas):,}</b> &nbsp;|&nbsp;
    LOCAL NEWS <b>{local_news_count:,}</b>
  </div>
</div>

<div id="controls">
  <div class="filter-group">
    <label>Source</label>
    <select id="filter-source">
      <option value="all">All Sources</option>
      <option value="NUFORC">NUFORC</option>
      <option value="Reddit">Reddit</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Year</label>
    <select id="filter-year">
      <option value="all">All Years</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Shape</label>
    <select id="filter-shape">
      <option value="all">All Shapes</option>
    </select>
  </div>
  <div class="filter-group">
    <label>Search</label>
    <div class="search-wrap">
      <input type="text" id="filter-search" placeholder="city, state, keyword…" style="width:180px;">
      <button id="clear-search" title="Clear search">✕</button>
    </div>
  </div>
  <span id="result-count"></span>
</div>

<div id="view-wrapper">
  <div id="globe-container">
    <div id="globe-hint">⬆ Switch to 2D for detailed exploration</div>
  </div>
  <div id="map"></div>
  <div id="tap-hint">👆 Tap any marker to read details</div>
  <div id="layer-panel">
    <div id="lp-header">
      <span id="lp-title">&#9632; Layers</span>
      <button id="lp-collapse" title="Collapse panel">&#9664;</button>
    </div>
    <button id="lp-collapse-all" title="Collapse all groups">&#9660; Collapse all</button>
    <div id="lp-body"></div>
  </div>
  <button id="lp-show" title="Show layers">&#9654; LAYERS</button>
</div>

<div id="legend"></div>

<div id="about-overlay">
  <div id="about-modal">
    <button id="about-close">✕ Close</button>
    <h2>Weaving Spiders</h2>

    <div style="text-align:center;margin:0 0 24px;">
      <pre style="
        display:inline-block; text-align:left;
        font-family:'Share Tech Mono',monospace; font-size:.58rem;
        line-height:1.35; color:#00cc44; opacity:.82;
        background:rgba(0,255,68,.04); border:1px solid #0a3;
        border-radius:3px; padding:14px 18px;
        white-space:pre; overflow-x:auto; max-width:100%;
      ">
 ╔══════════════════════════════════════════════╗
 ║  [PARACAS]──────────────────[NAZCA]          ║
 ║      |   \                   |               ║
 ║      |    \──[AMARNA?]       |               ║
 ║  [TIWANAKU]──[PUMA PUNKU]    |               ║
 ║      |           |       [CUSCO]             ║
 ║   [ARICA]    [33RD ║]    [COLCA VALLEY]      ║
 ║      |        PARALLEL   [CAJAMARCA]         ║
 ║      |           ║                           ║
 ║  [BUGA SPHERE]   ║   ← NO WELDS. NO SEAMS.  ║
 ║  [BETZ SPHERE]   ║   ← MOVES ON ITS OWN.    ║
 ║      |       [PACIFIC NW AQUIFER]            ║
 ║      └───────[FAIRCHILD AFB]                 ║
 ║                  |                           ║
 ║          [HANFORD NUCLEAR SITE]              ║
 ║                  |                           ║
 ║         IT'S ALL CONNECTED, MAN             ║
 ╚══════════════════════════════════════════════╝
      </pre>
      <div style="
        font-family:'Share Tech Mono',monospace;
        font-size:.72rem; color:#00ff44; letter-spacing:.18em;
        text-transform:uppercase; margin-top:8px;
        text-shadow:0 0 8px #00ff4466;
      ">Weaving Spiders Come Not Here</div>
    </div>

    <h3>Data Sources</h3>
    <ul>
      <li><b>NUFORC</b> — National UFO Reporting Center civilian hotline reports (bulk CSV)</li>
      <li><b>NUFORC Recent</b> — Live scrape of nuforc.org/webreports for current reports</li>
      <li><b>Reddit</b> — r/ufos and r/UFOs community sighting posts (JSON API)</li>
      <li><b>Curated reference layers</b> — Military bases, COG sites, USO locations, Missing 411 cases, Missing Scientists, 33rd Parallel sites, Nuclear sites, Cattle mutilation hotspots, UAP Window Areas, Ley Lines, Water &amp; Aquifer systems (manually researched)</li>
    </ul>

    <h3>Record Counts</h3>
    <ul>
      <li>UFO Sightings: <span class="stat">{nuforc_count:,} NUFORC + {reddit_count:,} Reddit</span></li>
      <li>Abduction Reports: <span class="stat">{abduction_count:,}</span></li>
      <li>Military Bases: <span class="stat">{len(military_bases):,}</span></li>
      <li>Missing 411 Cases: <span class="stat">{len(missing_411):,}</span></li>
      <li>Missing Scientists: <span class="stat">{len(missing_scientists):,}</span></li>
      <li>Water / Aquifer Sites: <span class="stat">{len(water_anomaly_sites):,}</span> (13 surface + 5 aquifer systems)</li>
    </ul>

    <h3>Key Findings</h3>
    <p><span class="hotspot">Pacific Northwest Hotspot Triangle</span><br>
    The densest UAP cluster in the dataset centers on eastern Washington and northern Idaho — directly above the Spokane Valley–Rathdrum Prairie Aquifer. Fairchild Air Force Base (heavy bomber/refueling hub) sits at the aquifer's western edge. The Hanford Nuclear Site is 130 miles south. Kenneth Arnold's first modern "flying saucer" sighting (June 24, 1947, over Mt. Rainier) and the Maury Island incident (June 21, 1947) both originate within 60 miles of this cluster. The correlation between the aquifer boundary, the military infrastructure, and the sighting density is the single most striking pattern in the dataset.</p>

    <p><span class="hotspot">New England Concentration</span><br>
    A secondary cluster appears across Massachusetts, Connecticut, and Rhode Island — consistent with decades of documented sightings in the Hudson Valley and Cape Cod corridors. The region contains high population density (increasing reporting rate), multiple military installations, and proximity to the Atlantic USO corridor.</p>

    <p><span class="hotspot">33rd Parallel Alignment</span><br>
    A disproportionate number of major UFO incidents, government facilities, ancient sacred sites, and anomalous phenomena cluster within a few degrees of 33° North latitude globally. Roswell (33.4°N), Area 51 (37°N but within the Southwest cluster), Phoenix Lights (33.4°N), Baghdad, and Damascus all sit on or near this line.</p>

    <h3>About</h3>
    <p>Built as an independent research visualization. All data is from public sources. This map is for educational and research purposes. Toggle layers to explore correlations between sighting density, infrastructure, and geography.</p>
    <p style="color:#3a7;font-size:.78rem;margin-top:16px">Last updated: {built_at}</p>

    <div style="text-align:center; margin: 20px 0;">
      <img src="charlie.gif"
           alt="Charlie Kelly Pepe Silvia conspiracy wall"
           style="width:320px; border:1px solid #0f4; opacity:0.9; border-radius:4px;">
      <p style="font-family:'Share Tech Mono',monospace; color:#0f4; font-size:0.8rem; margin-top:8px; letter-spacing:0.15em;">
        CHARLIE WAS RIGHT ALL ALONG
      </p>
    </div>
  </div>
</div>

<div id="built-at">Built {built_at}</div>

<script>
// ── Data ────────────────────────────────────────────────────
const ALL_SIGHTINGS    = {markers_json};
const ABDUCTION_REPORTS = {abduction_json};
const MILITARY_BASES   = {bases_json};
const COG_SITES        = {cog_json};
const USO_SITES        = {uso_json};
const MISSING_411        = {missing_json};
const REDDIT_MISSING     = {reddit_missing_json};
const MISSING_SCIENTISTS = {scientists_json};
const PARALLEL_33_SITES  = {p33_json};
const NUCLEAR_SITES      = {nuclear_json};
const CATTLE_SITES       = {cattle_json};
const WINDOW_AREAS       = {windows_json};
const LEY_LINES          = {leylines_json};
const WATER_ANOMALY_SITES = {water_json};
const LOCAL_NEWS          = {local_news_json};
const NUFORC_RECENT       = {nuforc_recent_json};
const SEISMIC_ACTIVITY    = {seismic_json};
const HUMANOID_ENCOUNTERS = {humanoid_json};
const ASRS_REPORTS        = {asrs_json};
const ASA_REPORTS         = {asa_json};
const POWER_SITES         = {power_json};
const ELONGATED_SKULLS    = {skulls_json};
const ANOMALOUS_SPHERES   = {spheres_json};
const ALIEN_MUMMIES       = {mummies_json};
const CLASSIC_CASES       = {classic_json};
const MAPBOX_TOKEN        = '{mapbox_token}';

// ── Map init ────────────────────────────────────────────────
const _isMobile = window.innerWidth < 768;
const map = L.map('map', {{
  center: [39.5, -98.35], zoom: _isMobile ? 3 : 4,
  zoomControl: true, attributionControl: false,
  maxBounds: [[-85, -220], [85, 220]],
  maxBoundsViscosity: 1.0,
  minZoom: 2,
}});

L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap &copy; CARTO', maxZoom: 19
}}).addTo(map);

// ── Year filter population ───────────────────────────────────
const yearSelect = document.getElementById('filter-year');
const years = [...new Set(ALL_SIGHTINGS.map(s => {{
  const m = (s.date || '').match(/\b(19|20)\d{{2}}\b/);
  return m ? m[0] : null;
}}).filter(Boolean))].sort((a,b) => b - a);
years.forEach(y => {{
  const opt = document.createElement('option');
  opt.value = y; opt.textContent = y;
  yearSelect.appendChild(opt);
}});

// ── Shape filter population ─────────────────────────────────
const shapes = [...new Set(ALL_SIGHTINGS.map(s => s.shape).filter(Boolean))].sort();
const shapeSelect = document.getElementById('filter-shape');
shapes.forEach(shape => {{
  if (shape && shape !== 'unknown') {{
    const opt = document.createElement('option');
    opt.value = shape; opt.textContent = shape;
    shapeSelect.appendChild(opt);
  }}
}});

// ── Emoji icon map ──────────────────────────────────────────
const SHAPE_EMOJI = {{
  light:'💡', circle:'🔵', triangle:'🔺', disk:'🛸', saucer:'🛸',
  fireball:'🔥', cylinder:'🛢️', sphere:'⚪', chevron:'✈️', diamond:'💎',
  cross:'✝️', rectangle:'⬜', formation:'🔷', other:'❓', unknown:'❓',
  changing:'🌀', cone:'🔺', cigar:'🛢️', egg:'⚪', teardrop:'💧',
  flash:'⚡', oval:'🔵',
}};

// Touch target wrapper: 44×44px transparent hit area (Apple HIG minimum),
// with the visual indicator centered inside.
function _touchWrap(innerHtml, visualSize) {{
  const pad = Math.max(0, Math.round((44 - visualSize) / 2));
  return `<div style="width:44px;height:44px;display:flex;align-items:center;
             justify-content:center;cursor:pointer;">${{innerHtml}}</div>`;
}}

function makeIcon(source, shape) {{
  const isNuforc = source === 'NUFORC' || source === 'NUFORC Recent';
  if (isNuforc) {{
    // NUFORC — tiny dim green dot (8px), 50% opacity, no emoji: background reference layer
    const dot = `<div style="width:8px;height:8px;border-radius:50%;
                   background:#00ff44;opacity:0.5;flex-shrink:0;"></div>`;
    return L.divIcon({{
      className: '',
      html: _touchWrap(dot, 8),
      iconSize: [44,44], iconAnchor: [22,22],
    }});
  }} else {{
    // Reddit / other — shape-based emoji on gold-glowing dark circle
    const emoji = SHAPE_EMOJI[(shape||'').toLowerCase()] || '🛸';
    return emojiIcon(emoji, '#ffaa00', 18);
  }}
}}

// ── Emoji icon helper — 44px touch target, 22px emoji on dark circle ─────────
function emojiIcon(emoji, color, size) {{
  size = size || 22;
  const box  = Math.max(32, size + 10);   // visual circle diameter
  const glow = `drop-shadow(0 0 5px ${{color}}) drop-shadow(0 0 10px ${{color}}55)`;
  const inner = `<div style="width:${{box}}px;height:${{box}}px;border-radius:50%;
    background:rgba(4,13,20,.75);border:1.5px solid ${{color}}66;
    display:flex;align-items:center;justify-content:center;
    filter:${{glow}};flex-shrink:0;">
    <span style="font-size:${{size}}px;line-height:1">${{emoji}}</span>
  </div>`;
  return L.divIcon({{
    className: '',
    html: _touchWrap(inner, box),
    iconSize: [44, 44], iconAnchor: [22, 22],
  }});
}}

// ── Branch colours for military ─────────────────────────────
const BRANCH_COLORS = {{
  Army:'#4caf50', Navy:'#2196f3', Marines:'#f44336',
  'Air Force':'#03a9f4', 'Space Force':'#9c27b0', Special:'#ff5722',
}};

function makeMilIcon(branch) {{
  const c = BRANCH_COLORS[branch] || '#ff4444';
  const inner = `<div style="width:32px;height:32px;border-radius:50%;
    background:rgba(4,13,20,.72);border:1.5px solid ${{c}}88;
    display:flex;align-items:center;justify-content:center;
    filter:drop-shadow(0 0 5px ${{c}});">
    <div style="width:0;height:0;border-left:9px solid transparent;
      border-right:9px solid transparent;border-bottom:16px solid ${{c}};"></div>
  </div>`;
  return L.divIcon({{
    className:'', html:_touchWrap(inner,32), iconSize:[44,44], iconAnchor:[22,22]
  }});
}}

function makeCogIcon() {{
  const inner = `<div style="width:32px;height:32px;border-radius:50%;
    background:rgba(4,13,20,.72);border:1.5px solid #ffe03388;
    display:flex;align-items:center;justify-content:center;
    filter:drop-shadow(0 0 5px #ffe033);">
    <div style="width:18px;height:18px;background:#ffe033;
      clip-path:polygon(50% 0%,61% 35%,98% 35%,68% 57%,79% 91%,50% 70%,21% 91%,32% 57%,2% 35%,39% 35%);"></div>
  </div>`;
  return L.divIcon({{
    className:'', html:_touchWrap(inner,32), iconSize:[44,44], iconAnchor:[22,22]
  }});
}}

// ── Cluster factory ─────────────────────────────────────────
function clusterGroup(color) {{
  return L.markerClusterGroup({{
    chunkedLoading: true,
    removeOutsideVisibleBounds: true,
    maxClusterRadius: 38,          // tighter clusters → expand sooner
    disableClusteringAtZoom: 10,   // individual markers at zoom 10+
    zoomToBoundsOnClick: true,     // click cluster → zoom in to expand
    iconCreateFunction(cluster) {{
      const n    = cluster.getChildCount();
      const size = n < 10 ? 34 : n < 50 ? 42 : n < 200 ? 50 : 58;
      const fs   = n < 10 ? 14 : n < 100 ? 13 : 11;
      return L.divIcon({{
        className:'',
        html:`<div style="
          width:${{size}}px;height:${{size}}px;border-radius:50%;
          background:${{color}}22;border:2.5px solid ${{color}};
          display:flex;align-items:center;justify-content:center;
          color:${{color}};font-family:'Share Tech Mono',monospace;
          font-size:${{fs}}px;font-weight:bold;letter-spacing:-.5px;
          box-shadow:0 0 12px ${{color}}66,inset 0 0 8px ${{color}}22;">
            ${{n}}
          </div>`,
        iconSize:[size,size], iconAnchor:[size/2,size/2]
      }});
    }}
  }});
}}

// ── Sightings layer — viewport lazy-loading ─────────────────
const markerLayer = clusterGroup('#00ff44');
// markerLayer starts OFF — user enables via layer panel

let addedIdx = new Set();
let activeFilters = {{ src:'all', year:'all', shape:'all', search:'' }};

function matches(s) {{
  if (activeFilters.src !== 'all' && !s.source.includes(activeFilters.src)) return false;
  if (activeFilters.shape !== 'all' && s.shape !== activeFilters.shape) return false;
  if (activeFilters.year !== 'all') {{
    const m = (s.date || '').match(/\b(19|20)\d{{2}}\b/);
    if (!m || m[0] !== activeFilters.year) return false;
  }}
  if (activeFilters.search) {{
    const hay = `${{s.location}} ${{s.summary}} ${{s.shape}}`.toLowerCase();
    if (!hay.includes(activeFilters.search)) return false;
  }}
  return true;
}}

// ── Duration formatter ───────────────────────────────────────
function fmtDuration(secs) {{
  const n = parseInt(secs);
  if (!secs || isNaN(n) || n <= 0) return '';
  if (n < 60)   return `${{n}}s`;
  if (n < 3600) return `${{Math.round(n/60)}}m`;
  return `${{(n/3600).toFixed(1)}}h`;
}}

function loadVisible() {{
  const bounds = map.getBounds().pad(0.4);
  const batch  = [];
  ALL_SIGHTINGS.forEach((s, i) => {{
    if (addedIdx.has(i) || !bounds.contains([s.lat, s.lon]) || !matches(s)) return;
    addedIdx.add(i);
    const m = L.marker([s.lat, s.lon], {{icon: makeIcon(s.source, s.shape)}});
    const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ View post</a>` : '';
    const durStr   = fmtDuration(s.duration);
    const metaExtra = durStr ? ` &nbsp;·&nbsp; ⏱ ${{durStr}}` : '';
    m.bindPopup(`
      <div class="popup-source" style="color:${{(s.source==='NUFORC'||s.source==='NUFORC Recent')?'#00ff44':'#ffaa00'}}">${{s.source}}</div>
      <div class="popup-title">${{s.location || 'Unknown Location'}}</div>
      <div class="popup-meta">📅 ${{s.date}} &nbsp;·&nbsp; 🔷 ${{s.shape || 'unknown'}}${{metaExtra}}</div>
      <div class="popup-summary">${{s.summary}}</div>
      ${{linkHtml}}
    `, {{maxWidth:290}});
    batch.push(m);
  }});
  if (batch.length) markerLayer.addLayers(batch);
  const total   = ALL_SIGHTINGS.filter(matches).length;
  const visible = markerLayer.getLayers().length;
  document.getElementById('result-count').textContent =
    `Showing ${{visible.toLocaleString()}} / ${{total.toLocaleString()}} sightings`;
}}

function renderMarkers() {{
  markerLayer.clearLayers();
  addedIdx.clear();
  const searchVal = document.getElementById('filter-search').value.toLowerCase().trim();
  document.getElementById('clear-search').style.display = searchVal ? 'block' : 'none';
  activeFilters = {{
    src:   document.getElementById('filter-source').value,
    year:  document.getElementById('filter-year').value,
    shape: document.getElementById('filter-shape').value,
    search: searchVal,
  }};
  loadVisible();
}}

map.on('moveend zoomend', loadVisible);

// ── Military bases ──────────────────────────────────────────
const militaryLayer = clusterGroup('#ff4444');
MILITARY_BASES.forEach(b => {{
  const c = BRANCH_COLORS[b.branch] || '#ff4444';
  const m = L.marker([b.lat, b.lon], {{icon: makeMilIcon(b.branch)}});
  m.bindPopup(`
    <div class="popup-source" style="color:${{c}}">&#9650; ${{b.branch}}</div>
    <div class="popup-title"  style="color:${{c}}">${{b.name}}</div>
    <div class="popup-meta">${{b.state}}</div>
  `, {{maxWidth:220}});
  militaryLayer.addLayer(m);
}});

// ── COG sites ───────────────────────────────────────────────
const cogLayer = clusterGroup('#ffe033');
COG_SITES.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: makeCogIcon()}});
  m.bindPopup(`
    <div class="popup-source" style="color:#ffe033;">&#9733; CONTINUITY OF GOVERNMENT</div>
    <div class="popup-title"  style="color:#ffe033;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#cc9;">${{site.location}}</div>
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth:320}});
  cogLayer.addLayer(m);
}});

// ── USO sites ───────────────────────────────────────────────
const usoLayer = clusterGroup('#00bfff');
USO_SITES.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('🌊','#00bfff',22)}});
  m.bindPopup(`
    <div class="popup-source" style="color:#00bfff;">🌊 UNIDENTIFIED SUBMERGED OBJECT</div>
    <div class="popup-title"  style="color:#00bfff;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#7ce;">${{site.location}}</div>
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth:320}});
  usoLayer.addLayer(m);
}});

// ── Abduction reports ───────────────────────────────────────
const abductionLayer = clusterGroup('#cc44ff');
ABDUCTION_REPORTS.forEach(s => {{
  const isNuforc = s.source === 'NUFORC Abduction';
  const emoji = isNuforc ? '👤' : '👽';
  const color = isNuforc ? '#ff44aa' : '#cc44ff';
  const m = L.marker([s.lat, s.lon], {{icon: emojiIcon(emoji, color, 18)}});
  const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ View post</a>` : '';
  m.bindPopup(`
    <div class="popup-source" style="color:${{color}}">${{emoji}} ${{s.source}}</div>
    <div class="popup-title"  style="color:${{color}}">${{s.location || 'Unknown Location'}}</div>
    <div class="popup-meta">📅 ${{s.date}}</div>
    <div class="popup-summary">${{s.summary}}</div>
    ${{linkHtml}}
  `, {{maxWidth:300}});
  abductionLayer.addLayer(m);
}});

// ── Missing 411 layer ───────────────────────────────────────
const missing411Layer = clusterGroup('#cc0044');
MISSING_411.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('🔴','#cc0044',20)}});
  const linkHtml = site.url
    ? `<a href="${{site.url}}" target="_blank" class="popup-link">→ Full case details</a>`
    : '';
  m.bindPopup(`
    <div class="popup-source" style="color:#ff3366;">🔴 MISSING 411</div>
    <div class="popup-title"  style="color:#ff3366;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#c88;">${{site.location}}</div>
    <div class="popup-summary" style="color:#daa;">Unexplained wilderness disappearance documented by researcher David Paulides. Source: vanished.us</div>
    ${{linkHtml}}
  `, {{maxWidth:300}});
  missing411Layer.addLayer(m);
}});

// ── Reddit Missing Reports layer ─────────────────────────────
const redditMissingLayer = clusterGroup('#8b0000');
REDDIT_MISSING.forEach(s => {{
  const m = L.marker([s.lat, s.lon], {{icon: emojiIcon('🔍','#8b0000',18)}});
  const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ View post</a>` : '';
  m.bindPopup(`
    <div class="popup-source" style="color:#cc2200;">🔍 REDDIT · r/Missing411</div>
    <div class="popup-title"  style="color:#cc2200;">${{s.location_label || s.location || 'Unknown Location'}}</div>
    <div class="popup-meta">📅 ${{s.date}}</div>
    <div class="popup-summary">${{s.summary}}</div>
    ${{linkHtml}}
  `, {{maxWidth:300}});
  redditMissingLayer.addLayer(m);
}});

// ── 33rd Parallel layer ─────────────────────────────────────
const parallel33Layer = L.layerGroup();

L.polyline([[33.0, -200], [33.0, 200]], {{
  color: '#ff2222', weight: 2, dashArray: '10,7', opacity: 0.75
}}).addTo(parallel33Layer);

L.marker([33.0, -148], {{icon: L.divIcon({{
  className: '',
  html: '<div style="color:#ff4444;font-family:Share Tech Mono,monospace;font-size:10px;white-space:nowrap;text-shadow:0 0 8px #ff0000;letter-spacing:.1em;">— 33° PARALLEL —</div>',
  iconSize: [130, 16], iconAnchor: [65, 8]
}})}}).addTo(parallel33Layer);

PARALLEL_33_SITES.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: L.divIcon({{
    className: '',
    html: '<div style="font-size:15px;line-height:1;filter:drop-shadow(0 0 5px #ff2222);">🔺</div>',
    iconSize: [18,18], iconAnchor: [9,9]
  }})}});
  m.bindPopup(`
    <div class="popup-source" style="color:#ff4444;">🔺 33RD PARALLEL SITE</div>
    <div class="popup-title"  style="color:#ff4444;">${{site.name}}</div>
    <div class="popup-summary">${{site.note}}</div>
  `, {{maxWidth:300}});
  parallel33Layer.addLayer(m);
}});

// ── Nuclear Sites layer ─────────────────────────────────────
const nuclearLayer = clusterGroup('#00ff99');
NUCLEAR_SITES.forEach(site => {{
  const typeColor = site.type === 'Incident' ? '#ff4400'
    : site.type === 'Testing' ? '#ffaa00' : '#00ff99';
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('⚛️', typeColor, 20)}});
  m.bindPopup(`
    <div class="popup-source" style="color:${{typeColor}};">⚛️ NUCLEAR — ${{site.type.toUpperCase()}}</div>
    <div class="popup-title"  style="color:${{typeColor}};">${{site.name}}</div>
    <div class="popup-meta"   style="color:#8cc;">📍 ${{site.location}}</div>
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth:320}});
  nuclearLayer.addLayer(m);
}});

// ── Cattle Mutilation layer ──────────────────────────────────
const cattleLayer = clusterGroup('#cc6600');
CATTLE_SITES.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('🐄','#cc6600',20)}});
  m.bindPopup(`
    <div class="popup-source" style="color:#cc6600;">🐄 CATTLE MUTILATION HOTSPOT</div>
    <div class="popup-title"  style="color:#cc6600;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#a85;">📍 ${{site.location}}</div>
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth:320}});
  cattleLayer.addLayer(m);
}});

// ── Window Areas layer ───────────────────────────────────────
const windowLayer = clusterGroup('#aa44ff');
WINDOW_AREAS.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('👁️','#aa44ff',20)}});
  m.bindPopup(`
    <div class="popup-source" style="color:#aa44ff;">👁️ WINDOW AREA — MULTI-PHENOMENON</div>
    <div class="popup-title"  style="color:#aa44ff;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#99a;">📍 ${{site.location}}</div>
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth:340}});
  windowLayer.addLayer(m);
}});

// ── Ley Lines layer ──────────────────────────────────────────
const leyLineLayer = L.layerGroup();

LEY_LINES.forEach(line => {{
  // ── main polyline ────────────────────────────────────────
  const poly = L.polyline(line.points, {{
    color:     line.color,
    weight:    2.5,
    dashArray: '10,6',
    opacity:   0.75,
  }});
  poly.bindPopup(`
    <div class="popup-source" style="color:${{line.color}};">✦ LEY LINE</div>
    <div class="popup-title"  style="color:${{line.color}};">${{line.name}}</div>
    <div class="popup-summary">${{line.description}}</div>
  `, {{maxWidth:340}});
  poly.addTo(leyLineLayer);

  // ── glow layer (wider, lower opacity) ───────────────────
  L.polyline(line.points, {{
    color:     line.color,
    weight:    6,
    dashArray: '10,6',
    opacity:   0.18,
    interactive: false,
  }}).addTo(leyLineLayer);

  // ── inline label at label_at position ───────────────────
  if (line.label_at) {{
    const labelEl = `<div style="
      color:${{line.color}};
      font-family:'Share Tech Mono',monospace;
      font-size:9px;
      letter-spacing:.14em;
      white-space:nowrap;
      text-shadow:0 0 6px ${{line.color}},0 0 12px ${{line.color}};
      background:rgba(4,13,20,.6);
      padding:1px 5px;
      border-left:2px solid ${{line.color}};
      pointer-events:none;
    ">${{line.short || line.name}}</div>`;

    L.marker(line.label_at, {{
      icon: L.divIcon({{
        className: 'ley-label',
        html: labelEl,
        iconSize:   [160, 16],
        iconAnchor: [0, 8],
      }}),
      interactive: false,
      zIndexOffset: -1000,
    }}).addTo(leyLineLayer);
  }}

  // ── waypoint markers ─────────────────────────────────────
  (line.waypoints || []).forEach(wp => {{
    const m = L.marker([wp.lat, wp.lon], {{
      icon: L.divIcon({{
        className: '',
        html: `<div style="
          width:9px;height:9px;border-radius:50%;
          background:${{line.color}};
          border:1.5px solid #fff2;
          box-shadow:0 0 6px ${{line.color}},0 0 12px ${{line.color}}44;
        "></div>`,
        iconSize:   [9, 9],
        iconAnchor: [4.5, 4.5],
      }}),
    }});
    m.bindPopup(`
      <div class="popup-source" style="color:${{line.color}};">✦ ${{line.name}}</div>
      <div class="popup-title"  style="color:${{line.color}};">${{wp.name}}</div>
      <div class="popup-summary">${{wp.note}}</div>
    `, {{maxWidth:320}});
    leyLineLayer.addLayer(m);
  }});
}});

// ── Missing Scientists layer ────────────────────────────────
const scientistsLayer = clusterGroup('#ffffff');
MISSING_SCIENTISTS.forEach(s => {{
  const statusColor = s.status.toLowerCase().startsWith('murder') ? '#ff2222'
    : s.status.toLowerCase().startsWith('dead') ? '#ff6600'
    : '#ffffff';
  const m = L.marker([s.lat, s.lon], {{icon: emojiIcon('☢️','#ffffff',20)}});
  m.bindPopup(`
    <div class="popup-source" style="color:#fff;letter-spacing:.15em;">☢️ MISSING SCIENTIST</div>
    <div class="popup-title"  style="color:#fff;">${{s.name}}</div>
    <div class="popup-meta"   style="color:#aaa;">📅 ${{s.date}} &nbsp;·&nbsp; 📍 ${{s.location}}</div>
    <div class="popup-meta"   style="color:#8cf;margin-bottom:6px;">🏛 ${{s.affiliation}}</div>
    <div class="popup-meta"   style="color:${{statusColor}};font-weight:700;margin-bottom:8px;">⚠️ ${{s.status}}</div>
    <div class="popup-summary" style="color:#ccc;">${{s.notes}}</div>
  `, {{maxWidth:320}});
  scientistsLayer.addLayer(m);
}});

// ── Water & Aquifer layer ────────────────────────────────────
const waterLayer = clusterGroup('#00cfff');
WATER_ANOMALY_SITES.forEach(site => {{
  const isAquifer = site.type === 'aquifer';
  const col       = isAquifer ? '#00aaff' : '#00eeff';
  const emoji     = isAquifer ? '🌊' : '💧';
  const glow      = isAquifer ? '#0088ff' : '#00cfff';
  // Spokane Valley gets extra glow — highlighted hotspot
  const isHotspot = site.name.includes('Spokane');
  const sz = isHotspot ? 24 : 20;
  const hotGlow = isHotspot ? `drop-shadow(0 0 10px #00cfff) drop-shadow(0 0 20px #00cfff88)` : '';
  const box = sz + 8;
  const m = L.marker([site.lat, site.lon], {{icon: L.divIcon({{
    className: '',
    html: `<div style="width:${{box}}px;height:${{box}}px;border-radius:50%;
             background:rgba(4,13,20,.68);border:1px solid ${{glow}}44;
             display:flex;align-items:center;justify-content:center;
             filter:drop-shadow(0 0 4px ${{glow}}) ${{hotGlow}};">
             <span style="font-size:${{sz}}px;line-height:1">${{emoji}}</span>
           </div>`,
    iconSize: [box, box], iconAnchor: [box/2, box/2],
  }})}});
  const typeLabel = isAquifer ? 'UNDERGROUND AQUIFER' : 'WATER ANOMALY SITE';
  const hotspotNote = isHotspot
    ? `<div class="popup-meta" style="color:#ff4;font-weight:700;">⚠️ SITS WITHIN PACIFIC NW UAP HOTSPOT TRIANGLE</div>`
    : '';
  m.bindPopup(`
    <div class="popup-source" style="color:${{col}};">${{emoji}} ${{typeLabel}}</div>
    <div class="popup-title"  style="color:${{col}};">${{site.name}}</div>
    <div class="popup-meta"   style="color:#7ce;">📍 ${{site.location}}</div>
    ${{hotspotNote}}
    <div class="popup-summary">${{site.description}}</div>
  `, {{maxWidth:340}});
  waterLayer.addLayer(m);
}});

// ── Power & Secrecy layer ────────────────────────────────────
const powerLayer = L.layerGroup();
POWER_SITES.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('🦉','#ffd700',22)}});
  m.bindPopup(`
    <div class="popup-source" style="color:#ffd700;">🦉 POWER &amp; SECRECY</div>
    <div class="popup-title"  style="color:#ffd700;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#cc9900;">📍 ${{site.location}} &nbsp;·&nbsp; ${{site.type}}</div>
    <div class="popup-summary">${{site.notes}}</div>
  `, {{maxWidth:340}});
  powerLayer.addLayer(m);
}});

// ── Elongated Skulls & Mummies ───────────────────────────────
const skullsLayer = clusterGroup('#c0a060');
ELONGATED_SKULLS.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('💀','#c0a060',20)}});
  m.bindPopup(`
    <div class="popup-source" style="color:#c0a060;">💀 ELONGATED SKULLS &amp; MUMMIES</div>
    <div class="popup-title"  style="color:#c0a060;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#a08050;">📍 ${{site.country}} &nbsp;·&nbsp; ${{site.status}}</div>
    <div class="popup-summary">${{site.notes}}</div>
  `, {{maxWidth:320}});
  skullsLayer.addLayer(m);
}});

// ── Anomalous Spheres ────────────────────────────────────────
const spheresLayer = clusterGroup('#aa66ff');
ANOMALOUS_SPHERES.forEach(site => {{
  const m = L.marker([site.lat, site.lon], {{icon: emojiIcon('🔮','#aa66ff',20)}});
  m.bindPopup(`
    <div class="popup-source" style="color:#aa66ff;">🔮 ANOMALOUS SPHERE</div>
    <div class="popup-title"  style="color:#aa66ff;">${{site.name}}</div>
    <div class="popup-meta"   style="color:#8844cc;">📍 ${{site.country}} &nbsp;·&nbsp; ${{site.status}}</div>
    <div class="popup-summary">${{site.notes}}</div>
  `, {{maxWidth:320}});
  spheresLayer.addLayer(m);
}});

// ── Alien Mummies ────────────────────────────────────────────
const mummiesLayer = clusterGroup('#9900ff');
ALIEN_MUMMIES.forEach(site => {{
  const st = (site.status || '').toUpperCase();
  const ringColor = st.startsWith('FAKE') ? '#ff2222'
                  : st.startsWith('VERIFIED') ? '#00ff44'
                  : '#ffaa00';   // CONTESTED = amber
  const box = 32;
  const glow = `drop-shadow(0 0 5px #9900ff) drop-shadow(0 0 10px #9900ff55)`;
  const inner = `<div style="width:${{box}}px;height:${{box}}px;border-radius:50%;
    background:rgba(4,13,20,.75);border:2px solid ${{ringColor}};
    display:flex;align-items:center;justify-content:center;
    filter:${{glow}};flex-shrink:0;">
    <span style="font-size:18px;line-height:1">👽</span>
  </div>`;
  const icon = L.divIcon({{
    className: '',
    html: _touchWrap(inner, box),
    iconSize: [44, 44], iconAnchor: [22, 22],
  }});
  const statusColor = st.startsWith('FAKE') ? '#ff4444'
                    : st.startsWith('VERIFIED') ? '#00ff44'
                    : '#ffaa00';
  const m = L.marker([site.lat, site.lon], {{icon}});
  m.bindPopup(`
    <div class="popup-source" style="color:#9900ff;">👽 ALIEN MUMMY — ${{site.location}}</div>
    <div class="popup-title"  style="color:#bb44ff;">${{site.name}}</div>
    <div class="popup-meta"   style="color:${{statusColor}};font-weight:700;">⬤ ${{site.status}}</div>
    <div class="popup-summary">${{site.description}}</div>
    <div style="color:#556;font-size:.72rem;margin-top:8px;border-top:1px solid #223;padding-top:6px;font-style:italic;">
      Status reflects current state of scientific debate. Investigation ongoing. Draw your own conclusions.
    </div>
  `, {{maxWidth:340}});
  mummiesLayer.addLayer(m);
}});

// ── Heatmap layers ───────────────────────────────────────────
// Must be declared before LAYER_REGISTRY so the const bindings exist.
const heatAllLayer = L.heatLayer(
  ALL_SIGHTINGS.map(s => [s.lat, s.lon, 0.5]),
  {{ radius:20, blur:14, maxZoom:10,
     gradient:{{ 0.2:'#003322', 0.45:'#00ff44', 0.7:'#ffff00', 0.9:'#ff8800', 1:'#ff2222' }} }}
);
const heatAbductionLayer = L.heatLayer(
  ABDUCTION_REPORTS.map(s => [s.lat, s.lon, 1.0]),
  {{ radius:35, blur:22, maxZoom:10, minOpacity:0.35,
     gradient:{{ 0.0:'#0d0020', 0.25:'#2d0060', 0.5:'#7700cc', 0.72:'#cc44ff', 0.88:'#ff99ff', 1:'#ffffff' }} }}
);

// ── Local News layer ─────────────────────────────────────────
const localNewsLayer = clusterGroup('#00ffcc');
LOCAL_NEWS.forEach(s => {{
  let icon;
  if (s.priority === 'high') {{
    // Pulsing white glow icon for breaking/priority reports
    const box = 38;
    icon = L.divIcon({{
      className: '',
      html: `<div style="position:relative;width:${{box}}px;height:${{box}}px;">
        <div style="position:absolute;inset:0;border-radius:50%;
          background:rgba(255,255,255,.15);border:2px solid #fff;
          animation:priority-glow 1.5s ease-in-out infinite;"></div>
        <div style="position:absolute;inset:0;border-radius:50%;
          border:2px solid rgba(255,255,255,.5);
          animation:pulse-ring 1.8s ease-out infinite;"></div>
        <div style="position:absolute;inset:0;display:flex;align-items:center;
          justify-content:center;font-size:20px;line-height:1">✈️</div>
      </div>`,
      iconSize: [44, 44], iconAnchor: [22, 22],
    }});
  }} else {{
    icon = emojiIcon('📡','#00ffcc',18);
  }}
  const m = L.marker([s.lat, s.lon], {{icon}});
  const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ Read article</a>` : '';
  const priorityBadge = s.priority === 'high'
    ? `<div style="color:#fff;font-weight:700;letter-spacing:.12em;margin-bottom:4px">⚡ BREAKING REPORT</div>` : '';
  m.bindPopup(`
    ${{priorityBadge}}
    <div class="popup-source" style="color:#00ffcc;">📡 LOCAL NEWS</div>
    <div class="popup-title"  style="color:#00ffcc;">${{s.location_label || s.location || 'Unknown Location'}}</div>
    <div class="popup-meta">📅 ${{s.date}} &nbsp;·&nbsp; 🗞️ ${{s.source_name || 'Local Report'}}</div>
    <div class="popup-summary">${{s.summary}}</div>
    ${{linkHtml}}
  `, {{maxWidth:320}});
  localNewsLayer.addLayer(m);
}});
// localNewsLayer NOT added to map here — added by layer panel when toggled ON

// ── ASRS Pilot Reports layer ─────────────────────────────────
const asrsLayer = clusterGroup('#00aaff');
ASRS_REPORTS.forEach(s => {{
  const m = L.marker([s.lat, s.lon], {{icon: emojiIcon('✈️','#00aaff',18)}});
  const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ Source / Reference</a>` : '';
  m.bindPopup(`
    <div class="popup-source" style="color:#00aaff;">✈️ PILOT UAP REPORT</div>
    <div class="popup-title"  style="color:#00aaff;">${{s.location_label || s.city || 'USA'}}</div>
    <div class="popup-meta">📅 ${{s.date}} &nbsp;·&nbsp; 🆔 ${{s.source_name || 'ASRS'}}</div>
    <div class="popup-summary">${{s.summary}}</div>
    ${{linkHtml}}
  `, {{maxWidth:320}});
  asrsLayer.addLayer(m);
}});

// ── ASA Reports layer ─────────────────────────────────────────
const asaLayer = clusterGroup('#00ffff');
ASA_REPORTS.forEach(s => {{
  let icon;
  if (s.priority === 'high') {{
    const box = 38;
    icon = L.divIcon({{
      className: '',
      html: `<div style="position:relative;width:${{box}}px;height:${{box}}px;">
        <div style="position:absolute;inset:0;border-radius:50%;
          background:rgba(255,255,255,.15);border:2px solid #fff;
          animation:priority-glow 1.5s ease-in-out infinite;"></div>
        <div style="position:absolute;inset:0;border-radius:50%;
          border:2px solid rgba(255,255,255,.5);
          animation:pulse-ring 1.8s ease-out infinite;"></div>
        <div style="position:absolute;inset:0;display:flex;align-items:center;
          justify-content:center;font-size:20px;line-height:1">✈️</div>
      </div>`,
      iconSize: [44, 44], iconAnchor: [22, 22],
    }});
  }} else {{
    icon = emojiIcon('🛩️','#00ffff',18);
  }}
  const m = L.marker([s.lat, s.lon], {{icon}});
  const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ View post</a>` : '';
  const priorityBadge = s.priority === 'high'
    ? `<div style="color:#fff;font-weight:700;letter-spacing:.12em;margin-bottom:4px">⚡ BREAKING REPORT</div>` : '';
  m.bindPopup(`
    ${{priorityBadge}}
    <div class="popup-source" style="color:#00ffff;">🛩️ AMERICANS FOR SAFE AEROSPACE</div>
    <div class="popup-title"  style="color:#00ffff;">${{s.location_label || s.city || 'Unknown Location'}}</div>
    <div class="popup-meta">📅 ${{s.date}} &nbsp;·&nbsp; 🔷 ${{s.shape || 'unknown'}}</div>
    <div class="popup-summary">${{s.summary}}</div>
    ${{linkHtml}}
  `, {{maxWidth:320}});
  asaLayer.addLayer(m);
}});

// ── Classic Cases layer ──────────────────��───────────────────
const classicLayer = L.layerGroup();
CLASSIC_CASES.forEach(c => {{
  const icon = L.divIcon({{
    className: '',
    html: `<div style="position:relative;width:38px;height:38px;">
      <div style="position:absolute;inset:0;border-radius:50%;
        border:2px solid #ffd700;background:rgba(255,215,0,.12);
        box-shadow:0 0 10px #ffd70066,0 0 20px #ffd70033;"></div>
      <div style="position:absolute;inset:0;display:flex;align-items:center;
        justify-content:center;font-size:18px;line-height:1">🔍</div>
    </div>`,
    iconSize: [44, 44], iconAnchor: [22, 22],
  }});
  const m = L.marker([c.lat, c.lon], {{icon}});
  m.bindPopup(`
    <div class="popup-source" style="color:#ffd700;">🔍 CLASSIC CASE</div>
    <div class="popup-title"  style="color:#ffd700;">${{c.name}}</div>
    <div class="popup-meta">📅 ${{c.date}}</div>
    <div class="popup-summary">${{c.notes}}</div>
  `, {{maxWidth:320}});
  classicLayer.addLayer(m);
}});

// ── NUFORC Recent layer ──────────────────────────────────────
const nuforcRecentLayer = clusterGroup('#00aaff');
NUFORC_RECENT.forEach(s => {{
  const emoji = SHAPE_EMOJI[(s.shape||'').toLowerCase()] || '🆕';
  const m = L.marker([s.lat, s.lon], {{icon: emojiIcon(emoji, '#00aaff', 18)}});
  m.bindPopup(`
    <div class="popup-source" style="color:#00aaff;">🆕 NUFORC RECENT</div>
    <div class="popup-title"  style="color:#00aaff;">${{s.location_label || s.city || 'Unknown'}}</div>
    <div class="popup-meta">📅 ${{s.date}} &nbsp;·&nbsp; 🔷 ${{s.shape || 'unknown'}}</div>
    <div class="popup-summary">${{s.summary}}</div>
  `, {{maxWidth:300}});
  nuforcRecentLayer.addLayer(m);
}});

// ── Seismic Activity layer ────────────────────────────────────
const seismicLayer = L.layerGroup();
SEISMIC_ACTIVITY.forEach(q => {{
  const mag = q.mag || 0;
  const sz  = mag >= 6 ? 28 : mag >= 4 ? 20 : 14;
  const col = mag >= 6 ? '#ff2200' : mag >= 4 ? '#ff6600' : '#ff9900';
  const pulse = mag >= 6
    ? `animation:pulse-ring 1.8s ease-out infinite;` : '';
  const icon = L.divIcon({{
    className: '',
    html: `<div style="width:${{sz}}px;height:${{sz}}px;border-radius:50%;
             background:${{col}}44;border:2px solid ${{col}};
             display:flex;align-items:center;justify-content:center;
             ${{pulse}}filter:drop-shadow(0 0 4px ${{col}});">
             <span style="font-size:${{Math.round(sz*0.55)}}px;line-height:1">🌋</span>
           </div>`,
    iconSize: [sz, sz], iconAnchor: [sz/2, sz/2],
  }});
  const m = L.marker([q.lat, q.lon], {{icon}});
  const linkHtml = q.url ? `<a href="${{q.url}}" target="_blank" class="popup-link">→ USGS event page</a>` : '';
  m.bindPopup(`
    <div class="popup-source" style="color:#ff6600;">🌋 SEISMIC ACTIVITY</div>
    <div class="popup-title"  style="color:#ff6600;">${{q.name}}</div>
    <div class="popup-meta"   style="color:#f84;">M${{q.mag}} &nbsp;·&nbsp; 📅 ${{q.date}}</div>
    ${{linkHtml}}
  `, {{maxWidth:280}});
  seismicLayer.addLayer(m);
}});

// ── Humanoid Encounters layer ─────────────────────────────────
const humanoidLayer = clusterGroup('#6600cc');
HUMANOID_ENCOUNTERS.forEach(s => {{
  const m = L.marker([s.lat, s.lon], {{icon: emojiIcon('🫥','#6600cc',18)}});
  const linkHtml = s.url ? `<a href="${{s.url}}" target="_blank" class="popup-link">→ View post</a>` : '';
  m.bindPopup(`
    <div class="popup-source" style="color:#9933ff;">🫥 HUMANOID ENCOUNTER — r/${{s.subreddit||''}}</div>
    <div class="popup-title"  style="color:#9933ff;">${{s.location_label || s.location || 'Unknown Location'}}</div>
    <div class="popup-meta">📅 ${{s.date}}</div>
    <div class="popup-summary">${{s.summary}}</div>
    ${{linkHtml}}
  `, {{maxWidth:300}});
  humanoidLayer.addLayer(m);
}});

// ── Custom layer panel ───────────────────────────────────────
// Replaces Leaflet's built-in control. Each group is collapsible;
// checkboxes call map.addLayer / removeLayer directly.
const LAYER_REGISTRY = {{
  'UFO Sightings':               markerLayer,
  'Abduction Reports':           abductionLayer,
  'Heat Map (All Sightings)':    heatAllLayer,
  'Heat Map (Abductions Only)':  heatAbductionLayer,
  'Military Bases':              militaryLayer,
  'COG Sites':                   cogLayer,
  'Nuclear Sites':               nuclearLayer,
  'USO Sites':                   usoLayer,
  'Missing Scientists':          scientistsLayer,
  'Missing 411':                 missing411Layer,
  'Reddit Missing Reports':      redditMissingLayer,
  'Power & Secrecy':             powerLayer,
  'Water & Aquifers':            waterLayer,
  'Cattle Mutilations':          cattleLayer,
  'Window Areas':                windowLayer,
  'Ley Lines':                   leyLineLayer,
  '33rd Parallel':               parallel33Layer,
  'Local News':                  localNewsLayer,
  'Classic Cases':               classicLayer,
  'NUFORC Recent':               nuforcRecentLayer,
  'Pilot Reports':        asrsLayer,
  'ASA Reports':                 asaLayer,
  'Seismic Activity':            seismicLayer,
  'Humanoid Encounters':         humanoidLayer,
  'Elongated Skulls':            skullsLayer,
  'Anomalous Spheres':           spheresLayer,
  'Alien Mummies':               mummiesLayer,
}};

const LAYER_GROUPS = [
  {{ icon:'🛸', name:'SIGHTINGS', open:true, items:[
    {{ name:'UFO Sightings',              color:'#00ff44', on:true  }},
    {{ name:'Heat Map (All Sightings)',   color:'#ff6600', on:false }},
    {{ name:'Abduction Reports',          color:'#ff44aa', on:false }},
    {{ name:'Heat Map (Abductions Only)', color:'#ff44aa', on:false }},
    {{ name:'NUFORC Recent',              color:'#00aaff', on:false }},
    {{ name:'Local News',                 color:'#00ffcc', on:false }},
    {{ name:'Classic Cases',              color:'#ffd700', on:false }},
  ]}},
  {{ icon:'✈️', name:'PILOT REPORTS', open:false, items:[
    {{ name:'Pilot Reports', color:'#00aaff', on:false }},
    {{ name:'ASA Reports',          color:'#00ffff', on:false }},
  ]}},
  {{ icon:'🏛️', name:'INFRASTRUCTURE', open:false, items:[
    {{ name:'Military Bases', color:'#ff4444', on:false }},
    {{ name:'COG Sites',      color:'#ffe033', on:false }},
    {{ name:'Nuclear Sites',  color:'#00ff99', on:false }},
    {{ name:'USO Sites',      color:'#00bfff', on:false }},
  ]}},
  {{ icon:'👤', name:'PEOPLE', open:false, items:[
    {{ name:'Missing Scientists',     color:'#ffffff', on:false }},
    {{ name:'Missing 411',            color:'#ff2255', on:false }},
    {{ name:'Reddit Missing Reports', color:'#8b0000', on:false }},
  ]}},
  {{ icon:'🦉', name:'POWER', open:false, items:[
    {{ name:'Power & Secrecy', color:'#ffd700', on:false }},
  ]}},
  {{ icon:'🌊', name:'ENVIRONMENT', open:false, items:[
    {{ name:'Seismic Activity',   color:'#ff6600', on:false }},
    {{ name:'Water & Aquifers',   color:'#00cfff', on:false }},
    {{ name:'Cattle Mutilations', color:'#cc6600', on:false }},
    {{ name:'Window Areas',       color:'#aa44ff', on:false }},
  ]}},
  {{ icon:'🔺', name:'PATTERNS', open:false, items:[
    {{ name:'Ley Lines',     color:'#ffaa00', on:false }},
    {{ name:'33rd Parallel', color:'#ff2222', on:false }},
  ]}},
  {{ icon:'🏺', name:'ANOMALOUS ARTIFACTS', open:false, items:[
    {{ name:'Humanoid Encounters', color:'#6600cc', on:false }},
    {{ name:'Elongated Skulls',    color:'#c0a060', on:false }},
    {{ name:'Anomalous Spheres',   color:'#aa66ff', on:false }},
    {{ name:'Alien Mummies',       color:'#9900ff', on:false }},
  ]}},
];

// ── Legend definitions (shown only when layer is active) ────
const LEGEND_DEFS = {{
  'UFO Sightings':      {{ ico:'<span style="font-size:12px">🛸💡🔵🔺</span>',          lbl:'UFO Sighting'       }},
  'Abduction Reports':  {{ ico:'<span style="font-size:12px">👤👽</span>',               lbl:'Abduction Report'   }},
  'Military Bases':     {{ ico:'<span style="color:#f44;font-size:13px">▲</span>',       lbl:'Military Base'      }},
  'COG Sites':          {{ ico:'<span style="color:#ffe033;font-size:13px">★</span>',    lbl:'COG Site'           }},
  'Nuclear Sites':      {{ ico:'<span style="font-size:12px">⚛️</span>',                 lbl:'Nuclear Site'       }},
  'USO Sites':          {{ ico:'<span style="font-size:12px">🌊</span>',                 lbl:'USO Site'           }},
  'Missing Scientists': {{ ico:'<span style="font-size:12px">☢️</span>',                 lbl:'Missing Scientist'  }},
  'Missing 411':            {{ ico:'<span style="font-size:12px">🔴</span>',  lbl:'Missing 411'            }},
  'Reddit Missing Reports': {{ ico:'<span style="font-size:12px">🔍</span>',  lbl:'Reddit Missing Report'  }},
  'Power & Secrecy':        {{ ico:'<span style="font-size:12px">🦉</span>',  lbl:'Power / Secrecy Site'   }},
  'Water & Aquifers':   {{ ico:'<span style="font-size:12px">💧🌊</span>',               lbl:'Water / Aquifer'    }},
  'Cattle Mutilations': {{ ico:'<span style="font-size:12px">🐄</span>',                 lbl:'Cattle Mutilation'  }},
  'Window Areas':       {{ ico:'<span style="font-size:12px">👁️</span>',                 lbl:'Window Area'        }},
  'Ley Lines':          {{ ico:'<span style="color:#ffaa00;font-size:10px">———</span>',  lbl:'Ley Line'           }},
  '33rd Parallel':               {{ ico:'<span style="color:#ff2222;font-size:10px">— —</span>',  lbl:'33rd Parallel'            }},
  'Heat Map (All Sightings)':    {{ ico:'<span style="font-size:12px">🔥</span>',                  lbl:'Heatmap — All Sightings'  }},
  'Heat Map (Abductions Only)':  {{ ico:'<span style="font-size:12px">🔥</span>',                  lbl:'Heatmap — Abductions'     }},
  'NUFORC Recent':               {{ ico:'<span style="font-size:12px">🆕</span>',                  lbl:'NUFORC Recent Report'     }},
  'Local News':                  {{ ico:'<span style="font-size:12px">📡</span>',                  lbl:'Local News Sighting'      }},
  'Classic Cases':               {{ ico:'<span style="color:#ffd700;font-size:12px">🔍</span>',    lbl:'Classic UAP Case'         }},
  'Pilot Reports':        {{ ico:'<span style="font-size:12px">✈️</span>',                  lbl:'Notable Pilot UAP Report' }},
  'ASA Reports':                 {{ ico:'<span style="font-size:12px">🛩️</span>',                  lbl:'ASA Report'               }},
  'Seismic Activity':            {{ ico:'<span style="font-size:12px">🌋</span>',                  lbl:'Earthquake (USGS)'        }},
  'Humanoid Encounters':         {{ ico:'<span style="font-size:12px">🫥</span>',                  lbl:'Humanoid Encounter'       }},
  'Elongated Skulls':            {{ ico:'<span style="font-size:12px">💀</span>',                  lbl:'Elongated Skull / Mummy'  }},
  'Anomalous Spheres':           {{ ico:'<span style="font-size:12px">🔮</span>',                  lbl:'Anomalous Sphere'         }},
  'Alien Mummies':               {{ ico:'<span style="font-size:12px">👽</span>',                  lbl:'Alien Mummy (Nazca)'      }},
}};

// ── Layer state ───────────────────────────────────────────────────────────────
// Declared before updateLegend/buildLayerPanel so both can reference it.
// Only names listed here are added to the map on startup.
const activeLayerNames = new Set(['UFO Sightings']);

// Sync map to initial activeLayerNames: add only layers that should start ON,
// leave all others off the map entirely (layer panel adds them when toggled).
// Runs after LAYER_REGISTRY is defined (see above) and after activeLayerNames.
setTimeout(() => {{
  Object.entries(LAYER_REGISTRY).forEach(([name, layer]) => {{
    if (activeLayerNames.has(name)) {{
      if (!map.hasLayer(layer)) map.addLayer(layer);
    }} else {{
      if (map.hasLayer(layer)) map.removeLayer(layer);
    }}
  }});
}}, 0);

function updateLegend() {{
  const leg = document.getElementById('legend');
  const order = LAYER_GROUPS.flatMap(g => g.items.map(i => i.name));
  const rows  = order
    .filter(n => activeLayerNames.has(n) && LEGEND_DEFS[n])
    .map(n => `<div class="legend-item">${{LEGEND_DEFS[n].ico}}&nbsp; ${{LEGEND_DEFS[n].lbl}}</div>`)
    .join('');
  leg.innerHTML = rows;
  leg.style.display = rows ? '' : 'none';
}}

(function buildLayerPanel() {{
  const body = document.getElementById('lp-body');
  LAYER_GROUPS.forEach(group => {{
    const groupEl = document.createElement('div');
    groupEl.className = 'lp-group' + (group.open ? ' open' : '');

    const hdr = document.createElement('div');
    hdr.className = 'lp-group-hdr';
    hdr.innerHTML = `<span class="lp-group-icon">${{group.icon}}</span>
      <span class="lp-group-name">${{group.name}}</span>
      <span class="lp-chevron">▾</span>`;
    hdr.addEventListener('click', () => groupEl.classList.toggle('open'));
    groupEl.appendChild(hdr);

    const items = document.createElement('div');
    items.className = 'lp-group-items';
    group.items.forEach(item => {{
      const lbl = document.createElement('label');
      lbl.className = 'lp-item';
      lbl.innerHTML = `
        <input type="checkbox" ${{item.on ? 'checked' : ''}} data-layer="${{item.name}}">
        <span class="lp-dot" style="background:${{item.color}};box-shadow:0 0 5px ${{item.color}}66;"></span>
        <span class="lp-name">${{item.name}}</span>`;
      lbl.querySelector('input').addEventListener('change', e => {{
        const layer = LAYER_REGISTRY[item.name];
        if (!layer) return;
        if (e.target.checked) {{
          map.addLayer(layer);
          activeLayerNames.add(item.name);
        }} else {{
          map.removeLayer(layer);
          activeLayerNames.delete(item.name);
        }}
        updateLegend();
        if (currentMode === 'globe') updateGlobe();
      }});
      items.appendChild(lbl);
    }});
    groupEl.appendChild(items);
    body.appendChild(groupEl);
  }});
}})();

// ── Panel collapse / expand ──────────────────────────────────
document.getElementById('lp-collapse').addEventListener('click', () => {{
  document.getElementById('layer-panel').style.display = 'none';
  document.getElementById('lp-show').style.display     = 'block';
}});
document.getElementById('lp-show').addEventListener('click', () => {{
  document.getElementById('layer-panel').style.display = '';
  document.getElementById('lp-show').style.display     = 'none';
}});
document.getElementById('lp-collapse-all').addEventListener('click', () => {{
  document.querySelectorAll('.lp-group').forEach(g => g.classList.remove('open'));
}});

// ── Filter events ───────────────────────────────────────────
document.getElementById('filter-source').addEventListener('change', renderMarkers);
document.getElementById('filter-year').addEventListener('change',   renderMarkers);
document.getElementById('filter-shape').addEventListener('change',  renderMarkers);
document.getElementById('filter-search').addEventListener('input',  renderMarkers);
document.getElementById('clear-search').addEventListener('click', () => {{
  document.getElementById('filter-search').value = '';
  renderMarkers();
  document.getElementById('filter-search').focus();
}});

updateLegend();
renderMarkers();

// ════════════════════════════════════════════════════════════
// GLOBE / FLAT MODE
// ════════════════════════════════════════════════════════════

const globeEl     = document.getElementById('globe-container');
const mapEl       = document.getElementById('map');
let   currentMode = 'flat';
let   mbMap       = null;
let   mbLoaded    = false;

// ── Mapbox layer config — per-layer paint for visual hierarchy ───────────────
// UFO Sightings handled separately as a clustered source (see initMapboxGlobe).
// Each remaining entry carries its own `paint` object; the loop uses it directly.
const MB_LAYERS = [
  // Abductions: vivid purple, medium size, bright stroke
  {{ id:'abductions', data:() => ABDUCTION_REPORTS,
     name:'Abduction Reports', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,2.5, 3,4.5, 7,9],
       'circle-color':             '#9900ff',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.5,
       'circle-stroke-color':      '#dd88ff',
       'circle-emissive-strength': 1,
     }}}},
  // NUFORC Recent: bright blue
  {{ id:'nuforc-recent', data:() => NUFORC_RECENT,
     name:'NUFORC Recent', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,3, 3,5, 7,10],
       'circle-color':             '#00aaff',
       'circle-opacity':           0.9,
       'circle-stroke-width':      1.5,
       'circle-stroke-color':      '#55ccff',
       'circle-emissive-strength': 1,
     }}}},
  // Local news: teal
  {{ id:'local-news', data:() => LOCAL_NEWS,
     name:'Local News', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,2.5, 3,4.5, 7,9],
       'circle-color':             '#00ffcc',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.2,
       'circle-stroke-color':      '#66ffee',
       'circle-emissive-strength': 1,
     }}}},
  // Military bases: large bright blue — high-importance infrastructure
  {{ id:'military', data:() => MILITARY_BASES,
     name:'Military Bases', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,5, 3,8, 7,14],
       'circle-color':             '#0077ff',
       'circle-opacity':           0.92,
       'circle-stroke-width':      2.5,
       'circle-stroke-color':      '#55aaff',
       'circle-emissive-strength': 1,
     }}}},
  // COG sites: large blood-red, thick ring
  {{ id:'cog', data:() => COG_SITES,
     name:'COG Sites', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,5, 3,8, 7,14],
       'circle-color':             '#ff1111',
       'circle-opacity':           0.92,
       'circle-stroke-width':      2.5,
       'circle-stroke-color':      '#ff6666',
       'circle-emissive-strength': 1,
     }}}},
  // Nuclear sites: large yellow, white stroke — hazard marker feel
  {{ id:'nuclear', data:() => NUCLEAR_SITES,
     name:'Nuclear Sites', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,5, 3,8, 7,14],
       'circle-color':             '#ffee00',
       'circle-opacity':           0.92,
       'circle-stroke-width':      2.5,
       'circle-stroke-color':      '#ffffff',
       'circle-emissive-strength': 1,
     }}}},
  // USO sites: cyan, medium-large
  {{ id:'uso', data:() => USO_SITES,
     name:'USO Sites', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,4, 3,6.5, 7,13],
       'circle-color':             '#00ddff',
       'circle-opacity':           0.9,
       'circle-stroke-width':      2,
       'circle-stroke-color':      '#88eeff',
       'circle-emissive-strength': 1,
     }}}},
  // Missing scientists: large white core + wide semi-transparent ring (simulates pulse)
  {{ id:'scientists', data:() => MISSING_SCIENTISTS,
     name:'Missing Scientists', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,6, 3,10, 7,18],
       'circle-color':             '#ffffff',
       'circle-opacity':           0.95,
       'circle-stroke-width':      5,
       'circle-stroke-color':      'rgba(255,255,255,0.3)',
       'circle-emissive-strength': 1,
     }}}},
  // Reddit Missing Reports: dark blood-red
  {{ id:'reddit-missing', data:() => REDDIT_MISSING,
     name:'Reddit Missing Reports', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,2.5, 3,4.5, 7,9],
       'circle-color':             '#8b0000',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.2,
       'circle-stroke-color':      '#cc2200',
       'circle-emissive-strength': 0.9,
     }}}},
  // Missing 411: crimson, medium
  {{ id:'missing411', data:() => MISSING_411,
     name:'Missing 411', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,2.5, 3,4.5, 7,9],
       'circle-color':             '#ff2244',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.2,
       'circle-stroke-color':      '#ff8888',
       'circle-emissive-strength': 1,
     }}}},
  // Cattle mutilations: warm brown
  {{ id:'cattle', data:() => CATTLE_SITES,
     name:'Cattle Mutilations', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,3, 3,5.5, 7,11],
       'circle-color':             '#cc6600',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.5,
       'circle-stroke-color':      '#ee9944',
       'circle-emissive-strength': 0.9,
     }}}},
  // Seismic activity: orange, magnitude-scaled radius
  {{ id:'seismic', data:() => SEISMIC_ACTIVITY,
     name:'Seismic Activity', paint:{{
       'circle-radius':            ['interpolate',['linear'],['get','mag'],
         2.5,4, 4,8, 6,16, 8,28],
       'circle-color':             ['interpolate',['linear'],['get','mag'],
         2.5,'#ff9900', 4,'#ff6600', 6,'#ff2200'],
       'circle-opacity':           0.75,
       'circle-stroke-width':      1.5,
       'circle-stroke-color':      '#ffcc00',
       'circle-emissive-strength': 1,
     }}}},
  // Humanoid encounters: deep purple
  {{ id:'humanoid', data:() => HUMANOID_ENCOUNTERS,
     name:'Humanoid Encounters', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,3, 3,5.5, 7,11],
       'circle-color':             '#6600cc',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.5,
       'circle-stroke-color':      '#9933ff',
       'circle-emissive-strength': 1,
     }}}},
  // Water anomalies: sky blue
  {{ id:'water', data:() => WATER_ANOMALY_SITES,
     name:'Water & Aquifers', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,3, 3,5.5, 7,11],
       'circle-color':             '#00bbff',
       'circle-opacity':           0.85,
       'circle-stroke-width':      1.5,
       'circle-stroke-color':      '#66ddff',
       'circle-emissive-strength': 0.9,
     }}}},
  // Window areas: burnt orange, medium-large
  {{ id:'windows', data:() => WINDOW_AREAS,
     name:'Window Areas', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,4, 3,7, 7,13],
       'circle-color':             '#ff9900',
       'circle-opacity':           0.9,
       'circle-stroke-width':      2,
       'circle-stroke-color':      '#ffcc66',
       'circle-emissive-strength': 1,
     }}}},
  // 33rd Parallel sites: red, medium
  {{ id:'p33pts', data:() => PARALLEL_33_SITES,
     name:'33rd Parallel', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,3, 3,5.5, 7,11],
       'circle-color':             '#ff2222',
       'circle-opacity':           0.88,
       'circle-stroke-width':      1.5,
       'circle-stroke-color':      '#ff8888',
       'circle-emissive-strength': 1,
     }}}},
  // Power & Secrecy: gold, prominent size
  {{ id:'power', data:() => POWER_SITES,
     name:'Power & Secrecy', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,5, 3,8, 7,14],
       'circle-color':             '#ffd700',
       'circle-opacity':           0.92,
       'circle-stroke-width':      2,
       'circle-stroke-color':      '#fff8c0',
       'circle-emissive-strength': 1,
     }}}},
  // Classic Cases: bright gold, larger to stand out
  {{ id:'classic', data:() => CLASSIC_CASES,
     name:'Classic Cases', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,5, 3,8, 7,15],
       'circle-color':             '#ffd700',
       'circle-opacity':           0.95,
       'circle-stroke-width':      2.5,
       'circle-stroke-color':      '#fff8c0',
       'circle-emissive-strength': 1,
     }}}},
  // Elongated skulls: warm bone-gold
  {{ id:'skulls', data:() => ELONGATED_SKULLS,
     name:'Elongated Skulls', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,3, 3,5.5, 7,11],
       'circle-color':             '#c0a060',
       'circle-opacity':           0.9,
       'circle-stroke-width':      1.5,
       'circle-stroke-color':      '#e8cc88',
       'circle-emissive-strength': 0.9,
     }}}},
  // Anomalous spheres: violet-purple
  {{ id:'spheres', data:() => ANOMALOUS_SPHERES,
     name:'Anomalous Spheres', paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,4, 3,7, 7,13],
       'circle-color':             '#aa66ff',
       'circle-opacity':           0.92,
       'circle-stroke-width':      2,
       'circle-stroke-color':      '#cc99ff',
       'circle-emissive-strength': 1,
     }}}},
  // Alien mummies: deep violet, stroke color keyed to status via match expression
  {{ id:'mummies', data:() => ALIEN_MUMMIES,
     name:'Alien Mummies',
     popupFn(props) {{
       const st = (props.status || '').toUpperCase();
       const sc = st.startsWith('FAKE') ? '#ff4444' : st.startsWith('VERIFIED') ? '#00ff44' : '#ffaa00';
       return `<div style="font-family:'Rajdhani',sans-serif;max-width:300px">
         <div style="font-weight:700;color:#bb44ff;font-size:1rem">${{props.name}}</div>
         ${{props.location ? `<div style="color:#7aaf94;font-size:.78rem">📍 ${{props.location}}</div>` : ''}}
         <div style="color:${{sc}};font-size:.78rem;font-weight:700;margin:4px 0">⬤ ${{props.status}}</div>
         <div style="color:#8cc;font-size:.82rem;margin-top:4px">${{props.summary}}</div>
         <div style="color:#445;font-size:.68rem;margin-top:8px;border-top:1px solid #223;padding-top:5px;font-style:italic">
           Status reflects current state of scientific debate. Investigation ongoing. Draw your own conclusions.
         </div></div>`;
     }},
     paint:{{
       'circle-radius':            ['interpolate',['linear'],['zoom'], 1,4, 3,7, 7,13],
       'circle-color':             '#9900ff',
       'circle-opacity':           0.92,
       'circle-stroke-width':      2.5,
       'circle-stroke-color':      ['match',['get','status'],
         'FAKE - confirmed','#ff2222',
         'VERIFIED REAL','#00ff44',
         '#ffaa00'],
       'circle-emissive-strength': 1,
     }}}},
];

function _toGeoJSON(items) {{
  return {{
    type: 'FeatureCollection',
    features: (items || []).filter(d => d.lat && (d.lon ?? d.lng)).map(d => ({{
      type: 'Feature',
      geometry: {{ type:'Point', coordinates:[+(d.lon ?? d.lng), +d.lat] }},
      properties: {{
        name:    d.name || d.location_label || d.location || '',
        date:    d.date    || '',
        summary: (d.summary || d.description || d.notes || '').slice(0, 200),
        source:  d.source  || '',
        shape:   d.shape   || '',
        status:  d.status  || '',
        location: d.location || '',
      }},
    }})),
  }};
}}

function _mbPopup(props, color) {{
  const dt   = props.date    ? `<div style="color:#5a9;font-size:.78rem">📅 ${{props.date}}${{props.shape ? ' · ' + props.shape : ''}}</div>` : '';
  const body = props.summary ? `<div style="color:#8cc;font-size:.82rem;margin-top:4px">${{props.summary.slice(0,160)}}</div>` : '';
  return `<div style="font-family:'Rajdhani',sans-serif;max-width:260px">
    <div style="font-weight:700;color:${{color}};font-size:1rem">${{props.name || 'Unknown'}}</div>
    ${{dt}}${{body}}</div>`;
}}

function syncGlobeLayers() {{
  if (!mbMap || !mbLoaded) return;
  // UFO Sightings cluster layers
  const sVis = activeLayerNames.has('UFO Sightings') ? 'visible' : 'none';
  ['lyr-sightings-clusters','lyr-sightings-count','lyr-sightings-pts'].forEach(lid => {{
    if (mbMap.getLayer(lid)) mbMap.setLayoutProperty(lid, 'visibility', sVis);
  }});
  // Circle layers
  MB_LAYERS.forEach(({{ id, name }}) => {{
    const vis = activeLayerNames.has(name) ? 'visible' : 'none';
    if (mbMap.getLayer('lyr-' + id)) mbMap.setLayoutProperty('lyr-' + id, 'visibility', vis);
  }});
  // Heatmaps
  if (mbMap.getLayer('lyr-heat-all'))
    mbMap.setLayoutProperty('lyr-heat-all', 'visibility',
      activeLayerNames.has('Heat Map (All Sightings)') ? 'visible' : 'none');
  if (mbMap.getLayer('lyr-heat-abduct'))
    mbMap.setLayoutProperty('lyr-heat-abduct', 'visibility',
      activeLayerNames.has('Heat Map (Abductions Only)') ? 'visible' : 'none');
  // Line layers
  [['lyr-p33-line','33rd Parallel'],['lyr-ley','Ley Lines']].forEach(([lid, lname]) => {{
    if (mbMap.getLayer(lid))
      mbMap.setLayoutProperty(lid, 'visibility', activeLayerNames.has(lname) ? 'visible' : 'none');
  }});
}}

function updateGlobe() {{ syncGlobeLayers(); }}

function initMapboxGlobe() {{
  console.log('[Globe] initMapboxGlobe — mbMap:', mbMap ? 'exists' : 'null',
              '| token:', MAPBOX_TOKEN ? MAPBOX_TOKEN.slice(0,12)+'...' : 'MISSING');
  if (mbMap) {{ mbMap.resize(); syncGlobeLayers(); return; }}
  if (!MAPBOX_TOKEN) {{
    globeEl.innerHTML = '<div style="color:#f55;font-family:monospace;padding:40px;text-align:center">Mapbox token missing — add mapbox_token.txt and rebuild.</div>';
    return;
  }}
  mapboxgl.accessToken = MAPBOX_TOKEN;
  mbMap = new mapboxgl.Map({{
    container: 'globe-container',
    style:      'mapbox://styles/mapbox/dark-v11',
    projection: 'globe',
    zoom:       _isMobile ? 2.5 : 1.5,
    center:     [-98.35, 39.5],
    antialias:  true,
  }});
  mbMap.addControl(new mapboxgl.NavigationControl({{ visualizePitch:false }}), 'bottom-right');

  mbMap.on('load', () => {{
    console.log('[Globe] ✅ map loaded — adding layers');
    mbLoaded = true;
    mbMap.setFog({{
      color:            'rgb(4,13,20)',
      'high-color':     'rgb(0,50,15)',
      'horizon-blend':  0.04,
      'star-intensity': 0.9,
      'space-color':    'rgb(2,6,12)',
    }});

    // ── Heatmap — all sightings (added first so circles render on top) ─────────
    mbMap.addSource('src-heat-all', {{ type:'geojson', data:_toGeoJSON(ALL_SIGHTINGS) }});
    mbMap.addLayer({{
      id:'lyr-heat-all', type:'heatmap', source:'src-heat-all',
      layout:{{ visibility: activeLayerNames.has('Heat Map (All Sightings)') ? 'visible' : 'none' }},
      paint:{{
        'heatmap-weight':     ['interpolate',['linear'],['zoom'], 0,0.4, 9,1.5],
        'heatmap-intensity':  ['interpolate',['linear'],['zoom'], 2,0.3, 6,0.8, 9,2],
        'heatmap-radius':     ['interpolate',['linear'],['zoom'], 2,4, 4,8, 6,15, 8,25],
        'heatmap-opacity':    ['interpolate',['linear'],['zoom'], 2,0.7, 9,0.55],
        'heatmap-color': [
          'interpolate', ['linear'], ['heatmap-density'],
          0,   'rgba(0,0,0,0)',
          0.2, '#0000ff',
          0.4, '#9900ff',
          0.6, '#ff0000',
          0.8, '#ff6600',
          1.0, '#ffffff',
        ],
      }},
    }});

    // ── Heatmap — abductions only ──────────────────────────────────────────────
    mbMap.addSource('src-heat-abduct', {{ type:'geojson', data:_toGeoJSON(ABDUCTION_REPORTS) }});
    mbMap.addLayer({{
      id:'lyr-heat-abduct', type:'heatmap', source:'src-heat-abduct',
      layout:{{ visibility: activeLayerNames.has('Heat Map (Abductions Only)') ? 'visible' : 'none' }},
      paint:{{
        'heatmap-weight':     ['interpolate',['linear'],['zoom'], 0,0.8, 9,2.5],
        'heatmap-intensity':  ['interpolate',['linear'],['zoom'], 0,0.8, 9,2.5],
        'heatmap-radius':     ['interpolate',['linear'],['zoom'], 0,18,  3,28, 9,45],
        'heatmap-opacity':    ['interpolate',['linear'],['zoom'], 2,0.88, 9,0.65],
        'heatmap-color': [
          'interpolate', ['linear'], ['heatmap-density'],
          0,   'rgba(0,0,0,0)',
          0.2, '#1a0040',
          0.4, '#4400aa',
          0.6, '#9900ff',
          0.8, '#dd66ff',
          1.0, '#ffffff',
        ],
      }},
    }});

    // ── UFO Sightings — clustered ──────────────────────────────────────────────
    const sVis = activeLayerNames.has('UFO Sightings') ? 'visible' : 'none';
    mbMap.addSource('src-sightings', {{
      type: 'geojson',
      data: _toGeoJSON(ALL_SIGHTINGS),
      cluster: true,
      clusterMaxZoom: 14,
      clusterRadius: 50,
    }});
    // Cluster bubble — maxzoom matches clusterMaxZoom so clusters show all the way to zoom 14
    mbMap.addLayer({{
      id:'lyr-sightings-clusters', type:'circle', source:'src-sightings',
      filter:['has','point_count'],
      maxzoom: 14,
      layout:{{ visibility:sVis }},
      paint:{{
        'circle-color':['step',['get','point_count'],
          '#003a1a', 10, '#005522', 50, '#007a33', 200, '#00aa44'],
        'circle-radius':['step',['get','point_count'],
          13, 10,18, 50,24, 200,30],
        'circle-opacity': 0.88,
        'circle-stroke-width': 1.5,
        'circle-stroke-color': '#00ff44',
        'circle-emissive-strength': 1,
      }},
    }});
    // Cluster count label; maxzoom matches cluster bubble
    mbMap.addLayer({{
      id:'lyr-sightings-count', type:'symbol', source:'src-sightings',
      filter:['has','point_count'],
      maxzoom: 14,
      layout:{{
        visibility: sVis,
        'text-field': '{{point_count_abbreviated}}',
        'text-font':  ['DIN Offc Pro Medium','Arial Unicode MS Bold'],
        'text-size':  11,
      }},
      paint:{{
        'text-color':       '#00ff44',
        'text-halo-color':  '#000000',
        'text-halo-width':  1.2,
      }},
    }});
    // Individual points — always visible across all zoom levels
    mbMap.addLayer({{
      id:'lyr-sightings-pts', type:'circle', source:'src-sightings',
      filter:['!',['has','point_count']],
      minzoom: 0,
      maxzoom: 24,
      layout:{{ visibility:sVis }},
      paint:{{
        'circle-radius': ['interpolate',['linear'],['zoom'], 0,3, 5,6, 8,10, 12,14, 16,18],
        'circle-color':  ['match',['get','source'],'NUFORC','#00ff44','#ffaa00'],
        'circle-opacity': 1.0,
        'circle-stroke-width': ['match',['get','source'],'NUFORC',0,1.2],
        'circle-stroke-color': '#ffaa00',
        'circle-emissive-strength': 1,
      }},
    }});
    mbMap.on('click','lyr-sightings-pts', e => {{
      // Bail if a cluster bubble is also at this point — let the cluster handler win
      if (mbMap.queryRenderedFeatures(e.point, {{ layers:['lyr-sightings-clusters'] }}).length) return;
      new mapboxgl.Popup({{ className:'mb-popup', maxWidth:'300px' }})
        .setLngLat(e.lngLat)
        .setHTML(_mbPopup(e.features[0].properties, '#00ff44'))
        .addTo(mbMap);
    }});
    mbMap.on('mouseenter','lyr-sightings-pts',  () => {{ mbMap.getCanvas().style.cursor='pointer'; }});
    mbMap.on('mouseleave','lyr-sightings-pts',  () => {{ mbMap.getCanvas().style.cursor=''; }});

    // Click cluster bubble → zoom in to expand
    mbMap.on('click', 'lyr-sightings-clusters', function(e) {{
      const features = mbMap.queryRenderedFeatures(e.point, {{ layers: ['lyr-sightings-clusters'] }});
      if (!features.length) return;
      const clusterId = features[0].properties.cluster_id;
      mbMap.getSource('src-sightings').getClusterExpansionZoom(clusterId, function(err, zoom) {{
        if (err) return;
        mbMap.easeTo({{
          center: features[0].geometry.coordinates,
          zoom: zoom + 1,
          duration: 500,
        }});
      }});
    }});
    // Click count label — symbol layer sits on top of bubble and swallows the click
    mbMap.on('click', 'lyr-sightings-count', function(e) {{
      const features = mbMap.queryRenderedFeatures(e.point, {{ layers: ['lyr-sightings-clusters'] }});
      if (!features.length) return;
      const clusterId = features[0].properties.cluster_id;
      mbMap.getSource('src-sightings').getClusterExpansionZoom(clusterId, function(err, zoom) {{
        if (err) return;
        mbMap.easeTo({{
          center: features[0].geometry.coordinates,
          zoom: zoom + 1,
          duration: 500,
        }});
      }});
    }});
    mbMap.on('mouseenter', 'lyr-sightings-clusters', function() {{ mbMap.getCanvas().style.cursor = 'pointer'; }});
    mbMap.on('mouseleave', 'lyr-sightings-clusters', function() {{ mbMap.getCanvas().style.cursor = ''; }});
    mbMap.on('mouseenter', 'lyr-sightings-count',    function() {{ mbMap.getCanvas().style.cursor = 'pointer'; }});
    mbMap.on('mouseleave', 'lyr-sightings-count',    function() {{ mbMap.getCanvas().style.cursor = ''; }});
    // Zoom diagnostics — fires when globe zoom ≥ 10
    mbMap.on('zoom', () => {{
      const z = mbMap.getZoom();
      if (z >= 10) console.log('[Globe] zoom:', z.toFixed(2),
        '| pts visibility:', mbMap.getLayoutProperty('lyr-sightings-pts','visibility'),
        '| pts features:', mbMap.queryRenderedFeatures({{layers:['lyr-sightings-pts']}}).length);
    }});

    // ── Circle layers ──────────────────────────────────────────────────────────
    MB_LAYERS.forEach(cfg => {{
      const fc  = _toGeoJSON(cfg.data());
      const vis = activeLayerNames.has(cfg.name) ? 'visible' : 'none';
      mbMap.addSource('src-' + cfg.id, {{ type:'geojson', data:fc }});
      mbMap.addLayer({{
        id:'lyr-' + cfg.id, type:'circle', source:'src-' + cfg.id,
        layout:{{ visibility:vis }},
        paint: cfg.paint,
      }});
      mbMap.on('click', 'lyr-' + cfg.id, e => {{
        const props = e.features[0].properties;
        const html  = cfg.popupFn ? cfg.popupFn(props) : _mbPopup(props, cfg.paint['circle-color']);
        new mapboxgl.Popup({{ className:'mb-popup', maxWidth:'320px' }})
          .setLngLat(e.lngLat)
          .setHTML(html)
          .addTo(mbMap);
      }});
      mbMap.on('mouseenter', 'lyr-' + cfg.id, () => {{ mbMap.getCanvas().style.cursor = 'pointer'; }});
      mbMap.on('mouseleave', 'lyr-' + cfg.id, () => {{ mbMap.getCanvas().style.cursor = ''; }});
    }});

    // ── 33rd Parallel line ─────────────────────────────────────────────────────
    mbMap.addSource('src-p33-line', {{
      type:'geojson',
      data:{{ type:'Feature', geometry:{{ type:'LineString', coordinates:[[-180,33],[180,33]] }} }},
    }});
    mbMap.addLayer({{
      id:'lyr-p33-line', type:'line', source:'src-p33-line',
      layout:{{ visibility: activeLayerNames.has('33rd Parallel') ? 'visible' : 'none' }},
      paint:{{ 'line-color':'#ff2222','line-width':1.5,'line-dasharray':[5,3],'line-opacity':0.8 }},
    }});

    // ── Ley lines ──────────────────────────────────────────────────────────────
    const leyFC = {{
      type:'FeatureCollection',
      features: LEY_LINES.map(l => ({{
        type:'Feature', properties:{{ color:l.color }},
        geometry:{{ type:'LineString', coordinates:l.points.map(([la,lo]) => [lo,la]) }},
      }})),
    }};
    mbMap.addSource('src-ley', {{ type:'geojson', data:leyFC }});
    mbMap.addLayer({{
      id:'lyr-ley', type:'line', source:'src-ley',
      layout:{{ visibility: activeLayerNames.has('Ley Lines') ? 'visible' : 'none' }},
      paint:{{ 'line-color':['get','color'],'line-width':1.5,'line-dasharray':[6,4],'line-opacity':0.75 }},
    }});

    syncGlobeLayers();
  }});
  mbMap.on('error', e => console.error('[Globe] ❌ Mapbox error:', e.error || e));
}}

// ── Mode switch ───────────────────────────────────────────
function setMode(mode) {{
  console.log('[Globe] setMode("' + mode + '") — was:', currentMode);
  currentMode = mode;
  const btn  = document.getElementById('mode-toggle');
  const hint = document.getElementById('globe-hint');
  const bar  = document.getElementById('controls');

  if (mode === 'globe') {{
    globeEl.style.display     = 'block';
    mapEl.style.opacity       = '0';
    mapEl.style.pointerEvents = 'none';
    btn.innerHTML             = '🌐&nbsp;GLOBE';
    btn.classList.add('active');
    hint.style.display        = 'block';
    bar.style.opacity         = '0.25';
    bar.style.pointerEvents   = 'none';
    console.log('[Globe] container display=block, queuing rAF for init');
    requestAnimationFrame(() => {{ console.log('[Globe] rAF fired → initMapboxGlobe'); initMapboxGlobe(); }});
  }} else {{
    globeEl.style.display     = 'none';
    mapEl.style.opacity       = '1';
    mapEl.style.pointerEvents = 'all';
    btn.innerHTML             = '🗺️&nbsp;2D MAP';
    btn.classList.remove('active');
    hint.style.display        = 'none';
    bar.style.opacity         = '';
    bar.style.pointerEvents   = '';
    setTimeout(() => {{
      map.invalidateSize({{ animate: false }});
      renderMarkers();
      loadVisible();
    }}, 350);
  }}
}}

document.getElementById('mode-toggle').addEventListener('click', () => {{
  console.log('[Globe] toggle clicked — currentMode:', currentMode);
  setMode(currentMode === 'globe' ? 'flat' : 'globe');
}});

// ── About panel ──────────────────────────────────────────────
document.getElementById('about-btn').addEventListener('click', () =>
  document.getElementById('about-overlay').classList.add('open'));
document.getElementById('about-close').addEventListener('click', () =>
  document.getElementById('about-overlay').classList.remove('open'));
document.getElementById('about-overlay').addEventListener('click', e => {{
  if (e.target === document.getElementById('about-overlay'))
    document.getElementById('about-overlay').classList.remove('open');
}});

// ── Mobile: hamburger to show/hide filter controls ────────
document.getElementById('controls-toggle').addEventListener('click', () => {{
  const bar = document.getElementById('controls');
  bar.classList.toggle('open');
}});

</script>
</body>
</html>"""

    with open(OUTPUT_MAP, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = os.path.getsize(OUTPUT_MAP) / 1024
    print(f"   ✅ Saved {OUTPUT_MAP}  ({size_kb:.0f} KB)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    data = load_export()

    # Separate any r/Missing411 Reddit posts that landed in sightings
    # (handles exports made before the split was added to fetch_data.py)
    raw_sightings  = data.get("sightings", [])
    reddit_missing = data.get("reddit_missing", [])
    if not reddit_missing:
        # Back-compat: pull Missing411 posts out of the sightings list
        reddit_missing = [s for s in raw_sightings if s.get("subreddit") == "Missing411"]
        raw_sightings  = [s for s in raw_sightings if s.get("subreddit") != "Missing411"]
        if reddit_missing:
            print(f"   ↳ Separated {len(reddit_missing)} r/Missing411 posts from sightings layer")

    build_map(
        sightings           = raw_sightings,
        abduction_sightings = data.get("abduction_reports", []),
        military_bases      = data.get("military_bases", []),
        cog_sites           = data.get("cog_sites", []),
        uso_sites           = data.get("uso_sites", []),
        missing_411              = data.get("missing_411", []),
        reddit_missing           = reddit_missing,
        missing_scientists       = _MISSING_SCIENTISTS_LIVE,
        parallel_33_sites        = data.get("parallel_33_sites", []),
        nuclear_sites            = data.get("nuclear_sites", []),
        cattle_mutilation_sites  = data.get("cattle_mutilation_sites", []),
        window_areas             = data.get("window_areas", []),
        ley_lines                = data.get("ley_lines", []),
        water_anomaly_sites      = data.get("water_anomaly_sites", []),
        local_news               = data.get("local_news", []),
        nuforc_recent            = data.get("nuforc_recent", []),
        seismic_activity         = data.get("seismic_activity", []),
        humanoid_encounters      = data.get("humanoid_encounters", []),
        asrs_reports             = data.get("asrs_reports", []),
        asa_reports              = data.get("asa_reports", []),
    )
    print(f"\n✅  Done — open {OUTPUT_MAP} in your browser.")
