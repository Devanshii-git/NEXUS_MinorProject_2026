import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import DistilBertTokenizer

# Default pre-trained tokenizer
TOKENIZER_NAME = "distilbert-base-uncased"


class RequirementDataset(Dataset):
    def __init__(
        self,
        csv_path: str,
        tokenizer: DistilBertTokenizer | None = None,
        max_length: int = 128,
    ):
        # Load CSV data
        self.data = pd.read_csv(csv_path)
        self.sentences = self.data["sentence"].tolist()
        self.labels = self.data["label"].tolist()

        # Initialise tokenizer
        self.tokenizer = tokenizer or DistilBertTokenizer.from_pretrained(
            TOKENIZER_NAME
        )
        self.max_length = max_length

    # Standard PyTorch Dataset interface
    def __len__(self) -> int:
        return len(self.sentences)

    def __getitem__(self, idx: int) -> dict:
        sentence = str(self.sentences[idx])
        label = int(self.labels[idx])

        # Tokenise with padding and truncation
        encoding = self.tokenizer.encode_plus(
            sentence,
            add_special_tokens=True,     
            max_length=self.max_length,
            padding="max_length",        
            truncation=True,              
            return_attention_mask=True,
            return_tensors="pt",          
        )

        return {
            "input_ids": encoding["input_ids"].squeeze(0),        # [max_length]
            "attention_mask": encoding["attention_mask"].squeeze(0),  # [max_length]
            "labels": torch.tensor(label, dtype=torch.long),
        }
