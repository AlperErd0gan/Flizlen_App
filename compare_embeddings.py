import os
import google.generativeai as genai
import numpy as np
from dotenv import load_dotenv
import re
import math
from collections import Counter

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=api_key)

# --- Model Definitions ---

class GeminiEmbeddingModel:
    def __init__(self, model_name):
        self.name = model_name
        self.type = "AI / Deep Learning"
        
    def get_score(self, text1, text2):
        try:
            v1 = self._embed(text1)
            v2 = self._embed(text2)
            
            if v1 is None or v2 is None:
                return 0.0
                
            return self._cosine_similarity(v1, v2)
        except Exception as e:
            return 0.0

    def _embed(self, text):
        try:
            result = genai.embed_content(
                model=self.name,
                content=text,
                task_type="retrieval_document"
            )
            return np.array(result['embedding'])
        except:
            return None

    def _cosine_similarity(self, v1, v2):
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        return np.dot(v1, v2) / (norm_v1 * norm_v2)

class TfidfBaselineModel:
    def __init__(self):
        self.name = "Statistical Baseline (TF-IDF)"
        self.type = "Statistical / N-Gram"
        # A tiny corpus to calculate "Inverse Document Frequency" (IDF)
        # If a word is rare (like "domates"), it has high weight.
        # If a word is common (like "ve"), it has low weight.
        self.corpus = [
            "domates biber patlıcan sebze meyve",
            "tarım ziraat çiftçi toprak hasat ekim",
            "bitcoin kripto para borsa ekonomi finans",
            "futbol spor maç gol skor şampiyon",
            "bitki hastalık zararlı ilaç gübre",
        ]
        self.idf_map = self._build_idf_map()

    def _build_idf_map(self):
        idf = {}
        total_docs = len(self.corpus)
        all_words = set()
        for doc in self.corpus:
            all_words.update(self._tokenize(doc))
        
        for word in all_words:
            # Count docs containing word
            doc_count = sum(1 for doc in self.corpus if word in self._tokenize(doc))
            # IDF = log(Total / Count)
            idf[word] = math.log(total_docs / (1 + doc_count))
        return idf

    def get_score(self, text1, text2):
        vec1 = self._vectorize(text1)
        vec2 = self._vectorize(text2)
        return self._cosine_similarity(vec1, vec2)

    def _tokenize(self, text):
        return re.findall(r'\w+', text.lower())

    def _vectorize(self, text):
        # Create a vector based on all known words in both texts + corpus
        tokens = self._tokenize(text)
        tf = Counter(tokens)
        vector = {}
        for word, count in tf.items():
            # TF-IDF = (Count/TotalWords) * IDF
            tf_val = count / len(tokens)
            idf_val = self.idf_map.get(word, 1.0) # Default IDF for unknown words
            vector[word] = tf_val * idf_val
        return vector

    def _cosine_similarity(self, vec1, vec2):
        # Dot product of sparse vectors (dicts)
        common_words = set(vec1.keys()) & set(vec2.keys())
        dot = sum(vec1[word] * vec2[word] for word in common_words)
        
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

# --- Configuration ---

models_to_test = [
    TfidfBaselineModel(),
    GeminiEmbeddingModel("models/text-embedding-004")
]

scenarios = [
    {
        "name": "Agriculture Context",
        "anchor": "Domates fidesi ne zaman ekilir?", 
        "positive": "Bahçede sebze yetiştiriciliği ve tohum ekim zamanları", 
        "negative": "Kripto para piyasalarında son durum ve bitcoin analizi"
    },
    {
        "name": "Plant Health",
        "anchor": "Yapraklarda sararma ve lekeler var",
        "positive": "Bitki hastalıkları ve zararlıları ile mücadele yöntemleri",
        "negative": "Formula 1 yarışlarında bu hafta kim kazandı"
    }
]

print(f"{'='*60}")
print(f"Embedding Comparison: Statistical vs AI")
print(f"{'='*60}\n")

results = {}

for model in models_to_test:
    print(f"Testing Model: {model.name} [{model.type}]")
    print(f"{'-'*40}")
    
    model_score = 0
    
    for scenario in scenarios:
        sim_pos = model.get_score(scenario['anchor'], scenario['positive'])
        sim_neg = model.get_score(scenario['anchor'], scenario['negative'])
        
        separation = sim_pos - sim_neg
        model_score += separation
        
        print(f"\n   Scenario: {scenario['name']}")
        print(f"   Anchor: '{scenario['anchor'][:30]}...'")
        print(f"   Related Sim:   {sim_pos:.4f}")
        print(f"   Unrelated Sim: {sim_neg:.4f}")
        print(f"   Separation:    {separation:.4f}")

    results[model.name] = model_score
    print(f"\n   Total Separation Score: {model_score:.4f}")
    print(f"{'='*60}\n")

# --- Conclusion ---
print(f"Final Verdict")

if not results:
    print("All models failed.")
else:
    best_model = max(results, key=results.get)
    print(f"Best Performing Model: {best_model}")

    if "text-embedding-004" in best_model:
        print("\nSUCCESS: The AI Embedding model (text-embedding-004) proved to be superior.")
        print("This validates that Vector Embeddings capture meaning better than statistical word analysis (TF-IDF).")
    else:
        print("\nNOTICE: The Statistical model performed surprisingly well.")
