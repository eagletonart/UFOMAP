"""
constants.py — single source of truth for all UFO map data.

Imported by both fetch_data.py and ufo_map_1.py.
Edit data here; both scripts pick up changes automatically.
"""

import os

# ── File paths ────────────────────────────────────────────────
NUFORC_CSV   = os.path.join(os.path.dirname(__file__), "nuforc_test.csv")
OUTPUT_MAP   = "ufo_map.html"
EXPORT_FILE  = "ufo_data_export.json"

NUFORC_FIELDS = [
    "datetime", "city", "state", "country", "shape",
    "duration_seconds", "duration_hm", "comments", "date_posted",
    "latitude", "longitude",
]

# ── Abduction keyword filter ──────────────────────────────────
ABDUCTION_KEYWORDS = [
    "abduct", "aboard", "taken aboard", "taken on board", "missing time",
    "lost time", "paralyz", "levitat", "floated up", "floated into",
    "beam of light", "pulled up", "examination table", "medical exam",
    "probed", "implant", "grey alien", "gray alien", "small beings",
    "taken inside", "inside the craft", "inside the object", "entities",
    "non-human", "humanoid", "took me", "they took", "i was taken",
]

# ── Missing 411 / Wilderness Disappearances ───────────────────
# Source: vanished.us (77 documented cases with coordinates)
MISSING_411_SITES = [
    {"name": "Alfred Nicholas Kochendorfer", "lat": 61.5304410, "lon": -148.9440694, "location": "Palmer, AK", "url": "https://vanished.us/alfred-nicholas-kochendorfer-vanished-from-butte"},
    {"name": "Allen Clarence Theis", "lat": 47.7385977, "lon": -109.3888108, "location": "Winifred, MT", "url": "https://vanished.us/allen-clarence-theis-missing-from-lewistown"},
    {"name": "Barbara Assunta Bolick", "lat": 46.3950952, "lon": -114.2559528, "location": "Bear Creek Overlook Trail, MT", "url": "https://vanished.us/barbara-assunta-bolick-vanished-from-bear-creek-overlook-trail"},
    {"name": "Barry Joel Tragen", "lat": 48.9350407, "lon": -114.3523012, "location": "Kintla Lake, MT", "url": "https://vanished.us/barry-joel-tragen-missing-from-kintla-lake"},
    {"name": "Bobby Panknin (age 4)", "lat": 48.8639825, "lon": -117.6150352, "location": "Deep Lake Area, WA", "url": "https://vanished.us/bobby-panknin-4-years-old-vanished-suddenly-from-the-deep-lake-area"},
    {"name": "Brandon Lamont Brownlee", "lat": 46.9311447, "lon": -112.9745473, "location": "Jenny Creek Trail, MT", "url": "https://vanished.us/brandon-lamont-brownlee-missing-from-jenny-creek-trail"},
    {"name": "Brandon Swanson", "lat": 44.6250625, "lon": -96.1205625, "location": "Porter, MN", "url": "https://vanished.us/brandon-swanson-vanished-last-words-were-oh-shit"},
    {"name": "Bruce Pike", "lat": 44.8866037, "lon": -110.7360704, "location": "Indian Creek Campground, Yellowstone, WY", "url": "https://vanished.us/bruce-pike-last-seen-at-indian-creek-campground"},
    {"name": "Bryce Florian", "lat": 48.2758784, "lon": -124.6803367, "location": "Shi Shi Beach Trail, WA", "url": "https://vanished.us/bryce-florian-disappeared-from-shi-shi-beach-trail"},
    {"name": "Capt. Matthew Kraft", "lat": 36.7816200, "lon": -118.2893230, "location": "Grays Meadows Campground, CA", "url": "https://vanished.us/captain-matthew-kraft-missing-from-grays-meadows-campground"},
    {"name": "Cassie Sheetz", "lat": 38.6938070, "lon": -79.5419732, "location": "Spruce Knob, Huckleberry Trail, WV", "url": "https://vanished.us/cassie-sheetz-missing-from-spruce-knob"},
    {"name": "Charles McCullar", "lat": 40.7541564, "lon": -121.3857036, "location": "Crater Lake / Pacific Crest Trail, CA", "url": "https://vanished.us/charles-mccullar-crater-lake"},
    {"name": "Charles Robert Rutherford", "lat": 46.5829527, "lon": -87.3841545, "location": "Presque Isle, Marquette, MI", "url": "https://vanished.us/charles-robert-rutherford-missing-from-presque-isle"},
    {"name": "Cian McLaughlin", "lat": 43.7259623, "lon": -110.7651383, "location": "Delta Lake / Garnet Canyon Trail, WY", "url": "https://vanished.us/cian-mclaughlin-vanished-whilst-out-on-a-hike-near-delta-lake"},
    {"name": "Connie Johnson", "lat": 46.2076952, "lon": -115.0376164, "location": "Big Rock Mountain, ID", "url": "https://vanished.us/connie-johnson-missing-from-big-rock-fog-mountain"},
    {"name": "Daniel Lynn Campbell", "lat": 44.9881483, "lon": -110.4279162, "location": "Hellroaring Creek, Yellowstone, WY", "url": "https://vanished.us/daniel-lynn-campbell-vanished-last-seen-hellroaring-creek-trailhead"},
    {"name": "Daniel Robinson", "lat": 33.3703197, "lon": -112.5837766, "location": "Buckeye, AZ", "url": "https://vanished.us/daniel-robinson-missing-buckeye"},
    {"name": "David Paul Morrison", "lat": 37.7459192, "lon": -119.5331992, "location": "Half Dome, Yosemite, CA", "url": "https://vanished.us/david-paul-morrison-missing-from-half-dome-yosemite-national-park"},
    {"name": "David Scott Partlow", "lat": 48.3466306, "lon": -114.0981767, "location": "Columbia Mountain, Flathead NF, MT", "url": "https://vanished.us/david-scott-partlow-vanished-from-columbia-mountain"},
    {"name": "Deborah Jean Swanson", "lat": 47.6668869, "lon": -116.7717207, "location": "Tubbs Hill Trail, Coeur d'Alene, ID", "url": "https://vanished.us/deborah-jean-swanson-vanished-from-the-tubbs-hill-trail"},
    {"name": "Dennis Eugene Johnson", "lat": 44.7520625, "lon": -110.4861875, "location": "Canyon Junction, Yellowstone, WY", "url": "https://vanished.us/dennis-eugene-johnson-vanished-while-looking-for-his-missing-sister"},
    {"name": "Dennis Martin (age 6)", "lat": 35.5625892, "lon": -83.7321163, "location": "Spence Field, Great Smoky Mountains, NC", "url": "https://vanished.us/dennis-martin-vanished-great-smokey-mountains"},
    {"name": "Derrick Engebretson", "lat": 42.5131895, "lon": -122.1458549, "location": "Winema National Forest / Pelican Butte, OR", "url": "https://vanished.us/derrick-engebretson-missing-from-winema-national-forest"},
    {"name": "Dikran Knadjian", "lat": 37.7397002, "lon": -119.5731916, "location": "Curry Village, Yosemite, CA", "url": "https://vanished.us/dikran-knadjian-missing-from-curry-village-yosemite"},
    {"name": "Donald Buchanan", "lat": 37.7454017, "lon": -119.5333816, "location": "Half Dome Trail, Yosemite, CA", "url": "https://vanished.us/donald-buchanan-missing-from-half-dome-yosemite"},
    {"name": "Donald Dugger", "lat": 48.9052657, "lon": -95.3144041, "location": "Warroad, MN", "url": "https://vanished.us/donald-dugger-vanished-from-his-vehicle-after-calling-911"},
    {"name": "Frances Brown", "lat": 54.9363490, "lon": -127.4593425, "location": "Kitseguecla Lake Rd, BC, Canada", "url": "https://vanished.us/frances-brown-vanished-from-kitseguecla-lake-rd"},
    {"name": "Fred Werm Comstock", "lat": 37.7952579, "lon": -119.3452131, "location": "Vogelsang High Sierra Camp, Yosemite, CA", "url": "https://vanished.us/fred-werm-comstock-missing-from-vogelsang-high-sierra-camp"},
    {"name": "George Penca", "lat": 37.7568139, "lon": -119.5969114, "location": "Upper Yosemite Falls, CA", "url": "https://vanished.us/george-penca-vanished-from-yosemite-national-park"},
    {"name": "Gerrish Family", "lat": 37.6099782, "lon": -119.8220690, "location": "Savage-Lundy Trail, Mariposa, CA", "url": "https://vanished.us/gerrish-family-found-dead-with-dog"},
    {"name": "Gilbert Mark Gilman", "lat": 47.5159423, "lon": -123.3311625, "location": "Staircase, Olympic National Park, WA", "url": "https://vanished.us/gilbert-mark-gilman-missing-in-staircase-olympic-national-park"},
    {"name": "GPS Joe (Joe Domin)", "lat": 34.0048324, "lon": -111.4712657, "location": "Mount Peeley Trailhead, Payson, AZ", "url": "https://vanished.us/gps-joe-joe-domin-vanished-off-the-face-of-the-earth"},
    {"name": "Jack Forest Thomas", "lat": 45.4933190, "lon": -115.3358810, "location": "Fern Falls Area, Idaho Centennial Trail, ID", "url": "https://vanished.us/jack-forest-thomas-missing-from-fern-falls-area"},
    {"name": "James Arthur", "lat": 37.4906187, "lon": -119.4966313, "location": "Iron Lakes, CA", "url": "https://vanished.us/james-arthur-missing-from-iron-lakes"},
    {"name": "James Duffy", "lat": 47.8626875, "lon": -120.9748125, "location": "Peavine Creek, Berne, WA", "url": "https://vanished.us/james-duffy-vanished-from-a-locked-campervan-at-peavine-creek"},
    {"name": "James Youngblom", "lat": 37.9232559, "lon": -119.4523847, "location": "LeConte Falls, Yosemite, CA", "url": "https://vanished.us/james-youngblom-found-dead-in-yosemite"},
    {"name": "Jason Andrew Knapp", "lat": 35.0202629, "lon": -82.6935482, "location": "Table Rock State Park, Pickens, SC", "url": "https://vanished.us/jason-andrew-knapp-missing-table-rock-state-park"},
    {"name": "Jason Lee Lovelady", "lat": 48.6923707, "lon": -121.9048197, "location": "Near Elbow Lake, Concrete, WA", "url": "https://vanished.us/jason-lee-lovelady-disappeared-from-near-elbow-lake-whilst-gathering-pine-cones"},
    {"name": "Jeff Estes", "lat": 37.8477926, "lon": -119.4926430, "location": "May Lake, Yosemite, CA", "url": "https://vanished.us/jeff-estes-missing-in-yosemite"},
    {"name": "Jeffrey Michael Bratcher", "lat": 47.0074167, "lon": -124.1613653, "location": "Ocean Shores, WA", "url": "https://vanished.us/jeffrey-michael-bratcher-is-missing-and-was-last-seen-in-ocean-shores"},
    {"name": "Jody Roberts", "lat": 47.2444137, "lon": -122.4343223, "location": "Tacoma, WA", "url": "https://vanished.us/jody-roberts-vanished-and-turned-up-12-years-later-in-alaska"},
    {"name": "Joel Thomazin", "lat": 37.9628119, "lon": -119.8382382, "location": "Hetch Hetchy Area, Yosemite, CA", "url": "https://vanished.us/joel-thomazin-missing-from-hetch-hetchy-area"},
    {"name": "John Blevins Cogdell", "lat": 37.7362471, "lon": -119.5638120, "location": "Upper Pines Campground, Yosemite, CA", "url": "https://vanished.us/john-blevins-cogdell-unexplained-death-in-yosemite"},
    {"name": "John Gunn", "lat": 37.7468386, "lon": -119.5903793, "location": "Yosemite Valley, CA", "url": "https://vanished.us/john-gunn-found-with-a-broken-neck-after-vanishing-from-yosemite"},
    {"name": "Joseph Robert Clewley", "lat": 46.6364888, "lon": -85.4959350, "location": "Tahqua Trail, McMillan Township, MI", "url": "https://vanished.us/joseph-robert-clewley-missing-from"},
    {"name": "Kenneth Klein", "lat": 37.7499690, "lon": -119.5886840, "location": "Yosemite Valley, CA", "url": "https://vanished.us/kenneth-klein-missing-from-yosemite-national-park"},
    {"name": "Kieran Burke", "lat": 37.7384615, "lon": -119.5748224, "location": "Curry Village, Yosemite, CA", "url": "https://vanished.us/kieran-burke-missing-from-curry-village-yosemite-national-park"},
    {"name": "Maureen Kelly", "lat": 45.9151125, "lon": -122.2025917, "location": "Canyon Creek Campground, Yacolt, WA", "url": "https://vanished.us/maureen-kelly-vanished-into-the-woods-wearing-only-a-fanny-pack"},
    {"name": "Michael Allen Ficery", "lat": 38.0279748, "lon": -119.6660063, "location": "Tiltill Mountain, Yosemite, CA", "url": "https://vanished.us/michael-allen-ficery-missing-in-yosemite-national-park"},
    {"name": "Nelson Paisley", "lat": 37.7217801, "lon": -119.7131550, "location": "Merced River, Yosemite, CA", "url": "https://vanished.us/nelson-paisley-missing-from-merced-river"},
    {"name": "Oscar Florence Hintta", "lat": 46.5699073, "lon": -88.9499083, "location": "Onion Falls, Trout Creek, MI", "url": "https://vanished.us/oscar-florence-hintta-missing-from-onion-falls"},
    {"name": "Patricia Colyer", "lat": 47.2528768, "lon": -122.4442906, "location": "Tacoma, WA", "url": "https://vanished.us/patricia-colyer-went-missing-and-was-last-seen-leaving-her-mothers-home-with-a-strange-woman"},
    {"name": "Paul Matthew Head", "lat": 37.0868570, "lon": -119.1561350, "location": "Dinkey Creek, CA", "url": "https://vanished.us/paul-matthew-head-disappeared-running-into-the-woods"},
    {"name": "Paula Jean Welden", "lat": 44.2506875, "lon": -72.8806875, "location": "Long Trail, Fayston, VT", "url": "https://vanished.us/paula-jean-welden-vanished-hiking-the-long-trail"},
    {"name": "Peter Dwight Germain", "lat": 62.3421763, "lon": -150.8740891, "location": "Near Trapper Creek, Petersville, AK", "url": "https://vanished.us/peter-dwight-germain-vanished-from-near-trapper-creek"},
    {"name": "Peter Jackson", "lat": 37.8704036, "lon": -119.6482386, "location": "White Wolf Campground, Yosemite, CA", "url": "https://vanished.us/peter-jackson-vanished-from-white-wolf-campground"},
    {"name": "Richard Judd", "lat": 37.6259390, "lon": -119.4494896, "location": "Lower Merced Pass Lake, Yosemite, CA", "url": "https://vanished.us/richard-judd-disappeared-in-yosemite"},
    {"name": "Robert Perry Bissell", "lat": 45.1448337, "lon": -121.9826220, "location": "Roaring River Wilderness, OR", "url": "https://vanished.us/robert-perry-bissell-left-his-campsite-and-vanished-into-the-roaring-river-wilderness-area"},
    {"name": "Robert Willis", "lat": 37.0739666, "lon": -119.1046580, "location": "Deer Creek, Dinkey Creek, CA", "url": "https://vanished.us/robert-willis-vanished-whilst-hunting-at-deer-creek"},
    {"name": "Ronald Scott Grey", "lat": 46.1401684, "lon": -115.9789311, "location": "Mirror Lake Ridge, Kooskia, ID", "url": "https://vanished.us/ronald-scott-grey-disappeared-from-mirror-lake-ridge"},
    {"name": "Ruthanne Ruppert", "lat": 37.7485335, "lon": -119.5826407, "location": "Yosemite Valley, CA", "url": "https://vanished.us/ruthanne-ruppert-missing-from-yosemite-medical-clinic"},
    {"name": "Sammy Boehlke", "lat": 42.9127833, "lon": -122.0722417, "location": "Cleetwood Cove, Crater Lake, OR", "url": "https://vanished.us/sammy-boehlke-missing-from-cleetwood-cove-crater-lake"},
    {"name": "Sandra Johnsen Hughes", "lat": 37.4982531, "lon": -119.3743725, "location": "Sierra National Forest, Bass Lake, CA", "url": "https://vanished.us/sandra-johnsen-hughes-missing-from-sierra-national-forest"},
    {"name": "Scott Tenzcar", "lat": 38.2471359, "lon": -119.2204094, "location": "Bridgeport, CA", "url": "https://vanished.us/scott-tenzcar-unexplained-death-in-yosemite"},
    {"name": "Stacy Ann Arras", "lat": 37.8087268, "lon": -119.4496709, "location": "Yosemite, CA", "url": "https://vanished.us/stacy-ann-arras-vanished-in-yosemite"},
    {"name": "Steve Martin", "lat": 48.6385291, "lon": -117.0885575, "location": "WA 99119", "url": "https://vanished.us/steve-martin-vanished-whilst-out-running-his-body-would-be-found-a-year-later"},
    {"name": "Stuart Isaacs", "lat": 44.4416028, "lon": -110.7196539, "location": "Craig Pass, Yellowstone, WY", "url": "https://vanished.us/stuart-isaacs-vehicle-was-found-abandoned-stuart-isaac-is-still-missing"},
    {"name": "Susan Schantin", "lat": 37.7288001, "lon": -119.6095000, "location": "Wildcat Creek, Yosemite Valley, CA", "url": "https://vanished.us/susan-schantin-last-seen-wildcat-creek"},
    {"name": "Susan Seymour Adams", "lat": 46.2182107, "lon": -114.5953889, "location": "Battle Lake, Selway-Bitterroot Wilderness, ID", "url": "https://vanished.us/susan-seymour-adams-vanished-from-battle-lake-selway-bitterroot-wilderness"},
    {"name": "Terrence Woods", "lat": 45.6632398, "lon": -115.5265174, "location": "Penman Mine, ID", "url": "https://vanished.us/terrence-woods-vanished-from-penman-mine-idaho"},
    {"name": "The Missing German Family", "lat": 35.9963429, "lon": -116.8222675, "location": "Warm Spring Canyon, Death Valley, CA", "url": "https://vanished.us/the-missing-german-death-valley-family"},
    {"name": "Thelma Pauline Melton", "lat": 35.4727684, "lon": -83.4287806, "location": "Forney Ridge Trail, Bryson City, NC", "url": "https://vanished.us/thelma-pauline-melton-hiking-on-trail-vanished"},
    {"name": "Timothy Barnes", "lat": 37.8646746, "lon": -119.4514844, "location": "Murphy Creek Trailhead, Yosemite, CA", "url": "https://vanished.us/timothy-barnes-last-seen-murphy-creek-trailhead-yosemite"},
    {"name": "Timothy Nolan", "lat": 37.7604804, "lon": -119.5073834, "location": "Quarter Domes, Yosemite, CA", "url": "https://vanished.us/timothy-nolan-unexplained-death-in-yosemite"},
    {"name": "Tom Opperman", "lat": 37.7384379, "lon": -119.4128535, "location": "Merced Lake, Yosemite, CA", "url": "https://vanished.us/tom-opperman-missing-from-merced-lake-yosemite"},
    {"name": "Trenny Gibson", "lat": 35.5569764, "lon": -83.4962661, "location": "Forney Ridge Trail, Bryson City, NC", "url": "https://vanished.us/trenny-gibson-vanished-whilst-on-a-school-trip-with-40-students"},
    {"name": "Walter Reinhard", "lat": 37.8647852, "lon": -119.6488084, "location": "White Wolf, Yosemite, CA", "url": "https://vanished.us/walter-reinhard-missing-from-white-wolf-yosemite-national-park"},
]

