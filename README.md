# Artinya - LLM Translation Pipeline

## Introduction

The **Artinya** project aims to enhance language translation by integrating advanced language analysis and contextual understanding. Utilizing state-of-the-art language models, this pipeline focuses on maintaining the nuances, tone, and cultural significance of the original text during translation. By employing a structured approach that includes description, translation, and evaluation, this project strives to provide high-quality translations that resonate with the intended audience.

## Methodologies

The pipeline consists of a series of steps designed to ensure accurate and context-aware translations:

1. **Description** (Optional):

   - The source text is analyzed for its style, tone, nuances, intent, cultural meaning, and symbolism. This analysis provides vital context for translation.

2. **Translation**:

   - If a description exists, the translation considers the analyzed attributes to ensure fidelity to the original text. If no description is provided, the text is translated as is.

3. **Evaluation**:
   - Post-translation, each output is evaluated based on criteria such as accuracy, clarity, and preservation of style. This evaluative step ensures that the translation meets the project's quality standards.

## Things That I Am Curious About

- How good is the translation?
- How expensive is the translation?
  - How many API calls?
  - How much re-translation averaging at?
  - How often do the models fail to generate structured output?
- Ablation studies to understand if these whole project is actually necessary or not

## Benchmark Results

coming soon.. ⛔

## TODO

1. Add ISO 639 language code support
2. Benchmarking, ablation studies
3. Pypi
