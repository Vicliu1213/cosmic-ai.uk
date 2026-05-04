#!/usr/bin/env sh

set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
ACME_SH="$ROOT_DIR/../acme.sh/acme.sh"
OUT_DIR="$ROOT_DIR/output/acme-validation"
LOG_DIR="$OUT_DIR/logs"

DOMAIN="${DOMAIN:-example.com}"
EMAIL="${EMAIL:-admin@example.com}"
WEBROOT="${WEBROOT:-/var/www/html}"
DNS_HOOK="${DNS_HOOK:-}"
SERVER_STAGING="https://acme-staging-v02.api.letsencrypt.org/directory"
SERVER_PROD="https://acme-v02.api.letsencrypt.org/directory"

mkdir -p "$OUT_DIR" "$LOG_DIR"

cat > "$OUT_DIR/manifest.env" <<EOF
DOMAIN=$DOMAIN
EMAIL=$EMAIL
WEBROOT=$WEBROOT
DNS_HOOK=$DNS_HOOK
SERVER_STAGING=$SERVER_STAGING
SERVER_PROD=$SERVER_PROD
EOF

cat > "$OUT_DIR/checklist.md" <<EOF
# acme.sh validation pack

## Inputs
- DOMAIN: $DOMAIN
- EMAIL: $EMAIL
- WEBROOT: $WEBROOT
- DNS_HOOK: ${DNS_HOOK:-<unset>}

## Validate
- staging dns: \`$ACME_SH --issue --staging -d $DOMAIN --dns ${DNS_HOOK:-<dns-hook>} --log $LOG_DIR/staging-dns.log --debug 2\`
- staging webroot: \`$ACME_SH --issue --staging -d $DOMAIN -w $WEBROOT --log $LOG_DIR/staging-webroot.log --debug 2\`
- staging standalone: \`$ACME_SH --issue --staging -d $DOMAIN --standalone --httpport 80 --log $LOG_DIR/staging-standalone.log --debug 2\`
- staging alpn: \`$ACME_SH --issue --staging -d $DOMAIN --alpn --tlsport 443 --log $LOG_DIR/staging-alpn.log --debug 2\`
- staging stateless: \`$ACME_SH --issue --staging -d $DOMAIN --stateless --log $LOG_DIR/staging-stateless.log --debug 2\`
- prod dns: \`$ACME_SH --issue --server $SERVER_PROD -d $DOMAIN --dns ${DNS_HOOK:-<dns-hook>} --log $LOG_DIR/prod-dns.log --debug 2\`
- install cert: \`$ACME_SH --install-cert -d $DOMAIN --cert-file $OUT_DIR/cert.pem --key-file $OUT_DIR/key.pem --fullchain-file $OUT_DIR/fullchain.pem --reloadcmd 'systemctl reload nginx'\`

## Verify
- \`$ACME_SH --info -d $DOMAIN\`
- \`$ACME_SH --list\`
- \`openssl x509 -in $OUT_DIR/fullchain.pem -noout -text\`
- \`openssl x509 -in $OUT_DIR/fullchain.pem -noout -dates\`
EOF

if [ -n "$DNS_HOOK" ]; then
  printf '%s\n' "DNS hook configured: $DNS_HOOK"
else
  printf '%s\n' "DNS hook not set; DNS commands remain template-only"
fi

printf '%s\n' "Validation pack written to: $OUT_DIR"
