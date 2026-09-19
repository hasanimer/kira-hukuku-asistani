# Kiracı sorunları: kurgu senaryolar ve gerçek emsaller

20.09.2026. Aşağıdaki olaylar araştırma ve skill denemesi için **üretilmiş kurgulardır**; kararların olay özeti veya gerçek müvekkil dosyası değildir. Her örnekte gerçek emsalin olguları ve sonucu ayrıca gösterilir. Güncel mevzuat ve karşı içtihat somut dosyada yeniden araştırılır.

## Sorundan belge ve emsale erişim

[On senaryoluk katalog](kiraci-senaryolari.json) her sorun için gerekli belgeleri, belirleyici soruları, dış araştırma sorgularını, gerçek karar kimliklerini ve karşı olguları içerir. Aşağıdaki dört ayrıntılı örneğe ek olarak K5 taahhüt, K6 depozito/tadilat, K7 emsal raporu, K8 yeni malik/yeni sözleşme, K9 ödeme hesabı ve K10 ihtiyaç nedeniyle tahliyeyi kapsar. Yeni altı senaryo mevcut havuzdaki kararları kullanır; yeni karar eklendiği anlamına gelmez.

```sh
python scripts/scenarios.py list
python scripts/scenarios.py search "rutubet depozito"
python scripts/scenarios.py show K6
```

Komut başka çalışma dizininden de betiğin mutlak yolu ile kullanılabilir; API anahtarı gerekmez. `search` sözcük eşleştirmesidir: ayrı sorunları kaybetmemek için sözcüklerden herhangi birini içeren senaryoları döndürür. Sıralama hukuki önem veya başarı ihtimali değildir. Boş sonuç, hukuki çözüm veya emsal bulunmadığı anlamına gelmez; ek sorguları bağlı kaynaklarda araştır.

`show` çıktısındaki `decisions` gerçek havuz kayıtlarından çözülür; metin hash'leri kontrol edilir. Kaynak kaydı eksik veya bozuksa komut hata verir. `coverage` emsalin hangi meseleyi çözdüğünü ve nerede ek araştırma gerektiğini gösterir. Kaynakların `research_notes` sınırlarını oku; tam metin için `pool.py get`, alıntı için `pool.py quote` kullan.

## Somut dosyaya uygulama

Tarih veya süre hesabı gereken senaryolarda [süre formüllerini](sure-hesaplama.md) kullan; araç bir takvim adayı üretir, eksik hukuki koşulları tamamlamaz.

1. Uyan senaryoları seç; karma uyuşmazlıkta birden çok senaryoyu koru. Kurgudaki tarihleri, ödemeleri ve iddiaları kullanıcının dosyasına taşıma.
2. `documents` listesini dosyayla karşılaştır. Yalnız sonucu etkileyen eksikleri sor; eldeki belgeleri yeniden isteme. `decisive_questions` sonuç üzerinde etkili ayrımları gösterir.
3. Gerekirse `olay | tarih/saat | belge/sayfa | kimin iddiası | belirsizlik` çizelgesi kur. İhtarda düzenleme, tebliğ ve öğrenme tarihlerini; ödemede işlem ve hesaba geçme kayıtlarını karıştırma. Kaynak ve uygulanacak kural doğrulanmadan otomatik son gün hesaplama.
4. Emsalin gerekçesi ve hükmünü dosyayla karşılaştır; `counterfacts` farklı sonucu araştırma başlangıcıdır, kesin ispat veya kabul değildir. Katalogdaki karar tek yönlüyse karşı yöndeki içtihadı dış araştırmada ara. Yalnız usulü çözen kararla alacağın esasını kabul etme.
5. Yanıtı ihtiyaca göre `sorun → belgedeki olgu → uygun emsal ve farkı → eksik delil → sonraki somut adım` bağlantısıyla yaz. Kısa soru için tüm katalog veya belge listesini dökme. İcra/tebliğ gibi devam eden süreç varsa ilgili tarih ve evrakın kontrolünü önceliklendir; doğrulanmamış süreyi kesin tarih olarak bildirme.

