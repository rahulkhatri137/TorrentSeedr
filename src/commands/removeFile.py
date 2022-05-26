from src.objs import *
from src.functions.floodControl import floodControl
from src.functions.exceptions import exceptions, noAccount

#: Remove files
@bot.message_handler(func=lambda message: message.text and message.text[:8] == '/remove_')
def removeFile(message):
    userId = message.from_user.id
    userLanguage = dbSql.getSetting(userId, 'language')

    if floodControl(message, userLanguage):
        if ac := dbSql.getDefaultAc(userId):
            sent = bot.send_message(message.chat.id, language['removingFile'][userLanguage])
            id = message.text[8:]

            account = Seedr(token=ac['token'])

            response = account.deleteFile(id).json()

            if 'error' in response:
                exceptions(message, response, ac, userLanguage)

            elif response['result'] == True:
                bot.edit_message_text(text=language['removedSuccessfully'][userLanguage], chat_id=message.chat.id, message_id=sent.id)

        else:
            noAccount(message, userLanguage)