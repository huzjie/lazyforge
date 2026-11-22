"""embedding —— 零依赖稀疏向量化：分词 + 特征哈希 + TF-IDF + BM25。"""
from .tokenizer import tokenize
from .hashing import HashedVectorizer
from .tfidf import TfidfVectorizer
from .bm25 import BM25
from .vectors import cosine, dot, l2

__all__ = ["tokenize", "HashedVectorizer", "TfidfVectorizer", "BM25", "cosine", "dot", "l2"]
