"""Calendar candidates for rent-law periods, not an automatic legal deadline opinion."""
import argparse
from calendar import monthrange
from datetime import date, timedelta
import json
import sys

TBK = 'https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6098&MevzuatTur=1&MevzuatTertip=5'


def add_months(start, months):
    index = start.year * 12 + start.month - 1 + months
    year, month = divmod(index, 12)
    month += 1
    return date(year, month, min(start.day, monthrange(year, month)[1]))


def calculate(rule, start, *, count=None, unit=None):
    dates = {}
    checks = [
        'Başlangıç olayı, belge ve uygulanacak tarihli mevzuat doğrulanmalı.',
        'Tatil/adli tatil, durma, uzama ve özel sözleşme koşulları uygulanmadı.',
    ]
    source = TBK
    if rule == 'takvim':
        if count is None or count < 1 or unit not in ('gun', 'hafta', 'ay', 'yil'):
            raise ValueError('takvim için pozitif --count ve --unit gerekir')
        if unit in ('gun', 'hafta'):
            result = start + timedelta(days=count * (7 if unit == 'hafta' else 1))
        else:
            result = add_months(start, count * (12 if unit == 'yil' else 1))
        dates['ham_bitis'] = result
        basis = 'TBK 92 / HMK 92: hangi rejimin uygulanacağı ayrıca seçilir'
        meaning = 'Gün hesabında olay günü sayılmaz; ay/yıl hesabı karşılık gelen gündür.'
    else:
        if count is not None or unit is not None:
            raise ValueError('--count/--unit yalnız takvim kuralında kullanılabilir')
        if rule == 'tbk344':
            dates['bes_yil_sonraki_yildonumu'] = add_months(start, 60)
            basis = 'TBK 344/3'
            meaning = 'Başlangıçtan beş yıl sonrası aday dönem sınırı; bedelin etkisi TBK 345 ile ayrıca incelenir.'
            checks.append('Yeni sözleşme, önceki tespit ve kira dönemi; yıldönümü tek başına hak veya hüküm oluşturmaz.')
        elif rule == 'tbk345':
            dates['otuz_gun_once_esigi'] = start - timedelta(days=30)
            basis = 'TBK 345/2–3'
            meaning = 'Girdi hedef dönem başlangıcıdır. Çıktı dava veya yazılı artış bildirimi için 30 gün önce eşiğidir; genel dava açma son günü değildir.'
            checks.append('Artış hükmü, bildirimin ulaşması ve hedef dönemin sonuna kadar dava koşulunu ayrı incele; geri sayılan eşiği tatil diye ileri taşıma.')
        elif rule == 'tbk315':
            dates['otuzuncu_gun'] = start + timedelta(days=30)
            basis = 'TBK 315: yalnız konut ve çatılı işyeri, asgari 30 günlük süre'
            meaning = 'Girdi yazılı bildirimin yapıldığı tarihtir. Ertesi gün birinci gün; çıktı sürenin ham son günüdür, tahliye tarihi değildir.'
            checks.append('İhtarda daha uzun süre varsa onu esas al; diğer kiralar veya İİK takipleri için bu ön ayarı kullanma.')
        elif rule == 'tbk351':
            dates['bir_aylik_bildirim_ham_sonu'] = add_months(start, 1)
            dates['alti_ayin_ham_dolum_tarihi'] = add_months(start, 6)
            basis = 'TBK 351/1'
            meaning = 'Girdi edinme tarihidir. Bir ay bildirim penceresidir; altı ay bekleme süresidir, dava açma son günü değildir.'
            checks.append('İhtiyaç, yazılı bildirimin süresinde ulaşması ve altı ayın dolması doğrulanmalı; TBK 351/2 dönem sonu yolu ayrı değerlendirilir.')
        elif rule == 'tbk352':
            dates['bir_aylik_basvuru_ham_sonu'] = add_months(start, 1)
            basis = 'TBK 352/1: tahliye taahhüdü'
            meaning = 'Girdi taahhüt edilen boşaltma tarihidir; imza tarihi değildir. Bir ay 30 güne çevrilmez.'
            checks.append('Taahhüt geçerliliği, dava/icra yolu, arabuluculuk ve TBK 353 etkisi ayrıca incelenmeli; iki haklı ihtar için bu başlangıcı kullanma.')
        elif rule == 'tbk347':
            dates['on_yillik_uzama_ham_sonu'] = add_months(start, 120)
            target = add_months(start, 132)
            dates['izleyen_ilk_uzama_yili_ham_sonu'] = target
            dates['uc_ay_once_bildirim_esigi'] = add_months(target, -3)
            basis = 'TBK 347/1: belirli süreli konut/çatılı işyeri'
            meaning = 'Girdi ilk sözleşme süresinin hukuken belirlenmiş bitimidir; ilk kira başlangıcı değildir. İlk hedef = ilk süre bitimi + 10 uzama yılı + 1 izleyen yıl.'
            checks.append('Geçiş hükümleri, yeni sözleşmeler, süre/bitiş gününün yorumu ve yazılı bildirimin ulaşması incelenmeli; belirsiz süreliye uygulanmaz.')
        elif rule == 'uets':
            dates['teblig_edilmis_sayilma_gunu'] = start + timedelta(days=5)
            basis = '7201 sayılı Kanun 7/a'
            source = 'https://www.ptt.gov.tr/e-tebligat-sss'
            meaning = 'Girdi UETS adresine ulaşma günüdür; izleyen beşinci günün sonunda tebliğ edilmiş sayılır. SMS/e-posta veya okuma tarihi değildir.'
            checks = ['UETS delil kaydını doğrula; beşinci günü iş gününe taşıma.',
                      'Bundan sonraki başvuru süresini ayrı hesapla; onun tatil ve diğer etkilerini ayrıca incele.']
        else:
            raise ValueError(f'Bilinmeyen kural: {rule}')
    return {
        'rule': rule, 'input_date': start.isoformat(), 'basis': basis,
        'source_url': source, 'status': 'takvim_adayi_hukuki_kontrol_gerekli',
        'raw_dates': {key: value.isoformat() for key, value in dates.items()},
        'meaning': meaning, 'pending_checks': checks,
        'holiday_adjustment_applied': False,
        'mediation_adjustment_applied': False,
    }


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rule', choices=['takvim', 'tbk344', 'tbk345', 'tbk315',
                                       'tbk351', 'tbk352', 'tbk347', 'uets'])
    parser.add_argument('date', type=date.fromisoformat, help='YYYY-MM-DD; see rule-specific input meaning')
    parser.add_argument('--count', type=int)
    parser.add_argument('--unit', choices=['gun', 'hafta', 'ay', 'yil'])
    args = parser.parse_args()
    try:
        result = calculate(args.rule, args.date, count=args.count, unit=args.unit)
    except (ValueError, OverflowError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
