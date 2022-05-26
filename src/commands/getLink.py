from src.objs import *
from src.functions.urlEncode import urlEncode
from src.functions.floodControl import floodControl
from src.functions.exceptions import exceptions, noAccount

#: Get download link of torrents
@bot.message_handler(func=lambda message: message.text and message.text[:9] == '/getLink_')
def getLink(message, called=False):
    userId = message.from_user.id
    userLanguage = dbSql.getSetting(userId, 'language')

    if floodControl(message, userLanguage):
        if ac := dbSql.getDefaultAc(userId):
            id = message.data[8:] if called else message.text[9:]
            account = Seedr(token=ac['token'])

            response = account.createArchive(id).json()

            if 'error' in response:
                exceptions(message, response, ac, userLanguage, called)

            elif 'archive_url' in response:
                encodedUrl = urlEncode(response['archive_url'])
                text = f"🔗 <code>{encodedUrl}</code>\n\n<b>🔥via @TorrentSeedrBot</b>"

                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(telebot.types.InlineKeyboardButton(text=language['openInBrowserBtn'][userLanguage], url=encodedUrl))
                markup.add(telebot.types.InlineKeyboardButton(text=language['openInPlayerBtn'][userLanguage], callback_data=f'getPlaylist_000_folder_{id}'))
                markup.add(telebot.types.InlineKeyboardButton(text=language['showFilesBtn'][userLanguage], callback_data=f'getFiles_{id}'), telebot.types.InlineKeyboardButton(text=language['deleteBtn'][userLanguage], callback_data=f'delete_{id}'))
                markup.add(telebot.types.InlineKeyboardButton(text=language['joinChannelBtn'][userLanguage], url='t.me/h9youtube'), telebot.types.InlineKeyboardButton(text=language['joinDiscussionBtn'][userLanguage], url='https://t.me/+mxHaXtNFM1g5MzI1'))

                if called:
                    bot.answer_callback_query(message.id)
                    bot.edit_message_text(text=text, chat_id=message.message.chat.id, message_id=message.message.id, reply_markup=markup)
                else:
                    bot.send_message(text=text, chat_id=message.chat.id, reply_markup=markup)

        else:
            noAccount(message, userLanguage)