from src.objs import *
from src.functions.floodControl import floodControl
from src.functions.convert import convertSize
from src.functions.exceptions import exceptions, noAccount

#: File manager
@bot.message_handler(commands=['files'])
def files(message, userLanguage=None):
    userId = message.from_user.id
    userLanguage = userLanguage or dbSql.getSetting(userId, 'language')

    if floodControl(message, userLanguage):
        if ac := dbSql.getDefaultAc(userId):
            account = Seedr(token=ac['token'])
            response = account.listContents().json()

            if 'error' in response:
                exceptions(message, response, ac, userLanguage)

            elif response['folders']:
                text = ''

                for i in response['folders']:
                    text += f"<b>📂 {i['fullname']}</b>\n\n💾 {convertSize(i['size'])}B, ⏰ {i['last_update']}"
                    text += f"\n\n{language['files'][userLanguage]} /getFiles_{i['id']}\n{language['link'][userLanguage]} /getLink_{i['id']}\n{language['delete'][userLanguage]} /delete_{i['id']}\n\n"

                bot.send_message(message.chat.id, text)

            else:
                bot.send_message(message.chat.id, language['noFiles'][userLanguage])
        else:
            noAccount(message, userLanguage)