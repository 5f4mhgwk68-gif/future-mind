"""بيانات تجريبية جاهزة:  python manage.py seed_data"""

import datetime as dt
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import (
    Attendance,
    CareerPlan,
    Child,
    Grade,
    HealthRecord,
    Lesson,
    LessonProgress,
    ParentalControl,
    PlanMilestone,
    Review,
    Subject,
    Teacher,
)

SUBJECT_NAMES = ["الرياضيات", "العلوم", "اللغة الإنجليزية", "اللغة العربية", "الدراسات الاجتماعية"]

# (username, الاسم الأول, اسم العائلة, كلمة السر)
PARENTS = [
    ("parent", "أحمد", "محمد", "future1234"),
    ("mona", "منى", "عبد الرحمن", "future1234"),
    ("khaled", "خالد", "السيد", "future1234"),
    ("nour", "نور", "إبراهيم", "future1234"),
]

# (username ولي الأمر, اسم الطفل, سنة الميلاد, الصف, المدرسة, أسلوب التعلم,
#  الاستيعاب, دقائق الشاشة, وضع التركيز, المجال, نسبة التوافق)
CHILDREN = [
    ("parent", "محمد أحمد", 2014, "الصف الأول الإعدادي", "مدرسة النور الحديثة", "audio", 84, 225, True, "هندسة الحاسبات", 87),
    ("parent", "ملك أحمد", 2017, "الصف الثالث الابتدائي", "مدرسة النور الحديثة", "visual", 78, 140, False, "طب الأطفال", 81),
    ("mona", "يوسف عمرو", 2013, "الصف الثاني الإعدادي", "مدرسة المستقبل الدولية", "kinesthetic", 72, 260, False, "الطيران", 76),
    ("mona", "حبيبة عمرو", 2016, "الصف الرابع الابتدائي", "مدرسة المستقبل الدولية", "reading", 88, 110, True, "الصيدلة", 84),
    ("khaled", "عمر خالد", 2012, "الصف الثالث الإعدادي", "مدرسة الأندلس", "visual", 69, 300, False, "التصميم والإعلام", 73),
    ("nour", "سلمى محمود", 2015, "الصف السادس الابتدائي", "مدرسة الرواد", "audio", 91, 95, True, "الذكاء الاصطناعي", 92),
]

TEACHERS = [
    ("أ. محمد علي", "teacher", "الرياضيات", "القاهرة"),
    ("أ. سارة حسن", "teacher", "اللغة الإنجليزية", "الجيزة"),
    ("أ. هبة مصطفى", "teacher", "العلوم", "الإسكندرية"),
    ("أ. كريم فؤاد", "teacher", "اللغة العربية", "المنصورة"),
    ("أ. داليا سمير", "teacher", "الدراسات الاجتماعية", "طنطا"),
    ("مدرسة النور الحديثة", "school", "مدينة نصر", "القاهرة"),
    ("مدرسة المستقبل الدولية", "school", "التجمع الخامس", "القاهرة"),
    ("مدرسة الأندلس", "school", "المهندسين", "الجيزة"),
    ("مدرسة الرواد", "school", "سموحة", "الإسكندرية"),
]

COMMENTS = [
    "متابعة ممتازة وتعامل راقٍ مع الأطفال.",
    "شرح مبسط وابني بقى بيحب المادة.",
    "التزام بالمواعيد وتقارير أسبوعية مفيدة.",
    "مستوى جيد لكن المجموعات كبيرة شوية.",
    "أفضل اختيار بالنسبة لينا هذه السنة.",
    "تواصل دائم مع ولي الأمر وده مريح جداً.",
]

LESSONS = [
    ("الكسور الاعتيادية", "الرياضيات", "ai_video", "بطل المغامرات"),
    ("دورة الماء في الطبيعة", "العلوم", "game", "المستكشف الصغير"),
    ("الأزمنة في الإنجليزية", "اللغة الإنجليزية", "audio", ""),
    ("الجملة الاسمية", "اللغة العربية", "quiz", ""),
    ("خرائط مصر القديمة", "الدراسات الاجتماعية", "game", "المؤرخ الصغير"),
    ("الجاذبية والحركة", "العلوم", "ai_video", "رائد الفضاء"),
]


