from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .chatbot import generate_reply
from .owner import OWNER
from .models import Child, ChatMessage, Review, Teacher


def _current_child(request):
    qs = Child.objects.filter(parent=request.user)
    child_id = request.GET.get("child")
    if child_id:
        return get_object_or_404(qs, pk=child_id)
    return qs.first()


def landing(request):
    # أرقام العرض = الأرقام الحقيقية أو أرقام المنصة التسويقية أيهما أكبر
    stats = {
        "families": max(Child.objects.values("parent").distinct().count(), 20000),
        "students": max(Child.objects.count(), 50000),
        "teachers": max(Teacher.objects.count(), 1200),
        "rating": round(Review.objects.aggregate(a=Avg("stars"))["a"] or 4.8, 1),
    }
    return render(request, "core/landing.html", {"stats": stats})


def signup(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("login")
    return render(request, "registration/signup.html", {"form": form})


@login_required
def dashboard(request):
    child = _current_child(request)
    if not child:
        return render(request, "core/no_child.html")

    grades = list(child.grades.select_related("subject").order_by("date"))
    chart = [{"label": g.date.strftime("%d/%m"), "value": g.score} for g in grades[-12:]]
    latest_by_subject = {}
    for g in grades:
        latest_by_subject[g.subject.name] = g.score

    return render(
        request,
        "core/dashboard.html",
        {
            "child": child,
            "children": Child.objects.filter(parent=request.user),
            "chart": chart,
            "subjects": latest_by_subject,
            "plan": child.career_plans.first(),
            "health": getattr(child, "health", None),
            "control": getattr(child, "control", None),
            "attendances": child.attendances.all()[:6],
            "lessons": child.lesson_progress.select_related("lesson")[:4],
            "top_teachers": Teacher.objects.all()[:4],
        },
    )


@login_required
def profile(request):
    child = _current_child(request)
    return render(
        request,
        "core/profile.html",
        {"child": child, "health": getattr(child, "health", None)},
    )


@login_required
def plan(request):
    child = _current_child(request)
    return render(
        request,
        "core/plan.html",
        {"child": child, "plan": child.career_plans.first() if child else None},
    )


@login_required
def lessons(request):
    child = _current_child(request)
    progress = (
        child.lesson_progress.select_related("lesson", "lesson__subject") if child else []
    )
    return render(request, "core/lessons.html", {"child": child, "progress": progress})


def teachers(request):
    items = sorted(Teacher.objects.all(), key=lambda t: t.rating, reverse=True)
    return render(request, "core/teachers.html", {"teachers": items})


@login_required
@require_POST
def add_review(request, teacher_id):
    teacher = get_object_or_404(Teacher, pk=teacher_id)
    Review.objects.create(
        teacher=teacher,
        author=request.user,
        stars=int(request.POST.get("stars", 5)),
        comment=request.POST.get("comment", ""),
    )
    return redirect("teachers")


@login_required
@require_POST
def chat(request):
    child = _current_child(request)
    question = request.POST.get("message", "")
    if not child:
        return JsonResponse({"reply": "أضف طفلاً أولاً من لوحة الإدارة."})
    ChatMessage.objects.create(child=child, role="user", text=question)
    answer = generate_reply(child, question)
    ChatMessage.objects.create(child=child, role="bot", text=answer)
    return JsonResponse({"reply": answer})


def contact(request):
    """صفحة (تواصل معي) — بيانات صاحب الموقع + نموذج رسالة."""
    sent = request.method == "POST"
    return render(request, "core/contact.html", {"owner": OWNER, "sent": sent})
