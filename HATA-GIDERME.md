# 🐛 Hata Giderme Rehberi

## "Ürün eklenirken hata oluştu" Hatası

Bu hata birkaç nedenden kaynaklanabilir:

### 1. Backend Terminal Loglarını Kontrol Edin

Backend terminalinde (backend çalıştırdığınız terminal) hata mesajlarını kontrol edin:

```bash
# Backend terminalinde şunları arayın:
❌ Stok kontrolü hatası
❌ URL'ye erişilemedi
❌ Genel hata
```

### 2. URL Formatını Kontrol Edin

URL şu formatta olmalı:
```
https://www.bershka.com/tr/...
```

Örnek:
```
https://www.bershka.com/tr/kadin/elbise/elbise-c1234567890p.html
```

### 3. Yaygın Hatalar ve Çözümleri

#### Hata: "URL'ye erişilemedi"
- **Neden**: İnternet bağlantısı yok veya Bershka sitesine erişilemiyor
- **Çözüm**: İnternet bağlantınızı kontrol edin

#### Hata: "Stok kontrolü yapılamadı"
- **Neden**: Bershka sitesinin yapısı değişmiş olabilir
- **Çözüm**: URL'nin doğru olduğundan emin olun, manuel kontrol deneyin

#### Hata: "Bu ürün URL'si zaten ekli"
- **Neden**: Aynı URL daha önce eklenmiş
- **Çözüm**: Farklı bir ürün URL'si deneyin

#### Hata: "Veritabanı hatası"
- **Neden**: Veritabanı erişim sorunu
- **Çözüm**: Backend'i yeniden başlatın

### 4. Debug Modu

Backend terminalinde detaylı hata mesajları göreceksiniz. Hata mesajını buraya kopyalayın.

### 5. Manuel Test

Backend terminalinde şu komutu çalıştırarak test edebilirsiniz:

```bash
curl -X POST http://localhost:5000/api/urunler \
  -H "Content-Type: application/json" \
  -d '{"urun_url": "BURAYA_URL_YAPIŞTIRIN"}'
```

### 6. Backend'i Yeniden Başlatın

Bazen backend'i yeniden başlatmak sorunu çözer:

```bash
# Backend'i durdurun (Ctrl + C)
# Sonra tekrar başlatın:
cd backend
source venv/bin/activate
python app.py
```

## Hata Mesajını Paylaşın

Eğer hata devam ediyorsa:
1. Backend terminalindeki tam hata mesajını kopyalayın
2. Eklemeye çalıştığınız URL'yi paylaşın
3. Hata mesajını buraya yapıştırın
