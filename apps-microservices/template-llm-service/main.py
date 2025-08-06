import json
from app.core.qualifier.utils import find_content_in_directory, PROMPT_TEMPLATE_FR
from vllm import LLM, SamplingParams

class QualifierService:
    def __init__(self):
        self.llm_args = {
            "model": "Vonreal/gemini1.5-flash",  # Gemini Flash 1.5 open source
            "quantization": "awq",              # Quantization mode
            "gpu_memory_utilization": 0.90,       # Utilisation GPU ajustée
            "trust_remote_code": True,            # Autoriser le code distant
            "max_model_len": 8192,                # Longueur max du contexte
            "dtype": "auto"                       # Type de données automatique
        }
        
        self.llm = LLM(**self.llm_args)

    def classify(self, url: str):
        content = find_content_in_directory("json", url)
        if content is None:
            return None, None, None
        sampling_params = SamplingParams(
            max_tokens=150,
            temperature=0.1,
            stop=["}"]
        )
        user_prompt = PROMPT_TEMPLATE_FR.format(url=url, content=content)
        conversation = [{"role": "user", "content": user_prompt}]
        outputs = self.llm.chat([conversation], sampling_params, use_tqdm=False)
        raw_text = outputs[0].outputs[0].text.strip() + "}"
        try:
            result = json.loads(raw_text)
        except Exception:
            result = {
                "type_page": "erreur_parsing",
                "chunk": None,
                "metadata": {"raw_output": raw_text}
            }
        chunk = content[:500]  # Exemple: premier chunk
        metadata = {"url": url}
        return result.get("type_page", "N/A"), chunk, metadata
