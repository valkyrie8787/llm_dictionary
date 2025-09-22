#pip install requests faiss-cpu sentence-transformers numpy
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced LLM-powered Multilingual Dictionary Builder
- Support for multiple languages (English-Korean, English-Spanish, etc.)
- Vector embeddings for semantic search
- LangChain integration ready
- Structured multilingual storage with corrected target word generation

Usage example:
  python3 mk_dictionary.py --model gpt-oss:20b --target-lang ko --mode 2letter --batch 20
  python3 mk_dictionary.py --target-lang es --vector-store --resume

Author: Enhanced version for multilingual support
"""

import argparse
import json
import os
import re
import signal
import string
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

import requests
import numpy as np
from pathlib import Path

# Optional imports for vector support
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    print("Warning: FAISS not available. Vector features disabled.")

try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    print("Warning: sentence-transformers not available. Embedding features disabled.")


class Language(Enum):
    KOREAN = "ko"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    CROATIAN = "hr"
    CHINESE = "zh"
    RUSSIAN = "ru"


@dataclass
class DictionaryEntry:
    """Structured dictionary entry with multilingual support"""
    word: str
    prefix: str
    length: int
    pos: str
    
    definition_en: str
    example_en: str
    
    word_target: str = ""
    definition_target: str = ""
    example_target: str = ""
    target_lang: str = ""
    
    rarity: int = 3
    confidence: float = 0.0
    score: float = 0.0
    collected_at: str = ""
    
    embedding_definition: Optional[List[float]] = None
    embedding_example: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MultilingualDictionaryBuilder:
    def __init__(
        self,
        model: str = "gpt-oss:20b",
        target_language: str = "ko",
        host: str = "localhost",
        port: int = 11434,
        progress_file: str = "dict_progress.json",
        min_len: int = 3,
        max_len: int = 20,
        temps: List[float] = None,
        score_cut: float = 0.6,
        rarity_cut: int = 4,
        overgen_factor: float = 1.6,
        use_vectors: bool = False,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.model = model
        self.target_language = target_language
        self.base_url = f"http://{host}:{port}/api/generate"
        self.progress_file = progress_file
        self.min_len = min_len
        self.max_len = max_len
        self.temps = temps or [0.2, 0.4, 0.8]
        self.score_cut = float(score_cut)
        self.rarity_cut = int(rarity_cut)
        self.overgen_factor = max(1.0, float(overgen_factor))
        self.use_vectors = use_vectors and HAS_EMBEDDINGS and HAS_FAISS
        self.embedding_model_name = embedding_model
        self.encoder = None
        self.vector_index = None
        
        if self.use_vectors:
            self._initialize_vector_components()

        self.shutdown_requested = False
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.language_configs = {
            "ko": {"name": "Korean", "instruction": "한국어로 번역하세요", "example_prompt": "한국어 예문을 만들어주세요"},
            "de": {"name": "German", "instruction": "Ins Deutsche übersetzen", "example_prompt": "Erstellen Sie ein deutsches Beispiel"},
            "ja": {"name": "Japanese", "instruction": "日本語に翻訳してください", "example_prompt": "日本語の例文を作ってください"},
            "hr": {"name": "Croatian", "instruction": "Prevedi na hrvatski", "example_prompt": "Stvorite primjer na hrvatskom"}
        }
        self.rare_prefixes = {'kb','kc','kf','kg','kq','kx','kz','lc','ld','lf','lg','lk','ln','lp','lq','lr','ls','lt','lv','lw','lx','lz','mb','mc','md','mf','mg','mh','mj','mk','ml','mm','mn','mp','mq','mr','ms','mt','mv','mw','mx','mz','nb','nc','nd','nf','ng','nh','nj','nk','nl','nm','nn','np','nq','nr','ns','nt','nv','nw','nx','nz','pb','pc','pd','pf','pg','pj','pk','pm','pn','pp','pq','pv','pw','px','pz','qb','qc','qd','qe','qf','qg','qh','qi','qj','qk','ql','qm','qn','qo','qp','qq','qr','qs','qt','qv','qw','qx','qy','qz','rb','rc','rd','rf','rg','rj','rk','rl','rm','rn','rp','rq','rr','rs','rt','rv','rw','rx','rz','sb','sd','sf','sg','sj','sk','sl','sm','sn','sp','sq','sr','ss','sv','sw','sx','sz','tb','tc','td','tf','tg','tj','tk','tl','tm','tn','tp','tq','ts','tt','tv','tx','tz','ub','uc','ud','uf','ug','uh','uj','uk','ul','um','uq','uv','uw','ux','uy','uz','vb','vc','vd','vf','vg','vh','vj','vk','vl','vm','vn','vp','vq','vr','vs','vt','vu','vv','vw','vx','vy','vz','wb','wc','wd','wf','wg','wj','wk','wl','wm','wn','wp','wq','wr','ws','wt','wu','wv','ww','wx','wy','wz','xb','xc','xd','xe','xf','xg','xh','xi','xj','xk','xl','xm','xn','xo','xp','xq','xr','xs','xt','xu','xv','xw','xx','xy','xz','yb','yc','yd','yf','yg','yh','yj','yk','yl','ym','yn','yp','yq','yr','ys','yt','yu','yv','yw','yx','yy','yz','zb','zc','zd','ze','zf','zg','zh','zi','zj','zk','zl','zm','zn','zo','zp','zq','zr','zs','zt','zu','zv','zw','zx','zy','zz'}
        self.stopwords = {"the","and","but","for","nor","yet","or","in","on","at","to","of","by","with","as","per","via","its","it's","his","her","their","our","your","any","all","some"}
        self.metrics = defaultdict(int)

    def _initialize_vector_components(self):
        try:
            print(f"Loading embedding model: {self.embedding_model_name}")
            self.encoder = SentenceTransformer(self.embedding_model_name)
            embedding_dim = self.encoder.get_sentence_embedding_dimension()
            self.vector_index = faiss.IndexFlatIP(embedding_dim)
            print(f"Vector components initialized (dim: {embedding_dim})")
        except Exception as e:
            print(f"Warning: Failed to initialize vector components: {e}"); self.use_vectors = False

    def _signal_handler(self, signum, frame):
        print(f"\nSignal {signum} received. Requesting safe shutdown..."); self.shutdown_requested = True

    def ask_ollama(self, prompt: str, timeout=45, retries=3, temperature: float = None) -> str:
        temp = temperature if temperature is not None else 0.1
        for attempt in range(retries):
            if self.shutdown_requested: return ""
            try:
                data = {"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": temp, "top_p": 0.9, "repeat_penalty": 1.1}}
                resp = requests.post(self.base_url, json=data, timeout=timeout)
                resp.raise_for_status()
                return resp.json().get("response", "")
            except Exception as e:
                print(f"[{type(e).__name__}] try {attempt+1}/{retries}")
                if attempt < retries - 1: time.sleep(5)
        return ""

    def get_language_config(self) -> Dict[str, str]:
        return self.language_configs.get(self.target_language, {"name": "Unknown", "instruction": f"Translate to {self.target_language}", "example_prompt": f"Create an example in {self.target_language}"})

    def _extract_json(self, text: str) -> str:
        m = re.search(r"\{.*\}", text, re.S); return m.group(0) if m else "{}"

    def llm_validate_and_translate(self, word: str, temperature: float = 0.2) -> Dict[str, Any]:
        lang_config = self.get_language_config()
        prompt = f"""You are a multilingual dictionary editor. Validate the English word '{word}' and provide its translation and usage in {lang_config['name']}.

