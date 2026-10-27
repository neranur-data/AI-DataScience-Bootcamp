
###############################################################
# RFM ile Müşteri Segmentasyonu (Customer Segmentation with RFM)
###############################################################

###############################################################
# İş Problemi (Business Problem)
###############################################################
# FLO müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama stratejileri belirlemek istiyor.
# Buna yönelik olarak müşterilerin davranışları tanımlanacak ve bu davranış öbeklenmelerine göre gruplar oluşturulacak..

###############################################################
# Veri Seti Hikayesi
###############################################################

# Veri seti son alışverişlerini 2020 - 2021 yıllarında OmniChannel(hem online hem offline alışveriş yapan) olarak yapan müşterilerin geçmiş alışveriş davranışlarından
# elde edilen bilgilerden oluşmaktadır.

# master_id: Eşsiz müşteri numarası
# order_channel : Alışveriş yapılan platforma ait hangi kanalın kullanıldığı (Android, ios, Desktop, Mobile, Offline)
# last_order_channel : En son alışverişin yapıldığı kanal
# first_order_date : Müşterinin yaptığı ilk alışveriş tarihi
# last_order_date : Müşterinin yaptığı son alışveriş tarihi
# last_order_date_online : Muşterinin online platformda yaptığı son alışveriş tarihi
# last_order_date_offline : Muşterinin offline platformda yaptığı son alışveriş tarihi
# order_num_total_ever_online : Müşterinin online platformda yaptığı toplam alışveriş sayısı
# order_num_total_ever_offline : Müşterinin offline'da yaptığı toplam alışveriş sayısı
# customer_value_total_ever_offline : Müşterinin offline alışverişlerinde ödediği toplam ücret
# customer_value_total_ever_online : Müşterinin online alışverişlerinde ödediği toplam ücret
# interested_in_categories_12 : Müşterinin son 12 ayda alışveriş yaptığı kategorilerin listesi

###############################################################
# GÖREVLER
###############################################################

# GÖREV 1: Veriyi Anlama (Data Understanding) ve Hazırlama
           # 1. flo_data_20K.csv verisini okuyunuz.
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option("display.width", 750)

# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

df = pd.read_csv("/Users/nera/PycharmProjects/AI-DataScience-Bootcamp/Week-03-CRM-Analytics/flo_data_20k.csv")

 # 2. Veri setinde
 # a. İlk 10 gözlem,
df.head(10)
df_copy = df.copy()
 # b. Değişken isimleri,

df.columns
# c. Betimsel istatistik,
df.describe().T
# d. Boş değer,
df.isnull().sum()
 # e. Değişken tipleri, incelemesi yapınız.

df.info()
# 3. Omnichannel müşterilerin hem online'dan hemde offline platformlardan alışveriş yaptığını ifade etmektedir. Herbir müşterinin toplam
# alışveriş sayısı ve harcaması için yeni değişkenler oluşturun.

df["order_num_total"] = df["order_num_total_ever_online"] + df["order_num_total_ever_offline"]
df["customer_value_total"] = df["customer_value_total_ever_online"] + df["customer_value_total_ever_offline"]
df.head()

# 4. Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.

df["first_order_date"] = pd.to_datetime(df["first_order_date"])
df["last_order_date"] = pd.to_datetime(df["last_order_date"])
df["last_order_date_online"] = pd.to_datetime(df["last_order_date_online"])
df["last_order_date_offline"] = pd.to_datetime(df["last_order_date_offline"])

df.info()

# 5. Alışveriş kanallarındaki müşteri sayısının, ortalama alınan ürün sayısının ve ortalama harcamaların dağılımına bakınız.

 df.groupby("order_channel")["order_num_total"].sum()
 df.groupby("order_channel")["customer_value_total"].sum()

# 6. En fazla kazancı getiren ilk 10 müşteriyi sıralayınız.

top_10_customers = df.sort_values("customer_value_total", ascending=False).head(10)
print(top_10_customers[["master_id", "customer_value_total"]])

# 7. En fazla siparişi veren ilk 10 müşteriyi sıralayınız.

top_10_customers = df.sort_values("order_num_total", ascending=False).head(10)
print(top_10_customers[["master_id", "order_num_total"]])

# Step 8: Veri Ön Hazırlık Sürecini Fonksiyonlaştırma
# Amaç: Veri hazırlama işlemlerini tek bir fonksiyonda toplamak.

