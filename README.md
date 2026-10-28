# Future Mind — منصة متابعة الطفل (Django + Templates)

مشروع Django كامل بلغة Python مع قوالب HTML/CSS/JS وواجهة عربية RTL.

## الإمكانيات
1. مراقبة المستوى والدرجات والحضور والانصراف.
2. تحديد أسلوب التعلم (سمعي / بصري / كتابي / حركي) وبناء خطة تعليمية مناسبة.
3. خطة طويلة المدى بمراحل عمرية توجّه الطفل لمجاله (هندسة، طب...).
4. ملف صحي كامل: التاريخ المرضي، الحساسية، الفحوصات.
5. أدوات مراقبة أبوية: وقت الشاشة، حظر السوشيال ميديا، الموقع.
6. تقييم المدرسين والمدارس بآراء أولياء الأمور.
7. تحويل المنهج إلى ألعاب وفيديوهات AI بشخصيات يحبها الطفل.
8. قسم الصحة والنشاط البدني.
9. شات بوت **Future Mind** يرد ببيانات الطفل الحقيقية من قاعدة البيانات.

## التشغيل في VS Code
```bash
cd future_mind_django
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations core
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```
ثم افتح: http://127.0.0.1:8000

- حساب ولي الأمر: `parent` / `future1234`
- لوحة الإدارة: http://127.0.0.1:8000/admin — `admin` / `admin1234`

## الصفحات
| المسار | الوصف |
|---|---|
| `/` | الصفحة الرئيسية (Landing) |
| `/dashboard/` | لوحة متابعة الطفل |
| `/plan/` | الخطة المستقبلية |
| `/lessons/` | الدروس التفاعلية وفيديوهات AI |
| `/teachers/` | تقييم المدرسين والمدارس |
| `/profile/` | الملف الشخصي والتاريخ المرضي |
| `/admin/` | لوحة الإدارة |

## ربط الشات بموديل AI حقيقي
عدّل الدالة `generate_reply` في `core/chatbot.py` لترسل السؤال + سياق الطفل
إلى OpenAI أو Gemini وترجّع النص.

## الهيكل
```
future_mind_django/
├── manage.py
├── requirements.txt
├── future_mind/        # الإعدادات والروابط
├── core/               # الموديلز والفيوز والشات بوت والبيانات التجريبية
├── templates/          # صفحات HTML
└── static/             # CSS / JS / صور
```
