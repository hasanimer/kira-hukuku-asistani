# Kira Tespit Davası Asistanı

Kira tespit dosyalarını incelemek, ilgili kararları araştırmak ve kaynaklara dayalı dilekçe taslakları hazırlamak için taşınabilir bir Codex skill'i.

**1.576 karar · 6098 sayılı Türk Borçlar Kanunu · Python standart kütüphanesi**

## Neler yapar?

- Dosyadaki olayları, tarihleri ve eksik belgeleri belirler.
- Lehe ve aleyhe kararları arar, tam metinleri okur ve alıntıları doğrular.
- Dava ve cevap dilekçesi ile bilirkişi raporuna itiraz taslağı hazırlar.
- Kanun hükümleri, karar gerekçeleri ve somut olay arasındaki bağlantıyı açıklar.

## Kurulum

Git ve Python 3.10 veya üzeri gerekir. Yerel arama için API anahtarı ya da ek Python paketi gerekmez. Güncel kaynak araştırması, kullandığınız asistanın internet ve araç erişimine bağlıdır.

Codex beceri dizininize klonlayın; hedef klasörde mevcut bir kopya varsa üzerine yazmayın. Özel bir `CODEX_HOME` kullanıyorsanız hedef olarak onun `skills` dizinini seçin.

```sh
git clone https://github.com/hasanimer/kira-tespit-asistani.git "$HOME/.codex/skills/kira-tespit-asistani"
```

Bu komut PowerShell, Bash ve Zsh ile kullanılabilir. Codex'te beceriyi `$kira-tespit-asistani` adıyla çağırın.

## Örnek istekler

> $kira-tespit-asistani kira tespit dosyamı incele; eksik belgeleri ve lehe/aleyhe emsalleri göster.

> $kira-tespit-asistani sözleşme ve dava dilekçesine dayanarak cevap dilekçesi taslağı hazırla.

> $kira-tespit-asistani bilirkişi raporundaki emsalleri ve hesap yöntemini incele, somut itirazları belirle.

## Nasıl çalışır?

Belgeler → olgu ve tarih çizelgesi → hukuki meseleler → kanun ve karar araştırması → uygulanabilirlik ve karşı görüş kontrolü → gerekçeli sonuç veya taslak.

Skill, ilgili kaynakları paket içinden seçerek okur. Kararlarla yeniden eğitilmiş bir model değildir. Ayrıntılar [çalışma mantığında](references/calisma-mantigi.md) açıklanır.

## Kapsam

Kararlar 14.10.2004–21.01.2026 tarih aralığındadır. Veri paketi sabit bir kopyadır ve kendiliğinden güncellenmez. Karar etiketleri bağımsız hukukçu doğrulamasından geçmemiştir. Somut dosyada uygulanacak hükmün dönemi ve güncelliği ayrıca kontrol edilir; taslaklar dosya belgeleriyle birlikte değerlendirilir.

## Depo yapısı

| Yol | İçerik |
| --- | --- |
| [SKILL.md](SKILL.md) | Asistan yönergeleri |
| [references/](references/) | Çalışma akışı, havuz ve mevzuat rehberleri |
| [data/](data/) | Karar tam metinleri, kanun ve kaynak kayıtları |
| [scripts/](scripts/) | Arama, madde erişimi ve bütünlük kontrolü |
| [agents/openai.yaml](agents/openai.yaml) | Codex görünüm bilgileri |

## Komut satırı

Depo kökünde çalıştırın. Sisteminizde gerekirse `python` yerine `python3` kullanın.

```sh
python scripts/pool.py stats
python scripts/pool.py search "eski kiracı" --kind esas_gerekcesi --limit 8
python scripts/tbk.py 344
python scripts/validate.py
```

Tam metin ve alıntı komutları için [havuz rehberini](references/havuz.md), kanun erişimi için [mevzuat rehberini](references/mevzuat.md) okuyun.

## Katkı

Hata bildirimi ve değişiklik önerileri için [katkı rehberini](CONTRIBUTING.md) kullanın. Veri kaynağı, sürüm ve bütünlük bilgileri [veri rehberinde](data/README.md) bulunur.
