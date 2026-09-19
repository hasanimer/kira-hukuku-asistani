"""Süre ve dava takvimi hesaplayıcı: TBK 344, 345 ve 347 süre denetimleri.

Yerel, standart kütüphane dışında harici bağımlılık gerektirmeyen araç.
"""
from __future__ import annotations

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
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        # 29 Şubat artık yıl olmayan yıla denk gelirse 1 Mart olarak kabul edilir
        return date(d.year + years, 3, 1)


def sub_months(d: date, months: int) -> date:
    """Tarihten belirtilen ay kadar çıkarır, ay sonu sınırlarını korur."""
    year = d.year
    month = d.month - months
    while month <= 0:
        month += 12
        year -= 1
    # Hedef aydaki son günü bul
    if month in (1, 3, 5, 7, 8, 10, 12):
        max_day = 31
    elif month in (4, 6, 9, 11):
        max_day = 30
    else:
        # Şubat: artık yıl kontrolü
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
        max_day = 29 if is_leap else 28
    day = min(d.day, max_day)
    return date(year, month, day)


def get_lease_year(start_date: date, year_index: int) -> Tuple[date, date]:
    """Belirtilen kira yılının (1-indexed) başlangıç ve bitiş tarihlerini döner."""
    if year_index < 1:
        raise ValueError("Kira yılı 1 veya daha büyük olmalıdır")
    p_start = add_years(start_date, year_index - 1)
    p_end = add_years(start_date, year_index) - timedelta(days=1)
    return p_start, p_end


