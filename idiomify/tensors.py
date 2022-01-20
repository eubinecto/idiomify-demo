"""
all the functions for building tensors are defined here.
builders must accept device as one of the parameters.
"""
import torch
from typing import List
from transformers import BertTokenizer


def idiom2subwords(idioms: List[str], tokenizer: BertTokenizer, k: int) -> torch.Tensor:
    mask_id = tokenizer.mask_token_id
    pad_id = tokenizer.pad_token_id
    # temporarily disable single-token status of the wisdoms
    wisdoms = [idiom.split(" ") for idiom in idioms]
    encodings = tokenizer(text=wisdoms,
                          add_special_tokens=False,
                          # should set this to True, as we already have the wisdoms split.
                          is_split_into_words=True,
                          padding='max_length',
                          max_length=k,  # set to k
                          return_tensors="pt")
    input_ids = encodings['input_ids']
    input_ids[input_ids == pad_id] = mask_id  # replace them with masks
    return input_ids


def inputs(definitions: List[str], tokenizer: BertTokenizer, k: int) -> torch.Tensor:
    lefts = [" ".join(["[MASK]"] * k)] * len(definitions)
    encodings = tokenizer(text=lefts,
                          text_pair=definitions,
                          return_tensors="pt",
                          add_special_tokens=True,
                          truncation=True,
                          padding=True,
                          verbose=True)
    input_ids: torch.Tensor = encodings['input_ids']
    cls_id: int = tokenizer.cls_token_id
    sep_id: int = tokenizer.sep_token_id
    mask_id: int = tokenizer.mask_token_id

    wisdom_mask = torch.where(input_ids == mask_id, 1, 0)
    desc_mask = torch.where(((input_ids != cls_id) & (input_ids != sep_id) & (input_ids != mask_id)), 1, 0)
    return torch.stack([input_ids,
                        encodings['token_type_ids'],
                        encodings['attention_mask'],
                        wisdom_mask,
                        desc_mask], dim=1)


def targets(idioms: List[str]) -> torch.Tensor:
    return torch.LongTensor([
        idioms.index(idiom)
        for idiom in idioms
    ])

