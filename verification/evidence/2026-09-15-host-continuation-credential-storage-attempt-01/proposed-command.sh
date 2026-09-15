# Run in Bash on Linux or macOS. Enter the key at the prompt.
(
  set +x
  umask 077
  task_vast_key_dir="${XDG_CONFIG_HOME:-$HOME/.config}/vastai"
  mkdir -p "$task_vast_key_dir" && chmod 700 "$task_vast_key_dir" || exit 1
  task_vast_key_file="$task_vast_key_dir/vast_api_key"
  if [ -L "$task_vast_key_file" ] || { [ -e "$task_vast_key_file" ] && [ ! -f "$task_vast_key_file" ]; }; then
    printf 'Expected a regular key file; inspect the configured path before continuing.\n' >&2
    exit 1
  fi
  touch "$task_vast_key_file" && chmod 600 "$task_vast_key_file" || exit 1
  read -r -s -p 'Host API key: ' task_vast_key || exit 1
  printf '\n'
  [ -n "$task_vast_key" ] || exit 1
  vastai set api-key "$task_vast_key"
)
