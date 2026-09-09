# Performance Race (Ödev 2.3)

Bu proje, 5 milyon satırlık bir log dosyasında belirli bir koşulu (örn: `/api/v1/orders` içeren satırları sayma) ararken 4 farklı Python yönteminin süre ve gerçek bellek (RSS) tüketimlerini karşılaştırmak için hazırlanmıştır.

## 📊 Bellek ve Performans Sonuçları (Gerçek RSS Ölçümü)

`resource` modülü (`ru_maxrss`) kullanılarak yapılan işletim sistemi seviyesindeki gerçek ölçümler sonucunda:

| Yöntem | Süre (Saniye) | Zirve RSS Bellek (MB) |
| :--- | :--- | :--- |
| **Polars** | 1.69s | 674.93 MB |
| **Naif Döngü** | 6.83s | 561.67 MB |
| **Multiprocessing** | 62.45s | 323.54 MB |
| **Generator** | 4.76s | 32.71 MB |

*Not: İlk ölçümlerde kullanılan `tracemalloc` yalnızca Python interpreter tahsislerini gördüğü için Polars ve Multiprocessing belleğini yansıtmamıştı. `resource` modülü ile yapılan gerçek OS RSS ölçümünde, Polars'ın hız kazanmak için belleği nasıl yoğun kullandığı net bir şekilde görülmüştür.*

## 🧠 Yöntemler Neden Farklı Sonuçlar Verdi?

1. **Polars (En Hızlı Yöntem):** Arka planda tamamen Rust tabanlı, son derece optimize edilmiş vektörel işlemler ve multi-threading kullanır. *Lazy execution* mimarisi sayesinde veriyi işlerken belleği cesurca ve yoğun bir şekilde kullanarak hızı zirveye çıkarır.
2. **Generator (En Bellek Dostu Klasik Yöntem):** Dosyayı tek seferde değil, `yield` mantığıyla satır satır okur. O an sadece okunan satır RAM'de tutulduğu için 5 milyon satırlık devasa bir dosyada minimum bellek tüketir. Bellek verimliliği açısından en iyi saf Python pratiğidir.
3. **Naif Yöntem (Aşırı RAM Tüketimi):** `readlines()` fonksiyonu dosyadaki tüm satırları tek seferde devasa bir Python listesi olarak RAM'e yükler. Bu yüzden bellek tüketimi 500 MB'ın üzerine fırlamıştır.
4. **Multiprocessing (En Yavaş Yöntem):** Basit string arama işlemi gibi "IO-bound" ve hafif işlemlerde, süreç (process) yaratma ve süreçler arası iletişim (IPC) maliyeti asıl yapılan işten çok daha ağırdır. Süreçleri paralel çalıştırmak için veriyi parçalayıp diğer süreçlere kopyalamak zaman kaybettirdiği için bu senaryoda en yavaş yöntem olmuştur.
