# backend/train.py
from datasets import Dataset
from transformers import (
    RobertaTokenizer,
    RobertaForSequenceClassification,
    Trainer,
    TrainingArguments
)
import json
from pathlib import Path

MODEL_NAME = "roberta-base"
DATA_FILE = Path("data/training_data.jsonl")
MODEL_OUT = Path("model_out")


def load_custom_dataset(file_path=DATA_FILE):
    texts, labels = [], []
    label_map = {"FAKE": 0, "REAL": 1}

    if not file_path.exists():
        raise ValueError("No training dataset found! Add some data first.")

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            texts.append(record["text"])
            labels.append(label_map[record["label"]])

    if len(texts) < 2:
        raise ValueError("Not enough samples to retrain (need at least 2).")

    return Dataset.from_dict({"text": texts, "label": labels})


def train_model():
    dataset = load_custom_dataset()
    tokenizer = RobertaTokenizer.from_pretrained(MODEL_NAME)

    def tokenize(batch):
        return tokenizer(
            batch["text"], padding="max_length", truncation=True, max_length=256
        )

    dataset = dataset.map(tokenize, batched=True)

    # Split only if enough data
    if len(dataset) > 5:  # need at least a few samples for eval
        dataset = dataset.train_test_split(test_size=0.2)
        train_data = dataset["train"]
        eval_data = dataset["test"]
        eval_strategy = "epoch"
    else:
        train_data = dataset
        eval_data = None
        eval_strategy = "no"

    model = RobertaForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

    training_args = TrainingArguments(
        output_dir=str(MODEL_OUT),
        evaluation_strategy=eval_strategy,
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        num_train_epochs=1,
        weight_decay=0.01,
        logging_dir="logs",
        logging_steps=10,
        save_total_limit=2,  # prevent too many checkpoints
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_data,
        eval_dataset=eval_data,
        tokenizer=tokenizer,
    )

    trainer.train()
    model.save_pretrained(MODEL_OUT)
    tokenizer.save_pretrained(MODEL_OUT)

    return {"status": "success", "message": "Model retrained and saved to model_out"}
