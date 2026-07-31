import os
import glob
from bs4 import BeautifulSoup

def verify():
    print("=== СТРОГАЯ ПРОВЕРКА РЕЗУЛЬТАТОВ ===")
    
    # 1. Проверяем наличие Руслана в personal.html
    personal_path = 'battle_analytics/personal.html'
    assert os.path.exists(personal_path), "Файл battle_analytics/personal.html не найден!"
    with open(personal_path, 'r', encoding='utf-8') as f:
        personal_html = f.read()
    
    has_ruslan = 'Руслан' in personal_html
    print(f"1. Руслан в personal.html: {'ОК (найден)' if has_ruslan else 'ОШИБКА (не найден)'}")

    # 2. Проверяем имя файла и deploy.py
    with open('deploy.py', 'r', encoding='utf-8') as f:
        deploy_content = f.read()
    deploy_ok = 'personal.html' in deploy_content and 'personal_stats.html' not in deploy_content
    print(f"2. Деплой настроен на personal.html: {'ОК' if deploy_ok else 'ОШИБКА'}")

    # 3. Проверяем досье обычных игроков на отсутствие колонки 'Противник'
    sample_dossier = 'battle_analytics/VadSJ/summary.html'
    if os.path.exists(sample_dossier):
        with open(sample_dossier, 'r', encoding='utf-8') as f:
            dossier_html = f.read()
        has_opponent_col = 'Противник' in dossier_html
        print(f"3. Колонка 'Противник' в досье обычного игрока: {'ОШИБКА (она есть)' if has_opponent_col else 'ОК (успешно удалена)'}")
    else:
        print("3. Досье VadSJ не найдено для проверки.")

    # 4. Проверяем индивидуальное досье ksotar
    ksotar_dossier = 'battle_analytics/ksotar/summary.html'
    if os.path.exists(ksotar_dossier):
        with open(ksotar_dossier, 'r', encoding='utf-8') as f:
            ksotar_html = f.read()
        
        has_tactical = 'Тактический анализ' in ksotar_html
        print(f"4. Тактический анализ в досье ksotar: {'ОШИБКА (он есть)' if has_tactical else 'ОК (успешно удален)'}")
        
        # Проверим ссылки на бои
        soup = BeautifulSoup(ksotar_html, 'html.parser')
        rows = soup.find_all('tr')
        broken_links = 0
        total_links = 0
        for r in rows:
            onclick = r.get('onclick', '')
            if "window.location=" in onclick:
                total_links += 1
                link = onclick.split("'")[1]
                # link имеет вид '../<p_folder>/battle_*.html'
                # Реальный путь в файловой системе: battle_analytics/<link без ../>
                parts = link.replace('../', '').split('/')
                if len(parts) == 2:
                    p_folder, filename = parts
                    full_path = os.path.normpath(os.path.join('battle_analytics', p_folder, filename))
                else:
                    full_path = os.path.normpath(os.path.join('battle_analytics', link.replace('../', '')))
                
                if not os.path.exists(full_path):
                    broken_links += 1
                    print(f"   [!] Битый путь к бою: {link} (разрешен в {full_path})")
        
        print(f"5. Ссылки на карточки боев в досье ksotar: Всего {total_links}, Битых: {broken_links} ({'ОК' if broken_links == 0 else 'ОШИБКА'})")
    else:
        print("4-5. Досье ksotar не найдено!")

if __name__ == '__main__':
    verify()
