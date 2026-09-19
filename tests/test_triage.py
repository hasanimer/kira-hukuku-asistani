import math
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from triage import build_request, interpret


class TriageTests(unittest.TestCase):
    def setUp(self):
        self.data = {'query': 'Tahliye ve depozito iadesi', 'candidates': [
            {'provider': 'a', 'source_id': '1', 'text': 'Taraf iddiası', 'full_text': False},
            {'provider': 'b', 'source_id': '1', 'text': 'Mahkeme gerekçesi', 'full_text': True}]}
        self.request = build_request(self.data)
        self.response = {'answers': {k: {'type': 'noul', 'noul': 0.2} for k in self.request['questions']}}

    def test_ranking_preserves_provenance_and_low_scores(self):
        self.response['answers']['relevant_1']['noul'] = 0.9
        result = interpret(self.request, self.response)
        self.assertEqual([x['provider'] for x in result['candidates']], ['b', 'a'])
        self.assertTrue(result['candidates'][1]['needs_full_text'])
        self.assertTrue(all(x['legal_review_required'] for x in result['candidates']))

    def test_invalid_probability_is_rejected(self):
        for value in (math.nan, math.inf, -1, 2, True, '0.9'):
            self.response['answers']['outside_scope']['noul'] = value
            with self.assertRaises(ValueError):
                interpret(self.request, self.response)

    def test_missing_answer_rejected(self):
        del self.response['answers']['route_tahliye']
        with self.assertRaises(ValueError):
            interpret(self.request, self.response)

    def test_non_object_inputs_and_responses_rejected(self):
        for value in ([], None, 'metin'):
            with self.assertRaises(ValueError):
                build_request(value)
            with self.assertRaises(ValueError):
                interpret(self.request, value)

    def test_duplicate_source_rejected(self):
        self.data['candidates'].append(self.data['candidates'][0])
        with self.assertRaises(ValueError):
            build_request(self.data)

    def test_source_completeness_cannot_be_assumed(self):
        del self.data['candidates'][0]['full_text']
        with self.assertRaises(ValueError):
            build_request(self.data)


if __name__ == '__main__':
    unittest.main()
