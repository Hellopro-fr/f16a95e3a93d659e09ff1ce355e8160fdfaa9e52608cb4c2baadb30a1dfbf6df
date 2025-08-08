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

        sampling_params = SamplingParams(max_tokens=150, temperature=0.1, stop=["}"])
        user_prompt = PROMPT_TEMPLATE_FR.format(url=url, content=content)
        conversation = [{"role": "user", "content": user_prompt}]
        
        formatted_prompt = self.tokenizer.apply_chat_template(
            conversation, 
            tokenize=False, 
            add_generation_prompt=True
        )

        outputs = self.llm.generate([formatted_prompt], sampling_params)
        raw_text = outputs[0].outputs[0].text.strip()

        # --- BLOC DE PARSING ROBUSTE ---
        try:
            # 1. Trouver la première accolade ouvrante
            start_index = raw_text.find('{')
            # 2. Trouver la dernière accolade fermante
            end_index = raw_text.rfind('}')

            # 3. Si les deux sont trouvées, extraire la sous-chaîne JSON
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_string = raw_text[start_index : end_index + 1]
                result = json.loads(json_string)
            else:
                # Si on ne trouve pas un bloc JSON valide, on lève une erreur
                raise ValueError("Bloc JSON non trouvé dans la sortie du LLM.")

        except (json.JSONDecodeError, ValueError) as e:
            # Pour le débogage, il est crucial de voir ce que le LLM a réellement renvoyé
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