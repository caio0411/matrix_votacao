"""Regras da enquete. Não depende do Matrix, por isso pode ser testado sem servidor."""

AJUDA = (
    "Comandos:\n"
    "!enquete Pergunta | Opção 1 | Opção 2   cria uma enquete\n"
    "!votar N      vota na opção N (votar de novo troca o voto)\n"
    "!resultado    mostra a apuração\n"
    "!encerrar     encerra a enquete (só quem criou)\n"
    "!ajuda        mostra esta mensagem"
)


def criar(texto, criador):
    partes = [parte.strip() for parte in texto.split("|")]
    pergunta = partes[0]
    opcoes = [parte for parte in partes[1:] if parte]

    if not pergunta or len(opcoes) < 2:
        raise ValueError("Formato: !enquete Pergunta | Opção 1 | Opção 2")
    if len(opcoes) > 10:
        raise ValueError("Use no máximo 10 opções.")

    return {
        "pergunta": pergunta,
        "opcoes": opcoes,
        "votos": {},  # usuário -> número da opção (1, 2, ...)
        "aberta": True,
        "criador": criador,
    }


def votar(estado, usuario, numero_texto):
    if not estado or not estado["aberta"]:
        raise ValueError("Não há enquete aberta nesta sala.")
    if not numero_texto.isdigit():
        raise ValueError("Formato: !votar N")

    numero = int(numero_texto)
    total = len(estado["opcoes"])
    if numero < 1 or numero > total:
        raise ValueError(f"Opção inválida. Escolha de 1 a {total}.")

    novo = dict(estado)
    novo["votos"] = dict(estado["votos"])
    novo["votos"][usuario] = numero  # sobrescreve: cada usuário tem um voto
    return novo


def encerrar(estado, usuario):
    if not estado or not estado["aberta"]:
        raise ValueError("Não há enquete aberta nesta sala.")
    if usuario != estado["criador"]:
        raise ValueError("Só quem criou a enquete pode encerrá-la.")

    novo = dict(estado)
    novo["aberta"] = False
    return novo


def contar(estado):
    contagem = [0] * len(estado["opcoes"])
    for numero in estado["votos"].values():
        contagem[numero - 1] += 1
    return contagem


def formatar(estado):
    contagem = contar(estado)
    total = sum(contagem)
    situacao = "aberta" if estado["aberta"] else "ENCERRADA"

    linhas = [f"Enquete ({situacao}): {estado['pergunta']}"]
    for i, opcao in enumerate(estado["opcoes"]):
        porcento = round(100 * contagem[i] / total) if total else 0
        linhas.append(f"  {i + 1}) {opcao}: {contagem[i]} voto(s) ({porcento}%)")
    linhas.append(f"Total: {total} voto(s)")
    return "\n".join(linhas)


def processar_comando(texto, remetente, estado):
    """Retorna (novo_estado, resposta). novo_estado é None quando nada muda."""
    comando, _, argumento = texto.strip().partition(" ")
    argumento = argumento.strip()

    try:
        if comando == "!ajuda":
            return None, AJUDA

        if comando == "!resultado":
            if not estado:
                return None, "Ainda não há enquete nesta sala."
            return None, formatar(estado)

        if comando == "!enquete":
            if estado and estado["aberta"]:
                return None, "Já existe uma enquete aberta. Use !encerrar antes."
            novo = criar(argumento, remetente)
            return novo, "Enquete criada!\n" + formatar(novo) + "\nVote com !votar N"

        if comando == "!votar":
            trocou = bool(estado) and remetente in estado["votos"]
            novo = votar(estado, remetente, argumento)
            numero = novo["votos"][remetente]
            acao = "trocou o voto para" if trocou else "votou em"
            return novo, f"{remetente} {acao} {numero}) {novo['opcoes'][numero - 1]}"

        if comando == "!encerrar":
            novo = encerrar(estado, remetente)
            return novo, "Enquete encerrada. Resultado final:\n" + formatar(novo)

    except ValueError as erro:
        return None, str(erro)

    return None, None  # não é comando do bot