class Command(BaseCommand):
    help = "تعبئة قاعدة البيانات ببيانات تجريبية"

    def handle(self, *args, **options):
        random.seed(7)

        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin1234")

        parents = {}
        for username, first, last, password in PARENTS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first, "last_name": last, "email": f"{username}@futuremind.app"},
            )
            if created:
                user.set_password(password)
                user.save()
            parents[username] = user

        subjects = {}
        for name in SUBJECT_NAMES:
            subjects[name], _ = Subject.objects.get_or_create(name=name)

        lessons = {}
        for title, subject, fmt, char in LESSONS:
            lessons[title], _ = Lesson.objects.get_or_create(
                title=title, defaults={"subject": subjects[subject], "fmt": fmt, "character": char}
            )

        today = dt.date.today()

        for (
            parent_key, name, year, grade_name, school, style,
            comprehension, screen, focus, field, match,
        ) in CHILDREN:
            parent = parents[parent_key]
            child, _ = Child.objects.get_or_create(
                parent=parent,
                name=name,
                defaults={
                    "birth_date": dt.date(year, random.randint(1, 12), random.randint(1, 27)),
                    "grade": grade_name,
                    "school": school,
                    "learning_style": style,
                    "comprehension_score": comprehension,
                    "daily_screen_minutes": screen,
                    "focus_mode": focus,
                },
            )

            if not child.grades.exists():
                base = {s: random.randint(62, 82) for s in SUBJECT_NAMES}
                for week in range(10, 0, -1):
                    for s_name, subject in subjects.items():
                        base[s_name] = min(99, base[s_name] + random.randint(0, 3))
                        Grade.objects.create(
                            child=child,
                            subject=subject,
                            score=base[s_name],
                            date=today - dt.timedelta(weeks=week),
                        )

            if not child.attendances.exists():
                for i in range(30):
                    day = today - dt.timedelta(days=i)
                    if day.weekday() in (4, 5):
                        continue
                    status = random.choices(["present", "late", "absent"], [88, 8, 4])[0]
                    Attendance.objects.create(
                        child=child,
                        date=day,
                        status=status,
                        check_in=dt.time(7, 45),
                        check_out=dt.time(14, 15),
                    )

            HealthRecord.objects.get_or_create(
                child=child,
                defaults={
                    "blood_type": random.choice(["O+", "A+", "B+", "AB+"]),
                    "chronic_conditions": random.choice(["لا توجد أمراض مزمنة", "ربو خفيف", "لا توجد أمراض مزمنة"]),
                    "allergies": random.choice(["حساسية من البنسلين", "لا توجد", "حساسية من الأتربة"]),
                    "last_checkup": today - dt.timedelta(days=random.randint(20, 120)),
                    "height_cm": random.randint(120, 165),
                    "weight_kg": random.randint(25, 55),
                    "daily_activity_minutes": random.choice([45, 60, 75]),
                    "notes": "ينصح بفحص نظر دوري بسبب ساعات الشاشة.",
                },
            )

            ParentalControl.objects.get_or_create(
                child=child,
                defaults={
                    "screen_limit_minutes": 180,
                    "block_social_from": dt.time(17, 0),
                    "block_social_to": dt.time(20, 0),
                    "location_sharing": True,
                    "last_location": "المدرسة — الفصل الدراسي",
                },
            )

            plan, made = CareerPlan.objects.get_or_create(
                child=child,
                defaults={
                    "target_field": field,
                    "match_percent": match,
                    "summary": f"ميول واضحة نحو {field} حسب تحليل الأنشطة والدرجات.",
                },
            )
            if made:
                milestones = [
                    (f"الآن · {child.age} سنة", "اكتشاف الميول", "اختبارات ذكاء ومهارات لتحديد الاتجاه", True),
                    ("14 سنة", "تأسيس علمي", "تقوية المواد الأساسية ومهارات المنطق", False),
                    ("16 سنة", "مشاريع عملية", f"أنشطة ومسابقات في مجال {field}", False),
                    ("18 سنة", "اختيار الكلية", f"{field} — مسار مرشّح بنسبة {match}%", False),
                ]
                for i, (age_label, title, desc, done) in enumerate(milestones):
                    PlanMilestone.objects.create(
                        plan=plan, age_label=age_label, title=title,
                        description=desc, done=done, order=i,
                    )

            for lesson in random.sample(list(lessons.values()), 4):
                LessonProgress.objects.get_or_create(
                    child=child, lesson=lesson, defaults={"percent": random.randint(35, 98)}
                )

        parent_users = list(parents.values())
        for name, kind, subject, city in TEACHERS:
            teacher, made = Teacher.objects.get_or_create(
                name=name, defaults={"kind": kind, "subject": subject, "city": city}
            )
            if made:
                for author in random.sample(parent_users, random.randint(2, len(parent_users))):
                    Review.objects.create(
                        teacher=teacher,
                        author=author,
                        stars=random.randint(3, 5),
                        comment=random.choice(COMMENTS),
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"تم إنشاء البيانات ✅ أولياء أمور: {len(PARENTS)} — أطفال: {Child.objects.count()} — "
                "الدخول: parent / mona / khaled / nour بكلمة سر future1234 — المدير: admin / admin1234"
            )
        )
