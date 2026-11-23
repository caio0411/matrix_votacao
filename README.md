# Votação com Matrix

Bot de enquetes para salas do [Matrix](https://matrix.org). Os participantes criam enquetes e votam por comandos no chat. O estado da enquete (pergunta, opções e votos) fica salvo na própria sala, como um evento de estado (`sd.trabalho.enquete`), e não no bot. Se o bot for reiniciado, nada se perde.

Trabalho da disciplina de Sistemas Distribuídos.

## Comandos

| Comando | O que faz |
|---|---|
| `!enquete Pergunta \| Opção 1 \| Opção 2` | Cria uma enquete (2 a 10 opções) |
| `!votar N` | Vota na opção N. Votar de novo troca o voto |
| `!resultado` | Mostra a apuração |
| `!encerrar` | Encerra a enquete (só quem criou) |
| `!ajuda` | Lista os comandos |

## Estrutura

| Arquivo | Função |
|---|---|
| `bot.py` | Conexão com o Matrix: login, recebe mensagens, lê e grava o estado da sala |
| `enquete.py` | Regras da enquete (criar, votar, encerrar, apurar) |
| `test_enquete.py` | Testes das regras |
| `docker-compose.yml` | Sobe o servidor Matrix (Synapse) e o cliente web (Element) |
| `element-config.json` | Aponta o Element para o servidor local |

## Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (no Linux, Docker e Docker Compose)
- [Python](https://www.python.org/downloads/) 3.10 ou mais novo
- Git

## Primeira execução

Faça isso só uma vez. Todos os comandos são executados dentro da pasta do projeto.

### 1. Baixar o projeto

```bash
git clone https://github.com/caio0411/matrix_votacao.git
cd matrix_votacao
```

### 2. Gerar a configuração do servidor

```bash
docker compose run --rm -e SYNAPSE_SERVER_NAME=localhost -e SYNAPSE_REPORT_STATS=no synapse generate
```

Isso cria a pasta `synapse-data/`.

### 3. Subir o servidor e o cliente web

```bash
docker compose up -d
```

Aguarde uns 30 segundos e abra http://localhost:8008. Deve aparecer "It works! Synapse is running".

### 4. Criar os usuários

```bash
docker compose exec synapse register_new_matrix_user -c /data/homeserver.yaml -u enquete -p enquete123 --no-admin http://localhost:8008
docker compose exec synapse register_new_matrix_user -c /data/homeserver.yaml -u ana -p ana12345 --no-admin http://localhost:8008
docker compose exec synapse register_new_matrix_user -c /data/homeserver.yaml -u beto -p beto12345 --no-admin http://localhost:8008
```

`enquete` é a conta do bot. `ana` e `beto` são usuários de teste. Para criar outros, repita o comando trocando `-u` e `-p`.

### 5. Instalar as dependências do bot

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se o PowerShell bloquear o `Activate.ps1`, rode antes: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Linux e macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 6. Iniciar o bot

```bash
python bot.py
```

Quando aparecer `Bot pronto`, deixe o terminal aberto.

### 7. Configurar a sala no navegador

1. Abra http://localhost:8080 e entre com `ana` / `ana12345`.
2. Crie uma sala nova com a criptografia desligada. O bot não lê salas criptografadas.
3. Na sala, convide o bot e o Beto:
   ```
   /invite @enquete:localhost
   /invite @beto:localhost
   ```
4. Dê permissão de moderador ao bot (necessário para salvar a enquete na sala):
   ```
   /op @enquete:localhost 50
   ```
5. Em outro navegador ou numa janela anônima, entre com `beto` / `beto12345` e aceite o convite.
6. Teste: `!enquete Onde almoçar? | Pizza | Sushi | Salada`, depois `!votar 1`.

Para ver o estado salvo na sala, digite `/devtools`, clique em "Explore room state" e abra `sd.trabalho.enquete`.

## Próximas execuções

Contas e salas ficam salvas. Para ligar tudo de novo:

Windows:

```powershell
docker compose up -d
.venv\Scripts\Activate.ps1
python bot.py
```

Linux e macOS:

```bash
docker compose up -d
source .venv/bin/activate
python bot.py
```

Para desligar: `Ctrl+C` no terminal do bot e depois `docker compose down`.

Para apagar tudo e começar do zero, apague também a pasta `synapse-data/`.


## Problemas comuns

| Problema | Solução |
|---|---|
| `Connection refused` ao criar usuários | O servidor ainda está iniciando. Aguarde e tente de novo |
| O bot não responde | A sala está criptografada. Crie outra com a criptografia desligada |
| Bot avisa que precisa ser moderador | Rode `/op @enquete:localhost 50` na sala |
| `Falha no login` ao iniciar o bot | O usuário `enquete` não foi criado ou o servidor está desligado |
| Element pede verificação de sessão | Clique em "Can't confirm?" e depois em "Reset", confirmando com a senha |
| Porta 8008 ou 8080 ocupada | Troque o número à esquerda em `ports` no `docker-compose.yml` |
