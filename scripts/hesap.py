"""Süre ve dava takvimi hesaplayıcı: TBK 344, 345 ve 347 süre denetimleri.

Yerel, standart kütüphane dışında harici bağımlılık gerektirmeyen araç.
"""
from __future__ import annotations

from deadlines import add_months, calculate

import argparse
from datetime import date, datetime, timedelta
import json
import sys
from typing import Any, Dict, List, Optional, Tuple


def parse_date(value: str) -> date:
    """Tarih dizgisini (DD.MM.YYYY, YYYY-MM-DD veya DD/MM/YYYY) date nesnesine çevirir."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Tarih boş olamaz")
    cleaned = value.strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Geçersiz tarih biçimi: '{value}'. Desteklenenler: GG.AA.YYYY veya YYYY-AA-GG")


def format_date(d: date) -> str:
    """Tarihi GG.AA.YYYY biçiminde döner."""
    return d.strftime("%d.%m.%Y")


def format_iso(d: date) -> str:
    """Tarihi YYYY-MM-DD biçiminde döner."""
    return d.isoformat()


def add_years(d: date, years: int) -> date:
    """Tarihe belirtilen yıl kadar ekler, 29 Şubat durumunu güvenle yönetir."""
    return add_months(d, years * 12)


def sub_months(d: date, months: int) -> date:
    """Tarihten belirtilen ay kadar çıkarır, ay sonu sınırlarını korur."""
    return add_months(d, -months)


def get_lease_year(start_date: date, year_index: int) -> Tuple[date, date]:
    """Belirtilen kira yılının (1-indexed) başlangıç ve bitiş tarihlerini döner."""
    if year_index < 1:
        raise ValueError("Kira yılı 1 veya daha büyük olmalıdır")
    p_start = add_years(start_date, year_index - 1)
    p_end = add_years(start_date, year_index) - timedelta(days=1)
    return p_start, p_end


def compute_periods(start_date: date, count: int = 12) -> List[Dict[str, Any]]:
    """Başlangıçtan itibaren kira dönemleri çizelgesini oluşturur."""
    if not 1 <= count <= 120:
        raise ValueError("Dönem sayısı 1–120 arasında olmalı")
    periods = []
    for i in range(1, count + 1):
        p_start, p_end = get_lease_year(start_date, i)
        is_hak_nesafet = (i >= 6) and ((i - 6) % 5 == 0)
        regime = "TBK 344/3 (Hak ve Nesafet inceleme adayı)" if is_hak_nesafet else "Artış rejimi ayrıca incelenmeli"
        if i >= 6 and not is_hak_nesafet:
            regime += " [Hak ve Nesafet Sonrası Ara Yıl]"

        periods.append({
            "kira_yili": i,
            "baslangic": format_date(p_start),
            "bitis": format_date(p_end),
            "baslangic_iso": format_iso(p_start),
            "bitis_iso": format_iso(p_end),
            "rejim": regime,
            "hak_nesafet_yili": is_hak_nesafet,
            "tbk347_uzama_yili": None,
            "status": "takvim_adayi_hukuki_kontrol_gerekli"
        })
    return periods


def compute_tespit(
    start_date: date,
    has_increase_clause: bool,
    notice_date: Optional[date] = None,
    action_date: Optional[date] = None,
    target_period_start: Optional[date] = None
) -> Dict[str, Any]:
    """TBK 344 ve 345 kapsamında kira tespiti süre ve hedef dönem analizini gerçekleştirir."""
    if target_period_start is None:
        raise ValueError("Hedef dönem açıkça belirtilmeli: --hedef-donem GG.AA.YYYY")
    target_year_idx = target_period_start.year - start_date.year + 1
    if target_year_idx < 1 or add_years(start_date, target_year_idx - 1) != target_period_start:
        raise ValueError("Hedef tarih kira yılı başlangıcıyla eşleşmiyor; sessizce sonraki döneme taşınmaz")
    target_start, target_end = get_lease_year(start_date, target_year_idx)
    first = add_years(start_date, 5)
    deadline_notice = target_start - timedelta(days=30)
    condition = None
    if action_date is not None:
        condition = action_date <= target_end and (
            has_increase_clause or action_date <= deadline_notice or
            (notice_date is not None and notice_date <= deadline_notice))
    candidate = target_start if condition is True else None
    notes = [
        "Yalnız tarih koşulu denetlenir; belge, sözleşme ve uygulanacak mevzuat ayrıca doğrulanır.",
        "Hedef dönem sonu genel dava açma son günü değildir; TBK 345 dönem etkisi bakımından incelenir.",
        "Tatil, arabuluculuk, önceki tespit ve yeni sözleşme etkileri hesaplanmadı.",
        "Dönem çizelgesi yıllık dönem varsayımıdır; mahkemenin hangi dönemden hüküm kuracağını belirlemez.",
    ]
    if condition is None:
        notes.append("Dava tarihi verilmedi; hedef döneme etki henüz doğrulanamaz.")
    elif condition:
        notes.append("Verilen tarihlerle hedef dönem için TBK 345 tarih koşulu aday olarak sağlanıyor.")
    else:
        notes.append("Verilen tarihler hedef döneme etkiyi desteklemiyor; sonraki dönem otomatik seçilmez, ayrıca araştırılır.")
    rayic_cycle = target_year_idx >= 6 and (target_year_idx - 6) % 5 == 0
    return {
        "status": "takvim_adayi_hukuki_kontrol_gerekli",
        "sozlesme_baslangic": format_date(start_date),
        "bes_yil_dolum_tarihi": format_date(first - timedelta(days=1)),
        "ilk_hak_nesafet_donemi": {
            "baslangic": format_date(first),
            "bitis": format_date(add_years(start_date, 6) - timedelta(days=1)), "kira_yili": 6},
        "hedef_donem": {
            "baslangic": format_date(target_start), "bitis": format_date(target_end),
            "kira_yili": target_year_idx, "hak_nesafet_uygulanabilir": None,
            "bes_yillik_dongu_adayi": rayic_cycle, "bes_yil_doldu_mu": target_start >= first,
            "rejim": "Hukuki inceleme gerekli; takvim döngüsü tek başına uygulanabilirliği belirlemez"},
        "sure_analizi": {
            "artis_sarti_var": has_increase_clause,
            "ihtar_tarihi": format_date(notice_date) if notice_date else None,
            "dava_tarihi": format_date(action_date) if action_date else None,
            "en_gec_ihtar_teblig_tarihi": format_date(deadline_notice),
            "en_gec_dava_tarihi": format_date(target_end),
            "uygulanan_kural": "TBK 345/3" if has_increase_clause else "TBK 345/2",
            "kararin_gecerlilik_tarihi": None,
            "aday_etki_tarihi": format_date(candidate) if candidate else None,
            "hedef_donem_tarih_kosulu": condition,
            "arabuluculuk_zorunlu": None},
        "alan_notu": "en_gec_dava_tarihi eski alan adıdır: yalnız hedef dönemin ham sonunu gösterir; genel hak düşümü veya tatil düzeltmesi değildir.",
        "tespitler": notes,
    }


def compute_tahliye_10yil(start_date: date, initial_years: int = 1) -> Dict[str, Any]:
    """TBK 347 uyarınca 10 yıllık uzama süresi sonunda fesih takvimini hesaplar."""
    if initial_years < 1:
        raise ValueError("İlk sözleşme süresi en az 1 yıl olmalıdır")
    first_end = add_years(start_date, initial_years)
    calculation = calculate('tbk347', first_end)
    raw = calculation['raw_dates']
    target = date.fromisoformat(raw['izleyen_ilk_uzama_yili_ham_sonu'])
    following = []
    for extra in range(1, 4):
        boundary = add_years(start_date, initial_years + 11 + extra)
        following.append({
            "uzama_yili": 11 + extra, "toplam_kira_yili": initial_years + 11 + extra,
            "donem_sonu": format_date(boundary),
            "en_gec_ihtar_tarihi": format_date(sub_months(boundary, 3)),
            "tahliye_dava_donemi": None})
    return {
        "status": calculation['status'],
        "sozlesme_baslangic": format_date(start_date),
        "ilk_sozlesme_suresi_yil": initial_years,
        "ilk_sozlesme_bitis": format_date(first_end),
        "on_yillik_uzama_baslangic": format_date(first_end),
        "on_yillik_uzama_bitis": format_date(add_years(start_date, initial_years + 10)),
        "toplam_yil": initial_years + 11,
        "ilk_fesih_donem_sonu": format_date(target),
        "en_gec_ihtar_teblig_tarihi": format_date(date.fromisoformat(raw['uc_ay_once_bildirim_esigi'])),
        "tahliye_dava_acma_araligi": None,
        "izleyen_uzama_yillari": following,
        "tespitler": calculation['pending_checks'] + [
            "Tarihler yıldönümü sınırlarıdır; bir önceki kullanım günüyle karıştırılmamalı.",
            "İlk sözleşme süresi + 10 uzama yılı + izleyen 1 yıl esas alınır.",
            "TBK 347 için otomatik bir aylık dava penceresi veya TBK 353 uzaması üretilmez.",
            "Dava yolu, arabuluculuk ve geçiş hükümleri somut dosyada incelenmelidir."],
    }


def render_text_tespit(res: Dict[str, Any]) -> str:
    lines = []
    lines.append("=== KİRA TESPİTİ SÜRE VE HEDEF DÖNEM ANALİZİ (TBK 344 / 345) ===")
    lines.append(f"Sözleşme Başlangıcı        : {res['sozlesme_baslangic']}")
    lines.append(f"5 Yıllık Sürenin Dolumu     : {res['bes_yil_dolum_tarihi']}")
    lines.append(f"İlk Hak ve Nesafet Dönemi   : {res['ilk_hak_nesafet_donemi']['baslangic']} - {res['ilk_hak_nesafet_donemi']['bitis']} (6. Kira Yılı)")
    lines.append("")
    lines.append(f"--- İncelenen Hedef Dönem: {res['hedef_donem']['baslangic']} - {res['hedef_donem']['bitis']} ({res['hedef_donem']['kira_yili']}. Kira Yılı) ---")
    lines.append(f"İncelenecek Hukuki Rejim   : {res['hedef_donem']['rejim']}")
    lines.append(f"Artış Şartı Durumu         : {'Var (TBK 345/3)' if res['sure_analizi']['artis_sarti_var'] else 'Yok (TBK 345/2)'}")
    lines.append(f"En Geç İhtar Tebliğ Tarihi : {res['sure_analizi']['en_gec_ihtar_teblig_tarihi']} (Yeni dönemden en geç 30 gün önce)")
    lines.append(f"Hedef Dönem Ham Sonu    : {res['sure_analizi']['en_gec_dava_tarihi']} (Dönem sonu)")
    if res['sure_analizi']['ihtar_tarihi']:
        lines.append(f"Bildirilen İhtar Tarihi    : {res['sure_analizi']['ihtar_tarihi']}")
    if res['sure_analizi']['dava_tarihi']:
        lines.append(f"Bildirilen Dava Tarihi     : {res['sure_analizi']['dava_tarihi']}")
    if res['sure_analizi']['aday_etki_tarihi']:
        lines.append(f"Aday Dönem Etkisi         : {res['sure_analizi']['aday_etki_tarihi']} (hukuki kontrol gerekli)")
    lines.append("")
    lines.append("Hukuki Değerlendirmeler:")
    for note in res['tespitler']:
        lines.append(f"  • {note}")
    return "\n".join(lines)


def render_text_tahliye(res: Dict[str, Any]) -> str:
    lines = []
    lines.append("=== 10 YILLIK UZAMA SÜRESİ SONU TAHLİYE TAKVİMİ (TBK 347) ===")
    lines.append(f"Sözleşme Başlangıcı        : {res['sozlesme_baslangic']} ({res['ilk_sozlesme_suresi_yil']} Yıl Süreli)")
    lines.append(f"İlk Sözleşme Sonu          : {res['ilk_sozlesme_bitis']}")
    lines.append(f"10 Yıllık Uzama Dönemi     : {res['on_yillik_uzama_baslangic']} - {res['on_yillik_uzama_bitis']}")
    lines.append(f"İlk Hedef Yıldönümü        : {res['ilk_fesih_donem_sonu']} takvim adayı (Toplam {res['toplam_yil']}. yıl sonu)")
    lines.append(f"En Geç İhtar Tebliğ Tarihi : {res['en_gec_ihtar_teblig_tarihi']} (Dönem bitiminden en az 3 ay önce tebliğ şartı)")
    lines.append("Dava penceresi otomatik hesaplanmadı; hukuki inceleme gerekli.")
    lines.append("")
    lines.append("Takip Eden Uzama Yılları:")
    for sub in res['izleyen_uzama_yillari']:
        lines.append(f"  • {sub['uzama_yili']}. Uzama Yılı (Toplam {sub['toplam_kira_yili']}. yıl): Dönem sonu {sub['donem_sonu']}, en geç ihtar {sub['en_gec_ihtar_tarihi']}")
    lines.append("")
    lines.append("Hukuki Tespitler:")
    for note in res['tespitler']:
        lines.append(f"  • {note}")
    return "\n".join(lines)


def render_text_donemler(periods: List[Dict[str, Any]], start_str: str) -> str:
    lines = []
    lines.append(f"=== KİRA DÖNEMLERİ ÇİZELGESİ (Başlangıç: {start_str}) ===")
    lines.append(f"{'Kira Yılı':<10} {'Dönem Aralığı':<25} {'Rejim / Hak ve Nesafet':<35} {'TBK 347 Durumu'}")
    lines.append("-" * 90)
    for p in periods:
        status_347 = "İlk sözleşme süresi ayrıca gerekli"
        lines.append(f"{p['kira_yili']:<10} {p['baslangic'] + ' - ' + p['bitis']:<25} {p['rejim']:<35} {status_347}")
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    # Alt komut: tespit
    p_tespit = sub.add_parser("tespit", help="TBK 344/345 kira tespiti ve süre denetimi")
    p_tespit.add_argument("--baslangic", "-b", required=True, help="Kira sözleşmesi başlangıç tarihi (GG.AA.YYYY veya YYYY-AA-GG)")
    group = p_tespit.add_mutually_exclusive_group(required=True)
    group.add_argument("--artis-sarti", dest="artis_sarti", action="store_true", default=False, help="Sözleşmede artış şartı var")
    group.add_argument("--artis-sarti-yok", dest="artis_sarti", action="store_false", help="Sözleşmede artış şartı yok")
    p_tespit.add_argument("--ihtar-tarihi", "-i", help="Kiracıya tebliğ edilen ihtarname tarihi (GG.AA.YYYY)")
    p_tespit.add_argument("--dava-tarihi", "-d", help="Açılmış veya planlanan dava tarihi (GG.AA.YYYY)")
    p_tespit.add_argument("--hedef-donem", "-t", required=True, help="Tespiti istenen spesifik dönem başlangıcı (GG.AA.YYYY)")
    p_tespit.add_argument("--json", action="store_true", help="JSON formatında çıktı üret")

    # Alt komut: tahliye-10yil
    p_tahliye = sub.add_parser("tahliye-10yil", help="TBK 347 10 yıllık uzama süresi sonu tahliye takvimi")
    p_tahliye.add_argument("--baslangic", "-b", required=True, help="Kira sözleşmesi başlangıç tarihi (GG.AA.YYYY veya YYYY-AA-GG)")
    p_tahliye.add_argument("--sure-yil", "-s", type=int, default=1, help="İlk sözleşme süresi yıl olarak (varsayılan: 1)")
    p_tahliye.add_argument("--json", action="store_true", help="JSON formatında çıktı üret")

    # Alt komut: donemler
    p_donem = sub.add_parser("donemler", help="Kronolojik kira dönemleri ve hukuki rejim çizelgesi")
    p_donem.add_argument("--baslangic", "-b", required=True, help="Kira sözleşmesi başlangıç tarihi (GG.AA.YYYY veya YYYY-AA-GG)")
    p_donem.add_argument("--yil", "-n", type=int, default=12, help="Gösterilecek kira yılı sayısı (varsayılan: 12)")
    p_donem.add_argument("--json", action="store_true", help="JSON formatında çıktı üret")

    args = parser.parse_args()

    try:
        start_d = parse_date(args.baslangic)

        if args.command == "tespit":
            notice_d = parse_date(args.ihtar_tarihi) if args.ihtar_tarihi else None
            action_d = parse_date(args.dava_tarihi) if args.dava_tarihi else None
            target_d = parse_date(args.hedef_donem) if args.hedef_donem else None
            res = compute_tespit(
                start_date=start_d,
                has_increase_clause=args.artis_sarti,
                notice_date=notice_d,
                action_date=action_d,
                target_period_start=target_d
            )
            if args.json:
                print(json.dumps(res, ensure_ascii=False, indent=2))
            else:
                print(render_text_tespit(res))

        elif args.command == "tahliye-10yil":
            res = compute_tahliye_10yil(start_d, initial_years=args.sure_yil)
            if args.json:
                print(json.dumps(res, ensure_ascii=False, indent=2))
            else:
                print(render_text_tahliye(res))

        elif args.command == "donemler":
            periods = compute_periods(start_d, count=args.yil)
            if args.json:
                print(json.dumps({
                    "baslangic": format_date(start_d),
                    "yil_sayisi": args.yil,
                    "donemler": periods
                }, ensure_ascii=False, indent=2))
            else:
                print(render_text_donemler(periods, format_date(start_d)))

    except (ValueError, OSError, OverflowError) as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
