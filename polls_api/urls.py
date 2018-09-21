from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'question', views.QuestionViewSet)

urlpatterns = router.urls
