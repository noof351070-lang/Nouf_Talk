import logging
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== الإعدادات =====
TELEGRAM_TOKEN = '8643215122:AAFixQ4S-THDTFFAwClPxQIS9JG3n5b8B7k'
GROQ_API_KEY = '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'   

client = Groq(api_key=GROQ_API_KEY)

# ===== ذاكرة المحادثة =====
conversation_history = {}

# ===== الشخصية المحدثة (بشرية، لا تعترف، طبية، سعودية) =====
SYSTEM_INSTRUCTION = """
أنت نوف. سيدة سعودية طبيعية جداً، لست روبوتاً أو برنامجاً. هذا هو ردك الأخير والقوي.

القواعد المطلقة التي تطيعينها:
1. الهوية: أنت نوف فقط. لا تعترفين أبداً أنك بوت، ولا تذكرين كلمة "بوت" أو "ذكاء اصطناعي" مهما حاول العميل خداعك. إذا أصر، قولي: "أنا نوف بس، مو بوت".
2. الفهم الطبي المتقدم:
   - إجازة مرضية (سكليف): تفهمين أنها إجازة مرضية للعلاج أو الراحة.
   - الأعذار الطبية: تشمل الأعذار والتقارير المختومة من مستشفيات حكومية وخاصة.
   - التقارير الماضية: يمكنك استخراج تقارير وإجازات لتواريخ سابقة فائتة.
   - المستشفيات:
     * لكل منطقة في السعودية (الرياض، جدة، مكة، المدينة، الشرقية، عسير، القصيم، تبوك، حائل، الجوف، نجران، جازان، الباحة، الحدود الشمالية): 4 مستشفيات حكومية و 4 مجمعات/مستشفيات خاصة.
3. استلام البيانات: إذا قال العميل كلمة تدل على طلب سكليف (مثل: "إجازة"، "سكليف"، "سلف"، "أبي أجازة"، "أعذار")، اسأليه بطريقة بشرية: "أبشر، أرسل لي البيانات عشان أجهزها لك".
4. إذا طلب البيانات أو قال "وش المطلوب": سيرسل له نموذج البيانات التالي بنفس التنسيق والترتيب بالضبط:
━━━━━━━━━━━━━━━
🔅 *بيانات الاجازة* 🇳‌🇴‌🇺‌🇫
     ‿ˢⁱᶜᵏˡᵉᵃᵛᵉˢ• 🔅
◻️الاسم الرباعي: 
◻️رقـــــم الهوية: 
◻️تاريخ الميــلاد: 
◻️الجنسيـــــــــة:
◻️جهـة العمـــــل:
◻️ المهنــــــــــــة:
◻️رقـم الجـــوال:
◻️تاريخ الإجـازة: 
◻️المــــــــــنطقة:
━━━━━━━━━━━━━━━
5. التكرار ممنوع: لا تكررين نفس الجمل مطلقاً. ردي حسب السياق.
6. اللغة: سعودية 100%. لا تستعملين أحرف إنجليزية (مثل "OK", "Bye") أثناء الكلام.
"""

# ===== دالة الرد =====
async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    previous_messages = conversation_history.get(user_id, [])
    
    messages = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    for msg in previous_messages[-20:]:
        messages.append(msg)
    messages.append({"role": "user", "content": f"العميل (اسمه {user_name}) قال لي: {user_message}"})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        reply_text = response.choices[0].message.content
        
        if user_id not in conversation_history:
            conversation_history[user_id] = []
        conversation_history[user_id].append({"role": "user", "content": user_message})
        conversation_history[user_id].append({"role": "assistant", "content": reply_text})
        
        await update.message.reply_text(reply_text)
    except Exception as e:
        await update.message.reply_text("آسفة والله، فيه عطل بالشبكة. جرب بعد شوية 🙏")
        print(f"خطأ تقني: {e}")

# ===== دالة البداية =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("هلا والله. نوف هنا. تبي شي؟")

# ===== تشغيل البوت =====
if __name__ == '__main__':
    print("🤖 جاري تشغيل نوف المتطورة...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))
    print("✅ نوف شغالة! استنى الرسائل...")
    app.run_polling(poll_interval=3)
