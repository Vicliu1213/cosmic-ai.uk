# acme.sh Issue Pack

## 1. Prepare

Pick one mode:
- `dns`
- `webroot`
- `standalone`
- `alpn`
- `stateless`

Pick one DNS provider if using DNS mode:
- `cloudflare` -> `dns_cf`
- `route53` -> `dns_aws`
- `aliyun` -> `dns_ali`
- `godaddy` -> `dns_gd`

## 2. Dry run

```sh
DOMAIN=example.com EMAIL=admin@example.com MODE=dns DNS_PROVIDER=cloudflare sh .hermes/scripts/acme_issue_pack.sh
```

## 3. Real issue

```sh
DOMAIN=example.com EMAIL=admin@example.com MODE=dns DNS_PROVIDER=cloudflare RUN_NOW=1 PRODUCTION=0 sh .hermes/scripts/acme_issue_pack.sh
```

## 4. Required env by provider

### Cloudflare
- `CF_Token`
- `CF_Account_ID`
- `CF_Zone_ID`

### Route53
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`

### Aliyun
- `Ali_Key`
- `Ali_Secret`

### GoDaddy
- `GD_Key`
- `GD_Secret`

## 5. Outputs

- `.hermes/output/acme-issue/manifest.env`
- `.hermes/output/acme-issue/provider-template.txt`
- `.hermes/output/acme-issue/checklist.md`
