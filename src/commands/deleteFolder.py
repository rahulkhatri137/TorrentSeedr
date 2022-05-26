from src.objs import *
from src.functions.floodControl import floodControl
from src.functions.exceptions import exceptions, noAccount

#: Delete folder
@bot.message_handler(func=lambda message: message.text and message.text[:8] == '/delete_')
def deleteFolder(message, called=False):
    userId = message.from_user.id
    userLanguage = dbSql.getSetting(userId, 'language')

    if floodControl(message, userLanguage):
        if ac := dbSql.getDefaultAc(userId):
            account = Seedr(token=ac['token'])

            id = message.data[7:] if called else message.text[8:]
            response = account.deleteFolder(id).json()

            if 'error' in response:
                exceptions(message, response, ac, userLanguage, called)

            elif response['result'] == True:
                if called:
                    bot.answer_callback_query(message.id)
                    bot.edit_message_text(text=language['deletedSuccessfully'][userLanguage], chat_id=message.message.chat.id, message_id=message.message.id)
                else:
                    bot.send_message(message.chat.id, language['deletedSuccessfully'][userLanguage])

        else:
            noAccount(message, userLanguage)