# ── Missing / Dead Scientists ─────────────────────────────────
MISSING_SCIENTISTS = [
    {"name": "Frank Maiwald", "lat": 34.0522, "lon": -118.2437, "date": "Jul 4, 2024", "affiliation": "NASA Jet Propulsion Laboratory", "location": "Los Angeles, CA", "status": "Dead — no autopsy performed", "notes": "NASA JPL researcher, cause of death never disclosed. No autopsy performed. 🔗 JPL/Caltech cluster: Maiwald, Hicks, Reza, and Grillmair all had direct NASA JPL or Caltech ties — three are dead, one missing. Four researchers from the same network, four anomalous deaths/disappearances.", "photo": "photos/maiwald_frank.jpg"},
    {"name": "Anthony Chavez", "lat": 35.8800, "lon": -106.3031, "date": "May 4, 2025", "affiliation": "Los Alamos National Laboratory", "location": "Los Alamos, NM", "status": "Missing", "notes": "Left car locked in driveway. No wallet, keys or personal items taken. Never found. 🔗 Los Alamos/KCNSC cluster: Chavez, Casias (LANL, Jun 2025), and Garcia (KCNSC, Aug 2025) all vanished within 4 months of each other — each leaving without phone, wallet, keys, or vehicle. All connected to US nuclear weapons programs.", "photo": "photos/chavez_anthony.jpg"},
    {"name": "Monica Reza", "lat": 34.3484, "lon": -117.8106, "date": "Jun 22, 2025", "affiliation": "NASA JPL / Air Force Research Lab", "location": "Angeles National Forest, CA", "status": "Missing", "notes": "Co-inventor of Mondaloy rocket superalloy. Vanished 30 feet from hiking companions. No trace found. ⚠️ Mondaloy connection: Neil McCasland's AFRL program managed Mondaloy production contracts. Both Reza and McCasland vanished within months of each other — completing the erasure of everyone with full knowledge of the alloy's production chain. 🔗 JPL/Caltech cluster: Reza shares the JPL research network with Maiwald, Hicks, and Grillmair — all dead or missing.", "photo": "photos/reza_monica.png"},
    {"name": "Melissa Casias", "lat": 35.8800, "lon": -106.3031, "date": "Jun 26, 2025", "affiliation": "Los Alamos National Laboratory", "location": "Los Alamos, NM", "status": "Missing — phones wiped", "notes": "Both phones found at home factory reset. Walked miles into desert with no phone, wallet or keys. 🔗 Los Alamos/KCNSC cluster: Casias, Chavez (LANL, May 2025), and Garcia (KCNSC, Aug 2025) all vanished within 4 months — each without phone, wallet, or vehicle. All connected to US nuclear weapons programs.", "photo": "photos/casias_melissa.jpg"},
    {"name": "Jason Thomas", "lat": 42.5001, "lon": -71.0662, "date": "Dec 12, 2025", "affiliation": "Novartis / DoD contracts", "location": "Wakefield, MA", "status": "Dead — found in lake", "notes": "Chemical biology researcher with active DoD contracts. Body recovered from Lake Quannapowitt March 17, 2026. 🔗 Massachusetts cluster: Thomas (Dec 12) and Loureiro (Dec 15) — two DoD-adjacent researchers died in the Boston metro area within 3 days of each other.", "photo": "photos/thomas_jason.jpg"},
    {"name": "Nuno Loureiro", "lat": 42.3317, "lon": -71.1203, "date": "Dec 15, 2025", "affiliation": "MIT Plasma Science and Fusion Center", "location": "Brookline, MA", "status": "Murdered", "notes": "Director of MIT fusion center, reportedly near breakthrough in unlimited clean energy. Shot at his front door. 🔗 Massachusetts cluster: Loureiro (Dec 15) and Thomas (Dec 12) — two DoD-adjacent researchers died in the Boston metro area within 3 days of each other.", "photo": "photos/loureiro_nuno.jpg"},
    {"name": "Carl Grillmair", "lat": 34.1478, "lon": -118.1445, "date": "Feb 16, 2026", "affiliation": "Caltech / NASA JPL", "location": "Pasadena, CA", "status": "Murdered", "notes": "Astrophysicist who contributed to discovery of water on distant planet. Shot on front porch at 6am. 🔗 JPL/Caltech cluster: Grillmair is the fourth member of the JPL/Caltech network to die or vanish — joined by Maiwald, Hicks (both dead, no autopsies), and Reza (missing).", "photo": "photos/grillmair_carl.jpg"},
    {"name": "Neil McCasland", "lat": 35.0853, "lon": -106.6504, "date": "Feb 27, 2026", "affiliation": "Wright-Patterson AFB / AFRL", "location": "Albuquerque, NM", "status": "Missing", "notes": "Oversaw $2.2B Air Force science program. Named in Wikileaks as UFO disclosure advisor to Tom DeLonge. Left home without phone, glasses or wearables. Clothing found nearby. ⚠️ Mondaloy connection: McCasland's AFRL program held oversight of Mondaloy superalloy production contracts. Monica Reza, Mondaloy's co-inventor, vanished just months earlier. Together they formed the final link in the Mondaloy knowledge chain — now completely severed.", "photo": "photos/mccasland_neil.jpg"},
    {"name": "Michael David Hicks", "lat": 34.2013, "lon": -118.1714, "date": "Jul 30, 2023", "affiliation": "NASA Jet Propulsion Laboratory", "location": "Pasadena, CA", "status": "Dead — no autopsy", "notes": "JPL research scientist 1998–2022. Published 80+ papers on comet and asteroid physical properties. Cause of death never disclosed. No autopsy performed. 🔗 JPL/Caltech cluster: Three other scientists from the same JPL/Caltech network are also dead or missing — Maiwald (dead, no autopsy), Reza (missing), and Grillmair (murdered). Hicks is the earliest known vertex of the cluster.", "photo": "photos/hicks_michael.jpg"},
    {"name": "Dallis Hardwick", "lat": 34.2013, "lon": -118.1714, "date": "Jan 5, 2014", "affiliation": "Rockwell Science Center / Aerojet Rocketdyne", "location": "California", "status": "Dead - cancer", "notes": "Co-inventor of Mondaloy nickel superalloy with Monica Reza. The first vertex of the Mondaloy triangle. Every person holding complete knowledge of Mondaloy's production chain is now dead or missing: Hardwick (2014), Reza (2025), McCasland (2026). Her death predates the pattern but is now viewed as the starting point of the chain severance.", "photo": "photos/hardwick_dallis.jpg"},
    {"name": "Steven Garcia", "lat": 35.1106, "lon": -106.6090, "date": "Aug 28, 2025", "affiliation": "Kansas City National Security Campus (KCNSC), Albuquerque", "location": "Albuquerque, NM", "status": "Missing", "notes": "Government contractor producing non-nuclear components for US nuclear weapons. Left home with only a handgun and water. No phone, keys, wallet or car. Anonymous source says he was stable and possibly targeted by foreign spies. 🔗 Los Alamos/KCNSC cluster: Garcia is the third member of the nuclear weapons contractor cluster — Chavez (LANL, May) and Casias (LANL, Jun) vanished months earlier. KCNSC produces the non-nuclear components that LANL designs.", "photo": "photos/garcia_steven.png"},
    {"name": "Wynn Free", "lat": 39.7392, "lon": -105.0663, "date": "Apr 14–18, 2026", "affiliation": "UAP Disclosure / Independent Researcher", "location": "Unknown — Boulder, CO area (unconfirmed)", "status": "Dead — circumstances unclear", "notes": "Co-author and biographer of David Wilcock. Wrote 'The Reincarnation of Edgar Cayce?' with Wilcock. Died approximately April 14–18, 2026; location and exact circumstances unconfirmed at time of entry. Death occurred days before Wilcock's own.", "photo": "photos/free_wynn.jpg"},
    {"name": "David Wilcock", "lat": 39.9619, "lon": -105.5097, "date": "Apr 20, 2026", "affiliation": "UAP Disclosure / Independent Researcher", "location": "Nederland, CO (near Boulder)", "status": "Dead — suspected suicide", "notes": "Prominent UAP disclosure researcher and author. Vocal advocate for government transparency on non-human intelligence. Died April 20, 2026 in Nederland, CO. Death ruled suspected suicide. His co-author and biographer Wynn Free died days earlier. Two of the most public voices on UAP disclosure dead within days of each other.", "photo": "photos/wilcock_david.jpg"},
    {"name": "Joshua LeBlanc", "lat": 34.7304, "lon": -86.5861, "date": "Jul 22, 2025", "affiliation": "NASA Marshall Space Flight Center", "location": "Huntsville, AL", "status": "Dead — Tesla crash fire", "notes": "Age 29. NASA nuclear propulsion engineer at Marshall Space Flight Center in Huntsville, Alabama. Died July 22, 2025 when his Tesla caught fire in a crash. ⚠️ Unexplained detail: LeBlanc's Tesla was parked at Huntsville International Airport for approximately 4 hours before the fatal crash — the reason for the airport visit and the 4-hour gap have never been publicly explained. No further details released by NASA or local authorities. MSFC leads NASA's Nuclear Thermal Propulsion project for deep space missions. 🔗 Huntsville cluster: LeBlanc is one of three NASA-connected deaths in the Huntsville research corridor — alongside Amy Eskridge (2022) and the Moffatt family (2026, whose son Andrew worked at UAH).", "photo": "photos/leblanc_joshua.jpg"},
    {"name": "Matthew James Sullivan", "lat": 38.8719, "lon": -77.0563, "date": "May 2024", "affiliation": "US Air Force Intelligence", "location": "Washington, DC area", "status": "Dead — circumstances unclear", "notes": "Air Force intelligence officer and whistleblower. Died in May 2024 before he was able to deliver planned testimony on UAP-related intelligence programs. Death occurred in the period of intense Congressional UFO hearings. Circumstances not publicly disclosed.", "photo": "photos/sullivan_james_matthew.png"},
    {"name": "Ning Li", "lat": 34.7248, "lon": -86.6404, "date": "2014", "affiliation": "University of Alabama in Huntsville / NASA", "location": "Huntsville, AL", "status": "Dead — car accident", "notes": "Theoretical physicist who developed a framework for anti-gravity propulsion using superconductors and rotating ions. Her 1991 paper in Physical Review B proposed that spinning superconductors could partially cancel gravity. Collaborated with NASA's Marshall Space Flight Center on experimental validation. Died 2014 in a car accident. Her anti-gravity research was quietly discontinued after her death.", "photo": "photos/li_ning.jpg"},
    {"name": "Amy Eskridge", "lat": 34.7312, "lon": -86.5847, "date": "Jun 11, 2022", "affiliation": "Aerospace industry, Huntsville, AL", "location": "Huntsville, AL", "status": "Dead — ruled suicide", "notes": "Aerospace researcher based in Huntsville, Alabama — the nerve center of US rocket and defense research (NASA Marshall Space Flight Center, Redstone Arsenal, numerous defense contractors). Died June 11, 2022. Death ruled suicide; no further details publicly released. Huntsville has produced a disproportionate cluster of aerospace and defense researchers whose deaths have drawn scrutiny: Eskridge, LeBlanc (2025), and Ning Li (2014) all died in or near the same research corridor.", "photo": "photos/eskridge_amy.jpg"},
    {"name": "James 'Tony' Moffatt + Family", "lat": 34.7157, "lon": -81.6382, "date": "Apr 17, 2026", "affiliation": "NASA Johnson Space Center / US Army (Ret.)", "location": "Union County Airport, SC", "status": "Dead — plane crash (4 killed)", "notes": "James 'Tony' Moffatt, 60 — NASA Johnson Space Center payload specialist with 14 Space Shuttle and ISS missions, retired Army Lt. Colonel, and experimental test pilot — died April 17, 2026 when his small aircraft crashed at Union County Airport, South Carolina. Also killed: wife Leasa Moffatt (61); son Andrew Moffatt (30), research engineer at University of Alabama Huntsville; son William Moffatt (28), cybersecurity professional. The entire family was wiped out in a single crash. Moffatt died three days before UAP disclosure researcher David Wilcock was found dead, ruled suicide. 🔗 Huntsville cluster: Moffatt's son Andrew worked at UAH — the same Huntsville, Alabama research corridor that claimed Amy Eskridge (2022) and Joshua LeBlanc (2025). Three NASA-connected deaths from the same geographic hub within 4 years.", "photo": "photos/moffatt_tony_james.jpg"},
]

