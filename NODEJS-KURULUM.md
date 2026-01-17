# Node.js Kurulum Rehberi (macOS)

## 🎯 Node.js Yükleme Yöntemleri

### Yöntem 1: Resmi İndirici (En Kolay - Önerilen) ⭐

1. **Tarayıcıda şu adrese gidin:**
   ```
   https://nodejs.org/
   ```

2. **"LTS" (Long Term Support) versiyonunu indirin**
   - Yeşil butona tıklayın
   - `.pkg` dosyası indirilecek

3. **İndirilen dosyayı çalıştırın**
   - Downloads klasöründe `.pkg` dosyasını bulun
   - Çift tıklayarak kurulum sihirbazını başlatın
   - "Continue" butonlarına tıklayarak ilerleyin
   - Admin şifrenizi girin
   - Kurulum tamamlanınca "Close" butonuna tıklayın

4. **Kurulumu kontrol edin:**
   ```bash
   node --version
   npm --version
   ```

5. **Yeni terminal açın** (kurulumun tanınması için)
   - Mevcut terminal'i kapatıp yeni bir terminal açın
   - Veya `source ~/.zshrc` komutunu çalıştırın

### Yöntem 2: Homebrew ile (Alternatif)

Eğer Homebrew yüklüyse:

```bash
brew install node
```

Homebrew yüklü değilse önce Homebrew'i yükleyin:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Yöntem 3: NVM ile (Geliştiriciler için)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.zshrc
nvm install --lts
```

## ✅ Kurulum Sonrası

Node.js yüklendikten sonra:

```bash
# Yeni terminal açın veya:
source ~/.zshrc

# Kontrol edin:
node --version
npm --version

# Frontend'i kurun:
cd frontend
npm install
npm run dev
```

## 🆘 Sorun Giderme

**"command not found" hatası alıyorsanız:**
- Yeni bir terminal penceresi açın
- Veya şu komutu çalıştırın: `source ~/.zshrc`

**Hala çalışmıyorsa:**
- Terminal'i tamamen kapatıp yeniden açın
- PATH'i kontrol edin: `echo $PATH`
