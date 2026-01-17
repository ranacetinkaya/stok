# 🛍️ Bershka Otomatik Stok Takip Sistemi

Bershka web sitesinden ürünlerin stok durumunu **otomatik olarak** kontrol eden ve stok geldiğinde **otomatik bildirim** gönderen sistem.

## ✨ Özellikler

- ✅ **Otomatik Stok Kontrolü**: Her 30 dakikada bir tüm ürünler kontrol edilir
- ✅ **Web Scraping**: Bershka sitesinden stok durumu otomatik çekilir
- ✅ **Email Bildirimi**: Stok geldiğinde otomatik email gönderilir
- ✅ **Manuel Kontrol**: İstediğiniz zaman manuel kontrol yapabilirsiniz
- ✅ **Kolay Kullanım**: Sadece ürün URL'si ekleyin, gerisini sistem halleder

## 🎯 Nasıl Çalışır?

1. **Ürün URL'si Ekleyin**: Bershka'dan beğendiğiniz ürünün URL'sini ekleyin
2. **Otomatik Kontrol**: Sistem her 30 dakikada bir stok durumunu kontrol eder
3. **Otomatik Bildirim**: Stok geldiğinde size email gönderilir
4. **Manuel Kontrol**: İstediğiniz zaman "Şimdi Kontrol Et" butonuna tıklayın

## 🚀 Kurulum

### 1. Backend Kurulumu

```bash
cd backend

# Python sanal ortamı oluşturun
python3 -m venv venv
source venv/bin/activate

# Gerekli paketleri yükleyin
pip install -r requirements.txt

# Email bildirimleri için .env dosyası oluşturun
cp ../env.example .env
# .env dosyasını düzenleyip email bilgilerinizi girin
```

### 2. Frontend Kurulumu

```bash
cd frontend
npm install
```

## 📧 Email Bildirimi Ayarları

1. `env.example` dosyasını `.env` olarak kopyalayın (backend klasöründe)
2. Email bilgilerinizi girin:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
RECIPIENT_EMAIL=your-email@gmail.com
```

### Gmail için Özel Ayarlar

Gmail kullanıyorsanız, normal şifreniz yerine **Uygulama Şifresi** kullanmanız gerekiyor:

1. Google Hesabınız > Güvenlik
2. 2 Adımlı Doğrulama'yı etkinleştirin
3. Uygulama Şifreleri bölümünden yeni bir şifre oluşturun
4. Bu şifreyi `EMAIL_PASSWORD` olarak kullanın

## 🎯 Kullanım

### Backend'i Başlatın

```bash
cd backend
source venv/bin/activate
python app.py
```

Backend `http://localhost:5000` adresinde çalışacak ve her 30 dakikada bir otomatik stok kontrolü yapacak.

### Frontend'i Başlatın

```bash
cd frontend
npm run dev
```

Frontend `http://localhost:3000` adresinde açılacak.

## 📱 Kullanım Adımları

1. **Ürün URL'si Bulun**:
   - Bershka web sitesine gidin
   - Beğendiğiniz ürünün sayfasına gidin
   - Tarayıcı adres çubuğundaki URL'yi kopyalayın
   - Örnek: `https://www.bershka.com/tr/urun/elbise-c1234567890p.html`

2. **URL'yi Ekleyin**:
   - Uygulamada "➕ Yeni Ürün Ekle" butonuna tıklayın
   - URL'yi yapıştırın
   - "Ekle ve Kontrol Et" butonuna tıklayın

3. **Otomatik Takip**:
   - Sistem her 30 dakikada bir kontrol eder
   - Stok durumu otomatik güncellenir
   - Stok geldiğinde email bildirimi alırsınız

4. **Manuel Kontrol** (İsteğe Bağlı):
   - Ürün kartında "🔍 Şimdi Kontrol Et" butonuna tıklayın
   - Veya "🔍 Tümünü Kontrol Et" ile tüm ürünleri kontrol edin

## 🔧 Teknik Detaylar

- **Web Scraping**: BeautifulSoup ve Requests kullanılarak Bershka sitesi kontrol edilir
- **Periyodik Kontrol**: APScheduler ile her 30 dakikada bir otomatik kontrol
- **Stok Tespiti**: Farklı yöntemlerle stok durumu tespit edilir:
  - "Add to bag" butonu kontrolü
  - "Out of stock" mesajı kontrolü
  - Beden seçenekleri kontrolü
  - JSON-LD structured data kontrolü
  - Stok durumu class/id kontrolü

## ⚠️ Önemli Notlar

- Sistem Bershka'nın web sitesini periyodik olarak kontrol eder
- Bershka sitesinin yapısı değişirse scraping mantığı güncellenebilir
- Rate limiting için ürünler arasında 2 saniye bekleme yapılır
- Email bildirimi her ürün için sadece bir kez gönderilir (stok 0'dan büyük değere çıktığında)

## 🐛 Sorun Giderme

**Stok durumu "Kontrol Edilemedi" gösteriyor:**
- URL'nin doğru olduğundan emin olun
- Bershka sitesine erişim olup olmadığını kontrol edin
- Manuel kontrol butonunu deneyin

**Email bildirimi gelmiyor:**
- `.env` dosyasının doğru yapılandırıldığından emin olun
- Gmail kullanıyorsanız Uygulama Şifresi kullandığınızdan emin olun
- Backend loglarını kontrol edin

**Otomatik kontrol çalışmıyor:**
- Backend'in çalıştığından emin olun
- Backend loglarında "Stok kontrolü başlatılıyor..." mesajını kontrol edin

## 📄 Lisans

Bu proje kişisel kullanım için geliştirilmiştir.
