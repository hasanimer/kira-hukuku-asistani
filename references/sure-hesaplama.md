# Kira hukukunda süre hesabı

İnceleme: 20.09.2026. Bu rehber **başlangıç olayını seçme → takvim hesabı → hukuki düzeltmeler → son kontrol** sırasını kullanır. Takvim sonucu tek başına hak düşümü, temerrüt veya dava açılabilirliği kararı değildir.

## Kaynak ve doğrulama durumu

- TBK 92–93, 315, 328–329, 344–345, 347 ve 350–353: [paketteki madde okuyucusu](../scripts/tbk.py), [resmî konsolide metin adresi](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6098&MevzuatTur=1&MevzuatTertip=5) ve [TBMM kabul metni](https://cdn.tbmm.gov.tr/KKBSPublicFile/D23/Y2/T1/KanunMetni/a657b33d-109c-473d-9266-5aa48d603ab2.html).
- HMK 91–93, 102–104: [TBMM kabul metni](https://cdn.tbmm.gov.tr/KKBSPublicFile/D23/Y2/T1/KanunMetni/4f31a7dc-5457-494d-81e2-266e2518a374.html); adli tatil için ayrıca [Adalet Bakanlığı açıklaması](https://basin.adalet.gov.tr/amp/bakan-tunctan-adli-tatil-aciklamasi).
- UETS: [PTT açıklaması](https://www.ptt.gov.tr/e-tebligat-sss), 7201 sayılı Kanun 7/a.
- Arabuluculuk: HUAK 18/A/15 ve 18/B; [kamu kurumundaki kanun kopyası](https://ardahan.gsb.gov.tr/Public/Edit/images/IM/12/Arabuluculuk/ARABULUCULUK%20KANUNU%20%C4%B0ND%C4%B0RMEK%20%C4%B0%C3%87%C4%B0N%20TIKLAYINIZ...%20%281%29.pdf), [kira uyuşmazlıklarını kapsama alan 7445 sayılı Kanun](https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y6/KanunMetni/2a3281c1-9f54-4acb-b1c0-9118aa578d7f.htm).

Bu incelemede Mevzuat Bilgi Sistemi PDF uçları hata verdi; TBMM kabul metinleri sonraki değişiklikleri içermez. Yukarıdaki maddeler ve yardımcı resmî kaynaklar incelendi, ancak bütün kanunların 20.09.2026 tarihli konsolide sürümünün çevrimiçi doğrulandığı ileri sürülmez. Somut dosyada uygulanacak sürümü yeniden doğrula. Araç, bu eksikliği kesin son gün ilan ederek aşmaz.

## Takvim işlemleri

`G(t,n)` = t tarihine n **takvim günü** ekle. `A(t,n)` = n takvim ayı ekle; karşılık gelen gün yoksa hedef ayın son gününü kullan. `Y(t,n)` = `A(t,12n)`. Ay/yıl işlemini ilk tarihten tek adımda yap; ay sonuna kırpılmış ara tarihten tekrar tekrar ilerleme.

| Süre | Ham formül | Örnek |
| --- | --- | --- |
| Gün, olay günü sayılmıyor | `G(t,n)` | 01.09.2026 + 30 gün = 01.10.2026 |
| Hafta | `G(t,7n)` | 01.09.2026 + 2 hafta = 15.09.2026 |
| Ay | `A(t,n)` | 31.01.2026 + 1 ay = 28.02.2026 |
| Yıl | `Y(t,n)` | 29.02.2024 + 1 yıl = 28.02.2025 |
| Önceden bildirim | Hedef tarihten ilgili gün/ay miktarını çıkar | 01.09.2026 − 30 gün = 02.08.2026 |

Dayanak: TBK 92 ve HMK 92. Hangi hükmün uygulanacağını işlem türü belirler. Bir ay 30 gün, üç ay 90 gün, bir yıl 365 gün olarak kodlanmaz. “Olay günü sayılmaz” diyerek ay hesabına ayrıca bir gün eklenmez. “Dönemin son kullanılan günü”, “yeni dönem başlangıcı” ve “hukuken sürenin dolduğu tarih” farklı alanlardır; belirsizliği otomatik ±1 gün ile çözme.

## Kira işlemleri için formüller

| İşlem | Başlangıç ve ham hesap | Sonucun sınırı |
| --- | --- | --- |
| TBK 344/3 ilk beş yıl | İlk başlangıç `S`; aday yıldönümü `Y(S,5)` | Altıncı kira yılına ilişkin değerlendirme; bedelin hangi dönemden etkili olduğu ayrıca TBK 345'e bağlı. Yeni sözleşme veya tespit varsa otomatik sıfırlama yapma. |
| TBK 345/2 dönemden önceki eşik | Hedef dönem başlangıcı `N`; `G(N,-30)` | Genel dava son günü değildir. Bu tarihe kadar dava veya uygun yazılı artış bildirimi, bildirim yolunda hedef dönem sonuna kadar dava koşuluyla değerlendirilir. |
| TBK 345/3 artış hükmü | Hedef dönemin belgelerden belirlenen sonu | Artış hükmünün kapsamını doğrula; 30 gün önce ihtarı bu seçenekte her durumda şart sayma. |
| TBK 315 konut/çatılı işyeri | Yazılı bildirim tarihi `T`; asgari `G(T,30)` | Ertesi gün sayım başlar. Verilen süre daha uzunsa uzun süre esas alınır; diğer kiralarda asgari 10 gün hükmünü ayrı değerlendir. Süre sonu tahliye tarihi değildir. |
| TBK 347 kiracının bildirimi | Belirli sürenin bitimi `E`; `G(E,-15)` | Konut/çatılı işyeri; yazılılık ve ulaşma araştırılır. Erken geri verme ile karıştırılmaz. |
| TBK 347/1 kiraya veren | İlk sözleşme süresinin bitimi `E`; on yıllık uzama `Y(E,10)`; izleyen ilk yıl sonu `F=Y(E,11)`; bildirim eşiği `A(F,-3)` | “Başlangıç + 10 yıl” yanlış kısayoldur. Geçiş hükümleri ve yeni sözleşmeler ayrıca incelenir. Belirsiz süreliye bu formül uygulanmaz. |
| TBK 328–329 belirsiz süre | Yerel âdet/aksi sözleşme yoksa başlangıca bağlı altı aylık dönemler; seçilen bitimden üç ay önce bildirim | Herhangi bir güne üç ay eklemek fesih dönemi seçmez. Bildirim döneme yetişmezse sonraki dönem araştırılır. TBK 347/2 kiraya veren yönünden ayrıca kontrol edilir. |
| TBK 350 ihtiyaç/yeniden inşa | Belirli sürenin bitimi veya belirsiz sürede usulünce belirlenen fesih tarihi `E`; `A(E,1)` | Bu tarihin ve dava şartlarının doğrulanması gerekir; arabuluculuk/TBK 353 etkileri henüz eklenmemiştir. |
| TBK 351/1 yeni malik | Edinme `D`; bildirim için `A(D,1)`; altı aylık bekleme için `A(D,6)` | Altı ay **son başvuru süresi değildir**. Yazılı bildirimin ulaşması ve ihtiyacın koşulları ayrı. |
| TBK 351/2 alternatif yol | Sözleşme süresinin bitimi `E`; `A(E,1)` | Edinmeden altı ay bekleme yoluyla karıştırma; hangi yolun seçildiğini yaz. |
| TBK 352/1 taahhüt | Taahhüt edilen boşaltma tarihi `B`; `A(B,1)` | İmza/teslim tarihi değil; dava ve icra seçeneklerinin özel koşullarını ayrı incele. |
| TBK 352/2 iki haklı ihtar | Kanundaki kira süresi/kira yılı ayrımıyla bulunan bitim `E`; `A(E,1)` | İkinci ihtarın tarihine bir ay eklenmez. Haklılık, muacceliyet ve aynı dönem koşulları ayrıca araştırılır. |
| TBK 352/3 kiracı/eşinin konutu | Sözleşme bitimi `E`; `A(E,1)` | Konutun niteliği, konumu ve kiraya verenin önceden bilgisi ayrıca incelenir. |
| TBK 353 uzama | Süresindeki yazılı dava bildirimi varsa bir kira yıllık uzama rejimini incele | “Bildirim tarihi + 365” formülü kullanılmaz. İlgili dava türü, asıl pencere ve kira yılı belirlenmeden otomatik tarih yok. |

## Tatil, arabuluculuk ve tebligat düzeltmeleri

**Hasar bildirimi:** TBK 335'in hemen yazılı bildirim koşuluna sabit üç ay ekleme. TBK 342'deki üç ay, dava/takibin bankaya bildirilmesine ilişkindir; hasar bildiriminin genel son günü değildir. Görünür/gizli ayıp, geri verme, öğrenme ve ulaşma tarihlerini [teslim rehberine](teslim-masraf-kefalet.md) göre ayrı incele.

Süre seçmeden önce [kira rejimini](kira-rejimi-ve-taraflar.md) belirle. TBK 329 taşınır yapıları da kapsar; TBK 330'daki üç günlük taşınır kira bildirimi her büfe/konteynere uygulanmaz. Ürün kirasında temerrüt bakımından TBK 362'nin en az 60 günlük ödeme süresini ayrıca incele; bunu 30 günlük konut/çatılı işyeri süresiyle karıştırma. Bu ayrımlar için otomatik yeni hesap komutu eklenmemiştir. Sözleşmede daha özel bildirim hükmü olup olmadığını kontrol et; [İstanbul BAM 36. HD 2024/1082–2025/1809](emsal-listesi-dogrulama.md) kararındaki iki ay sözleşmeseldir, genel TBK 350 süresi değildir.

**Resmî tatil:** HMK 93 bakımından ara tatil günleri sayılır; son gün resmî tatile rastlarsa tatili izleyen ilk iş günü değerlendirilir. TBK 93'ün kendi kapsamını ve aksine anlaşmayı ayrıca incele. Tam/yarım gün tatili, hafta sonunu ve işlem saatini ilgili yılın resmî takvimiyle doğrula. Araç resmî tatil takvimi içermez; sonuçları ileri kaydırmaz. Geriye sayılan “en az 30 gün/üç ay önce” bildirim eşiğine süreyi kısaltan bir ileri kaydırma uygulama.

**Adli tatil:** HMK 104, adli tatile tabi işlerde **HMK'nın tayin ettiği süreler** için ayrıca incelenir. Kira uyuşmazlığı olması bütün TBK sürelerini adli tatil sonrasına taşımaz. İşin istisna olup olmadığı, süreyi koyan kanun ve resmî tatille birleşme kontrol edilir. Genel `+7 gün` işlemi bütün süreler için geçerli değildir.

**Dava şartı arabuluculuk:** HUAK 18/A/15 kapsamında başvurudan son tutanağa kadar zamanaşımı durur, hak düşürücü süre işlemez. Kavramsal hesap: `kalan = uygulanabilir toplam süre − başvuruya kadar işlemiş bölüm`; son tutanaktan sonra kalan bölüm yürür. Bir aylık süreyi bu amaçla 30 güne çevirme. Başvuru/son tutanak günlerinin sayımı, başvurunun süresinde olması, uyuşmazlığın kapsamı ve tekrar başvurunun etkisi ayrıca incelenmeden tarih üretme. Geçmiş süreyi canlandırdığı veya her ihtar, bekleme ve TBK 345 etki eşiğini durdurduğu varsayılmaz. İhtiyari arabuluculukta HUAK 16 rejimini ayrı araştır. Araç otomatik durma hesabı yapmaz.

**Elektronik tebligat:** UETS'ye ulaşma tarihi `U` ise kanunen tebliğ günü `G(U,5)` gününün sonudur. Beş gün iş günü değildir; hafta sonuna rastlayan tebliğ gününü ileri taşıma. Okuma/SMS/e-posta tarihi başlangıç olarak kullanılmaz. Bundan sonra başlayan dava/itiraz süresi kendi rejimiyle ayrı hesaplanır. Normal KEP yazışmasını otomatik UETS tebligatı sayma.

## Kararla kontrol edilen on yıllık uzama örneği

İstanbul BAM 36. HD, E. 2021/1010, K. 2023/2382, 19.10.2023 tam metni incelendi. Mahkeme 01.11.2009 başlangıçlı bir yıllık sözleşmede ilk sürenin 01.11.2010, on yıllık uzamanın 01.11.2020, izleyen yılın 01.11.2021 tarihinde dolduğunu değerlendirmiş; 03.11.2020 tarihli davayı erken bulmuş ve kiraya verenin istinafını esastan reddetmiştir. [Karar kaynağı](https://app.dejure.ai/dokuman/bb12b6b8-f33f-43ff-aded-6c9a2d166985).

Bu örnek `ilk süre bitimi + 10 + 1 yıl` ayrımını kontrol eder. Tarafın pandemi nedeniyle dört ay ekleme iddiası kabul edilen hesap değildir. Metnin dava anlatımındaki “47” madde atfı ile gerekçedeki 347'yi karıştırma. Kararın tam metni BAM ek havuzundadır: `pool.py get bb12b6b8-f33f-43ff-aded-6c9a2d166985`. Bütün eski sözleşmeler için geçiş hükmü incelemesini ortadan kaldırmaz.

## Komutlar ve çıktı

`deadlines.py` tek bir süre kuralının ham hesabını yapar. `hesap.py` kira dönemi çizelgesini ve TBK 345 tarih koşullarını birleştirir; ay/yıl işlemleri ve TBK 347 hesabında aynı takvim işlevlerini kullanır. `hesap.py tespit` için `--hedef-donem` ile `--artis-sarti` veya `--artis-sarti-yok` açıkça verilmelidir; eksik hedefi bugüne göre seçmez, dönemle eşleşmeyen tarihi sessizce düzeltmez.

`hesap.py` çıktısında `kararin_gecerlilik_tarihi` kesinlik izlenimi vermemek için boş bırakılır; yalnız tarih koşulu sağlanıyorsa `aday_etki_tarihi` üretilir. Tarih koşulu sağlanmıyorsa sonraki dönem otomatik ilan edilmez. `tahliye_dava_acma_araligi` alanı da otomatik bir aylık pencere varsaymamak için boştur. Eski `en_gec_dava_tarihi` alanı yalnız hedef dönemin ham sonunu gösterir; genel dava son günü değildir.

```sh
python scripts/deadlines.py takvim 2026-01-31 --count 1 --unit ay
python scripts/deadlines.py tbk345 2026-09-01
python scripts/deadlines.py tbk315 2026-09-01
python scripts/deadlines.py tbk351 2026-01-31
python scripts/deadlines.py tbk352 2026-01-31
python scripts/deadlines.py tbk347 2010-11-01
python scripts/deadlines.py tbk344 2020-09-01
python scripts/deadlines.py uets 2026-09-01
```

Sırasıyla beklenen ham sonuçlar: 28.02.2026; 02.08.2026; 01.10.2026; 28.02.2026 ve 31.07.2026; 28.02.2026; 01.11.2020/01.11.2021 ve 01.08.2021; 01.09.2025; 06.09.2026 gününün sonu. Tatil nedeniyle bunların nihai son gün olduğu söylenmez. Özellikle 02.08.2026 ve 06.09.2026'nın pazar olması iki işlemin aynı şekilde erteleneceği anlamına gelmez.

Her hesapta `başlangıç olayı ve belgesi | norm/sürüm | ham formül | ham tarih | uygulanacak düzeltmeler | doğrulanmış son tarih veya açık kalan kontrol` göster. Betik `raw_dates`, `basis`, `meaning`, `pending_checks` döndürür; `status` takvim adayıdır. Belge veya hukuki nitelendirme eksikse takvim adayını kesin son gün diye dilekçeye taşıma.
