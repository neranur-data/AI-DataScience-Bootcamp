from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)

# persona.csv dosyasını bu Python dosyasıyla aynı klasöre koyun.
# CSV dosyasında ilk sütun eski satır numarasıdır; index_col=0 ile indeks olarak okuyoruz.
dosya = Path(__file__).resolve().parent / "persona.csv"

df = pd.read_csv(dosya, index_col=0)
print(df.head())

# GÖREV 1 - Veri setini tanıma ve 10 soruyu yanıtlama
print('GÖREV 1')
print(df.head())
df.info()
print(df.shape)
print(df.describe(include='all'))

print('Soru 2 - SOURCE sayısı ve frekansları')
print(df['SOURCE'].nunique())
print(df['SOURCE'].value_counts())

print('Soru 3 - Farklı PRICE sayısı')
print(df['PRICE'].nunique())

print('Soru 4 - Fiyata göre satış adetleri')
print(df['PRICE'].value_counts().sort_index())

print('Soru 5 - Ülkeye göre satış adetleri')
print(df['COUNTRY'].value_counts())

print('Soru 6 - Ülkeye göre toplam gelir')
print(df.groupby('COUNTRY')['PRICE'].sum())

print('Soru 7 - Cihaz türüne göre satış adetleri')
print(df['SOURCE'].value_counts())

print('Soru 8 - Ülkeye göre ortalama fiyat')
print(df.groupby('COUNTRY')['PRICE'].mean())

print('Soru 9 - Cihaz türüne göre ortalama fiyat')
print(df.groupby('SOURCE')['PRICE'].mean())

print('Soru 10 - Ülke ve cihaz türüne göre ortalama fiyat')
print(df.groupby(['COUNTRY', 'SOURCE'])['PRICE'].mean())

# GÖREV 2 - Ülke, cihaz, cinsiyet ve yaşa göre ortalama gelir

agg_df = df.groupby(['COUNTRY', 'SOURCE', 'SEX', 'AGE']).agg({'PRICE': 'mean'})
print(agg_df.head())

# GÖREV 3 - Ortalamaları büyükten küçüğe sıralama

agg_df = agg_df.sort_values('PRICE', ascending=False)
print(agg_df.head())

# GÖREV 4 - İndeksleri normal sütunlara dönüştürme

agg_df = agg_df.reset_index()
print(agg_df.head())

# GÖREV 5 - Yaşları kategorilere ayırma

agg_df['AGE_CAT'] = pd.cut(
    agg_df['AGE'],
    bins=[-1, 18, 23, 30, 40, 70],
    labels=['0_18', '19_23', '24_30', '31_40', '41_70']
)
print(agg_df.head())

# GÖREV 6 - Müşteri persona isimlerini oluşturma ve tekilleştirme

agg_df['customers_level_based'] = (
    agg_df['COUNTRY'].str.upper() + '_' +
    agg_df['SOURCE'].str.upper() + '_' +
    agg_df['SEX'].str.upper() + '_' +
    agg_df['AGE_CAT'].astype(str)
)
agg_df = agg_df.groupby('customers_level_based', as_index=False)['PRICE'].mean()
print(agg_df.head())

# GÖREV 7 - Ortalama gelire göre dört segment oluşturma

agg_df['SEGMENT'] = pd.qcut(agg_df['PRICE'], q=4, labels=['D', 'C', 'B', 'A'])
agg_df = agg_df.sort_values('PRICE', ascending=False).reset_index(drop=True)
print(agg_df.head())
print(agg_df.groupby('SEGMENT', observed=True)['PRICE'].agg(['mean', 'max', 'sum']))

# GÖREV 8 - Örnek müşterileri bulma

# 33 yaş, Türkiye, Android, kadın -> 31_40 yaş grubu
musteri_1 = 'TUR_ANDROID_FEMALE_31_40'
print('Müşteri 1:')
print(agg_df[agg_df['customers_level_based'] == musteri_1])

# 35 yaş, Fransa, iOS, kadın -> 31_40 yaş grubu
musteri_2 = 'FRA_IOS_FEMALE_31_40'
print('Müşteri 2:')
print(agg_df[agg_df['customers_level_based'] == musteri_2])

# Sonuçları CSV dosyasına kaydetme
agg_df.to_csv('persona_segmentleri_sade.csv', index=False)
