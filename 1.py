from telethon import TelegramClient, events, functions, types, utils
import asyncio
import pytz
from datetime import datetime, timedelta
import logging
import random
import os
import sys
import re
import json
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap
from io import BytesIO
import requests
from gtts import gTTS
import jdatetime
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for cross-platform colored terminal output
colorama.init(autoreset=True)

# ASCII Art Logo
LOGO = f"""
{Fore.CYAN}╔════════════════════════════════════════════╗
{Fore.CYAN}║ {Fore.BLUE}████████╗███████╗██╗     ███████╗██████╗  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}╚══██╔══╝██╔════╝██║     ██╔════╝██╔══██╗ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}   ██║   █████╗  ██║     █████╗  ██████╔╝ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}   ██║   ██╔══╝  ██║     ██╔══╝  ██╔══██╗ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}   ██║   ███████╗███████╗███████╗██████╔╝ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.BLUE}   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═════╝  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}███████╗███████╗██╗     ███████╗██████╗  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}██╔════╝██╔════╝██║     ██╔════╝██╔══██╗ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}███████╗█████╗  ██║     █████╗  ██████╔╝ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}╚════██║██╔══╝  ██║     ██╔══╝  ██╔══██╗ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}███████║███████╗███████╗███████╗██████╔╝ {Fore.CYAN}║
{Fore.CYAN}║ {Fore.MAGENTA}╚══════╝╚══════╝╚══════╝╚══════╝╚═════╝  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██████╗  ██████╗ ████████╗               {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██╔══██╗██╔═══██╗╚══██╔══╝               {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██████╔╝██║   ██║   ██║                  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██╔══██╗██║   ██║   ██║                  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}██████╔╝╚██████╔╝   ██║                  {Fore.CYAN}║
{Fore.CYAN}║ {Fore.YELLOW}╚═════╝  ╚═════╝    ╚═╝                  {Fore.CYAN}║
{Fore.CYAN}╚════════════════════════════════════════════╝
{Fore.GREEN}        Enhanced Version 2.0 (2025)
"""

# Configuration variables
CONFIG_FILE = "config.json"
LOG_FILE = "selfbot.log"

# Default configuration settings
default_config = {
    "api_id": 29042268,
    "api_hash": "54a7b377dd4a04a58108639febe2f443",
    "session_name": "anon",
    "log_level": "ERROR",
    "timezone": "Asia/Tehran",
    "auto_backup": True,
    "backup_interval": 60,  # minutes
    "enemy_reply_chance": 100,  # percentage
    "enemy_auto_reply": True,
    "auto_read_messages": False,
    "allowed_users": []
}

# Global variables
enemies = set()
current_font = 'normal'
actions = {
    'typing': False,
    'online': False,
    'reaction': False,
    'read': False,
    'auto_reply': False
}
spam_words = []
saved_messages = []
reminders = []
time_enabled = True
saved_pics = []
custom_replies = {}
blocked_words = []
last_backup_time = None
running = True
start_time = time.time()

# Command history for undo functionality
command_history = []
MAX_HISTORY = 50

locked_chats = {
    'screenshot': set(),  # Screenshot protection
    'forward': set(),     # Forward protection
    'copy': set(),        # Copy protection
    'delete': set(),      # Auto-delete messages
    'edit': set()         # Prevent editing
}

# Font styles expanded
font_styles = {
    'normal': lambda text: text,
    'bold': lambda text: f"**{text}**",
    'italic': lambda text: f"__{text}__",
    'script': lambda text: f"`{text}`",
    'double': lambda text: f"```{text}```",
    'bubble': lambda text: f"||{text}||",
    'square': lambda text: f"```{text}```",
    'strikethrough': lambda text: f"~~{text}~~",
    'underline': lambda text: f"___{text}___",
    'caps': lambda text: text.upper(),
    'lowercase': lambda text: text.lower(),
    'title': lambda text: text.title(),
    'space': lambda text: " ".join(text),
    'reverse': lambda text: text[::-1]
}

# Insults list - unchanged for compatibility
insults = [
    "کیرم تو کص ننت", "مادرجنده", "کص ننت", "کونی", "جنده", "کیری", "بی ناموس", "حرومزاده", "مادر قحبه", "جاکش",
    "کص ننه", "ننه جنده", "مادر کصده", "خارکصه", "کون گشاد", "ننه کیردزد", "مادر به خطا", "توله سگ", "پدر سگ", "حروم لقمه",
    "ننه الکسیس", "کص ننت میجوشه", "کیرم تو کص مادرت", "مادر جنده ی حرومی", "زنا زاده", "مادر خراب", "کصکش", "ننه سگ پرست",
    "مادرتو گاییدم", "خواهرتو گاییدم", "کیر سگ تو کص ننت", "کص مادرت", "کیر خر تو کص ننت", "کص خواهرت", "کون گشاد",
    "سیکتیر کص ننه", "ننه کیر خور", "خارکصده", "مادر جنده", "ننه خیابونی", "کیرم تو دهنت", "کص لیس", "ساک زن",
    "کیرم تو قبر ننت", "بی غیرت", "کص ننه پولی", "کیرم تو کص زنده و مردت", "مادر به خطا", "لاشی", "عوضی", "آشغال",
    "ننه کص طلا", "کیرم تو کص ننت بالا پایین", "کیر قاطر تو کص ننت", "کص ننت خونه خالی", "کیرم تو کص ننت یه دور", 
    "مادر خراب گشاد", "کیرم تو نسل اولت", "کیرم تو کص ننت محکم", "کیر خر تو کص مادرت", "کیرم تو روح مادر جندت",
    "کص ننت سفید برفی", "کیرم تو کص خارت", "کیر سگ تو کص مادرت", "کص ننه کیر خور", "کیرم تو کص زیر خواب",
    "مادر جنده ولگرد", "کیرم تو دهن مادرت", "کص مادرت گشاد", "کیرم تو لای پای مادرت", "کص ننت خیس",
    "کیرم تو کص مادرت بگردش", "کص ننه پاره", "مادر جنده حرفه ای", "کیرم تو کص و کون ننت", "کص ننه تنگ",
    "کیرم تو حلق مادرت", "ننه جنده مفت خور", "کیرم از پهنا تو کص ننت", "کص مادرت بد بو", "کیرم تو همه کس و کارت",
    "مادر کصده سیاه", "کیرم تو کص گشاد مادرت", "کص ننه ساک زن", "کیرم تو کص خاندانت", "مادر جنده خیابونی",
    "کیرم تو کص ننت یه عمر", "ننه جنده کص خور", "کیرم تو نسل و نژادت", "کص مادرت پاره", "کیرم تو شرف مادرت",
    "مادر جنده فراری", "کیرم تو روح مادرت", "کص ننه جندت", "کیرم تو غیرتت", "کص مادر بدکاره",
    "کیرم تو ننه جندت", "مادر کصده لاشی", "کیرم تو وجود مادرت", "کص ننه بی آبرو", "کیرم تو شعور ننت"
]

