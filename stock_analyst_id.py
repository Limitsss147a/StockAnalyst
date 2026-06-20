import argparse
import pandas as pd
import numpy as np

def analyze_stock(symbol, csv_path):
    print(f"Menganalisis saham {symbol} dari {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
        if 'date' not in df.columns or 'close' not in df.columns:
            print("Error: CSV harus memiliki kolom 'date' dan 'close'")
            return
            
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        if len(df) < 2:
            print("Data tidak cukup untuk analisis.")
            return
            
        first_price = df['close'].iloc[0]
        last_price = df['close'].iloc[-1]
        pct_change = ((last_price - first_price) / first_price) * 100
        
        print(f"\n--- HASIL ANALISIS {symbol} ---")
        print(f"Harga Awal  : {first_price}")
        print(f"Harga Akhir : {last_price}")
        print(f"Perubahan   : {pct_change:+.2f}%")
        
        # Simple Moving Averages
        if len(df) >= 20:
            sma20 = df['close'].rolling(20).mean().iloc[-1]
            print(f"SMA 20      : {sma20:.2f}")
        if len(df) >= 50:
            sma50 = df['close'].rolling(50).mean().iloc[-1]
            print(f"SMA 50      : {sma50:.2f}")
            
    except Exception as e:
        print(f"Terjadi kesalahan saat membaca CSV: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple CLI app to analyze Indonesian stock market prices from CSV data.")
    parser.add_argument("--symbol", required=True, help="IDX Symbol (e.g. BBCA.JK)")
    parser.add_argument("--csv", required=True, help="Path to prices CSV file")
    
    args = parser.parse_args()
    analyze_stock(args.symbol, args.csv)
