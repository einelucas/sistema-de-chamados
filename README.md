# Central de Solicitações

Sistema interno de gerenciamento de solicitações (chamados), construído como projeto de referência
para novos sistemas internos da equipe. Permite registrar, acompanhar, atualizar e concluir
solicitações feitas por usuários internos, com controle de acesso por papel, comentários,
histórico de alterações, anexos e um dashboard com indicadores.

## Sumário

- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Requisitos](#requisitos)
- [Instalação e execução com Docker (recomendado)](#instalação-e-execução-com-docker-recomendado)
- [Instalação e execução local (sem Docker)](#instalação-e-execução-local-sem-docker)
- [Migrations e seed](#migrations-e-seed)
- [Execução dos testes](#execução-dos-testes)
- [Credenciais iniciais](#credenciais-iniciais)
- [Documentação da API](#documentação-da-api)
- [Autenticação](#autenticação)
- [Regras de negócio e permissões](#regras-de-negócio-e-permissões)
- [Segurança em produção](#segurança-em-produção)
- [Principais decisões arquiteturais](#principais-decisões-arquiteturais)
- [Problemas comuns](#problemas-comuns)
- [Próximos passos](#próximos-passos)

## Arquitetura

Aplicação dividida em dois projetos independentes que se comunicam por API HTTP:

- **Frontend**: Nuxt 3 (Vue 3 + TypeScript), consumindo a API via `$fetch`/`useAsyncData`.
- **Backend**: FastAPI (Python), com PostgreSQL como banco de dados, organizado em camadas
  (rotas → serviços → repositórios → modelos).

```
Usuário → Frontend (Nuxt, porta 3000) → API REST (FastAPI, porta 8000) → PostgreSQL (porta 5432)
```

## Tecnologias

**Frontend**: Nuxt 3, Vue 3, TypeScript, Composition API (`<script setup>`), Pinia (apenas para o
estado global de autenticação), Chart.js/vue-chartjs para os gráficos do dashboard.

**Backend**: FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PostgreSQL, Pytest, python-jose (JWT),
Passlib + bcrypt (hash de senha).

## Estrutura de pastas

```
central-solicitacoes/
├── frontend/
│   └── app/
│       ├── assets/css/        # Design tokens e estilos globais
│       ├── components/        # layout/ ui/ solicitacoes/ dashboard/
│       ├── composables/       # useAuth, useRequests, useComments, useAttachments...
│       ├── layouts/           # default.vue (autenticado), auth.vue (login)
│       ├── middleware/        # auth, admin, guest
│       ├── pages/             # roteamento do Nuxt
│       ├── plugins/           # cliente $api, restauração de sessão
│       ├── stores/            # auth (Pinia)
│       ├── types/             # tipos TypeScript espelhando os schemas do backend
│       └── utils/             # formatação, tratamento de erros
├── backend/
│   └── app/
│       ├── api/routes/        # endpoints
│       ├── api/dependencies/  # autenticação, sessão de banco
│       ├── core/              # config, segurança (JWT/hash), logging, exceções
│       ├── database/          # engine e sessão SQLAlchemy
│       ├── models/            # modelos SQLAlchemy
│       ├── schemas/           # schemas Pydantic (entrada/saída)
│       ├── repositories/      # acesso a dados
│       └── services/          # regras de negócio e permissões
│   ├── alembic/                # migrations
│   ├── tests/                  # testes Pytest
│   └── seed.py                 # script de seed
├── docker-compose.yml
├── .env.example
└── README.md
```

## Requisitos

- Docker e Docker Compose (para a instalação recomendada), **ou**
- Node.js 20+ e npm (para rodar o frontend localmente)
- Python 3.12+ e PostgreSQL 16+ (para rodar o backend localmente)

## Instalação e execução com Docker (recomendado)

```bash
# 1. Na raiz do projeto, copie o .env de exemplo
cp .env.example .env

# 2. Suba os três serviços (PostgreSQL, backend e frontend)
docker compose up --build
```

O backend aplica as migrations e roda o seed automaticamente ao subir (veja o `CMD` do
`backend/Dockerfile`). Após a subida:

- Frontend: http://localhost:3000
- Backend (docs interativas): http://localhost:8000/docs
- Backend (health check): http://localhost:8000/health

Para parar: `docker compose down`. Para apagar também os dados do banco: `docker compose down -v`.

> **Nota sobre `ENVIRONMENT`**: o `.env.example` define `ENVIRONMENT=development`, o que permite
> subir o Docker Compose imediatamente com as credenciais de exemplo. Para um deploy real, defina
> `ENVIRONMENT=production` **e** substitua `SECRET_KEY`, `ADMIN_PASSWORD` e `POSTGRES_PASSWORD` por
> valores fortes — veja [Segurança em produção](#segurança-em-produção). Com `ENVIRONMENT=production`
> e qualquer um desses valores ainda no padrão de exemplo, o backend recusa iniciar.

## Instalação e execução local (sem Docker)

### Banco de dados

Crie um banco PostgreSQL local, por exemplo:

```bash
createdb central_solicitacoes
```

### Backend

```bash
cd backend
cp .env.example .env
# edite .env se necessário (ex.: credenciais do PostgreSQL local)

pip install -e ".[dev]"

# aplica as migrations
alembic upgrade head

# cria o usuário administrador inicial
python seed.py

# inicia a API em modo desenvolvimento
uvicorn app.main:app --reload --port 8000
```

A API ficará disponível em `http://localhost:8000`, com documentação interativa em
`http://localhost:8000/docs`.

### Frontend

Em outro terminal:

```bash
cd frontend
cp .env.example .env
# garanta que NUXT_PUBLIC_API_BASE aponta para http://localhost:8000/api/v1

npm ci
npm run dev
```

O frontend ficará disponível em `http://localhost:3000`.

Antes de enviar alterações, valide o projeto do mesmo jeito que o CI faria:

```bash
npm run typecheck   # checagem de tipos TypeScript/Vue, sem erros
npm run build        # build de producao, gera .output/
```

## Migrations e seed

- As migrations ficam em `backend/alembic/versions/`:
  - `0001_initial.py` cria todas as tabelas, enums, índices e chaves estrangeiras.
  - `0002_add_exclusao_history_action.py` adiciona o valor `EXCLUSAO` ao enum `history_action`,
    usado para registrar no histórico quando uma solicitação é excluída (logicamente).
- Ambas foram validadas em um PostgreSQL 16 limpo com o ciclo completo
  `alembic upgrade head` → `alembic downgrade base` → `alembic upgrade head`, executado
  múltiplas vezes sem erro.
- **Limitação conhecida**: o `downgrade()` da migration `0002` não é suportado (levanta
  `NotImplementedError` de propósito). O PostgreSQL não permite remover um valor de um tipo
  `ENUM` sem recriar o tipo inteiro; como esta é uma migration aditiva (não destrutiva), o
  downgrade documenta essa limitação em vez de arriscar perda de dados silenciosa. Um
  `alembic downgrade base` completo do zero (`0002` → nada) portanto não é suportado; use
  `alembic downgrade 0001_initial` apenas se tiver certeza de que nenhum registro usa `EXCLUSAO`.
- Para criar uma nova migration após alterar os modelos:
  ```bash
  cd backend
  alembic revision --autogenerate -m "descricao da mudanca"
  alembic upgrade head
  ```
- O script `backend/seed.py` cria **apenas** o usuário administrador inicial, usando as
  variáveis `ADMIN_EMAIL`, `ADMIN_NAME` e `ADMIN_PASSWORD` do `.env`. Ele é idempotente: se o
  administrador já existir, nenhuma ação é executada.

## Execução dos testes

Os testes do backend usam SQLite em memória por padrão, isolado do banco de produção/
desenvolvimento, e não exigem PostgreSQL rodando:

```bash
cd backend
pip install -e ".[dev]"
pytest -v
```

Cobrem, entre outros: login válido/inválido/token expirado/usuário inativo, rotas protegidas,
CRUD de solicitações, transições de status válidas e inválidas, exclusão lógica com registro em
histórico, permissões por papel (ADMIN/ANALYST/USER), propriedade de registro (um usuário não
acessa solicitação de outro), proteção do último administrador e autoexclusão, upload/download de
anexos (tipo inválido, tamanho excedido, acesso não autorizado, nome de arquivo malicioso),
escopo do dashboard por papel, e validação de configuração insegura em produção.

Adicionalmente, há testes de **integração com um PostgreSQL real**
(`tests/test_integration_postgres.py`) que validam o ciclo de migrations, os enums nativos e as
constraints de unicidade/chave estrangeira aplicadas pelo próprio banco — algo que o SQLite não
reproduz fielmente. Eles são pulados automaticamente se não houver Postgres acessível; para
rodá-los:

```bash
createdb central_solicitacoes_test
TEST_POSTGRES_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/central_solicitacoes_test" pytest -v
```

## Credenciais iniciais

Após rodar o seed (automático no Docker, manual via `python seed.py` localmente), use as
credenciais definidas no `.env`:

- **E-mail**: valor de `ADMIN_EMAIL` (padrão: `admin@example.com`)
- **Senha**: valor de `ADMIN_PASSWORD` (padrão: `troque-esta-senha` — **altere antes de usar em
  produção**)

Novos usuários (analistas e usuários comuns) são criados pelo administrador na área
`/admin/usuarios`.

## Documentação da API

A documentação interativa (Swagger UI) é gerada automaticamente pelo FastAPI e fica disponível em
`http://localhost:8000/docs` (ou `/redoc` para a versão Redoc). Todos os endpoints estão sob o
prefixo `/api/v1`, por exemplo:

```
POST   /api/v1/auth/login
GET    /api/v1/auth/me
GET    /api/v1/requests
POST   /api/v1/requests
PATCH  /api/v1/requests/{id}/status
GET    /api/v1/dashboard/summary
```

## Autenticação

A autenticação é feita por **JWT (JSON Web Token)**:

1. O usuário envia e-mail e senha para `POST /api/v1/auth/login`.
2. O backend valida a senha (hash bcrypt via Passlib) e, se válida, retorna um `access_token`
   assinado (HS256) contendo o ID do usuário e seu papel, com expiração configurável
   (`ACCESS_TOKEN_EXPIRE_MINUTES`).
3. O frontend guarda o token em `sessionStorage` (armazenamento por aba/sessão do navegador) e o
   envia em todas as chamadas subsequentes via header `Authorization: Bearer <token>`.
4. Cada rota protegida do backend valida o token através da dependência `get_current_user`; rotas
   administrativas usam dependências adicionais (`require_admin`, `require_analyst_or_admin`) que
   verificam o papel do usuário.
5. Quando o token expira ou é inválido, o backend responde `401`; o cliente HTTP do frontend
   (`plugins/api.ts`) intercepta essa resposta e desloga o usuário automaticamente, redirecionando
   para `/login`.
6. No frontend, o middleware `auth` protege páginas que exigem login e o middleware `admin`
   restringe páginas administrativas a usuários com papel `ADMIN`.

Os controles de acesso por papel (usuário comum só vê suas próprias solicitações; analistas podem
atualizar status/prioridade/responsável; apenas administradores gerenciam usuários) são aplicados
**no backend**, na camada de serviços — o frontend apenas reflete essas permissões na interface,
sem ser a única barreira de proteção.

## Regras de negócio e permissões

Resumo das regras aplicadas em `app/services/` (sempre no backend, nunca apenas no frontend):

**Transições de status.** Uma solicitação segue uma máquina de estados simples — não é possível
pular etapas arbitrariamente:

```
ABERTA        → EM_ANDAMENTO, AGUARDANDO, CANCELADA
EM_ANDAMENTO  → AGUARDANDO, CONCLUIDA, CANCELADA, ABERTA
AGUARDANDO    → EM_ANDAMENTO, CANCELADA, ABERTA
CONCLUIDA     → ABERTA (reabertura)
CANCELADA     → ABERTA (reabertura)
```

Transições fora dessa tabela retornam `400 Bad Request`. Apenas ANALYST e ADMIN podem alterar
status, prioridade e responsável.

**Propriedade de registro.** Um usuário comum (`USER`) só visualiza/edita solicitações onde é
solicitante ou responsável; tentar acessar pelo ID de uma solicitação de outra pessoa retorna
`403 Forbidden`, mesmo alterando a URL manualmente.

**Proteção do último administrador e autoexclusão**, aplicadas em `UserService`:
- Um administrador não pode excluir nem desativar a própria conta (`403`).
- Ninguém pode excluir, desativar ou rebaixar de papel o **último** administrador ativo do
  sistema (`409 Conflict`) — sempre deve sobrar ao menos um admin operante.
- Excluir um usuário que possui solicitações, comentários, anexos ou histórico vinculados
  retorna `409 Conflict` em vez de um erro de banco não tratado; a alternativa recomendada é
  desativar o usuário.

**Exclusão lógica.** Solicitações nunca são apagadas fisicamente (`is_deleted=true`); a exclusão
também gera uma entrada `EXCLUSAO` no histórico de auditoria.

**Dashboard por papel.** ADMIN e ANALYST veem indicadores globais (todas as solicitações).
Um usuário `USER` vê apenas indicadores das solicitações onde é solicitante ou responsável — os
totais da empresa não são expostos a esse perfil.

## Segurança em produção

Ao iniciar (`app/main.py`, antes mesmo do servidor subir), o backend chama
`Settings.validate_for_production()`, que só tem efeito quando `ENVIRONMENT=production`. Nesse
caso, a aplicação **recusa iniciar** (levanta `RuntimeError` e encerra o processo) se detectar:

- `SECRET_KEY` igual a um dos valores de exemplo do `.env.example`, ou com menos de 32 caracteres;
- `ADMIN_PASSWORD` igual ao valor de exemplo, ou com menos de 8 caracteres;
- `DATABASE_URL` ainda usando a credencial padrão `postgres:postgres`;
- `CORS_ORIGINS` contendo `*` (aberto para qualquer origem).

Em `ENVIRONMENT=development` (padrão) ou `test`, essas checagens não têm efeito, para não
atrapalhar o ambiente local. Veja `backend/tests/test_config_security.py` para os testes desse
comportamento.

## Principais decisões arquiteturais

- **Separação de camadas no backend** (`routes` → `services` → `repositories` → `models`) para
  manter regras de negócio fora dos endpoints e evitar duplicação.
- **Exclusão lógica de solicitações** (`is_deleted`), preservando o histórico e rastreabilidade em
  vez de apagar dados definitivamente.
- **Histórico automático**: qualquer alteração relevante (status, prioridade, responsável, edição
  de dados, comentário, anexo) gera uma entrada em `request_history`, registrada pelo
  `HistoryService` dentro da mesma transação da alteração.
- **Anexos com armazenamento local organizado**: nomes de arquivo gerados com UUID (evita
  sobrescrita e *path traversal*), validação de extensão/tamanho antes de gravar, e download apenas
  através de endpoint autenticado — nunca por caminho direto no sistema de arquivos. A estrutura
  (`AttachmentService`) já isola a lógica de armazenamento, facilitando trocar para um provedor de
  nuvem (S3, GCS etc.) no futuro sem alterar as rotas.
- **Pinia usado apenas para autenticação**: é o único estado realmente global e compartilhado por
  toda a aplicação (header, sidebar, middlewares). Demais estados de tela ficam locais aos
  componentes/páginas via Composition API.
- **Cliente de API centralizado** (`frontend/app/plugins/api.ts` + composables em
  `frontend/app/composables/`): nenhum componente monta URLs de API diretamente.
- **Enums no banco de dados** (`user_role`, `request_status`, `request_priority`,
  `request_category`, `history_action`) para garantir consistência de dados no nível do banco,
  além da validação do Pydantic na camada de API.

## Problemas comuns

- **`password cannot be longer than 72 bytes` ou erro de bcrypt ao rodar os testes**: use a versão
  de `bcrypt` fixada no `pyproject.toml` (`bcrypt==4.0.1`); versões mais novas têm incompatibilidade
  conhecida com o Passlib 1.7.4.
- **E-mails com domínio `.local` são rejeitados na validação (`EmailStr`)**: a biblioteca
  `email-validator` recusa alguns TLDs reservados como `.local`. Por isso o e-mail padrão do
  administrador é `admin@example.com` (`.com` reservado pela RFC 2606 para documentação, aceito
  pelo validador) — não use `.local` em e-mails reais de usuários.
- **`alembic upgrade head` falha com `type "user_role" already exists` em um banco limpo**: isso
  indicava um bug já corrigido nesta auditoria (a migration criava os enums duas vezes). Se ainda
  ocorrer, confirme que está usando a versão corrigida de `0001_initial.py` (sem chamadas
  explícitas de `.create()` para os enums no `upgrade()`).
- **Backend recusa iniciar com `RuntimeError: Configuracao insegura`**: isso é esperado se
  `ENVIRONMENT=production` estiver definido com valores de exemplo (`SECRET_KEY`,
  `ADMIN_PASSWORD` ou `DATABASE_URL` padrão, ou `CORS_ORIGINS=*`). Veja
  [Segurança em produção](#segurança-em-produção). Para desenvolvimento local, use
  `ENVIRONMENT=development` (padrão do `.env.example`).
- **Frontend não conecta ao backend**: confira se `NUXT_PUBLIC_API_BASE` (frontend) aponta para a
  mesma origem configurada em `CORS_ORIGINS` (backend) e se o backend está acessível na porta 8000.
- **Erro ao rodar `alembic upgrade head`**: confirme que `DATABASE_URL` no `.env` do backend aponta
  para um PostgreSQL acessível e que o banco já existe (`createdb central_solicitacoes`).
- **`npm run typecheck` falha com `Cannot find name 'process'`**: garanta que `@types/node` está
  instalado (`npm ci`); essa dependência é necessária porque `nuxt.config.ts` lê `process.env`.

## Próximos passos

- Adicionar paginação por cursor para grandes volumes de solicitações.
- Migrar o armazenamento de anexos para um provedor de nuvem (S3/GCS), reaproveitando a interface
  já isolada em `AttachmentService`.
- Adicionar testes end-to-end no frontend (ex.: Playwright) cobrindo os principais fluxos de tela.
- Tornar as categorias de solicitação configuráveis via banco de dados (hoje são um enum fixo,
  como enum do banco, mas isolado em `app/models/enums.py` para facilitar a migração).
- Adicionar notificações por e-mail em mudanças de status e novos comentários.
- Implementar refresh token para sessões de longa duração, hoje limitadas pela expiração fixa do
  `ACCESS_TOKEN_EXPIRE_MINUTES`.
- Adicionar um lock distribuído (ex.: advisory lock do PostgreSQL) em torno de `alembic upgrade
  head` no `CMD` do `backend/Dockerfile` antes de permitir múltiplas réplicas do backend — hoje o
  Docker Compose sobe apenas uma instância de cada serviço, então não há risco de migrations
  concorrentes, mas isso passaria a ser um risco real ao escalar horizontalmente (`docker compose
  up --scale backend=N`).