def compute_periods(start_date: date, count: int = 12) -> List[Dict[str, Any]]:
    """Başlangıçtan itibaren kira dönemleri çizelgesini oluşturur."""
    periods = []
    for i in range(1, count + 1):
        p_start, p_end = get_lease_year(start_date, i)
        is_hak_nesafet = (i >= 6) and ((i - 6) % 5 == 0)
        regime = "TBK 344/3 (Hak ve Nesafet / Emsal Rayiç)" if is_hak_nesafet else "TBK 344/1-2 (TÜFE 12 Aylık Değişim Tavanı)"
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
            "tbk347_uzama_yili": max(0, i - 1) if i > 1 else 0
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
    # 5 yıllık sürenin bittiği tarih: 5. kira yılının son günü
    five_years_end = add_years(start_date, 5) - timedelta(days=1)
    # İlk hak ve nesafet dönemi: 6. kira yılı başı
    first_hak_nesafet_start = add_years(start_date, 5)
    first_hak_nesafet_end = add_years(start_date, 6) - timedelta(days=1)

    # Hedef dönem belirlenmemişse:
    # Eğer dava veya ihtar tarihi varsa ona göre, yoksa ilk hak ve nesafet dönemini hedef al
    ref_date = action_date or notice_date or date.today()
    if target_period_start is None:
        # ref_date'in içine düştüğü veya takip eden ilk uygun dönemi bul
        # Kira yılını bul
        curr_idx = 1
        while True:
            p_s, p_e = get_lease_year(start_date, curr_idx)
            if p_s <= ref_date <= p_e:
                # ref_date bu dönemde; dava genellikle bir sonraki dönem için açılır
                target_period_start = add_years(start_date, curr_idx)
                break
            elif ref_date < p_s:
                target_period_start = p_s
                break
            curr_idx += 1
            if curr_idx > 100:
                target_period_start = first_hak_nesafet_start
                break

    # Hedef dönemin sınırlarını bul
    # target_period_start'ın kira yılı indeksini hesapla
    t_idx = 1
    while True:
        p_s, p_e = get_lease_year(start_date, t_idx)
        if p_s == target_period_start:
            target_start = p_s
            target_end = p_e
            target_year_idx = t_idx
            break
        elif p_s > target_period_start:
            # Tam eşleşmediyse en yakın dönem başını referans al
            target_start = p_s
            target_end = p_e
            target_year_idx = t_idx
            break
        t_idx += 1
        if t_idx > 120:
            target_start = target_period_start
            target_end = add_years(target_period_start, 1) - timedelta(days=1)
            target_year_idx = 6
            break

    # TBK 345/2: Yeni dönemin başlangıcından en geç otuz gün önceki tarih
    deadline_notice = target_start - timedelta(days=30)
    # TBK 345/3 & 345/2: Dava açma son günü (dönemin son günü)
    deadline_action = target_end

    # 5 yıl kontrolü (TBK 344/3)
    is_five_years_passed = (target_start >= first_hak_nesafet_start)
    is_rayic_eligible = is_five_years_passed and ((target_year_idx - 6) % 5 == 0)

    # TBK 345 kural denetimi
    applicable_from = None
    rule_applied = None
    timely_notice = None
    status_summary = []

    if has_increase_clause:
        rule_applied = "TBK 345/3 (Sözleşmede Artış Şartı Var)"
        status_summary.append("Sözleşmede artış şartı bulunduğundan 30 gün önceden ihtar tebliği zorunlu değildir.")
        status_summary.append(f"Dava, hedef dönemin sonuna ({format_date(deadline_action)}) kadar açılırsa, tespit kararı dönemin başından ({format_date(target_start)}) itibaren geçerli olur.")
        if action_date:
            if action_date <= deadline_action:
                applicable_from = target_start
                status_summary.append(f"Dava tarihi ({format_date(action_date)}) hedef dönem sonundan önce olduğundan karar {format_date(target_start)} tarihinden itibaren kiracıyı bağlar.")
            else:
                next_start = add_years(target_start, 1)
                applicable_from = next_start
                status_summary.append(f"Dava tarihi ({format_date(action_date)}) hedef dönem sonunu aştığından karar izleyen dönemden ({format_date(next_start)}) itibaren uygulanabilir.")
        else:
            applicable_from = target_start
    else:
        rule_applied = "TBK 345/2 (Sözleşmede Artış Şartı Yok)"
        status_summary.append(f"Sözleşmede artış şartı bulunmadığından, tespit kararının dönemin başından ({format_date(target_start)}) itibaren geçerli olması için en geç {format_date(deadline_notice)} tarihine kadar ihtarname tebliğ edilmiş veya dava açılmış olmalıdır.")

        notice_timely = (notice_date is not None and notice_date <= deadline_notice)
        action_timely = (action_date is not None and action_date <= deadline_notice)
        timely_notice = notice_timely

        if action_timely:
            applicable_from = target_start
            status_summary.append(f"Dava en geç 30 gün önce ({format_date(action_date)} <= {format_date(deadline_notice)}) açıldığından karar {format_date(target_start)} tarihinden itibaren geçerlidir.")
        elif notice_timely:
            status_summary.append(f"İhtarname 30 günden önce ({format_date(notice_date)} <= {format_date(deadline_notice)}) tebliğ edilmiştir.")
            if action_date:
                if action_date <= deadline_action:
                    applicable_from = target_start
                    status_summary.append(f"Dava dönem sonuna ({format_date(deadline_action)}) kadar açıldığından tespit kararı {format_date(target_start)} tarihinden itibaren yürürlüğe girer.")
                else:
                    next_start = add_years(target_start, 1)
                    applicable_from = next_start
                    status_summary.append(f"Dava hedef dönem sonundan sonra açıldığından izleyen dönem ({format_date(next_start)}) dikkate alınır.")
            else:
                applicable_from = target_start
                status_summary.append(f"Dava hedef dönemin sonuna ({format_date(deadline_action)}) kadar açılmalıdır.")
        else:
            # 30 gün şartı sağlanamadı
            next_start = add_years(target_start, 1)
            applicable_from = next_start
            if notice_date and notice_date > deadline_notice:
                status_summary.append(f"İhtar tebliğ tarihi ({format_date(notice_date)}) 30 günlük süreden ({format_date(deadline_notice)}) sonradır. Bu nedenle tespit kararı bu dönem için değil, izleyen kira dönemi başından ({format_date(next_start)}) itibaren geçerli olur.")
            elif action_date and action_date > deadline_notice:
                status_summary.append(f"Dava tarihi ({format_date(action_date)}) 30 günlük süreden sonradır ve süresinde ihtar tebliği yoktur. Tespit kararı izleyen kira dönemi başından ({format_date(next_start)}) itibaren hüküm doğurur.")
            else:
                status_summary.append(f"30 günlük ihtar/dava süresi kaçırılırsa tespit bir sonraki dönemden ({format_date(next_start)}) itibaren geçerli olur.")

    # Arabuluculuk notu
    mediation_required = True
    status_summary.append("01.09.2023 tarihinden itibaren kira uyuşmazlıklarında (TBK 344/345 dahil) dava şartı arabuluculuk (7445 s. K. / HUAK 18/B) zorunludur; dava açılmadan önce arabuluculuk son tutanağı düzenlenmiş olmalıdır.")

    return {
        "sozlesme_baslangic": format_date(start_date),
        "bes_yil_dolum_tarihi": format_date(five_years_end),
        "ilk_hak_nesafet_donemi": {
            "baslangic": format_date(first_hak_nesafet_start),
            "bitis": format_date(first_hak_nesafet_end),
            "kira_yili": 6
        },
        "hedef_donem": {
            "baslangic": format_date(target_start),
            "bitis": format_date(target_end),
            "kira_yili": target_year_idx,
            "hak_nesafet_uygulanabilir": is_rayic_eligible,
            "bes_yil_doldu_mu": is_five_years_passed,
            "rejim": "TBK 344/3 Emsal Rayiç ve Hakkaniyet" if is_rayic_eligible else ("TBK 344/1-2 TÜFE Tavanı (Ara Yıl)" if is_five_years_passed else "TBK 344/1-2 TÜFE Tavanı (İlk 5 Yıl)")
        },
        "sure_analizi": {
            "artis_sarti_var": has_increase_clause,
            "ihtar_tarihi": format_date(notice_date) if notice_date else None,
            "dava_tarihi": format_date(action_date) if action_date else None,
            "en_gec_ihtar_teblig_tarihi": format_date(deadline_notice),
            "en_gec_dava_tarihi": format_date(deadline_action),
            "uygulanan_kural": rule_applied,
            "kararin_gecerlilik_tarihi": format_date(applicable_from) if applicable_from else None,
            "arabuluculuk_zorunlu": mediation_required
        },
        "tespitler": status_summary
    }


