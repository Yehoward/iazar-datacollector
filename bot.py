from os import environ
import csv
import sys
import asyncio
from datetime import datetime
from pathlib import Path

from telebot import TeleBot, types as T
from telebot.async_telebot import AsyncTeleBot
from telebot.util import quick_markup

from transformers import pipeline

TOKEN = environ["KEY"]

bot = AsyncTeleBot(TOKEN)


pipe = pipeline(model="Yehoward/whisper-small-ro")

udata = {}


def transcribe(audio: bytes) -> str:
    return pipe(audio)["text"]


def is_voice(msg: T.Message) -> bool:
    return msg.voice is not None

@bot.message_handler(commands=["ajutor", "start", "help"])
async def ajutor(msg: T.Message):
    H_MESSAGE = """
Colectăm date în <a href="https://wiki.froth.zone/wiki/Graiul_moldovenesc?lang=ro">graiul Moldovenesc</a> pentru antrenarea mea.
Datele vor fi un mesaj vocal și transcrierea/conținutul mesajului.

<strong>
Reguli:
    - Nu transmiteți mesaje mai lungi de 30s.
    - Nu transmiteți mesaje cu conținut vulgar.
    - Nu utilizați neologisme (cuvinte împrumutate din alte limbi).
    - Nu utilizați alfabet străin.
</strong>

Utilizare:
    - Transmiteți un mesaj vocal
    - Dupa procesare, corectați textul propus de robot
    - Cînd textul coiencide cu ceea ce a fost spus în audio, salvați
"""

    await bot.send_message(msg.chat.id, H_MESSAGE, parse_mode="html", disable_web_page_preview=True)

@bot.message_handler(content_types=["voice"])
async def transcribe_voice(msg: T.Message):

    print("am primit mesaj vocal")
    if msg.voice is None:
        print("transcribe_voice: Telebot bug", file=sys.stderr)
        return

    if udata.get(msg.from_user.id) is not None:
        await bot.reply_to(
            msg, "Ștergem audioul nesalvat. Dacă doriți să-l salvați, retransmiteți-l."
        )

    if msg.voice.duration >= 30:
        await bot.send_message(msg.chat.id, "Mesajul vocal depășește limita de 30s" )
        return

    raspuns = await bot.reply_to(msg, "descarcăm audioul")
    file: T.File = await bot.get_file(msg.voice.file_id)
    data = await bot.download_file(file.file_path)

    text = transcribe(data)

    udata[msg.from_user.id] = {
        "audio": data,
        "text": text,
        "msg_v": raspuns,
    }

    kb = quick_markup(
        {
            "salvează": {"callback_data": "salveaza"},
        },
        row_width=1,
    )

    await bot.edit_message_text(
        f"Copiați și transmiteți-mi textul corectat:\n<code>{text}</code>",
        msg.chat.id,
        raspuns.id,
        reply_markup=kb,
        parse_mode="html",
    )



@bot.callback_query_handler(func=lambda par: par.data == "salveaza")
async def salvare(call: T.CallbackQuery):
    await _salvare(call.message, call.from_user.id)

@bot.message_handler(commands=["salv"])
async def save_from_message(msg: T.Message):
    await _salvare(msg, msg.from_user.id)

async def _salvare(call: T.Message, user_id):
    name = datetime.now().isoformat(timespec="seconds")
    data = udata[user_id]["audio"]
    text = udata[user_id]["text"]
    audio_name = f"data/tg-{name}.wav"
    with open(f"dataset/data/tg-{name}.wav", "bx") as a:
        a.write(data)

    csv_path = Path().cwd() / "dataset" / "nevalidate.csv"

    with open(csv_path, "a") as f:
        print("info: salvăm datele in csv")
        data = csv.DictWriter(f, ["file_name", "transcription"])
        data.writerow({"file_name": audio_name, "transcription": text})

    print("info: datele-s salvate")


    udata.pop(user_id)

    await bot.send_message(
        call.chat.id,
        f"Datele au fost salvate. Vă mulțumim",
        reply_markup=None,
    )


@bot.message_handler(content_types=["text"])
async def edit_text(msg: T.Message):
    if msg.from_user.id not in udata.keys():
        return

    raspuns = udata[msg.from_user.id]["msg_v"]
    text = msg.text
    udata[msg.from_user.id]["text"] = text

    await bot.edit_message_reply_markup(
        msg.chat.id,
        raspuns.id,
    )
    udata[msg.from_user.id]["msg_v"] = await bot.reply_to(
        msg,
        f"Copiați și transmiteți-mi textul corectat:\n<code>{text}</code>",
        reply_markup=quick_markup(
            {
                "salvează": {"callback_data": "salveaza"},
            },
            row_width=1,
        ),
        parse_mode="html",
    )





async def main():
    await bot.infinity_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
