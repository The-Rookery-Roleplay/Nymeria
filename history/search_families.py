import re
import os

# Files to search
files = [
    r"characters\00_agot_char_north_ancestors.txt",
    r"characters\00_agot_char_north.txt",
]

# All families to search for
families = [
    "Stark", "Mormont", "Umber", "Karstark", "Glover", "Bolton", "Hornwood",
    "Locke", "Reed", "Dustin", "Ryswell", "Tallhart", "FisherSS", "Cerwyn",
    "Slate", "Ashwood", "Flint", "FlintWW", "FlintFF", "Woolfield",
    "Hide", "Beech", "Mollen", "Poole", "Weir", "Orcutt", "Sapp", "Burl",
    "Lurk", "Elliver", "Grayson", "Crook", "Hawley", "Reamy", "Riggwelt",
    "Holt", "Seaver", "Portan", "Nash", "Stilt", "Cray", "Croggen", "Flood",
    "Quagg", "Clay", "Strand", "Jeyne", "Fross", "Reaves", "Fog", "WellsN",
    "Spears", "Dronigan", "Long", "Caulfield", "Leadranack", "Slowburn",
    "Cairns", "Shale", "Aldcreek", "Cade", "Orlych", "Thaw", "Stump",
    "Sedge", "Lightfoot", "Mack", "Hume", "Rockhead", "Scrimshaw", "Tumbler",
    "Colt", "Condon", "Risk", "Barker", "Brummel", "Pinn", "Blackbrow",
    "Sully", "Catcher", "Greenleaf", "Harclay", "Knott", "Burley", "Liddle",
    "Norrey", "Kell", "Madden", "Wull", "Brewer", "Cantle", "Ironsmith",
    "Glenmore", "Somber", "Banks", "Bray", "Ryder", "Proud", "Darsett",
    "Branch", "Moss", "Woods", "Bole", "Howle", "Hartleaf", "Still",
    "Crowl", "Stane", "Frikrigg", "Mundrel", "Yggr", "Karn", "Magnar",
    "Barley", "Draywin", "Verran", "Stout", "Noll", "Mund", "Brownbarrow",
    "Porter", "Brent", "Bates", "Kiddle", "Herring", "Messer", "Wibberley",
    "Bywash", "Coaler", "Flade", "Overton", "Goodman", "Pale", "Dusk",
    "Broths", "Silverfield", "Shackes", "Marsh", "Hatchett", "Mazin", "Waterman"
]

def extract_char_blocks(content):
    """Parse CK3 character file into individual character blocks.
    Each block starts with 'ID = {' at column 0 (or with minimal indent)
    and ends with a matching closing brace.
    """
    blocks = []
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        # Match character definition start: "CharID = {"
        m = re.match(r'^(\w+)\s*=\s*\{', lines[i])
        if m:
            char_id = m.group(1)
            start_line = i
            brace_count = lines[i].count('{') - lines[i].count('}')
            block_lines = [lines[i]]
            i += 1
            while i < len(lines) and brace_count > 0:
                brace_count += lines[i].count('{') - lines[i].count('}')
                block_lines.append(lines[i])
                i += 1
            blocks.append((char_id, start_line + 1, '\n'.join(block_lines)))
        else:
            i += 1
    return blocks

results = {}

for filepath in files:
    full_path = os.path.join(os.path.dirname(__file__), filepath)
    with open(full_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    blocks = extract_char_blocks(content)
    
    for family in families:
        if family in results:
            continue
        
        dynn_pattern = re.compile(r'dynasty\s*=\s*dynn_' + re.escape(family) + r'\b')
        house_pattern = re.compile(r'dynasty_house\s*=\s*house_' + re.escape(family) + r'\b')
        
        for char_id, start_line, block_text in blocks:
            match_dynn = dynn_pattern.search(block_text)
            match_house = house_pattern.search(block_text)
            
            if match_dynn or match_house:
                dynasty_type = "dynasty" if match_dynn else "dynasty_house"
                dynasty_id = f"dynn_{family}" if match_dynn else f"house_{family}"
                
                culture = None
                religion = None
                
                cul_match = re.search(r'culture\s*=\s*(\S+)', block_text)
                rel_match = re.search(r'religion\s*=\s*(\S+)', block_text)
                if cul_match:
                    culture = cul_match.group(1)
                if rel_match:
                    religion = rel_match.group(1)
                
                results[family] = {
                    'culture': culture or 'NOT IN BLOCK',
                    'religion': religion or 'NOT IN BLOCK',
                    'dynasty_type': dynasty_type,
                    'dynasty_id': dynasty_id,
                    'file': os.path.basename(filepath),
                    'line': start_line,
                    'char_id': char_id,
                }
                break

# Print results as a table
print(f"{'Family':<18} {'Culture':<25} {'Dyn Type':<16} {'Dynasty ID':<25} {'Religion':<20} {'File'}")
print("-" * 130)

for family in families:
    if family in results:
        r = results[family]
        print(f"{family:<18} {r['culture']:<25} {r['dynasty_type']:<16} {r['dynasty_id']:<25} {r['religion']:<20} {r['file']}")
    else:
        print(f"{family:<18} {'*** NOT FOUND ***':<25} {'':<16} {'':<25} {'':<20}")

print(f"\nTotal families: {len(families)}")
print(f"Found: {len(results)}")
print(f"Not found: {len(families) - len(results)}")

not_found = [f for f in families if f not in results]
if not_found:
    print(f"\nNot found families: {', '.join(not_found)}")

# Summary of unique cultures
cultures = {}
for f, r in results.items():
    c = r['culture']
    if c not in cultures:
        cultures[c] = []
    cultures[c].append(f)

print("\n\n=== CULTURE SUMMARY ===")
for c in sorted(cultures.keys()):
    print(f"\n{c} ({len(cultures[c])} families):")
    print(f"  {', '.join(sorted(cultures[c]))}")

# Summary of unique religions
religions = {}
for f, r in results.items():
    rel = r['religion']
    if rel not in religions:
        religions[rel] = []
    religions[rel].append(f)

print("\n\n=== RELIGION SUMMARY ===")
for rel in sorted(religions.keys()):
    print(f"\n{rel} ({len(religions[rel])} families):")
    print(f"  {', '.join(sorted(religions[rel]))}")

# Dynasty type summary
print("\n\n=== DYNASTY TYPE SUMMARY ===")
dh = [f for f in families if f in results and results[f]['dynasty_type'] == 'dynasty_house']
print(f"dynasty_house ({len(dh)}): {', '.join(dh)}")
d = [f for f in families if f in results and results[f]['dynasty_type'] == 'dynasty']
print(f"dynasty ({len(d)}): all others ({len(d)} families)")
