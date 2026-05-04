#!/usr/bin/env sh

set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
ACME_SH="$ROOT_DIR/../acme.sh/acme.sh"
OUT_DIR="$ROOT_DIR/output/acme-issue"
LOG_DIR="$OUT_DIR/logs"

DOMAIN="${DOMAIN:-}"
EMAIL="${EMAIL:-}"
MODE="${MODE:-dns}"
DNS_PROVIDER="${DNS_PROVIDER:-}"
DNS_HOOK="${DNS_HOOK:-}"
WEBROOT="${WEBROOT:-/var/www/html}"
PRODUCTION="${PRODUCTION:-0}"
RUN_NOW="${RUN_NOW:-0}"
RELOADCMD="${RELOADCMD:-systemctl reload nginx}"
CERT_FILE="${CERT_FILE:-$OUT_DIR/cert.pem}"
KEY_FILE="${KEY_FILE:-$OUT_DIR/key.pem}"
FULLCHAIN_FILE="${FULLCHAIN_FILE:-$OUT_DIR/fullchain.pem}"
CA_STAGING="https://acme-staging-v02.api.letsencrypt.org/directory"
CA_PROD="https://acme-v02.api.letsencrypt.org/directory"

usage() {
  cat <<EOF
Usage: DOMAIN=example.com EMAIL=admin@example.com $0

Optional env:
  MODE=dns|webroot|standalone|alpn|stateless
  DNS_PROVIDER=cloudflare|route53|aliyun|godaddy|...
  DNS_HOOK=dns_<provider>
  PRODUCTION=1
  RUN_NOW=1
  WEBROOT=/var/www/html
  RELOADCMD='systemctl reload nginx'
EOF
}

provider_requirements() {
  case "$DNS_PROVIDER" in
    cloudflare)
      cat <<EOF
Required env for cloudflare:
  CF_Token
  CF_Account_ID
  CF_Zone_ID
EOF
      ;;
    route53)
      cat <<EOF
Required env for route53:
  AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY
  AWS_REGION
EOF
      ;;
    aliyun)
      cat <<EOF
Required env for aliyun:
  Ali_Key
  Ali_Secret
EOF
      ;;
    godaddy)
      cat <<EOF
Required env for godaddy:
  GD_Key
  GD_Secret
EOF
      ;;
    "")
      printf '%s\n' "DNS_PROVIDER not set; using DNS_HOOK only if provided"
      ;;
    *)
      printf '%s\n' "Provider template not defined for: $DNS_PROVIDER"
      ;;
  esac
}

provider_hook() {
  case "$DNS_PROVIDER" in
    cloudflare) printf '%s\n' "dns_cf" ;;
    route53) printf '%s\n' "dns_aws" ;;
    aliyun) printf '%s\n' "dns_ali" ;;
    godaddy) printf '%s\n' "dns_gd" ;;
    "") printf '%s\n' "" ;;
    *) printf '%s\n' "" ;;
  esac
}

build_issue_cmd() {
  server="$1"
  base="$ACME_SH --issue --server $server -d $DOMAIN"
  case "$MODE" in
    dns)
      hook="${DNS_HOOK:-$(provider_hook)}"
      if [ -n "$hook" ]; then
        printf '%s --dns %s' "$base" "$hook"
      else
        printf '%s --dns %s' "$base" "<dns-hook>"
      fi
      ;;
    webroot)
      printf '%s -w %s' "$base" "$WEBROOT"
      ;;
    standalone)
      printf '%s --standalone --httpport 80' "$base"
      ;;
    alpn)
      printf '%s --alpn --tlsport 443' "$base"
      ;;
    stateless)
      printf '%s --stateless' "$base"
      ;;
    *)
      printf '%s\n' "Unsupported MODE: $MODE" >&2
      exit 2
      ;;
  esac
}

run_cmd() {
  if [ "$RUN_NOW" = "1" ]; then
    sh -c "$1"
  else
    printf '%s\n' "$1"
  fi
}

require_value() {
  name="$1"
  value="$2"
  if [ -z "$value" ]; then
    printf '%s\n' "Missing required value: $name" >&2
    usage >&2
    exit 2
  fi
}

require_value DOMAIN "$DOMAIN"
require_value EMAIL "$EMAIL"

mkdir -p "$OUT_DIR" "$LOG_DIR"

