<div align="center">

# Kira Hukuku Asistanı

**Dosyadan içtihada, içtihattan gerekçeli taslağa.**

Kira tespiti, tahliye, uyarlama, alacak ve depozito dosyaları için kaynaklara dayalı araştırma ve dilekçe hazırlama becerisi.

[![Paket kontrolü](https://github.com/hasanimer/kira-hukuku-asistani/actions/workflows/validate.yml/badge.svg)](https://github.com/hasanimer/kira-hukuku-asistani/actions/workflows/validate.yml)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square)
![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827?style=flat-square)

[Hızlı başlangıç](#hızlı-başlangıç) · [Kullanım örnekleri](#kullanım-örnekleri) · [Çalışma akışı](#çalışma-akışı) · [Rehberler](#rehberler)

</div>

---

| **1.589 karar** | **6098 sayılı Kanun** | **Taşınabilir paket** |
| :---: | :---: | :---: |
| Tam metin, künye ve kaynak izi | Türk Borçlar Kanunu tam metni | Yerel aramada API anahtarı gerekmez |

## Dosyanız için ne yapar?

<table>
<tr>
<td width="50%" valign="top">

<h3>01 · Dosya analizi</h3>
Olayları ve tarihleri düzenler; sonucu etkileyen eksik bilgi ve belgeleri belirler.

</td>
<td width="50%" valign="top">

<h3>02 · Emsal araştırması</h3>
Lehe ve aleyhe kararları bulur; tam metinleri inceler, birebir alıntıları doğrular.

</td>
</tr>
<tr>
<td width="50%" valign="top">

<h3>03 · Dilekçe taslağı</h3>
Dava ve cevap dilekçelerinde somut olay, delil, hukuki dayanak ve talep arasında bağ kurar.

</td>
<td width="50%" valign="top">

<h3>04 · Rapor incelemesi</h3>
Bilirkişi raporunun emsallerini ve hesap yöntemini inceleyerek somut itirazlar hazırlar.

</td>
</tr>
</table>

## Hızlı başlangıç

**Gerekenler:** Codex, Git ve Python 3.10+. Yerel yardımcılar yalnız Python standart kütüphanesini kullanır.

### 1. Skill'i ekleyin

```sh
git clone https://github.com/hasanimer/kira-hukuku-asistani.git "$HOME/.codex/skills/kira-tespit-asistani"
```

<details>
<summary>Kurulum yolu ve mevcut kurulum hakkında</summary>

Komut PowerShell, Bash ve Zsh ile kullanılabilir. Özel bir `CODEX_HOME` kullanıyorsanız hedef olarak onun `skills` dizinini seçin. Hedef klasörde mevcut bir kopya varsa üzerine yazmadan önce değişikliklerinizi koruyun.

</details>

### 2. Codex'te çağırın

```text
$kira-tespit-asistani kira tespit dosyamı incele;
eksik belgeleri ve lehe/aleyhe emsalleri göster.
```

### 3. Dosyanızla çalışın

İlgili sözleşmeyi, dilekçeyi veya raporu paylaşın; istediğiniz çıktıyı belirtin. Asistan önce belirleyici olguları çıkarır, ardından ilgili kaynakları araştırır.

## Kullanım örnekleri

[Kiracı sorunları: 10 kurgu senaryo, belge listeleri ve gerçek emsaller →](references/kiraci-senaryolari.md)

Kiracının sorunundan ilgili karara ulaşmak için API anahtarı gerektirmeyen senaryo aracı:

```sh
python scripts/scenarios.py list
python scripts/scenarios.py search "rutubet depozito"
python scripts/scenarios.py show K6
```

Her senaryo gerekli belgeleri, sonucu değiştiren soruları ve emsalin sınırlarını gösterir. Kurgu olaylar gerçek karar metinlerinden ayrıdır; sıralama kazanma ihtimali değildir.

[Süre formülleri ve hesap rehberi →](references/sure-hesaplama.md)

```sh
python scripts/deadlines.py tbk345 2026-09-01
python scripts/deadlines.py takvim 2026-01-31 --count 1 --unit ay
```

Araç gün/ay/yıl ayrımını, ilgili kira sürelerini ve UETS hesabını gösterir. Sonuçlar takvim adayıdır; tatil, arabuluculuk ve somut dosyanın hukuki koşulları ayrıca kontrol edilir.

**Dosyanın güçlü ve zayıf yönlerini görmek için**

> $kira-tespit-asistani sözleşmeyi ve olayları incele. Talep edilen dönem bakımından belirleyici konuları, eksik belgeleri ve karşı tarafın ileri sürebileceği itirazları göster.

**Cevap dilekçesi hazırlamak için**

> $kira-tespit-asistani sözleşme ve dava dilekçesine dayanarak cevap dilekçesi taslağı hazırla. Dayandığın kararları tam metinden doğrula.

**Bilirkişi raporunu değerlendirmek için**

> $kira-tespit-asistani bilirkişi raporundaki emsalleri ve hesap yöntemini incele; dosyadaki belgelere bağlı somut itirazları belirle.

## Çalışma akışı

| Aşama | Yapılan iş |
| :--- | :--- |
| **01 · Dosyayı anla** | Belgelerden olgu ve tarih çizelgesi çıkarılır. |
| **02 · Soruyu belirle** | Sonucu değiştiren hukuki meseleler ayrıştırılır. |
| **03 · Kaynağı araştır** | İlgili kanun hükümleri ve karar tam metinleri okunur. |
| **04 · Karşılaştır** | Lehe/aleyhe gerekçeler, olgusal farklar ve dönem incelenir. |
| **05 · Sonucu hazırla** | Kaynaklara bağlı değerlendirme veya taslak oluşturulur. |

Skill, ilgili kaynakları paket içinden seçerek okur; kararlarla yeniden eğitilmiş bir model değildir. [Ayrıntılı çalışma mantığı →](references/calisma-mantigi.md)

## Veri kapsamı

Yerel karar havuzu kira tespiti ağırlıklıdır. Diğer kira hukuku konuları [modüller](references/moduller.md) üzerinden bağlı karar ve mevzuat kaynaklarında araştırılır. İsteğe bağlı [TypeSafe entegrasyonu](references/typesafe.md), karma talepleri yönlendirir ve karar adaylarını sıralar; hukuki sonuç veya dava başarı oranı üretmez. TypeSafe kullanımı ayrıca API anahtarı ve ağ erişimi gerektirir. Mevcut `$kira-tespit-asistani` çağrısı korunmuştur.

| | |
| :--- | :--- |
| **Karar havuzu** | 1.589 karar · 14.10.2004–21.05.2026 |
| **Mevzuat** | 6098 sayılı Türk Borçlar Kanunu |
| **Kaynak kontrolü** | Künye, metin hash'i ve birebir alıntı doğrulaması |
| **Otomatik denetim** | Windows ve Linux üzerinde paket bütünlüğü kontrolleri |

> [!NOTE]
> Veri paketi sabit bir kopyadır; kendiliğinden güncellenmez. Karar etiketleri bağımsız hukukçu doğrulamasından geçmemiştir. Somut dosyada uygulanacak hükmün dönemi ve güncelliği ayrıca kontrol edilir. Güncel kaynak araştırması, asistanın internet ve araç erişimine bağlıdır.

## Komut satırı

Depo kökünde çalıştırın. Sisteminizde gerekirse `python` yerine `python3` kullanın.

```sh
# Havuzun kapsamını görün
python scripts/pool.py stats

# İlgili kararları arayın
python scripts/pool.py search "eski kiracı" --kind esas_gerekcesi --limit 8

# Kanun maddesini okuyun
python scripts/tbk.py 344

# Paketin bütünlüğünü kontrol edin
python scripts/validate.py
```

<details>
<summary>Depo yapısı</summary>

```text
kira-tespit-asistani/
├── SKILL.md             Asistan yönergeleri
├── agents/              Codex görünüm bilgileri
├── data/                Karar havuzu, mevzuat ve kaynak kayıtları
├── references/          Çalışma akışı ve kullanım rehberleri
├── scripts/             Arama, madde erişimi ve doğrulama
└── .github/workflows/   Otomatik paket kontrolleri
```

</details>

## Rehberler

| Başlamak için | Ayrıntıya inmek için |
| :--- | :--- |
| [Skill yönergeleri](SKILL.md) | [Karar havuzu ve arama komutları](references/havuz.md) |
| [Çalışma mantığı](references/calisma-mantigi.md) | [Borçlar Kanunu erişimi](references/mevzuat.md) |
| [Kira tespiti ve hak ve nesafet](references/uygulama-rehberi.md) | [Fazla ödeme iadesi ve ispat](references/iade-ispat.md) |
| [Rehber kaynak kontrolü](references/rehber-dogrulama.md) | [BAM kararları ve kullanım sınırları](references/bam-kararlari.md) |
| [Katkı rehberi](CONTRIBUTING.md) | [Veri kaynakları ve bütünlük](data/README.md) |

---

<div align="center">

**Bir hata mı buldunuz, bir öneriniz mi var?**

[Issue açın](https://github.com/hasanimer/kira-hukuku-asistani/issues) · [Katkı rehberini okuyun](CONTRIBUTING.md)

</div>
