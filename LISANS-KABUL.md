# Xcode Lisansını Kabul Etme

## Adım 1: Terminal'de şu komutu çalıştırın:

```bash
sudo xcodebuild -license
```

## Adım 2: Şifrenizi girin
- Mac'inizin admin şifresini girmeniz istenecek
- Şifre yazılırken görünmez (normal bir durum)
- Enter'a basın

## Adım 3: Lisans sözleşmesini okuyun
- Terminal'de lisans sözleşmesi görünecek
- Aşağı kaydırmak için **boşluk tuşu** kullanın
- Sonuna kadar okuyun

## Adım 4: Lisansı kabul edin
- Sözleşmenin sonunda şunu yazın: **`agree`**
- Enter'a basın

## Alternatif: Direkt kabul etmek için

Eğer sözleşmeyi okumadan direkt kabul etmek isterseniz:

```bash
sudo xcodebuild -license accept
```

**Not:** Bu komut sözleşmeyi okumadan direkt kabul eder. İlk seçenek daha güvenlidir.

## Kontrol

Lisansın kabul edildiğini kontrol etmek için:

```bash
xcode-select -p
```

Bu komut bir yol döndürmeli (örnek: `/Library/Developer/CommandLineTools`)

## Sonraki Adım

Lisans kabul edildikten sonra:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
