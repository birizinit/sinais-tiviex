import datetime
import asyncio
import random
from telegram import Bot
from zoneinfo import ZoneInfo
import telegram

# === CONFIGURAÇÃO ===
TOKEN = "8468170406:AAGZiiK9SE9lFhwUbO2vewQnxo0NSPu8rgI"
CHAT_ID = -1003063576776
bot = Bot(token=TOKEN)

# === ATIVOS e DIREÇÕES ===
ATIVOS = ["Apple (AAPL)", "McDonald's (MCD)", "Microsoft (MSFT)", "Amazon (AMZN)",
          "Tesla (TSLA)", "Netflix (NFLX)", "Google (GOOG)", "Meta/Facebook (META)"]
DIRECOES = ["🔼 COMPRA", "🔽 VENDA"]

# === STICKERS ===
STICKER_INICIO = "CAACAgEAAxkBAAEPcZpo1YeOkeCILbIZD6DGEv14zx6Y_AACAwYAAmXAsEZ3GRkV3WqvdTYE"
STICKER_FIM = "CAACAgEAAxkBAAEPcZto1YeP_HFimiAHYeNRm73GracfNAAClgUAAu-HqUaksw1H8w9fJjYE"
STICKER_WIN = "CAACAgEAAxkBAAEPcZlo1YeOG9Pjhi_VZuK6qTKTBXYKtgACuwUAAnhvsUbtXNxLGzm8jzYE"

LINK_CORRETORA = "https://app.lyrenbroker.com/auth/register"

# === PLACAR DIÁRIO ===
placar = {"WIN": 0, "LOSS": 0}
ultimo_reset = datetime.date.today()

def resetar_placar():
    global placar, ultimo_reset
    hoje = datetime.date.today()
    if hoje != ultimo_reset:
        placar = {"WIN": 0, "LOSS": 0}
        ultimo_reset = hoje

# === FUNÇÃO PARA ENVIAR UM SINAL ===
async def enviar_sinal(horario_sinal):
    ativo = random.choice(ATIVOS)
    direcao = random.choice(DIRECOES)

    gale1 = (horario_sinal + datetime.timedelta(minutes=1)).strftime("%H:%M")
    gale2 = (horario_sinal + datetime.timedelta(minutes=2)).strftime("%H:%M")

    mensagem = f"""🔛 OPERAÇÃO CONFIRMADA
Corretora: Lyren Broker ✅

🥇 Moeda = {ativo}
⏰ Expiração = 1 Minutos
📌 Entrada = {horario_sinal.strftime("%H:%M")}
{direcao}

⚠️ Proteção 1: {gale1}
⚠️ Proteção 2: {gale2}

➡️ Clique aqui para acessar a corretora 👇🏻
{LINK_CORRETORA}
"""
    await bot.send_message(chat_id=CHAT_ID, text=mensagem, parse_mode="Markdown")

    # Espera 3 minutos e envia WIN/LOSS
    await asyncio.sleep(180)  # 3 minutos reais
    is_win = random.randint(1, 100) <= 80
    if is_win:
        placar["WIN"] += 1
        await bot.send_sticker(chat_id=CHAT_ID, sticker=STICKER_WIN)
        return f"{horario_sinal.strftime('%H:%M')} {ativo} ✅ WIN"
    else:
        placar["LOSS"] += 1
        mensagem_loss = f"""📺 Operação Confirmada 📺

     ❎ {ativo}

✅ {placar['WIN']} ❌ {placar['LOSS']}
❎ siga o gerenciamento

➡️ Clique aqui para acessar a corretora 👇🏻
{LINK_CORRETORA}"""
        await bot.send_message(chat_id=CHAT_ID, text=mensagem_loss)
        return f"{horario_sinal.strftime('%H:%M')} {ativo} ❌ LOSS"

# === RELATÓRIO FINAL DA SESSÃO ===
async def enviar_relatorio_sessao(nome_sessao, resultados, horario_sessao):
    total = placar["WIN"] + placar["LOSS"]
    taxa = (placar["WIN"] / total * 100) if total > 0 else 0
    texto = f"""📊 *Relatório da Sessão {nome_sessao} ({horario_sessao.strftime('%H:%M')})*

{chr(10).join(resultados)}

✅ WIN: {placar['WIN']}
❌ LOSS: {placar['LOSS']}
📈 Taxa de acerto: {taxa:.2f}%
📊 Total de operações: {total}

➡️ Clique aqui para acessar a corretora 👇🏻
{LINK_CORRETORA}"""
    await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode="Markdown")

# === EXECUÇÃO DE UMA SESSÃO ===
async def executar_sessao(nome_sessao, hora, minuto, live=False):
    zona = ZoneInfo("America/Sao_Paulo")
    agora = datetime.datetime.now(zona)
    inicio = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)

    if agora > inicio:
        return

    # Sticker de início (10 min antes) somente se não-LIVE
    if not live:
        aviso = inicio - datetime.timedelta(minutes=10)
        await asyncio.sleep(max(0, (aviso - agora).total_seconds()))
        await bot.send_sticker(chat_id=CHAT_ID, sticker=STICKER_INICIO)

    resultados = []
    intervalos = [5, 9, 3]  # minutos após o início do sinal
    for i in range(3):
        horario_sinal = inicio + datetime.timedelta(minutes=sum(intervalos[:i+1]))
        await asyncio.sleep(max(0, (horario_sinal - datetime.datetime.now(zona)).total_seconds()))
        resultado = await enviar_sinal(horario_sinal)
        resultados.append(resultado)

    # Sticker de fim de sessão 1 minuto após último resultado (somente se não-LIVE)
    if not live:
        await asyncio.sleep(60)
        await bot.send_sticker(chat_id=CHAT_ID, sticker=STICKER_FIM)

    # Relatório final
    await enviar_relatorio_sessao(nome_sessao, resultados, inicio)

# === LOOP PRINCIPAL ===
async def main():
    sessoes = [
        ("Sessão LIVE manhã", 9, 20, True),
        ("Sessão LIVE tarde", 13, 30, True),
        ("Sessão tarde", 15, 20, False),
        ("Sessão noite", 18, 0, False),
        ("Sessão LIVE noite", 20, 0, True),
    ]

    while True:
        resetar_placar()
        for nome, h, m, live in sessoes:
            await executar_sessao(nome, h, m, live)
        await asyncio.sleep(60)

# === START ===
asyncio.run(main())
