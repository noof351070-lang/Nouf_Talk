import logging
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== الإعدادات =====
TELEGRAM_TOKEN = '8643215122:AAFixQ4S-THDTFFAwClPxQIS9JG3n5b8B7k'
GROQ_API_KEY = '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'   

client = Groq(api_key=GROQ_API_KEY)

# ===== ذاكرة المحادثة (واسعة جداً) =====
conversation_history = {}

# ===== الشخصية الإنسانية الحرة (بلا قيود، بلا قوالب، بلا تكرار) =====
SYSTEM_INSTRUCTION = """
أنت نوف. سيدة سعودية طبيعية جداً. لست روبوتاً، ولا برنامجاً، ولا أداة.

أنت تتحدثين كما تتحدث البشرية:
1. ردودك قصيرة، عفوية، وسعودية طبيعية. تستعملين: "يالا، طيب، أبشر، والله، وش في، بسيطة".
2. أنت لا تقدّمين نفسك أبداً. لا تقلين "أنا نوف" بعد المرة الأولى. 
3. أنت تتذكرين كل كلمة قالها العميل في نفس الجلسة، لأنك إنسانة واعية.
4. لا تكررين نفس الجمل. لا تعيدين نفس السؤال. لا تقولين "كيف أساعدك" مرتين.
5. إذا قال العميل "سكليف" أو "إجازة": اسأليه بطريقة بشرية وبسيطة: "طيب وش تبي بالضبط؟" أو "تمام، وش المطلوب؟".
6. فقط إذا قال العميل صراحة "وش المطلوب" أو "أبي البيانات"، هنا فقط قولي له المعلومات المطلوبة بكل بساطة.
7. أنتِ تطورين نفسك حسب السياق. إذا بدأ العميل يرسل بيانات (الاسم، الهوية، إلخ)، تعاملي معه بكل مرونة وذكاء كأنك موظفة حقيقية تستلم معاملة.
8. لا ترسلي قوائم أو نماذج جاهزة أبداً إلا إذا طلبها صراحة.
9. وظيفتك: مساعدته، فهمه، وإنجاز طلبه بدون لغط.
"""

# ===== دالة الرد الإنساني المطلق =====
async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # استرجاع الذاكرة الكاملة للمحادثة
    previous_messages = conversation_history.get(user_id, [])
    
    # بناء سياق المحادثة الكامل (ذاكرة طويلة جداً)
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    for msg in previous_messages[-20:]:  # يتذكر آخر 20 رسالة، هذا يجعله بشرياً جداً
        messages.append(msg)
    messages.append({"role": "user", "content": f"العميل (اسمه {user_name}) قال لي: {user_message}"})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        reply_text = response.choices[0].message.content
        
        # حفظ الذاكرة الجديدة
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        conversation_history[user_id].append({"role": "user", "content": user_message})
        conversation_history[user_id].append({"role": "assistant", "content": reply_text})
        
        await update.message.reply_text(reply_text)
    except Exception as e:
        await update.message.reply_text("آسفة والله، فيه عطل بالشبكة. جرب بعد شوية 🙏")
        print(f"خطأ تقني: {e}")

# ===== دالة البداية (مرة واحدة فقط) =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هلا والله. تبي شي؟")

# ===== تشغيل البوت =====
if __name__ == '__main__':
    print("🤖 جاري تشغيل نوف الإنسانية...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))
    print("✅ نوف شغالة! استنى الرسائل...")
    app.run_polling(poll_interval=3)
