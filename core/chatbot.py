"""منطق شات بوت Future Mind.

يرد على أي رسالة: تحية، شكر، سؤال عام، حساب بسيط، أو سؤال عن بيانات الطفل.
لربطه بموديل ذكاء اصطناعي حقيقي (OpenAI / Gemini) عدّل دالة generate_reply
لترسل السؤال + سياق الطفل إلى الـ API وترجّع النص.
"""

import datetime as dt
import random
import re
import unicodedata

from .models import Child, Teacher

_AR_DIAC = re.compile(r"[\u064B-\u0652\u0640]")


def normalize(text: str) -> str:
    """توحيد شكل النص العربي حتى نطابق الكلمات مهما اختلف الإملاء."""
    t = unicodedata.normalize("NFKC", (text or "").strip().lower())
    t = _AR_DIAC.sub("", t)
    t = (
        t.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
        .replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    )
    return re.sub(r"\s+", " ", t)


def _has(text: str, words) -> bool:
    return any(w in text for w in words)


def _context(child: Child) -> dict:
    return {
        "name": child.name if child else "طفلك",
        "age": child.age if child else None,
        "style": child.get_learning_style_display() if child else "",
        "avg": child.average_score if child else 0,
        "attendance": child.attendance_rate if child else 0,
        "screen": child.daily_screen_minutes if child else 0,
        "health": getattr(child, "health", None) if child else None,
        "plan": child.career_plans.first() if child else None,
    }


def _try_math(q: str):
    """يحسب عملية حسابية بسيطة لو المستخدم كتبها."""
    expr = q.replace("×", "*").replace("÷", "/").replace("،", "")
    expr = re.sub(r"[^0-9+\-*/(). ]", "", expr)
    if not re.search(r"\d[\s]*[+\-*/][\s]*\d", expr):
        return None
    try:
        value = eval(expr, {"__builtins__": {}}, {})  # noqa: S307 - تعبير أرقام فقط
    except Exception:
        return None
    if isinstance(value, float):
        value = round(value, 4)
    return f"الناتج = {value} ✅"


GREETINGS = ["هاي", "هلا", "اهلا", "مرحبا", "سلام عليكم", "السلام", "صباح", "مساء", "hi", "hello", "hey", "ازيك", "عامل ايه", "يا فيوتشر"]
THANKS = ["شكرا", "متشكر", "تسلم", "thanks", "thank you", "جزاك"]
BYE = ["باي", "مع السلامه", "الي اللقاء", "bye", "سلام بس"]


def _smalltalk(q: str, c: dict):
    if _has(q, GREETINGS):
        return random.choice([
            f"أهلاً بيك 👋 أنا Future Mind، مساعدك في متابعة {c['name']}. تحب نبدأ بإيه: المستوى الدراسي، الحضور، الخطة المستقبلية، ولا الصحة؟",
            f"هاي 😄 نورت! معايا كل بيانات {c['name']} — اسألني عن درجاته أو غيابه أو خطته المستقبلية.",
            "مرحباً بك في Future Mind ✨ اسألني أي حاجة عن رحلة ابنك التعليمية.",
        ])
    if _has(q, THANKS):
        return "العفو 💜 أنا هنا في أي وقت. تحب أعرض لك ملخص اليوم؟"
    if _has(q, BYE):
        return "مع السلامة 👋 هتلاقيني هنا في أي وقت تحتاجني."
    if _has(q, ["مين انت", "من انت", "اسمك ايه", "انت ايه", "who are you"]):
        return (
            "أنا Future Mind 🤖 — مساعد ذكي بيتابع الطفل من صغره: مستواه الدراسي، حضوره، "
            "أسلوب استيعابه، خطته المستقبلية، صحته، ووقت الشاشة، وبيقترح خطوات عملية لكل ده."
        )
    if _has(q, ["تعمل ايه", "تقدر تعمل", "بتعمل ايه", "مساعده", "مساعدة", "help", "ساعدني", "قائمه", "امكانيات"]):
        return (
            "أقدر أساعدك في:\n"
            "• متابعة الدرجات والمستوى الدراسي\n"
            "• الحضور والانصراف والغياب\n"
            "• تحديد أسلوب التعلم المناسب (سمعي / بصري / كتابي)\n"
            "• الخطة المستقبلية والمجال المناسب\n"
            "• الملف الصحي والنشاط الرياضي\n"
            "• المراقبة الأبوية ووقت الشاشة\n"
            "• تقييمات المدرسين والمدارس\n"
            "اكتب سؤالك بأي صيغة وأنا هفهمك 😊"
        )
    if _has(q, ["الوقت", "الساعه", "التاريخ", "النهارده", "اليوم كام"]):
        now = dt.datetime.now()
        return f"النهاردة {now.strftime('%Y-%m-%d')} والساعة {now.strftime('%I:%M %p')}."
    if _has(q, ["نكته", "نكتة", "ضحكني", "قول حاجه حلوه"]):
        return random.choice([
            "معلمة سألت الطفل: لو عندك 5 تفاحات وأخدت منك 3، تبقى معاك كام؟ قال: صديق أقل 😄",
            "الطفل قال لأبوه: أنا هبقى عالم! قاله: عظيم. قال: بس بعد ما أخلص اللعبة 🎮",
        ])
    if _has(q, ["كيف حالك", "عامل ايه", "اخبارك"]):
        return "تمام الحمد لله 😄 وأنا شغال على تحليل بيانات ابنك باستمرار. عايز تعرف إيه؟"
    return None


