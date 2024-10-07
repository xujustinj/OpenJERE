from abc import ABC, abstractmethod
from collections import Counter
from functools import cached_property
import json
import os
from typing import Dict, List, Optional

from openjere.config import Hyper
from openjere.config.const import (
    PAD,
    OOV,
    EOS,
    SEP_SEMICOLON,
    NO_RELATION,
    SEP_VERTICAL_BAR,
)


class AbstractPreprocessor(ABC):
    def __init__(self, hyper: Hyper):
        self.hyper = hyper
        self.raw_data_root = hyper.raw_data_root
        self.data_root = hyper.data_root

        if not os.path.exists(self.data_root):
            os.makedirs(self.data_root)

    @cached_property
    def relation_vocab(self) -> Dict[str, int]:
        if not os.path.exists(self.hyper.relation_vocab_path):
            self.gen_relation_vocab()
        return self.hyper.rel2id

    # model
    @abstractmethod
    def _read_line(self, line: str) -> Optional[str]:
        raise NotImplementedError

    # model
    @abstractmethod
    def _check_valid(self, text: str, spo_list: List[Dict[str, str]]) -> bool:
        raise NotImplementedError

    # model
    def gen_all_data(self):
        for path in self.hyper.raw_data_list:
            self._gen_one_data(path)

    # model
    def _gen_one_data(self, dataset):
        source = os.path.join(self.raw_data_root, dataset)
        target = os.path.join(self.data_root, dataset)
        with open(source, "r", encoding="utf-8") as s,\
            open(target, "w", encoding="utf-8") as t:
            for line in s:
                line = line.strip("\n")
                if line == "":
                    continue
                newline = self._read_line(line)
                if newline is not None:
                    t.write(newline)
                    t.write("\n")

    # model
    def gen_bio_vocab(self):
        result = {PAD: 3, "B": 0, "I": 1, "O": 2}
        with open(self.hyper.bio_vocab_path, "w") as f:
            json.dump(result, f)

    def gen_vocab(
        self,
        min_freq: int,
        init_result: Dict[str, int] = {
            PAD: 0,
            EOS: 1,
            SEP_VERTICAL_BAR: 2,
            SEP_SEMICOLON: 3,
        },
    ):
        # might contain sos, eos, pad ....
        source = os.path.join(self.raw_data_root, self.hyper.train)
        target = self.hyper.word_vocab_path

        cnt = Counter()

        for text in self.yield_key(source, "text"):
            cnt.update(self.hyper.tokenizer(text))

        result = init_result
        i = len(init_result)
        assert max(init_result.values()) == i - 1
        for k, v in cnt.items():
            if v > min_freq:
                result[k] = i
                i += 1
        result[OOV] = i
        assert len(result) == i + 1
        with open(self.hyper.word_vocab_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False)

    def spo_to_entities(self, text: str, spo_list: List[Dict[str, str]]) -> List[str]:
        entities = set(t["object"] for t in spo_list) | set(
            t["subject"] for t in spo_list
        )
        return list(entities)

    def spo_to_relations(self, text: str, spo_list: List[Dict[str, str]]) -> List[str]:
        return [t["predicate"] for t in spo_list]

    def gen_relation_vocab(self):
        relation_vocab = {}
        rel_set = set()
        source = os.path.join(self.raw_data_root, self.hyper.train)

        for spo_list in self.yield_key(source, "spo_list"):
            rel_set.update(self.spo_to_relations("", spo_list))

        relation_vocab = {k: v for v, k in enumerate(rel_set)}
        relation_vocab[NO_RELATION] = len(relation_vocab)
        with open(self.hyper.relation_vocab_path, "w", encoding="utf-8") as f:
            json.dump(relation_vocab, f, ensure_ascii=False)

    def yield_key(self, source: str, key: str):
        with open(source, "r", encoding="utf-8") as s:
            for line in s:
                line = line.strip("\n")
                if not line:
                    return None
                instance = json.loads(line)
                value = instance[key]
                yield value