# Setup logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_FILE
)
logger = logging.getLogger("TelegramSelfBot")

# Convert numbers to superscript
def to_superscript(num):
    superscripts = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
    }
    return ''.join(superscripts.get(n, n) for n in str(num))

# Pretty print functions
def print_header(text):
    """Print a header with decoration"""
    width = len(text) + 4
    print(f"\n{Fore.CYAN}{'═' * width}")
    print(f"{Fore.CYAN}║ {Fore.WHITE}{text} {Fore.CYAN}║")
    print(f"{Fore.CYAN}{'═' * width}\n")

def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠️ {text}")

def print_info(text):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ️ {text}")

def print_status(label, status, active=True):
    """Print a status item with colored indicator"""
    status_color = Fore.GREEN if active else Fore.RED
    status_icon = "✅" if active else "❌"
    print(f"{Fore.WHITE}{label}: {status_color}{status_icon} {status}")

def print_loading(text="Loading", cycles=3):
    """Display a loading animation"""
    animations = [".  ", ".. ", "..."]
    for _ in range(cycles):
        for animation in animations:
            sys.stdout.write(f"\r{Fore.YELLOW}{text} {animation}")
            sys.stdout.flush()
            time.sleep(0.3)
    sys.stdout.write("\r" + " " * (len(text) + 5) + "\r")
    sys.stdout.flush()

def print_progress_bar(iteration, total, prefix='', suffix='', length=30, fill='█'):
    """Call in a loop to create terminal progress bar"""
    percent = "{0:.1f}".format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '░' * (length - filled_length)
    sys.stdout.write(f'\r{Fore.BLUE}{prefix} |{Fore.CYAN}{bar}{Fore.BLUE}| {percent}% {suffix}')
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

# Config management functions
def load_config():
    """Load configuration from file or create default"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Update with any missing keys from default config
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print_error(f"Failed to load config: {e}")
            return default_config
    else:
        save_config(default_config)
        return default_config

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print_error(f"Failed to save config: {e}")
        return False

# Data backup functions
def backup_data():
    """Backup all user data to file"""
    global last_backup_time
    backup_data = {
        "enemies": list(enemies),
        "current_font": current_font,
        "actions": actions,
        "spam_words": spam_words,
        "saved_messages": saved_messages,
        "reminders": reminders,
        "time_enabled": time_enabled,
        "saved_pics": saved_pics,
        "custom_replies": custom_replies,
        "blocked_words": blocked_words,
        "locked_chats": {k: list(v) for k, v in locked_chats.items()}
    }
    
    try:
        with open("selfbot_backup.json", 'w') as f:
            json.dump(backup_data, f, indent=4)
        last_backup_time = datetime.now()
        return True
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

def restore_data():
    """Restore user data from backup file"""
    global enemies, current_font, actions, spam_words, saved_messages, reminders
    global time_enabled, saved_pics, custom_replies, blocked_words, locked_chats
    
    if not os.path.exists("selfbot_backup.json"):
        return False
    
    try:
        with open("selfbot_backup.json", 'r') as f:
            data = json.load(f)
            
        enemies = set(data.get("enemies", []))
        current_font = data.get("current_font", "normal")
        actions.update(data.get("actions", {}))
        spam_words = data.get("spam_words", [])
        saved_messages = data.get("saved_messages", [])
        reminders = data.get("reminders", [])
        time_enabled = data.get("time_enabled", True)
        saved_pics = data.get("saved_pics", [])
        custom_replies = data.get("custom_replies", {})
        blocked_words = data.get("blocked_words", [])
        
        # Restore locked_chats as sets
        locked_chats_data = data.get("locked_chats", {})
        for key, value in locked_chats_data.items():
            if key in locked_chats:
                locked_chats[key] = set(value)
                
        return True
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return False

# Enhanced utility functions
async def text_to_voice(text, lang='fa'):
    """Convert text to voice file with progress indicators"""
    print_info("Converting text to voice...")
    try:
        tts = gTTS(text=text, lang=lang)
        filename = "voice.mp3"
        tts.save(filename)
        print_success("Voice file created successfully")
        return filename
    except Exception as e:
        logger.error(f"Error in text to voice: {e}")
        print_error(f"Failed to convert text to voice: {e}")
        return None

async def text_to_image(text, bg_color='white', text_color='black'):
    """Convert text to image with enhanced customization"""
    print_info("Creating image from text...")
    try:
        width = 800
        height = max(400, len(text) // 20 * 50)  # Dynamic height based on text length
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        font_size = 40
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            # Fallback to default
            font = ImageFont.load_default()
        
        lines = textwrap.wrap(text, width=30)
        y = 50
        for i, line in enumerate(lines):
            print_progress_bar(i + 1, len(lines), 'Progress:', 'Complete', 20)
            draw.text((50, y), line, font=font, fill=text_color)
            y += font_size + 10
            
        filename = "text.png"
        img.save(filename)
        print_success("Image created successfully")
        return filename
    except Exception as e:
        logger.error(f"Error in text to image: {e}")
        print_error(f"Failed to convert text to image: {e}")
        return None

async def text_to_gif(text, duration=500, bg_color='white'):
    """Convert text to animated GIF with customization"""
    print_info("Creating GIF from text...")
    try:
        width = 800
        height = 400
        frames = []
        colors = ['red', 'blue', 'green', 'purple', 'orange']
        
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
        
        for i, color in enumerate(colors):
            print_progress_bar(i + 1, len(colors), 'Creating frames:', 'Complete', 20)
            img = Image.new('RGB', (width, height), color=bg_color)
            draw = ImageDraw.Draw(img)
            draw.text((50, 150), text, font=font, fill=color)
            frames.append(img)
        
        filename = "text.gif"
        frames[0].save(
            filename,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0
        )
        print_success("GIF created successfully")
        return filename
    except Exception as e:
        logger.error(f"Error in text to gif: {e}")
        print_error(f"Failed to convert text to GIF: {e}")
        return None

async def update_time(client):
    """Update the last name with current time"""
    while running:
        try:
            if time_enabled:
                config = load_config()
                now = datetime.now(pytz.timezone(config['timezone']))
                hours = to_superscript(now.strftime('%H'))
                minutes = to_superscript(now.strftime('%M'))
                time_string = f"{hours}:{minutes}"
                await client(functions.account.UpdateProfileRequest(last_name=time_string))
        except Exception as e:
            logger.error(f'Error updating time: {e}')
        await asyncio.sleep(60)

async def auto_online(client):
    """Keep user online automatically"""
    while running and actions['online']:
        try:
            await client(functions.account.UpdateStatusRequest(offline=False))
        except Exception as e:
            logger.error(f'Error updating online status: {e}')
        await asyncio.sleep(30)

async def auto_typing(client, chat):
    """Maintain typing status in chat"""
    while running and actions['typing']:
        try:
            async with client.action(chat, 'typing'):
                await asyncio.sleep(3)
        except Exception as e:
            logger.error(f'Error in typing action: {e}')
            break

async def auto_reaction(event):
    """Add automatic reaction to messages"""
    if actions['reaction']:
        try:
            await event.message.react('👍')
        except Exception as e:
            logger.error(f'Error adding reaction: {e}')

async def auto_read_messages(event, client):
    """Mark messages as read automatically"""
    if actions['read']:
        try:
            await client.send_read_acknowledge(event.chat_id, event.message)
        except Exception as e:
            logger.error(f'Error marking message as read: {e}')

async def schedule_message(client, chat_id, delay, message):
    """Schedule message sending with countdown"""
    print_info(f"Message scheduled to send in {delay} minutes")
    for i in range(delay):
        remaining = delay - i
        if remaining % 5 == 0 or remaining <= 5:  # Show updates every 5 minutes or in final countdown
            logger.info(f"Scheduled message will send in {remaining} minutes")
        await asyncio.sleep(60)
    
    try:
        await client.send_message(chat_id, message)
        print_success(f"Scheduled message sent: {message[:30]}...")
        return True
    except Exception as e:
        logger.error(f"Failed to send scheduled message: {e}")
        print_error(f"Failed to send scheduled message: {e}")
        return False

async def spam_messages(client, chat_id, count, message):
    """Send multiple messages in sequence with progress indicators"""
    print_info(f"Sending {count} messages...")
    success_count = 0
    
    for i in range(count):
        try:
            await client.send_message(chat_id, message)
            success_count += 1
            print_progress_bar(i + 1, count, 'Sending:', 'Complete', 20)
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Error in spam message {i+1}: {e}")
    
    print_success(f"Successfully sent {success_count}/{count} messages")
    return success_count

async def check_reminders(client):
    """Check and send reminders"""
    while running:
        current_time = datetime.now().strftime('%H:%M')
        to_remove = []
        
        for i, (reminder_time, message, chat_id) in enumerate(reminders):
            if reminder_time == current_time:
                try:
                    await client.send_message(chat_id, f"🔔 یادآوری: {message}")
                    to_remove.append(i)
                except Exception as e:
                    logger.error(f"Failed to send reminder: {e}")
        
        # Remove sent reminders
        for i in sorted(to_remove, reverse=True):
            del reminders[i]
            
        await asyncio.sleep(30)  # Check every 30 seconds

async def auto_backup(client):
    """Automatically backup data at intervals"""
    config = load_config()
    if not config['auto_backup']:
        return
        
    interval = config['backup_interval'] * 60  # Convert to seconds
    
    while running:
        await asyncio.sleep(interval)
        if backup_data():
            logger.info("Auto-backup completed successfully")
        else:
            logger.error("Auto-backup failed")

async def handle_anti_delete(event):
    """Save deleted messages for anti-delete feature"""
    chat_id = str(event.chat_id)
    if chat_id in locked_chats['delete'] and event.message:
        try:
            # Save message info before it's deleted
            msg = event.message
            sender = await event.get_sender()
            sender_name = utils.get_display_name(sender) if sender else "Unknown"
            
            saved_text = f"🔴 Deleted message from {sender_name}:\n{msg.text}"
            await event.reply(saved_text)
            return True
        except Exception as e:
            logger.error(f"Error in anti-delete: {e}")
    return False

async def show_help_menu(client, event):
    """Show enhanced help menu with categories"""
    help_text = f"""
{Fore.CYAN}📱 راهنمای ربات سلف بات نسخه 2.0:

