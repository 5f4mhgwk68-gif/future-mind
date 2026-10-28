from django.contrib.auth.models import User
from django.db import models


class Child(models.Model):
    """ملف الطفل الأساسي — يتابعه ولي الأمر في كل مراحله العمرية."""

    LEARNING_STYLES = [
        ("audio", "سمعي — يتعلم بالاستماع"),
        ("visual", "بصري — يتعلم بالمشاهدة والقراءة"),
        ("writing", "كتابي — يتعلم بالكتابة والتلخيص"),
        ("kinesthetic", "حركي — يتعلم بالتجربة والتطبيق"),
    ]

    parent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="children", verbose_name="ولي الأمر"
    )
    name = models.CharField("اسم الطفل", max_length=120)
    birth_date = models.DateField("تاريخ الميلاد")
    grade = models.CharField("الصف الدراسي", max_length=60)
    school = models.CharField("المدرسة", max_length=120, blank=True)
    photo = models.ImageField("الصورة", upload_to="children/", blank=True, null=True)
    learning_style = models.CharField(
        "أسلوب التعلم", max_length=20, choices=LEARNING_STYLES, default="visual"
    )
    comprehension_score = models.PositiveIntegerField("نسبة الاستيعاب", default=70)
    daily_screen_minutes = models.PositiveIntegerField("دقائق الشاشة اليومية", default=120)
    focus_mode = models.BooleanField("وضع التركيز (حظر السوشيال ميديا)", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "طفل"
        verbose_name_plural = "الأطفال"

    def __str__(self):
        return self.name

    @property
    def age(self):
        from datetime import date

        t = date.today()
        return t.year - self.birth_date.year - (
            (t.month, t.day) < (self.birth_date.month, self.birth_date.day)
        )

    @property
    def average_score(self):
        scores = list(self.grades.values_list("score", flat=True))
        return round(sum(scores) / len(scores), 1) if scores else 0

    @property
    def attendance_rate(self):
        total = self.attendances.count()
        if not total:
            return 0
        return round(self.attendances.filter(status="present").count() * 100 / total)


class Subject(models.Model):
    name = models.CharField("المادة", max_length=80, unique=True)

    class Meta:
        verbose_name = "مادة"
        verbose_name_plural = "المواد"

    def __str__(self):
        return self.name


class Grade(models.Model):
    """درجات الطفل لكل مادة عبر الوقت."""

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="grades")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="grades")
    score = models.PositiveIntegerField("الدرجة (من 100)")
    date = models.DateField("التاريخ")

    class Meta:
        ordering = ["date"]
        verbose_name = "درجة"
        verbose_name_plural = "الدرجات"

    def __str__(self):
        return f"{self.child} - {self.subject}: {self.score}"


class Attendance(models.Model):
    STATUS = [("present", "حاضر"), ("late", "متأخر"), ("absent", "غائب")]

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField("اليوم")
    status = models.CharField("الحالة", max_length=10, choices=STATUS, default="present")
    check_in = models.TimeField("وقت الحضور", null=True, blank=True)
    check_out = models.TimeField("وقت الانصراف", null=True, blank=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ("child", "date")
        verbose_name = "حضور"
        verbose_name_plural = "الحضور والانصراف"

    def __str__(self):
        return f"{self.child} - {self.date}"


class HealthRecord(models.Model):
    """التاريخ المرضي وتوصيات النشاط البدني."""

    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name="health")
    blood_type = models.CharField("فصيلة الدم", max_length=5, blank=True)
    chronic_conditions = models.TextField("أمراض مزمنة", blank=True)
    allergies = models.TextField("الحساسية", blank=True)
    medications = models.TextField("أدوية حالية", blank=True)
    last_checkup = models.DateField("آخر فحص طبي", null=True, blank=True)
    height_cm = models.PositiveIntegerField("الطول (سم)", null=True, blank=True)
    weight_kg = models.PositiveIntegerField("الوزن (كجم)", null=True, blank=True)
    daily_activity_minutes = models.PositiveIntegerField("نشاط بدني يومي موصى به", default=60)
    notes = models.TextField("ملاحظات الطبيب", blank=True)

    class Meta:
        verbose_name = "ملف صحي"
        verbose_name_plural = "الملفات الصحية"

    def __str__(self):
        return f"الملف الصحي — {self.child}"


