#!/usr/bin/env bash
# Install Ollama if needed, start it with the Kuber runtime flags,
# and warm qwen3:8b. Safe to re-run.
set -euo pipefail

MODEL="${OLLAMA_MODEL:-qwen3:8b}"
OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11434}"
HEALTH_URL="http://${OLLAMA_HOST}/api/tags"

log() { printf '==> %s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

ollama_up() {
  curl -sf "$HEALTH_URL" >/dev/null 2>&1
}

install_ollama() {
  if command -v ollama >/dev/null 2>&1; then
    log "Ollama already installed: $(command -v ollama)"
    return
  fi

  log "Ollama not found — installing"

  case "$(uname -s)" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        brew install ollama
      else
        log "Homebrew not found; downloading the official Mac app"
        local zip
        zip="$(mktemp -t ollama).zip"
        curl -fL "https://ollama.com/download/Ollama-darwin.zip" -o "$zip"
        local dest="${HOME}/Applications"
        mkdir -p "$dest"
        ditto -xk "$zip" "$dest"
        rm -f "$zip"
        if [[ -x /usr/local/bin/ollama ]]; then
          :
        elif [[ -x /opt/homebrew/bin/ollama ]]; then
          :
        elif [[ -x "${dest}/Ollama.app/Contents/Resources/ollama" ]]; then
          mkdir -p "${HOME}/.local/bin"
          ln -sf "${dest}/Ollama.app/Contents/Resources/ollama" "${HOME}/.local/bin/ollama"
          export PATH="${HOME}/.local/bin:${PATH}"
        fi
      fi
      ;;
    Linux)
      curl -fsSL https://ollama.com/install.sh | sh
      ;;
    *)
      die "Unsupported OS. Install Ollama from https://ollama.com/download and re-run this script."
      ;;
  esac

  command -v ollama >/dev/null 2>&1 || die "Ollama installed but 'ollama' is not on PATH. Open a new terminal and re-run."
}

start_serve() {
  if ollama_up; then
    log "Ollama is already running on ${OLLAMA_HOST}"
    log "Context/flash-attention flags only apply if this script starts the server. Stop the existing process first if you need them."
    return
  fi

  log "Starting ollama serve (ctx=32768, flash attention, kv=q8_0)"
  export OLLAMA_CONTEXT_LENGTH=32768
  export OLLAMA_FLASH_ATTENTION=1
  export OLLAMA_KV_CACHE_TYPE=q8_0

  nohup ollama serve >/tmp/kuber-ollama.log 2>&1 &
  disown || true

  local i
  for i in $(seq 1 60); do
    if ollama_up; then
      log "Ollama is up"
      return
    fi
    sleep 0.5
  done
  die "Ollama did not become ready. Check /tmp/kuber-ollama.log"
}

ensure_model() {
  log "Checking model ${MODEL}"
  ollama list
  if ollama list | awk 'NR>1 {print $1}' | grep -Fxq "${MODEL}"; then
    log "${MODEL} already downloaded — skipping pull"
  else
    log "Pulling ${MODEL} (one-time, several GB)"
    ollama pull "${MODEL}"
  fi
}

warmup() {
  log "Warming ${MODEL}"
  ollama run "${MODEL}" "Respond with the single word: ready."
  log "Done. Leave this machine as-is and open Kuber."
}

install_ollama
start_serve
ensure_model
warmup
