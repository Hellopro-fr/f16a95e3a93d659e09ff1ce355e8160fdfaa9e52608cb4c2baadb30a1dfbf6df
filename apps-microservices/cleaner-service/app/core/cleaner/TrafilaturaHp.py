import json
import trafilatura
import logging
import re
import os
import unicodedata
import csv

from typing import Dict, List
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from bs4 import BeautifulSoup
from copy import deepcopy
from markdownify import markdownify as md
from datetime import datetime
from langdetect import detect
from sentence_splitter import SentenceSplitter
from collections import Counter

from app.schemas.cleaner.cleaner import BaseTrafilaturaReponse, TrafilaturaReponseHtml, BaseTrafilatura

from lxml.etree import tostring, SubElement

from app.core.credentials import settings

os.makedirs(f'{settings.DOCUMENT_ROOT}/logs', exist_ok=True)

file_handler = TimedRotatingFileHandler(
    filename=f"{settings.DOCUMENT_ROOT}/logs/trafilatura.log",
    when='midnight',  # Rotate at midnight
    interval=1,       # Rotate every day
    backupCount=30,   # Keep 30 days of logs
    encoding='utf-8'
)
log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.propagate = False

class TrafilaturaHp:
    def __init__(self, info: list[BaseTrafilatura] = [], **kwargs):
        object.__setattr__(self, '_initializing', True)
        object.__setattr__(self, '_trafilatura', trafilatura)
        object.__setattr__(self, '_bs', BeautifulSoup)
        object.__setattr__(self, '_config', deepcopy(self._trafilatura.settings.DEFAULT_CONFIG))

        object.__setattr__(self, 'info', info)
        object.__setattr__(self, 'logger', kwargs.get("logger") if kwargs.get("logger") else logger)

        object.__setattr__(self, 'date', datetime.now())

        object.__setattr__(self, 'OUTPUT_DIR', f"/output/json/{self.date.strftime("%Y/%m/%d")}/")

        object.__setattr__(self, 'output', f"{settings.DOCUMENT_ROOT}{self.OUTPUT_DIR}{self.date.strftime("%Y-%m-%d-%H-%M-%S")}-trafilatura.json")

        object.__setattr__(self, 'w_csv', False)
        object.__setattr__(self, 'OUTPUT_CSV_DIR', f"/output/csv/{self.date.strftime("%Y/%m/%d")}/")
        object.__setattr__(self, 'output_csv', f"{settings.DOCUMENT_ROOT}{self.OUTPUT_CSV_DIR}{self.date.strftime("%Y-%m-%d-%H-%M-%S")}-trafilatura.csv")

        object.__setattr__(self, 'output_types', kwargs.get("output_types") if kwargs.get("output_types") else {'markdown': 'md'})

        os.makedirs(f"{settings.DOCUMENT_ROOT}{object.__getattribute__(self, 'OUTPUT_DIR')}", exist_ok=True)

        object.__setattr__(self, 'sizes', [10, 25, 50, 100, 150, 200, 300, 500, 750, 1000])

        object.__setattr__(self, '_initializing', False)

    def __setattr__(self, name, value):
        if name.startswith("_") and not self.__dict__.get("_initializing", False):
            raise TypeError("Info de configuration non modifiable")

        if name == 'info' and not isinstance(value, list):
            raise TypeError("Valeur info doit être une liste de dict")
        elif name == 'w_csv' and not isinstance(value, bool):
            raise TypeError("Valeur doit être booléen")
        
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise TypeError("Info de configuration non récupérable")
        return object.__getattribute__(self, name)

    @staticmethod
    def _normalize_sentence(text: str) -> str:
        """Normalizes a sentence for accurate comparison."""
        return unicodedata.normalize("NFKC", text).strip().lower()

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """Cleans up whitespace and removes control characters."""
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text) # Remove control characters
        text = re.sub(r'\s+', ' ', text) # Collapse whitespace
        return text.strip()

    @staticmethod
    def save_results_to_json(results: List[Dict], output_path: Path):
        """Saves a list of dictionaries to a JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logging.info(f"Results successfully saved to {output_path}")

    """
    @function extract
    @params keys -> dict = {
        "url": "url",
        "content": "content",
    }
    """
    def extract(self, keys: dict = {}) -> List[BaseTrafilaturaReponse | TrafilaturaReponseHtml]:
        response_objects: List[BaseTrafilaturaReponse | TrafilaturaReponseHtml] = []
        html = []
        for item in self.info:
            url = getattr(item, keys.get('url') or 'url', None)
            content = getattr(item, keys.get('content') or 'content', None)

            fetch_content = getattr(item, keys.get('fetch') or 'fetch', False)

            if fetch_content:
                content_fetch = self._trafilatura.fetch_url(url, no_ssl=True)

                if content_fetch:
                    content = content_fetch

            res = self.extract_content(url, content)

            if fetch_content:
                response_objects.append(
                    TrafilaturaReponseHtml(url=url, content=self._normalize_whitespace(res), html=content or "")
                )
            else:
                response_objects.append(
                    BaseTrafilaturaReponse(url=url, content=self._normalize_whitespace(res))
                )
            if not res:
                response_objects.append(
                    BaseTrafilaturaReponse(url=url, content="")
                )
                continue

        result = [obj.model_dump() for obj in response_objects]
        self.save_results_to_json(results=result, output_path=Path(self.output))

        return response_objects
    
    def extract_content(self, url, content) -> str:
        if not content:
            self.logger.info("Contenu de page vide pour l'URL : {url}")
            return None
        soup = self._bs(content, "html5lib")
        main_element = self.extract_bs(soup)
        self.logger.info(f"---------------------------------")
        self.logger.info(f"URL : {url}")
        final_content = ""
        if main_element:
            self.logger.info(f"Extraction avec BS4 - Main - html5lib")
            final_content = md(str(main_element), heading_style="ATX", escape_html=False)
            if final_content.strip() == "":
                self.logger.info(f"Extraction avec BS4 - Main - lxml")
                soup = self._bs(content, "lxml")
                main_element = self.extract_bs(soup)
                final_content = md(str(main_element), heading_style="ATX", escape_html=False)
        else:
            soup = BeautifulSoup(content, 'html5lib')

            # Supprimer tout ce qui est potentiellement JS
            for tag in soup.find_all(['script', 'noscript', 'style']):
                tag.decompose()

            content = str(soup)
            tree = self._trafilatura.load_html(content)
            if tree is not None:
                anchors = tree.xpath("//*[contains(@class, 'product') or contains(@id, 'product') or contains(@class, 'produit') or contains(@id, 'produit')]//a")
                if anchors is not None:
                    self.logger.info("Détection éléments de produits en balise a ==> modification a en h3")
                    for a_tag in anchors:
                        parent = a_tag.getparent()
                        if parent is None:
                            continue

                        h3_tag = SubElement(parent, 'h3')

                        h3_tag.text = a_tag.text
                        for child in a_tag:
                            h3_tag.append(child)

                        parent.insert(parent.index(a_tag), h3_tag)

                        parent.remove(a_tag)
                        content = tostring(tree, method='html', encoding='unicode')

            results = {}
            for i, (output_type, ext) in enumerate(self.output_types.items()):
                for size in self.sizes:
                    self._config.set("DEFAULT", "MIN_EXTRACTED_SIZE", str(size))

                    extracted = trafilatura.extract(
                        content,
                        output_format=output_type,
                        include_tables=True,
                        include_links=True,
                        include_images=True,
                        include_formatting=True,
                        include_comments=True,
                        # with_metadata=True,  # Important pour que trafilatura extraie l'image principale
                        favor_recall=True,
                        # favor_precision=True,
                        config=self._config,
                        deduplicate=True,
                        url=url,
                        prune_xpath=[
                            "//*[contains(@class, 'd-none')]", # Exclude d-none class
                            # "//*[contains(@class, 'hidden')]",  # Exclude hidden class
                            # "//*[@style[contains(., 'display:none')]]"  # Exclude inline display:none
                            "//footer",
                            "//nav",
                            "//script",
                            "//noscript",
                            "//style"
                        ]
                    )

                    if not extracted:
                        self.logger.info(f"MIN_EXTRACTED_SIZE={size:>5}: SKIPPED (empty)")
                        continue

                    results[size] = extracted
                    length = len(extracted)
                    self.logger.info(f"MIN_EXTRACTED_SIZE={size:>5}: {length:>6} characters")

                if results:
                    best_size = max(results.keys(), key=lambda k: len(results[k]))
                    self.logger.info(f"Meilleur MIN_EXTRACTED_SIZE: {best_size}")
                    final_content = results[best_size]
                    
                    article_content = self.extract_article(soup)
                    if article_content:
                        self.logger.info(f"Extraction article")
                        self.logger.info(f"URL avec article : {url}")
                        final_content = article_content + "\n" + final_content
                        final_content = self.dedoublonnage(final_content)
                else:
                    self.logger.info(f"Aucune extraction valide!")
        return final_content
    
    def dedoublonnage(self, text: str, min_occurrences: int = 2) -> str:
        try:
            lang = detect(text)
        except:
            lang = "fr"

        splitter = SentenceSplitter(language=lang)
        sentences = splitter.split(text)

        normalized_sentences = [self._normalize_sentence(s) for s in sentences]
        counts = Counter(normalized_sentences)

        seen = set()
        deduplicated = []
        for i, s in enumerate(sentences):
            norm = normalized_sentences[i]
            if counts[norm] >= min_occurrences:
                if norm not in seen:
                    deduplicated.append(s)
                    seen.add(norm)
            else:
                deduplicated.append(s)

        return " ".join(deduplicated)
    
    def extract_bs(self, soup) -> str:
        """Extrait le texte avec BeautifulSoup en ciblant les balises pertinentes."""
        for img in soup.find_all('img'):
            img.decompose()
        
        self.logger.info("Récupération de main")
        main_element = soup.find('main') or soup.select_one("body > :is(#main, .main)")

        if main_element:
            # main_element.prettify()
            self.logger.info("Récupération de main et vérification header + footer")
            for selector in (':scope > header', ':scope > footer'):
                if element_to_remove := main_element.select_one(selector):
                    self.logger.info(f"Suppression {selector} dans contenu de main")
                    element_to_remove.decompose()

        if not main_element:
            return None

        return main_element
    
    
    def extract_article(self, soup) -> str|None:
        found_articles = soup.select('article[id*="product"], article[class*="product"], article[id*="produit"], article[class*="produit"]')
        return None if not found_articles else "\n".join([md(str(article), heading_style="ATX") for article in found_articles])