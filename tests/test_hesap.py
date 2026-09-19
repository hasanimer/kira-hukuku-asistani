"""Unit tests for scripts/hesap.py."""
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from hesap import (
    parse_date,
    add_years,
    sub_months,
    compute_periods,
    compute_tespit,
    compute_tahliye_10yil
)


class HesapTests(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(parse_date("01.07.2020"), date(2020, 7, 1))
        self.assertEqual(parse_date("2020-07-01"), date(2020, 7, 1))
        self.assertEqual(parse_date("01/07/2020"), date(2020, 7, 1))
        with self.assertRaises(ValueError):
            parse_date("")
        with self.assertRaises(ValueError):
            parse_date("invalid-date")
        with self.assertRaises(ValueError):
            parse_date("32.01.2020")

    def test_add_years_and_leap_year(self):
        self.assertEqual(add_years(date(2021, 5, 10), 3), date(2024, 5, 10))
        # 29 Şubat'tan 1 yıl sonrası artık olmayan yılda 1 Mart olmalı
        self.assertEqual(add_years(date(2020, 2, 29), 1), date(2021, 3, 1))
        # 29 Şubat'tan 4 yıl sonrası (2024 artık yıl) 29 Şubat olmalı
        self.assertEqual(add_years(date(2020, 2, 29), 4), date(2024, 2, 29))

    def test_sub_months(self):
        # 31 Aralık - 3 ay = 30 Eylül
        self.assertEqual(sub_months(date(2025, 12, 31), 3), date(2025, 9, 30))
        # 31 Mayıs - 3 ay = 28 Şubat (2025 artık yıl değil)
        self.assertEqual(sub_months(date(2025, 5, 31), 3), date(2025, 2, 28))
        # Yıl devri: 15 Ocak - 3 ay = 15 Ekim önceki yıl
        self.assertEqual(sub_months(date(2025, 1, 15), 3), date(2024, 10, 15))

    def test_compute_periods_and_hak_nesafet(self):
        start = date(2018, 7, 1)
        periods = compute_periods(start, count=12)
        self.assertEqual(len(periods), 12)

        # 1. Kira Yılı: 01.07.2018 - 30.06.2019
        self.assertEqual(periods[0]["baslangic"], "01.07.2018")
        self.assertEqual(periods[0]["bitis"], "30.06.2019")
        self.assertFalse(periods[0]["hak_nesafet_yili"])

        # 5. Kira Yılı: 01.07.2022 - 30.06.2023 (5 yılın dolumu)
        self.assertEqual(periods[4]["bitis"], "30.06.2023")
        self.assertFalse(periods[4]["hak_nesafet_yili"])

        # 6. Kira Yılı (İlk hak ve nesafet): 01.07.2023 - 30.06.2024
        self.assertEqual(periods[5]["baslangic"], "01.07.2023")
        self.assertTrue(periods[5]["hak_nesafet_yili"])
        self.assertIn("Hak ve Nesafet", periods[5]["rejim"])

        # 7-10. Kira Yılları: Ara yıl
        self.assertFalse(periods[6]["hak_nesafet_yili"])
        self.assertIn("Ara Yıl", periods[6]["rejim"])

        # 11. Kira Yılı (İkinci hak ve nesafet): 01.07.2028 - 30.06.2029
        self.assertEqual(periods[10]["baslangic"], "01.07.2028")
        self.assertTrue(periods[10]["hak_nesafet_yili"])

    def test_tbk345_with_increase_clause(self):
        start = date(2018, 7, 1)
        target = date(2024, 7, 1)
        action = date(2024, 11, 15)  # Hedef dönem içinde dava
        res = compute_tespit(
            start_date=start,
            has_increase_clause=True,
            notice_date=None,
            action_date=action,
            target_period_start=target
        )
        self.assertTrue(res["sure_analizi"]["artis_sarti_var"])
        self.assertEqual(res["sure_analizi"]["kararin_gecerlilik_tarihi"], "01.07.2024")
        self.assertIn("TBK 345/3", res["sure_analizi"]["uygulanan_kural"])

    def test_tbk345_without_increase_clause_timely_notice(self):
        start = date(2018, 7, 1)
        target = date(2024, 7, 1)
        # 30 gün öncesi son gün: 01.06.2024
        notice = date(2024, 5, 25)  # Süresinde ihtar
        action = date(2024, 9, 10)  # Dönem içinde açılan dava
        res = compute_tespit(
            start_date=start,
            has_increase_clause=False,
            notice_date=notice,
            action_date=action,
            target_period_start=target
        )
        self.assertFalse(res["sure_analizi"]["artis_sarti_var"])
        self.assertEqual(res["sure_analizi"]["en_gec_ihtar_teblig_tarihi"], "01.06.2024")
        self.assertEqual(res["sure_analizi"]["kararin_gecerlilik_tarihi"], "01.07.2024")

    def test_tbk345_without_increase_clause_late_notice(self):
        start = date(2018, 7, 1)
        target = date(2024, 7, 1)
        # 30 gün öncesi son gün: 01.06.2024
        notice = date(2024, 6, 15)  # Geç tebliğ edilen ihtar
        action = date(2024, 9, 10)
        res = compute_tespit(
            start_date=start,
            has_increase_clause=False,
            notice_date=notice,
            action_date=action,
            target_period_start=target
        )
        # Süre kaçırıldığı için tespit izleyen dönem (01.07.2025) başından geçerli olur
        self.assertEqual(res["sure_analizi"]["kararin_gecerlilik_tarihi"], "01.07.2025")

    def test_tbk347_ten_year_extension(self):
        start = date(2015, 1, 1)
        res = compute_tahliye_10yil(start, initial_years=1)
        self.assertEqual(res["ilk_sozlesme_bitis"], "31.12.2015")
        self.assertEqual(res["on_yillik_uzama_baslangic"], "01.01.2016")
        self.assertEqual(res["on_yillik_uzama_bitis"], "31.12.2025")
        self.assertEqual(res["toplam_yil"], 11)
        self.assertEqual(res["ilk_fesih_donem_sonu"], "31.12.2025")
        # En az 3 ay önce ihtar: 30.09.2025
        self.assertEqual(res["en_gec_ihtar_teblig_tarihi"], "30.09.2025")
        # Dava dönemi: 01.01.2026 - 31.01.2026
        self.assertEqual(res["tahliye_dava_acma_araligi"], "01.01.2026 - 31.01.2026")
        self.assertEqual(len(res["izleyen_uzama_yillari"]), 3)

    def test_cli_subprocess(self):
        # tespit json testi
        cmd = [
            sys.executable,
            str(ROOT / "scripts/hesap.py"),
            "tespit",
            "--baslangic", "01.07.2018",
            "--artis-sarti",
            "--dava-tarihi", "15.05.2024",
            "--json"
        ]
        proc = subprocess.run(cmd, capture_output=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["sozlesme_baslangic"], "01.07.2018")
        self.assertTrue(data["sure_analizi"]["artis_sarti_var"])

        # tahliye-10yil json testi
        cmd2 = [
            sys.executable,
            str(ROOT / "scripts/hesap.py"),
            "tahliye-10yil",
            "--baslangic", "01.01.2015",
            "--json"
        ]
        proc2 = subprocess.run(cmd2, capture_output=True, encoding="utf-8")
        self.assertEqual(proc2.returncode, 0)
        data2 = json.loads(proc2.stdout)
        self.assertEqual(data2["toplam_yil"], 11)

        # Hatalı parametre testi
        cmd_err = [
            sys.executable,
            str(ROOT / "scripts/hesap.py"),
            "tespit",
            "--baslangic", "invalid-date"
        ]
        proc_err = subprocess.run(cmd_err, capture_output=True, encoding="utf-8")
        self.assertNotEqual(proc_err.returncode, 0)


if __name__ == "__main__":
    unittest.main()