def prepare_rfm_data(dataframe):

    # Orijinal veri setini korumak için kopyasını oluşturuyoruz.
    df = dataframe.copy()

    # Online ve offline sipariş sayılarını toplayarak toplam sipariş sayısını hesaplıyoruz.
    df["order_num_total"] = (
        df["order_num_total_ever_online"] +
        df["order_num_total_ever_offline"]
    )

    # Online ve offline harcamaları toplayarak toplam harcamayı hesaplıyoruz.
    df["customer_value_total"] = (
        df["customer_value_total_ever_online"] +
        df["customer_value_total_ever_offline"]
    )

    # Tarih içeren sütunları belirliyoruz.
    date_columns = [
        "first_order_date",
        "last_order_date",
        "last_order_date_online",
        "last_order_date_offline"
    ]

    # Tarih sütunlarını datetime formatına dönüştürüyoruz.
    for col in date_columns:
        df[col] = pd.to_datetime(df[col])

    # Hazırlanan veri setini geri döndürüyoruz.
    return df


# Fonksiyonu başlangıçtaki veri setine uyguluyoruz.
df_prepared = prepare_rfm_data(df_copy)

# Hazırlanan veri setinin yapısını kontrol ediyoruz.
df_prepared.info()

# İlk 10 satırı görüntülüyoruz.
print(df_prepared.head(10))

##########################################
# GÖREV 2: RFM Metriklerinin Hesaplanması
############################################

# Adım 1: Analiz tarihini belirliyoruz.
# Veri setindeki en son alışveriş tarihinin bir gün sonrasını kullanıyoruz.

analysis_date = df_prepared["last_order_date"].max() + pd.Timedelta(days=1)

print("Analiz tarihi:", analysis_date)


# Adım 2: Recency değerini hesaplıyoruz.
# Müşterinin son alışverişinden analiz tarihine kadar geçen gün sayısı.

df_prepared["recency"] = (
    analysis_date - df_prepared["last_order_date"]
).dt.days


# Adım 3: RFM tablosunu oluşturuyoruz.
# Frequency toplam sipariş sayısını,
# Monetary ise toplam harcama tutarını temsil ediyor.

rfm = df_prepared[
    [
        "master_id",
        "recency",
        "order_num_total",
        "customer_value_total"
    ]
].copy()


# Adım 4: Sütun isimlerini RFM terminolojisine uygun hale getiriyoruz.

rfm.columns = [
    "customer_id",
    "recency",
    "frequency",
    "monetary"
]


# Adım 5: Oluşturduğumuz RFM tablosunu kontrol ediyoruz.

print(rfm.head(10))
print(rfm.describe().T)

###############################################################
# GÖREV 3: RF ve RFM Skorlarının Hesaplanması
###############################################################

# Adım 1: Recency, Frequency ve Monetary değerlerini
# 1 ile 5 arasında puanlara dönüştürüyoruz.

# Recency: Son alışverişi daha yakın olan müşteriler
# daha yüksek puan alır.
# Recency değeri küçükse puanı yüksek olmalıdır.

rfm["recency_score"] = pd.qcut(
    rfm["recency"],
    q=5,
    labels=[5, 4, 3, 2, 1]
)


# Frequency: Daha fazla alışveriş yapan müşteriler
# daha yüksek puan alır.
# rank(method="first") aynı sipariş sayısına sahip müşterilerin
# sıralanmasını sağlayarak qcut işlemindeki olası hataları önler.

rfm["frequency_score"] = pd.qcut(
    rfm["frequency"].rank(method="first"),
    q=5,
    labels=[1, 2, 3, 4, 5]
)


# Monetary: Daha fazla harcama yapan müşteriler
# daha yüksek puan alır.

rfm["monetary_score"] = pd.qcut(
    rfm["monetary"],
    q=5,
    labels=[1, 2, 3, 4, 5]
)


# Adım 2: Recency ve Frequency puanlarını birleştiriyoruz.
# astype(str) sayısal puanları metne dönüştürür.
# Böylece puanları toplamak yerine yan yana birleştiririz.

rfm["RF_SCORE"] = (
    rfm["recency_score"].astype(str) +
    rfm["frequency_score"].astype(str)
)


# Adım 3: Recency, Frequency ve Monetary puanlarını
# birleştirerek RFM skorunu oluşturuyoruz.

rfm["RFM_SCORE"] = (
    rfm["recency_score"].astype(str) +
    rfm["frequency_score"].astype(str) +
    rfm["monetary_score"].astype(str)
)


# Hesaplanan puanları ve skorları kontrol ediyoruz.

print(
    rfm[
        [
            "recency",
            "frequency",
            "monetary",
            "recency_score",
            "frequency_score",
            "monetary_score",
            "RF_SCORE",
            "RFM_SCORE"
        ]
    ].head(10)
)



# GÖREV 4: RF Skorlarının Segment Olarak Tanımlanması

# Adım 1: RF skorlarına karşılık gelen müşteri segmentlerini
# bir sözlük (dictionary) içerisinde tanımlıyoruz.

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}


# Adım 2: RF skorlarını ilgili müşteri segmentleriyle eşleştiriyoruz.
# map() metodu sözlükteki kurallara göre segment ataması yapar.

rfm["segment"] = rfm["RF_SCORE"].replace(
    seg_map,
    regex=True
)


# Adım 3: Segmentlere ayrılmış müşteri tablosunu kontrol ediyoruz.

print(
    rfm[
        [
            "customer_id",
            "recency_score",
            "frequency_score",
            "RF_SCORE",
            "segment"
        ]
    ].head(10)
)


# Adım 4: Her segmentte kaç müşteri olduğunu hesaplıyoruz.

segment_counts = rfm["segment"].value_counts()

print(segment_counts)

# GÖREV 5: Aksiyon zamanı!
# 1. Segmentlerin recency, frequnecy ve monetary ortalamalarını inceleyiniz.
segment_analysis = rfm.groupby("segment").agg(
    {
        "recency": "mean",
        "frequency": "mean",
        "monetary": "mean"
    }
).round(2)

# Segmentleri ortalama harcama tutarına göre sıralıyoruz.
segment_analysis = segment_analysis.sort_values(
    by="monetary",
    ascending=False
)

# Sonuçları görüntülüyoruz.
print(segment_analysis)

# 2. RFM analizi yardımıyla iki farklı kampanya için
# uygun müşterileri belirleyiniz ve müşteri ID'lerini CSV'ye kaydediniz.

# RFM segment bilgilerini ana veri setine ekliyoruz.
df_campaign = df_prepared.merge(
    rfm[["customer_id", "segment"]],
    left_on="master_id",
    right_on="customer_id",
    how="left"
)
############################
# a. FLO bünyesine yeni bir kadın ayakkabı markası dahil ediyor. Dahil ettiği markanın ürün fiyatları genel müşteri tercihlerinin üstünde. Bu nedenle markanın
# tanıtımı ve ürün satışları için ilgilenecek profildeki müşterilerle özel olarak iletişime geçeilmek isteniliyor. Sadık müşterilerinden(champions,loyal_customers),
# ortalama 250 TL üzeri ve kadın kategorisinden alışveriş yapan kişiler özel olarak iletişim kuralacak müşteriler. Bu müşterilerin id numaralarını csv dosyasına
# yeni_marka_hedef_müşteri_id.cvs olarak kaydediniz.

# Yeni kadın ayakkabı markası için hedef müşterileri belirleme
# Koşullar:
# 1. Champions veya loyal_customers segmentinde olmak.
# 2. Ortalama sipariş tutarının 250 TL üzerinde olması.
# 3. Kadın kategorisinden alışveriş yapmış olmak.

# RFM segment bilgilerini ana veri setiyle birleştiriyoruz.
df_campaign = df_prepared.merge(
    rfm[["customer_id", "segment"]],
    left_on="master_id",
    right_on="customer_id",
    how="left"
)

# Müşterilerin ortalama sipariş tutarını hesaplıyoruz.
df_campaign["average_order_value"] = (
    df_campaign["customer_value_total"] /
    df_campaign["order_num_total"]
)

# Champions veya loyal_customers segmentindeki müşterileri belirliyoruz.
loyal_condition = df_campaign["segment"].isin(
    ["champions", "loyal_customers"]
)

# Ortalama sipariş tutarı 250 TL'den yüksek olanları belirliyoruz.
spending_condition = df_campaign["average_order_value"] > 250

# Kadın kategorisinden alışveriş yapan müşterileri belirliyoruz.
women_condition = df_campaign[
    "interested_in_categories_12"
].str.contains("KADIN", case=False, na=False)

# Üç koşulu da sağlayan müşterilerin ID'lerini seçiyoruz.
new_brand_customers = df_campaign.loc[
    loyal_condition & spending_condition & women_condition,
    ["master_id"]
]

# Müşteri ID'lerini CSV dosyasına kaydediyoruz.
new_brand_customers.to_csv(
    "yeni_marka_hedef_musteri_id.csv",
    index=False
)

# Seçilen müşteri sayısını ve ilk 10 müşteriyi görüntülüyoruz.
print("Hedef müşteri sayısı:", len(new_brand_customers))
print(new_brand_customers.head(10))

#######################
# b. Erkek ve Çoçuk ürünlerinde %40'a yakın indirim planlanmaktadır. Bu indirimle ilgili kategorilerle ilgilenen geçmişte iyi müşteri olan ama uzun süredir
# alışveriş yapmayan kaybedilmemesi gereken müşteriler, uykuda olanlar ve yeni gelen müşteriler özel olarak hedef alınmak isteniliyor. Uygun profildeki müşterilerin id'lerini csv dosyasına indirim_hedef_müşteri_ids.csv
# olarak kaydediniz.
# 2B. Erkek ve çocuk ürünleri indirim kampanyası
# için hedef müşterileri belirliyoruz.

# Kaybedilmemesi gereken, uykuda olan ve yeni gelen
# müşterilerin segmentlerini seçiyoruz.

discount_segment_condition = df_campaign["segment"].isin(
    ["cant_loose", "hibernating", "new_customers"]
)

# Erkek veya çocuk kategorisiyle ilgilenen müşterileri belirliyoruz.
discount_category_condition = df_campaign[
    "interested_in_categories_12"
].str.contains("ERKEK|COCUK|ÇOCUK", case=False, na=False)

# Hem segment hem kategori koşulunu sağlayan
# müşterilerin ID numaralarını seçiyoruz.
discount_customers = df_campaign.loc[
    discount_segment_condition & discount_category_condition,
    ["master_id"]
]

# Seçilen müşteri ID'lerini CSV dosyasına kaydediyoruz.
discount_customers.to_csv(
    "indirim_hedef_musteri_ids.csv",
    index=False
)

# Hedef müşteri sayısını ve ilk 10 müşteriyi görüntülüyoruz.
print("İndirim hedef müşteri sayısı:", len(discount_customers))
print(discount_customers.head(10))


###############################################################
# GÖREV 6: Tüm Süreci Fonksiyonlaştırınız
###############################################################

def rfm_analysis(dataframe):

    # 1. VERİ ÖN HAZIRLIK

    # Orijinal veri setinin kopyasını oluşturuyoruz.
    df = dataframe.copy()

    # Toplam sipariş sayısını hesaplıyoruz.
    df["order_num_total"] = (
        df["order_num_total_ever_online"] +
        df["order_num_total_ever_offline"]
    )

    # Toplam harcama tutarını hesaplıyoruz.
    df["customer_value_total"] = (
        df["customer_value_total_ever_online"] +
        df["customer_value_total_ever_offline"]
    )

    # Tarih sütunlarını datetime formatına dönüştürüyoruz.
    date_columns = [
        "first_order_date",
        "last_order_date",
        "last_order_date_online",
        "last_order_date_offline"
    ]

    for col in date_columns:
        df[col] = pd.to_datetime(df[col])


    # 2. RFM METRİKLERİNİN HESAPLANMASI

    # Analiz tarihini belirliyoruz.
    analysis_date = df["last_order_date"].max() + pd.Timedelta(days=1)

    # Son alışverişten itibaren geçen gün sayısını hesaplıyoruz.
    df["recency"] = (
        analysis_date - df["last_order_date"]
    ).dt.days

    # RFM tablosunu oluşturuyoruz.
    rfm = df[
        [
            "master_id",
            "recency",
            "order_num_total",
            "customer_value_total"
        ]
    ].copy()

    # Sütun isimlerini düzenliyoruz.
    rfm.columns = [
        "customer_id",
        "recency",
        "frequency",
        "monetary"
    ]


    # 3. RF VE RFM SKORLARININ HESAPLANMASI

    # Recency puanını hesaplıyoruz.
    rfm["recency_score"] = pd.qcut(
        rfm["recency"],
        q=5,
        labels=[5, 4, 3, 2, 1]
    )

    # Frequency puanını hesaplıyoruz.
    rfm["frequency_score"] = pd.qcut(
        rfm["frequency"].rank(method="first"),
        q=5,
        labels=[1, 2, 3, 4, 5]
    )

    # Monetary puanını hesaplıyoruz.
    rfm["monetary_score"] = pd.qcut(
        rfm["monetary"],
        q=5,
        labels=[1, 2, 3, 4, 5]
    )

    # Recency ve Frequency puanlarını birleştiriyoruz.
    rfm["RF_SCORE"] = (
        rfm["recency_score"].astype(str) +
        rfm["frequency_score"].astype(str)
    )

    # Üç puanı birleştirerek RFM skorunu oluşturuyoruz.
    rfm["RFM_SCORE"] = (
        rfm["recency_score"].astype(str) +
        rfm["frequency_score"].astype(str) +
        rfm["monetary_score"].astype(str)
    )


    # 4. MÜŞTERİ SEGMENTASYONU

    # RF skorlarını müşteri segmentlerine eşleştiriyoruz.
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_Risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm["segment"] = rfm["RF_SCORE"].replace(
        seg_map,
        regex=True
    )


    # 5. SEGMENT ANALİZİ

    # Segmentlerin RFM ortalamalarını hesaplıyoruz.
    segment_analysis = rfm.groupby("segment").agg(
        {
            "recency": "mean",
            "frequency": "mean",
            "monetary": "mean"
        }
    ).round(2)


    # 6. KAMPANYALAR İÇİN VERİ HAZIRLAMA

    # Segment bilgilerini ana veri setine ekliyoruz.
    df_campaign = df.merge(
        rfm[["customer_id", "segment"]],
        left_on="master_id",
        right_on="customer_id",
        how="left"
    )

    # Ortalama sipariş tutarını hesaplıyoruz.
    df_campaign["average_order_value"] = (
        df_campaign["customer_value_total"] /
        df_campaign["order_num_total"]
    )


    # 7. YENİ KADIN AYAKKABI MARKASI KAMPANYASI

    # Sadık müşteri koşulunu oluşturuyoruz.
    loyal_condition = df_campaign["segment"].isin(
        ["champions", "loyal_customers"]
    )

    # Ortalama sipariş tutarı koşulunu oluşturuyoruz.
    spending_condition = df_campaign["average_order_value"] > 250

    # Kadın kategorisi koşulunu oluşturuyoruz.
    women_condition = df_campaign[
        "interested_in_categories_12"
    ].str.contains("KADIN", case=False, na=False)

    # Koşulları sağlayan müşterileri seçiyoruz.
    new_brand_customers = df_campaign.loc[
        loyal_condition & spending_condition & women_condition,
        ["master_id"]
    ]

    # Müşteri ID'lerini CSV dosyasına kaydediyoruz.
    new_brand_customers.to_csv(
        "yeni_marka_hedef_musteri_id.csv",
        index=False
    )


    # 8. ERKEK VE ÇOCUK İNDİRİM KAMPANYASI

    # Hedef müşteri segmentlerini belirliyoruz.
    discount_segment_condition = df_campaign["segment"].isin(
        ["cant_loose", "hibernating", "new_customers"]
    )

    # Erkek veya çocuk kategorisi koşulunu oluşturuyoruz.
    discount_category_condition = df_campaign[
        "interested_in_categories_12"
    ].str.contains("ERKEK|COCUK|ÇOCUK", case=False, na=False)

    # Koşulları sağlayan müşterileri seçiyoruz.
    discount_customers = df_campaign.loc[
        discount_segment_condition & discount_category_condition,
        ["master_id"]
    ]

    # Müşteri ID'lerini CSV dosyasına kaydediyoruz.
    discount_customers.to_csv(
        "indirim_hedef_musteri_ids.csv",
        index=False
    )


    # 9. SONUÇLARI GERİ DÖNDÜRME

    # Analiz tablolarını ve hedef müşteri listelerini döndürüyoruz.
    return rfm, segment_analysis, new_brand_customers, discount_customers


# Fonksiyonu başlangıçtaki veri seti üzerinde çalıştırıyoruz.
rfm_result, segment_summary, brand_targets, discount_targets = rfm_analysis(df_copy)


# Sonuçları kontrol ediyoruz.
print("RFM Analiz Sonuçları:")
print(rfm_result.head())

print("\nSegment Ortalamaları:")
print(segment_summary)

print("\nYeni Marka Hedef Müşteri Sayısı:", len(brand_targets))
print("İndirim Hedef Müşteri Sayısı:", len(discount_targets))

