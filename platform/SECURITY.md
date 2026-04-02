# Seguranca da plataforma

Este documento descreve **medidas implementadas** e **expectativas de deploy**. Nao substitui auditoria independente nem analise de ameacas formal.

## O que a aplicacao faz

| Area | Medida |
|------|--------|
| Palavras-passe | **Argon2id** (novos e migracoes); **bcrypt** continua aceite para hashes antigos; rehash automatico no login. |
| JWT | HS256; claims `exp`, `iat`, `sub` obrigatorias; tolerancia de relogio curta; `tv` para revogacao de sessoes. |
| Conteudo das aulas | **Fernet** (AES-128 CBC + HMAC) em repouso; chave validada ao arranque se definida. |
| Transporte | HTTPS deve ser terminado no **reverse proxy** ou no servidor; `REQUIRE_HTTPS` forca redirecionamento e HSTS. |
| Cookies | HttpOnly; `Secure` quando `REQUIRE_HTTPS` ou `COOKIE_SAMESITE=none`. |
| API | Cabecalhos `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`; CORS configuravel. |
| UI estatica (`/ui`) | CSP restritiva (sem scripts externos por defeito). |
| Assistente | Quota diaria por utilizador; rate limit opcional por IP; limite de tamanho do corpo JSON; logs sem texto da pergunta. |
| Corpo HTTP | Limites por `Content-Length` em POST (`/auth`, `/admin`, `/student`, assistente) — mitigar payloads enormes. |
| Erros 500 | JSON com `request_id`; `EXPOSE_INTERNAL_ERRORS=false` (producao) evita mensagens de excecao ao cliente. |
| Admin | Lista de alunos paginada (`limit`/`offset`) para escalabilidade. |
| Pedidos | `GET /.well-known/security.txt` (RFC 9116) — editar contacto antes de producao publica. |

## O que **nao** e

- **Nao** e “criptografia ponta-a-ponta” no sentido de mensagens legiveis apenas no cliente: o servidor desencripta conteudo para alunos autenticados. O modelo assume confianca no backend e TLS no trafego.
- **Nao** substitui backups, gestao de segredos (Vault, etc.), nem WAF — sao camadas adicionais em producao.

## Checklist de producao

1. `JWT_SECRET` forte (>= 32 caracteres; ja validado).
2. `CONTENT_ENCRYPTION_KEY` Fernet unica e guardada em cofre; sem chave nao ha recuperacao do texto das aulas.
3. TLS com certificados validos; `REQUIRE_HTTPS=true` e `TRUSTED_HOSTS` alinhados com o dominio publico.
4. `CORS_ORIGINS` restrito aos fronts conhecidos (evitar `*` com cookies).
5. Atras de reverse proxy: configurar `TRUSTED_FORWARDED_FOR=true` **apenas** se o proxy **substituir** `X-Forwarded-For` de forma confiavel (evitar spoofing).
6. Editar contacto em `/.well-known/security.txt` (ver `app/main.py`) ou servir ficheiro estatico equivalente.
7. `EXPOSE_INTERNAL_ERRORS=false` em producao.
8. Monitorizar logs JSON (`app.request`, `app.error`, `app.assistant`) e `GET /health` / `/health/ready`.

## Reportar vulnerabilidades

Substituir o contacto em `security.txt` pelo teu processo (email ou pagina de divulgacao responsavel).
