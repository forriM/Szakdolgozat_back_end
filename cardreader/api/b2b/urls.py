from django.urls import path
from cardreader.api.b2b import views


urlpatterns = [
    path('idcard/', views.read_id_card, name = 'read_id_card'),
    path('register/', views.create_company, name = 'create_company'),
    path('healthcard/', views.read_healthcare_card, name = 'read_healthcare_card'),
    path('studentcard/', views.read_student_card, name = 'read_student_card'),
]