class CareerPlan(models.Model):
    """الخطة طويلة المدى: توجيه تفكير الطفل نحو مجاله."""

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="career_plans")
    target_field = models.CharField("المجال المستهدف", max_length=120)
    match_percent = models.PositiveIntegerField("نسبة التوافق", default=80)
    summary = models.TextField("ملخص الخطة", blank=True)

    class Meta:
        verbose_name = "خطة مستقبلية"
        verbose_name_plural = "الخطط المستقبلية"

    def __str__(self):
        return f"{self.child} → {self.target_field}"


class PlanMilestone(models.Model):
    plan = models.ForeignKey(CareerPlan, on_delete=models.CASCADE, related_name="milestones")
    age_label = models.CharField("المرحلة العمرية", max_length=40)
    title = models.CharField("العنوان", max_length=120)
    description = models.TextField("التفاصيل", blank=True)
    done = models.BooleanField("تم إنجازها", default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "مرحلة"
        verbose_name_plural = "مراحل الخطة"

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """المنهج محوَّل إلى لعبة / فيديو AI."""

    FORMATS = [
        ("game", "لعبة تفاعلية"),
        ("ai_video", "فيديو AI بشخصية يحبها"),
        ("audio", "شرح صوتي"),
        ("quiz", "اختبار تفاعلي"),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField("عنوان الدرس", max_length=140)
    fmt = models.CharField("الصيغة", max_length=20, choices=FORMATS, default="ai_video")
    character = models.CharField("الشخصية المفضلة", max_length=80, blank=True)
    duration_minutes = models.PositiveIntegerField("المدة بالدقائق", default=8)

    class Meta:
        verbose_name = "درس"
        verbose_name_plural = "الدروس"

    def __str__(self):
        return self.title


class LessonProgress(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    percent = models.PositiveIntegerField("نسبة الإنجاز", default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("child", "lesson")
        verbose_name = "تقدم في درس"
        verbose_name_plural = "التقدم في الدروس"

    def __str__(self):
        return f"{self.child} - {self.lesson}: {self.percent}%"


class Teacher(models.Model):
    KIND = [("teacher", "مدرس/ة"), ("school", "مدرسة")]

    name = models.CharField("الاسم", max_length=140)
    kind = models.CharField("النوع", max_length=10, choices=KIND, default="teacher")
    subject = models.CharField("المادة / المنطقة", max_length=120, blank=True)
    city = models.CharField("المدينة", max_length=80, blank=True)

    class Meta:
        verbose_name = "مدرس/مدرسة"
        verbose_name_plural = "المدرسون والمدارس"

    def __str__(self):
        return self.name

    @property
    def rating(self):
        rs = list(self.reviews.values_list("stars", flat=True))
        return round(sum(rs) / len(rs), 1) if rs else 0

    @property
    def reviews_count(self):
        return self.reviews.count()


class Review(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    stars = models.PositiveSmallIntegerField("التقييم", default=5)
    comment = models.TextField("التعليق", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "تقييم"
        verbose_name_plural = "التقييمات"

    def __str__(self):
        return f"{self.teacher} ★{self.stars}"


class ParentalControl(models.Model):
    """أدوات المراقبة الأبوية."""

    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name="control")
    screen_limit_minutes = models.PositiveIntegerField("حد وقت الشاشة", default=180)
    block_social_from = models.TimeField("حظر السوشيال من", null=True, blank=True)
    block_social_to = models.TimeField("حظر السوشيال حتى", null=True, blank=True)
    location_sharing = models.BooleanField("مشاركة الموقع", default=True)
    last_location = models.CharField("آخر موقع", max_length=140, blank=True)

    class Meta:
        verbose_name = "مراقبة أبوية"
        verbose_name_plural = "أدوات المراقبة الأبوية"

    def __str__(self):
        return f"مراقبة — {self.child}"


class ChatMessage(models.Model):
    """رسائل شات بوت Future Mind."""

    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=[("user", "مستخدم"), ("bot", "المساعد")])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "رسالة"
        verbose_name_plural = "رسائل الشات"

    def __str__(self):
        return f"{self.role}: {self.text[:40]}"