def compute_tahliye_10yil(start_date: date, initial_years: int = 1) -> Dict[str, Any]:
    """TBK 347 uyarınca 10 yıllık uzama süresi sonunda fesih takvimini hesaplar."""
    if initial_years < 1:
        raise ValueError("İlk sözleşme süresi en az 1 yıl olmalıdır")

    # İlk sözleşmenin sona erdiği tarih
    contract_end = add_years(start_date, initial_years) - timedelta(days=1)
    # 10 yıllık uzama süresinin başlangıcı
    extension_start = add_years(start_date, initial_years)
    # 10 yıllık uzama süresinin bittiği tarih (toplam initial_years + 10 yıl)
    ten_year_extension_end = add_years(start_date, initial_years + 10) - timedelta(days=1)
    total_years_passed = initial_years + 10

    # TBK 347/1: "bu süreyi izleyen her uzama yılının bitiminden en az üç ay önce bildirimde bulunmak koşuluyla"
    # İlk fesih hakkının doğduğu dönem bitimi: 10 yıllık uzamanın bittiği tarih (1+10=11. yıl sonu)
    first_termination_target_end = ten_year_extension_end

    # En geç bildirim (ihtar) tebliğ tarihi: bitimden en az 3 ay önce kiracıya ULAŞMIŞ olmalı
    latest_notice_date = sub_months(first_termination_target_end, 3)

    # Dava açma süresi: Dönem bitimini takip eden 1 ay içinde
    action_window_start = first_termination_target_end + timedelta(days=1)
    action_window_end = add_years(action_window_start, 0) + timedelta(days=30)  # 1 aylık süre

    # Sonraki uzama yılları takvimi (ilk 3 takip eden yıl)
    subsequent_years = []
    for extra in range(1, 4):
        target_end = add_years(first_termination_target_end, extra)
        notice_deadline = sub_months(target_end, 3)
        action_start = target_end + timedelta(days=1)
        subsequent_years.append({
            "uzama_yili": 10 + extra,
            "toplam_kira_yili": total_years_passed + extra,
            "donem_sonu": format_date(target_end),
            "en_gec_ihtar_tarihi": format_date(notice_deadline),
            "tahliye_dava_donemi": f"{format_date(action_start)} - {format_date(action_start + timedelta(days=30))}"
        })

    notes = [
        f"TBK 347 uyarınca kiraya veren sözleşme süresinin bitimine dayanarak sözleşmeyi feshedemez.",
        f"Ancak {initial_years} yıllık sözleşme süresi + 10 yıllık uzama süresi = toplam {total_years_passed} yıl dolduğunda sebepsiz fesih hakkı doğar.",
        f"Fesih bildiriminin (ihtarname) en geç {format_date(latest_notice_date)} tarihinde kiracıya tebliğ edilmiş olması şarttır (en az 3 ay önce).",
        f"Tahliye davası kural olarak dönem sonunu ({format_date(first_termination_target_end)}) takip eden 1 ay içinde açılır. Süresinde ihtar tebliğ edilmişse TBK 353 uyarınca izleyen uzama yılı sonuna kadar da açılabilir.",
        f"01.09.2023 sonrası tahliye davalarında dava açılmadan önce dava şartı arabuluculuk (HUAK 18/B) tamamlanmalıdır."
    ]

    return {
        "sozlesme_baslangic": format_date(start_date),
        "ilk_sozlesme_suresi_yil": initial_years,
        "ilk_sozlesme_bitis": format_date(contract_end),
        "on_yillik_uzama_baslangic": format_date(extension_start),
        "on_yillik_uzama_bitis": format_date(ten_year_extension_end),
        "toplam_yil": total_years_passed,
        "ilk_fesih_donem_sonu": format_date(first_termination_target_end),
        "en_gec_ihtar_teblig_tarihi": format_date(latest_notice_date),
        "tahliye_dava_acma_araligi": f"{format_date(action_window_start)} - {format_date(action_window_end)}",
        "izleyen_uzama_yillari": subsequent_years,
        "tespitler": notes
    }


