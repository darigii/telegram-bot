import telebot

bot = telebot.TeleBot('7636108576:AAGkqpU-8A_Rq7JguRPDI0GlhQwSOJIOpAg')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'<b>Привет,  {message.from_user.first_name} {message.from_user.last_name}! </b>!  Мы рады видеть тебя здесь!✨ \nВ нашем боте ты найдешь самые стильные и качественные товары прямо из <b>Кореи</b>: от косметики и моды до уникальных аксессуаров и вкусняшек.🇰🇷', parse_mode='html')
bot.polling(non_stop=True)