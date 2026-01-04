from django.urls import path
from accounts import views as UserViews
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenVerifyView
from .views import StockPredictionAPIView, TrainStockModelAPIView, StockPredictionWithPotentialEarningAPIView, TaskStatusAPIView, TrainedModelsAPIView


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('register/', UserViews.RegisterView.as_view()),
    path('protected-view/', UserViews.protected_view.as_view()),

    # Forecast API
    path('forecast/', StockPredictionWithPotentialEarningAPIView.as_view(), name='stock_prediction'),
    # Train model API
    path('train/', TrainStockModelAPIView.as_view(), name='train_model'),
    # Task status API
    path('task-status/<str:task_id>/', TaskStatusAPIView.as_view(), name='task_status'),
    # Trained models API
    path('trained-models/', TrainedModelsAPIView.as_view(), name='trained_models'),

]
