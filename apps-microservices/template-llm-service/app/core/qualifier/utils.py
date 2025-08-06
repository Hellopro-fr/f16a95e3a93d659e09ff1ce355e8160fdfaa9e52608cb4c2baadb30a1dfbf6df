import json
from pathlib import Path
from typing import Optional

def find_content_in_directory(directory_path: str, target_url: str) -> Optional[str]:
    data_dir = Path(directory_path)
    if not data_dir.is_dir():
        print(f"Erreur : Le répertoire '{directory_path}' n'existe pas.")
        return None
    for file_path in data_dir.glob('*.json'):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    continue
                for item in data:
                    if item.get("url") == target_url:
                        return item.get("content") or "Contenu vide."
        except Exception as e:
            print(f"Erreur lecture {file_path}: {e}")
    return None

PROMPT_TEMPLATE_FR = """
Tu es un classifieur de type de pages pour sites de fournisseurs de matériel professionnel.
[...] # Le même contenu complet du prompt que dans ton projet initial
"""
