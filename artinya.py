import csv
from engine import Describe, TranslateEval

class Artinya:
    def __init__(self, src_lang, dest_lang, max_retries=5, descriptions=True, eval=True):
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.max_retries = max_retries
        self.descriptions = descriptions
        self.eval = eval
    
    def pipe(self, prompts: list[str], verbose=True):
        if self.descriptions:
            print("Describing...")
            describer = Describe(src_lang = self.src_lang, max_retries = self.max_retries)
            desc_results = describer.describe(prompts)
        else:
            desc_results = None
        
        print("Translating...")
        translator = TranslateEval(src_lang = self.src_lang, dest_lang = self.dest_lang, max_retries = self.max_retries, descriptions=desc_results)
        translate_results = translator.translate(prompts)
        
        if verbose:
            from tabulate import tabulate
            table_data = [
                ["Description Completion Tokens", desc_results['completion_tokens']],
                ["Description Prompt Tokens", desc_results['prompt_tokens']],
                ["Description Cached Tokens", desc_results['cached_tokens']],
                ["Description Total Tokens", desc_results['total_tokens']],
                ["Description Total Retry Attempts", desc_results['total_retry_attempts']],
                ["Average Description Retry Attempts", desc_results['average_retry_attempts']],
                ["-"*30, "-"*8], 

                ["Translation Completion Tokens", translate_results['translation_completion_tokens']],
                ["Translation Prompt Tokens", translate_results['translation_prompt_tokens']],
                ["Translation Cached Tokens", translate_results['translation_cached_tokens']],
                ["Translation Total Tokens", translate_results['translation_total_tokens']],
                ["Translation Total Retry Attempts", translate_results['translation_total_retry_attempts']],
                ["Average Translation Retry Attempts", translate_results['average_translation_retry_attempts']],
                ["-"*30, "-"*8], 

                ["Evaluation Completion Tokens", translate_results['evaluation_completion_tokens']],
                ["Evaluation Prompt Tokens", translate_results['evaluation_prompt_tokens']],
                ["Evaluation Cached Tokens", translate_results['evaluation_cached_tokens']],
                ["Evaluation Total Tokens", translate_results['evaluation_total_tokens']],
                ["Evaluation Total Retry Attempts", translate_results['evaluation_total_retry_attempts']],
                ["Average Evaluation Retry Attempts", translate_results['average_evaluation_retry_attempts']]
            ]
            print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid"))
            
        return desc_results, translate_results

    def to_csv(self, prompts, translate_results, filename='results.csv'):
        # 2 columns -> original text, translated text
        # translate_result is like this -> {'results': ['Mona Lisa adalah lukisan potret karya Leonardo da Vinci, yang menggambarkan subjek dengan ekspresi yang penuh teka-teki.', 'Ada tiga manhwa 
# yang menurutku benar-benar lucu banget, yaitu Return of the Mount Hua Sect, Return of the Mad Demon, dan Love Advice from the Great Duke of Hell. Yang ketiga adalah yang paling aku rekomendasikan dalam hal humor, tapi ketiga-tiganya itu greay!'], 'translation_completion_tokens': 89, 'translation_prompt_tokens': 1078, 'translation_cached_tokens': 0, 'translation_total_tokens': 1167, 'translation_total_retry_attempts': 0, 'average_translation_completion_tokens': 0.0, 'evaluation_completion_tokens': 46, 'evaluation_prompt_tokens': 651, 'evaluation_cached_tokens': 0, 'evaluation_total_tokens': 697, 'evaluation_total_retry_attempts': 0, 'average_evaluation_completion_tokens': 0.0}
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Original Text", "Translated Text"])
            for idx, result in enumerate(translate_results['results']):
                writer.writerow([prompts[idx], result])
                
if __name__ == "__main__":
    artinya = Artinya(src_lang='english', dest_lang='indonesia', max_retries=5, descriptions=True, eval=True)
    prompts = [
        "The Mona Lisa is a portrait painting by Leonardo da Vinci, depicting the subject with an enigmatic expression.",
        "There is three manhwa that i find genuinely as funny as ged they are return of the mount hua sect ,return of the mad demon and love advice from the great duke of hell. The third one is the one i recommend the most in therm of humor but the three are greay",
    ]
    desc_results, translate_results = artinya.pipe(prompts)
    
    with open ("desc.txt", "w") as f:
        f.write(str(desc_results))
    
    with open ("translate.txt", "w") as f:
        f.write(str(translate_results))
    
    artinya.to_csv(prompts, translate_results)