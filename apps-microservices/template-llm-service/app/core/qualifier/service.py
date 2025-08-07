import json
from vllm import LLM, SamplingParams
from app.core.qualifier.utils import PROMPT_TEMPLATE_FR # On garde le prompt

class QualifierService:
    def __init__(self):
        self.llm_args = {
            "model": "TheBloke/deepseek-llm-7b-chat-AWQ",
            "quantization": "awq",
            "gpu_memory_utilization": 0.90,
            "trust_remote_code": True,
            "dtype": "auto"
        }
        self.llm = LLM(**self.llm_args)
        self.tokenizer = self.llm.get_tokenizer()

    # La signature de la méthode change pour accepter le contenu
    def classify(self, url: str, content: str):
        # La recherche de fichier est supprimée !
        if not content:
            # On peut gérer le cas où un contenu vide est envoyé
            return "contenu_vide", None, {"url": url}

        sampling_params = SamplingParams(max_tokens=150, temperature=0.1, stop=["}"])
        
        # Le prompt est maintenant formaté avec le contenu reçu directement
        user_prompt = PROMPT_TEMPLATE_FR.format(url=url, content=content)
        
        conversation = [{"role": "user", "content": user_prompt}]
        
        formatted_prompt = self.tokenizer.apply_chat_template(
            conversation, 
            tokenize=False, 
            add_generation_prompt=True
        )

        outputs = self.llm.generate([formatted_prompt], sampling_params)
        
        raw_text = outputs[0].outputs[0].text.strip()
        
        if not raw_text.startswith('{'):
            raw_text = '{' + raw_text
        if not raw_text.endswith('}'):
            raw_text = raw_text + "}"

        try:
            result = json.loads(raw_text)
        except Exception:
            result = {
                "type_page": "erreur_parsing",
                "chunk": None,
                "metadata": {"raw_output": raw_text}
            }
            
        chunk = content[:500]
        metadata = {"url": url}
        return result.get("type_page", "N/A"), chunk, metadata