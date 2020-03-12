import convertapi
import os
import telebot
import tempfile
import requests
from io import BytesIO

token = os.environ['TELEGRAM_TOKEN']
convertapi.api_secret = os.environ['CONVERTAPI_SECRET']

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Please send me your files')

@bot.message_handler(content_types=['document', 'audio', 'photo', 'video'])
def convert_to_pdf(message):
    #print(message)
    bot.send_message(message.chat.id, 'Converting...')
    send_photo_warning = False
    content_type = message.content_type

    documents = getattr(message, content_type)
    if not isinstance(documents, list):
        documents = [documents]

    for doc in documents:
        file_id = doc.file_id
        file_info = bot.get_file(file_id)
        #print(file_info)
        file_url = 'https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path)

        file_data = BytesIO(requests.get(file_url).content)
        try:
            file_name = doc.file_name
        except:
            file_name = file_info.file_path.replace("/", "_")
            send_photo_warning = True
        upload_io = convertapi.UploadIO(file_data, filename=file_name)
        converted_result = convertapi.convert('pdf', {'File': upload_io})
        converted_files = converted_result.save_files(tempfile.gettempdir())

        for file in converted_files:
            bot.send_document(message.chat.id, open(file, 'rb'))

    if send_photo_warning:
        bot.send_message(message.chat.id, 'You sent this file as a photo. If you require better quality, please send it as a document.')

bot.polling()
