# Async API Client Benchmark (Ödev 2.4)

Bu projede, harici bir API'ye 1000 adet eşzamanlı istek atarken **Senkron (`requests`)** ile **Asenkron (`httpx + asyncio.Semaphore`)** yaklaşımının performansları karşılaştırılmıştır.

## 📊 Test Sonuçları (Güncel ve Düzeltilmiş Ölçüm)

| Yaklaşım | Başarı Oranı | Toplam Süre | Açıklama |
| :--- | :--- | :--- | :--- |
| **Senkron (`requests`)** | 1000 / 1000 | 694.80 saniye | İstekler tamamen sıralı (bloklayıcı) atıldığı için ağ gecikmeleri üst üste binmiştir. |
| **Asenkron (Düzeltilmiş)** | 1000 / 1000 | 14.11 saniye | `Semaphore(10)` ile eşzamanlılık sınırlandırılmış ve bekleme mantığı doğru konumlandırılarak performans zirveye çıkarılmıştır. |

---

## ⚠️ Vaka Analizi: Semaphore Contention (Tıkanıklık) Hatası ve Çözümü

Projenin ilk geliştirme aşamasında asenkron yaklaşımın senkrondan yavaş çıkması (`1850.86 sn`) ve başarı oranının düşmesi üzerine detaylı bir hata analizi gerçekleştirilmiştir:

1. **İlk Hatalı Yaklaşım (Semaphore İçinde Uyku):** `async with semaphore` bloğunun *içerisinde* retry mekanizması ve `asyncio.sleep` (backoff) çağrısı yapılmıştır. Rate limit (`429`) hatası alan bir istek uyurken 10 slotluk kilidi meşgul etmeye devam etmiş, tüm slotlar "bekleyen" isteklerle dolunca eşzamanlılık pratikte bire düşerek sistem kilitlenmiştir.
2. **Uygulanan Çözüm:** `asyncio.sleep` bekleme mantığı semaphore bloğunun **dışına** çıkarılmış, ayrıca 404 gibi tekrar denenmemesi gereken hatalar ayrıştırılmıştır. Böylece slotlar sadece anlık istek atılırken işgal edilmiş, arka planda uyuyan istekler slotları tıkamamıştır.

---

## 🔑 Teknik Kazanımlar

- **Bloklayıcı vs Non-Blocking:** Senkron yapıda ağ IO beklemeleri işlemciyi kilitlerken, asenkron yapıda `async/await` sayesinde boştaki süreler diğer isteklerin iletilmesi için verimli kullanılmıştır.
- **Rate Limit & Retry Yönetimi:** Büyük ölçekli API isteklerinde sunucuyu boğmamak (`DoS` etkisi yaratmamak) için `Semaphore` ve hata durumlarında artan bekleme süreleri (`exponential backoff`) hayati önem taşır.
