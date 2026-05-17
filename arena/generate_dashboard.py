import json
import os
import glob

def generate():
    snaps_dir = "arena/snapshots"
    template_path = "arena/reports/template.html"
    output_path = "arena/reports/dashboard.html"
    
    if not os.path.exists(template_path):
        print("Template not found!")
        return

    # Load all snapshots
    all_snaps = {}
    # Make sure we use a robust glob and sorting
    snap_files = sorted(glob.glob(os.path.join(snaps_dir, "arena_*.json")))
    
    if not snap_files:
        print(f"No snapshot files found in {snaps_dir}")
        return

    for f in snap_files:
        try:
            with open(f, 'r', encoding='utf-8') as sf:
                data = json.load(sf)
                if 'timestamp' in data and 'players' in data:
                    all_snaps[data['timestamp']] = data
                else:
                    print(f"Warning: {f} has invalid structure.")
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    if not all_snaps:
        print("No valid snapshots data found.")
        return

    # Read template
    with open(template_path, 'r', encoding='utf-8') as tf:
        html = tf.read()
    
    # Inject data as a JSON string
    # We use a very direct replacement
    data_json = json.dumps(all_snaps, ensure_ascii=False)
    html = html.replace('SNAPSHOTS_DATA', data_json)
    
    # Save output
    with open(output_path, 'w', encoding='utf-8') as of:
        of.write(html)
        
    print(f"Dashboard generated: {output_path} with {len(all_snaps)} snapshots.")

if __name__ == "__main__":
    generate()
