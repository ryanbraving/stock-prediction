from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import StockPredictionSerializer
from rest_framework import status
from rest_framework.response import Response
from .tasks import train_model_task
from celery.result import AsyncResult
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
from django.conf import settings
from .utils import save_plot
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
from sklearn.metrics import mean_squared_error, r2_score
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, LSTM, Input

# Define the trained models directory
TRAINED_MODELS_DIR = 'trained_models'

def get_model_path(ticker):
    """Get model path for ticker, fallback to default if not found"""
    ticker_model = os.path.join(TRAINED_MODELS_DIR, f'{ticker}_stock_prediction_model.keras')
    default_model = os.path.join(TRAINED_MODELS_DIR, 'stock_prediction_model.keras')
    return ticker_model if os.path.exists(ticker_model) else default_model

def get_model_info(ticker):
    """Get model info for display"""
    ticker_model = os.path.join(TRAINED_MODELS_DIR, f'{ticker}_stock_prediction_model.keras')
    if os.path.exists(ticker_model):
        return f"Trained model exists for {ticker}"
    return f"Trained model doesn't exist for {ticker}, using default trained model"


class StockPredictionAPIView(APIView):
    def post(self, request):
        serializer = StockPredictionSerializer(data=request.data)
        if serializer.is_valid():
            ticker = serializer.validated_data['ticker'].upper()

            # Fetch the data from yfinance
            now = datetime.now()
            start = datetime(now.year - 10, now.month, now.day)
            end = now
            df = yf.download(ticker, start, end)
            if df.empty:
                return Response({"error": "No data found for the given ticker.",
                                 'status': status.HTTP_404_NOT_FOUND})


            df = df.reset_index()
            # Generate Basic Plot
            plt.switch_backend('AGG')
            plt.figure(figsize=(12, 5))
            plt.plot(df.Close, label='Closing Price')
            plt.title(f'Closing price of {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            # Save the plot to a file
            plot_img_path = f'{ticker}_plot.png'
            plot_img = save_plot(plot_img_path)

            # 100 Days moving average
            ma100 = df.Close.rolling(100).mean()
            plt.switch_backend('AGG')
            plt.figure(figsize=(12, 5))
            plt.plot(df.Close, label='Closing Price')
            plt.plot(ma100, 'r', label='100 DMA')
            plt.title(f'100 Days Moving Average of {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            plot_img_path = f'{ticker}_100_dma.png'
            plot_100_dma = save_plot(plot_img_path)

            # 200 Days moving average
            ma200 = df.Close.rolling(200).mean()
            plt.switch_backend('AGG')
            plt.figure(figsize=(12, 5))
            plt.plot(df.Close, label='Closing Price')
            plt.plot(ma100, 'r', label='100 DMA')
            plt.plot(ma200, 'g', label='200 DMA')
            plt.title(f'200 Days Moving Average of {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            plot_img_path = f'{ticker}_200_dma.png'
            plot_200_dma = save_plot(plot_img_path)

            # Splitting data into Training & Testing datasets
            data_training = pd.DataFrame(df.Close[0:int(len(df) * 0.7)])
            data_testing = pd.DataFrame(df.Close[int(len(df) * 0.7): int(len(df))])

            # Scaling down the data between 0 and 1
            scaler = MinMaxScaler(feature_range=(0, 1))

            # Load ML Model
            model = load_model(get_model_path(ticker))

            # Preparing Test Data
            past_100_days = data_training.tail(100)
            final_df = pd.concat([past_100_days, data_testing], ignore_index=True)
            input_data = scaler.fit_transform(final_df)

            x_test = []
            y_test = []
            for i in range(100, input_data.shape[0]):
                x_test.append(input_data[i - 100: i])
                y_test.append(input_data[i, 0])
            x_test, y_test = np.array(x_test), np.array(y_test)

            # Making Predictions
            y_predicted = model.predict(x_test)

            # Revert the scaled prices to original price
            y_predicted = scaler.inverse_transform(y_predicted.reshape(-1, 1)).flatten()
            y_test = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

            # Plot the final prediction
            plt.switch_backend('AGG')
            plt.figure(figsize=(12, 5))
            plt.plot(y_test, 'b', label='Original Price')
            plt.plot(y_predicted, 'r', label='Predicted Price')
            plt.title(f'Final Prediction for {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            plot_img_path = f'{ticker}_final_prediction.png'
            plot_prediction = save_plot(plot_img_path)

            # Model Evaluation
            # Mean Squared Error (MSE)
            mse = mean_squared_error(y_test, y_predicted)

            # Root Mean Squared Error (RMSE)
            rmse = np.sqrt(mse)

            # R-Squared
            r2 = r2_score(y_test, y_predicted)

            return Response({
                'status': 'success',
                'model_info': get_model_info(ticker),
                'plot_img': plot_img,
                'plot_100_dma': plot_100_dma,
                'plot_200_dma': plot_200_dma,
                'plot_prediction': plot_prediction,
                'model_performance': {
                    'mse': mse,
                    'rmse': rmse,
                    'r2': r2
                },
            })
        
class TrainStockModelAPIView(APIView):
    def post(self, request):
        serializer = StockPredictionSerializer(data=request.data)
        if serializer.is_valid():
            ticker = serializer.validated_data['ticker'].upper()
            
            # Start async training task
            task = train_model_task.delay(ticker)
            
            return Response({
                'status': 'training_started',
                'task_id': task.id,
                'ticker': ticker,
                'message': f'Model training started for {ticker}. Use task_id to check progress.'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StockPredictionWithPotentialEarningAPIView(APIView):
    def post(self, request):
        serializer = StockPredictionSerializer(data=request.data)
        if serializer.is_valid():
            ticker = serializer.validated_data['ticker'].upper()
            investment_amount = request.data.get('investment_amount', 1000)  # Default $1000

            # Fetch the data from yfinance
            now = datetime.now()
            start = datetime(now.year - 10, now.month, now.day)
            end = now
            df = yf.download(ticker, start, end)
            if df.empty:
                return Response({"error": "No data found for the given ticker.",
                                 'status': status.HTTP_404_NOT_FOUND})

            df = df.reset_index()
            
            # Splitting data into Training & Testing datasets
            data_training = pd.DataFrame(df.Close[0:int(len(df) * 0.7)])
            data_testing = pd.DataFrame(df.Close[int(len(df) * 0.7): int(len(df))])

            # Scaling down the data between 0 and 1
            scaler = MinMaxScaler(feature_range=(0, 1))

            # Load ML Model
            model = load_model(get_model_path(ticker))

            # Preparing Test Data
            past_100_days = data_training.tail(100)
            final_df = pd.concat([past_100_days, data_testing], ignore_index=True)
            input_data = scaler.fit_transform(final_df)

            x_test = []
            y_test = []
            for i in range(100, input_data.shape[0]):
                x_test.append(input_data[i - 100: i])
                y_test.append(input_data[i, 0])
            x_test, y_test = np.array(x_test), np.array(y_test)

            # Making Predictions
            y_predicted = model.predict(x_test)

            # Revert the scaled prices to original price
            y_predicted = scaler.inverse_transform(y_predicted.reshape(-1, 1)).flatten()
            y_test = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

            # Get current and predicted prices for recommendations
            current_price = df.Close.iloc[-1]
            predicted_future_price = y_predicted[-1]

            # Buy/Sell Signal Detection
            buy_signals = []
            sell_signals = []
            trades = []
            
            # Simple strategy: Buy when predicted price goes up, sell when it goes down
            for i in range(1, len(y_predicted)):
                price_change = y_predicted[i] - y_predicted[i-1]
                if price_change > 0 and len(buy_signals) == len(sell_signals):  # Buy signal
                    buy_signals.append({
                        'day': i,
                        'price': float(y_predicted[i-1]),
                        'action': 'BUY'
                    })
                elif price_change < 0 and len(buy_signals) > len(sell_signals):  # Sell signal
                    sell_signals.append({
                        'day': i,
                        'price': float(y_predicted[i-1]),
                        'action': 'SELL'
                    })
            
            # Calculate trading profit with realistic costs
            transaction_cost = 0.001  # 0.1% per trade
            slippage = 0.0005  # 0.05% slippage
            total_profit = 0
            current_cash = investment_amount
            total_fees = 0
            
            for i, buy in enumerate(buy_signals):
                if i < len(sell_signals):
                    sell = sell_signals[i]
                    
                    # Buy with costs
                    buy_cost = current_cash * transaction_cost
                    available_cash = current_cash - buy_cost
                    buy_price_with_slippage = buy['price'] * (1 + slippage)
                    shares_bought_trade = available_cash / buy_price_with_slippage
                    
                    # Sell with costs
                    sell_price_with_slippage = sell['price'] * (1 - slippage)
                    gross_sell_value = shares_bought_trade * sell_price_with_slippage
                    sell_cost = gross_sell_value * transaction_cost
                    net_sell_value = gross_sell_value - sell_cost
                    
                    trade_profit = net_sell_value - current_cash
                    total_profit += trade_profit
                    trade_fees = buy_cost + sell_cost
                    total_fees += trade_fees
                    
                    trades.append({
                        'buy_day': buy['day'],
                        'buy_price': buy['price'],
                        'buy_price_actual': float(buy_price_with_slippage),
                        'sell_day': sell['day'],
                        'sell_price': sell['price'],
                        'sell_price_actual': float(sell_price_with_slippage),
                        'shares': float(shares_bought_trade),
                        'gross_profit': float(gross_sell_value - available_cash),
                        'fees': float(trade_fees),
                        'net_profit': float(trade_profit),
                        'return_percentage': float((trade_profit / current_cash) * 100)
                    })
                    current_cash = net_sell_value  # Use net proceeds for next trade

            # Generate plots
            plt.switch_backend('AGG')
            plt.figure(figsize=(12, 5))
            plt.plot(df.Close, label='Closing Price')
            plt.title(f'Closing price of {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            plot_img_path = f'{ticker}_plot.png'
            plot_img = save_plot(plot_img_path)

            ma100 = df.Close.rolling(100).mean()
            plt.figure(figsize=(12, 5))
            plt.plot(df.Close, label='Closing Price')
            plt.plot(ma100, 'r', label='100 DMA')
            plt.title(f'100 Days Moving Average of {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            plot_img_path = f'{ticker}_100_dma.png'
            plot_100_dma = save_plot(plot_img_path)

            ma200 = df.Close.rolling(200).mean()
            plt.figure(figsize=(12, 5))
            plt.plot(df.Close, label='Closing Price')
            plt.plot(ma100, 'r', label='100 DMA')
            plt.plot(ma200, 'g', label='200 DMA')
            plt.title(f'200 Days Moving Average of {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            plot_img_path = f'{ticker}_200_dma.png'
            plot_200_dma = save_plot(plot_img_path)

            plt.figure(figsize=(12, 5))
            plt.plot(y_test, 'b', label='Original Price')
            plt.plot(y_predicted, 'r', label='Predicted Price')
            plt.title(f'Final Prediction for {ticker}')
            plt.xlabel('Days')
            plt.ylabel('Price')
            plt.legend()
            plot_img_path = f'{ticker}_final_prediction.png'
            plot_prediction = save_plot(plot_img_path)

            # Model Evaluation
            mse = mean_squared_error(y_test, y_predicted)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_predicted)

            # Calculate timeframe and add strategy details
            test_period_days = len(y_test)
            test_start_date = df.Date.iloc[len(data_training) + 100]  # Start of test period
            test_end_date = df.Date.iloc[-1]  # End of test period
            
            return Response({
                'status': 'success',
                'model_info': get_model_info(ticker),
                'ticker': ticker,
                'plot_img': plot_img,
                'plot_100_dma': plot_100_dma,
                'plot_200_dma': plot_200_dma,
                'plot_prediction': plot_prediction,
                'model_performance': {
                    'mse': mse,
                    'rmse': rmse,
                    'r2': r2
                },
                'trading_strategy': {
                    'investment_amount': investment_amount,
                    'current_price': float(current_price.iloc[0]),
                    'strategy_explanation': {
                        'method': 'ML Forecast-Based Trading',
                        'description': 'Buy when model predicts price will go UP tomorrow, sell when it predicts price will go DOWN tomorrow',
                        'based_on': 'LSTM neural network predictions trained on historical price patterns',
                        'timeframe': f'{test_period_days} trading days',
                        'period': f'From {test_start_date.strftime("%Y-%m-%d")} to {test_end_date.strftime("%Y-%m-%d")}',
                        'trades_per_day': f'{len(trades) / test_period_days:.1f} average'
                    },
                    'buy_signals': buy_signals,
                    'sell_signals': sell_signals,
                    'trades': trades,
                    'total_trades': len(trades),
                    'gross_trading_profit': float(total_profit + total_fees),
                    'total_fees': float(total_fees),
                    'net_trading_profit': float(total_profit),
                    'final_portfolio_value': float(current_cash),
                    'trading_return_percentage': float(((current_cash - investment_amount) / investment_amount) * 100),
                    'trading_costs': {
                        'transaction_cost_rate': f'{transaction_cost * 100}%',
                        'slippage_rate': f'{slippage * 100}%',
                        'total_fees_paid': float(total_fees)
                    }
                },
                'recommendations': {
                    'current_action': 'BUY' if predicted_future_price > current_price.iloc[0] else 'SELL',
                    'confidence': f'{abs((predicted_future_price - current_price.iloc[0]) / current_price.iloc[0] * 100):.2f}%',
                    'next_target_price': float(predicted_future_price)
                },
                'disclaimer': 'This is not financial advice. Past performance does not guarantee future results.'
            })


class TaskStatusAPIView(APIView):
    def get(self, request, task_id):
        """Check the status of a Celery task"""
        task = AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'status': 'pending',
                'message': 'Task is waiting to be processed'
            }
        elif task.state == 'PROGRESS':
            response = {
                'status': 'in_progress',
                'message': task.info.get('message', 'Task is being processed'),
                'progress': task.info.get('progress', 0)
            }
        elif task.state == 'SUCCESS':
            response = {
                'status': 'completed',
                'result': task.result
            }
        else:  # FAILURE
            response = {
                'status': 'failed',
                'error': str(task.info)
            }
        
        return Response(response)

class TrainedModelsAPIView(APIView):
    def get(self, request):
        """List all trained models by scanning the trained_models directory"""
        
        def time_ago(timestamp):
            """Convert timestamp to relative time string"""
            now = datetime.now()
            diff = now - datetime.fromtimestamp(timestamp)
            
            seconds = int(diff.total_seconds())
            if seconds < 60:
                return f"{seconds} seconds ago"
            
            minutes = seconds // 60
            if minutes < 60:
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            
            hours = minutes // 60
            if hours < 24:
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            
            days = hours // 24
            return f"{days} day{'s' if days > 1 else ''} ago"
        
        try:
            models = []
            trained_models_dir = 'trained_models'
            
            if os.path.exists(trained_models_dir):
                for filename in os.listdir(trained_models_dir):
                    if filename.endswith('_stock_prediction_model.keras'):
                        # Extract ticker from filename like "AAPL_stock_prediction_model.keras"
                        ticker = filename.split('_stock_prediction_model.keras')[0]
                        file_path = os.path.join(trained_models_dir, filename)
                        
                        # Get file modification time
                        mod_time = os.path.getmtime(file_path)
                        
                        models.append({
                            'ticker': ticker,
                            'model_path': file_path,
                            'trained_at': time_ago(mod_time),
                            'file_size': os.path.getsize(file_path),
                            'model_summary': None  # Add this for consistency
                        })
            
            # Sort by modification time (newest first)
            models.sort(key=lambda x: os.path.getmtime(os.path.join('trained_models', f"{x['ticker']}_stock_prediction_model.keras")), reverse=True)
            
            return Response({
                'status': 'success',
                'models': models,
                'count': len(models)
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'models': []
            })