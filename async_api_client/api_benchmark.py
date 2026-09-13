import time
import asyncio
import requests
import httpx

API_URL = "https://jsonplaceholder.typicode.com/photos/"
NUM_REQUESTS = 1000

# (a) Senkron İstekler (requests) - Bloklayıcı (Sırayla)
def fetch_sync():
    print(f"Başlıyor: {NUM_REQUESTS} Senkron İstek (requests)... (Bu biraz sürebilir)")
    start_time = time.time()
    
    success_count = 0
    for i in range(1, NUM_REQUESTS + 1):
        try:
            response = requests.get(f"{API_URL}{i}")
            if response.status_code == 200:
                success_count += 1
        except Exception:
            pass
            
    duration = time.time() - start_time
    print(f"[Senkron] {success_count}/{NUM_REQUESTS} başarılı. Süre: {duration:.2f} saniye\n")
    return duration

# (b) Asenkron İstekler (httpx + asyncio) - Düzeltilmiş Eşzamanlı Yapı
async def fetch_single_async(client, url, semaphore, max_retries=5):
    for attempt in range(max_retries):
        try:
            # ÖNEMLİ DÜZELTME: Semaphore sadece istek atıldığı anda slot alır ve bittiğinde hemen bırakır.
            async with semaphore:
                response = await client.get(url)
            
            # Kontroller ve beklemeler semaphore bloğunun DIŞINDADIR (Slotları tıkamaz)
            if response.status_code == 200:
                return True
            elif response.status_code == 429 or (500 <= response.status_code < 600):
                # Rate limit (429) veya sunucu hatalarında (5xx) slot tutulmadan beklenir
                await asyncio.sleep(2 ** attempt)
            else:
                # 404 gibi tekrar denenmemesi gereken istemci hatalarında döngü kırılır
                break
        except Exception:
            if attempt == max_retries - 1:
                return False
            await asyncio.sleep(2 ** attempt)
            
    return False

async def fetch_async():
    print(f"Başlıyor: {NUM_REQUESTS} Asenkron İstek (httpx + Semaphore=10)...")
    start_time = time.time()
    
    semaphore = asyncio.Semaphore(10)
    
    async with httpx.AsyncClient() as client:
        tasks = [
            fetch_single_async(client, f"{API_URL}{i}", semaphore) 
            for i in range(1, NUM_REQUESTS + 1)
        ]
        # Tüm asenkron görevleri başlat ve bitmelerini bekle
        results = await asyncio.gather(*tasks)
        success_count = sum(results)
        
    duration = time.time() - start_time
    print(f"[Asenkron] {success_count}/{NUM_REQUESTS} başarılı. Süre: {duration:.2f} saniye\n")
    return duration

if __name__ == "__main__":
    print("--- API İstemci Performans Testi ---\n")
    
    # 1. Senkron Test
    fetch_sync()
    
    # 2. Asenkron Test
    asyncio.run(fetch_async())