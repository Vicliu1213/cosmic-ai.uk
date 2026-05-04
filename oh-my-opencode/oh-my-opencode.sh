#!/usr/bin/env bash

if [ -n "${ZSH_VERSION:-}" ]; then
  emulate -L zsh
fi

_oh_my_opencode_dir() {
  if [ -n "${OH_MY_OPENCODE_DIR:-}" ]; then
    printf '%s\n' "${OH_MY_OPENCODE_DIR}"
    return
  fi
  printf '%s\n' "${PWD}"
}

_oh_my_opencode_bin() {
  printf '%s\n' "${OPENCODE_BIN:-opencode}"
}

oc() {
  "${OPENCODE_BIN:-opencode}" "$@"
}

oco() {
  local project_dir
  project_dir="${OPENCODE_PROJECT_DIR:-$PWD}"
  "${OPENCODE_BIN:-opencode}" -c "${project_dir}" "$@"
}

opencode() {
  command "${OPENCODE_BIN:-opencode}" "$@"
}

_oh_my_opencode_prompt() {
  printf 'OpenCode[%s] ' "${PWD##*/}"
}

if [ -n "${ZSH_VERSION:-}" ]; then
  setopt prompt_subst
  PROMPT='$(_oh_my_opencode_prompt)${PROMPT}'
fi

_oh_my_opencode_load_completion() {
  local completion_file
  completion_file="$(_oh_my_opencode_dir)/completions/opencode.${SHELL##*/}"
  [ -f "${completion_file}" ] && . "${completion_file}"
}

_oh_my_opencode_load_completion
