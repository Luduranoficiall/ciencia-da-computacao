# Plataforma do curso (API)

Backend **FastAPI** com:

- **Base de dados SQLite** (ficheiro local) ou outra URL SQLAlchemy — progresso por aluno, certificados, modulos.
- **Apenas administrador** vê lista completa de alunos, progresso e pode descarregar qualquer certificado (`GET /admin/...`).
- **Alunos** só vêem o próprio progresso e certificado; conteúdo das aulas é guardado **encriptado em repouso** (Fernet); na API chega já desencriptado **após login** (não substitui HTTPS em produção).
- **Certificado PDF** ao concluir **todos** os módulos cujo `slug` coincide com os `id` de `data/curriculum.json`, com **módulo correspondente na BD**. Emissão **idempotente** (um certificado por aluno; repetir não duplica).
- **Anti-duplicidade**: email único; par `(user_id, module_slug)` único em progresso; um certificado por `user_id` e `serial` único.
- **Multi-dispositivo**: API stateless com JWT; qualquer cliente (web responsiva, app nativa, PWA futura) usa os mesmos endpoints. **CORS** configurável.
- **UI do aluno (web/PWA)**: servida em `GET /ui/` (login, lista de módulos, progresso e download do certificado).
- **Personal Prof**: `POST /student/assistant/ask` com quota diária por aluno (`ASSISTANT_DAILY_LIMIT_PER_USER`) e opcional limite por IP (`ASSISTANT_RATE_LIMIT_PER_MINUTE_PER_IP`, janela 60s). Com `ASSISTANT_OPENAI_API_KEY` (API OpenAI-compatible) usa LLM; sem chave, resposta local a partir do módulo.
- **Verificacao publica do certificado** (sem dados pessoais): `GET /public/certificates/verify/{serial}` (serial com `A-Za-z0-9_-`); pagina em `/ui/verify.html`.
- **Landing do curso** (sem login): textos em `data/course_presentation.json` (validado no CI com JSON Schema); `GET /public/course-presentation`; a UI em `/ui/` carrega e mostra o conteúdo antes do login.
- **Robustez**: SQLite com **WAL** + `pool_pre_ping`; `GET /health` e `GET /health/ready` (este verifica a BD) incluem `assistant.llm_configured` sem expor segredos; cabecalho **`X-Request-ID`**; **rate limit** opcional em `POST /auth/token`; **`TrustedHostMiddleware`** opcional.
- **JWT** com `iat`/`exp` em timestamp (interoperavel).
- **Password policy + lockout**: maiuscula/minuscula/numero/simbolo configuraveis; bloqueio temporario por conta apos falhas repetidas de login.
- **Sessao web**: apos login, cookies **HttpOnly** `access_token` e `refresh_token` (este ultimo so para `POST /auth/refresh` e `POST /auth/logout`). A UI usa `credentials: include` e **nao** guarda tokens em `localStorage`. A API continua a aceitar `Authorization: Bearer` (Swagger / scripts).
- **Controlo admin**: `GET /admin/students` lista paginada (`limit`/`offset`) e inclui `active_sessions` (refresh tokens ainda validos). `POST /admin/students/{id}/revoke-sessions` revoga **todos** os refresh tokens e **invalida imediatamente** os JWTs de access desse utilizador (claim `tv` / `access_token_version` na BD). Migracao SQLite automatica em arranque se faltar a coluna `users.access_token_version`.
- **Auditoria**: acoes administrativas sao um conjunto **fechado** (`AuditAction` em `app/audit_service.py`); `record_audit_log` so aceita esses valores; `GET /admin/audit-log?action=...` usa o mesmo enum e devolve **422** se o valor nao for valido (OpenAPI lista os valores).

## Arranque local

Na pasta `platform/`:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
cp .env.example .env
# Editar .env: CONTENT_ENCRYPTION_KEY, JWT_SECRET
mkdir -p data
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Abrir `http://127.0.0.1:8000/docs` (Swagger).

1. Criar admin: definir `BOOTSTRAP_ADMIN_EMAIL` e `BOOTSTRAP_ADMIN_PASSWORD` no `.env` **ou** inserir utilizador com `role=admin` na BD.
2. Login OAuth2: `POST /auth/token` com `username` = email, `password` = palavra-passe.
3. Sincronizar modulos vazios a partir do grafo: `POST /admin/modules/sync-from-curriculum` (conteúdo placeholder encriptado).
4. Atualizar conteúdo: `POST /admin/modules` com `slug`, `title`, `body_markdown` (substitui se o `slug` já existir).
5. Criar alunos: `POST /admin/students` com email, password, `full_name` (nome no certificado).
6. Aluno: lista modulos, lê conteúdo, marca `POST /student/progress/{slug}`, quando elegível `POST /student/certificate/issue` e `GET /student/certificate/pdf`.
7. UI do aluno: acede a `http://127.0.0.1:8000/ui/` e usa as mesmas credenciais; em cada módulo pode **Perguntar ao assistente** (Personal Prof), que chama `POST /student/assistant/ask`.
8. Validar certificado (publico): `http://127.0.0.1:8000/ui/verify.html`

## Docker (producao/dev)

No diretorio raiz do repositorio:

```bash
docker compose up -d --build
```

API em `http://127.0.0.1:8000` com dados persistidos em `./data`.

## Produção (mínimo)

- **SECURITY.md** — checklist de seguranca (Argon2id, Fernet, TLS, proxy, `/.well-known/security.txt`) e limites do modelo de confianca.
- **HTTPS obrigatório** (TLS termina no reverse proxy ou no servidor); cifrado no disco protege cópias da BD, não o tráfego.
- `JWT_SECRET` forte; `CORS_ORIGINS` restrito; firewall só para ti no painel admin se expuseres a mesma API.
- Hardening (opcional, via `.env`): `REQUIRE_HTTPS=true` ativa redirecionamento para HTTPS + HSTS e adiciona headers de segurança (CSP) na UI.
- `TRUSTED_HOSTS` (virgula) quando o servidor recebe o `Host` publico (detras de proxy, alinhar com o dominio).
- `RATE_LIMIT_AUTH_PER_MINUTE` para mitigar brute-force no login (0 desliga).
- Backup regular do ficheiro SQLite (ou dump Postgres se mudares `DATABASE_URL`).
- O conteúdo encriptado usa `CONTENT_ENCRYPTION_KEY`: sem esta chave **não há** recuperação do texto das aulas.

## Testes

O ficheiro `pytest.ini` define `pythonpath` para importar o pacote `app` sem variaveis de ambiente extra.

```bash
.venv/bin/python -m compileall -q app
.venv/bin/pytest tests/ -v
```

O CI (`platform-api`) corre `compileall` e `pytest` em `platform/`.

## Documentação OpenAPI

Com o servidor a correr: `/docs` e `/openapi.json`.