cat > "$OUT_DIR/manifest.env" <<EOF
DOMAIN=$DOMAIN
EMAIL=$EMAIL
MODE=$MODE
DNS_PROVIDER=$DNS_PROVIDER
DNS_HOOK=$DNS_HOOK
WEBROOT=$WEBROOT
PRODUCTION=$PRODUCTION
RUN_NOW=$RUN_NOW
RELOADCMD=$RELOADCMD
CERT_FILE=$CERT_FILE
KEY_FILE=$KEY_FILE
FULLCHAIN_FILE=$FULLCHAIN_FILE
EOF

cat > "$OUT_DIR/provider-template.txt" <<EOF
$([ -n "$DNS_PROVIDER" ] && provider_requirements || printf '%s\n' "Set DNS_PROVIDER to see provider requirements")

Suggested DNS hook: ${DNS_HOOK:-$(provider_hook)}
EOF

printf '%s\n' "=== acme.sh validation pack ===" > "$OUT_DIR/checklist.md"
printf '%s\n' "Domain: $DOMAIN" >> "$OUT_DIR/checklist.md"
printf '%s\n' "Email: $EMAIL" >> "$OUT_DIR/checklist.md"
printf '%s\n' "Mode: $MODE" >> "$OUT_DIR/checklist.md"
printf '%s\n' "DNS provider: ${DNS_PROVIDER:-<unset>}" >> "$OUT_DIR/checklist.md"
printf '%s\n' "Suggested DNS hook: ${DNS_HOOK:-$(provider_hook)}" >> "$OUT_DIR/checklist.md"
printf '%s\n' "" >> "$OUT_DIR/checklist.md"
printf '%s\n' "Staging issue:" >> "$OUT_DIR/checklist.md"
printf '%s\n' "$ACME_SH --register-account -m $EMAIL --server $CA_STAGING" >> "$OUT_DIR/checklist.md"
printf '%s\n' "$(build_issue_cmd "$CA_STAGING") --log $LOG_DIR/staging.log --debug 2" >> "$OUT_DIR/checklist.md"
if [ "$PRODUCTION" = "1" ]; then
  printf '%s\n' "Production issue:" >> "$OUT_DIR/checklist.md"
  printf '%s\n' "$ACME_SH --register-account -m $EMAIL --server $CA_PROD" >> "$OUT_DIR/checklist.md"
  printf '%s\n' "$(build_issue_cmd "$CA_PROD") --log $LOG_DIR/prod.log --debug 2" >> "$OUT_DIR/checklist.md"
fi
printf '%s\n' "" >> "$OUT_DIR/checklist.md"
printf '%s\n' "Install cert:" >> "$OUT_DIR/checklist.md"
printf '%s\n' "$ACME_SH --install-cert -d $DOMAIN --cert-file $CERT_FILE --key-file $KEY_FILE --fullchain-file $FULLCHAIN_FILE --reloadcmd '$RELOADCMD'" >> "$OUT_DIR/checklist.md"
printf '%s\n' "" >> "$OUT_DIR/checklist.md"
printf '%s\n' "Verify:" >> "$OUT_DIR/checklist.md"
printf '%s\n' "$ACME_SH --info -d $DOMAIN" >> "$OUT_DIR/checklist.md"
printf '%s\n' "openssl x509 -in $FULLCHAIN_FILE -noout -text" >> "$OUT_DIR/checklist.md"
printf '%s\n' "openssl x509 -in $FULLCHAIN_FILE -noout -dates" >> "$OUT_DIR/checklist.md"

printf '%s\n' "Provider requirements:" 
provider_requirements

account_cmd="$ACME_SH --register-account -m $EMAIL --server $CA_STAGING"
printf '%s\n' "Account command: $account_cmd"
run_cmd "$account_cmd"

staging_cmd="$(build_issue_cmd "$CA_STAGING") --log $LOG_DIR/staging.log --debug 2"
printf '%s\n' "Staging command: $staging_cmd"
run_cmd "$staging_cmd"

if [ "$PRODUCTION" = "1" ]; then
  prod_account_cmd="$ACME_SH --register-account -m $EMAIL --server $CA_PROD"
  printf '%s\n' "Production account command: $prod_account_cmd"
  run_cmd "$prod_account_cmd"

  prod_cmd="$(build_issue_cmd "$CA_PROD") --log $LOG_DIR/prod.log --debug 2"
  printf '%s\n' "Production command: $prod_cmd"
  run_cmd "$prod_cmd"
fi

install_cmd="$ACME_SH --install-cert -d $DOMAIN --cert-file $CERT_FILE --key-file $KEY_FILE --fullchain-file $FULLCHAIN_FILE --reloadcmd '$RELOADCMD'"
printf '%s\n' "Install command: $install_cmd"
run_cmd "$install_cmd"

printf '%s\n' "Verification pack written to: $OUT_DIR"
