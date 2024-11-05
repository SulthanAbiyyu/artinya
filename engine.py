import re
import os
from openai import OpenAI, max_retries
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API")

def llm(system_prompt, query_prompt, parse=True) :
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": f"{system_prompt}"},
                {
                    "role": "user",
                    "content": f"{query_prompt}"
                }
            ]
        )
        if parse:
            return {
                "response": completion.choices[0].message.content,
                "used_prompt_tokens": completion.usage.prompt_tokens,
                "used_completion_tokens": completion.usage.completion_tokens,
                "total_used_tokens": completion.usage.total_tokens,
                "cached_prompt_tokens": completion.usage.prompt_tokens_details.cached_tokens
            }
        return completion
    except Exception as e:
        print(f"An error occurred while calling the OpenAI API: {e}")
        return None

class Describe:
    # Class-level variables are maintained per session, reflecting whole data description task.
    from prompts import DESCRIBE_SYSTEM_PROMPT, DESCRIBE_MAIN_PROMPT
    
    completion_tokens = 0
    prompt_tokens = 0
    cached_tokens = 0
    total_tokens = 0
    total_retry_attempts = 0
    
    def __init__(self, max_retries=5, src_lang="English"): #TODO: Later use ISO 639 language codes instead.. so I will have to map them to the language names 
        self.max_retries = max_retries
        self.src_lang = src_lang
        
    def _parse_analysis(self, text):
        pattern = r'<<(\w+)>>:\s*(.*?)\s*(?=<<\w+>>:|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        parsed_results = {}
        
        for label, content in matches:
            parsed_results[label] = content.strip()
        
        return parsed_results

    def _has_required_tokens(self, parsed_results):
        required_tokens = ["Style", "Tone", "Nuances", "Intent", "CulturalMeaning", "Symbolism"]
        return all(token in parsed_results for token in required_tokens)

    def _get_structured_response(self, prompt, max_retries):
        for attempt in range(max_retries):
            response = llm(system_prompt=self.DESCRIBE_SYSTEM_PROMPT, query_prompt=self.DESCRIBE_MAIN_PROMPT.format(QUERY=prompt, SRC_LANG=self.src_lang))
            
            self.completion_tokens += response["used_completion_tokens"]
            self.prompt_tokens += response["used_prompt_tokens"]
            self.cached_tokens += response["cached_prompt_tokens"]
            self.total_tokens += response["total_used_tokens"]
            
            response_text = response["response"]
            parsed_results = self._parse_analysis(response_text)

            if self._has_required_tokens(parsed_results):
                return parsed_results
            else:
                self.total_retry_attempts += 1
                print(f"Attempt {attempt + 1} failed: Missing tokens, retrying...")

        return None # bad response 😞
    
    def describe(self, prompts: list) -> dict:
        results = []
        
        for prompt in prompts:
            results.append(self._get_structured_response(prompt, self.max_retries))
        
        return {
            "results": results,
            "completion_tokens": self.completion_tokens,
            "prompt_tokens": self.prompt_tokens,
            "cached_tokens": self.cached_tokens,
            "total_tokens": self.total_tokens,
            "total_retry_attempts": self.total_retry_attempts,
            "average_completion_tokens": self.total_retry_attempts / len(prompts)
        }
        
# for translation, I need to differentiate between retry because of bad structured response and retry because of bad translation quality
# add a logic wheter description is exist or not