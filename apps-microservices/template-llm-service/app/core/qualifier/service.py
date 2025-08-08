import json
from vllm import LLM, SamplingParams
from app.core.qualifier.utils import PROMPT_TEMPLATE_FR

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

    def classify(self, url: str, content: str):
        if not content:
            return "contenu_vide", None, {"url": url}

        # --- CORRECTION FINALE ICI ---
        # On retire le stop token qui coupait la génération trop tôt
        # et on augmente un peu les max_tokens par sécurité.
        sampling_params = SamplingParams(max_tokens=250, temperature=0.1) # stop=["}"] a été retiré

        user_prompt = PROMPT_TEMPLATE_FR.format(url=url, content=content)
        conversation = [{"role": "user", "content": user_prompt}]
        
        formatted_prompt = self.tokenizer.apply_chat_template(
            conversation, 
            tokenize=False, 
            add_generation_prompt=True
        )

        outputs = self.llm.generate([formatted_prompt], sampling_params)
        raw_text = outputs[0].outputs[0].text.strip()

        # Le bloc de parsing robuste reste essentiel
        try:
            start_index = raw_text.find('{')
            end_index = raw_text.rfind('}')

            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_string = raw_text[start_index : end_index + 1]
                result = json.loads(json_string)
            else:
                raise ValueError("Bloc JSON non trouvé dans la sortie du LLM.")

        except (json.JSONDecodeError, ValueError) as e:
            print("--- ERREUR DE PARSING JSON ---")
            print(f"Erreur: {e}")
            print(f"Sortie brute du LLM: '{raw_text}'")
            
            result = {
                "type_page": "erreur_parsing",
                "chunk": None,
                "metadata": {"raw_output": raw_text}
            }
            
        chunk = content[:500]
        metadata = {"url": url}
        return result.get("type_page", "N/A"), chunk, metadata