{Fore.YELLOW}⚙️ تنظیمات دشمن:
• {Fore.WHITE}تنظیم دشمن (ریپلای) - اضافه کردن به لیست دشمن
• {Fore.WHITE}حذف دشمن (ریپلای) - حذف از لیست دشمن  
• {Fore.WHITE}لیست دشمن - نمایش لیست دشمنان
• {Fore.WHITE}insult [on/off] - فعال/غیرفعال کردن پاسخ خودکار به دشمن

{Fore.YELLOW}🔤 فونت ها:
• {Fore.WHITE}bold on/off - فونت ضخیم
• {Fore.WHITE}italic on/off - فونت کج
• {Fore.WHITE}script on/off - فونت دست‌نویس 
• {Fore.WHITE}double on/off - فونت دوتایی
• {Fore.WHITE}bubble on/off - فونت حبابی
• {Fore.WHITE}square on/off - فونت مربعی
• {Fore.WHITE}strikethrough on/off - فونت خط خورده
• {Fore.WHITE}underline on/off - فونت زیر خط دار
• {Fore.WHITE}caps on/off - فونت بزرگ
• {Fore.WHITE}lowercase on/off - فونت کوچک
• {Fore.WHITE}title on/off - فونت عنوان
• {Fore.WHITE}space on/off - فونت فاصله‌دار
• {Fore.WHITE}reverse on/off - فونت معکوس

{Fore.YELLOW}⚡️ اکشن های خودکار:
• {Fore.WHITE}typing on/off - تایپینگ دائم
• {Fore.WHITE}online on/off - آنلاین دائم 
• {Fore.WHITE}reaction on/off - ری‌اکشن خودکار
• {Fore.WHITE}time on/off - نمایش ساعت در نام
• {Fore.WHITE}read on/off - خواندن خودکار پیام‌ها
• {Fore.WHITE}reply on/off - پاسخ خودکار به پیام‌ها

{Fore.YELLOW}🔒 قفل‌ها:
• {Fore.WHITE}screenshot on/off - قفل اسکرین‌شات
• {Fore.WHITE}forward on/off - قفل فوروارد
• {Fore.WHITE}copy on/off - قفل کپی
• {Fore.WHITE}delete on/off - ضد حذف پیام
• {Fore.WHITE}edit on/off - ضد ویرایش پیام

{Fore.YELLOW}🎨 تبدیل‌ها:
• {Fore.WHITE}متن به ویس بگو [متن] - تبدیل متن به ویس
• {Fore.WHITE}متن به عکس [متن] - تبدیل متن به عکس
• {Fore.WHITE}متن به گیف [متن] - تبدیل متن به گیف
• {Fore.WHITE}save pic - ذخیره عکس (ریپلای)
• {Fore.WHITE}show pics - نمایش عکس‌های ذخیره شده

