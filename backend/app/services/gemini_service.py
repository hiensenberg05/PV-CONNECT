# import os
# from functools import lru_cache
# from app.config import GEMINI_API_KEY





# try:
#     from groq import GroqClient  # type: ignore
#     _HAS_GROQ_SDK = True
# except Exception:


#     _HAS_GROQ_SDK = False
# import hashlib
# import json


# import threading
# import time
# import queue


# # Lightweight rate-limiter / serial executor
# class RateLimitedExecutor:
#     def __init__(self, requests_per_minute: int = 60):
#         self._q = queue.Queue()
#         self._interval = 60.0 / max(1, requests_per_minute)
#         self._thread = threading.Thread(target=self._worker, daemon=True)
#         self._thread.start()

#     def submit(self, fn):
#         ev = threading.Event()
#         container = {"result": None, "exc": None}
#         self._q.put((fn, ev, container))
#         ev.wait()
#         if container["exc"]:
#             raise container["exc"]
#         return container["result"]

#     def _worker(self):
#         while True:
#             fn, ev, container = self._q.get()
#             try:
#                 container["result"] = fn()
#             except Exception as e:
#                 container["exc"] = e
#             finally:
#                 try:
#                     ev.set()
#                 except Exception:
#                     pass
#                 self._q.task_done()
#             time.sleep(self._interval)


# class SimpleResponse:
#     """Minimal response wrapper so callers can use `response.text` like before."""
#     def __init__(self, text: str):
#         self.text = text


# class GroqHTTPClient:
#     """Very small HTTP client to call Groq inference endpoint.

#     This implementation is intentionally minimal: it expects an environment
#     variable `GROQ_API_KEY` (falls back to `GEMINI_API_KEY`) and will POST a
#     JSON body with the prompt. Adjust the URL/contract if your Groq setup is
#     different.
#     """

#     def __init__(self, api_key: str = None, base_url: str = "https://api.groq.com/v1"):
#         self.api_key = api_key or os.getenv("GROQ_API_KEY") or GEMINI_API_KEY
#         self.base_url = base_url

#     def generate(self, prompt: str, **kwargs) -> SimpleResponse:
#         import requests

#         if not self.api_key:
#             raise RuntimeError("No GROQ API key configured (GROQ_API_KEY or GEMINI_API_KEY)")

#         # Endpoint and payload may vary; this is a reasonable default.
#         url = f"{self.base_url}/models/default:predict"
#         payload = {"prompt": prompt, "max_output_tokens": kwargs.get("max_output_tokens", 512)}
#         headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

#         r = requests.post(url, json=payload, headers=headers, timeout=60)
#         r.raise_for_status()
#         data = r.json()

#         # Attempt to find a text field in the response; adapt if your API differs.
#         text = None
#         if isinstance(data, dict):
#             # common field names
#             for key in ("output", "text", "result", "prediction"):
#                 if key in data and isinstance(data[key], str):
#                     text = data[key]
#                     break
#             # nested output
#             if text is None:
#                 out = data.get("output") or data.get("result") or data.get("predictions")
#                 if isinstance(out, list) and out:
#                     first = out[0]
#                     if isinstance(first, dict):
#                         # try typical chain-of-thought field names
#                         for k in ("text", "content", "answer"):
#                             if k in first and isinstance(first[k], str):
#                                 text = first[k]
#                                 break
#                     elif isinstance(first, str):
#                         text = first
#         if text is None:
#             # fallback to raw JSON
#             text = json.dumps(data)

#         return SimpleResponse(text)

# class GroqModel:
#     """Adapter so callers can call `generate_content(prompt)` similar to
#     Google `GenerativeModel.generate_content`.
#     """

#     def __init__(self, client):
#         self._client = client

#     def generate_content(self, prompt, **kwargs):
#         # delegate to HTTP client or SDK and return SimpleResponse-like object
#         if _HAS_GROQ_SDK:
#             # If the SDK exists, try to call its predict method; adapt as needed.
#             try:
#                 res = self._client.predict(prompt, **kwargs)
#                 # try to extract text
#                 text = None
#                 if hasattr(res, "text"):
#                     text = res.text
#                 elif isinstance(res, dict):
#                     text = res.get("output") or res.get("text") or json.dumps(res)
#                 else:
#                     text = str(res)
#                 return SimpleResponse(text)
#             except Exception as e:  # pragma: no cover - SDK-specific
#                 raise
#         else:
#             return self._client.generate(prompt, **kwargs)

