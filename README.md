# Performance Race (Görev 2.3)

Bu proje, 5 milyon satırlık bir log dosyasında belirli bir koşulu (örn: `/api/v1/orders` içeren satırları sayma) ararken 4 farklı Python yönteminin süre ve bellek tüketimlerini karşılaştırmak için hazırlanmıştır.

## 📊 Performans Karşılaştırma Tablosu

| Yöntem | Süre (Saniye) | Tepe Bellek (MB) |
| :--- | :--- | :--- |
| **(d) Polars** | 0.70s | 0.16 MB |
| **(b) Generator** | 3.90s | 0.15 MB |
| **(a) Naif Satır Döngüsü** | 5.00s | 501.71 MB |
| **(c) Multiprocessing** | 22.75s | 101.11 MB |

## 🧠 Yöntemler Neden Farklı Sonuçlar Verdi?

1. **Polars (En Hızlı Yöntem):** 
Arka planda tamamen Rust tabanlı, son derece optimize edilmiş vektörel işlemler ve multi-threading kullanır. `Lazy execution` (tembel çalışma) mimarisi sayesinde dosyayı RAM'e yığmadan disk üzerinden doğrudan filtreleme yapar. Bu sayede bellek tüketimi sıfıra yakındır ve işlem hızı rakipsizdir.

2. **Generator (En Bellek Dostu Klasik Yöntem):** 
Dosyayı tek seferde değil, `yield` mantığıyla satır satır okur. O an sadece okunan satır RAM'de tutulduğu için 5 milyon satırlık devasa bir dosya sadece 0.15 MB bellek tüketir. Sistem kaynaklarını korumak için standart Python'daki en iyi pratiktir.

3. **Naif Yöntem (Aşırı RAM Tüketimi):** 
`readlines()` fonksiyonu dosyadaki tüm satırları tek seferde devasa bir Python listesi olarak RAM'e yükler. Bu yüzden bellek tüketimi 500 MB'ın üzerine fırlamıştır. Daha büyük dosyalarda (örneğin 5-10 GB) sistem belleği tükenecek ve `MemoryError` hatası verecektir.

4. **Multiprocessing (En Yavaş Yöntem):** 
Basit string arama işlemi gibi "IO-bound" (Girdi/Çıktı ağırlıklı) ve hafif işlemlerde, süreç (process) yaratma ve süreçler arası iletişim (IPC) maliyeti asıl yapılan işten çok daha ağırdır. İşlemcileri paralel çalıştırmak için veriyi parçalayıp diğer süreçlere kopyalamak (serialization) zaman kaybettirdiği için, bu spesifik senaryoda en yavaş yöntem olmuştur. Multiprocessing, CPU-bound (yoğun matematiksel işlem gerektiren) görevler için uygundur.

## Bellek ve Performans Sonuçları (Gerçek RSS Ölçümü)
`resource` modülü (`ru_maxrss`) kullanılarak yapılan işletim sistemi seviyesindeki ölçümler sonucunda:

| Yöntem | Süre (Saniye) | Zirve RSS Bellek |
|---|---|---|
| Polars | 1.69s | 674.93 MB |
| Naif Döngü | 6.83s | 561.67 MB |
| Multiprocessing | 62.45s | 323.54 MB |
| Generator | 4.76s | 32.71 MB |

*Not: İlk ölçümlerde kullanılan `tracemalloc` yalnızca Python interpreter tahsislerini gördüğü için Polars ve Multiprocessing bellekleri yansıtılmamıştı. `resource` modülü ile yapılan gerçek OS RSS ölçümünde, Polars'ın hız kazanmak için belleği nasıl yoğun kullandığı net bir şekilde görülmüştür.*