# Yerel havuz ve kaynak izi

Varsayılan kök: bu skill klasöründeki `data/`. Yardımcı yolu kendi konumundan çözer; skill klasörünün tamamı başka dizine taşınabilir. Ana havuzdaki 1.576 karar ile `bam-selected.jsonl` dosyasındaki 17 BAM kararı ve `yargitay-selected.jsonl` dosyasındaki 3 Yargıtay kararının toplam 1.596 tam metni pakete dahildir. BAM seçkisi için [kullanım notlarını](bam-kararlari.md) oku. Başka havuzu açıkça seçmek için komuta `--root "..."` ekle.

Bu paket 20.09.2026 tarihinde güncellenmiş sabit kopyadır; kaynak proje değişince otomatik güncellenmez. `data/manifest.json` kaynak ve paket dosyalarının hash değerlerini, kayıt sayısını ve etiket birleştirme yöntemini içerir. Hukuki içerik korunarak aktarılmıştır. Açık kişi adı çıkarılan kayıtlarda `redactions` anonimleştirmeyi, `source_text_sha256` kaynak metnini, `text_sha256` yerel metni izler.

## Sürümler

19.09.2026 tarihinde incelenen dosyalar:

- `topic-rescan-assistant-adjusted.jsonl`: varsayılan sıkı havuz, 1.576 kayıt; tarih aralığı 14.10.2004–21.01.2026. Yeniden tarama ve bilinen 13 dışlama birlikte uygulanmış.
- `value_assessment` etiketleri önceki 1.645 kayıtlık `verified-topic-pool.jsonl` havuzundan yalnız `(document_id, text_sha256)` eşleşmesiyle paket kayıtlarına eklenmiştir. Önceki havuza çalışma zamanında ihtiyaç yoktur; dışlanmış kararlar pakete geri eklenmemiştir.
- `data/verified-topic-report.md`, `data/topic-rescan-report.md`: seçim yöntemleri ve sınırlılıkları; yollar skill köküne göredir.

`verified` adı bağımsız hukukçu onayı anlamına gelmez. Aynı JEV modelinin yeniden değerlendirmesi bağımsız model testi değildir. `human_validated: false` kayıtlarını insan onaylı diye sunma.

## Salt okunur yardımcı

Python standart kütüphanesi yeterli. Skill kökünde çalıştırılacak PowerShell örnekleri (başka çalışma dizininde betiğin mutlak yolunu kullan):

```powershell
python scripts/pool.py stats
python scripts/pool.py search "eski kiracı" --kind esas_gerekcesi --limit 8
python scripts/pool.py search emsal bilirkişi --limit 8
python scripts/pool.py get KARAR_KIMLIGI
python scripts/pool.py quote KARAR_KIMLIGI "Birebir kısa alıntı"
```

`KARAR_KIMLIGI` yerine aramada dönen `document_id` kullan. Arama bütün terimlerin bulunmasını ister; aksanları sadeleştirerek eşleştirir. Sıralama yalnız sözcük geçişlerine dayanır, hukuki önem veya emsal gücü puanı değildir. Arama kesiti tam metin yerine geçmez. Sonuç sayısı sınırlı olduğu için `total_matches` alanını kontrol et, gerekirse sorguyu daralt veya limiti artır.

Yardımcı her okumada kayıt metni SHA-256 değerini kontrol eder; uyuşmazlıkta durur. Hash yalnız dosya içi bütünlüğü doğrular, resmî kaynağın doğruluğunu veya eksiksizliğini kanıtlamaz. `quote` büyük/küçük harf, noktalama ve boşlukları değiştirmeden arar; konumlar Python Unicode karakter dizisinde sıfır tabanlı, bitiş hariçtir. Bulunamayan alıntıyı yaklaşık eşleşmiş diye doğrulama.

Araştırma izinde: havuz dosyası, document_id, court, esas_no, karar_no, karar_tarihi, text_sha256, alıntı ve konumu, dosyaya uygulanabilirlik gerekçesi. Kayıtta doğrulanmış kaynak URL'si yoksa URL türetme; yerel dosya ve künye ile atıf yap.

Yalnız BAM kararları için `python scripts/pool.py search ihtar --court-type bam` kullan. BAM kaynak adresleri `source_url`, kullanım sınırları `research_notes` alanında döner. Dejure bağlantıları giriş gerektirebilir; yerel tam metin erişimi çevrimdışı çalışır.

Yargıtay ekleri için [seçki ve kullanım sınırlarını](yargitay-kararlari.md) oku. `--court-type yargitay` yalnız tür etiketi olan kayıtları süzer; etiketsiz ana havuz kayıtları bu filtreyle görünmeyebilir.
