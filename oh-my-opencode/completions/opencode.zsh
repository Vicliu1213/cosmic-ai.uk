#compdef opencode oc oco

_oh_my_opencode_completion() {
  local -a opts
  opts=(
    '-h[help]'
    '--help[help]'
    '-d[debug]'
    '--debug[debug]'
    '-c[working directory]:directory:_files -/'
    '--cwd[working directory]:directory:_files -/'
    '-p[prompt mode]'
    '--prompt[prompt mode]'
    '-f[output format]:format:(text json)'
    '--output-format[output format]:format:(text json)'
    '-q[quiet]'
    '--quiet[quiet]'
  )
  _describe 'command line option' opts
}

compdef _oh_my_opencode_completion opencode oc oco 2>/dev/null || true