# class CachedModel:
#     """Preserve previous caching + dedupe + rate-limit behavior but backed by
#     GroqModel instead of Google GenerativeModel.
#     """

#     def __init__(self, model, ttl: int = 300, requests_per_minute: int = 60):
#         self._model = model
#         self._ttl = ttl
#         self._cache = {}  # key -> (response, expiry_ts)
#         self._lock = threading.Lock()
#         self._inflight = {}  # key -> threading.Event
#         self._executor = RateLimitedExecutor(requests_per_minute=requests_per_minute)

#     def _key(self, prompt: str, **kwargs) -> str:
#         normalized = prompt.strip()
#         if kwargs:
#             try:
#                 normalized += "|" + json.dumps(kwargs, sort_keys=True)
#             except Exception:
#                 normalized += "|"
#         return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

#     def generate_content(self, prompt: str, **kwargs):
#         key = self._key(prompt, **kwargs)
#         now = time.time()

#         with self._lock:
#             item = self._cache.get(key)
#             if item and item[1] > now:
#                 return item[0]
#             ev = self._inflight.get(key)
#             if ev:
#                 ev.wait()
#                 item = self._cache.get(key)
#                 if item:
#                     return item[0]
#             else:
#                 ev = threading.Event()
#                 self._inflight[key] = ev

#         def call_model():
#             return self._model.generate_content(prompt, **kwargs)

#         response = self._executor.submit(call_model)

#         with self._lock:
#             self._cache[key] = (response, now + self._ttl)
#             ev.set()
#             self._inflight.pop(key, None)

#         return response

# @lru_cache(maxsize=1)
# def get_client():
#     """Return a Groq client instance or HTTP client fallback."""
#     if _HAS_GROQ_SDK:
#         # attempt to initialize SDK client using GROQ_API_KEY or GEMINI_API_KEY
#         api_key = os.getenv("GROQ_API_KEY") or GEMINI_API_KEY
#         return GroqClient(api_key=api_key)  # type: ignore
#     else:
#         return GroqHTTPClient(api_key=os.getenv("GROQ_API_KEY") or GEMINI_API_KEY)

# @lru_cache(maxsize=4)
# def get_model(name: str = "models/gemini-flash-latest", ttl: int = 300, rpm: int = 60):
#     """Return a CachedModel backed by Groq. `name` is accepted for
#     compatibility but may be ignored depending on Groq setup.
#     """
#     client = get_client()
#     # If SDK present, wrap SDK client; otherwise wrap HTTP client
#     base = GroqModel(client)
#     return CachedModel(base, ttl=ttl, requests_per_minute=rpm)


# 

# import os
# import time
# import queue
# import hashlib
# import threading
# import requests
# from functools import lru_cache


# # ---------------- Rate Limiter ----------------
# class RateLimitedExecutor:
#     def __init__(self, requests_per_minute: int = 30):
#         self._q = queue.Queue()
#         self._interval = 60.0 / max(1, requests_per_minute)
#         self._thread = threading.Thread(target=self._worker, daemon=True)
#         self._thread.start()

#     def submit(self, fn):
#         ev = threading.Event()
#         box = {"result": None, "exc": None}
#         self._q.put((fn, ev, box))
#         ev.wait()
#         if box["exc"]:
#             raise box["exc"]
#         return box["result"]

#     def _worker(self):
#         while True:
#             fn, ev, box = self._q.get()
#             try:
#                 box["result"] = fn()
#             except Exception as e:
#                 box["exc"] = e
#             finally:
#                 ev.set()
#                 self._q.task_done()
#             time.sleep(self._interval)


# # ---------------- Response Wrapper ----------------
# class SimpleResponse:
#     def __init__(self, text: str):
#         self.text = text


# # ---------------- Groq Client ----------------
# class GroqClient:
#     def __init__(self, api_key: str):
#         if not api_key:
#             raise RuntimeError("GROQ_API_KEY not set")
#         self.api_key = api_key
#         self.url = "https://api.groq.com/openai/v1/chat/completions"

#     def generate(self, prompt: str, max_tokens: int = 128) -> SimpleResponse:
#         # 🔐 SAFETY: ensure prompt is valid
#         prompt = (prompt or "").strip()
#         if not prompt:
#             prompt = "Hello"

#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json",
#         }

#         payload = {
#             "model": "llama-3.3-70b-versatile",
#             "messages": [
#                 {"role": "user", "content": prompt}
#             ],
#             "temperature": 0,
#             "max_tokens": max_tokens,
#         }

#         r = requests.post(self.url, json=payload, headers=headers, timeout=60)
#         r.raise_for_status()

