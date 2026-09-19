# Kira tespiti doğrudan havuzu — kör yeniden tarama

Yeniden taranan: **1658 karar**. İnsan doğrulaması değildir.

Dahil: **1577** · Hariç: **81** · İnsan incelemesi: **0**

Önceden tam metinle dışlanan 13 kararın yeniden tarama dağılımı: `{'haric': 12, 'dahil': 1}`.

Yeni model dışlama adayı: **69** · Önceki asistan dışlamaları da uygulanan sıkı çalışma havuzu: **1576**

- `topic-rescan-keep.jsonl`: Sıkı ikinci taramada korpusta tutulanlar.
- `topic-rescan-exclude.jsonl`: Sıkı ikinci taramada kapsam dışı görülenler.
- `topic-rescan-review.jsonl`: Kararsız olup insan incelemesi gerekenler.

- `topic-rescan-new-exclusions.jsonl`: Önceden asistan tarafından incelenmemiş yeni dışlama adayları.
- `topic-rescan-assistant-adjusted.jsonl`: Sıkı taramada dahil kalan ve bilinen 13 yanlış olumluyu içermeyen çalışma havuzu.

Aynı JEV modeli farklı ve daha sıkı bir yönergeyle yeniden kullanılmıştır; sonuç bağımsız model doğrulaması veya insan doğruluğu ölçümü değildir.
