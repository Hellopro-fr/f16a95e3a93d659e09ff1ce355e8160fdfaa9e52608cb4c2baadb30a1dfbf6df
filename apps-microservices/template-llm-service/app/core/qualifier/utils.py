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

En entrée, tu reçois le contenu texte présent dans le code source html d’une page. Attention il faut donc identifier le contenu principal de la page et en identifier le sens et ne pas se laisser influencer par le contenu présent dans le header ou le footer par exemple

Ta tâche est de déterminer quelle est la fonction principale de cette page pour l’utilisateur final, pas simplement sa structure HTML.

En sortie, tu dois produire un objet JSON :

Si la page correspond à un des types listés → retourne uniquement :
{{ "type_page": "valeur" }}

Si la page ne correspond à aucun type → retourne :
{{ "type_page": "autre", "commentaire_si_autre": "explication en 15 mots max" }}

Critère clé : ne te base pas uniquement sur les balises Markdown.
Analyse le but de la page pour l’utilisateur final : s’informer, comparer, acheter, demander un devis, découvrir une offre locale, etc.

Voici les types de pages possibles :
"home" : page d’accueil du site
"listing_produit" : page présentant une gamme de produits ou une catégorie de produits
"fiche_produit" : page présentant en détail un produit spécifique
"fiche_realisation" : page montrant un projet ou cas client réalisé
"Presentation-societe" : présentation de l’entreprise, qui sommes nous
"contact" : prise de contact, liste des magasins
"cgv_mentions_legales_cgu" : page juridique
"article" : Guide d'achat, article de blog, actualité ou guide éditorial
"Savoir_faire" : page présentant un savoir faire particulier de l'entreprise
"Page_local" : page dédiée au référencement naturel pour une localisation
"demande_devis" : page pour obtenir un devis
"compte_client" : espace client
"recrutement" : page de recrutement
"references_clients" : témoignages ou logos de clients
"faq" : questions fréquentes
"plan_du_site" : plan global
"politique_confidentialite" : politique de confidentialité ou cookies
"autre" : si aucun type ne correspond

Rappels :
- Si "type_page" ≠ "autre", ne génère pas de champ "commentaire_si_autre".
- Génère seulement le JSON, sans autre texte.
- Analyse le but marketing ou fonctionnel de la page.

Voici l'url de la page: {url}

Contenu en entrée (Markdown) :
{content}
"""