# ── Chinese Scientists ────────────────────────────────────────
# NOTE: At least 9 Chinese scientists in military AI, hypersonics, space defense
# and advanced weapons have died since 2018. Chinese media calls it "extremely
# uncommon." Military analysts now asking: is there a silent scientist war?
CHINESE_SCIENTISTS = [
    {"name": "Feng Yanghe", "field": "MIL AI", "lat": 39.9042, "lon": 116.4074, "date": "Jul 1, 2023", "affiliation": "National University of Defense Technology (NUDT)", "location": "Beijing, China", "status": "Dead ☠️ — mysterious car crash", "notes": "Age 38. Military AI researcher at the National University of Defense Technology — China's most elite defense science institution. Developed the 'War Skull' AI platform, which simulates invasion scenarios including a Taiwan operation. Died in a car crash in Beijing at 3am on July 1, 2023, while leaving a late-night work meeting. His official obituary used the phrase 'sacrificed while performing official duties' — highly unusual language for a road accident, typically reserved for soldiers killed in combat. Chinese defense analysts considered the language a deliberate signal. His death came as China was accelerating military AI development to match US capabilities."},
    {"name": "Zhang Xiaoxin", "field": "SPACE", "lat": 39.9042, "lon": 116.4074, "date": "Dec 2024", "affiliation": "Chinese space research sector", "location": "Beijing, China", "status": "Dead ☠️ — car accident", "notes": "Age 62. Chinese space expert who died in a car accident in December 2024. Details of the crash and the program he was working on have not been publicly disclosed. His death is one of at least nine documented cases of Chinese scientists in sensitive defense and aerospace fields dying under sudden or unexplained circumstances since 2018 — a pattern Chinese state media has described as 'extremely uncommon.'"},
    {"name": "Chen Shuming", "field": "CHIPS", "lat": 39.9042, "lon": 116.4074, "date": "2018", "affiliation": "Chinese microelectronics / semiconductor sector", "location": "Beijing, China", "status": "Dead ☠️ — crash", "notes": "Age 57. Microelectronics specialist killed in a crash in 2018. Chen worked in the sensitive semiconductor and advanced electronics sector — a field of acute strategic importance as the US moved to restrict China's access to advanced chip technology. His death preceded a wave of US export controls that would cripple China's semiconductor ambitions. Details of the accident were not publicly disclosed by Chinese authorities."},
    {"name": "Fang Daining", "field": "HYPER", "lat": 39.9042, "lon": 116.4074, "date": "2022–2024 (est.)", "affiliation": "Chinese hypersonics research", "location": "Beijing, China", "status": "Dead ☠️ — apparent medical issues", "notes": "Age 68. Hypersonics researcher who died of apparent medical issues. China has invested heavily in hypersonic weapons development — the DF-17 and DF-ZF glide vehicles — and the deaths of senior hypersonics researchers have drawn attention from Western defense analysts. Fang's death is part of a documented cluster of hypersonics specialists who have died in the 2018–2025 period. No details released by Chinese authorities."},
    {"name": "Yan Hong", "field": "HYPER", "lat": 39.9042, "lon": 116.4074, "date": "2022–2024 (est.)", "affiliation": "Chinese hypersonics research", "location": "Beijing, China", "status": "Dead ☠️ — apparent medical issues", "notes": "Age 56. Hypersonics researcher who died of apparent medical issues in the same period as colleague Fang Daining. The simultaneous loss of two senior hypersonics researchers has been flagged by analysts as statistically unlikely. China's hypersonics programs are considered among the most advanced in the world, and the identities and research areas of scientists involved are closely held state secrets. No cause of death was publicly disclosed."},
    {"name": "Zhang Daibing", "field": "DRONES", "lat": 39.9042, "lon": 116.4074, "date": "2023–2025 (est.)", "affiliation": "Chinese UAV / drone research sector", "location": "Beijing, China", "status": "Dead ☠️ — unspecified accident", "notes": "Age 47. Drone and unmanned aerial vehicle (UAV) expert who died in an unspecified accident. China has become the world's leading producer of military drones, and its UAV programs — including the Wing Loong and CH-series attack drones deployed in conflicts across the Middle East and Africa — represent a major strategic export. The loss of a specialist-level researcher in this field at age 47 is significant. Chinese authorities released no details of the circumstances."},
    {"name": "Liu Donghao", "field": "DATA", "lat": 39.9042, "lon": 116.4074, "date": "2023–2025 (est.)", "affiliation": "Chinese military data science / AI sector", "location": "Beijing, China", "status": "Dead ☠️ — sudden illness", "notes": "Age 51. Military data scientist who died of sudden illness. Data science and AI for battlefield applications is one of China's highest-priority defense research areas — directly relevant to autonomous weapons, targeting systems, and electronic warfare. Liu's death at 51 with no disclosed cause follows the same pattern seen across at least eight other Chinese defense researchers in the same period."},
    {"name": "Zhou Guangyuan", "field": "CHEM", "lat": 39.9042, "lon": 116.4074, "date": "2023–2025 (est.)", "affiliation": "Chinese advanced materials / chemistry research", "location": "Beijing, China", "status": "Dead ☠️ — sudden illness", "notes": "Age 51. Chemist working in advanced materials research who died of sudden illness. Advanced materials — including energetic materials for warheads, radar-absorbing coatings, and hypersonic thermal protection systems — are a critical enabling technology for next-generation Chinese weapons. Zhou's death at 51, with no details disclosed by Chinese authorities, fits the pattern of researchers in sensitive fields dying suddenly and quietly."},
    {"name": "Li Minyong", "field": "BIO", "lat": 23.1291, "lon": 113.2644, "date": "Nov 2025", "affiliation": "Sun Yat-sen University / Guangzhou Institute of Biomedicine", "location": "Guangzhou, China", "status": "Dead ☠️ — sudden illness", "notes": "Age 49. Biomedical chemist developing innovative light-controlled drug delivery technology at Sun Yat-sen University. Died suddenly in Guangzhou, November 2025. Light-controlled drug technology has dual-use applications in advanced military medicine and biological research. Cause of death officially listed as sudden illness; no further details released. Li is the most recent confirmed death in a cluster of at least nine Chinese researchers in sensitive fields who have died since 2018 — a pattern Chinese media has described as 'extremely uncommon' and that military analysts are now characterizing as a possible 'silent scientist war.'"},
]

