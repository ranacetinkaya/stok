# 🔄 Backend'i Yeniden Başlatma

## ⚠️ Önemli: Backend'i Yeniden Başlatmanız Gerekiyor

Yeni paketler yüklendi, backend'i yeniden başlatmanız gerekiyor.

## Adımlar:

### 1. Mevcut Backend'i Durdurun

Terminal'de backend çalışıyorsa:
- `Ctrl + C` tuşlarına basın (Mac'te Cmd değil, Ctrl)

Veya:
```bash
kill $(lsof -ti:5000)
```

### 2. Backend'i Yeniden Başlatın

```bash
cd backend
source venv/bin/activate
python app.py
```

### 3. Başarılı Mesajı

Backend başladığında şunu göreceksiniz:
```
🚀 Bershka Otomatik Stok Takip Sistemi başlatılıyor...
📧 Email bildirimleri için .env dosyasını yapılandırın
⏰ Otomatik stok kontrolü her 30 dakikada bir yapılacak
 * Running on http://127.0.0.1:5000
```

## ✅ Kontrol

Backend çalışıyor mu?
```bash
curl http://localhost:5000/
```

Başarılı olursa JSON yanıt göreceksiniz.

## 🐛 Hala Hata Alıyorsanız

1. Backend loglarını kontrol edin (terminal çıktısı)
2. Hangi URL'yi eklemeye çalıştığınızı kontrol edin
3. URL formatı: `https://www.bershka.com/tr/...` şeklinde olmalı