{Fore.YELLOW}📝 قابلیت های دیگر:
• {Fore.WHITE}schedule [زمان] [پیام] - ارسال پیام زماندار
• {Fore.WHITE}spam [تعداد] [پیام] - اسپم پیام
• {Fore.WHITE}save - ذخیره پیام (ریپلای)
• {Fore.WHITE}saved - نمایش پیام های ذخیره شده
• {Fore.WHITE}remind [زمان] [پیام] - تنظیم یادآور
• {Fore.WHITE}search [متن] - جستجو در پیام ها
• {Fore.WHITE}block word [کلمه] - مسدود کردن کلمه
• {Fore.WHITE}unblock word [کلمه] - رفع مسدودیت کلمه
• {Fore.WHITE}block list - نمایش لیست کلمات مسدود شده
• {Fore.WHITE}auto reply [trigger] [response] - تنظیم پاسخ خودکار
• {Fore.WHITE}delete reply [trigger] - حذف پاسخ خودکار
• {Fore.WHITE}replies - نمایش لیست پاسخ‌های خودکار
• {Fore.WHITE}backup - ذخیره پشتیبان از داده‌ها
• {Fore.WHITE}restore - بازیابی داده‌ها از پشتیبان
• {Fore.WHITE}undo - برگرداندن آخرین عملیات
• {Fore.WHITE}وضعیت - نمایش وضعیت ربات
• {Fore.WHITE}exit - خروج از برنامه
"""
    try:
        await event.edit(help_text.replace(Fore.CYAN, "").replace(Fore.YELLOW, "").replace(Fore.WHITE, ""))
    except:
        print(help_text)

async def show_status(client, event):
    """Show enhanced bot status with detailed information"""
    try:
        # Measure ping
        start_time = time.time()
        await client(functions.PingRequest(ping_id=0))
        end_time = time.time()
        ping = round((end_time - start_time) * 1000, 2)

        # Get time information
        config = load_config()
        tz = pytz.timezone(config['timezone'])
        now = datetime.now(tz)
        
        # Jalali date for Iran
        j_date = jdatetime.datetime.fromgregorian(datetime=now)
        jalali_date = j_date.strftime('%Y/%m/%d')
        local_time = now.strftime('%H:%M:%S')

        # Calculate uptime
        uptime_seconds = int(time.time() - start_time)
        uptime = str(timedelta(seconds=uptime_seconds))

        # Memory usage
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory_usage = f"{process.memory_info().rss / 1024 / 1024:.2f} MB"
        except ImportError:
            memory_usage = "N/A"

        status_text = f"""
⚡️ وضعیت ربات سلف بات

📊 اطلاعات سیستم:
• پینگ: {ping} ms
• زمان کارکرد: {uptime}
• مصرف حافظه: {memory_usage}
• آخرین پشتیبان‌گیری: {last_backup_time.strftime('%Y/%m/%d %H:%M') if last_backup_time else 'هیچوقت'}

📅 اطلاعات زمانی:
• تاریخ شمسی: {jalali_date}
• ساعت: {local_time}
• منطقه زمانی: {config['timezone']}

💡 وضعیت قابلیت‌ها:
• تایپینگ: {'✅' if actions['typing'] else '❌'}
• آنلاین: {'✅' if actions['online'] else '❌'} 
• ری‌اکشن: {'✅' if actions['reaction'] else '❌'}
• ساعت: {'✅' if time_enabled else '❌'}
• خواندن خودکار: {'✅' if actions['read'] else '❌'}
• پاسخ خودکار: {'✅' if actions['auto_reply'] else '❌'}

📌 آمار:
• تعداد دشمنان: {len(enemies)}
• پیام‌های ذخیره شده: {len(saved_messages)}
• یادآوری‌ها: {len(reminders)}
• کلمات مسدود شده: {len(blocked_words)}
• پاسخ‌های خودکار: {len(custom_replies)}

