import os

path = 'battle_analytics/generate_personal_stats.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("OUTPUT_FILE = os.path.join(ANALYTICS_DIR, 'personal_stats.html')", "OUTPUT_FILE = os.path.join(ANALYTICS_DIR, 'personal.html')")
text = text.replace('personal_stats.html', 'personal.html')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

deploy_path = 'deploy.py'
if os.path.exists(deploy_path):
    with open(deploy_path, 'r', encoding='utf-8') as f:
        deploy_text = f.read()
    deploy_text = deploy_text.replace('personal_stats.html', 'personal.html')
    with open(deploy_path, 'w', encoding='utf-8') as f:
        f.write(deploy_text)

old_p = 'battle_analytics/personal_stats.html'
new_p = 'battle_analytics/personal.html'
if os.path.exists(old_p):
    os.rename(old_p, new_p)

print('Successfully renamed personal_stats to personal!')