# ── UAP Whistleblowers ────────────────────────────────────────
WHISTLEBLOWERS = [
    # ── Active / Living ──────────────────────────────────────
    {"name": "David Grusch", "lat": 38.8951, "lon": -77.0364, "date": "Jul 26, 2023 (testified)", "affiliation": "Air Force / National Geospatial-Intelligence Agency", "location": "Washington, DC", "status": "Active 📢 — received death threats", "emoji": "📢", "notes": "Former Air Force officer and National Geospatial-Intelligence Agency official who testified before Congress on July 26, 2023 under oath that the US government possesses non-human biologics and has conducted crash retrieval programs for non-human craft. Stated he had personally been shown evidence of UAP crash retrieval legacy programs by multiple intelligence insiders. Faced retaliation, received death threats, and colleagues who corroborated his claims were also targeted. Considered the highest-credibility government whistleblower in UAP history.", "photo": "photos/grusch_david.jpg"},
    {"name": "Ryan Graves", "lat": 36.8529, "lon": -75.9780, "date": "Jul 26, 2023 (testified)", "affiliation": "US Navy / Americans for Safe Aerospace", "location": "Virginia Beach, VA", "status": "Active 📢 — founding UAP advocacy org", "emoji": "📢", "notes": "Former Navy F/A-18 Super Hornet pilot who testified before Congress on July 26, 2023 about UAP encounters during training missions off the East Coast beginning in 2014. Described objects with no visible propulsion holding fixed positions against 120-knot winds and accelerating instantly. Founded Americans for Safe Aerospace (ASA) to advocate for pilots to safely report UAP encounters without career consequences. Argues UAP sightings are vastly underreported due to stigma.", "photo": "photos/graves_ryan.jpg"},
    {"name": "David Fravor", "lat": 32.8884, "lon": -117.2351, "date": "Jul 26, 2023 (testified)", "affiliation": "US Navy", "location": "San Diego, CA area", "status": "Active 📢 — Tic Tac witness", "emoji": "📢", "notes": "Retired Navy Commander and F/A-18 pilot who testified before Congress on July 26, 2023 about the infamous 'Tic Tac' UAP encounter off the San Diego coast in November 2004. Described a white, oblong craft approximately 40 feet long with no wings, rotors, or exhaust, which mirrored his aircraft's movements before accelerating away at speeds beyond any known technology. His encounter was corroborated by three other aircrew and was captured on the FLIR camera. Called it 'the most advanced aircraft I've ever seen in my life.'", "photo": "photos/fravor_david.jpg"},
    {"name": "Dylan Borland", "lat": 37.0826, "lon": -76.3637, "date": "Sep 2025 (testified)", "affiliation": "US Air Force / Langley AFB", "location": "Langley AFB, VA", "status": "Active 📢 — blacklisted after testimony", "emoji": "📢", "notes": "Air Force veteran who testified before Congress in September 2025 about witnessing a massive 100-foot triangle hovering silently over Langley AFB in 2012. Described the craft as completely silent, moving at low altitude over the base perimeter before disappearing. After going public, Borland reported being blacklisted from intelligence community positions for which he was otherwise qualified — a pattern seen with other UAP witnesses who come forward.", "photo": "photos/borland_dylan.png"},
    {"name": "Jeffrey Nuccetelli", "lat": 34.7366, "lon": -120.5658, "date": "Sep 2025 (testified)", "affiliation": "US Air Force / Vandenberg AFB", "location": "Vandenberg AFB, CA", "status": "Active 📢 — 16-year AF veteran", "emoji": "📢", "notes": "Air Force veteran with 16 years of service who testified before Congress in September 2025 about witnessing a massive craft near Vandenberg Space Force Base between 2003 and 2005. Described objects of extraordinary size operating in restricted airspace with no noise, visible propulsion, or transponder signature. Vandenberg is home to Space Launch Delta 30 and has long been associated with UAP reports from military personnel operating in the restricted airspace over the Pacific coast.", "photo": "photos/nuccetelli_jeffrey.jpg"},
    {"name": "Alexandro Wiggins", "lat": 37.3388, "lon": -121.8853, "date": "Sep 2025 (testified)", "affiliation": "US Navy / USS Jackson", "location": "California coast (USS Jackson)", "status": "Active 📢 — first active-duty Navy testifier", "emoji": "📢", "notes": "Navy Senior Chief with 23 years of service and the first active-duty Navy member to testify before Congress about a UAP encounter. In February 2023, while serving aboard the USS Jackson off the California coast, Wiggins witnessed a Tic Tac-shaped object emerge from beneath the ocean surface and ascend rapidly before disappearing. His testimony is significant as it constitutes an active-duty, on-the-record account from a serving military member — a threshold previously never crossed in Congressional UAP hearings.", "photo": "photos/wiggins_alexandro.jpg"},
    # ── Deceased ─────────────────────────────────────────────
    {"name": "Matthew James Sullivan", "lat": 38.8462, "lon": -77.1711, "date": "May 12, 2024", "affiliation": "US Air Force Intelligence", "location": "Falls Church, VA", "status": "Dead ☠️ — accidental overdose (4 substances)", "emoji": "☠️", "notes": "Air Force intelligence officer who died May 12, 2024 of an accidental overdose involving four separate substances — weeks before he was scheduled to testify before Congress about UAP-related intelligence programs. Sullivan had personally witnessed UAPs in government possession and was prepared to expose details of a crash retrieval legacy program. His death eliminated a critical witness during the most active period of Congressional UAP hearings. Circumstances have not been independently investigated.", "photo": "photos/sullivan_james_matthew.png"},
    {"name": "David Wilcock", "lat": 39.9619, "lon": -105.5097, "date": "Apr 20, 2026", "affiliation": "UAP Disclosure / Independent Researcher", "location": "Nederland, CO", "status": "Dead ☠️ — ruled suicide", "emoji": "☠️", "notes": "Prominent UAP disclosure researcher and author who had posted publicly that he was 'not suicidal' days before his death. Found dead April 20, 2026 in Nederland, CO. Death ruled suicide. His co-author and biographer Wynn Free died within days of him. The timing — two of the most public voices on UAP disclosure dead within days of each other — has drawn scrutiny from the disclosure community.", "photo": "photos/wilcock_david.jpg"},
    {"name": "Lou Elizondo", "lat": 38.9072, "lon": -77.0369, "date": "2007–2017 (AATIP director)", "affiliation": "Pentagon / Defense Intelligence Agency", "location": "Washington, DC area", "status": "Active 📢 — resigned in protest", "emoji": "📢", "notes": "Former counterintelligence officer who ran the Pentagon's Advanced Aerospace Threat Identification Program (AATIP) from 2007 to 2017. Resigned in protest after concluding that the program's findings — non-human craft operating in US airspace — were being systematically suppressed. Went public in 2017 alongside Christopher Mellon, triggering the modern UAP disclosure wave. Has stated under oath that the US government possesses off-world technology and non-human biologics. Worked closely with David Grusch and Mellon through the To The Stars Academy.", "photo": "photos/elizondo_lou.jpg"},
    {"name": "Christopher Mellon", "lat": 38.8951, "lon": -77.0500, "date": "2017–present (public advocate)", "affiliation": "Office of the Secretary of Defense / Senate Intelligence Committee", "location": "Washington, DC area", "status": "Active 📢 — Senate intel veteran", "emoji": "📢", "notes": "Former Deputy Assistant Secretary of Defense for Intelligence under Presidents Clinton and George W. Bush, and former Staff Director of the Senate Intelligence Committee. Left government and joined Lou Elizondo and the To The Stars Academy in 2017 to push for UAP disclosure. Was instrumental in getting the 2017 New York Times Tic Tac story published by providing authenticated military UAP footage. Has testified to Congress and publicly stated that multiple government programs exist that possess non-human craft. Regarded as the most credentialed UAP advocate in Washington.", "photo": "photos/mellon_chris.jpg"},
    {"name": "Bob Lazar", "lat": 36.1699, "lon": -115.1398, "date": "1989 (went public)", "affiliation": "Los Alamos National Laboratory / S-4 (alleged)", "location": "Las Vegas, NV", "status": "Active 📢 — original S-4 whistleblower", "emoji": "📢", "notes": "Physicist who claimed to have worked at a classified facility called S-4, adjacent to Area 51, in 1989. Alleged that he was tasked with back-engineering the propulsion system of recovered non-human craft — specifically gravity wave generators powered by Element 115 (moscovium), an element not officially synthesized until 2003. His descriptions of the facility and the technology have been corroborated in part by declassified documents, his Los Alamos employment records, and the later synthesis of Element 115. Subject of a 2019 Netflix documentary. Remains the most consequential early UAP whistleblower in American history.", "photo": "photos/lazar_bob.jpg"},
    {"name": "James 'Tony' Moffatt + Family", "lat": 34.7157, "lon": -81.6382, "date": "Apr 17, 2026", "affiliation": "NASA Johnson Space Center / US Army (Ret.)", "location": "Union County Airport, SC", "status": "Dead ☠️ — plane crash (4 killed)", "emoji": "☠️", "notes": "James 'Tony' Moffatt, 60 — NASA JSC payload specialist (14 Shuttle/ISS missions), retired Army Lt. Colonel, experimental test pilot — died April 17, 2026 in a crash at Union County Airport, SC. Also killed: wife Leasa (61); son Andrew (30), research engineer UAH; son William (28), cybersecurity. Entire family wiped out. Died three days before UAP researcher David Wilcock was found dead. 🔗 Huntsville cluster: son Andrew worked at UAH — same research corridor as Amy Eskridge (2022) and Joshua LeBlanc (2025).", "photo": "photos/moffatt_tony_james.jpg"},
]

# ── 33rd Parallel notable sites ───────────────────────────────
PARALLEL_33_SITES = [
    {"name": "Roswell, NM", "lat": 33.3943, "lon": -104.5230, "note": "Site of the 1947 UFO crash — officially explained as a weather balloon. Roswell sits almost exactly on the 33rd parallel."},
    {"name": "Denton, TX", "lat": 33.2148, "lon": -97.1331, "note": "FEMA Region 6 headquarters and COG underground bunker complex. Esotericists note its position on the 33rd parallel."},
    {"name": "Phoenix, AZ", "lat": 33.4484, "lon": -112.0740, "note": "Site of the 1997 Phoenix Lights mass sighting — observed by thousands of witnesses. Sits on the 33rd parallel."},
    {"name": "Bermuda Triangle (N vertex)", "lat": 32.3078, "lon": -64.7505, "note": "The northern vertex of the Bermuda Triangle (Bermuda Island). Countless ships and aircraft have vanished in this zone, near the 33rd parallel."},
    {"name": "Casablanca, Morocco", "lat": 33.5731, "lon": -7.5898, "note": "Major city on the 33rd parallel. Site of the 1943 wartime conference between Roosevelt and Churchill. Ancient Phoenician trading post."},
    {"name": "Baghdad, Iraq", "lat": 33.3152, "lon": 44.3661, "note": "Ancient Babylon and modern Baghdad sit on the 33rd parallel. Cradle of written civilization, cuneiform, and early astronomical records."},
    {"name": "Hiroshima, Japan", "lat": 34.3853, "lon": 132.4553, "note": "First city destroyed by an atomic bomb (Aug 6, 1945). Sits just above the 33rd parallel; Nagasaki (second atomic bomb) sits at 32.7°N."},
    {"name": "Dealey Plaza (JFK), Dallas TX", "lat": 32.7792, "lon": -96.8089, "note": "Site of JFK's assassination on Nov 22, 1963 — at 32.78°N, within the esoteric 33rd parallel band. Dallas is also home to a major Masonic temple."},
]

# ── Nuclear sites and incidents ───────────────────────────────
NUCLEAR_SITES = [
    {"name": "Three Mile Island", "lat": 40.1538, "lon": -76.7252, "location": "Middletown, PA", "type": "Incident", "description": "Partial meltdown on March 28, 1979 — worst nuclear accident in US history. Released radioactive gases into the atmosphere. Exposed 2 million people to low-level radiation."},
    {"name": "Hanford Site", "lat": 46.5540, "lon": -119.4863, "location": "Richland, WA", "type": "Facility", "description": "Produced plutonium for the first nuclear bomb and the Fat Man bomb dropped on Nagasaki. Most contaminated nuclear site in the US. 56 million gallons of radioactive waste stored in aging underground tanks, many leaking."},
    {"name": "Nevada Test Site (NTS)", "lat": 37.1206, "lon": -116.0623, "location": "Nye County, NV", "type": "Testing", "description": "928 nuclear tests conducted 1951–1992, including 100 above-ground detonations. Radioactive fallout drifted across the continental US. Downwinders developed cancer at anomalously high rates. Adjacent to Area 51."},
    {"name": "Los Alamos National Laboratory", "lat": 35.8800, "lon": -106.3031, "location": "Los Alamos, NM", "type": "Research", "description": "Birthplace of the atomic bomb (Manhattan Project). Still active nuclear weapons research facility. In 2025, two scientists went missing within 7 weeks of each other from this complex."},
    {"name": "Oak Ridge National Laboratory", "lat": 36.0104, "lon": -84.2696, "location": "Oak Ridge, TN", "type": "Facility", "description": "Originally produced enriched uranium for Little Boy (Hiroshima bomb). Home to the graphite reactor — world's first continuously operating nuclear reactor. Multiple classified waste disposal incidents documented."},
    {"name": "Savannah River Site", "lat": 33.3463, "lon": -81.7374, "location": "Aiken County, SC", "type": "Facility", "description": "Produced tritium and plutonium for nuclear weapons. Stored 51 million gallons of high-level radioactive waste. Located on the 33rd parallel. Documented leaks into the Savannah River watershed."},
    {"name": "Chernobyl Nuclear Power Plant", "lat": 51.3890, "lon": 30.0978, "location": "Pripyat, Ukraine", "type": "Incident", "description": "Catastrophic meltdown April 26, 1986 — worst nuclear disaster in history. Reactor 4 exploded, releasing 400x the radiation of Hiroshima. 350,000 people evacuated. The Exclusion Zone remains uninhabitable."},
    {"name": "Fukushima Daiichi", "lat": 37.4213, "lon": 141.0328, "location": "Okuma, Fukushima, Japan", "type": "Incident", "description": "Three reactor meltdowns triggered by the 2011 Tōhoku earthquake/tsunami. 154,000 people evacuated. Contaminated water still being released into the Pacific Ocean. The most complex ongoing nuclear emergency in history."},
]

# ── Cattle mutilation hotspots ────────────────────────────────
CATTLE_MUTILATION_SITES = [
    {"name": "San Luis Valley, CO", "lat": 37.4000, "lon": -105.8000, "location": "Colorado", "description": "Ground zero for US cattle mutilations. Over 10,000 documented cases since 1967. Animals found with surgical precision organ removal, drained of blood, no tracks. FBI investigated in 1979 but closed the case unsolved. Adjacent to Dulce underground base claims."},
    {"name": "Dulce, NM", "lat": 36.9367, "lon": -106.9856, "location": "New Mexico", "description": "Small town on the Jicarilla Apache Reservation, reportedly above a secret underground base (Dulce Base). Extremely high concentration of cattle mutilations in surrounding area. Witness Phil Schneider claimed to have worked in the base before going public — he was found dead in 1996."},
    {"name": "Northeastern Wyoming", "lat": 44.5000, "lon": -105.5000, "location": "Wyoming", "description": "Crook and Weston counties documented some of the first modern cattle mutilation reports in 1967. Snippy the horse (actually a horse named Lady) was the first high-profile case. Hundreds of cases followed throughout the 1970s with no convictions."},
    {"name": "Western Kansas", "lat": 38.5000, "lon": -100.5000, "location": "Kansas", "description": "Recurring hotspot for cattle mutilation reports spanning decades. Animals found with ear, eye, tongue and reproductive organ removal. No blood on the ground or around carcass. No predator tracks or insect activity — inconsistent with natural decomposition."},
    {"name": "Eastern Oregon", "lat": 43.5000, "lon": -118.5000, "location": "Oregon", "description": "Harney and Malheur counties have documented dozens of mutilation cases. Ranchers report finding animals with the same signature: laser-like cuts, missing organs, no blood. Some cases investigated by local law enforcement with no conclusions."},
    {"name": "Wheaton, KS (Pottawatomie County)", "lat": 39.3400, "lon": -96.3200, "location": "Kansas", "description": "December 2025: cattle found with udders surgically removed, no blood at the scene. Investigated by Chuck Zukowski, veteran mutilation researcher who has documented over 200 cases. Fits the classic pattern: precise excisions, zero hemorrhage, no predator tracks."},
    {"name": "Harney County, OR", "lat": 43.0000, "lon": -119.0000, "location": "Oregon", "description": "Ongoing mutilation cluster active since at least 2019. Subject of the 2025 documentary 'Not One Drop of Blood,' which chronicled multiple cases across the county. Ranchers describe finding cattle with the same surgical signature repeated across years — missing organs, completely exsanguinated, no evidence of predator or human activity at the scene."},
    {"name": "Umatilla County, OR", "lat": 45.6000, "lon": -118.7000, "location": "Oregon", "description": "September 2020: cattle found with tongue, glands, and sex organs removed with what investigators described as surgical precision. Cuts showed no tearing or jagged edges inconsistent with predator or knife work. No blood recovered from the carcass or surrounding ground. Part of a broader pattern of Pacific Northwest mutilations that intensified in 2020."},
]