def render_text_tespit(res: Dict[str, Any]) -> str:
    lines = []
    lines.append("=== KİRA TESPİTİ SÜRE VE HEDEF DÖNEM ANALİZİ (TBK 344 / 345) ===")
    lines.append(f"Sözleşme Başlangıcı        : {res['sozlesme_baslangic']}")
    lines.append(f"5 Yıllık Sürenin Dolumu     : {res['bes_yil_dolum_tarihi']}")
    lines.append(f"İlk Hak ve Nesafet Dönemi   : {res['ilk_hak_nesafet_donemi']['baslangic']} - {res['ilk_hak_nesafet_donemi']['bitis']} (6. Kira Yılı)")
    lines.append("")
    lines.append(f"--- İncelenen Hedef Dönem: {res['hedef_donem']['baslangic']} - {res['hedef_donem']['bitis']} ({res['hedef_donem']['kira_yili']}. Kira Yılı) ---")
    lines.append(f"Uygulanacak Hukuki Rejim   : {res['hedef_donem']['rejim']}")
    lines.append(f"Artış Şartı Durumu         : {'Var (TBK 345/3)' if res['sure_analizi']['artis_sarti_var'] else 'Yok (TBK 345/2)'}")
    lines.append(f"En Geç İhtar Tebliğ Tarihi : {res['sure_analizi']['en_gec_ihtar_teblig_tarihi']} (Yeni dönemden en geç 30 gün önce)")
    lines.append(f"En Geç Dava Açma Tarihi    : {res['sure_analizi']['en_gec_dava_tarihi']} (Dönem sonu)")
    if res['sure_analizi']['ihtar_tarihi']:
        lines.append(f"Bildirilen İhtar Tarihi    : {res['sure_analizi']['ihtar_tarihi']}")
    if res['sure_analizi']['dava_tarihi']:
        lines.append(f"Bildirilen Dava Tarihi     : {res['sure_analizi']['dava_tarihi']}")
    if res['sure_analizi']['kararin_gecerlilik_tarihi']:
        lines.append(f"Tespitin Hüküm Tarihi      : {res['sure_analizi']['kararin_gecerlilik_tarihi']} tarihinden itibaren geçerli")
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
    lines.append(f"Sebepsiz Fesih Hakkı       : {res['ilk_fesih_donem_sonu']} tarihi itibarıyla doğar (Toplam {res['toplam_yil']}. yıl sonu)")
    lines.append(f"En Geç İhtar Tebliğ Tarihi : {res['en_gec_ihtar_teblig_tarihi']} (Dönem bitiminden en az 3 ay önce tebliğ şartı)")
    lines.append(f"Tahliye Davası Açma Süresi : {res['tahliye_dava_acma_araligi']} (Dönem bitiminden itibaren 1 ay)")
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
        status_347 = f"{p['tbk347_uzama_yili']}. uzama yılı" if p['tbk347_uzama_yili'] > 0 else "İlk sözleşme yılı"
        lines.append(f"{p['kira_yili']:<10} {p['baslangic'] + ' - ' + p['bitis']:<25} {p['rejim']:<35} {status_347}")
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    # Alt komut: tespit
    p_tespit = sub.add_parser("tespit", help="TBK 344/345 kira tespiti ve süre denetimi")
    p_tespit.add_argument("--baslangic", "-b", required=True, help="Kira sözleşmesi başlangıç tarihi (GG.AA.YYYY veya YYYY-AA-GG)")
    group = p_tespit.add_mutually_exclusive_group()
    group.add_argument("--artis-sarti", dest="artis_sarti", action="store_true", default=False, help="Sözleşmede artış şartı var")
    group.add_argument("--artis-sarti-yok", dest="artis_sarti", action="store_false", help="Sözleşmede artış şartı yok")
    p_tespit.add_argument("--ihtar-tarihi", "-i", help="Kiracıya tebliğ edilen ihtarname tarihi (GG.AA.YYYY)")
    p_tespit.add_argument("--dava-tarihi", "-d", help="Açılmış veya planlanan dava tarihi (GG.AA.YYYY)")
    p_tespit.add_argument("--hedef-donem", "-t", help="Tespiti istenen spesifik dönem başlangıcı (GG.AA.YYYY)")
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

    except (ValueError, OSError) as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
