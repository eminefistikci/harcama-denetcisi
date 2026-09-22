# Kişisel Harcama Denetçisi

Kişisel finans hareketlerini içeren CSV dosyalarını analiz eden, doğrulayan ve anomalileri, tekrarlayan işlemleri, düzenli ödemeleri ve dönem kıyaslamalarını raporlayan bir komut satırı uygulamasıdır.

## Kurulum
Proje Python 3.11 veya daha yeni bir sürüm gerektirir.

1. Proje dizinine gidin:
```bash
cd harcama_denetcisi
```

2. Sanal ortam oluşturun ve aktif edin:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Gerekli bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

## CSV Veri Formatı
Uygulama UTF-8 kodlamalı, virgülle ayrılmış CSV dosyalarını işler. Sütun sırasından bağımsız olarak başlık isimlerine göre eşleme yapılır.

| Sütun | Zorunlu | Açıklama |
|---|:---:|---|
| `transaction_id` | Evet | Benzersiz işlem kimliği |
| `transaction_date` | Evet | `YYYY-MM-DD` formatında işlem tarihi |
| `description` | Hayır | İşlem açıklaması |
| `merchant` | Evet | İşyeri / alıcı adı |
| `category` | Evet | Harcama veya gelir kategorisi |
| `transaction_type` | Evet | `expense`, `income` veya `refund` |
| `amount` | Evet | Pozitif ondalık tutar |
| `currency` | Evet | 3 harfli para birimi kodu (`TRY`, `USD` vb.) |
| `payment_method` | Hayır | Ödeme yöntemi (Kart, Havale vb.) |
| `city` | Hayır | İşlemin yapıldığı şehir |

## Kullanım ve Komutlar

Uygulama modül olarak çalıştırılır:

```bash
python -m harcama_denetcisi <komut> <csv_dosyasi> [seçenekler]
```

### 1. Dosya Doğrulama (`validate`)
CSV dosyasının geçerliliğini ve geçersiz satırları nedenleriyle listeler:
```bash
python -m harcama_denetcisi validate harcama_denetcisi/ornek_harcamalar.csv
```

### 2. Genel Finansal Özet (`summary`)
Para birimi bazında toplam gelir, gider, net harcama ve nakit akışını gösterir:
```bash
python -m harcama_denetcisi summary harcama_denetcisi/ornek_harcamalar.csv
# JSON formatında almak için:
python -m harcama_denetcisi summary harcama_denetcisi/ornek_harcamalar.csv --format json
```

### 3. Kategori Raporu (`category-report`)
Kategori bazında harcama dağılımını ve yüzdelerini büyükten küçüğe sıralar:
```bash
python -m harcama_denetcisi category-report harcama_denetcisi/ornek_harcamalar.csv
```

### 4. Aylık Rapor (`monthly-report`)
Harcamaların ve nakit akışının aylara göre değişimini gösterir:
```bash
python -m harcama_denetcisi monthly-report harcama_denetcisi/ornek_harcamalar.csv
```

### 5. İşyeri Raporu (`merchant-report`)
En çok harcama yapılan işyerlerini listeler (`--top` opsiyoneldir):
```bash
python -m harcama_denetcisi merchant-report harcama_denetcisi/ornek_harcamalar.csv --top 5
```

### 6. Arama ve Filtreleme (`search`)
Açıklama veya işyeri alanında metin araması yapar:
```bash
python -m harcama_denetcisi search harcama_denetcisi/ornek_harcamalar.csv --query "market"
```

### 7. Düzenli Ödemeler / Abonelikler (`recurring`)
25-35 günlük periyotlarla tekrarlanan sabit ödemeleri ve bir sonraki ödeme tarihini tespit eder:
```bash
python -m harcama_denetcisi recurring harcama_denetcisi/ornek_harcamalar.csv
```

### 8. Olası Mükerrer İşlemler (`duplicates`)
Aynı gün, aynı tutar ve işyerine ait şüpheli çift çekimleri gruplar:
```bash
python -m harcama_denetcisi duplicates harcama_denetcisi/ornek_harcamalar.csv
```

