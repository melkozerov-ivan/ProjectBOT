import logging
import datetime

from telegram.ext import Application, MessageHandler, filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup
from config import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


async def echo(update, context):
    q = f'Я получил сообщение "{update.message.text}"'
    await update.message.reply_text(q)
    return 2


async def eeecho(update, context):
    q = f'{update.message.text}'
    await update.message.reply_text(q.upper() + ' ' + q.lower() + '...')
    return ConversationHandler.END


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я эхо-бот. Напишите мне что-нибудь, и я пришлю это назад!")
    return 1


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


TIMER = 0


async def set_timer(update, context):
    global TIMER
    TIMER = int(f'{update.message.text}'.replace('/timer ', ''))
    print(TIMER)
    chat_id = update.effective_message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    context.job_queue.run_once(task, TIMER, chat_id=chat_id, name=str(chat_id), data=TIMER)

    text = f'Вернусь через {TIMER} с.!'
    if job_removed:
        text += ' Старая задача удалена.'
    await update.effective_message.reply_text(text)


async def task(context):
    await context.bot.send_message(context.job.chat_id, text=f'КУКУ! {TIMER}c. прошли!')


async def unset(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    await update.message.reply_text(text)


async def fdate(update, context):
    q = datetime.datetime.now()
    await update.message.reply_html(str(q).split()[0], reply_markup=markup) + f'{update.message.text}'


async def ftime(update, context):
    q = datetime.datetime.now()
    await update.message.reply_html(str(q).split()[1].split('.')[0], reply_markup=markup)


async def help_command(update, context):
    await update.message.reply_text("Я пока не умею помогать... Я только ваше эхо.",
                                    reply_markup=markup)


async def stop(update, context):
    await update.message.reply_text("Тишина...", reply_markup=markup)
    return ConversationHandler.END


markup = ReplyKeyboardMarkup([['/help', '/start'], ['/date', '/time'], ['/timer', '/unset']], one_time_keyboard=False)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, echo)],

            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, eeecho)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("date", fdate))
    application.add_handler(CommandHandler("time", ftime))
    application.add_handler(CommandHandler("timer", set_timer))
    application.add_handler(CommandHandler("unset", unset))

    application.run_polling()


if __name__ == '__main__':
    main()
