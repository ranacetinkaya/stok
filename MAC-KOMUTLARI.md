# Mac Terminal Komutları

## Process Durdurma

### Backend'i Durdurmak İçin:

**Yöntem 1: Ctrl + C** (En kolay)
- Terminal'de backend çalışırken
- `Ctrl + C` tuşlarına basın
- Process durur

**Yöntem 2: Process ID ile Durdurma**
```bash
# Çalışan backend'i bul
lsof -ti:5000

# Durdur (PID numarasını yukarıdaki komuttan alın)
kill <PID_NUMARASI>

# Veya direkt:
kill $(lsof -ti:5000)
```

**Yöntem 3: Tüm Python Process'lerini Durdur**
```bash
pkill -f "python.*app.py"
```

## Frontend'i Durdurmak İçin:

Aynı şekilde `Ctrl + C` kullanın veya:
```bash
kill $(lsof -ti:3000)
```

## Yeni Terminal Açma (Mac)

- **Cmd + T**: Yeni sekme
- **Cmd + N**: Yeni pencere
- **Cmd + K**: Terminal'i temizle

## Backend ve Frontend'i Başlatma

### Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
python app.py
```

### Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

## Hızlı Kontrol

Hangi portlar kullanılıyor?
```bash
lsof -i :5000  # Backend
lsof -i :3000  # Frontend
```
