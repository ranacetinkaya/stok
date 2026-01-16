# 🔧 Railway Deploy Sorun Giderme

## Yaygın Hatalar ve Çözümleri

### 1. ❌ "No module named 'flask'"

**Sorun:** Python paketleri yüklenmemiş

**Çözüm:**
- Railway Settings → Build Command: `pip install -r requirements.txt`
- Veya `nixpacks.toml` dosyasını kullanın (zaten mevcut)

### 2. ❌ "Port already in use" veya Port Hatası

**Sorun:** Port ayarları yanlış

**Çözüm:**
- Environment Variables'da `PORT` değişkenini ekleyin
- Railway otomatik port atar, `PORT` env var'ını kullanın
- Backend kodunda zaten `os.getenv('PORT', 5001)` var ✅

### 3. ❌ "ChromeDriver not found" (Selenium Hatası)

**Sorun:** ChromeDriver kurulu değil

**Çözüm:**
- `backend/nixpacks.toml` dosyası zaten mevcut ✅
- Railway otomatik olarak ChromeDriver kurar
- Eğer hala sorun varsa, `nixpacks.toml` dosyasını kontrol edin

### 4. ❌ "Database not found" veya SQLite Hatası

**Sorun:** Database dosyası oluşturulmuyor

**Çözüm:**
- Railway'de persistent storage kullanın
- Veya `DATABASE_PATH` environment variable'ını kontrol edin
- Railway'de dosya sistemi geçici olabilir, persistent volume ekleyin

### 5. ❌ Build Hatası

**Sorun:** Build command çalışmıyor

**Çözüm:**
- Railway Settings → Build Command: `cd backend && pip install -r requirements.txt`
- Root Directory: `backend` olarak ayarlayın

### 6. ❌ "Module not found" veya Import Hatası

**Sorun:** Paketler requirements.txt'de eksik

**Çözüm:**
- `requirements.txt` dosyasını kontrol edin
- Tüm bağımlılıkların listelendiğinden emin olun

## ✅ Doğru Railway Ayarları

### Settings:
- **Root Directory:** `backend`
- **Start Command:** `python app.py`
- **Build Command:** (boş bırakın, nixpacks.toml kullanılacak)

### Environment Variables:
```
PORT=5001
HOST=0.0.0.0
DEBUG=False
DATABASE_PATH=stok.db
```

### Networking:
- **Generate Domain** butonuna tıklayın
- Public URL alın

## 🔍 Log Kontrolü

Railway'de hata alırsanız:

1. **Deployments** sekmesine gidin
2. Son deployment'a tıklayın
3. **Logs** sekmesine bakın
4. Hata mesajını kopyalayın

## 📝 Hata Mesajını Paylaşın

Hata mesajını paylaşırsanız, daha spesifik çözüm önerebilirim!
