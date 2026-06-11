
import json
import os
import glob

# Try to find the raw response dump for GetUsersRawInfos.
# The init dumps might not have it, but maybe there's a specific folder?
# Let's search all files in arena/ for the word "league" or "division"
import re
for root, dirs, files in os.walk('arena'):
    for file in files:
        if file.endswith('.json'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'league' in content.lower() or 'division' in content.lower():
                    print(f"Found match in {path}")
