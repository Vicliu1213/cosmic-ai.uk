_oh_my_opencode_completion() {
  local cur
  cur="${COMP_WORDS[COMP_CWORD]}"
  COMPREPLY=($(compgen -W "-h --help -d --debug -c --cwd -p --prompt -f --output-format -q --quiet" -- "${cur}"))
}

complete -F _oh_my_opencode_completion opencode oc oco
