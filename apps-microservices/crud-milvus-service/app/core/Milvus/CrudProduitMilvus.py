import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from logging.handlers import TimedRotatingFileHandler
from app.core.credentials import settings
from app.core.Milvus.Config import Config

from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    MilvusException,
)

# --- CONFIGURATION ---


os.makedirs(f'{settings.DOCUMENT_ROOT}/logs', exist_ok=True)

file_handler = TimedRotatingFileHandler(
    filename=f"{settings.DOCUMENT_ROOT}/logs/crud_produit.log",
    when='midnight',  # Rotate at midnight
    interval=1,       # Rotate every day
    backupCount=30,   # Keep 30 days of logs
    encoding='utf-8'
)

console_handler = logging.StreamHandler()

log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)
console_handler.setFormatter(log_format)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.propagate = False


@dataclass
class ModelConfig:
    model_id: str = "dangvantuan/sentence-camembert-large"
    collection_name: str = "produits"
    dimension: int = 1024


class CrudProduitMilvus:
    def __init__(self, config: Config = Config() , **kwargs: Any):
        self.config = config
        self.collection: Optional[Collection] = None
        if not self.config.ZILLIZ_URI or not self.config.ZILLIZ_API_KEY:
            raise ValueError("Zilliz Cloud URI and API Key must be set in the environment.")
        self.logger = kwargs.get('logger', logger)
        
    def _connect_to_milvus(self):
        self.logger.info("Connexion sur Zilliz cloud...")
        connections.connect("default", uri=self.config.ZILLIZ_URI, token=self.config.ZILLIZ_API_KEY)
        self.logger.info("✓ Connexion sur Zilliz cloud avec succès.")
    
    def _get_or_create_collection(self, model_config: ModelConfig) -> Collection:
        collection_name = model_config.collection_name
        model_key = model_config.model_id

        if utility.has_collection(collection_name) and self.config.RECREATE_COLLECTIONS:
            logging.warning(f"[{model_key}] Collection déjà existante → suppréssion en cours : '{collection_name}'")
            utility.drop_collection(collection_name)

        if not utility.has_collection(collection_name):
            self.logger.info(f"Collection '{collection_name}' non trouvée. Création...")
            # Définition du schéma détaillé
            fields = [
                # Todo : ce clé doit être unique
                FieldSchema(name="id", dtype=DataType.INT64 , is_primary = True , auto_id = True ,max_length=64),
                FieldSchema(name="chunk_id", dtype=DataType.VARCHAR , max_length=64),
                FieldSchema(name="id_produit", dtype=DataType.VARCHAR , max_length=255),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=model_config.dimension),
                FieldSchema(name="nom_produit", dtype=DataType.VARCHAR, max_length=2048),
                FieldSchema(name="id_categorie", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="categorie", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="id_fournisseur", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="fournisseur", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="domaine", dtype=DataType.VARCHAR, max_length=255),
                FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="chunk_number", dtype=DataType.INT64),
                FieldSchema(name="total_chunks", dtype=DataType.INT64),
                FieldSchema(name="metadata", dtype=DataType.JSON, description="Contient le record JSON original complet et d'autres métadonnées")
            ]
            schema = CollectionSchema(fields, description=f"Collection de chunks de produits pour {model_key}")
            collection = Collection(collection_name, schema, consistency_level="Strong")
            
            self.logger.info(f"[{model_key}] Création HNSW index pour l'embedding")

            # TODO : Vérifier les paramètres d'indexation
            # Exemple d'indexation HNSW pour les embeddings
            index_params = {"metric_type": "COSINE", "index_type": "HNSW", "params": {"M": 16, "efConstruction": 256}}
            collection.create_index(field_name="embedding", index_params=index_params)

            # Optionnel: Créer des index scalaires pour les filtres fréquents
            collection.create_index(field_name="id_produit", index_name="idx_id_produit")
            collection.create_index(field_name="id_categorie", index_name="idx_id_categorie")
            self.logger.info(f"[{model_key}] ✓ Index créés.")
        else:
            self.logger.info(f"[{model_key}] Connexion à la collection existante : '{collection_name}'")
            collection = Collection(collection_name)
        
        collection.load()
        self.logger.info(f"[{model_key}] ✓ Collection '{collection_name}' chargée et prête.")
        return collection


    def insert_produit(self, produit: Dict[str, Any]) -> Dict[str, Any]:
        data = produit

        model_config = ModelConfig()
        model_key = model_config.model_id

        try:
            
            self._connect_to_milvus()
            self.collection = self._get_or_create_collection(model_config)
            
            if not data or self.collection is None:
                return {
                    "status": "error",
                    "message": "Aucune donnée à insérer ou collection non initialisée."
                }
            
            self.logger.info(f"[{model_key}][PRODUIT] Insertion de batch de {len(data)} entités dans '{self.collection.name}'...")
           
            result = self.collection.insert(data)
            self.collection.flush()

            self.logger.info(f"Résultat insertion : {result}") 
            self.logger.info(f"Clé primaire : {result.primary_keys}") 
            
            self.logger.info(f"[{model_key}] ✓ Insertion terminée avec succès.")
            
            return {
                "ids": str(result.primary_keys[0]) if result.primary_keys else "",
                "status": "success",
            }

        except MilvusException as e:
            self.logger.error(f"[{model_key}][PRODUIT] Erreur Milvus lors de l'insertion : {e}")
            self.logger.error(f"Data : {data}")
        except Exception as e:
            self.logger.error(f"[{model_key}][PRODUIT] insertion de batch : {e}", exc_info=True)
            self.logger.error(f"Data : {data}")
    
    def update_produit(self, produit: Dict[str, Any]) -> Dict[str, Any]:
        data = produit
        model_config = ModelConfig()
        model_key = model_config.model_id

        try:
            
            self._connect_to_milvus()
            self.collection = self._get_or_create_collection(model_config)
            
            if not data or self.collection is None:
                return {
                    "status": "error",
                    "message": "Aucune donnée à mettre à jour ou collection non initialisée."
                }
            
            if not data.get("id"):
                self.logger.error(f"[{model_key}][PRODUIT] Mise à jour de produit sans ID.")
                return {
                    "status": "error",
                    "message": "Clé primaire (ID) requise pour la mise à jour."
                }

            self.logger.info(f"[{model_key}][PRODUIT] Mise à jour de batch de {len(data)} entités dans '{self.collection.name}'...")
            result = self.collection.upsert(data)
            self.collection.flush()
            self.logger.info(f"[{model_key}] ✓ Mise à jour terminée avec succès.")
            
            return {
                "ids": str(result.primary_keys[0]) if result.primary_keys else "",
                "status": "success",
            }

        except MilvusException as e:
            self.logger.error(f"[{model_key}][PRODUIT] Erreur Milvus lors de mise à jour : {e}")
            self.logger.error(f"Data : {data}")
        except Exception as e:
            self.logger.error(f"[{model_key}][PRODUIT] Mise à jour de batch : {e}", exc_info=True)
            self.logger.error(f"Data : {data}")

    def delete_produit(self,produit: Dict[str, Any]) -> Dict[str, Any]:
        model_config = ModelConfig()
        model_key = model_config.model_id
        id_entity_milvus = produit.get("id")
        
        try:
            self._connect_to_milvus()
            self.collection = self._get_or_create_collection(model_config)

            if not self.collection:
                return {
                    "status": "error",
                    "message": "Collection non initialisée."
                }

            if not id_entity_milvus:
                self.logger.error(f"[{model_key}][PRODUIT] Suppression de produit sans ID.")
                return {
                    "status": "error",
                    "message": "Clé primaire (ID) requise pour la suppression."
                }

            self.logger.info(f"[{model_key}][PRODUIT] Suppression de l'entité avec ID {id_entity_milvus} dans '{self.collection.name}'...")
            result = self.collection.delete(f"id == {id_entity_milvus}")
            self.collection.flush()
            self.logger.info(f"[{model_key}] ✓ Suppression terminée avec succès.")

            return {
                "status": "success",
                "message": f"Produit avec ID {id_entity_milvus} supprimé."
            }

        except MilvusException as e:
            self.logger.error(f"[{model_key}][PRODUIT] Erreur Milvus lors de la suppression : {e}")
        except Exception as e:
            self.logger.error(f"[{model_key}][PRODUIT] Suppression de produit : {e}", exc_info=True)
    
    
    def get_produit(self,id_produit: str) -> Dict[str, Any]:
        list_produit = [id_produit]
        model_config = ModelConfig()
        model_key = model_config.model_id
        
        try:
            self._connect_to_milvus()
            self.collection = self._get_or_create_collection(model_config)

            if not self.collection:
                return {
                    "status": "error",
                    "message": "Collection non initialisée."
                }

            if not id_produit:
                self.logger.error(f"[{model_key}][PRODUIT] Récupèration de produit sans ID.")
                return {
                    "status": "error",
                    "message": "ID produit requise pour la récupération."
                }

            self.logger.info(f"[{model_key}][PRODUIT] Récupèration de l'entité avec ID produit {id_produit} dans '{self.collection.name}'...")
            result = self.collection.query(
                expr=f"id_produit in {list_produit}",
                output_fields=["id","id_produit","chunk_id","total_chunks","nom_produit","id_categorie","categorie","id_fournisseur","fournisseur","domaine"]
                )
            self.collection.flush()
            self.logger.info(f"[{model_key}] ✓ Récupèration terminée avec succès.")

            return {
                "status": "success",
                "data": result
            }

        except MilvusException as e:
            self.logger.error(f"[{model_key}][PRODUIT] Erreur Milvus lors de la récupération : {e}")
        except Exception as e:
            self.logger.error(f"[{model_key}][PRODUIT] Récupèration de produit : {e}", exc_info=True)