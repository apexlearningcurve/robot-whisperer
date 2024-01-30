from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from jsonformer import Jsonformer

from LLM.prompts import classifier_prompt_1
from LLM.action_models import generic_function


class FunctionCaller:
    def __init__(
        self, model_name: str = "TheBloke/Mistral-7B-Instruct-v0.2-GPTQ"
    ) -> None:
        self.device = (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )
        script_folder = Path(__file__).resolve().parent
        weights_dir = script_folder / "weights"

        # Load model
        self.llm = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            trust_remote_code=False,
            cache_dir=weights_dir,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=False,
            device=self.device,
            cache_dir=weights_dir,
        )

        self.jsonformer = Jsonformer(self.llm, self.tokenizer, generic_function, "")

    def generate(self, prompt):
        self.jsonformer.prompt = classifier_prompt_1.format(user_query=prompt)
        fn_call = self.jsonformer()

        return fn_call
