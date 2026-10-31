import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def load_data(file_path):
    """
    Tahap Extract: Membaca dataset dari folder data/raw/
    """
    print("=" * 60)
    print("1. EXTRACT / LOAD DATA")
    print("=" * 60)
    print(f"Membaca dataset dari: {file_path}")
    df = pd.read_csv(file_path)
    print("Data berhasil dimuat!")
    print("-" * 50)
    return df

def inspect_data(df):
    """
    Pemeriksaan awal kondisi dataset (Task B)
    """
    print("=" * 60)
    print("2. DATA INSPECTION (Task B)")
    print("=" * 60)
    
    print("melihat 5 data teratas csv")
    print(df.head())
    print("-" * 50)

    print("melihat total baris dan kolom CSV")
    print(df.shape)
    print("-" * 50)

    print("Melihat header kolom")
    print(df.columns.tolist())
    print("-" * 50)

    print("melihat tipe data tiap kolom")
    print(df.dtypes)
    print("-" * 50)

    print("melihat missing value di masing-masing kolom:")
    missing_per_col = df.isnull().sum()
    print(missing_per_col[missing_per_col > 0])
    print("\nmelihat total missing value di seluruh kolom:")
    print(df.isnull().sum().sum())
    print("-" * 50)

    print("total data duplikat:", df.duplicated().sum())
    print("-" * 50)

    print("melihat nilai unik dari masing-masing kolom kategorikal:")
    categori = df.select_dtypes(include="object").columns
    for data in categori:
        print(f"\nKolom: {data}")
        print("Nilai unik:")
        print(df[data].unique().tolist())
        print("-" * 50)

    return df

def clean_data(df):
    """
    Tahap Transform - Data Cleaning (Task C)
    """
    print("=" * 60)
    print("3. DATA CLEANING (Task C)")
    print("=" * 60)
    
    df_clean = df.copy()
    
    total_data_awal = len(df_clean)
    missing_awal = df_clean.isnull().sum().sum()
    
    # 1. Menghapus data duplikat
    dup_count = df_clean.duplicated().sum()
    df_clean = df_clean.drop_duplicates().reset_index(drop=True)
    print(f"Jumlah baris terduplikasi yang dihapus: {dup_count}")
    
    # 2. Menyeragamkan penulisan data kategorikal dan menghapus spasi yang tidak diperlukan
    str_cols = ['make', 'aspiration', 'body-style', 'drive-wheels', 'engine-location', 'engine-type', 'fuel-system']
    for col in str_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip().str.lower()
        
    # Drive-wheels: standardisasi penulisan agar seragam (AWD diseragamkan ke 4wd)
    df_clean['drive-wheels'] = df_clean['drive-wheels'].replace({'awd': '4wd'})

    # 3. Menyeragamkan format tanggal transaction_date
    df_clean['transaction_date'] = pd.to_datetime(df_clean['transaction_date'], dayfirst=True, format='mixed')
    # Mengisi tanggal kosong dengan metode forward fill lalu backward fill
    df_clean['transaction_date'] = df_clean['transaction_date'].ffill().bfill()
    df_clean['transaction_date'] = df_clean['transaction_date'].dt.strftime('%Y-%m-%d')
    
    # 4. Menangani missing values pada kolom kategorikal
    # make diisi dengan modus
    df_clean['make'] = df_clean['make'].replace('nan', np.nan).fillna(df_clean['make'].mode()[0])
    
    # num-of-doors diisi modus ('four' karena mayoritas sedan berpintu 4)
    df_clean['num-of-doors'] = df_clean['num-of-doors'].fillna('four')
    
    # horsepower-binned diisi dengan modus
    df_clean['horsepower-binned'] = df_clean['horsepower-binned'].fillna(df_clean['horsepower-binned'].mode()[0])
    
    # 5. Menangani missing values pada kolom numerik
    # stroke diisi nilai mean
    df_clean['stroke'] = df_clean['stroke'].fillna(df_clean['stroke'].mean())
    
    # horsepower dan price diisi nilai median
    df_clean['horsepower'] = df_clean['horsepower'].fillna(df_clean['horsepower'].median())
    df_clean['price'] = df_clean['price'].fillna(df_clean['price'].median())
    
    # 6. Memperbaiki tipe data num-of-doors
    # Tipe data teks 'two' dan 'four' diubah menjadi integer
    door_int_map = {'two': 2, 'four': 4}
    df_clean['num-of-doors_int'] = df_clean['num-of-doors'].map(door_int_map).astype(int)
    
    total_data_akhir = len(df_clean)
    missing_akhir = df_clean.isnull().sum().sum()
    
    print(f"Jumlah data sebelum cleaning: {total_data_awal} baris")
    print(f"Jumlah data sesudah cleaning: {total_data_akhir} baris")
    print(f"Jumlah missing values sebelum cleaning: {missing_awal}")
    print(f"Jumlah missing values sesudah cleaning: {missing_akhir}")
    print("Kolom yang mengalami perubahan / pembersihan:")
    changed_cols = ['make', 'body-style', 'drive-wheels', 'fuel-system', 'transaction_date', 'num-of-doors', 'stroke', 'horsepower', 'price', 'horsepower-binned']
    print(changed_cols)
    print("-" * 50)
    
    return df_clean

