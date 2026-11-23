"""Bot de enquetes para Matrix. O estado da enquete fica salvo na sala, não no bot."""

import asyncio
import os

from nio import (
    AsyncClient,
    InviteMemberEvent,
    LoginResponse,
    MatrixRoom,
    RoomGetStateEventResponse,
    RoomMessageText,
    RoomPutStateResponse,
)

import enquete

HOMESERVER = os.environ.get("MATRIX_HOMESERVER", "http://localhost:8008")
USUARIO = os.environ.get("MATRIX_USUARIO", "@enquete:localhost")
SENHA = os.environ.get("MATRIX_SENHA", "enquete123")

# Tipo do evento de estado onde a enquete é guardada
TIPO_ESTADO = "sd.trabalho.enquete"

client = AsyncClient(HOMESERVER, USUARIO)


async def ler_estado(sala_id):
    resposta = await client.room_get_state_event(sala_id, TIPO_ESTADO, "")
    if isinstance(resposta, RoomGetStateEventResponse) and resposta.content:
        return resposta.content
    return None


async def gravar_estado(sala_id, estado):
    resposta = await client.room_put_state(sala_id, TIPO_ESTADO, estado, state_key="")
    return isinstance(resposta, RoomPutStateResponse)


async def enviar(sala_id, texto):
    await client.room_send(
        sala_id,
        message_type="m.room.message",
        content={"msgtype": "m.text", "body": texto},
    )


async def ao_receber_mensagem(sala: MatrixRoom, evento: RoomMessageText):
    if evento.sender == client.user_id or not evento.body.startswith("!"):
        return

    estado = await ler_estado(sala.room_id)
    novo_estado, resposta = enquete.processar_comando(evento.body, evento.sender, estado)

    if novo_estado is not None and not await gravar_estado(sala.room_id, novo_estado):
        resposta = (
            "Não consegui salvar a enquete: o bot precisa ser moderador.\n"
            f"Digite na sala: /op {client.user_id} 50"
        )

    if resposta:
        await enviar(sala.room_id, resposta)
    print(f"[{sala.display_name}] {evento.sender}: {evento.body}")


async def ao_receber_convite(sala, evento: InviteMemberEvent):
    if evento.state_key == client.user_id and evento.membership == "invite":
        await client.join(sala.room_id)
        await enviar(sala.room_id, "Olá! Sou o bot de enquetes. Digite !ajuda")
        print(f"Entrei na sala {sala.room_id}")


async def main():
    resposta = await client.login(SENHA, device_name="bot-enquete")
    if not isinstance(resposta, LoginResponse):
        print("Falha no login:", resposta)
        await client.close()
        return
    print("Logado como", client.user_id)

    # Primeiro sync sem callbacks: ignora mensagens antigas
    await client.sync(timeout=10000, full_state=True)

    for sala_id in list(client.invited_rooms):
        await client.join(sala_id)

    client.add_event_callback(ao_receber_mensagem, RoomMessageText)
    client.add_event_callback(ao_receber_convite, InviteMemberEvent)

    print("Bot pronto. Convide", client.user_id, "para uma sala.")
    try:
        await client.sync_forever(timeout=30000)
    finally:
        await client.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot encerrado.")
