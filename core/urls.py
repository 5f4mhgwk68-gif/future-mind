from django.urls import path

from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("signup/", views.signup, name="signup"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("plan/", views.plan, name="plan"),
    path("lessons/", views.lessons, name="lessons"),
    path("teachers/", views.teachers, name="teachers"),
    path("teachers/<int:teacher_id>/review/", views.add_review, name="add_review"),
    path("contact/", views.contact, name="contact"),
    path("chat/", views.chat, name="chat"),
]
