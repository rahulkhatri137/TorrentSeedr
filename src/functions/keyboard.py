from src.objs import *

#: Main reply keyboard
def mainReplyKeyboard(userId, userLanguage):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    button1 = telebot.types.KeyboardButton(text=language['fileManagerBtn'][userLanguage])
    button2 = telebot.types.KeyboardButton(text=language['activeTorrentsBtn'][userLanguage])
    button3 = telebot.types.KeyboardButton(text=language['wishlistBtn'][userLanguage])
    button4 = telebot.types.KeyboardButton(text=language['accountBtn'][userLanguage])
    button5 = telebot.types.KeyboardButton(text=language['settingsBtn'][userLanguage])
    button6 = telebot.types.KeyboardButton(text=language['helpBtn'][userLanguage])
    button7 = telebot.types.KeyboardButton(text=language['supportBtn'][userLanguage])
    button9 = telebot.types.KeyboardButton(text=language['addAccountBtn'][userLanguage])
    button10 = telebot.types.KeyboardButton(text=language['switchBtn'][userLanguage])
    button11 = telebot.types.KeyboardButton(text='🆓 Get free space')

    if account := dbSql.getAccounts(userId):
        keyboard.row(button1, button2)
        keyboard.row(button10, button3, button4) if len(account) > 1 else keyboard.row(button3, button4)

        if dbSql.getSetting(userId, 'githubId') == '0':
            keyboard.row(button11, button7)
        else:
            keyboard.row(button7)

    else:
        keyboard.row(button9)
    return keyboard

def githubAuthKeyboard(userLanguage):
    markup = telebot.types.InlineKeyboardMarkup()

    markup.add(
        telebot.types.InlineKeyboardButton(
            text=language['followOnGithubBtn'][userLanguage],
            url="https://github.com/hemantapkh",
        )
    )

    markup.add(telebot.types.InlineKeyboardButton(text=language['verifyBtn'][userLanguage], url='https://github.com/login/oauth/authorize?client_id=ba5e2296f2bbe59f5097'))

    return markup

#: Markup for non subscribed users
def notSubscribedMarkup(userLanguage):
    return telebot.types.InlineKeyboardMarkup(
        [
            [
                telebot.types.InlineKeyboardButton(
                    text=language['subscribeChannelBtn'][userLanguage],
                    url='https://www.youtube.com/h9youtube?sub_confirmation=1',
                ),
                telebot.types.InlineKeyboardButton(
                    text=language['joinChannelBtn'][userLanguage],
                    url='https://t.me/h9youtube',
                ),
            ]
        ]
    )

#: Reply keyboard for cancel button
def cancelReplyKeyboard(userLanguage):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(telebot.types.KeyboardButton(text=language['cancelBtn'][userLanguage]))

    return keyboard