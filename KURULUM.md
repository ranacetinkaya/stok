# 🚀 macOS Kurulum Rehberi

## Sorun: Xcode Command Line Tools Gerekli

macOS'ta Python paketlerini kurmak için Xcode Command Line Tools gereklidir.

## ✅ Çözüm 1: Xcode Command Line Tools Yükleme (Önerilen)

### Adım 1: Terminal'de komutu çalıştırın
```bash
xcode-select --install
```

### Adım 2: Dialog penceresinde
- Açılan pencerede **"Install"** butonuna tıklayın
- Yükleme 5-10 dakika sürebilir (internet hızınıza bağlı)
- Yükleme tamamlandığında terminal'e geri dönün

### Adım 3: Yüklemenin tamamlandığını kontrol edin
```bash
xcode-select -p
```
Bu komut bir yol döndürmeli (örnek: `/Library/Developer/CommandLineTools`)

### Adım 4: Artık paketleri kurabilirsiniz
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## ✅ Çözüm 2: Homebrew ile Python Kurulumu (Alternatif)

Eğer Xcode tools yüklemek istemiyorsanız:

### Adım 1: Homebrew'i yükleyin
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Adım 2: Python'u Homebrew ile yükleyin
```bash
brew install python3
```

### Adım 3: Paketleri kurun
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## ⚠️ Not

Xcode Command Line Tools yüklemesi **ücretsizdir** ve sadece birkaç GB yer kaplar. 
Sistem Python'unu kullanmak için gerekli araçları sağlar.

## 🆘 Sorun Giderme

**Dialog penceresi açılmıyor mu?**
```bash
# Manuel olarak indirin ve yükleyin
softwareupdate --list
softwareupdate --install "Command Line Tools for Xcode"
```

**Hala çalışmıyor mu?**
```bash
# Xcode tools yolunu kontrol edin
sudo xcode-select --reset
xcode-select --install
```
