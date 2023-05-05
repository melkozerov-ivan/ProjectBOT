import logging

from random import choice, choices

from aiogram import Bot, Dispatcher, types

from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler

from telegram import ReplyKeyboardMarkup

import config

import sqlalchemy as sa

from data import db_session

from data.Players import Player

bot = Bot(token=config.BOT_TOKEN)

dp = Dispatcher(bot)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def users():
    db_sess = db_session.create_session()
    return db_sess.execute(sa.select(Player.login)).scalars().all()


def variants(integ):
    db_sess = db_session.create_session()
    q = choices(config.WEAPONS, 2 * integ)
    h = []
    for i in range(1, integ + 1):
        player = db_sess.query(Player).filter(Player.id == i).first()
        if player:
            player.weap = [q[2 * i - 2], q[2 * i - 1]]
            db_sess.commit()
    for i in range(1, integ + 1):
        user = db_sess.execute(sa.select(Player).where(Player.id == i)).scalars().first()
        h.append(user)
    return h


def killerwep(kil):
    db_sess = db_session.create_session()
    wep = db_sess.execute(sa.select(Player.weap).where(Player.id == kil)).scalars().first()
    return wep


def not_answered(login):
    db_sess = db_session.create_session()
    ans = db_sess.execute(sa.select(Player.ans).where(Player.id == login)).scalars().first()
    return ans


@dp.message_handler()
async def del_wep(message: types.Message):
    text = message.text
    if 'weap' in text:
        await message.delete()


@dp.message_handler(content_types=['new_chat_member'])
async def ad_to_db(message: types.Message):
    db_sess = db_session.create_session()
    user = Player(
        login=message.from_user.id
    )
    db_sess.add(user)
    db_sess.commit()


async def start(update, context):
    q = users()
    config.KILLER = choice(q)
    config.ALL_ANSWERS = len(q)
    await update.message.reply_text(f"Киллер - выбирайте орудие. Напишите weap, а затем название оружия.")
    await update.message.reply_text(variants(len(q)))
    return 1


async def register(update, context):
    q = f'Игра началась. Вычислите преступника и орудие убийства. Можно начинать обсуждение'
    weap = update.message.text
    if weap in killerwep(config.KILLER):
        config.KILLERWEP = weap
        await update.message.reply_text(q)
    else:
        await update.message.reply_text('Этого оружия нет в арсенале')


async def answer(update, context):
    q = f'Введите предпологаемое имя Убийцы и его оружие через пробел'
    await update.message.reply_text(q)
    return 3


async def check_answer(update, context):
    q = str(update.message.text).split()
    if not_answered(update.effective_user):
        if config.KILLERWEP == q[1] and config.KILLER == q[0]:
            await update.message.reply_text('Верно, победили инспектора')
            return ConversationHandler.END
        else:
            await update.message.reply_text("Обвинение ложно!")
            config.ALL_ANSWERS -= 1
            if config.ALL_ANSWERS == 0:
                return ConversationHandler.END


async def help_command(update, context):
    await update.message.reply_text("Я пока не умею помогать... Я только ваше эхо.",
                                    reply_markup=markup)


async def stop(update, context):  # Для киллера
    await update.message.reply_text("Тишина...", reply_markup=markup)
    return ConversationHandler.END


markup = ReplyKeyboardMarkup([['/help', '/start'], ['/date', '/time'], ['/timer', '/unset']], one_time_keyboard=False)


def main():
    application = Application.builder().token(config.BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, register)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("answer", answer))
    application.run_polling()


if __name__ == '__main__':
    main()


