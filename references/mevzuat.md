# Türk Borçlar Kanunu

- `data/mevzuat/6098-source.json`: tam metnin yedi kaynak bölümü; kaynak adresi, alınma zamanı ve bölüm bilgileri korunur.
- `data/mevzuat/6098-turk-borclar-kanunu.md`: bölümlerin aralarına iki satır sonu eklenerek birleştirilen aranabilir tam metin.
- `scripts/tbk.py`: madde numarasıyla erişim. Bölüm sırası, toplam bayt sayısı, 1–649 madde başlıkları ve kaynak hash'i denetlenir.

[Resmî kaynak: 6098 sayılı Türk Borçlar Kanunu](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6098&MevzuatTur=1&MevzuatTertip=5).

Alınma zamanı kaynak JSON dosyasındadır. Paket sabit kopyadır; sonraki değişiklikleri ve geçmiş olayda uygulanacak sürümü ayrıca kontrol edin. Geçici hükmün metinde bulunması bugün uygulanacağı anlamına gelmez.

Depo kökünde:

```sh
python scripts/tbk.py
python scripts/tbk.py 344
python scripts/tbk.py 345
```

Numarasız çağrı kaynak bilgisini verir. Madde çıktısı sonraki konu başlığını, araya giren geçici hükümleri veya dipnotları da içerebilir; bunları istenen madde hükmünden ayırın. Son maddenin çıktısı ek tabloları da kapsar.
