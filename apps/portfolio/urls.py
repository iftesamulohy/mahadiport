from django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.home, name="home"),
    path("case/<slug:slug>/", views.case_detail, name="case_detail"),
    path("case/<slug:slug>/panel/", views.case_panel, name="case_panel"),
    path("skills/<slug:slug>/", views.skills_tab, name="skills_tab"),
]