🔒 قفل‌های فعال:
• اسکرین‌شات: {len(locked_chats['screenshot'])}
• فوروارد: {len(locked_chats['forward'])}
• کپی: {len(locked_chats['copy'])}
• ضد حذف: {len(locked_chats['delete'])}
• ضد ویرایش: {len(locked_chats['edit'])}
"""
        await event.edit(status_text)
    except Exception as e:
        logger.error(f"Error in status handler: {e}")
        print_error(f"Error showing status: {e}")

async def main():
    """Main function with enhanced UI and error handling"""
    # Print logo and initialize
    print(LOGO)
    print_header("Initializing Telegram Self-Bot")
    
    # Load configuration
    config = load_config()
    print_info(f"Configuration loaded from {CONFIG_FILE}")
    
    # Setup logging
    log_level = getattr(logging, config['log_level'])
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=LOG_FILE)
    
    # Restore data if available
    if os.path.exists("selfbot_backup.json"):
        if restore_data():
            print_success("Data restored from backup")
        else:
            print_warning("Failed to restore data from backup")
    
    # Initialize client with animated progress
    print_loading("Connecting to Telegram")
    client = TelegramClient(config['session_name'], config['api_id'], config['api_hash'])
    
    try:
        # Connect to Telegram
        await client.connect()
        print_success("Connected to Telegram")
        
        # Check authorization
        if not await client.is_user_authorized():
            print_header("Authentication Required")
            print("Please enter your phone number (e.g., +989123456789):")
            phone = input(f"{Fore.GREEN}> ")
            
            try:
                print_loading("Sending verification code")
                await client.send_code_request(phone)
                print_success("Verification code sent")
                
                print("\nPlease enter the verification code:")
                code = input(f"{Fore.GREEN}> ")
                
                print_loading("Verifying code")
                await client.sign_in(phone, code)
                print_success("Verification successful")
                
            except Exception as e:
                if "two-steps verification" in str(e).lower():
                    print_warning("Two-step verification is enabled")
                    print("Please enter your password:")
                    password = input(f"{Fore.GREEN}> ")
                    
                    print_loading("Verifying password")
                    await client.sign_in(password=password)
                    print_success("Password verification successful")
                else:
                    print_error(f"Login error: {str(e)}")
                    return
        
        # Successfully logged in
        me = await client.get_me()
        print_success(f"Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or 'No username'})")
        print_info("Self-bot is now active! Type 'پنل' in any chat to see commands.")
        
        # Start background tasks
        asyncio.create_task(update_time(client))
        asyncio.create_task(check_reminders(client))
        asyncio.create_task(auto_backup(client))
        
        # Event handlers
        @client.on(events.NewMessage(pattern=r'^time (on|off)$'))
        async def time_handler(event):
            global time_enabled
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                status = event.pattern_match.group(1)
                time_enabled = (status == 'on')
                if not time_enabled:
                    await client(functions.account.UpdateProfileRequest(last_name=''))
                
                # Add to command history
                command_history.append(('time', not time_enabled))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                    
                await event.edit(f"✅ نمایش ساعت {'فعال' if time_enabled else 'غیرفعال'} شد")
            except Exception as e:
                logger.error(f"Error in time handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern=r'^insult (on|off)$'))
        async def insult_toggle_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                status = event.pattern_match.group(1)
                config = load_config()
                config['enemy_auto_reply'] = (status == 'on')
                save_config(config)
                
                await event.edit(f"✅ پاسخ خودکار به دشمن {'فعال' if config['enemy_auto_reply'] else 'غیرفعال'} شد")
            except Exception as e:
                logger.error(f"Error in insult toggle handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^متن به ویس بگو (.+)$'))
        async def voice_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                text = event.pattern_match.group(1)
                await event.edit("⏳ در حال تبدیل متن به ویس...")
                
                voice_file = await text_to_voice(text)
                if voice_file:
                    await event.delete()
                    await client.send_file(event.chat_id, voice_file)
                    os.remove(voice_file)
                else:
                    await event.edit("❌ خطا در تبدیل متن به ویس")
            except Exception as e:
                logger.error(f"Error in voice handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^save pic$'))
        async def save_pic_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                if not event.is_reply:
                    await event.edit("❌ لطفا روی یک عکس ریپلای کنید")
                    return
                    
                replied = await event.get_reply_message()
                if not replied.photo:
                    await event.edit("❌ پیام ریپلای شده عکس نیست")
                    return
                    
                await event.edit("⏳ در حال ذخیره عکس...")
                path = await client.download_media(replied.photo)
                saved_pics.append(path)
                
                # Add to command history
                command_history.append(('save_pic', path))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                
                # Backup after significant change
                backup_data()
                
                await event.edit("✅ عکس ذخیره شد")
            except Exception as e:
                logger.error(f"Error in save pic handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^show pics$'))
        async def show_pics_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                if not saved_pics:
                    await event.edit("❌ هیچ عکسی ذخیره نشده است")
                    return
                
                await event.edit(f"⏳ در حال بارگذاری {len(saved_pics)} عکس...")
                
                # Send saved pictures one by one
                for i, pic_path in enumerate(saved_pics):
                    if os.path.exists(pic_path):
                        await client.send_file(event.chat_id, pic_path, caption=f"عکس {i+1}/{len(saved_pics)}")
                    else:
                        await client.send_message(event.chat_id, f"❌ عکس {i+1} یافت نشد")
                
                await event.edit(f"✅ {len(saved_pics)} عکس نمایش داده شد")
            except Exception as e:
                logger.error(f"Error in show pics handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^متن به عکس (.+)$'))
        async def img_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                text = event.pattern_match.group(1)
                await event.edit("⏳ در حال تبدیل متن به عکس...")
                
                img_file = await text_to_image(text)
                if img_file:
                    await event.delete()
                    await client.send_file(event.chat_id, img_file)
                    os.remove(img_file)
                else:
                    await event.edit("❌ خطا در تبدیل متن به عکس")
            except Exception as e:
                logger.error(f"Error in image handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='^متن به گیف (.+)$'))
        async def gif_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                text = event.pattern_match.group(1)
                await event.edit("⏳ در حال تبدیل متن به گیف...")
                
                gif_file = await text_to_gif(text)
                if gif_file:
                    await event.delete()
                    await client.send_file(event.chat_id, gif_file)
                    os.remove(gif_file)
                else:
                    await event.edit("❌ خطا در تبدیل متن به گیف")
            except Exception as e:
                logger.error(f"Error in gif handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern=r'^(screenshot|forward|copy|delete|edit) (on|off)$'))
        async def lock_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                command, status = event.raw_text.lower().split()
                chat_id = str(event.chat_id)
                
                # Previous state for undo
                prev_state = chat_id in locked_chats[command]
                
                if status == 'on':
                    locked_chats[command].add(chat_id)
                    await event.edit(f"✅ قفل {command} فعال شد")
                else:
                    locked_chats[command].discard(chat_id)
                    await event.edit(f"✅ قفل {command} غیرفعال شد")
                
                # Add to command history
                command_history.append(('lock', (command, chat_id, prev_state)))
                if len(command_history) > MAX_HISTORY:
                    command_history.pop(0)
                    
                # Backup after significant change
                backup_data()
                    
            except Exception as e:
                logger.error(f"Error in lock handler: {e}")
                await event.edit(f"❌ خطا: {str(e)}")

        @client.on(events.NewMessage(pattern='پنل'))
        async def panel_handler(event):
            try:
                if not event.from_id:
                    return
                    
                if event.from_id.user_id == (await client.get_me()).id:
                    await show_help_menu(client, event)
            except Exception as e:
                logger.error(f"Error in panel handler: {e}")
                pass

        @client.on(events.NewMessage(pattern='undo'))
        async def undo_handler(event):
            try:
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    return
                    
                if not command_history:
                    await event.edit("❌ تاریخچه دستورات خالی است")
                    return
                
                last_command = command_history.pop()
                command_type, data = last_command
                
                if command_type == 'time':
                    global time_enabled
                    time_enabled = data
                    if not time_enabled:
                        await client(functions.account.UpdateProfileRequest(last_name=''))
                    await event.edit(f"✅ وضعیت نمایش ساعت به {'فعال' if time_enabled else 'غیرفعال'} برگردانده شد")
                
                elif command_type == 'lock':
                    lock_type, chat_id, prev_state = data
                    if prev_state:
                        locked_chats[lock_type].add(chat_id)
                    else:
                        locked_chats[lock_type].discard(chat_id)
                    await event.edit(f"✅ وضعیت قفل {lock_type} به {'فعال' if prev_state else 'غیرفعال'} برگردانده شد")
                
                elif command_type == 'font':
                    global current_font
                    current_font = data
                    await event.edit(f"✅ فونت به {current_font} برگردانده شد")
                
                elif command_type == 'enemy_add':
                    enemies.discard(data)
                    await event.edit("✅ کاربر از لیست دشمن حذف شد")
                
                elif command_type == 'enemy_remove':
                    enemies.add(data)
                    await event.edit("✅ کاربر به لیست دشمن اضافه شد")
                
                elif command_type == 'action':
                    action_type, prev_state = data
                    actions[action_type] = prev_state
                    await event.edit(f"✅ وضعیت {action_type} به {'فعال' if prev_state else 'غیرفعال'} برگردانده شد")
                
                elif command_type == 'save_msg':
                    saved_messages.pop()
                    await event.edit("✅ آخرین پیام ذخیره شده حذف شد")
                
                elif command_type == 'save_pic':
                    path = data
                    if path in saved_pics:
                        saved_pics.remove(path)
                    if os.path.exists(path):
                        os.remove(path)
                    await event.edit("✅ آخرین عکس ذخیره شده حذف شد")
                
                elif command_type == 'block_word':
                    blocked_words.remove(data)
                    await event.edit(f"✅ کلمه '{data}' از لیست کلمات مسدود شده حذف شد")
                
                elif command_type == 'unblock_word':
                    blocked_words.append(data)
                    await event.edit(f"✅ کلمه '{data}' به لیست کلمات مسدود شده اضافه شد")
                
                elif command_type == 'add_reply':
                    trigger = data
                    if trigger in custom_replies:
                        del custom_replies[trigger]
                    await event.edit(f"✅ پاسخ خودکار برای '{trigger}' حذف شد")
                
                elif command_type == 'del_reply':
                    trigger, response = data
                    custom_replies[trigger] = response
                    await event.edit(f"✅ پاسخ خودکار برای '{trigger}' بازگردانده شد")
                
                # Backup after undo
                backup_data()
                
            except Exception as e:
                logger.error(f"Error in undo handler: {e}")
                await event.edit(f"❌ خطا در برگرداندن عملیات: {str(e)}")

        @client.on(events.NewMessage)
        async def enemy_handler(event):
            try:
                if not event.from_id:
                    return
                
                config = load_config()
                if event.from_id.user_id == (await client.get_me()).id:
                    if event.raw_text == 'تنظیم دشمن' and event.is_reply:
                        # Fix for enemy reply bug
                        replied = await event.get_reply_message()
                        if replied and replied.from_id and hasattr(replied.from_id, 'user_id'):
                            user_id = str(replied.from_id.user_id)
                            # Previous state for undo
                            prev_state = user_id in enemies
                            
                            # Add to enemies set
                            enemies.add(user_id)
                            
                            # Add to command history
                            command_history.append(('enemy_add', user_id))
                            if len(command_history) > MAX_HISTORY:
                                command_history.pop(0)
                                
                            # Backup after significant change
                            backup_data()
                            
                            await event.reply('✅ کاربر به لیست دشمن اضافه شد')
                        else:
                            await event.reply('❌ نمی‌توان این کاربر را به لیست دشمن اضافه کرد')

                    elif event.raw_text == 'حذف دشمن' and event.is_reply:
                        replied = await event.get_reply_message()
                        if replied and replied.from_id and hasattr(replied.from_id, 'user_id'):
                            user_id = str(replied.from_id.user_id)
                            # Previous state for undo
                            prev_state = user_id in enemies
                            
                            # Remove from enemies set
                            enemies.discard(user_id)
                            
                            # Add to command history
                            command_history.append(('enemy_remove', user_id))
                            if len(command_history) > MAX_HISTORY:
                                command_history.pop(0)
                                
                            # Backup after significant change
                            backup_data()
                            
                            await event.reply('✅ کاربر از لیست دشمن حذف شد')
                        else:
                            await event.reply('❌ نمی‌توان این کاربر را از لیست دشمن حذف کرد')

                    elif event.raw_text == 'لیست دشمن':
                        enemy_list = ''
                        for i, enemy in enumerate(enemies, 1):
                            try:
                                user = await client.get_entity(int(enemy))
                                enemy_list += f'{i}. {user.first_name} {user.last_name or ""} (@{user.username or "بدون یوزرنیم"})\n'
                            except:
                                enemy_list += f'{i}. ID: {enemy}\n'
                        await event.reply(enemy_list or '❌ لیست دشمن خالی است')

                # Auto-reply to enemy messages
                elif config['enemy_auto_reply'] and str(event.from_id.user_id) in enemies:
                    # Fix: Only reply to enemies if auto-reply is enabled
                    insult1 = random.choice(insults)
                    insult2 = random.choice(insults)
                    while insult2 == insult1:
                        insult2 = random.choice(insults)
                    
                    # Send insults with a slight delay
                    await event.reply(insult1)
                    await asyncio.sleep(0.5)  # Increased delay for better visibility
                    await event.reply(insult2)
            except Exception as e:
                logger.error(f"Error in enemy handler: {e}")
                pass

        @client.on(events.NewMessage)
        async def font_handler(event):
            global current_font
            
            try:
                if not event.from_id or not event.raw_text:
                    return
                            
                if event.from_id.user_id != (await client.get_me()).id:
                    return

                text = event.raw_text.lower().split()
                
                # Font style settings
                if len(text) == 2 and text[1] in ['on', 'off'] and text[0] in font_styles:
                    font, status = text
                    
                    # Previous state for undo
                    prev_font = current_font
                    
                    if status == 'on':
                        current_font = font
                        await event.edit(f'✅ حالت {font} فعال شد')
                    else:
                        current_font = 'normal'
                        await event.edit(f'✅ حالت {font} غیرفعال شد')
                    
                    # Add to command history
                    command_history.append(('font', prev_font))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                
                # Apply font formatting to message
                elif current_font != 'normal' and current_font in font_styles:
                    await event.edit(font_styles[current_font](event.raw_text))
            except Exception as e:
                logger.error(f"Error in font handler: {e}")
                pass

        @client.on(events.NewMessage)
        async def check_locks(event):
            try:
                chat_id = str(event.chat_id)
                
                # Check if message forwarding is locked in this chat
                if chat_id in locked_chats['forward'] and event.forward:
                    await event.delete()
                    logger.info(f"Deleted forwarded message in chat {chat_id}")
                    
                # Check if message copying is locked in this chat
                if chat_id in locked_chats['copy'] and event.forward_from:
                    await event.delete()
                    logger.info(f"Deleted copied message in chat {chat_id}")
                    
            except Exception as e:
                logger.error(f"Error in check locks: {e}")

        @client.on(events.NewMessage)
        async def message_handler(event):
            try:
                # Auto-read messages if enabled
                if actions['read']:
                    await auto_read_messages(event, client)
                
                # Do not process further if message is not from the user
                if not event.from_id or event.from_id.user_id != (await client.get_me()).id:
                    # Check for custom replies if auto_reply is enabled
                    if actions['auto_reply'] and event.raw_text and event.raw_text in custom_replies:
                        await event.reply(custom_replies[event.raw_text])
                    return

                # Check for blocked words
                if any(word in event.raw_text.lower() for word in blocked_words):
                    await event.delete()
                    return

                # Auto actions
                if actions['typing']:
                    asyncio.create_task(auto_typing(client, event.chat_id))
                
                if actions['reaction']:
                    await auto_reaction(event)

                # Schedule message
                if event.raw_text.startswith('schedule '):
                    parts = event.raw_text.split(maxsplit=2)
                    if len(parts) == 3:
                        try:
                            delay = int(parts[1])
                            message = parts[2]
                            asyncio.create_task(schedule_message(client, event.chat_id, delay, message))
                            await event.reply(f'✅ پیام بعد از {delay} دقیقه ارسال خواهد شد')
                        except ValueError:
                            await event.reply('❌ فرمت صحیح: schedule [زمان به دقیقه] [پیام]')

                # Spam messages
                elif event.raw_text.startswith('spam '):
                    parts = event.raw_text.split(maxsplit=2)
                    if len(parts) == 3:
                        try:
                            count = int(parts[1])
                            if count > 50:  # Limit to prevent abuse
                                await event.reply('❌ حداکثر تعداد پیام برای اسپم 50 است')
                                return
                                
                            message = parts[2]
                            asyncio.create_task(spam_messages(client, event.chat_id, count, message))
                        except ValueError:
                            await event.reply('❌ فرمت صحیح: spam [تعداد] [پیام]')

                # Save message
                elif event.raw_text == 'save' and event.is_reply:
                    replied = await event.get_reply_message()
                    if replied and replied.text:
                        # Previous state for undo
                        prev_len = len(saved_messages)
                        
                        saved_messages.append(replied.text)
                        
                        # Add to command history
                        command_history.append(('save_msg', None))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                            
                        # Backup after significant change
                        backup_data()
                        
                        await event.reply('✅ پیام ذخیره شد')
                    else:
                        await event.reply('❌ پیام ریپلای شده متن ندارد')

                # Show saved messages
                elif event.raw_text == 'saved':
                    if not saved_messages:
                        await event.reply('❌ پیامی ذخیره نشده است')
                        return
                        
                    saved_text = '\n\n'.join(f'{i+1}. {msg}' for i, msg in enumerate(saved_messages))
                    
                    # Split long messages if needed
                    if len(saved_text) > 4000:
                        chunks = [saved_text[i:i+4000] for i in range(0, len(saved_text), 4000)]
                        for i, chunk in enumerate(chunks):
                            await event.reply(f"بخش {i+1}/{len(chunks)}:\n\n{chunk}")
                    else:
                        await event.reply(saved_text)

                # Set reminder
                elif event.raw_text.startswith('remind '):
                    parts = event.raw_text.split(maxsplit=2)
                    if len(parts) == 3:
                        time_str = parts[1]
                        message = parts[2]
                        
                        # Validate time format (HH:MM)
                        if re.match(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$', time_str):
                            reminders.append((time_str, message, event.chat_id))
                            
                            # Backup after significant change
                            backup_data()
                            
                            await event.reply(f'✅ یادآور برای ساعت {time_str} تنظیم شد')
                        else:
                            await event.reply('❌ فرمت زمان اشتباه است. از فرمت HH:MM استفاده کنید')
                    else:
                        await event.reply('❌ فرمت صحیح: remind [زمان] [پیام]')

                # Search in messages
                elif event.raw_text.startswith('search '):
                    query = event.raw_text.split(maxsplit=1)[1]
                    await event.edit(f"🔍 در حال جستجوی '{query}'...")
                    
                    messages = await client.get_messages(event.chat_id, search=query, limit=10)
                    if not messages:
                        await event.edit("❌ پیامی یافت نشد")
                        return
                        
                    result = f"🔍 نتایج جستجو برای '{query}':\n\n"
                    for i, msg in enumerate(messages, 1):
                        sender = await msg.get_sender()
                        sender_name = utils.get_display_name(sender) if sender else "Unknown"
                        result += f"{i}. از {sender_name}: {msg.text[:100]}{'...' if len(msg.text) > 100 else ''}\n\n"
                    
                    await event.edit(result)

                # Block word
                elif event.raw_text.startswith('block word '):
                    word = event.raw_text.split(maxsplit=2)[2].lower()
                    if word in blocked_words:
                        await event.reply(f"❌ کلمه '{word}' قبلاً مسدود شده است")
                    else:
                        # Previous state for undo
                        blocked_words.append(word)
                        
                        # Add to command history
                        command_history.append(('block_word', word))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                            
                        # Backup after significant change
                        backup_data()
                        
                        await event.reply(f"✅ کلمه '{word}' مسدود شد")

                # Unblock word
                elif event.raw_text.startswith('unblock word '):
                    word = event.raw_text.split(maxsplit=2)[2].lower()
                    if word not in blocked_words:
                        await event.reply(f"❌ کلمه '{word}' در لیست مسدود شده‌ها نیست")
                    else:
                        # Previous state for undo
                        blocked_words.remove(word)
                        
                        # Add to command history
                        command_history.append(('unblock_word', word))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                            
                        # Backup after significant change
                        backup_data()
                        
                        await event.reply(f"✅ کلمه '{word}' از لیست مسدود شده‌ها حذف شد")

                # Show blocked words
                elif event.raw_text == 'block list':
                    if not blocked_words:
                        await event.reply("❌ لیست کلمات مسدود شده خالی است")
                    else:
                        block_list = '\n'.join(f"{i+1}. {word}" for i, word in enumerate(blocked_words))
                        await event.reply(f"📋 لیست کلمات مسدود شده:\n\n{block_list}")

                # Set auto reply
                elif event.raw_text.startswith('auto reply '):
                    parts = event.raw_text.split(maxsplit=3)
                    if len(parts) == 4:
                        trigger = parts[2]
                        response = parts[3]
                        
                        # Previous state for undo
                        prev_response = custom_replies.get(trigger, None)
                        
                        custom_replies[trigger] = response
                        
                        # Add to command history
                        command_history.append(('add_reply', trigger))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                            
                        # Backup after significant change
                        backup_data()
                        
                        await event.reply(f"✅ پاسخ خودکار برای '{trigger}' تنظیم شد")
                    else:
                        await event.reply("❌ فرمت صحیح: auto reply [کلمه کلیدی] [پاسخ]")

                # Delete auto reply
                elif event.raw_text.startswith('delete reply '):
                    trigger = event.raw_text.split(maxsplit=2)[2]
                    if trigger not in custom_replies:
                        await event.reply(f"❌ هیچ پاسخ خودکاری برای '{trigger}' وجود ندارد")
                    else:
                        # Previous state for undo
                        prev_response = custom_replies[trigger]
                        
                        del custom_replies[trigger]
                        
                        # Add to command history
                        command_history.append(('del_reply', (trigger, prev_response)))
                        if len(command_history) > MAX_HISTORY:
                            command_history.pop(0)
                            
                        # Backup after significant change
                        backup_data()
                        
                        await event.reply(f"✅ پاسخ خودکار برای '{trigger}' حذف شد")

                # Show auto replies
                elif event.raw_text == 'replies':
                    if not custom_replies:
                        await event.reply("❌ هیچ پاسخ خودکاری تنظیم نشده است")
                    else:
                        reply_list = '\n\n'.join(f"🔹 {trigger}:\n{response}" for trigger, response in custom_replies.items())
                        await event.reply(f"📋 لیست پاسخ‌های خودکار:\n\n{reply_list}")

                # Backup data manually
                elif event.raw_text == 'backup':
                    if backup_data():
                        await event.reply("✅ پشتیبان‌گیری با موفقیت انجام شد")
                    else:
                        await event.reply("❌ خطا در پشتیبان‌گیری")

                # Restore data manually
                elif event.raw_text == 'restore':
                    if restore_data():
                        await event.reply("✅ بازیابی داده‌ها با موفقیت انجام شد")
                    else:
                        await event.reply("❌ فایل پشتیبان یافت نشد یا مشکلی در بازیابی وجود دارد")

                # Toggle typing status
                elif event.raw_text in ['typing on', 'typing off']:
                    # Previous state for undo
                    prev_state = actions['typing']
                    
                    actions['typing'] = event.raw_text.endswith('on')
                    
                    # Add to command history
                    command_history.append(('action', ('typing', prev_state)))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                    
                    await event.reply(f"✅ تایپینگ {'فعال' if actions['typing'] else 'غیرفعال'} شد")

                # Toggle online status
                elif event.raw_text in ['online on', 'online off']:
                    # Previous state for undo
                    prev_state = actions['online']
                    
                    actions['online'] = event.raw_text.endswith('on')
                    
                    # Add to command history
                    command_history.append(('action', ('online', prev_state)))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                    
                    if actions['online']:
                        asyncio.create_task(auto_online(client))
                    await event.reply(f"✅ آنلاین {'فعال' if actions['online'] else 'غیرفعال'} شد")

                # Toggle reaction status
                elif event.raw_text in ['reaction on', 'reaction off']:
                    # Previous state for undo
                    prev_state = actions['reaction']
                    
                    actions['reaction'] = event.raw_text.endswith('on')
                    
                    # Add to command history
                    command_history.append(('action', ('reaction', prev_state)))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                    
                    await event.reply(f"✅ ری‌اکشن {'فعال' if actions['reaction'] else 'غیرفعال'} شد")

                # Toggle read status
                elif event.raw_text in ['read on', 'read off']:
                    # Previous state for undo
                    prev_state = actions['read']
                    
                    actions['read'] = event.raw_text.endswith('on')
                    
                    # Add to command history
                    command_history.append(('action', ('read', prev_state)))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                    
                    await event.reply(f"✅ خواندن خودکار {'فعال' if actions['read'] else 'غیرفعال'} شد")

                # Toggle auto reply status
                elif event.raw_text in ['reply on', 'reply off']:
                    # Previous state for undo
                    prev_state = actions['auto_reply']
                    
                    actions['auto_reply'] = event.raw_text.endswith('on')
                    
                    # Add to command history
                    command_history.append(('action', ('auto_reply', prev_state)))
                    if len(command_history) > MAX_HISTORY:
                        command_history.pop(0)
                    
                    await event.reply(f"✅ پاسخ خودکار {'فعال' if actions['auto_reply'] else 'غیرفعال'} شد")

                # Exit command
                elif event.raw_text == 'exit':
                    await event.reply("✅ در حال خروج از برنامه...")
                    global running
                    running = False
                    await client.disconnect()
                    return
            except Exception as e:
                logger.error(f"Error in message handler: {e}")
                pass

        @client.on(events.NewMessage(pattern='وضعیت'))
        async def status_handler(event):
            try:
                if not event.from_id:
                    return
                    
                if event.from_id.user_id == (await client.get_me()).id:
                    await show_status(client, event)
            except Exception as e:
                logger.error(f"Error in status handler: {e}")
                print_error(f"Error showing status: {e}")

        @client.on(events.MessageDeleted)
        async def delete_handler(event):
            """Handle deleted messages for anti-delete feature"""
            try:
                for deleted_id in event.deleted_ids:
                    chat_id = str(event.chat_id)
                    if chat_id in locked_chats['delete']:
                        # Try to find the message in our cache
                        msg = await client.get_messages(event.chat_id, ids=deleted_id)
                        if msg and msg.text:
                            sender = await msg.get_sender()
                            sender_name = utils.get_display_name(sender) if sender else "Unknown"
                            
                            saved_text = f"🔴 پیام حذف شده از {sender_name}:\n{msg.text}"
                            await client.send_message(event.chat_id, saved_text)
            except Exception as e:
                logger.error(f"Error in delete handler: {e}")

        @client.on(events.MessageEdited)
        async def edit_handler(event):
            """Handle edited messages for anti-edit feature"""
            try:
                chat_id = str(event.chat_id)
                if chat_id in locked_chats['edit'] and event.message:
                    # We need to find the original message
                    msg_id = event.message.id
                    
                    # Get edit history
                    edit_history = await client(functions.channels.GetMessageEditHistoryRequest(
                        channel=event.chat_id,
                        id=msg_id
                    ))
                    
                    if edit_history and edit_history.messages:
                        # Get the original message (first in history)
                        original = edit_history.messages[-1]
                        current = event.message
                        
                        if original.message != current.message:
                            sender = await event.get_sender()
                            sender_name = utils.get_display_name(sender) if sender else "Unknown"
                            
                            edit_text = f"🔄 پیام ویرایش شده از {sender_name}:\n\nقبل:\n{original.message}\n\nبعد:\n{current.message}"
                            await client.send_message(event.chat_id, edit_text)
            except Exception as e:
                logger.error(f"Error in edit handler: {e}")

        # Run the client until disconnected
        print_success("Self-bot is running")
        await client.run_until_disconnected()

    except KeyboardInterrupt:
        print_warning("\nKilling the self-bot by keyboard interrupt...")
        return
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        logger.error(f"Unexpected error: {e}")
        return
    finally:
        
        running = False
        if client and client.is_connected():
            await client.disconnect()
        print_info("Self-bot has been shut down")

def init():
    """Initialize and run the self-bot"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\nExiting self-bot...")
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")
        logging.error(f"Unexpected init error: {e}")

if __name__ == '__main__':
    init()