### 9. Aykırı Harcama Tespiti (`anomalies`)
Kategori medyanının belirli bir katının (`multiplier`) üzerindeki yüksek harcamaları listeler:
```bash
python -m harcama_denetcisi anomalies harcama_denetcisi/ornek_harcamalar.csv --multiplier 2.5 --min-amount 500
```

### 10. Dönem Karşılaştırma (`compare`)
İki farklı tarih aralığının harcama ve kategori değişim farklarını hesaplar:
```bash
python -m harcama_denetcisi compare harcama_denetcisi/ornek_harcamalar.csv --period1 2026-05-01 2026-05-31 --period2 2026-06-01 2026-06-30
```

### 11. Güvenli Dışa Aktarma (`export`)
Raporu atomik olarak bir JSON dosyasına aktarır:
```bash
python -m harcama_denetcisi export harcama_denetcisi/ornek_harcamalar.csv --report category-report --output rapor.json --format json
```

## Tasarım ve Mimari Kararlar

* **Pydantic v2 & Immutability (`models.py`):** Ham CSV satırları doğrulanıp `Transaction` modeline dönüştürülür. Modellerin kazara değiştirilmesini önlemek amacıyla `frozen=True` yapılandırması kullanılmış; sayısal hassasiyet kayıplarının önüne geçmek için parasal alanlar `Decimal` olarak tutulmuştur.
* **Lazy Evaluation (`reader.py`):** Büyük CSV dosyalarının tek seferde belleğe alınmasını önlemek için `yield` ve `yield from` kullanılarak generator akışı kurulmuştur.
* **Closure ve Higher-Order Functions (`filters.py`):** Filtreleme mantığı `make_transaction_filter` fonksiyonuyla closure tabanlı bir predicate üretir[cite: 11, 14]. `compose_filters` ile birden fazla predicate `all()` kullanılarak birleştirilir. `make_period_filter` ise `functools.partial` yardımıyla oluşturulmuştur.
* **Decorator & Decorator Factory (`decorators.py`):** `@measure_runtime` decorator'ı ile analitik fonksiyonların çalışma süresi ölçülürken, parametrik `@audit_action("action_name")` decorator factory ile başlangıç/bitiş logları rapor çıktısını bozmamak adına `sys.stderr` üzerinden basılır[cite: 11, 13]. Her iki decorator da meta veriyi korumak için `functools.wraps` kullanır.
* **Context Manager ile Atomik Yazma (`reports.py`):** `export` komutunda veriler doğrudan hedef dosyaya yazılmaz. `@contextmanager` ile yazılan `atomic_writer`, veriyi önce geçici bir `.tmp` dosyasına yazar; işlem başarıyla bittiğinde `os.replace` ile atomik olarak hedef dosyanın yerine geçirir. Bir hata durumunda yarım dosya kalması engellenir.
* **Registry Pattern (`reports.py`):** Tablo ve JSON biçimlendirme fonksiyonları uzun `if/elif` blokları yerine bir format registry sözlüğü üzerinden dinamik olarak seçilir.
* **Fazladan CSV Sütunları Yönetimi (`extra="ignore"`):** Gerçek hayat banka ve finans ekstrelerinde uygulamada tanımlanmamış ek sütunlar bulunabilir. `Transaction` modelinde `extra="ignore"` yapılandırması tercih edilerek, zorunlu alanları taşıyan fakat fazladan sütun içeren dosyaların gereksiz yere reddedilmesi önlenmiş, uygulamanın esnekliği artırılmıştır.

## Bilinen Sınırlamalar

* Farklı para birimleri arasında otomatik kur dönüşümü yapılmaz; her para birimi bağımsız olarak analiz edilir ve raporlanır[cite: 11].
* Dönem karşılaştırmasında (`compare`), ilk dönemde harcaması bulunmayan (`0`) kategoriler için yüzde değişimi sıfıra bölme hatasını önlemek amacıyla `N/A` olarak gösterilir