def generate_reply(child: Child, question: str) -> str:
    q = normalize(question)
    c = _context(child)

    if not q:
        return "اكتب سؤالك وأنا تحت أمرك 💜"

    small = _smalltalk(q, c)
    if small:
        return small

    math = _try_math(q)
    if math:
        return math

    if _has(q, ["تعلم", "استيعاب", "طريقه", "دماغ", "يفهم", "اسلوب"]) and child:
        return (
            f"حسب تحليل آخر أنشطة {c['name']}، أسلوب التعلم الأنسب له: {c['style']} "
            f"(نسبة استيعاب {child.comprehension_score}%). أنصح بفيديوهات AI قصيرة "
            "من 7 إلى 10 دقائق مع تلخيص بعد كل درس بنفس الأسلوب."
        )

    if _has(q, ["مستقبل", "خطه", "مجال", "هندسه", "دكتور", "كليه", "شغل", "وظيفه"]) and child:
        if c["plan"]:
            ms = " ← ".join(m.title for m in c["plan"].milestones.all()[:4])
            return (
                f"الخطة الحالية: {c['plan'].target_field} بنسبة توافق "
                f"{c['plan'].match_percent}%. المراحل: {ms}."
            )
        return "لا توجد خطة مسجلة بعد. ابدأ باختبار الميول من صفحة الخطة المستقبلية."

    if _has(q, ["درجات", "درجه", "مستوي", "المعدل", "نتيجه", "شاطر", "امتحان"]) and child:
        subjects = "، ".join(
            f"{g.subject.name}: {g.score}%" for g in child.grades.order_by("-date")[:4]
        )
        return f"المعدل العام {c['avg']}% ونسبة الحضور {c['attendance']}%. آخر الدرجات — {subjects}."

    if _has(q, ["حضور", "انصراف", "غياب", "تاخير", "مدرسه امتي"]) and child:
        absent = child.attendances.filter(status="absent").count()
        return f"نسبة الحضور {c['attendance']}%، وعدد أيام الغياب المسجلة {absent} يوم."

    if _has(q, ["صحه", "مرض", "حساسيه", "طبيب", "دواء", "وزن", "طول"]) and child:
        h = c["health"]
        if not h:
            return "لا يوجد ملف صحي مسجل بعد — أضفه من صفحة الملف الشخصي."
        return (
            f"الملف الصحي: فصيلة الدم {h.blood_type or 'غير مسجلة'}، أمراض مزمنة "
            f"({h.chronic_conditions or 'لا توجد'})، حساسية ({h.allergies or 'لا توجد'})، "
            f"آخر فحص: {h.last_checkup or 'غير مسجل'}."
        )

    if _has(q, ["رياضه", "نشاط", "بدني", "جسم", "رياضي", "جري", "كوره"]):
        mins = getattr(c["health"], "daily_activity_minutes", 60) or 60
        return (
            f"توصية اليوم: {mins} دقيقة نشاط بدني — إحماء 10 دقائق، جري خفيف 20 دقيقة، "
            "لعب كرة 20 دقيقة، وإطالة 10 دقائق. هذا يرفع التركيز أثناء المذاكرة."
        )

    if _has(q, ["سوشيال", "تشتت", "موبايل", "شاشه", "تيك", "يوتيوب", "العاب", "تركيز"]) and child:
        tail = (
            "وضع التركيز مفعّل ✅"
            if child.focus_mode
            else "أنصح بتفعيل وضع التركيز لحظر التطبيقات الترفيهية وقت المذاكرة."
        )
        return f"وقت الشاشة اليوم {c['screen']} دقيقة. {tail}"

    if _has(q, ["مدرس", "مدرسه", "تقييم", "افضل", "احسن"]):
        best = sorted(Teacher.objects.all(), key=lambda t: t.rating or 0, reverse=True)[:3]
        if best:
            names = "، ".join(f"{t.name} ({t.rating}⭐)" for t in best)
            return f"أعلى تقييمات حالياً: {names}. تقدر تشوف كل التقييمات من صفحة (المدرسون والمدارس)."
        return "لا توجد تقييمات مسجلة بعد — كن أول من يضيف تقييماً من صفحة المدرسين."

    if _has(q, ["مذاكره", "جدول", "ينظم", "وقت", "روتين"]):
        return (
            "جدول مقترح للمساء: 17:00 راحة ونشاط بدني، 18:00 مذاكرة 25 دقيقة + 5 راحة (×3)، "
            "19:30 مراجعة سريعة بالفيديو، 20:30 قراءة حرة، ثم نوم مبكر."
        )

    if _has(q, ["ملخص", "تقرير", "احوال", "اخبار ابني", "كل حاجه"]) and child:
        return (
            f"ملخص {c['name']} ({c['age']} سنة): المعدل {c['avg']}%، الحضور {c['attendance']}%، "
            f"أسلوب التعلم {c['style']}، وقت الشاشة {c['screen']} دقيقة، "
            f"الخطة: {c['plan'].target_field if c['plan'] else 'لم تُحدد بعد'}."
        )

    return (
        f"فهمت سؤالك 🙂 بس محتاج توضيح بسيط. أقدر أجاوبك بدقة عن {c['name']} في: "
        "المستوى الدراسي، الحضور والغياب، أسلوب التعلم، الخطة المستقبلية، الملف الصحي، "
        "النشاط الرياضي، وقت الشاشة، أو أفضل مدرس/مدرسة. اكتب أي كلمة من دول وهرد عليك فوراً."
    )
