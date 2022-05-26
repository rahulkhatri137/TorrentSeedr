from src.objs import *
from src.functions.floodControl import floodControl
from src.functions.exceptions import exceptions, noAccount

#: Cancel active downloads
@bot.message_handler(func=lambda message: message.text and message.text[:8] == '/cancel_')
def cancelDownload(message, called=False):
    userId = message.from_user.id
    userLanguage = dbSql.getSetting(userId, 'language')

    if floodControl(message, userLanguage):
        if ac := dbSql.getDefaultAc(userId):
            account = Seedr(token=ac['token'])

            if not called:
                sent = bot.send_message(message.chat.id, language['cancellingDownload'][userLanguage])
                id = message.text[8:]

            else:
                id = message.data[7:]

            response = account.deleteTorrent(id).json()

            if 'error' in response:
                exceptions(message, response, ac, userLanguage, called)

            elif response['result'] == True:
                bot.edit_message_text(text=language['cancelledSuccessfully'][userLanguage], chat_id=message.message.chat.id if called else message.chat.id, message_id=message.message.id if called else sent.id)

        else:
            noAccount(message, userLanguage)