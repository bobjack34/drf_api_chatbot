# Kleines Ruff Tutorial

## Install Ruff VSCode
Ruff Extension Astral

## Install Ruff 
pip install ruff
bzw. 
uv add --dev ruff

# RUFF FORMAT

## in VSCode 
Ruff als Formatter wählen
bei Format on save

## auf CLI
uv run ruff check

# RUFF FORmat fix
Ruff kann auch Fehler beheben

## in VSCODE
um Ruff zu nutzen, kann man in die Commands von VS Code gehen mit Shift + STRG + p und ruff eingeben:

Shift + STRG + p: Ruff: fix all autofixable problems
Shift + STRG + p: Ruff: fix imports

## auf CLI
uv run ruff check --fix

# Ruff mögliche Settings in pyproject.toml (wird von VSCODE berücksichtigt)
https://docs.astral.sh/ruff/rules/

[tool.ruff]
select = [
  "E",  # pycodestyle (z. B. Einrückung, Leerzeichen, Zeilenlänge)
  "F",  # pyflakes (z. B. undefinierte Variablen)
  "I",  # isort (Import-Sortierung)
  "B",  # flake8-bugbear (potenzielle Bugs)
  "C4", # flake8-comprehensions (List/Dict Comprehension-Optimierungen)
  "T20",# flake8-print (print()-Aufrufe)
  "UP", # pyupgrade (modernere Syntax)
  "N",  # pep8-naming (Namenskonventionen)
  "S",  # bandit (Sicherheitsprüfungen)
  "D",  # pydocstyle (Docstring-Regeln)
]
# bestimmte Fehler ignorieren
ignore = ["E501"]

## typische Settings

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "B", "N", "S"]
exclude = ["*/tests/*", "*/migrations/*", "build/"]

[tool.ruff.isort]
known-first-party = ["events", "users", "project"]
force-sort-within-sections = true
combine-as-imports = true