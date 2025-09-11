import os
import subprocess
import sys
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try :
    
    from rubpy import Client, filters, utils
    from rubpy.types import Updates
except ImportError :
    install('rubpy')
    
try :
    
    import requests
except ImportError :
    install('requests')

# ساخت ربات با rubpy
bot = Client(name='music_styles')

# لیست سبک‌های موسیقی
music_styles = [
    "1- Pop 🎉", "2- Intense 🔥", "3- Violin 🎻", "4- Anthemic 🎺", 
    "5- Male Voice 👨‍🎤", "6- Funk 🎵", "7- Ethereal 🌌", 
    "8- Hard Rock 🤘", "9- Groovy 🎸", "10- Soul 🎷", 
    "11- Psychedelic 🌈", "12- Catchy 🎶", "13- Male Vocals 🎤", 
    "14- Japanese 🇯🇵", "15- Ambient 🌌", "16- Atmospheric ☁️", 
    "17- Synth 🎹", "18- Dreamy 🌙", "19- Electric Guitar 🎸"
]

# متغیرهای موقتی برای ذخیره انتخاب‌ها
user_data = {}

# هندلر برای نمایش راهنما با /start
@bot.on_message_updates(filters.Commands(['start']),filters.is_private)
async def start(update: Updates):
    user_id = update.object_guid
    # ایجاد دیکشنری جدید برای ذخیره اطلاعات کاربر
    user_data[user_id] = {}

    welcome_message = (
        "سلام! 🎶\n"
        "من یک ربات برای ساخت آهنگ هستم. با استفاده از لیست زیر می‌توانید یک سبک موسیقی انتخاب کنید.\n\n"
        "لطفاً عدد مرتبط با سبک مورد نظر را وارد کنید:\n\n"
    )
    styles = "\n".join(music_styles)
    await update.reply(welcome_message + styles)

# هندلر برای نمایش راهنما با /help
@bot.on_message_updates(filters.Commands(['help']),filters.is_private)
async def help_command(update: Updates):
    help_message = (
        "/start - شروع و انتخاب سبک موسیقی\n"
        "/help - دریافت راهنما\n"
        "پس از انتخاب سبک، از شما خواسته می‌شود متن آهنگ خود را وارد کنید."
    )
    await update.reply(help_message)

# هندلر برای دریافت انتخاب سبک موسیقی
@bot.on_message_updates(filters.is_private)
async def choose_style(update: Updates):
    user_id = update.object_guid # دریافت user_id به‌درستی

    # اگر کاربر هنوز سبکی انتخاب نکرده
    if user_id not in user_data:
        user_data[user_id] = {}

    if 'style' not in user_data[user_id]:
        # دریافت شماره انتخابی کاربر
        try:
            style_index = int(update.message.text.strip()) - 1
            if 0 <= style_index < len(music_styles):
                style_name = music_styles[style_index].split("- ")[1]
                user_data[user_id]['style'] = style_name
                await update.reply(f"سبک {style_name} انتخاب شد. 🎶\nحالا متن آهنگ رو ارسال کن:")
            else:
                await update.reply("لطفاً یک عدد معتبر انتخاب کنید.")
        except ValueError:
            await update.reply("لطفاً یک عدد معتبر انتخاب کنید.")
    
    # دریافت متن آهنگ
    elif 'text' not in user_data[user_id]:
        user_data[user_id]['text'] = update.message.text.strip()
        await update.reply("منتظر باش تا آهنگت ساخته بشه 🎵...")

        # ساخت موسیقی با API
        style = user_data[user_id]['style']
        text = user_data[user_id]['text']
        music_url = await create_music(style, text)

        if music_url:
            # دانلود و ارسال آهنگ به کاربر
            await send_music(update, music_url)
        else:
            await update.reply("مشکلی در ساخت موسیقی پیش آمد. لطفاً دوباره امتحان کنید.")

        # پاک کردن دیتا بعد از ارسال آهنگ
        del user_data[user_id]

# تابع برای ساخت موسیقی با API
async def create_music(style, text):
    api_url = "https://api.api-code.ir/c-music/"
    params = {
        "style": style.replace(' ', '').lower(),  # تغییر سبک به فرمت مناسب برای API
        "text": text.replace(' ', '+')  # جایگزینی فاصله‌ها با + برای API
    }
    
    try:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                return data["music_url"]
        return None
    except Exception as e:
        print(f"Error in API request: {e}")
        return None

# تابع برای دانلود و ارسال موسیقی
async def send_music(update: Updates, music_url):
    try:
        music_response = requests.get(music_url)
        if music_response.status_code == 200:
            file_name = "music.mp3"
            with open(file_name, "wb") as f:
                f.write(music_response.content)

            # ارسال فایل موسیقی به کاربر
            await update.reply_document(file_name, caption="این هم آهنگت 🎵")
        else:
            await update.reply("مشکلی در دانلود موسیقی پیش آمد.")
    except Exception as e:
        print(f"Error in downloading music: {e}")
        await update.reply("مشکلی در دانلود موسیقی پیش آمد.")

# اجرای ربات
bot.run()