# ── Bermuda Triangle / Missing Vessels ───────────────────────
BERMUDA_SITES = [
    {"name": "Bermuda Triangle Zone", "lat": 25.0000, "lon": -71.0000, "type": "zone", "description": "The Bermuda Triangle spans roughly 500,000 square miles between Miami (FL), Bermuda, and Puerto Rico. Over 50 ships and 20 aircraft have vanished within this zone under unexplained circumstances. The area overlaps heavily with documented USO activity near Puerto Rico and the Bahamas — both are major hotspots for unidentified submerged objects. The US Navy's AUTEC (Atlantic Undersea Test and Evaluation Center) is located on Andros Island in the Bahamas, directly within the triangle."},
    {"name": "USS Cyclops", "lat": 13.1000, "lon": -59.6000, "type": "vessel", "date": "March 1918", "description": "The largest non-combat loss in US Navy history. The USS Cyclops, a 542-foot collier carrying 10,800 tons of manganese ore, vanished in March 1918 with 309 crew and passengers. No distress call was sent, no wreckage was ever found, and no explanation has been established. Last known position near Barbados. The ship had no known structural defects, weather was calm, and the route was well-traveled."},
    {"name": "Flight 19", "lat": 26.1220, "lon": -80.1434, "type": "aircraft", "date": "December 5, 1945", "description": "Five TBM Avenger torpedo bombers departed Naval Air Station Fort Lauderdale on a routine training mission and were never seen again. All 14 airmen aboard were lost. Radio transmissions recorded the flight leader saying 'We cannot see land… everything is wrong… even the ocean doesn't look as it should.' A Martin Mariner rescue aircraft sent to search also disappeared. No wreckage from any of the six aircraft was ever conclusively identified."},
    {"name": "Star Tiger", "lat": 32.3000, "lon": -64.8000, "type": "aircraft", "date": "January 30, 1948", "description": "British South American Airways Avro Tudor IV airliner disappeared on a flight from Santa Maria (Azores) to Bermuda with 31 passengers and crew. Last radio contact was routine, with no distress call. The aircraft vanished approximately 400 miles northeast of Bermuda. The official inquiry concluded: 'What happened in this case will never be known and the calamity admits of no solution.'"},
    {"name": "SS Marine Sulphur Queen", "lat": 24.5000, "lon": -83.0000, "type": "vessel", "date": "February 1963", "description": "A T2 tanker carrying 15,000 tons of molten sulfur disappeared in February 1963 in the Gulf of Mexico near Key West with 39 crew. A few life jackets and debris were found but the ship itself — over 500 feet long — was never located. The Coast Guard noted that the sulfur cargo, carried at extremely high temperatures, could have created explosive conditions, but no satisfactory explanation was confirmed."},
    {"name": "USS Scorpion", "lat": 37.7400, "lon": -34.9800, "type": "submarine", "date": "May 22, 1968", "description": "Nuclear attack submarine lost in the Atlantic Ocean southwest of the Azores with 99 crew. The wreck was found in 3,000 meters of water but the cause of sinking remains officially undetermined. Two competing theories — torpedo malfunction and hydraulic failure — have never been confirmed. The Navy's investigation was classified for decades. USS Scorpion disappeared in the same year and same ocean as the Israeli submarine INS Dakar and the French submarine Minerve."},
    {"name": "MH370", "lat": -38.0000, "lon": 88.0000, "type": "aircraft", "date": "March 8, 2014", "description": "Malaysia Airlines Flight 370 disappeared with 239 passengers and crew on a flight from Kuala Lumpur to Beijing. The Boeing 777 vanished from radar over the Gulf of Thailand, made unexplained course reversals, and flew for approximately 7 hours before entering the southern Indian Ocean. Despite the largest and most expensive search in aviation history, the main wreckage has never been found. A small number of flaperon fragments washed ashore on Réunion and Tanzania. The disappearance remains officially unsolved."},
]

# ── Window Areas (multi-phenomenon hotspots) ──────────────────
WINDOW_AREAS = [
    {"name": "Skinwalker Ranch", "lat": 40.2572, "lon": -109.8928, "location": "Uintah Basin, UT", "description": "496-acre ranch with the densest concentration of anomalous phenomena documented anywhere on Earth: UFOs, poltergeist activity, cattle mutilations, invisible entities, crop circles, portals, and interdimensional beings. Studied by NIDS (funded by Robert Bigelow) and later by the US government's AATIP program. Now subject of the History Channel series."},
    {"name": "Bradshaw Ranch", "lat": 34.8639, "lon": -111.7810, "location": "Near Sedona, AZ", "description": "Known as 'Arizona's Skinwalker Ranch.' Rancher Bob Bradshaw documented 30+ years of UFO activity, orbs, shadow beings, and cattle anomalies. Eventually surrounded by barbed wire and occupied by men in unmarked vehicles after government interest. Bradshaw was allegedly visited by government agents and pressured to sell."},
    {"name": "Point Pleasant, WV", "lat": 38.8520, "lon": -82.1329, "location": "West Virginia", "description": "Site of the 1966–67 Mothman sightings, precursors to the Silver Bridge collapse that killed 46 people. Town experienced a massive wave of UFO sightings, Men in Black encounters, poltergeist activity and prophetic visions. Investigated by John Keel, who coined the term 'window area.'"},
    {"name": "Marfa Lights", "lat": 30.3085, "lon": -104.0202, "location": "Marfa, TX", "description": "Unexplained lights observed near Marfa since the 1880s. Officially attributed to car headlights on distant roads, but the phenomenon predates automobiles. Lights appear to react intelligently — chasing observers and splitting apart. McDonald Observatory astronomers have been unable to explain the phenomenon."},
    {"name": "Yakima Indian Reservation", "lat": 46.6021, "lon": -120.5059, "location": "Yakima, WA", "description": "One of the most active UFO window areas in the Pacific Northwest. Fire lookout Greg Long documented hundreds of sightings 1972–1992. Orbs and structured craft regularly observed over the ridgelines. Phenomena appear to cluster around the tribal reservation boundaries."},
    {"name": "Gulf Breeze, FL", "lat": 30.3574, "lon": -87.1631, "location": "Florida Panhandle", "description": "Site of the famous 1987–88 Gulf Breeze UFO sightings, photographed by Ed Walters with alleged multiple-witness corroboration. The case became one of MUFON's most investigated. Eglin Air Force Base is nearby. The area continued to produce sighting reports into the 1990s."},
    {"name": "Pine Bush, NY", "lat": 41.6090, "lon": -74.2993, "location": "New York", "description": "Small town in the Hudson Valley considered the 'UFO capital of the Northeast.' Massive triangle craft sightings by hundreds of witnesses in the 1980s. Multiple local residents report ongoing contact experiences. Located near Stewart Air National Guard Base and various underground facilities."},
    {"name": "Sedona Vortexes", "lat": 34.8697, "lon": -111.7610, "location": "Sedona, AZ", "description": "Red rock desert region with documented electromagnetic anomalies at specific vortex sites. Unusually high concentration of UFO sightings, psychic experiences, and claims of interdimensional contact. The area sits atop vast underground water systems and unique iron-oxide geology that may generate unusual electromagnetic fields."},
]

