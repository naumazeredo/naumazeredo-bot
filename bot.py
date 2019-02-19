#!/usr/bin/env python
# encoding=utf-8

import sys
import os
import logging
import dataset
from telegram import *
from telegram.ext import *
from emoji import emojize

logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

token = os.environ['TOKEN']

updater = Updater(token=token)
dispatcher = updater.dispatcher

db = dataset.connect("sqlite:///bot.db")

ADMINS = [187158190]

def is_admin(update):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        return False
    return True


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text='It\'s a trap, Bino!')


def noob(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Do you mean: @Laderlappen?')


def luucasv(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text=emojize('Do you mean: :heart:?', use_aliases=True))


def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text=update.message.text)


def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id,
                     text=text_caps)


def inline_caps(bot, update):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
            )
        )
    bot.answer_inline_query(update.inline_query.id, results)


def alarm(bot, job):
    bot.send_message(chat_id=job.context,
                     text='BEEP')


def timer(bot, update, job_queue):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Setting a timer!')

    job_queue.run_once(alarm, 10, context=update.message.chat_id)


def type_smt(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id,
                         action=telegram.ChatAction.TYPING)


def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="42")


def beca(bot, update):
    kiss_button = InlineKeyboardButton("Kiss",
                                       callback_data="😘")
    hug_button = InlineKeyboardButton("Hug",
                                      callback_data="🤗")

    custom_keyboard = [[ kiss_button, hug_button ]]
    reply_markup = InlineKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text='What do you want?',
                     reply_markup=reply_markup)


def query_result(bot, update):
    query = update.callback_query

    bot.edit_message_text(chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text=query.data)


def answer(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="What's the answer to Life, the Universe and Everything?",
                     reply_markup=ForceReply())


def samuraiexx(bot, update):
    custom_keyboard = [[
        InlineKeyboardButton("Sim", callback_data="👾"),
        InlineKeyboardButton("Com certeza", callback_data="🤖")
    ]]
    reply_markup = InlineKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text='O de Castro é noob?',
                     reply_markup=reply_markup)


def my_id(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="User ID: " + str(update.message.from_user.id))

def rank_markup(rank):
    if rank < 1200: return '*'
    if rank >= 1600 and rank < 1900: return '_'
    if rank >= 1900: return '_*'
    return ''


def conceito(bot, update, args):
    if len(args) == 0:
        conceitos = db['conceitos']
        result = list(conceitos.all(order_by='-rank'))

        msg = "*Ranking dos conceitos*\n"

        for user in result:
            markup = rank_markup(user['rank'])

            msg += user['name'] + ': ';
            rank = user['rank']
            msg += markup
            msg += str(user['rank'])
            msg += markup[::-1]
            msg += '\n'

        bot.send_message(chat_id=update.message.chat_id,
                         text=msg,
                         parse_mode=ParseMode.MARKDOWN)
    elif not is_admin(update):
        bot.send_message(chat_id=update.message.chat_id,
                         text="Acesso negado. Seu conceito eu que decido!")
    elif len(args) == 2:
        name = args[0]
        delta = int(args[1])

        if delta == 0:
            bot.send_message(chat_id=update.message.chat_id, text="Nada para atualizar!")
            return

        conceitos = db['conceitos']
        conceitos.insert_ignore(dict(lowername=name.lower(),
                                     name=name,
                                     rank=1500),
                                ['lowername'])
        user = conceitos.find_one(lowername=name.lower())
        user['rank'] += delta
        conceitos.update(user, ['id'])

        print(user)

        markup = rank_markup(user['rank'])

        msg = ''

        if delta < 0: msg += "*Voce caiu no meu conceito*\n"
        else: msg += "*Subindo no conceito... Muito bem!*\n"

        msg += user['name']
        msg += ": "
        msg += markup
        msg += str(user['rank'])
        msg += markup[::-1]

        bot.send_message(chat_id=update.message.chat_id,
                         text=msg,
                         parse_mode=ParseMode.MARKDOWN)
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Comando incorreto\nUso: /conceito [nome delta_conceito]")


def main():

    start_handler = CommandHandler('start', start)
    noob_handler = CommandHandler('noob', noob)
    luucasv_handler = CommandHandler('luucasv', luucasv)
    samuraiexx_handler = CommandHandler('samuraiexx', samuraiexx)
    unknown_handler = MessageHandler(Filters.command, unknown)

    echo_handler = MessageHandler(Filters.text, echo)
    caps_handler = CommandHandler('caps', caps, pass_args=True)
    inline_caps_handler = InlineQueryHandler(inline_caps)
    timer_handler = CommandHandler('timer', timer, pass_job_queue=True)

    type_smt_handler = CommandHandler('type', type_smt)

    beca_handler = CommandHandler('beca', beca)

    answer_handler = CommandHandler('answer', answer)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(noob_handler)
    dispatcher.add_handler(luucasv_handler)
    dispatcher.add_handler(samuraiexx_handler)

    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(caps_handler)
    dispatcher.add_handler(inline_caps_handler)
    dispatcher.add_handler(timer_handler)

    dispatcher.add_handler(type_smt_handler)

    dispatcher.add_handler(beca_handler)

    dispatcher.add_handler(CallbackQueryHandler(query_result))

    dispatcher.add_handler(answer_handler)

    dispatcher.add_handler(CommandHandler('my_id', my_id))

    dispatcher.add_handler(CommandHandler('conceito', conceito, pass_args=True))

    dispatcher.add_handler(unknown_handler)

    print("Melhor bot da fase da Terra está rodando em 3... 2... 1...")

    updater.start_polling()


if __name__ == "__main__":
    main()
