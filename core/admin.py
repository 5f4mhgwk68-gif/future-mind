from django.contrib import admin

from .models import (
    Attendance,
    CareerPlan,
    ChatMessage,
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


class MilestoneInline(admin.TabularInline):
    model = PlanMilestone
    extra = 1


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ("name", "grade", "school", "learning_style", "average_score", "attendance_rate")
    search_fields = ("name", "school")


@admin.register(CareerPlan)
class CareerPlanAdmin(admin.ModelAdmin):
    list_display = ("child", "target_field", "match_percent")
    inlines = [MilestoneInline]


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "subject", "rating", "reviews_count")


for model in (
    Subject,
    Grade,
    Attendance,
    HealthRecord,
    Lesson,
    LessonProgress,
    ParentalControl,
    Review,
    ChatMessage,
):
    admin.site.register(model)