def transform_data(df_clean):
    """
    Tahap Transform - Data Transformation (Task D)
    """
    print("=" * 60)
    print("4. DATA TRANSFORMATION (Task D)")
    print("=" * 60)
    
    df_transformed = df_clean.copy()
    
    # Mapping fitur num-of-doors menjadi skala biner / rasio
    door_map = {'two': 0.0, 'four': 1.0}
    df_transformed['num-of-doors'] = df_clean['num-of-doors'].map(door_map).fillna(1.0)
    if 'num-of-doors_int' in df_transformed.columns:
        df_transformed = df_transformed.drop(columns=['num-of-doors_int'])

    # num-of-cylinders: ubah nama angka ke numerik lalu lakukan min-max scaling
    cyl_map = {'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'eight': 8, 'twelve': 12}
    df_transformed['num-of-cylinders'] = df_transformed['num-of-cylinders'].map(cyl_map)
    df_transformed['num-of-cylinders'] = (df_transformed['num-of-cylinders'] - 2) / (12 - 2)

    # horsepower_ordinal: ordinal encoding untuk horsepower-binned (Low=0, Medium=1, High=2)
    hp_map = {'low': 0, 'medium': 1, 'high': 2, 'Low': 0, 'Medium': 1, 'High': 2}
    df_transformed['horsepower_ordinal'] = df_transformed['horsepower-binned'].map(hp_map).fillna(0).astype(int)

    # make_freq: frequency encoding untuk make
    make_freq = df_transformed['make'].value_counts(normalize=True)
    df_transformed['make_freq'] = df_transformed['make'].map(make_freq)

    # Min-Max Scaling pada kolom numerik
    scale_cols = ['symboling', 'curb-weight', 'engine-size', 'horsepower', 'peak-rpm', 'city-mpg', 'highway-mpg', 'price']
    scaler = MinMaxScaler()
    df_transformed[scale_cols] = scaler.fit_transform(df_transformed[scale_cols])

    # One-Hot Encoding pada kolom kategorikal nominal
    ohe_cols = ['body-style', 'drive-wheels', 'aspiration', 'engine-type', 'engine-location', 'fuel-system']
    df_transformed = pd.get_dummies(df_transformed, columns=ohe_cols, dtype=int)

    # Drop kolom mentah yang sudah terwakili oleh hasil transformasi
    drop_cols = ['transaction_date', 'horsepower-binned', 'make']
    df_transformed = df_transformed.drop(columns=[c for c in drop_cols if c in df_transformed.columns])

    print(f"Dimensi data setelah transformasi: {df_transformed.shape[0]} baris x {df_transformed.shape[1]} kolom")
    print("Kolom hasil transformasi:")
    print(f"- Min-Max Scaling: {scale_cols}")
    print("- Ordinal Encoding: ['horsepower_ordinal']")
    print("- Frequency Encoding: ['make_freq']")
    print(f"- One-Hot Encoding: {ohe_cols}")
    print("-" * 50)
    
    return df_transformed

def save_data(df, output_path):
    """
    Tahap Load: Menyimpan processed dataset ke folder data/processed/
    """
    print("=" * 60)
    print("5. LOAD / SAVE PROCESSED DATA (Task F)")
    print("=" * 60)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Dataset berhasil disimpan ke: {output_path}")
    print(f"Ukuran file: {df.shape[0]} baris x {df.shape[1]} kolom")
    print("=" * 60)

def run_pipeline(input_path="data/raw/automobileEDA_dirty_training.csv", output_path="data/processed/automobileEDA_processed.csv"):
    """
    Fungsi penggabung seluruh alur ETL dari awal hingga akhir
    """
    print("\n" + "#" * 60)
    print(" MEMULAI AUTOMOBILE DATA PIPELINE (ETL)")
    print("#" * 60 + "\n")
    
    # 1. Extract
    df_raw = load_data(input_path)
    
    # 2. Inspect (Task B)
    inspect_data(df_raw)
    
    # 3. Clean (Task C)
    df_clean = clean_data(df_raw)
    
    # 4. Transform (Task D)
    df_proc = transform_data(df_clean)
    
    # 5. Load (Task F)
    save_data(df_proc, output_path)
    
    print("\n" + "#" * 60)
    print(" PIPELINE BERHASIL DIJALANKAN DENGAN SUKSES!")
    print("#" * 60 + "\n")

if __name__ == "__main__":
    run_pipeline()
