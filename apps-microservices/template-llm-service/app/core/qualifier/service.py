import json
from vllm import LLM, SamplingParams
from app.core.qualifier.utils import find_content_in_directory, PROMPT_TEMPLATE_FR

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
        # On récupère le tokenizer pour formater correctement les prompts de chat
        self.tokenizer = self.llm.get_tokenizer()

    def classify(self, url: str):
        content = find_content_in_directory("json", url)
        if content is None:
            return None, None, None

        sampling_params = SamplingParams(max_tokens=150, temperature=0.1, stop=["}"])
        user_prompt = PROMPT_TEMPLATE_FR.format(url=url, content=content)
        
        # --- CORRECTION MAJEURE ICI ---
        conversation = [{"role": "user", "content": user_prompt}]
        
        # On utilise le tokenizer pour appliquer le template de chat du modèle
        formatted_prompt = self.tokenizer.apply_chat_template(
            conversation, 
            tokenize=False, 
            add_generation_prompt=True
        )

        # On appelle llm.generate() (la bonne méthode) avec le prompt formaté
        outputs = self.llm.generate([formatted_prompt], sampling_params)
        
        raw_text = outputs[0].outputs[0].text.strip()
        
        # On s'assure que la réponse est un JSON valide
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