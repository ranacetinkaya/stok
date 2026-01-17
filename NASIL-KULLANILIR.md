# 📖 Stok Takip Uygulaması Nasıl Kullanılır?

## ❓ Sık Sorulan Sorular

### 1. Bershka'nın ürünlerine erişimi var mı?

**Hayır, bu uygulama Bershka'nın API'sine bağlı değil.**

Bu uygulama **manuel bir stok takip sistemi**. Yani:
- Bershka'nın web sitesinden veya mağazadan ürün bilgilerini **siz manuel olarak** ekliyorsunuz
- Uygulama otomatik olarak Bershka'dan ürün çekmiyor
- Siz hangi ürünleri takip etmek istiyorsanız onları ekliyorsunuz

### 2. Ürün kodu ve adı nedir? Bunlarla mı buluyor?

**Evet, ürün kodu ve adı sizin belirlediğiniz bilgiler.**

- **Ürün Adı**: Takip etmek istediğiniz ürünün adı (örnek: "Siyah Deri Ceket")
- **Ürün Kodu**: Ürünü tanımlamak için kullandığınız kod (örnek: "BERSHKA-12345" veya "BC-2024-001")

Bu bilgilerle uygulama ürünü **bulmuyor**, sadece **takip ediyor**. Yani:
- Siz Bershka mağazasına gidip ürünü kontrol ediyorsunuz
- Stok durumunu uygulamaya giriyorsunuz
- Stok 0'dan büyük bir değere çıktığında email bildirimi alıyorsunuz

## 🎯 Nasıl Çalışır?

### Senaryo Örneği:

1. **Ürün Ekleme:**
   - Bershka'da beğendiğiniz bir ürün var (örnek: "Kırmızı Elbise")
   - Mağazada stokta yok, size uygun beden yok
   - Uygulamaya ekliyorsunuz:
     - Ürün Adı: "Kırmızı Elbise - Beden M"
     - Ürün Kodu: "BERSHKA-ELBISE-001"
     - Mevcut Stok: 0 (stokta yok)

2. **Stok Kontrolü:**
   - Birkaç gün sonra mağazaya gidiyorsunuz
   - Ürün gelmiş mi kontrol ediyorsunuz
   - Eğer gelmişse, uygulamada stok miktarını güncelliyorsunuz (örnek: 5 adet)

3. **Otomatik Bildirim:**
   - Stok 0'dan 5'e çıktığında
   - Uygulama otomatik olarak size email gönderir
   - "🎉 Stok Geldi: Kırmızı Elbise" mesajı alırsınız

## 📝 Kullanım Adımları

### Adım 1: Ürün Ekleme

1. "➕ Yeni Ürün Ekle" butonuna tıklayın
2. Bilgileri doldurun:
   - **Ürün Adı**: Takip etmek istediğiniz ürünün adı
   - **Ürün Kodu**: Ürünü tanımlamak için kod (istediğiniz gibi)
   - **Mevcut Stok**: Şu anki stok durumu (genelde 0)
   - **Minimum Stok**: Uyarı almak istediğiniz minimum seviye
3. "➕ Ekle" butonuna tıklayın

### Adım 2: Stok Güncelleme

1. Ürün kartında "Stok Güncelle" bölümüne yeni miktarı yazın
2. Enter'a basın veya ✓ butonuna tıklayın
3. Eğer stok 0'dan büyük bir değere çıktıysa, otomatik email bildirimi gönderilir

### Adım 3: Stok Durumu Takibi

- 🟢 **Yeşil**: Stokta var (yeterli stok)
- 🟠 **Turuncu**: Stok az (minimum seviyenin altında)
- 🔴 **Kırmızı**: Stokta yok

## 💡 İpuçları

1. **Ürün Kodu Nasıl Belirlenir?**
   - Bershka'nın kendi ürün kodunu kullanabilirsiniz (varsa)
   - Kendi kodlama sisteminizi oluşturabilirsiniz
   - Örnek: "BERSHKA-2024-ELBISE-001"

2. **Stok Kontrolü Ne Zaman Yapılır?**
   - İstediğiniz zaman manuel olarak kontrol edip güncelleyebilirsiniz
   - Mağazaya gittiğinizde
   - Web sitesini kontrol ettiğinizde

3. **Email Bildirimi Nasıl Çalışır?**
   - Stok 0'dan büyük bir değere çıktığında otomatik gönderilir
   - Her ürün için sadece bir kez gönderilir
   - Email ayarlarını `.env` dosyasında yapılandırmanız gerekir

## 🔄 Otomatik Entegrasyon İsterseniz

Eğer Bershka'nın API'sine otomatik bağlanmak isterseniz:
- Bershka'nın resmi API'si olup olmadığını kontrol etmeniz gerekir
- API varsa, backend kodunu güncelleyebiliriz
- Ancak çoğu e-ticaret sitesi API erişimi için özel izin gerektirir

## 📧 Email Bildirimi Ayarlama

Email bildirimi almak için:

1. `backend` klasöründe `.env` dosyası oluşturun
2. Email bilgilerinizi girin (Gmail için Uygulama Şifresi gerekir)
3. Detaylar için `README.md` dosyasına bakın
