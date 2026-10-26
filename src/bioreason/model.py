"""Optional OpenAI-compatible reasoning adapter with explicit human-controlled activation.

No API key is required for deterministic operation. This module does not run
background agents, and it never sends data to a model unless explicitly called.
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never forward a model request or its Authorization header to a redirect."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


class ModelError(RuntimeError):
    pass


def ask_model(role, evidence, *, endpoint=None, model=None, api_key=None, timeout=30):
    """Call a configured chat-completions endpoint; return a candidate, not a fact.

    Credentials and endpoints are never included in the returned object.
    Only HTTPS endpoints or loopback HTTP are permitted.
    """
    endpoint = endpoint or os.environ.get("BIOREASON_MODEL_ENDPOINT", "")
    model = model or os.environ.get("BIOREASON_MODEL_NAME", "")
    api_key = api_key if api_key is not None else os.environ.get("BIOREASON_MODEL_API_KEY", "")
    if not endpoint or not model:
        raise ModelError("Model endpoint and model name must be explicitly configured")
    parsed = urllib.parse.urlsplit(endpoint)
    loopback = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not (parsed.scheme == "http" and loopback):
        raise ModelError("Model endpoint must use HTTPS or loopback HTTP")
    if parsed.username or parsed.password or parsed.fragment:
        raise ModelError("Model endpoint must not contain credentials or fragments")
    if not isinstance(evidence, dict):
        raise ModelError("Evidence must be a JSON object")
    if len(json.dumps(evidence)) > 50000:
        raise ModelError("Evidence exceeds the 50 KB input budget")

    instructions = (
        "You are the BioReason " + role + " role. "
        "Use only the supplied bibliographic evidence. "
        "Never invent citations, findings, novelty, causality, or validation. "
        "State uncertainty. Return a short proposed analysis, not a verified claim."
    )
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": json.dumps(evidence, ensure_ascii=False)},
        ],
        "temperature": 0,
    }).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    request = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
    try:
        opener = urllib.request.build_opener(_NoRedirect)
        with opener.open(request, timeout=timeout) as response:
            result = json.load(response)
        output = result["choices"][0]["message"]["content"]
        if not isinstance(output, str) or not output.strip():
            raise ModelError("Model returned empty content")
    except (urllib.error.URLError, KeyError, IndexError, ValueError, TypeError) as exc:
        raise ModelError("Model request failed or returned invalid data") from exc
    return {
        "role": role,
        "candidate": output,
        "status": "unverified model-generated suggestion",
        "model": model,
    }
