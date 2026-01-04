from celery import shared_task
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Input
import os
import time
import sys
from datetime import datetime, timedelta

@shared_task(bind=True)
def train_model_task(self, ticker):
    """
    Celery task to train ML model for stock prediction
    """
    start_time = time.time()
    total_epochs = 50  # Define epochs as variable
    
    class ProgressCapture:
        def __init__(self, task, epochs):
            self.task = task
            self.epochs = epochs
            self.original_stdout = sys.stdout
            
        def write(self, text):
            self.original_stdout.write(text)
            if "Epoch" in text and f"/{self.epochs}" in text:
                # Parse epoch info from output like "Epoch 12/50"
                try:
                    # Extract the number before /{epochs}
                    current = int(text.split(f'/{self.epochs}')[0].split()[-1])
                    progress = int((current / self.epochs) * 100)
                    
                    self.task.update_state(
                        state='PROGRESS',
                        meta={
                            'current_epoch': current,
                            'total_epochs': self.epochs,
                            'progress': progress,
                            'message': f'Epoch {current}/{self.epochs}'
                        }
                    )
                except:
                    pass
                    
        def flush(self):
            self.original_stdout.flush()
    
    try:
        # Download stock data
        now = datetime.now()
        start = datetime(now.year - 4, now.month, now.day)
        end = now
        df = yf.download(ticker, start, end)
        df = df.reset_index()
        
        # Prepare data
        data_training = pd.DataFrame(df['Close'][0:int(len(df)*0.70)])
        scaler = MinMaxScaler(feature_range=(0,1))
        data_training_array = scaler.fit_transform(data_training)
        
        # Create training data
        x_train = []
        y_train = []
        for i in range(100, data_training_array.shape[0]):
            x_train.append(data_training_array[i-100: i])
            y_train.append(data_training_array[i, 0])
        x_train, y_train = np.array(x_train), np.array(y_train)
        
        # Build LSTM model
        model = Sequential()
        model.add(Input(shape=(x_train.shape[1], 1)))
        model.add(LSTM(units=128, activation='tanh', return_sequences=True))
        model.add(LSTM(64, return_sequences=True))
        model.add(LSTM(32))
        model.add(Dense(25))
        model.add(Dense(1))
        
        model.compile(loss='mean_squared_error', optimizer='adam')


        # Train model with stdout capture
        progress_capture = ProgressCapture(self, total_epochs)
        sys.stdout = progress_capture
        
        try:
            model.fit(x_train, y_train, epochs=total_epochs, batch_size=16, verbose=1)
        finally:
            sys.stdout = progress_capture.original_stdout

        model.summary()
        # Capture model summary
        summary_lines = []
        model.summary(print_fn=lambda x: summary_lines.append(x))
        summary_text = "\n".join(summary_lines)
        
        model_summary = {
            'raw_summary': summary_text,
            'total_params': model.count_params(),
            'trainable_params': sum([layer.count_params() for layer in model.layers if layer.trainable])
        }
        
        # Save model
        model_path = f'trained_models/{ticker}_stock_prediction_model.keras'
        model.save(model_path)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        return {
            'status': 'success',
            'message': f'Model trained successfully for {ticker}',
            'model_path': model_path,
            'elapsed_time': elapsed_time,
            'elapsed_time_formatted': f'{elapsed_time:.2f}s',
            'model_summary': model_summary
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }