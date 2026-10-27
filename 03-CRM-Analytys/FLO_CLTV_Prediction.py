##############################################################
# BG-NBD ve Gamma-Gamma ile CLTV Prediction
#Bir müşteri önümüzdeki 6 ay boyunca FLO'ya tahminen ne kadar gelir sağlayacak?
#Buna CLTV (Customer Lifetime Value – Müşteri Yaşam Boyu Değeri) tahmini diyoruz
##############################################################
#RFM ile CLTV arasındaki fark
#RFM analizinde: Müşterinin geçmiş alışverişlerine bakarak ne kadar aktif ve değerli olduğunu belirledik.

#CLTV Prediction'da: Geçmiş alışveriş davranışlarından yararlanarak gelecekteki alışveriş sayısını ve harcama değerini tahmin edeceğiz.
#BG/NBD: Müşteri gelecekte kaç kez alışveriş yapabilir?
#Gamma-Gamma: Müşteri bir alışverişte ortalama ne kadar harcayabilir?

###############################################################
# İş Problemi (Business Problem)
###############################################################
# FLO satış ve pazarlama faaliyetleri için roadmap belirlemek istemektedir.
# Şirketin orta uzun vadeli plan yapabilmesi için var olan müşterilerin gelecekte şirkete sağlayacakları potansiyel değerin tahmin edilmesi gerekmektedir.


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
# GÖREV 1: Veriyi Hazırlama
           # 1. flo_data_20K.csv verisini okuyunuz.Dataframe’in kopyasını oluşturunuz.
import pandas as pd
pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)
df = pd.read_csv("/Users/nera/PycharmProjects/AI-DataScience-Bootcamp/Week-03-CRM-Analytics/flo_data_20k.csv")
df_copy = df.copy()

print(df_copy.head())
print(df_copy.shape)
           # 2. Aykırı değerleri baskılamak için gerekli olan outlier_thresholds ve replace_with_thresholds fonksiyonlarını tanımlayınız.
           # Not: cltv hesaplanırken frequency değerleri integer olması gerekmektedir.Bu nedenle alt ve üst limitlerini round() ile yuvarlayınız.
def outlier_thresholds(dataframe, variable):

    # Değişkenin %1 ve %99'luk çeyreklik değerlerini hesaplıyoruz.
    quartile1 = dataframe[variable].quantile(0.01)
    quartile3 = dataframe[variable].quantile(0.99)

    # Çeyreklikler arasındaki farkı hesaplıyoruz.
    interquantile_range = quartile3 - quartile1

    # Alt ve üst sınırları belirliyoruz.
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range

    # CLTV analizinde Frequency tam sayı olmalıdır.
    # Bu nedenle sınırları en yakın tam sayıya yuvarlıyoruz.
    return round(low_limit), round(up_limit)


# Aykırı değerleri belirlenen sınırlarla değiştiren fonksiyon.
def replace_with_thresholds(dataframe, variable):

    # Önce alt ve üst sınırları hesaplıyoruz.
    low_limit, up_limit = outlier_thresholds(dataframe, variable)

    # Alt sınırın altındaki değerleri alt sınırla değiştiriyoruz.
    dataframe.loc[
        dataframe[variable] < low_limit, variable
    ] = low_limit

    # Üst sınırın üzerindeki değerleri üst sınırla değiştiriyoruz.
    dataframe.loc[
        dataframe[variable] > up_limit, variable
    ] = up_limit


           # 3. "order_num_total_ever_online","order_num_total_ever_offline","customer_value_total_ever_offline","customer_value_total_ever_online" değişkenlerinin
           # aykırı değerleri varsa baskılayanız.
    outlier_columns = [
        "order_num_total_ever_online",
        "order_num_total_ever_offline",
        "customer_value_total_ever_offline",
        "customer_value_total_ever_online"
    ]

    # Her sütun için alt ve üst sınırları hesaplayıp
    # aykırı değerleri bu sınırlarla değiştiriyoruz.
    for col in outlier_columns:
        replace_with_thresholds(df_copy, col)

    # Baskılama sonrası değişkenlerin istatistiklerini inceliyoruz.
    print(df_copy[outlier_columns].describe())

    # Baskılama sonrası aykırı değer kontrolü yapıyoruz.
    for col in outlier_columns:
        low_limit, up_limit = outlier_thresholds(df_copy, col)

        outlier_count = (
                (df_copy[col] < low_limit) |
                (df_copy[col] > up_limit)
        ).sum()

        print(col, "-> Aykırı değer sayısı:", outlier_count)

           # 4. Omnichannel müşterilerin hem online'dan hemde offline platformlardan alışveriş yaptığını ifade etmektedir. Herbir müşterinin toplam
           # alışveriş sayısı ve harcaması için yeni değişkenler oluşturun.
        # Online ve offline sipariş sayılarını topluyoruz.
        df_copy["order_num_total"] = (
                df_copy["order_num_total_ever_online"] +
                df_copy["order_num_total_ever_offline"]
        )

        # Online ve offline harcama tutarlarını topluyoruz.
        df_copy["customer_value_total"] = (
                df_copy["customer_value_total_ever_online"] +
                df_copy["customer_value_total_ever_offline"]
        )

        # Oluşturduğumuz yeni sütunları kontrol ediyoruz.
        print(df_copy[["order_num_total", "customer_value_total"]].head())
        print(df_copy.shape)

           # 5. Değişken tiplerini inceleyiniz. Tarih ifade eden değişkenlerin tipini date'e çeviriniz.
# Sütunların mevcut veri tiplerini kontrol ediyoruz.
print(df_copy.dtypes)

# Tarih içeren sütunları belirliyoruz.
date_columns = [
    "first_order_date",
    "last_order_date",
    "last_order_date_online",
    "last_order_date_offline"
]

# Tarih sütunlarını datetime tipine dönüştürüyoruz.
for col in date_columns:
    df_copy[col] = pd.to_datetime(df_copy[col])

# Dönüşüm sonrası veri tiplerini tekrar kontrol ediyoruz.
print(df_copy[date_columns].dtypes)

###############################################################
# GÖREV 2: CLTV Veri Yapısının Oluşturulması
###############################################################

# 1. Son alışveriş tarihinden 2 gün sonrasını analiz tarihi olarak belirliyoruz.

analysis_date = df_copy["last_order_date"].max() + pd.Timedelta(days=2)

print("Analiz tarihi:", analysis_date)

# 2. CLTV hesaplamasında kullanılacak yeni DataFrame'i oluşturuyoruz.

cltv = pd.DataFrame()

# Müşteri kimliklerini ekliyoruz.
cltv["customer_id"] = df_copy["master_id"]

# İlk ve son alışveriş arasındaki süreyi hafta olarak hesaplıyoruz.
cltv["recency_cltv_weekly"] = (
    (df_copy["last_order_date"] - df_copy["first_order_date"]).dt.days / 7
)

# İlk alışverişten analiz tarihine kadar geçen süreyi hafta olarak hesaplıyoruz.
cltv["T_weekly"] = (
    (analysis_date - df_copy["first_order_date"]).dt.days / 7
)

# Müşterinin toplam alışveriş sayısını ekliyoruz.
cltv["frequency"] = df_copy["order_num_total"].astype(int)

# Alışveriş başına ortalama harcamayı hesaplıyoruz.
cltv["monetary_cltv_avg"] = (
    df_copy["customer_value_total"] / df_copy["order_num_total"]
)

# İlk 5 satırı görüntülüyoruz.
print(cltv.head())
# CLTV DataFrame'inin boyutunu ve veri tiplerini kontrol ediyoruz.
print(cltv.shape)
print(cltv.dtypes)

# GÖREV 3: BG/NBD, Gamma-Gamma Modellerinin Kurulması, CLTV'nin hesaplanması
###############################################################

# 1. BG/NBD modelini kuruyoruz.

from lifetimes import BetaGeoFitter

# BG/NBD modelini oluşturuyoruz.
bgf = BetaGeoFitter(penalizer_coef=0.001)

# Modeli geçmiş müşteri verileriyle eğitiyoruz.
bgf.fit(
    cltv["frequency"],
    cltv["recency_cltv_weekly"],
    cltv["T_weekly"]
)

# a. Önümüzdeki 3 ay için beklenen satın alma sayısını tahmin ediyoruz.
cltv["exp_sales_3_month"] = bgf.predict(
    4 * 3,
    cltv["frequency"],
    cltv["recency_cltv_weekly"],
    cltv["T_weekly"]
)

# b. Önümüzdeki 6 ay için beklenen satın alma sayısını tahmin ediyoruz.
cltv["exp_sales_6_month"] = bgf.predict(
    4 * 6,
    cltv["frequency"],
    cltv["recency_cltv_weekly"],
    cltv["T_weekly"]
)

# Tahmin sonuçlarını inceliyoruz.
print(cltv[[
    "customer_id",
    "exp_sales_3_month",
    "exp_sales_6_month"
]].head())
# 3 ayda en çok alışveriş yapması beklenen 10 müşteri.
print(cltv.sort_values(
    "exp_sales_3_month", ascending=False
).head(10))

# 6 ayda en çok alışveriş yapması beklenen 10 müşteri.
print(cltv.sort_values(
    "exp_sales_6_month", ascending=False
).head(10))
           # 2. Gamma-Gamma modelini fit ediniz. Müşterilerin ortalama bırakacakları değeri tahminleyip exp_average_value olarak cltv dataframe'ine ekleyiniz.

# 2. Gamma-Gamma modelini kuruyoruz.
# Müşterilerin beklenen ortalama alışveriş tutarını tahmin ediyoruz.

from lifetimes import GammaGammaFitter

# Gamma-Gamma modelini oluşturuyoruz.
ggf = GammaGammaFitter(penalizer_coef=0.01)

# Modeli geçmiş müşteri verileriyle eğitiyoruz.
ggf.fit(
    cltv["frequency"],
    cltv["monetary_cltv_avg"]
)

# Her müşterinin beklenen ortalama alışveriş tutarını hesaplıyoruz.
cltv["exp_average_value"] = ggf.conditional_expected_average_profit(
    cltv["frequency"],
    cltv["monetary_cltv_avg"]
)

# İlk 5 müşterinin sonuçlarını inceliyoruz.
print(cltv[[
    "customer_id",
    "frequency",
    "monetary_cltv_avg",
    "exp_average_value"
]].head())
           # 3. 6 aylık CLTV hesaplayınız ve cltv ismiyle dataframe'e ekleyiniz.
# 3. Müşterilerin 6 aylık CLTV değerlerini hesaplıyoruz.

# BG/NBD ve Gamma-Gamma modellerini kullanarak CLTV hesaplıyoruz.
cltv["cltv"] = ggf.customer_lifetime_value(
    bgf,
    cltv["frequency"],
    cltv["recency_cltv_weekly"],
    cltv["T_weekly"],
    cltv["monetary_cltv_avg"],
    time=6,
    freq="W",
    discount_rate=0.01
)

# b CLTV değeri en yüksek 20 müşteriyi görüntülüyoruz.
print(cltv.sort_values("cltv", ascending=False).head(20))


###############################################################
# GÖREV 4: CLTV'ye Göre Segmentlerin Oluşturulması
###############################################################

# 1. Müşterileri 6 aylık CLTV değerlerine göre 4 segmente ayırıyoruz.

cltv["cltv_segment"] = pd.qcut(
    cltv["cltv"],
    q=4,
    labels=["D", "C", "B", "A"]
)

# Segmentlerdeki müşteri sayılarını inceliyoruz.
print(cltv["cltv_segment"].value_counts())

# Her segmentin ortalama değerlerini inceliyoruz.
segment_summary = cltv.groupby(
    "cltv_segment", observed=True
).agg({
    "recency_cltv_weekly": "mean",
    "T_weekly": "mean",
    "frequency": "mean",
    "monetary_cltv_avg": "mean",
    "cltv": "mean"
})

print(segment_summary)
###############################################################
# BONUS: Tüm Süreci Fonksiyonlaştırma
###############################################################

import pandas as pd
from lifetimes import BetaGeoFitter, GammaGammaFitter