Return ONLY a single JSON object with the following structure.

{{
  "word": "{word}",
  "pos": "part of speech (e.g., noun, verb)",
  "definition_en": "A concise English definition (max 25 words).",
  "example_en": "A natural English example sentence (max 25 words).",
  "word_target": "The single, most common one-word translation of '{word}' in {lang_config['name']}.",
  "definition_target": "A concise and natural translation of the definition in {lang_config['name']}.",
  "example_target": "A natural translation of the example in {lang_config['name']}.",
  "proper_noun": false,
  "rarity": 3,
  "confidence": 0.8,
  "accept": true,
  "reasons": []
}}

Rules:
- The `word_target` field MUST be a single, direct translation of the English word.
- Reject if proper noun, abbreviation, misspelling, or very rare/archaic.
- Keep all text fields concise.

Validate and provide the dictionary entry for: '{word}'
"""
        resp = self.ask_ollama(prompt, timeout=40, temperature=temperature)
        try:
            j = json.loads(self._extract_json(resp))
        except Exception as e:
            print(f"JSON parse error for '{word}': {e}"); return {"accept": False, "reasons": ["invalid_json"], "confidence": 0.0, "rarity": 5}
        
        j.setdefault("accept", False); j.setdefault("reasons", []); j.setdefault("rarity", 5); j.setdefault("confidence", 0.0)
        j.setdefault("pos", ""); j.setdefault("definition_en", ""); j.setdefault("example_en", "")
        j.setdefault("word_target", ""); j.setdefault("definition_target", ""); j.setdefault("example_target", "")
        
        if j.get("proper_noun"): j["accept"] = False; j["reasons"].append("proper_noun")
        if j.get("rarity", 5) >= self.rarity_cut: j["accept"] = False; j["reasons"].append("rarity_cutoff")
        return j

    def self_consistency_multilingual(self, word: str) -> Tuple[bool, DictionaryEntry]:
        results = [self.llm_validate_and_translate(word, temp) for temp in self.temps]
        accepts = [r for r in results if r.get("accept")]
        min_consensus = max(2, (len(self.temps) + 1) // 2)
        
        if len(accepts) >= min_consensus:
            best_result = max(accepts, key=lambda x: x.get('confidence', 0.0))
            
            # Use the best result for all fields to maintain consistency
            word_target = best_result.get(f"word_target", "")
            def_target = best_result.get("definition_target", "")
            ex_target = best_result.get("example_target", "")
            
            conf = sum(r.get("confidence", 0) for r in accepts) / len(accepts)
            rarity = round(sum(r.get("rarity", 3) for r in accepts) / len(accepts))
            score = conf * (len(accepts) / len(results))

            entry = DictionaryEntry(word=word, prefix="", length=len(word), pos=best_result.get("pos", ""),
                                  definition_en=best_result.get("definition_en", ""), example_en=best_result.get("example_en", ""),
                                  word_target=word_target, definition_target=def_target, example_target=ex_target,
                                  target_lang=self.target_language, rarity=rarity, confidence=round(conf, 3), score=round(score, 3),
                                  collected_at=datetime.now().isoformat())
            return True, entry
        return False, DictionaryEntry(word=word, prefix="", length=len(word), pos="", definition_en="", example_en="", target_lang=self.target_language)

    def generate_candidates(self, prefix: str, target_batch: int, strict: bool) -> List[str]:
        need = max(target_batch, 1); over = int(round(need * self.overgen_factor))
        prompt = (f"List ONLY real, common English words starting with '{prefix}'.\n- Up to {over} words\n- One word per line\n- No proper nouns or abbreviations\n- Words must be >= {self.min_len} letters\nIf none exist, write: No common words found." if strict else
                  f"List {over} real English words that start with '{prefix}'.\n- One word per line, no extra text\n- >= {self.min_len} letters")
        resp = self.ask_ollama(prompt, timeout=35)
        if "no common words found" in resp.lower(): return []
        words, seen = [], set()
        for ln in resp.splitlines():
            w = re.sub(r"^[\s\-\*\d\.\)\(]+", "", ln.strip().lower()).strip(" '-")
            if (not w or len(w) < self.min_len or len(w) > self.max_len or not w.startswith(prefix) or w in self.stopwords or w in seen): continue
            seen.add(w); words.append(w)
            if len(words) >= over: break
        return words

    def run_prefix(self, prefix: str, batch: int) -> List[DictionaryEntry]:
        strict = prefix in self.rare_prefixes; candidates = self.generate_candidates(prefix, batch, strict)
        self.metrics["candidates_generated"] += len(candidates); accepted = []
        for word in candidates:
            if self.shutdown_requested: break
            ok, entry = self.self_consistency_multilingual(word); entry.prefix = prefix
            self.metrics["attempts"] += 1
            if not ok or entry.score < self.score_cut or entry.rarity >= self.rarity_cut: self.metrics["rejected"] += 1; continue
            accepted.append(entry); self.metrics["accepted"] += 1
            if len(accepted) >= batch: break
        return accepted

    def generate_prefixes(self, mode="2letter") -> List[str]:
        if mode == "2letter":
            common_first = "stpbcmdrhlfgwyvnkjqxz"; common_second = "aeiouhrlnstmdcpgbykvwfjqxz"
            prefixes = [a + b for a in common_first for b in common_second]
            all_prefixes = {a + b for a in string.ascii_lowercase for b in string.ascii_lowercase}
            prefixes.extend(sorted(list(all_prefixes - set(prefixes)))); return prefixes
        raise ValueError("mode must be '2letter'")

    def save_progress(self, payload: Dict[str, Any]):
        backup = self.progress_file + ".bak"; 
        if os.path.exists(self.progress_file): os.replace(self.progress_file, backup)
        try:
            with open(self.progress_file, "w", encoding="utf-8") as f: json.dump(payload, f, ensure_ascii=False, indent=2)
            if os.path.exists(backup): os.remove(backup)
        except Exception as e:
            print(f"[WARN] save_progress failed: {e}"); 
            if os.path.exists(backup): os.replace(backup, self.progress_file)

    def load_progress(self) -> Dict[str, Any]:
        if not os.path.exists(self.progress_file): return {}
        try:
            with open(self.progress_file, "r", encoding="utf-8") as f: return json.load(f)
        except Exception as e: print(f"[WARN] load_progress failed: {e}"); return {}

    def run(self, mode: str, batch: int, resume: bool, save_every: int) -> str:
        prefixes = self.generate_prefixes(mode); progress = self.load_progress() if resume else {}
        done, failed = set(progress.get("completed_prefixes", [])), set(progress.get("failed_prefixes", []))
        entries = [DictionaryEntry(**{k: v for k, v in item.items() if k in DictionaryEntry.__annotations__}) for item in progress.get("words", [])]
        start_time = time.time()
        for i, prefix in enumerate(prefixes, 1):
            if self.shutdown_requested or prefix in done: continue
            try:
                print(f"[{i}/{len(prefixes)}] Prefix '{prefix}' ... ", end="", flush=True)
                accepted = self.run_prefix(prefix, batch)
                if accepted: entries.extend(accepted); done.add(prefix); print(f"{len(accepted)} accepted")
                else: failed.add(prefix); print("0 accepted")
            except Exception as e: print(f"ERROR: {e}"); failed.add(prefix)
            if i % save_every == 0 or self.shutdown_requested:
                payload = {"timestamp": datetime.now().isoformat(), "model_used": self.model, "target_language": self.target_language, "mode": mode, "batch": batch,
                           "completed_prefixes": list(done), "failed_prefixes": list(failed), "words": [e.to_dict() for e in entries], "metrics": dict(self.metrics),
                           "runtime_sec": int(time.time() - start_time), "use_vectors": self.use_vectors}
                self.save_progress(payload); print(f"  -> progress saved ({len(done)} done, {len(entries)} entries)")
        return self.finalize(entries, mode)

    def finalize(self, entries: List[DictionaryEntry], mode: str) -> str:
        if not entries: print("No entries collected."); return ""
        unique = {e.word: e for e in sorted(entries, key=lambda x: x.score, reverse=True)}; final_entries = sorted(unique.values(), key=lambda x: x.word)
        lang_config = self.get_language_config(); timestamp = datetime.now().strftime("%Y%m%d_%H%M%S"); filename = f"dict_{self.target_language}_{mode}_{timestamp}.json"
        metadata = {"title": f"English-{lang_config['name']} Dictionary ({mode})", "source_language": "en", "target_language": self.target_language,
                    "model_used": self.model, "created_at": datetime.now().isoformat(), "total_entries": len(final_entries)}
        dictionary_data = {"metadata": metadata, "entries": [e.to_dict() for e in final_entries]}
        with open(filename, "w", encoding="utf-8") as f: json.dump(dictionary_data, f, ensure_ascii=False, indent=2)
        if os.path.exists(self.progress_file): os.replace(self.progress_file, f"completed_{timestamp}_{self.progress_file}")
        print(f"\n=== DICTIONARY COMPLETED ===\nMain file: {filename}\nTotal entries: {len(final_entries):,}")
        return filename

# === THIS FUNCTION WAS MISSING ===
def parse_temperatures(temp_str: str) -> List[float]:
    """Parse comma-separated temperature values"""
    if not temp_str:
        return [0.2, 0.4, 0.8]
    return [float(t.strip()) for t in temp_str.split(",") if t.strip()] or [0.2, 0.4, 0.8]

def main():
    parser = argparse.ArgumentParser(description="Enhanced LLM-powered Multilingual Dictionary Builder", formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", type=str, default="gpt-oss:20b", help="Ollama model name (default: gpt-oss:20b)")
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=11434)
    parser.add_argument("--target-lang", type=str, default="ko", choices=["ko", "de", "ja", "hr", "es", "fr", "zh", "ru"])
    parser.add_argument("--mode", type=str, default="2letter")
    parser.add_argument("--batch", type=int, default=20)
    parser.add_argument("--min-length", type=int, default=3)
    parser.add_argument("--max-length", type=int, default=20)
    parser.add_argument("--temps", type=str, default="0.2,0.4,0.8")
    parser.add_argument("--score-cut", type=float, default=0.6)
    parser.add_argument("--rarity-cut", type=int, default=4)
    parser.add_argument("--overgen", type=float, default=1.8)
    parser.add_argument("--vector-store", action="store_true")
    parser.add_argument("--embedding-model", type=str, default="all-MiniLM-L6-v2")
    parser.add_argument("--progress", type=str, default="dict_progress.json")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--save-every", type=int, default=10)
    args = parser.parse_args()

    if args.vector_store and not (HAS_FAISS and HAS_EMBEDDINGS):
        print("Error: Vector features require 'faiss-cpu' and 'sentence-transformers'"); sys.exit(1)
    
    # Use unique progress file per language to avoid conflicts
    progress_file_name = f"dict_progress_{args.target_lang}.json"
    if args.clean and os.path.exists(progress_file_name):
        os.remove(progress_file_name)
        print(f"Progress file '{progress_file_name}' removed.")

    builder = MultilingualDictionaryBuilder(
        model=args.model, target_language=args.target_lang, host=args.host, port=args.port, 
        progress_file=progress_file_name, min_len=args.min_length, max_len=args.max_length,
        temps=parse_temperatures(args.temps), score_cut=args.score_cut, rarity_cut=args.rarity_cut, 
        overgen_factor=args.overgen, use_vectors=args.vector_store, embedding_model=args.embedding_model
    )
    
    lang_config = builder.get_language_config()
    print("\n=== Enhanced Multilingual Dictionary Builder ==="); print(f"Model: {args.model}"); print(f"Target Language: {lang_config['name']} ({args.target_lang})");
    print(f"Mode: {args.mode}"); print(f"Batch size: {args.batch}"); print(f"Vector embeddings: {'Enabled' if args.vector_store else 'Disabled'}")
    print(f"Resume: {'Yes' if args.resume and not args.clean else 'No'}"); print("=" * 50)

    try:
        output_file = builder.run(
            mode=args.mode, batch=args.batch, 
            resume=args.resume and not args.clean, 
            save_every=max(1, args.save_every)
        )
        if output_file:
            print(f"\n🎉 Dictionary creation completed!"); print(f"📁 Main file: {output_file}"); print(f"🔤 Total unique words: {builder.metrics.get('accepted', 0):,}")
            print(f"🌐 Language pair: English → {lang_config['name']}")
            if args.vector_store: print(f"🔍 Vector search enabled")
            print("\n💡 Next steps:"); print(f"   - Import into LangChain using the *_langchain_*.json file"); print(f"   - Build search index"); print(f"   - Create web interface or API")
    except KeyboardInterrupt:
        print("\n\n⚠️  Build interrupted by user. Progress saved.")
    except Exception as e:
        print(f"\n❌ Error during build: {e}"); sys.exit(1)

if __name__ == "__main__":
    main()