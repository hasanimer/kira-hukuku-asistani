import json
from datetime import date
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from deadlines import add_months, calculate


class DeadlineTests(unittest.TestCase):
    def dates(self, rule, value, **kwargs):
        return calculate(rule, date.fromisoformat(value), **kwargs)['raw_dates']

    def test_month_is_not_thirty_days(self):
        self.assertEqual(self.dates('takvim', '2026-01-31', count=1, unit='ay')['ham_bitis'], '2026-02-28')
        self.assertEqual(self.dates('takvim', '2026-01-31', count=30, unit='gun')['ham_bitis'], '2026-03-02')

    def test_leap_day_and_direct_month_arithmetic(self):
        self.assertEqual(add_months(date(2024, 2, 29), 12), date(2025, 2, 28))
        self.assertEqual(add_months(date(2024, 1, 31), 1), date(2024, 2, 29))
        self.assertEqual(add_months(date(2026, 1, 31), 2), date(2026, 3, 31))
        self.assertEqual(add_months(date(2026, 3, 31), -1), date(2026, 2, 28))

    def test_notice_day_excluded_once(self):
        self.assertEqual(self.dates('tbk315', '2026-09-01')['otuzuncu_gun'], '2026-10-01')
        self.assertEqual(self.dates('takvim', '2026-09-01', count=2, unit='hafta')['ham_bitis'], '2026-09-15')

    def test_backward_threshold_not_rolled_forward(self):
        self.assertEqual(self.dates('tbk345', '2026-09-01')['otuz_gun_once_esigi'], '2026-08-02')

    def test_new_owner_waiting_period_separate_from_notice(self):
        self.assertEqual(self.dates('tbk351', '2026-01-31'), {
            'bir_aylik_bildirim_ham_sonu': '2026-02-28',
            'alti_ayin_ham_dolum_tarihi': '2026-07-31'})

    def test_undertaking_month_and_five_year_boundary(self):
        self.assertEqual(self.dates('tbk352', '2026-01-31')['bir_aylik_basvuru_ham_sonu'], '2026-02-28')
        self.assertEqual(self.dates('tbk344', '2020-09-01')['bes_yil_sonraki_yildonumu'], '2025-09-01')

    def test_bam_ten_year_example(self):
        self.assertEqual(self.dates('tbk347', '2010-11-01'), {
            'on_yillik_uzama_ham_sonu': '2020-11-01',
            'izleyen_ilk_uzama_yili_ham_sonu': '2021-11-01',
            'uc_ay_once_bildirim_esigi': '2021-08-01'})

    def test_uets_fifth_day_remains_sunday(self):
        self.assertEqual(self.dates('uets', '2026-09-01')['teblig_edilmis_sayilma_gunu'], '2026-09-06')

    def test_outputs_are_not_final_deadlines(self):
        for rule in ['takvim', 'tbk344', 'tbk345', 'tbk315', 'tbk351', 'tbk352', 'tbk347', 'uets']:
            args = {'count': 1, 'unit': 'gun'} if rule == 'takvim' else {}
            result = calculate(rule, date(2026, 1, 1), **args)
            self.assertEqual(result['status'], 'takvim_adayi_hukuki_kontrol_gerekli')
            self.assertTrue(result['pending_checks'])
            self.assertFalse(result['holiday_adjustment_applied'])
            self.assertFalse(result['mediation_adjustment_applied'])

    def test_invalid_options_are_not_silently_ignored(self):
        for kwargs in ({}, {'count': 0, 'unit': 'gun'}, {'count': -1, 'unit': 'ay'}):
            with self.assertRaises(ValueError):
                calculate('takvim', date(2026, 1, 1), **kwargs)
        with self.assertRaises(ValueError):
            calculate('uets', date(2026, 1, 1), count=30)

    def test_cli_portable_and_bad_date_fails_without_output(self):
        command = [sys.executable, str(ROOT / 'scripts/deadlines.py')]
        result = subprocess.run(command + ['tbk345', '2026-09-01'], cwd=ROOT.parent,
                                capture_output=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('raw_dates', json.loads(result.stdout))
        result = subprocess.run(command + ['tbk352', '2026-02-30'], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b'')


if __name__ == '__main__':
    unittest.main()
