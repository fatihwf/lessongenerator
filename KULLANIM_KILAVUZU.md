# 🎓 Bloom Lesson Generator - Kullanım Kılavuzu

Bu proje, Bloom taksonomisine dayalı, kişiselleştirilmiş ders içerikleri üreten bir yapay zeka uygulamasıdır.

## 🚀 Hızlı Başlangıç (Windows)

Proje klasöründeki **`run_app.bat`** dosyasına çift tıklamanız yeterlidir. Bu betik:
1. Gerekli kütüphaneleri (`requirements.txt`) yükler.
2. Backend sunucusunu (`localhost:8080`) başlatır.
3. Frontend arayüzünü (`localhost:3000`) başlatır.

---

## 🛠 Ön Gereksinimler

Uygulamanın çalışması için bilgisayarınızda şunların kurulu olması gerekir:

1. **Python 3.10+**: [python.org](https://www.python.org/)
2. **Node.js (v18+)**: [nodejs.org](https://nodejs.org/)
3. **pnpm**: Terminale `npm install -g pnpm` yazarak kurabilirsiniz. (Önemli: Proje pnpm kullanmaktadır.)

---

## 🌐 Erişim

*   **Uygulama Arayüzü:** [http://localhost:3000](http://localhost:3000) (Açılan tarayıcı ekranı burası olmalıdır.)
*   **API Dökümantasyonu:** [http://localhost:8080/docs](http://localhost:8080/docs)

## 🔑 Yapılandırma
Tüm API ve model ayarları ana dizindeki `.env` dosyasında yapılmıştır. Uygulama **OpenRouter** üzerinden **DeepSeek V4 Flash** modelini kullanmaktadır.