# ── Ley Lines ─────────────────────────────────────────────────
# Each entry: name, short, color, label_at [lat,lon], description,
#   points [[lat,lon],...] — full line including extension endpoints,
#   waypoints [{name, lat, lon, note}] — named stops with popups
LEY_LINES = [
    {
        "name": "American Ley",
        "short": "AMERICAN LEY",
        "color": "#00ffcc",
        "label_at": [39.5, -105.5],
        "description": "Proposed alignment connecting the greatest pre-Columbian earthwork city (Cahokia) through the enigmatic Serpent Mound to the Masonic-planned capital of the United States. The line continues westward toward the Pacific and east into the Atlantic. Cahokia's Monks Mound is larger at its base than the Great Pyramid. Washington DC's street plan contains unmistakable pentagram geometry.",
        "points": [
            [38.5, -128.0],       # Pacific extension
            [38.6558, -90.0627],  # Cahokia Mounds, IL
            [39.0259, -83.4302],  # Serpent Mound, OH
            [38.8951, -77.0364],  # Washington, DC
            [39.8,   -55.0],      # Atlantic extension
        ],
        "waypoints": [
            {"name": "Cahokia Mounds", "lat": 38.6558, "lon": -90.0627, "note": "Largest pre-Columbian city north of Mexico. Population ~20,000 at peak (1100 CE). Monks Mound base covers more area than the Great Pyramid of Giza. Abandoned suddenly around 1300 CE — reason unknown."},
            {"name": "Serpent Mound", "lat": 39.0259, "lon": -83.4302, "note": "1,348-foot effigy mound shaped like an uncoiling serpent swallowing an egg. Aligned precisely with summer solstice sunset and winter solstice sunrise. Built directly over an ancient crypto-explosion impact structure."},
            {"name": "Washington, DC", "lat": 38.8951, "lon": -77.0364, "note": "Capital sited and designed by Freemasons. Street plan contains a 5-pointed star with the White House at its south apex. 'Jenkins Hill' (Capitol site) described by surveyor Pierre Charles L'Enfant as 'a pedestal waiting for a monument.' Aligned with summer solstice sunrise."},
        ],
    },
    {
        "name": "Pacific Ley",
        "short": "PACIFIC LEY",
        "color": "#ff6600",
        "label_at": [36.5, -116.0],
        "description": "Proposed north-south alignment connecting major volcanic and sacred sites along the Pacific spine of North America. Crater Lake formed from the catastrophic collapse of Mt. Mazama 7,700 years ago — the Klamath tribe recorded the event in oral tradition. Mount Shasta is a focus of Native American prophecy and modern interdimensional contact claims. Sedona's documented electromagnetic vortexes sit at the alignment's midpoint. The line terminates at Chichen Itza, the great Mayan pyramid astronomically aligned to the equinox serpent shadow.",
        "points": [
            [45.5, -125.0],       # Pacific Ocean extension north
            [42.9127, -122.0722], # Crater Lake, OR
            [41.4092, -122.1949], # Mount Shasta, CA
            [36.2, -117.0],       # Death Valley / Panamint intersection
            [34.8697, -111.7610], # Sedona, AZ
            [20.6843,  -88.5678], # Chichen Itza, Mexico
            [15.0,    -90.0],     # Central America extension
        ],
        "waypoints": [
            {"name": "Crater Lake", "lat": 42.9127, "lon": -122.0722, "note": "Formed 7,700 years ago when Mt. Mazama collapsed after a cataclysmic eruption. The Klamath people recorded witnessing the event — one of the oldest direct observations of a geological event in history. USO sightings reported in the lake."},
            {"name": "Mount Shasta", "lat": 41.4092, "lon": -122.1949, "note": "Dormant stratovolcano considered sacred by multiple Native American tribes. Modern accounts describe Lemurian survivors living inside the mountain, interdimensional portals, and persistent UFO activity. Mt. Shasta has more reported UFO sightings per square mile than almost anywhere in the US."},
            {"name": "Sedona Vortexes", "lat": 34.8697, "lon": -111.7610, "note": "Four documented vortex sites with measurable electromagnetic anomalies. Airport Mesa, Cathedral Rock, Bell Rock, and Boynton Canyon. Unusual compass behavior, anomalous plant growth spiraling, and unusually high rates of psychic/contact experiences reported."},
            {"name": "Chichen Itza", "lat": 20.6843, "lon": -88.5678, "note": "El Castillo pyramid constructed so that on the spring and autumn equinoxes, the play of light and shadow creates the illusion of a feathered serpent descending the northern staircase. Built ca. 600–900 CE with astronomical precision that modern engineers struggle to replicate."},
        ],
    },
    {
        "name": "33rd Parallel Ley",
        "short": "33° PARALLEL LEY",
        "color": "#ff2244",
        "label_at": [33.2, -115.0],
        "description": "The 33rd degree of north latitude has been called the most mystically significant parallel on Earth. It passes through Roswell, Phoenix, Denton (FEMA COG headquarters), Baghdad (ancient Babylon), Hiroshima, Casablanca, and Bermuda. The number 33 is the highest degree of Scottish Rite Freemasonry. An extraordinary number of historically significant events have occurred at or near this latitude.",
        "points": [
            [33.0, -130.0],       # Pacific extension
            [33.4484, -112.0740], # Phoenix, AZ
            [33.3943, -104.5230], # Roswell, NM
            [33.2148,  -97.1331], # Denton, TX
            [32.7792,  -96.8089], # Dealey Plaza, Dallas TX
            [32.3078,  -64.7505], # Bermuda
            [33.5731,   -7.5898], # Casablanca, Morocco
            [33.3152,   44.3661], # Baghdad, Iraq
            [34.3853,  132.4553], # Hiroshima, Japan
            [33.5,     140.0],    # Pacific east extension
        ],
        "waypoints": [
            {"name": "Phoenix, AZ — Phoenix Lights", "lat": 33.4484, "lon": -112.0740, "note": "1997 Phoenix Lights: V-shaped craft reported by thousands including the Governor of Arizona. Mass sighting over a city of 1.5 million. Air Force claimed flares — witnesses say the craft was observed silently for over an hour before the flares were dropped."},
            {"name": "Roswell, NM", "lat": 33.3943, "lon": -104.5230, "note": "July 1947: debris from an unknown craft recovered by the Army Air Force. Initial press release stated 'flying disc' recovered. Retracted within hours. Witness testimonies of non-human bodies persisted for decades. RAAF was home to the world's only atomic bomb wing at the time of the crash."},
            {"name": "Denton, TX — FEMA Region 6", "lat": 33.2148, "lon": -97.1331, "note": "FEMA Region 6 headquarters and underground Continuity of Government facility at 33.2° N. The esoteric significance of this site on the 33rd parallel is noted by researchers of the Federal Arc network."},
            {"name": "Dealey Plaza, Dallas TX", "lat": 32.7792, "lon": -96.8089, "note": "JFK assassinated Nov 22, 1963 at 32.78°N — within the esoteric 33rd parallel band. Dallas hosts a major Scottish Rite Masonic Temple. The triple underpass at Dealey Plaza was the first Masonic temple site in Dallas."},
            {"name": "Bermuda Triangle (N vertex)", "lat": 32.3078, "lon": -64.7505, "note": "Northern vertex of the Bermuda Triangle. Over 75 aircraft and hundreds of ships have disappeared in this zone without explanation. The US Navy's AUTEC (Atlantic Undersea Test and Evaluation Center) operates classified underwater facilities in the area."},
            {"name": "Casablanca, Morocco", "lat": 33.5731, "lon": -7.5898, "note": "Ancient Phoenician port on the 33rd parallel. Site of the secret 1943 Casablanca Conference between Roosevelt and Churchill that shaped the post-war world. Roosevelt crossed the Atlantic specifically to meet at this latitude."},
            {"name": "Baghdad / Ancient Babylon", "lat": 33.3152, "lon": 44.3661, "note": "The world's first empire, first written law code, and first astronomical records were produced at 33°N. The Hanging Gardens, one of the Seven Wonders, stood here. Modern Baghdad is built directly atop ancient Babylon."},
            {"name": "Hiroshima, Japan", "lat": 34.3853, "lon": 132.4553, "note": "First atomic bomb dropped August 6, 1945 at 34.4°N. Nagasaki (second bomb, August 9) sits at 32.7°N. Both targets bracketing the 33rd parallel. The Hiroshima bomb was called 'Little Boy'; the Nagasaki bomb 'Fat Man' — the two names used by Freemasons for initiates."},
        ],
    },
    {
        "name": "Appalachian Mound Ley",
        "short": "APPALACHIAN LEY",
        "color": "#aaff44",
        "label_at": [36.8, -80.5],
        "description": "A north-south alignment proposed to connect the ancient Native American mound-builder civilizations of the American Southeast. Running along the eastern flanks of the Appalachian Mountains, this alignment passes through some of the most significant pre-Columbian earthwork complexes in North America. The Mississippian mound-builder culture (800–1600 CE) constructed hundreds of platform mounds across this corridor with astronomical alignments to solstices and equinoxes.",
        "points": [
            [30.5, -89.5],        # Gulf Coast extension
            [32.6373, -91.4059],  # Poverty Point, LA
            [34.2256, -84.7459],  # Etowah Mounds, GA
            [35.0367, -79.9836],  # Town Creek Mound, NC
            [39.0259, -83.4302],  # Serpent Mound, OH
            [39.9215, -80.7340],  # Grave Creek Mound, WV
            [40.0481, -82.4349],  # Newark Earthworks, OH
            [41.5, -81.0],        # Lake Erie extension
        ],
        "waypoints": [
            {"name": "Poverty Point", "lat": 32.6373, "lon": -91.4059, "note": "3,400-year-old earthwork complex in Louisiana — one of the largest prehistoric earthen constructions in North America. Six concentric C-shaped ridges spanning 3/4 mile diameter. Built by a hunter-gatherer society with no evidence of agriculture, contradicting conventional models of monument-building civilizations."},
            {"name": "Etowah Mounds", "lat": 34.2256, "lon": -84.7459, "note": "Major Mississippian ceremonial center (1000–1550 CE) in Georgia. Three platform mounds surrounding a central plaza. Remarkable carved marble effigies found here depict figures in trance or death postures — possibly shamanic ritual objects."},
            {"name": "Town Creek Mound", "lat": 35.0367, "lon": -79.9836, "note": "Pee Dee culture ceremonial mound in North Carolina (1100–1400 CE). Reconstructed temple mound surrounded by a palisade wall. Served as a regional religious center for towns across the Piedmont."},
            {"name": "Serpent Mound", "lat": 39.0259, "lon": -83.4302, "note": "The largest serpent effigy mound in the world. Built over a confirmed meteorite impact crater. Aligns with solstice and equinox astronomical events. The 'egg' being swallowed may represent the sun at summer solstice."},
            {"name": "Grave Creek Mound", "lat": 39.9215, "lon": -80.7340, "note": "Largest conical burial mound of the Adena culture (250–150 BCE), standing 62 feet high. A controversial inscribed sandstone tablet found inside contains symbols resembling ancient Iberian and Canaanite scripts, suggesting possible pre-Columbian trans-Atlantic contact."},
            {"name": "Newark Earthworks", "lat": 40.0481, "lon": -82.4349, "note": "Hopewell culture (100 BCE–500 CE) geometric earthworks covering 4 square miles — the largest set of geometric earthen enclosures in the world. Precise circles and octagons aligned to the 18.6-year lunar standstill cycle. A Masonic lodge was built atop the Great Circle in the 19th century."},
        ],
    },
    {
        "name": "UK–Atlantic Ley",
        "short": "UK–ATLANTIC LEY",
        "color": "#ffaa00",
        "label_at": [47.0, -30.0],
        "description": "The proposed trans-Atlantic extension of the St. Michael's Ley Line — England's most famous sacred alignment. Running from St. Michael's Mount in Cornwall through Glastonbury and Stonehenge, the line continues across the Atlantic through the Azores archipelago (itself possibly a remnant of the sunken continent of Atlantis, according to Plato's description) and on toward the Caribbean and Mesoamerica. The Azores sit on the mid-Atlantic ridge — geologically the boundary between two tectonic plates.",
        "points": [
            [50.1174, -5.5148],   # St. Michael's Mount, Cornwall
            [51.1444, -2.7161],   # Glastonbury Tor
            [51.4285, -1.8544],   # Avebury Stone Circle
            [51.1789, -1.8262],   # Stonehenge
            [47.0,   -20.0],      # Mid-Atlantic
            [37.7412, -25.6756],  # Azores (Ponta Delgada)
            [32.3078, -64.7505],  # Bermuda
            [25.0,   -77.5],      # Bahamas / Bimini
            [20.6843, -88.5678],  # Chichen Itza, Mexico
        ],
        "waypoints": [
            {"name": "St. Michael's Mount", "lat": 50.1174, "lon": -5.5148, "note": "Tidal island accessible only at low tide, topped by a medieval castle. Mirrors Mont Saint-Michel in Normandy almost exactly — same dedication, same tidal island format, same latitude difference. Both sit on the St. Michael alignment."},
            {"name": "Glastonbury Tor", "lat": 51.1444, "lon": -2.7161, "note": "Possible site of ancient Avalon. Joseph of Arimathea allegedly brought the Holy Grail here. The hill has seven terraces that may be remnants of a three-dimensional labyrinth. Anomalous EMF readings documented at the summit."},
            {"name": "Avebury Stone Circle", "lat": 51.4285, "lon": -1.8544, "note": "Largest stone circle in the world — so large an entire village exists inside it. 2600 BCE. The nearby Silbury Hill (130 feet, 5 million cubic feet of chalk) is Europe's largest prehistoric mound and its purpose remains entirely unknown."},
            {"name": "Stonehenge", "lat": 51.1789, "lon": -1.8262, "note": "Construction began ~3000 BCE. The 80 bluestones were transported 200+ miles from Wales — a feat that mystifies modern engineers. Precisely aligned with summer solstice sunrise and winter solstice sunset. The outer sarsen stones weigh up to 25 tons each."},
            {"name": "Azores — Possible Atlantis", "lat": 37.7412, "lon": -25.6756, "note": "The Azores sit on the mid-Atlantic ridge at the junction of three tectonic plates — exactly where Plato described Atlantis ('beyond the Pillars of Hercules'). Submerged megalithic-looking formations have been reported off the coasts of several Azorean islands. Geologically the most active volcanic zone in the Atlantic."},
            {"name": "Bimini Road", "lat": 25.7, "lon": -79.3, "note": "Underwater formation of large rectangular limestone blocks discovered off North Bimini, Bahamas in 1968 — the same year Edgar Cayce predicted a remnant of Atlantis would surface. Mainstream geology calls it a natural beachrock formation. Alternative researchers note the stones' near-perfect rectangular joints and apparent road-like arrangement."},
            {"name": "Chichen Itza", "lat": 20.6843, "lon": -88.5678, "note": "Terminal point of the proposed Atlantic ley. El Castillo pyramid's equinox serpent-shadow phenomenon requires astronomical knowledge refined over centuries. The sacred cenote (limestone sinkhole) here was used for ritual offerings — including human sacrifice — to the rain god Chaac."},
        ],
    },
]