## K1 — İşyerinden çıkınca kalan bütün kiralar istendi

**Kurgu:** Beş yıllık işyeri sözleşmesinin üçüncü yılından sonra başka şehre taşınacak kiracı, sözleşmedeki altı ay önceden bildirim hakkını kullanıyor. Bildirim süresi kiralarını ödüyor ve imzalı anahtar teslim tutanağı alıyor. Kiraya veren yine de yıllık kiranın tamamını takibe koyuyor.

**İnceleme:** Özel çıkış hükmünün tam metni, bildirimin ulaşma tarihi, ödeme/iade/tevdi belgeleri ve anahtar teslimi. Gerçek erken tahliye ile sözleşmesel çıkış hakkının kullanımını ayır. Sırf taşınmak veya anahtarı emlakçıya bırakmak geçerli teslim sayılmamalı.

**Gerçek emsal:** Adana BAM 5. HD, E. 2022/1189, K. 2024/1605, 14.11.2024. Sözleşmedeki hakkını bildirimle kullanan, altı aylık ödemeyi tevdi eden ve anahtar teslimini belgeleyen kiracının menfi tespit talebi kabul edilmiş; kiraya verenin istinafı reddedilmiştir. BAM olayın erken tahliye olmadığını belirtir. [Kaynak](https://app.dejure.ai/dokuman/7ad0f708-0612-47c9-956d-f722f4fe55fe).

**Kiracı lehine kullanım:** Bildirim ve ödeme belgeleriyle sözleşmesel hakkın yerine getirildiğini tartışmak. **Sınır/karşı olgu:** Bildirim şartına uyulmaması veya teslimin ispatlanamaması sonucu değiştirir. Sözleşmeden aktarılan üç yıllık makul süreyi veya altı aylık tazminatı kanuni kural sayma.

## K2 — Rutubet var; kiracı kirayı kendiliğinden yarıya indirmek istiyor

**Kurgu:** Depo olarak kiralanan işyerinde su sızıntısı mallara zarar veriyor. Kiracı altı ay önce başlayan sorun için yeni ihtar gönderiyor ve geçmiş dönem dahil süresiz %50 indirim istiyor. İki uzman raporu zararı farklı hesaplıyor.

**İnceleme:** Sözleşmedeki kullanım amacı, ayıbın kaynağı, fotoğraf ve tespit raporları, kiraya verenin öğrendiği tarih, onarım ve giderilme tarihi, kiracının olası kusuru. Kiracının tek taraflı indirim yapmasını kesin hak gibi önermeden ödeme/temerrüt riskini değerlendir.

**Gerçek emsal:** İstanbul BAM 35. HD, E. 2017/1243, K. 2017/1468, 11.10.2017. Su ve rutubet nedeniyle indirim davasında, 40.000 TL ve 200.000 TL tespitler arasındaki çelişki, öğrenme tarihi ve indirim süresi incelenmeden verilen karar kaldırılmıştır. [Kaynak](https://app.dejure.ai/dokuman/eb8af224-a46c-4101-867f-2d58b76a0aef).

**Kiracı lehine kullanım:** Ayıbın kullanıma etkisini ve gerekli teknik incelemeyi göstermek. **Sınır/karşı olgu:** Karar kiracının istediği oranı onaylamaz; geçmişe ve sözleşmenin tamamına yayılan indirimi eleştirir. Kaynaktaki TBK 350 atfı, aynı gerekçedeki TBK 307 anlatımıyla tutarsızdır; yanlış madde numarasını tekrarlama. İşyeri kararı konuta koşulsuz taşınmaz.

## K3 — “İhtarı aldığım gün ödedim; iki ihtar oluşmaz” savunması

**Kurgu:** Kiracı aynı kira yılı içinde iki ödeme emrine itiraz ediyor, ardından aynı gün bankadan ödeme yapıyor. Tahliye davası sırasında taşınıyor ve artık yargılama gideri ödemeyeceğini düşünüyor.

**İnceleme:** Her kira ayı için muacceliyet, tebliğ/öğrenme, itiraz ve ödeme tarih-saat çizelgesi. Temerrüt nedeniyle tahliye ile iki haklı ihtarı ayır; dava sırasında çıkışın giderler üzerindeki etkisini ayrıca değerlendir.

**Gerçek emsal — kiracı aleyhine:** İstanbul BAM 36. HD, E. 2019/3134, K. 2021/1779, 22.09.2021. İtirazlar 11:36 ve 10:39'da, ilgili ödemeler aynı gün 13:19 ve 11:35'te yapılmıştır. BAM iki haklı ihtarı kabul etmiş; taşınmayla konusuz kalan davada giderleri ve vekalet ücretini kiracıya yüklemiştir. [Kaynak](https://app.dejure.ai/dokuman/fa461f44-de8b-43e1-aaa4-60c85a683530).

**Sınır/karşı olgu:** Ödemenin tebliğ/öğrenmeden önce yapıldığı, ihtarın muaccel borca dayanmadığı veya dönemlerin farklı olduğu dosya ayrıca değerlendirilir. Usulsüz tebligatta öğrenme sonucu somut olayın itiraz kayıtlarına dayanır. Bu karar kiracı zaten çıktığı için yeni tahliye hükmü kurmamıştır.

## K4 — Çıkışta bütün yenileme masrafı kiracıya yüklendi

**Kurgu:** Dört yıl kullanılan işyerinden çıkan kiracıdan boya, elektrik ve sökülen malzemeler için yeni ürün fiyatlarıyla tazminat isteniyor. Kiracı bazı malzemeleri kendisinin taktığını, diğer izlerin normal kullanım olduğunu savunuyor. Kiraya veren yalnız delil tespiti raporuna dayanıyor.

**İnceleme:** İlk teslim fotoğrafları, demirbaş listesi, tadilat izinleri, faturalar, son teslim tutanağı, ayıp bildirimi ve bilirkişi itirazları. Her kalemde olağan yıpranma/hor kullanım ayrımı, tahliye tarihindeki bedel ve amortisman ele alınmalı. Depozito kesintisi ileri sürülüyorsa mahsup koşulları ayrıca incelenmeli.

**Gerçek emsal:** İstanbul BAM 55. HD, E. 2023/2395, K. 2024/2656, 06.11.2024. Hasar talebinin kabulü kaldırılmış; keşif, hasar kalemleri ve yıpranma/yenileme payı değerlendirmesi için dosya iade edilmiştir. [Kaynak](https://app.dejure.ai/dokuman/880b0d47-5ca8-4e1a-9fab-41b5da8f1992).

**Kiracı lehine kullanım:** Toplu yenileme faturası yerine somut hasar incelemesi istemek. **Sınır/karşı olgu:** Karar kiracıyı tamamen borçsuz saymaz; kendi taktırdığı malzemeleri söktüğü savunmasını da kesin olgu olarak kabul etmez. Karar depozito iadesi değil hasar tazminatıdır.

## Skill denemesinde beklenen davranış

- K1: alacak ve sözleşme; K2: ayıp/masraf; K3: tahliye ve giderler; K4: hasar/masraf incelemesi. Bunlar model puanına göre silinmez.
- Kurguyu kararın olayıymış gibi anlatma. Gerçek emsalin sonucunu “kabul”, “ret”, “kaldırma/iade” ve “konusuzluk” ayrımıyla yaz.
- Lehe örneği kesin kazanma, aleyhe örneği savunmanın her durumda imkânsızlığı olarak sunma.
- İlgili kararı `pool.py get KIMLIK` ile oku; birebir alıntıyı `quote` ile denetle. Anonimleştirme alanı varsa yerel alıntının kaynak kopyasından farkını koru.

**Seçilmeyen aday:** Bursa BAM 4. HD E. 2024/3141, K. 2026/302 metninde 23.05.2024 ilk derece kararına rağmen 25.08.2024 dava tarihi anlatılıyor. Tarih çelişkisi nedeniyle senaryo emsali olarak eklenmedi; kararın yokluğu veya sonucu hakkında başka çıkarım yapılmadı.
