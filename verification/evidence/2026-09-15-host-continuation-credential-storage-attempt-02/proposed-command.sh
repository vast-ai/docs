# Run in Bash on Linux or macOS. Enter the key at the prompt.
(
  set +x
  umask 077
  case "${XDG_CONFIG_HOME:-}" in
    /*) task_vast_key_dir="$XDG_CONFIG_HOME/vastai" ;;
    *) task_vast_key_dir="$HOME/.config/vastai" ;;
  esac
  task_vast_key_file="$task_vast_key_dir/vast_api_key"
  if [ -L "$task_vast_key_file" ] || { [ -e "$task_vast_key_file" ] && [ ! -f "$task_vast_key_file" ]; }; then
    printf 'Expected a regular key file; inspect the configured path before continuing.\n' >&2
    exit 1
  fi
  read -r -s -p 'Host API key: ' task_vast_key || exit 1
  printf '\n'
  [ -n "$task_vast_key" ] || exit 1
  mkdir -p "$task_vast_key_dir" && chmod 700 "$task_vast_key_dir" || exit 1
  touch "$task_vast_key_file" && chmod 600 "$task_vast_key_file" || exit 1
  vastai set api-key "$task_vast_key"
)