# ── US Military Installations ─────────────────────────────────
MILITARY_BASES = [
    # Army
    {"name": "Fort Liberty (Bragg)",           "branch": "Army",        "state": "NC", "lat": 35.1397, "lon": -79.0060},
    {"name": "Fort Campbell",                  "branch": "Army",        "state": "KY", "lat": 36.6643, "lon": -87.4714},
    {"name": "Fort Cavazos (Hood)",            "branch": "Army",        "state": "TX", "lat": 31.1354, "lon": -97.7810},
    {"name": "Fort Moore (Benning)",           "branch": "Army",        "state": "GA", "lat": 32.3617, "lon": -84.9549},
    {"name": "Fort Stewart",                   "branch": "Army",        "state": "GA", "lat": 31.8696, "lon": -81.6087},
    {"name": "Fort Carson",                    "branch": "Army",        "state": "CO", "lat": 38.7340, "lon": -104.7854},
    {"name": "Fort Riley",                     "branch": "Army",        "state": "KS", "lat": 39.0750, "lon": -96.8003},
    {"name": "Fort Drum",                      "branch": "Army",        "state": "NY", "lat": 44.0537, "lon": -75.7732},
    {"name": "Fort Wainwright",                "branch": "Army",        "state": "AK", "lat": 64.8278, "lon": -147.6536},
    {"name": "Fort Bliss",                     "branch": "Army",        "state": "TX", "lat": 31.8127, "lon": -106.4198},
    {"name": "Fort Sill",                      "branch": "Army",        "state": "OK", "lat": 34.6717, "lon": -98.3989},
    {"name": "Fort Leonard Wood",              "branch": "Army",        "state": "MO", "lat": 37.7209, "lon": -92.1386},
    {"name": "Fort Huachuca",                  "branch": "Army",        "state": "AZ", "lat": 31.5495, "lon": -110.3454},
    {"name": "Fort Irwin (NTC)",               "branch": "Army",        "state": "CA", "lat": 35.2627, "lon": -116.6838},
    {"name": "Fort Knox",                      "branch": "Army",        "state": "KY", "lat": 37.8977, "lon": -85.9631},
    {"name": "Fort Leavenworth",               "branch": "Army",        "state": "KS", "lat": 39.3614, "lon": -94.9244},
    {"name": "Fort Gregg-Adams (Lee)",         "branch": "Army",        "state": "VA", "lat": 37.2381, "lon": -77.3283},
    {"name": "Fort Eisenhower (Gordon)",       "branch": "Army",        "state": "GA", "lat": 33.4199, "lon": -82.1513},
    {"name": "Fort Sam Houston",               "branch": "Army",        "state": "TX", "lat": 29.4449, "lon": -98.4398},
    {"name": "Redstone Arsenal",               "branch": "Army",        "state": "AL", "lat": 34.6788, "lon": -86.6480},
    {"name": "White Sands Missile Range",      "branch": "Army",        "state": "NM", "lat": 32.3836, "lon": -106.4829},
    {"name": "Dugway Proving Ground",          "branch": "Army",        "state": "UT", "lat": 40.1619, "lon": -112.9380},
    {"name": "Yuma Proving Ground",            "branch": "Army",        "state": "AZ", "lat": 32.4942, "lon": -114.3494},
    {"name": "Aberdeen Proving Ground",        "branch": "Army",        "state": "MD", "lat": 39.4615, "lon": -76.1305},
    # Navy
    {"name": "NAS Norfolk (Joint Base)",       "branch": "Navy",        "state": "VA", "lat": 36.9476, "lon": -76.3290},
    {"name": "Naval Base San Diego",           "branch": "Navy",        "state": "CA", "lat": 32.6858, "lon": -117.1360},
    {"name": "Joint Base Pearl Harbor-Hickam", "branch": "Navy",        "state": "HI", "lat": 21.3618, "lon": -157.9719},
    {"name": "Naval Base Kitsap (Bremerton)",  "branch": "Navy",        "state": "WA", "lat": 47.5596, "lon": -122.6276},
    {"name": "NAS Jacksonville",               "branch": "Navy",        "state": "FL", "lat": 30.2352, "lon": -81.6783},
    {"name": "NAS Pensacola",                  "branch": "Navy",        "state": "FL", "lat": 30.3535, "lon": -87.3186},
    {"name": "NAS Patuxent River",             "branch": "Navy",        "state": "MD", "lat": 38.2843, "lon": -76.4117},
    {"name": "NAS Oceana",                     "branch": "Navy",        "state": "VA", "lat": 36.8201, "lon": -76.0335},
    {"name": "NAS Lemoore",                    "branch": "Navy",        "state": "CA", "lat": 36.3332, "lon": -119.9523},
    {"name": "NAS Whidbey Island",             "branch": "Navy",        "state": "WA", "lat": 48.3519, "lon": -122.6557},
    {"name": "Naval Station Everett",          "branch": "Navy",        "state": "WA", "lat": 47.9982, "lon": -122.2218},
    {"name": "NAS Fallon",                     "branch": "Navy",        "state": "NV", "lat": 39.4166, "lon": -118.7006},
    {"name": "NAS Point Mugu",                 "branch": "Navy",        "state": "CA", "lat": 34.1170, "lon": -119.1209},
    {"name": "Naval Base Ventura County",      "branch": "Navy",        "state": "CA", "lat": 34.1700, "lon": -119.1100},
    {"name": "China Lake NAWS",                "branch": "Navy",        "state": "CA", "lat": 35.6854, "lon": -117.6918},
    {"name": "NAS Corpus Christi",             "branch": "Navy",        "state": "TX", "lat": 27.6954, "lon": -97.2861},
    {"name": "NAS Meridian",                   "branch": "Navy",        "state": "MS", "lat": 32.5537, "lon": -88.5562},
    {"name": "NAS Kingsville",                 "branch": "Navy",        "state": "TX", "lat": 27.5072, "lon": -97.8097},
    # Marine Corps
    {"name": "Camp Lejeune",                   "branch": "Marines",     "state": "NC", "lat": 34.6581, "lon": -77.3400},
    {"name": "Camp Pendleton",                 "branch": "Marines",     "state": "CA", "lat": 33.3744, "lon": -117.4494},
    {"name": "MCB Quantico",                   "branch": "Marines",     "state": "VA", "lat": 38.5235, "lon": -77.3541},
    {"name": "MCAS Cherry Point",              "branch": "Marines",     "state": "NC", "lat": 34.9003, "lon": -76.8804},
    {"name": "MCAS Miramar",                   "branch": "Marines",     "state": "CA", "lat": 32.8690, "lon": -117.1426},
    {"name": "MCAS Kaneohe Bay",               "branch": "Marines",     "state": "HI", "lat": 21.4497, "lon": -157.7680},
    {"name": "MCAGCC Twentynine Palms",        "branch": "Marines",     "state": "CA", "lat": 34.2992, "lon": -116.0628},
    {"name": "MCAS Beaufort",                  "branch": "Marines",     "state": "SC", "lat": 32.4774, "lon": -80.7232},
    {"name": "MCAS Yuma",                      "branch": "Marines",     "state": "AZ", "lat": 32.6566, "lon": -114.6157},
    {"name": "Camp Butler (Okinawa)",          "branch": "Marines",     "state": "HI", "lat": 26.3010, "lon": 127.7680},
    # Air Force
    {"name": "Edwards AFB",                    "branch": "Air Force",   "state": "CA", "lat": 34.9054, "lon": -117.8838},
    {"name": "Wright-Patterson AFB",           "branch": "Air Force",   "state": "OH", "lat": 39.8260, "lon": -84.0482},
    {"name": "Nellis AFB",                     "branch": "Air Force",   "state": "NV", "lat": 36.2358, "lon": -115.0340},
    {"name": "Joint Base Langley-Eustis",      "branch": "Air Force",   "state": "VA", "lat": 37.0829, "lon": -76.3598},
    {"name": "Eglin AFB",                      "branch": "Air Force",   "state": "FL", "lat": 30.4832, "lon": -86.5253},
    {"name": "Tinker AFB",                     "branch": "Air Force",   "state": "OK", "lat": 35.4147, "lon": -97.3866},
    {"name": "Barksdale AFB",                  "branch": "Air Force",   "state": "LA", "lat": 32.5018, "lon": -93.6627},
    {"name": "Whiteman AFB",                   "branch": "Air Force",   "state": "MO", "lat": 38.7277, "lon": -93.5479},
    {"name": "Dyess AFB",                      "branch": "Air Force",   "state": "TX", "lat": 32.4208, "lon": -99.8548},
    {"name": "Ellsworth AFB",                  "branch": "Air Force",   "state": "SD", "lat": 44.1455, "lon": -103.1014},
    {"name": "Minot AFB",                      "branch": "Air Force",   "state": "ND", "lat": 48.4157, "lon": -101.3580},
    {"name": "Malmstrom AFB",                  "branch": "Air Force",   "state": "MT", "lat": 47.5096, "lon": -111.1863},
    {"name": "F.E. Warren AFB",                "branch": "Air Force",   "state": "WY", "lat": 41.1456, "lon": -104.8694},
    {"name": "Offutt AFB",                     "branch": "Air Force",   "state": "NE", "lat": 41.1181, "lon": -95.9125},
    {"name": "Joint Base Andrews",             "branch": "Air Force",   "state": "MD", "lat": 38.8108, "lon": -76.8669},
    {"name": "Joint Base McGuire-Dix-Lakehurst","branch": "Air Force",  "state": "NJ", "lat": 40.0156, "lon": -74.5934},
    {"name": "Dover AFB",                      "branch": "Air Force",   "state": "DE", "lat": 39.1295, "lon": -75.4665},
    {"name": "Seymour Johnson AFB",            "branch": "Air Force",   "state": "NC", "lat": 35.3394, "lon": -77.9607},
    {"name": "Shaw AFB",                       "branch": "Air Force",   "state": "SC", "lat": 33.9727, "lon": -80.4731},
    {"name": "Moody AFB",                      "branch": "Air Force",   "state": "GA", "lat": 30.9674, "lon": -83.1931},
    {"name": "Tyndall AFB",                    "branch": "Air Force",   "state": "FL", "lat": 30.0783, "lon": -85.6083},
    {"name": "MacDill AFB",                    "branch": "Air Force",   "state": "FL", "lat": 27.8493, "lon": -82.5213},
    {"name": "Robins AFB",                     "branch": "Air Force",   "state": "GA", "lat": 32.6400, "lon": -83.5919},
    {"name": "Maxwell AFB",                    "branch": "Air Force",   "state": "AL", "lat": 32.3824, "lon": -86.3663},
    {"name": "Keesler AFB",                    "branch": "Air Force",   "state": "MS", "lat": 30.4113, "lon": -88.9239},
    {"name": "Columbus AFB",                   "branch": "Air Force",   "state": "MS", "lat": 33.6438, "lon": -88.4455},
    {"name": "Laughlin AFB",                   "branch": "Air Force",   "state": "TX", "lat": 29.3593, "lon": -100.7788},
    {"name": "JBSA Randolph",                  "branch": "Air Force",   "state": "TX", "lat": 29.5297, "lon": -98.2791},
    {"name": "Sheppard AFB",                   "branch": "Air Force",   "state": "TX", "lat": 33.9844, "lon": -98.8306},
    {"name": "Cannon AFB",                     "branch": "Air Force",   "state": "NM", "lat": 34.3828, "lon": -103.3218},
    {"name": "Holloman AFB",                   "branch": "Air Force",   "state": "NM", "lat": 32.8530, "lon": -106.1078},
    {"name": "Kirtland AFB",                   "branch": "Air Force",   "state": "NM", "lat": 35.0454, "lon": -106.5485},
    {"name": "Davis-Monthan AFB",              "branch": "Air Force",   "state": "AZ", "lat": 32.1665, "lon": -110.8834},
    {"name": "Luke AFB",                       "branch": "Air Force",   "state": "AZ", "lat": 33.5350, "lon": -112.3832},
    {"name": "Travis AFB",                     "branch": "Air Force",   "state": "CA", "lat": 38.2628, "lon": -121.9269},
    {"name": "Beale AFB",                      "branch": "Air Force",   "state": "CA", "lat": 39.1361, "lon": -121.4367},
    {"name": "Hill AFB",                       "branch": "Air Force",   "state": "UT", "lat": 41.1240, "lon": -111.9732},
    {"name": "Mountain Home AFB",              "branch": "Air Force",   "state": "ID", "lat": 43.0436, "lon": -115.8724},
    {"name": "Fairchild AFB",                  "branch": "Air Force",   "state": "WA", "lat": 47.6151, "lon": -117.6558},
    {"name": "Joint Base Lewis-McChord",       "branch": "Air Force",   "state": "WA", "lat": 47.1377, "lon": -122.4758},
    {"name": "Joint Base Elmendorf-Richardson","branch": "Air Force",   "state": "AK", "lat": 61.2534, "lon": -149.7967},
    {"name": "Eielson AFB",                    "branch": "Air Force",   "state": "AK", "lat": 64.6657, "lon": -147.1021},
    {"name": "Hanscom AFB",                    "branch": "Air Force",   "state": "MA", "lat": 42.4610, "lon": -71.2868},
    {"name": "Selfridge ANGB",                 "branch": "Air Force",   "state": "MI", "lat": 42.6083, "lon": -82.8358},
    {"name": "Grand Forks AFB",                "branch": "Air Force",   "state": "ND", "lat": 47.9611, "lon": -97.3762},
    {"name": "Goodfellow AFB",                 "branch": "Air Force",   "state": "TX", "lat": 31.4237, "lon": -100.3974},
    # Space Force
    {"name": "Peterson SFB",                   "branch": "Space Force", "state": "CO", "lat": 38.8194, "lon": -104.7007},
    {"name": "Schriever SFB",                  "branch": "Space Force", "state": "CO", "lat": 38.8044, "lon": -104.5286},
    {"name": "Cheyenne Mountain SFS",          "branch": "Space Force", "state": "CO", "lat": 38.7443, "lon": -104.8462},
    {"name": "Patrick SFB",                    "branch": "Space Force", "state": "FL", "lat": 28.2348, "lon": -80.6103},
    {"name": "Vandenberg SFB",                 "branch": "Space Force", "state": "CA", "lat": 34.7420, "lon": -120.5724},
    {"name": "Los Angeles AFB (SFB)",          "branch": "Space Force", "state": "CA", "lat": 33.9169, "lon": -118.3884},
    {"name": "Buckley SFB",                    "branch": "Space Force", "state": "CO", "lat": 39.7177, "lon": -104.7514},
    # Special / Notable
    {"name": "Area 51 / Groom Lake",           "branch": "Special",     "state": "NV", "lat": 37.2350, "lon": -115.8111},
    {"name": "HAARP Research Station",         "branch": "Special",     "state": "AK", "lat": 62.3934, "lon": -145.1521},
    {"name": "Tonopah Test Range",             "branch": "Special",     "state": "NV", "lat": 37.7980, "lon": -116.7810},
]

# ── Continuity of Government Sites ────────────────────────────
_ARC = (" Part of the 'Federal Arc' — the roughly 300-mile ring of hardened COG facilities"
        " surrounding Washington D.C., designed to ensure government survival after a"
        " nuclear strike on the capital.")

COG_SITES = [
    # East Coast / Federal Arc
    {"name": "Mount Weather Emergency Operations Center",
     "location": "Bluemont, Virginia", "lat": 39.0631, "lon": -77.8897,
     "description": "Primary federal government relocation site operated by FEMA. Houses the President, Cabinet, and Supreme Court during national emergencies. Features underground command facilities, emergency broadcast systems, and a self-contained community capable of supporting 2,000 people indefinitely. Known internally as 'High Point Special Facility'." + _ARC},
    {"name": "Raven Rock Mountain Complex (Site R)",
     "location": "Blue Ridge Summit, Pennsylvania", "lat": 39.7196, "lon": -77.4610,
     "description": "The 'Underground Pentagon' — the DoD's alternate national military command center carved into Raven Rock Mountain. Operational since 1953, it can sustain military command operations after a nuclear strike. Vice President Cheney was taken here on 9/11. Capacity for ~1,400 personnel." + _ARC},
    {"name": "The Greenbrier Bunker (Project Greek Island)",
     "location": "White Sulphur Springs, West Virginia", "lat": 37.7882, "lon": -80.2956,
     "description": "Secret congressional relocation facility hidden beneath the luxury Greenbrier resort. Built in 1962 and kept classified for 30 years until exposed by the Washington Post in 1992. Could shelter all 535 members of Congress for months. Now decommissioned and open for public tours." + _ARC},
    {"name": "Fort Ritchie / Alternate National Military Command Center",
     "location": "Cascade, Maryland", "lat": 39.7243, "lon": -77.4797,
     "description": "Cold War-era alternate National Military Command Center at Fort Ritchie. Served as a backup command post for the Pentagon, linked to Raven Rock via secure communications. Closed in 1998 under BRAC but its underground facilities were considered among the most secure in the country." + _ARC},
    {"name": "Sugar Grove SIGINT Station",
     "location": "Sugar Grove, West Virginia", "lat": 38.5196, "lon": -79.2776,
     "description": "NSA signals intelligence facility and reported COG communications relay site. Located in a National Radio Quiet Zone. Operated massive dish antennas for intercepting satellite communications. Closed in 2015 and transferred to the Green Bank Observatory." + _ARC},
    {"name": "OPM Federal Records Center (Boyers Bunker)",
     "location": "Boyers, Pennsylvania", "lat": 41.0990, "lon": -79.8788,
     "description": "Underground federal records facility built inside a former limestone mine. Stores over 56 million federal employee personnel files. Also designated as a COG site. Employs ~600 federal workers operating underground daily." + _ARC},
    {"name": "Peters Mountain Relay Station",
     "location": "Millboro, Virginia", "lat": 37.9215, "lon": -79.5407,
     "description": "Hardened emergency communications relay station on Peters Mountain, part of the Cold War Minimum Essential Emergency Communications Network (MEECN). Designed to maintain presidential command-and-control over nuclear forces even after a first strike." + _ARC},
    {"name": "Mount Pony / Federal Reserve Bunker",
     "location": "Culpeper, Virginia", "lat": 38.5001, "lon": -78.0001,
     "description": "Cold War-era Federal Reserve continuity facility. Stored $4 billion in currency to stabilize the economy after a nuclear attack. Declassified and decommissioned in 1988; now the Library of Congress Packard Campus for Audio Visual Conservation." + _ARC},
    {"name": "Brandywine / FEMA COG Relay Site",
     "location": "Upper Marlboro, Maryland", "lat": 38.8012, "lon": -76.7497,
     "description": "FEMA emergency broadcast and communications relay facility serving the National Capital Region. Part of the Emergency Alert System infrastructure with a COG role." + _ARC},
    {"name": "Olney Federal Complex",
     "location": "Olney, Maryland", "lat": 39.1537, "lon": -77.0697,
     "description": "Federal government alternate operations complex north of Washington D.C. Used by multiple agencies as a continuity of operations site." + _ARC},
    {"name": "Blue Ridge Arsenal / Viewtree Mountain Site",
     "location": "Bentonville, Virginia", "lat": 38.9957, "lon": -78.3249,
     "description": "Reported hardened government facility along the Blue Ridge Mountains. Served as a communications and command relay node in the federal government's Cold War survival network." + _ARC},
    {"name": "Isolated Communications Outlet — Chatham, VA",
     "location": "Chatham, Virginia", "lat": 36.8237, "lon": -79.4025,
     "description": "Hardened Emergency Action Message relay site, part of the Navy's TACAMO ground network for communicating with ballistic missile submarines. Designed to survive EMP and transmit emergency nuclear launch orders." + _ARC},
    {"name": "Alternate Joint Communications Center (AJCC)",
     "location": "Fort Detrick, Maryland", "lat": 39.4311, "lon": -77.4183,
     "description": "DISA alternate joint communications center at Fort Detrick. Provides continuity for critical DoD networks. Fort Detrick also houses USAMRIID, relevant to biological COG planning." + _ARC},
    # National / Non-East-Coast
    {"name": "Cheyenne Mountain Complex",
     "location": "Colorado Springs, Colorado", "lat": 38.7443, "lon": -104.8462,
     "description": "NORAD and USNORTHCOM alternate command center buried 2,000 feet inside a granite mountain. Built to survive a nearby nuclear detonation. Buildings are mounted on 1,319 giant steel springs to absorb blast shock."},
    {"name": "Offutt AFB — STRATCOM Underground Command",
     "location": "Bellevue, Nebraska", "lat": 41.1181, "lon": -95.9125,
     "description": "Home of US Strategic Command (USSTRATCOM). Features a hardened underground command post capable of directing nuclear forces independently of Washington D.C. President George W. Bush was diverted here on 9/11."},
    {"name": "Denver International Airport — Underground Facilities",
     "location": "Denver, Colorado", "lat": 39.8561, "lon": -104.6737,
     "description": "DIA's vast underground infrastructure has fueled widespread COG speculation. Features 5 levels of underground tunnels, blast-resistant construction, and its own water and fuel systems. Proximity to NORAD and Cheyenne Mountain makes it a persistent subject of continuity planning discussions."},
    {"name": "FEMA Region 6 Underground Bunker",
     "location": "Denton, Texas", "lat": 33.2148, "lon": -97.1331,
     "description": "Declassified FEMA regional emergency operations bunker serving TX, NM, OK, AR, and LA. Designed to maintain continuity of federal emergency management operations during a catastrophic national event."},
]

