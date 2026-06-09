# NotebookLM Test Çözme Arayüzü

NotebookLM tarafından özel bir formatta üretilen testleri ayrıştırmak ve etkileşimli olarak çözmek için tasarlanmış Streamlit tabanlı bir web uygulamasıdır. Kullanıcılar test sorularını içeren metin dosyalarını yükleyebilir, soruları çözebilir ve açıklamalar ile belge referanslarını içeren anlık geri bildirimler alabilir.

## Önemli Not

Bu arayüz yalnızca özel bir prompt ile NotebookLM’den üretilmiş test çıktılarıyla çalışır.

Kullanmak için:

1. Kaynaklarınızı NotebookLM’e yükleyin.
2. Belirlenen test üretme promptunu NotebookLM’in chat kısmına yapıştırın.
3. NotebookLM’in ürettiği cevabı `.txt` dosyası olarak kaydedin.
4. `.txt` dosyasını bu arayüze yükleyin veya `tests/` klasörünün içine koyun.

Promptu paylaşmak isterseniz uygulama içine prompt linki veya yönlendirme butonu ekleyebilirsiniz.

## Özellikler

- **Etkileşimli Test Arayüzü:** Sorular arasında gezinin, cevapları seçin ve puanınızı gerçek zamanlı olarak görün.
- **Anlık Geri Bildirim:** Seçtiğiniz şıkkın doğruluğunu anında kontrol edin, detaylı açıklamaları ve kaynak belge referanslarını inceleyin.
- **Dosya Yükleme Desteği:** Sunucuda depolamaya gerek kalmadan sol menü üzerinden doğrudan `.txt` uzantılı dosyalar yükleyin.
- **Yerel Dizin Okuma:** Uygulama başlatıldığında yerel `tests/` klasöründeki test dosyalarını otomatik olarak yükler.
- **Özelleştirilmiş Tasarım:** Streamlit teması ve özel CSS eklemeleriyle modern bir kullanıcı deneyimi sunar.

## Kurulum

### 1. Depoyu klonlayın

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Gerekli kütüphaneleri yükleyin

```bash
pip install -r requirements.txt
```

Eğer `requirements.txt` dosyanız yoksa Streamlit’i elle yükleyebilirsiniz:

```bash
pip install streamlit
```

### 3. Proje yapısını oluşturun

Dizininizin aşağıdaki gibi göründüğünden emin olun:

```text
project-root/
├─ app.py
├─ tests_parser.py
├─ requirements.txt
├─ .streamlit/
│  └─ config.toml
└─ tests/
   └─ ornek-test.txt
```

> Not: `tests/` klasörü boşsa ve GitHub’da görünmesini istiyorsanız içine `.gitkeep` dosyası ekleyebilirsiniz.

## Kullanım

### 1. Streamlit uygulamasını çalıştırın

```bash
streamlit run app.py
```

### 2. Test dosyalarınızı hazırlayın

Testinizi oluşturmak için NotebookLM’de belirtilen özel promptu kullanın. Çıktıyı `.txt` dosyası olarak kaydedin.

### 3. Testleri yükleyin

Testleri iki şekilde yükleyebilirsiniz:

- Otomatik yükleme için `.txt` dosyalarını `tests/` klasörüne yerleştirin.
- Uygulama çalışırken sol menüdeki dosya yükleme alanından `.txt` dosyalarını doğrudan yükleyin.

## Beklenen Test Formatı

Uygulama, NotebookLM çıktılarının aşağıdakine benzer düzenli bir formatta olmasını bekler:

```text
### Question 1 [Remember | Easy] [—]
Soru metni burada yer alır...

A) A seçeneği
B) B seçeneği
C) C seçeneği
D) D seçeneği
E) E seçeneği

**Correct Answer:** C
**Document Reference:** Kaynak belge veya bölüm
**Rationale:** Doğru cevabın açıklaması
```

Bu yapıya uymayan dosyalar doğru şekilde ayrıştırılamayabilir.