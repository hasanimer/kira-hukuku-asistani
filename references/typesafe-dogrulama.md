# TypeSafe doğrulama kaydı

20.09.2026; canlı API'nin bildirdiği model: `jev-1.13.0`. Küçük örnek kümesiyle entegrasyon ve davranış kontrolüdür; Türk kira hukukunda doğruluk oranı veya karşılaştırmalı başarı çalışması değildir.

## Gözlemler ve düzeltme

İlk canlı denemede altıncı yıl kira tespiti talebine uyarlama sinyali 0,88; boş imza/aile konutu savunmasına parasal güvence sinyali 0,67 döndü. Tanımlar somut kapsam ve dışlamalarla netleştirildi. Sonraki çağrıda aynı iki talepte bu sinyaller sırasıyla 0,15 ve 0,18 oldu; tespit 0,90, tahliye 0,76 kaldı. Bunlar tekil model yanıtlarıdır, genel hata oranı değildir.

Depozito, hasar ve ödenmeyen kira içeren karma örnekte güvence 0,94 ve alacak 0,85 çıktı. Kira ilişkisi bulunmadığı açıkça belirtilen fazla mesai örneğinde kapsam dışı sinyali 0,86 oldu. Bu iki örnek tanım düzeltmesinden önce çalıştırıldı; güncel sürüm için geniş regresyon değerlendirmesi yerine geçmez.

Tam metni okunmuş İstanbul BAM 36. HD E. 2024/5083, K. 2026/377 ile ilgisiz temsili ceza pasajı birlikte verildiğinde, ilgili karar 0,90; ilgisiz pasaj 0,02 sıralama sinyali aldı. Kaynak kimliği korundu ve eksik pasaj tam metin olarak işaretlenmedi. Bu deneme hukuki yorumun doğrulandığı anlamına gelmez. Karar bağlantısı [modül rehberindedir](moduller.md).

## Erişim durumu

- DeJure üzerinden arama ve tam metin alma çalıştı.
- Bağlı içtihat aracı üzerinden depozito kararı arandı ve tam metni alındı.
- Legaluga MCP arama ve karar getirme çağrıları hata verdi. Yerel köprü üzerinden yapılan denemede sunucu HTTP 500 döndürdü. Bu çalışmada Legaluga havuzundan başarılı veri alındığı veya 9 milyon kayıt sayısının doğrulandığı iddia edilmez. Skill, erişim yeniden sağlandığında kaynak kimliklerini koruyarak bu araçları kullanabilir.

API anahtarı kullanıcı tarafından belirtilen yerel env dosyasından okundu; anahtar ve özel env yolu public dosyalara eklenmedi. Canlı isteklerde müvekkil belgesi kullanılmadı.

## Yerel kontroller

`python -m unittest discover -s tests -v`: kaynak kimliklerinin korunması, sıralamada düşük puanlı adayların kaybolmaması, eksik yanıt ve geçersiz olasılıkların reddi, yinelenen kaynak ve belirsiz tam metin durumunun reddi.

`python scripts/validate.py`: 1.580 mevcut kararın ve mevzuatın bütünlüğü, yerel bağlantılar ve yardımcı komutlar. Skill şema kontrolü ayrıca çalıştırılır. Bu denetimler canlı servislerin her zaman erişilebilirliğini veya hukuki sonuçların doğruluğunu garanti etmez.
