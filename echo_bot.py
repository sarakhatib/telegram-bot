import requests
import telebot
from telebot import types
import qrcode
import cv2
import os
from dotenv import load_dotenv

load_dotenv()

token = os.environ["TELEGRAM_BOT_TOKEN"]

bot = telebot.TeleBot(token,
                      parse_mode=None)  # You can set parse_mode by default. HTML or MARKDOWN
bot.delete_webhook()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    name = message.from_user.first_name
    reply = "Hello " + name + ", I hope you're doing well today \U0001F603"
    bot.send_message(message.chat.id, reply)
    process(message)


def process(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Generate", callback_data="0"),
               types.InlineKeyboardButton("Scan", callback_data="1"))
    bot.send_message(message.chat.id, "Would you like to generate a QR Code or scan a QR Code?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, inline_message_id=None)
    if call.data == '0':
        sent = bot.send_message(call.message.chat.id, "Please send me a link")
        bot.register_next_step_handler(sent, generate_qr_code)
    else:
        sent = bot.send_message(call.message.chat.id, "Please send me a picture")
        bot.register_next_step_handler(sent, read_qr_code)


def generate_qr_code(message):
    img = qrcode.make(message.text)
    img.save('out.jpg')
    bot.send_chat_action(message.chat.id, 'upload_photo')
    img = open('out.jpg', 'rb')
    bot.send_photo(message.chat.id, img)
    img.close()
    os.remove('out.jpg')


def read_qr_code(message):
    fileID = message.photo[-1].file_id
    file = bot.get_file(fileID)
    d = cv2.QRCodeDetector()
    img = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(token, file.file_path))
    with open('photo.jpg', 'wb') as f:
        f.write(img.content)
    val, points, straight_qrcode = d.detectAndDecode(cv2.imread('photo.jpg'))
    f.close()
    os.remove('photo.jpg')
    bot.send_message(message.chat.id, val)


# @bot.message_handler(commands=['help'])
# def send_instructions(message):
#     bot.send_message(message.chat.id, "Please follow these instructions to get help:")
#
#
# @bot.message_handler(regexp="it's soso")
# def special_welcome(message):
#     bot.reply_to(message, "Oh it's you \U0001F602")
#

bot.infinity_polling()
