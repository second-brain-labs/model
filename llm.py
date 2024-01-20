from typing import Optional, List, Mapping, Any
from llama_index.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.llms.base import llm_completion_callback

import os
import time

from modal import Image, Stub, gpu, enter, method

MODEL_DIR = "/model"
BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"


def download_models():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    AutoModelForCausalLM.from_pretrained(BASE_MODEL)
    AutoTokenizer.from_pretrained(BASE_MODEL)


image = (
    Image.debian_slim(python_version="3.10")
    .pip_install(
        "accelerate~=0.18.0",
        "transformers",
        "torch~=2.0.0",
        "sentencepiece~=0.1.97",
        "llama-index",
    )
    .run_function(download_models)
)

stub = Stub(name="secondbrain", image=image)

@stub.cls(
    gpu="A100",
    timeout=60 * 10,
    container_idle_timeout=60 * 10,
    allow_concurrent_inputs=10,
)
class Model:
    def __enter__(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float16)
        model.to("cuda")
        self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        self.tokenizer.bos_token_id = 1

        model.eval()
        self.model = torch.compile(model)
        self.device = "cuda"

    @method()
    def generate(
        self,
        input,
        max_new_tokens=1024,
    ):
        import torch
        from transformers import GenerationConfig

        inputs = self.tokenizer(input, return_tensors="pt")
        input_ids = inputs["input_ids"].to(self.device)

        generation_config = GenerationConfig(
            top_p=0.75,
            top_k=40,
            num_beams=1,
            temperature=0.1,
            do_sample=True,
        )
        with torch.no_grad():
            generation_output = self.model.generate(
                input_ids=input_ids,
                generation_config=generation_config,
                return_dict_in_generate=True,
                output_scores=True,
                max_new_tokens=max_new_tokens,
                pad_token_id=self.tokenizer.eos_token_id
            )
        s = generation_output.sequences[0]
        output = self.tokenizer.decode(s)
        print(f"\033[96m{input}\033[0m")
        return output.split(input)[1].strip()

class MixtralModalLLM(CustomLLM):
    context_window: int = 8192
    num_output: int = 1024
    model_name: str = "second-brain-model"

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_name,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        with stub.run():
            return CompletionResponse(text=Model().generate.remote(prompt))

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, **kwargs: Any
    ) -> CompletionResponseGen:
        with stub.run():
            yield CompletionResponse(text = Model().generate.remote(prompt))

@stub.local_entrypoint()
def main():
    model = Model()
    questions = [
        "Implement a Python function to compute the Fibonacci numbers.",
        "What is the fable involving a fox and grapes?",
        "What were the major contributing factors to the fall of the Roman Empire?",
        "Describe the city of the future, considering advances in technology, environmental changes, and societal shifts.",
        "What is the product of 9 and 8?",
        "Who was Emperor Norton I, and what was his significance in San Francisco's history?",
    ]
    for question in questions:
        print("Sending new request:", question)
        print(model.generate.remote(question))


if __name__ == "__main__":
    main()