def cltv_prediction(dataframe):

    # Orijinal veriyi korumak için kopyasını oluşturuyoruz.
    df = dataframe.copy()

    ###########################################################
    # GÖREV 1: Veriyi Hazırlama
    ###########################################################

    # 1. Aykırı değerlerin alt ve üst sınırlarını hesaplıyoruz.
    def outlier_thresholds(dataframe, variable):

        quartile1 = dataframe[variable].quantile(0.01)
        quartile3 = dataframe[variable].quantile(0.99)

        interquantile_range = quartile3 - quartile1

        up_limit = quartile3 + 1.5 * interquantile_range
        low_limit = quartile1 - 1.5 * interquantile_range

        return round(low_limit), round(up_limit)

    # 2. Aykırı değerleri sınır değerleriyle değiştiriyoruz.
    def replace_with_thresholds(dataframe, variable):

        low_limit, up_limit = outlier_thresholds(dataframe, variable)

        dataframe.loc[
            dataframe[variable] < low_limit, variable
        ] = low_limit

        dataframe.loc[
            dataframe[variable] > up_limit, variable
        ] = up_limit

    # 3. Aykırı değerleri baskılayacağımız sütunları belirliyoruz.
    outlier_columns = [
        "order_num_total_ever_online",
        "order_num_total_ever_offline",
        "customer_value_total_ever_offline",
        "customer_value_total_ever_online"
    ]

    for col in outlier_columns:
        replace_with_thresholds(df, col)

    # 4. Toplam alışveriş sayısını hesaplıyoruz.
    df["order_num_total"] = (
        df["order_num_total_ever_online"] +
        df["order_num_total_ever_offline"]
    )

    # Toplam harcama tutarını hesaplıyoruz.
    df["customer_value_total"] = (
        df["customer_value_total_ever_online"] +
        df["customer_value_total_ever_offline"]
    )

    # 5. Tarih sütunlarını datetime tipine dönüştürüyoruz.
    date_columns = [
        "first_order_date",
        "last_order_date",
        "last_order_date_online",
        "last_order_date_offline"
    ]

    for col in date_columns:
        df[col] = pd.to_datetime(df[col])

    ###########################################################
    # GÖREV 2: CLTV Veri Yapısının Oluşturulması
    ###########################################################

    # Analiz tarihini belirliyoruz.
    analysis_date = df["last_order_date"].max() + pd.Timedelta(days=2)

    # CLTV DataFrame'ini oluşturuyoruz.
    cltv = pd.DataFrame()

    cltv["customer_id"] = df["master_id"]

    cltv["recency_cltv_weekly"] = (
        (df["last_order_date"] - df["first_order_date"]).dt.days / 7
    )

    cltv["T_weekly"] = (
        (analysis_date - df["first_order_date"]).dt.days / 7
    )

    cltv["frequency"] = df["order_num_total"].astype(int)

    cltv["monetary_cltv_avg"] = (
        df["customer_value_total"] / df["order_num_total"]
    )

    ###########################################################
    # GÖREV 3: BG/NBD ve Gamma-Gamma Modelleri
    ###########################################################

    # BG/NBD modelini oluşturuyor ve eğitiyoruz.
    bgf = BetaGeoFitter(penalizer_coef=0.001)

    bgf.fit(
        cltv["frequency"],
        cltv["recency_cltv_weekly"],
        cltv["T_weekly"]
    )

    # 3 aylık beklenen alışveriş sayısını tahmin ediyoruz.
    cltv["exp_sales_3_month"] = bgf.predict(
        4 * 3,
        cltv["frequency"],
        cltv["recency_cltv_weekly"],
        cltv["T_weekly"]
    )

    # 6 aylık beklenen alışveriş sayısını tahmin ediyoruz.
    cltv["exp_sales_6_month"] = bgf.predict(
        4 * 6,
        cltv["frequency"],
        cltv["recency_cltv_weekly"],
        cltv["T_weekly"]
    )

    # Gamma-Gamma modelini oluşturuyor ve eğitiyoruz.
    ggf = GammaGammaFitter(penalizer_coef=0.01)

    ggf.fit(
        cltv["frequency"],
        cltv["monetary_cltv_avg"]
    )

    # Beklenen ortalama alışveriş tutarını hesaplıyoruz.
    cltv["exp_average_value"] = (
        ggf.conditional_expected_average_profit(
            cltv["frequency"],
            cltv["monetary_cltv_avg"]
        )
    )

    # 6 aylık CLTV değerini hesaplıyoruz.
    cltv["cltv"] = ggf.customer_lifetime_value(
        bgf,
        cltv["frequency"],
        cltv["recency_cltv_weekly"],
        cltv["T_weekly"],
        cltv["monetary_cltv_avg"],
        time=6,
        freq="W",
        discount_rate=0.01
    )

    ###########################################################
    # GÖREV 4: CLTV Segmentlerinin Oluşturulması
    ###########################################################

    # Müşterileri CLTV değerlerine göre 4 gruba ayırıyoruz.
    cltv["cltv_segment"] = pd.qcut(
        cltv["cltv"],
        q=4,
        labels=["D", "C", "B", "A"]
    )

    # Segmentlerin ortalama değerlerini hesaplıyoruz.
    segment_summary = cltv.groupby(
        "cltv_segment", observed=True
    ).agg({
        "recency_cltv_weekly": "mean",
        "T_weekly": "mean",
        "frequency": "mean",
        "monetary_cltv_avg": "mean",
        "cltv": "mean"
    })

    # Sonuçları döndürüyoruz.
    return cltv, segment_summary

# Orijinal CSV dosyasını okuyoruz.
df = pd.read_csv("/Users/nera/PycharmProjects/AI-DataScience-Bootcamp/Week-03-CRM-Analytics/flo_data_20k.csv")

# Fonksiyonu çalıştırıyoruz.
cltv_result, segment_summary = cltv_prediction(df)

# CLTV değeri en yüksek 20 müşteriyi görüntülüyoruz.
print(cltv_result.sort_values("cltv", ascending=False).head(20))

# Segmentlerin özet istatistiklerini görüntülüyoruz.
print(segment_summary)


