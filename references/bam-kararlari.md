# BAM seçkisi

İki kararın tam metni `data/bam-selected.jsonl` içindedir. Ana havuzla birlikte aranır; bağımsız hukukçu doğrulaması yapılmamıştır. Kaynakta görülen metin hataları düzeltilmeden korunmuş, kullanım sınırları ayrı notlanmıştır. Bu kayıtların etiketleri JEV çıktısı değil, asistanın tam metin incelemesidir.

## Adana BAM 5. Hukuk Dairesi

**2024/1566 E., 2026/82 K., 07.01.2026** — [Kaynak](https://app.dejure.ai/dokuman/34ffba87-e4ff-4051-9441-4a72fe6564bd).

İnternet ilanlarından hareket eden, kira bedelini hangi somut kriterlerle belirlediği açıklanmayan bilirkişi raporu nedeniyle ilk derece kararı kaldırılmış ve dosya iade edilmiştir. Emsal sözleşmelerin toplanması, taşınmazların ayrı ayrı incelenmesi ve karşılaştırmanın somutlaştırılması konularında araştırma adayıdır. Bilirkişi raporuna itirazda kullanılabilir.

İlk derece kararında geçen %15 indirim, BAM'ın onayladığı genel bir indirim oranı olarak sunulmamalıdır. Taraf itirazları ile BAM gerekçesini ayır.

## Denizli BAM 6. Hukuk Dairesi

**2025/925 E., 2025/385 K., 22.10.2025** — [Kaynak](https://app.dejure.ai/dokuman/615160e1-265c-486a-9b9a-4a82061a94b6).

Artış şartı olmayan sözleşmede ihtar, hedef kira dönemi ve işyeri bedelinin net/brüt niteliği için sınırlı araştırma adayıdır. Kira bedeline yönelik başvurular reddedilmiş, vekâlet ücreti yönünden ilk derece kararı kaldırılarak yeniden hüküm kurulmuştur; bütün kararın onandığı söylenmemelidir.

Metin TBK 344'ü eski ÜFE ifadesiyle aktarmaktadır. Güncel mevzuat yerine kullanılmaz. Vekâlet ücreti hesabı ve taraf ifadelerinde tutarsızlık vardır; bu kısım ücret hesabına veya genel kurala dayanak yapılmaz. Talepteki 7.000 TL ile hükümdeki 7.650 TL brüt bedel, talebin net/brüt niteliği dosyadan doğrulanmadan karşılaştırılmaz.

## Seçime alınmayan aday

Antalya BAM 6. HD, 2022/1456 E., 2024/385 K., 19.02.2024 tam metni incelendi. Gerekçede davacının katılma istinafı kesinlik nedeniyle reddedilirken sonuç bölümünde taraf sıfatları ve ret türü farklı aktarılıyor. Bu metin uyuşmazlığı çözülmeden örnek seçkiye alınmadı. Tam metni pakete kopyalanmadı.

## Erişim

```sh
python scripts/pool.py search bilirkişi --court-type bam
python scripts/pool.py get 34ffba87-e4ff-4051-9441-4a72fe6564bd
python scripts/pool.py get 615160e1-265c-486a-9b9a-4a82061a94b6
```

Sonuçlardaki `research_notes` asistan değerlendirmesidir; mahkeme metni değildir. Atıf ve alıntıdan önce `get` ile metni oku ve `quote` ile birebir eşleşmeyi kontrol et. Bu iki örnek ülke çapındaki BAM uygulamasının tamamını temsil etmez.
