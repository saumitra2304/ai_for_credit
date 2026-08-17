"""
Streaming client for a local vLLM server running Qwen/Qwen3.5-4B.

Usage:
    python gemma_stream.py
    python gemma_stream.py "your prompt here"
"""

import sys
import time

t_import_start = time.perf_counter()
from openai import OpenAI, APIConnectionError, BadRequestError
t_import_end = time.perf_counter()

BASE_URL = "http://localhost:8000/v1"
MODEL = "neuralmagic/gemma-2-2b-it-FP8"

# Qwen supports the system role natively in its chat template.
SYSTEM_PROMPT = "You are a helpful, concise assistant."


def build_messages(user_prompt: str) -> list[dict]:
    return [
        {"role": "user", "content": f"{SYSTEM_PROMPT}\n\n{user_prompt}"}
    ]


def stream_chat(client: OpenAI, user_prompt: str) -> str:
    """Stream a completion, printing tokens as they arrive. Returns full text."""
    stream = client.chat.completions.create(
        model=MODEL,
        messages=build_messages(user_prompt),
        temperature=0.7,
        max_tokens=512,
        stream=True,
        stream_options={"include_usage": True},
    )

    pieces = []
    t_request = time.perf_counter()
    t_first_token = None
    usage = None

    for chunk in stream:
        # The final chunk carries usage and has an empty choices list.
        if getattr(chunk, "usage", None):
            usage = chunk.usage
            continue
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta.content
        if not delta:
            # First chunk carries the role with content=None; skip it.
            continue

        if t_first_token is None:
            t_first_token = time.perf_counter()

        pieces.append(delta)
        print(delta, end="", flush=True)

    t_end = time.perf_counter()
    print()

    report(t_request, t_first_token, t_end, usage)
    return "".join(pieces)


def report(t_request, t_first_token, t_end, usage) -> None:
    print("-" * 50)
    print(f"import openai      : {t_import_end - t_import_start:6.2f}s")

    if t_first_token is None:
        print("no tokens received")
        return

    ttft = t_first_token - t_request
    gen = t_end - t_first_token
    print(f"time to first token: {ttft:6.2f}s")
    print(f"generation         : {gen:6.2f}s")

    if usage:
        print(f"prompt tokens      : {usage.prompt_tokens}")
        print(f"output tokens      : {usage.completion_tokens}")
        if gen > 0:
            print(f"throughput         : {usage.completion_tokens / gen:6.1f} tok/s")


def main() -> int:
    prompt = " ".join(sys.argv[1:]) or "What is the capital of France? and tell me the history of france in depth and also of europe and world war 2"

    client = OpenAI(base_url=BASE_URL, api_key="EMPTY")

    try:
        stream_chat(client, prompt)
    except APIConnectionError:
        print(
            "Could not reach the server at "
            f"{BASE_URL}.\nIs the container up, and has it printed "
            "'Uvicorn running on http://0.0.0.0:8000' yet?",
            file=sys.stderr,
        )
        return 1
    except BadRequestError as e:
        print(f"Server rejected the request: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())