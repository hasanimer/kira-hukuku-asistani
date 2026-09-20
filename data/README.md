# Veri paketi

Karar havuzu 1.603 kayıt içerir; kararların hukuki içeriği korunur. Açık kişi adı çıkarılan kayıtlarda anonimleştirme `redactions` alanında belirtilir; `source_text_sha256` kaynak metnini, `text_sha256` dağıtılan metni izler. Seçim ve etiketleme yöntemleri [havuz rehberinde](../references/havuz.md) açıklanır. Bu paket tüm kira uyuşmazlıklarını veya güncel içtihadın tamamını kapsadığı iddiasını taşımaz.

| Dosya | Amaç |
| --- | --- |
| `yargitay-selected.jsonl` | On Yargıtay kararının tam metni, kaynak bağlantısı ve inceleme notları |
| `bam-selected.jsonl` | On yedi BAM kararının tam metni, kaynak bağlantısı ve asistan inceleme notları |
| `topic-rescan-assistant-adjusted.jsonl` | Karar künyesi, tam metin, metin hash'i ve değerlendirme etiketleri |
| `topic-rescan-report.md` | Sıkı havuz seçiminin yöntemi |
| `verified-topic-report.md` | Önceki seçim aşamasının raporu |
| `mevzuat/6098-source.json` | Kanunun kaynak bölümleri ve alınma bilgisi |
| `mevzuat/6098-turk-borclar-kanunu.md` | Kanunun okunabilir tam metni |
| `manifest.json` | Paket dosyalarının SHA-256 değerleri ve kaynak sürüm izleri |

`verified` dosya adı insan doğrulaması anlamına gelmez. Etiketler aday karar seçimini destekler; kararı okumadan hukuki sonuca dönüşmez.

Kanunun resmî adresi kaynak JSON dosyasındadır. Kararlarda `document_id`, künye, `raw_sha256` ve `text_sha256` izleri korunur. Metin hash'i yerel bütünlüğü gösterir; tek başına resmî doğrulama değildir. Çalıştırma ortamı ve anahtar yuvası gibi iç operasyon alanları pakete dahil edilmez.

`python scripts/validate.py` kayıt sayısını, dosya/metin hash'lerini, kanun bütünlüğünü ve yardımcıların temel davranışlarını doğrular. `.gitattributes` veri baytlarının işletim sistemine göre değiştirilmesini önler.

Kaynak metin düzeltmesi öneriyorsanız kayıt kimliğini, kaynağı ve değişikliğin gerekçesini belirtin; metni sessizce değiştirmeyin. Müvekkil dosyalarını bu veri dizinine eklemeyin.
