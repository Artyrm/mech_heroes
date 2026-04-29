# Заметки об окружении пользователя

## Python / Anaconda

- Python установлен через **Anaconda3** по пути `C:\tools\Anaconda3`
- **Прямой путь к интерпретатору:** `C:\tools\Anaconda3\python.exe`
- Для запуска с активацией conda используется:
  ```
  %windir%\System32\WindowsPowerShell\v1.0\powershell.exe -ExecutionPolicy ByPass -NoExit -Command "& 'C:\tools\Anaconda3\shell\condabin\conda-hook.ps1' ; conda activate 'C:\tools\Anaconda3'"
  ```
- В скриптах и командах **всегда использовать прямой путь:**
  ```powershell
  & 'C:\tools\Anaconda3\python.exe' script.py
  ```
  или в однострочниках:
  ```powershell
  & 'C:\tools\Anaconda3\python.exe' -c "print('hello')"
  ```
- Команды `python`, `python3`, `py` — **НЕ работают** в стандартной powershell-сессии без активации conda.

## ОС и оболочка

- **ОС:** Windows (PowerShell)
- В PowerShell нельзя писать `cmd1 & cmd2` — использовать `;` или отдельные вызовы.
- Кириллические пути работают нормально при правильном указании кодировки.

## Рабочая директория проекта

- Основной проект (Клан Орки): `g:\Video\!Медведи\Mech Heroes\Клан Орки\accountant_bot\`

## Git

- Репозиторий: `Artyrm/mech_heroes`
- `.gitignore` присутствует в корне проекта.
