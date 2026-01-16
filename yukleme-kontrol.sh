#!/bin/bash

echo "🔍 Xcode Command Line Tools kontrol ediliyor..."
echo ""

# Yükleme durumunu kontrol et
if xcode-select -p &>/dev/null; then
    echo "✅ Xcode Command Line Tools yüklü!"
    echo "📍 Konum: $(xcode-select -p)"
    echo ""
    echo "🎉 Artık Python paketlerini kurabilirsiniz:"
    echo "   cd backend"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
else
    echo "❌ Xcode Command Line Tools henüz yüklü değil."
    echo ""
    echo "Yükleme için:"
    echo "   xcode-select --install"
    echo ""
    echo "Eğer dialog penceresi açılmadıysa, App Store'dan Xcode'u indirebilirsiniz"
    echo "(sadece Command Line Tools için tam Xcode gerekmez, ama çalışır)"
fi
