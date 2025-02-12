---
library_name: transformers
tags:
- BERT
- Transformers
- BETO
- Clickbait
license: mit
language:
- es
pipeline_tag: text-classification
---

# BETO Spanish Clickbaits Model 

This clickbait analysis model is based on the BETO, a Spanish variant of BERT. 

## Model Details

BETO is a BERT model trained on a big Spanish corpus. BETO is of size similar to a BERT-Base and was trained with the Whole Word Masking technique.

[BETO huggingface](https://huggingface.co/dccuchile/bert-base-spanish-wwm-cased)

Model fine-tuned with a news (around ~30k) of several Spanish Newspapers.

## Training evaluate

Using transformers

```
BATCH_SIZE = 100
NUM_PROCS = 32
LR = 0.00005
EPOCHS = 5
MAX_LENGTH = 25
MODEL = 'dccuchile/bert-base-spanish-wwm-cased'

{'eval_loss': 0.0386480949819088,
 'eval_accuracy': 0.9872786230980294,
 'eval_runtime': 10.0476,
 'eval_samples_per_second': 398.999,
 'eval_steps_per_second': 4.081,
 'epoch': 5.0}
```

## Uses

This model is designed to classify newspaper news as clickbaits or not. 

You can see a use case in this url:
[Spanish Newspapers](https://clickbait.taniwa.es/)

### Direct Use

```
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TextClassificationPipeline,
)

tokenizer = AutoTokenizer.from_pretrained("taniwasl/clickbait_es")
model = AutoModelForSequenceClassification.from_pretrained("taniwasl/clickbait_es")

review_text = 'La explosión destruye parcialmente el edificio, Egipto'

nlp = TextClassificationPipeline(task = "text-classification",
                model = model,
                tokenizer = tokenizer,
                max_length = 25,
                truncation=True,
                add_special_tokens=True
                )

print(nlp(review_text))
```

## License Disclaimer

The license MIT best describes our intentions for our work. 
However we are not sure that all the datasets used to train BETO have licenses compatible with MIT (specially for commercial use). 
Please use at your own discretion only for no commercial use.