#!/bin/sh
set -eu

SECRETS_DIR="/secrets"
mkdir -p "$SECRETS_DIR" 
apk add --no-cache openssl >/dev/null 2>&1

# Create secret if not exists. printf without \n — critical.
create() {
  name="$1"; value="$2"
  if [ -f "$SECRETS_DIR/$name" ]; then
    echo "OK  $name already exists. Skipping"
  else
    printf '%s' "$value" > "$SECRETS_DIR/$name"
    chmod 644 "$SECRETS_DIR/$name"
    echo "++  created $name"
  fi
}

# External secret from template - warn
external() {
  name="$1"
  if [ ! -f "$SECRETS_DIR/$name" ]; then
    if [ -f "$SECRETS_DIR/$name.example" ]; then
      cp "$SECRETS_DIR/$name.example" "$SECRETS_DIR/$name"
    else
      printf 'CHANGE_ME' > "$SECRETS_DIR/$name"
    fi
    chmod 644 "$SECRETS_DIR/$name"
    echo "!!  $name created template — set your real value"
  else
    echo "OK  $name already exists. Skipping"
  fi
}

# --- Secrets generation ---
# create "secret_name.txt"             "$(openssl rand -base64 24)"

# --- External secrets. Manually. ---
external "max_api_token.txt"
external "yandex_llm_api_key.txt"

echo ""
echo "Finished. Write secrets info before start project!"