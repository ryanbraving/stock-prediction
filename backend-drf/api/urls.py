from django.urls import path
from accounts import views as UserViews
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.views import TokenVerifyView
from .views import StockPredictionAPIView, TrainStockModelAPIView, StockPredictionWithPotentialEarningAPIView


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('register/', UserViews.RegisterView.as_view()),
    path('protected-view/', UserViews.protected_view.as_view()),

    # Prediction API
    path('predict/', StockPredictionAPIView.as_view(), name='stock_prediction'),
    # path('predict-earnings/', StockPredictionWithPotentialEarningAPIView.as_view(), name='stock_prediction_earnings'),
    # Train model API
    path('train/', TrainStockModelAPIView.as_view(), name='train_model'),

]