#         data = r.json()
#         text = data["choices"][0]["message"]["content"]
#         return SimpleResponse(text)


# # ---------------- Cached Model ----------------
# class CachedModel:
#     def __init__(self, client: GroqClient, ttl: int = 300, rpm: int = 30):
#         self.client = client
#         self.ttl = int(ttl)
#         self.cache = {}
#         self.lock = threading.Lock()
#         self.inflight = {}
#         self.executor = RateLimitedExecutor(rpm)

#     def _key(self, prompt: str) -> str:
#         return hashlib.sha256((prompt or "").strip().encode()).hexdigest()

#     def generate_content(self, prompt: str, **kwargs):
#         key = self._key(prompt)
#         now = time.time()

#         with self.lock:
#             if key in self.cache and self.cache[key][1] > now:
#                 return self.cache[key][0]

#             if key in self.inflight:
#                 self.inflight[key].wait()
#                 return self.cache[key][0]

#             ev = threading.Event()
#             self.inflight[key] = ev

#         def call():
#             return self.client.generate(prompt)

#         response = self.executor.submit(call)

#         with self.lock:
#             self.cache[key] = (response, now + self.ttl)
#             ev.set()
#             self.inflight.pop(key, None)

#         return response


# # ---------------- Public Factory ----------------
# @lru_cache(maxsize=1)
# def get_model(ttl: int = 300, rpm: int = 30):
#     api_key = os.getenv("GROQ_API_KEY")
#     return CachedModel(GroqClient(api_key), ttl=ttl, rpm=rpm)



import os
import time
import queue
import hashlib
import threading
import requests
from functools import lru_cache


# ---------------- Rate Limiter ----------------
class RateLimitedExecutor:
    def __init__(self, requests_per_minute: int = 30):
        self._q = queue.Queue()
        self._interval = 60.0 / max(1, requests_per_minute)
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def submit(self, fn):
        ev = threading.Event()
        box = {"result": None, "exc": None}
        self._q.put((fn, ev, box))
        ev.wait()
        if box["exc"]:
            raise box["exc"]
        return box["result"]

    def _worker(self):
        while True:
            fn, ev, box = self._q.get()
            try:
                box["result"] = fn()
            except Exception as e:
                box["exc"] = e
            finally:
                ev.set()
                self._q.task_done()
            time.sleep(self._interval)


# ---------------- Response Wrapper ----------------
class SimpleResponse:
    def __init__(self, text: str):
        self.text = text


# ---------------- Groq Client ----------------
class GroqClient:
    def __init__(self, api_key: str, model: str):
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set")
        self.api_key = api_key
        self.model = model
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, prompt: str, max_tokens: int = 128) -> SimpleResponse:
        prompt = (prompt or "").strip() or "Hello"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,   # ✅ now dynamic
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0,
            "max_tokens": max_tokens,
        }

        r = requests.post(self.url, json=payload, headers=headers, timeout=60)
        r.raise_for_status()

        data = r.json()
        text = data["choices"][0]["message"]["content"]
        return SimpleResponse(text)


# ---------------- Cached Model ----------------
class CachedModel:
    def __init__(self, client: GroqClient, ttl: int = 300, rpm: int = 30):
        self.client = client
        self.ttl = int(ttl)
        self.cache = {}
        self.lock = threading.Lock()
        self.inflight = {}
        self.executor = RateLimitedExecutor(rpm)

    def _key(self, prompt: str) -> str:
        return hashlib.sha256((prompt or "").strip().encode()).hexdigest()

    def generate_content(self, prompt: str, **kwargs):
        key = self._key(prompt)
        now = time.time()

        with self.lock:
            if key in self.cache and self.cache[key][1] > now:
                return self.cache[key][0]

            if key in self.inflight:
                self.inflight[key].wait()
                return self.cache[key][0]

            ev = threading.Event()
            self.inflight[key] = ev

        def call():
            return self.client.generate(prompt)

        response = self.executor.submit(call)

        with self.lock:
            self.cache[key] = (response, now + self.ttl)
            ev.set()
            self.inflight.pop(key, None)

        return response


# ---------------- Public Factory ----------------
@lru_cache(maxsize=8)
def get_model(
    model: str = "llama-3.3-70b-versatile",  # ✅ default model
    ttl: int = 300,
    rpm: int = 30
):
    api_key = os.getenv("GROQ_API_KEY")
    return CachedModel(
        GroqClient(api_key, model=model),
        ttl=ttl,
        rpm=rpm
    )
