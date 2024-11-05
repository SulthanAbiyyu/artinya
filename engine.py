import re
import os
from openai import OpenAI
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

    def _get_structured_response(self, prompt):
        for attempt in range(self.max_retries):
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
                print(f"Attempt {attempt + 1}/{self.max_retries} | failed: Missing tokens, retrying...")

        return None # bad response 😞
    
    def describe(self, prompts: list) -> dict:
        results = []
        
        for prompt in prompts:
            results.append(self._get_structured_response(prompt))
        
        return {
            "results": results,
            "completion_tokens": self.completion_tokens,
            "prompt_tokens": self.prompt_tokens,
            "cached_tokens": self.cached_tokens,
            "total_tokens": self.total_tokens,
            "total_retry_attempts": self.total_retry_attempts,
            "average_retry_attempts": self.total_retry_attempts / len(prompts)
        }
        
class TranslateEval:
    # Class-level variables are maintained per session, reflecting whole data description task.
    from prompts import (
            TRANSLATE_SYSTEM_PROMPT, 
            TRANSLATE_MAIN_PROMPT, 
            TRANSLATE_MAIN_NO_DESC_PROMPT,
            EVALUATE_SYSTEM_PROMPT,
            EVALUATE_MAIN_PROMPT
        )

    translation_completion_tokens = 0
    translation_prompt_tokens = 0
    translation_cached_tokens = 0
    translation_total_tokens = 0
    translation_total_retry_attempts = 0
    
    eval_completion_tokens = 0
    eval_prompt_tokens = 0
    eval_cached_tokens = 0
    eval_total_tokens = 0
    eval_total_retry_attempts = 0
    
    def __init__(self, src_lang, dest_lang, descriptions=None, max_retries=5, eval=True):
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.max_retries = max_retries
        self.eval = eval
        self.descriptions = descriptions
        
        if self.descriptions is not None: 
            self.TRANSLATE_MAIN_PROMPT = self.TRANSLATE_MAIN_PROMPT
        else:
            self.TRANSLATE_MAIN_PROMPT = self.TRANSLATE_MAIN_NO_DESC_PROMPT
    
    def _translate(self, src_lang, dest_lang, query, description):
        if self.descriptions is not None:
            query_prompt = self.TRANSLATE_MAIN_PROMPT.format(SRC_LANG = src_lang, DEST_LANG = dest_lang, QUERY = query, DESCRIPTION = description)
        else:
            query_prompt = self.TRANSLATE_MAIN_PROMPT.format(SRC_LANG = src_lang, DEST_LANG = dest_lang, QUERY = query)
            
        if self.eval:
            for attempt in range(self.max_retries):
                response = llm(
                                    system_prompt=self.TRANSLATE_SYSTEM_PROMPT, 
                                    query_prompt=query_prompt
                                )
                
                self.translation_completion_tokens += response["used_completion_tokens"]
                self.translation_prompt_tokens += response["used_prompt_tokens"]
                self.translation_cached_tokens += response["cached_prompt_tokens"]
                self.translation_total_tokens += response["total_used_tokens"]
                
                response_text = response["response"]
                eval_result = self._evaluate(query, response_text)
                
                if eval_result == "Translation Passed":
                    return response_text
                else:
                    self.translation_total_retry_attempts += 1
                    print(f"Attempt {attempt + 1}/{self.max_retries} | failed: Bad translation, retrying...")
                    
        else:
            response = llm(
                            system_prompt=self.TRANSLATE_SYSTEM_PROMPT, 
                            query_prompt=query_prompt
                        )
            
            self.translation_completion_tokens += response["used_completion_tokens"]
            self.translation_prompt_tokens += response["used_prompt_tokens"]
            self.translation_cached_tokens += response["cached_prompt_tokens"]
            self.translation_total_tokens += response["total_used_tokens"]
            
            return response["response"]
    
    def _evaluate(self, query, translation):
        for attempt in range(self.max_retries):
            response = llm(
                            system_prompt=self.EVALUATE_SYSTEM_PROMPT, 
                            query_prompt=self.EVALUATE_MAIN_PROMPT.format(SRC_LANG=self.src_lang, DEST_LANG=self.dest_lang, QUERY=query, TRANSLATION=translation)
                        )
            self.eval_completion_tokens += response["used_completion_tokens"]
            self.eval_prompt_tokens += response["used_prompt_tokens"]
            self.eval_cached_tokens += response["cached_prompt_tokens"]
            self.eval_total_tokens += response["total_used_tokens"]
            
            response_text = response["response"]
            parsed_results = self._parse_evaluation(response_text)
            
            if self._has_required_eval_tokens(parsed_results):
                return self._score_evaluation(parsed_results)
            else:
                self.eval_total_retry_attempts += 1
                print(f"Attempt {attempt + 1}/{self.max_retries} | failed: Missing tokens, retrying...")
    
    def _has_required_eval_tokens(self, parsed_results):
        required_tokens = ["Accuracy", "Clarity", "StyleAndTone"]
        return all(token in parsed_results for token in required_tokens)
    
    def _parse_evaluation(self, response):
        pattern = r'<<(\w+)>>:\s*(.*?)\s*(?=<<\w+>>:|$)'
        matches = re.findall(pattern, response, re.DOTALL)
        
        parsed_results = {}
        
        for label, content in matches:
            parsed_results[label] = content.strip().strip('"')
        
        return parsed_results

    def _score_evaluation(self, parsed_results):
        score = 0
        for key in ['Accuracy', 'Clarity', 'StyleAndTone']:
            if parsed_results.get(key, '').lower().replace("\n", "").replace("-", "") == 'yes':
                score += 1
        if score >= 2:
            return "Translation Passed"
        else:
            return "Translation Failed"
        
    def _stringify_description(self, description):
        return f"Style: {description['Style']}\nTone: {description['Tone']}\nNuances: {description['Nuances']}\nIntent: {description['Intent']}\nCultural Meaning: {description['CulturalMeaning']}\nSymbolism: {description['Symbolism']}"
    
    def translate(self, queries: list) -> dict:
        results = []
        
        for idx, query in enumerate(queries):
            if self.descriptions is not None:
                description = self._stringify_description(self.descriptions["results"][idx])
            else:
                description = None
                
            results.append(self._translate(self.src_lang, self.dest_lang, query, description))
        
        return {
            "results": results,
            "translation_completion_tokens": self.translation_completion_tokens,
            "translation_prompt_tokens": self.translation_prompt_tokens,
            "translation_cached_tokens": self.translation_cached_tokens,
            "translation_total_tokens": self.translation_total_tokens,
            "translation_total_retry_attempts": self.translation_total_retry_attempts,
            "average_translation_retry_attempts": self.translation_total_retry_attempts / len(queries),
            "evaluation_completion_tokens": self.eval_completion_tokens,
            "evaluation_prompt_tokens": self.eval_prompt_tokens,
            "evaluation_cached_tokens": self.eval_cached_tokens,
            "evaluation_total_tokens": self.eval_total_tokens,
            "evaluation_total_retry_attempts": self.eval_total_retry_attempts,
            "average_evaluation_retry_attempts": self.eval_total_retry_attempts / len(queries)
        }