# ── USO Sites ─────────────────────────────────────────────────
USO_SITES = [
    {"name": "Laguna Cartagena",
     "location": "Lajas, Puerto Rico", "lat": 17.9897, "lon": -67.1358,
     "description": "One of the most active USO hotspots in the world. Hundreds of reported incidents since the 1980s with objects entering and exiting the lagoon at high speed. Sits within the 'Bermuda Triangle of the Caribbean' corridor."},
    {"name": "Shag Harbour Incident Site",
     "location": "Shag Harbour, Nova Scotia, Canada", "lat": 43.4706, "lon": -65.7417,
     "description": "On October 4, 1967, multiple witnesses including RCMP officers observed an unidentified object crash into the ocean. Canadian and US naval assets conducted an underwater search but no wreckage was recovered. Officially recorded in Canadian government files."},
    {"name": "Point Dume Underwater Anomaly",
     "location": "Malibu, California", "lat": 34.0003, "lon": -118.9500,
     "description": "A large oval structure ~2,000 feet below the surface identified in Google Earth sonar imagery. Roughly 3 miles wide with apparent support pillars and a flat top. Long history of USO sightings with objects entering and exiting the Pacific Ocean."},
    {"name": "Santa Catalina Island USO Zone",
     "location": "Catalina Island, California", "lat": 33.3894, "lon": -118.4168,
     "description": "Persistent USO hotspot for decades. Commercial fishermen, Navy personnel, and civilians have reported glowing objects at extraordinary speeds above and below water. A 1992 incident involved multiple US Navy witnesses observing a large object launch from the water."},
    {"name": "Baltic Sea Anomaly",
     "location": "Baltic Sea, between Sweden and Finland", "lat": 58.3000, "lon": 19.5700,
     "description": "Discovered by Ocean X in 2011 using sonar. A roughly circular object ~60 meters in diameter at 85 meters depth with a 300-meter skid mark. All electronic equipment on the dive boat reportedly failed within 200 meters of the object."},
    {"name": "Gulf of Mexico USO Corridor",
     "location": "Gulf of Mexico", "lat": 25.5000, "lon": -89.5000,
     "description": "Sustained USO reports from offshore oil platform workers, fishing vessels, and military aircraft. Objects emerging from depths exceeding 14,000 feet at speeds impossible for known craft. Several incidents involve objects reportedly circling drilling platforms."},
    {"name": "Bermuda Triangle / Atlantic USO Zone",
     "location": "North Atlantic Ocean", "lat": 25.0000, "lon": -71.0000,
     "description": "Hundreds of USO reports alongside the region's well-known disappearances. US Navy submarines have reportedly encountered objects moving at speeds far exceeding any known submerged vessel. The Puerto Rico Trench reaches nearly 28,000 feet — the deepest point in the Atlantic."},
    {"name": "Bering Sea USO Corridor",
     "location": "Bering Sea, Alaska", "lat": 57.0000, "lon": -178.0000,
     "description": "Cold War US and Soviet naval operations produced numerous classified USO encounter reports. Objects tracked at 150–200 knots at crush depths. Declassified Soviet reports describe USOs circling submarines and departing at extraordinary speed."},
    {"name": "Lake Champlain USO Reports",
     "location": "Burlington, Vermont", "lat": 44.4759, "lon": -73.2121,
     "description": "Lake Champlain has generated serious USO reports alongside the legendary 'Champ' creature. Large luminous objects described entering and exiting the lake. The lake reaches 400 feet deep and connects to the St. Lawrence Seaway."},
]

# ── Water & Aquifer Anomaly Sites ─────────────────────────────
# Surface water bodies known for UAP/anomalous activity + major US aquifers
WATER_ANOMALY_SITES = [
    # ── Surface water / UAP-active bodies ────────────────────
    {"name": "Puget Sound", "lat": 47.6062, "lon": -122.3321, "location": "Washington State",
     "type": "water", "description": "Broad inland sea with an unusually high concentration of USO and UAP sightings. Numerous reports of luminous objects entering and exiting the Sound. Proximity to Naval Station Kitsap (home of the largest US nuclear submarine fleet) and Boeing's aerospace facilities adds strategic significance."},
    {"name": "Columbia River", "lat": 45.6021, "lon": -122.5000, "location": "Oregon/Washington",
     "type": "water", "description": "Major river corridor with persistent UAP reports along its length from the Cascade headwaters to the Pacific. Multiple reports of glowing objects tracking the river at low altitude. The Hanford Nuclear Site sits directly on the Columbia — one of the most contaminated nuclear sites on Earth."},
    {"name": "Lake Erie", "lat": 41.8780, "lon": -81.5000, "location": "Ohio/Pennsylvania",
     "type": "water", "description": "Lake Erie has generated more consistent UFO/USO reports than any other Great Lake. Luminous objects described hovering over the water and making sharp maneuvers. The 1988 Eastlake, Ohio sighting was witnessed by multiple police officers. Objects frequently reported rising from and descending into the lake."},
    {"name": "Lake Michigan", "lat": 43.8000, "lon": -87.0000, "location": "Illinois/Michigan",
     "type": "water", "description": "Site of the famous 1994 mass sighting tracked by FAA radar and observed by multiple witnesses across four states simultaneously. Triangular and boomerang-shaped craft reported over the lake surface. Chicago's location at the southern tip creates an urban observation advantage."},
    {"name": "Flathead Lake", "lat": 47.8800, "lon": -114.1300, "location": "Montana",
     "type": "water", "description": "Largest natural freshwater lake west of the Mississippi. Persistent reports of large serpentine creatures and submerged luminous objects. Located in the Montana triangle of anomalous phenomena. Blackfeet and Salish tribal traditions describe powerful water spirits associated with the lake."},
    {"name": "Lake Tahoe", "lat": 39.0968, "lon": -120.0324, "location": "California/Nevada",
     "type": "water", "description": "At 1,645 feet deep, one of the deepest lakes in North America. Persistent reports of large unidentified submerged objects and divers encountering unusual phenomena. The lake never fully freezes and its deepest sections are poorly mapped. Multiple reports of luminous craft emerging from the surface."},
    {"name": "Crater Lake", "lat": 42.9127, "lon": -122.1428, "location": "Oregon",
     "type": "water", "description": "Formed 7,700 years ago when Mt. Mazama collapsed after a cataclysmic eruption witnessed by the Klamath people — one of the oldest recorded geological observations in history. At 1,943 feet, the deepest lake in the US. Multiple USO reports including glowing objects entering the lake. The lake has no surface inflows or outflows — its water source is entirely precipitation."},
    {"name": "Great Salt Lake", "lat": 40.7700, "lon": -112.3800, "location": "Utah",
     "type": "water", "description": "Hypersaline remnant of ancient Lake Bonneville, which once covered much of the Great Basin. Multiple UAP reports over the lake surface and nearby salt flats. Hill Air Force Base is immediately adjacent. The Dugway Proving Ground — sometimes called 'Area 52' — lies 85 miles to the southwest. Unusual atmospheric phenomena common over the highly reflective salt surface."},
    {"name": "Lake Champlain", "lat": 44.4759, "lon": -73.2121, "location": "Vermont/New York",
     "type": "water", "description": "Famous for 'Champ,' a lake creature with over 300 documented sightings since 1609, and persistent UAP activity. Sandra Mansi photographed an alleged creature in 1977. The lake sits in a glacially carved basin 400 feet deep. Multiple reports of luminous spheres rising from and entering the water. The lake connects to the St. Lawrence Seaway via the Richelieu River."},
    {"name": "Paulina Lake", "lat": 43.7165, "lon": -121.2589, "location": "Oregon",
     "type": "water", "description": "Volcanic caldera lake in Newberry Volcano. Persistent reports of anomalous lights and submerged glowing objects. Sits within one of the largest shield volcanos in the US. The Newberry Volcano caldera is geothermally active with drilling projects accessing very high subsurface temperatures. Located in a zone of elevated UAP activity on the Pacific Crest corridor."},
    {"name": "Lake Okanagan", "lat": 49.8851, "lon": -119.4960, "location": "British Columbia, Canada",
     "type": "water", "description": "Home of 'Ogopogo,' a lake creature with deep roots in Syilx First Nations tradition (N'ha-a-itk, the lake demon). 200+ modern sightings. The lake is 84 miles long and 761 feet deep — poorly explored in its lower reaches. Multiple photographs and video recordings of unidentified objects both on the surface and in the air above the lake."},
    {"name": "Loch Ness", "lat": 57.3229, "lon": -4.4244, "location": "Scotland",
     "type": "water", "description": "22 miles long, up to 755 feet deep, holding more fresh water than all lakes in England and Wales combined. The Nessie phenomenon dates to a 565 CE account by St. Columba. The loch's peat-darkened water limits visibility to inches, making comprehensive surveys impossible. UAP sightings above the loch correlate with creature reports. Robert Rines' 1972 and 1975 sonar contacts remain unexplained."},
    {"name": "Lake Titicaca", "lat": -15.8402, "lon": -69.3342, "location": "Peru/Bolivia",
     "type": "water", "description": "At 12,507 feet the world's highest navigable lake. Sacred to the Inca as the birthplace of the sun and the origin point of their civilization. Persistent UAP reports including a famous 2015 case videotaped by multiple witnesses. The submerged Inca ruins in Tiwanaku style have been documented at 60 feet depth. Local Uros people live on floating reed islands with traditions of sky beings."},
    # ── Major US aquifer systems ──────────────────────────────
    {"name": "Ogallala Aquifer (High Plains)", "lat": 38.5000, "lon": -101.0000,
     "location": "TX/OK/KS/NE/CO/WY/SD/ND", "type": "aquifer",
     "description": "The largest aquifer system in North America — 174,000 square miles underlaying 8 states. Up to 1,000 feet thick in Nebraska. Supplies 30% of all US groundwater used for irrigation. Recharges at a rate far slower than depletion — some zones are running dry within decades. The High Plains above it have some of the highest concentrations of cattle mutilation reports in the US. Several nuclear missile silo fields sit directly above the aquifer."},
    {"name": "Floridan Aquifer", "lat": 29.5000, "lon": -82.5000,
     "location": "Florida/Georgia/Alabama/South Carolina", "type": "aquifer",
     "description": "One of the most productive aquifer systems in the world, underlying 100,000 square miles. Water has been moving through this limestone system for millions of years — some zones contain water recharged during the last Ice Age. Florida's Gulf Coast is heavily associated with USO activity and this aquifer directly connects to numerous springs, sinkholes, and underwater cave systems that remain largely unexplored."},
    {"name": "Snake River Plain Aquifer", "lat": 43.5000, "lon": -114.0000,
     "location": "Idaho", "type": "aquifer",
     "description": "Vast basaltic aquifer underlying most of southern Idaho, recharged from the Lost River and Lemhi mountain ranges. The Snake River Plain is one of the most UAP-active regions in the western US. The Idaho National Laboratory (INL) — the US's primary nuclear research facility — sits directly above the aquifer. INL is home to the world's largest concentration of nuclear reactors (52 built on site). Multiple UAP reports cluster around INL facilities."},
    {"name": "Central Valley Aquifer", "lat": 36.7783, "lon": -119.4179,
     "location": "California", "type": "aquifer",
     "description": "Enormous aquifer system underlying California's 450-mile-long Central Valley, one of the world's most productive agricultural regions. Severe overdraft has caused the valley floor to sink as much as 28 feet in some locations. Edwards Air Force Base and China Lake Naval Air Weapons Station sit at the valley's southern end — two of the most restricted aerospace facilities in the US, with persistent UAP reports along the Sierra Nevada eastern escarpment directly above aquifer recharge zones."},
    {"name": "Spokane Valley–Rathdrum Prairie Aquifer", "lat": 47.8000, "lon": -117.0000,
     "location": "Eastern Washington/Northern Idaho", "type": "aquifer",
     "description": "CRITICAL HOTSPOT: This aquifer sits at the center of the identified Pacific Northwest UAP triangle. A massive gravel aquifer holding up to 10 trillion gallons, formed by Missoula Flood catastrophic outwash 13,000 years ago. The surface aquifer recharge zone directly overlaps with one of the densest UFO sighting clusters in the Pacific Northwest. Fairchild Air Force Base (heavy bomber and aerial refueling hub) sits directly above the western edge. Hanford Nuclear Site is 130 miles south. The 1947 Maury Island UFO incident — the first modern UFO case — occurred 30 miles west, and Kenneth Arnold's first flying saucer sighting was made 60 miles south over Mt. Rainier just days later."},
]