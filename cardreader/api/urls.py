from django.template.context_processors import static
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf.urls.static import static

from cardreader.api import views
from djangoProject import settings

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('idcard/', views.idcard_view, name='id_cards'),
    path('idcard/<int:id>/', views.idcard_view, name='id_cards'),
    path('idcard/<int:id>/<int:group_id>/', views.idcard_view, name='id_cards'),
    path('idcard/base64/', views.add_idcard_base64, name='id_cards_base64'),
    path('healthcard/', views.healthcare_card_view, name='healthcare_cards'),
    path('healthcard/<int:id>/', views.healthcare_card_view, name='healthcare_card_detail'),
    path('healthcard/<int:id>/<int:group_id>/', views.healthcare_card_view, name='healthcare_card_detail'),

    path('healthcard/base64/', views.add_healthcare_card_base64, name='healthcare_cards_base64'),
    path('studentcard/', views.student_card_view, name='student_cards'),
    path('studentcard/<int:id>/', views.student_card_view, name='student_cards'),
    path('studentcard/<int:id>/<int:group_id>/', views.student_card_view, name='student_cards'),
    path('studentcard/base64/', views.add_student_card_base64, name='student_cards_base64'),
    path('groups/', views.group_view, name='create_group'),
    path('groups/<int:id>/', views.group_view, name='get_group'),
    path('groups/add_cards/<int:group_id>/', views.add_cards_to_group, name='add-cards-to-group'),
    path('invitations/', views.pending_invitations, name='pending-invitations'),
    path('invitations/<int:invitation_id>/<str:action>/', views.respond_invitation, name='respond-invitation'),
    path('invitations/<int:group_id>/', views.invite_user, name='invite-user'),
    path('b2b/', include("cardreader.api.b2b.urls")),
]
