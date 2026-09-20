import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import decision_qa as qa


class AnswerTests(unittest.TestCase):
    def test_blind_questions_have_no_answer_or_source_fields(self):
        data, _ = qa.load_qa()
        out = qa.questions(data)
        self.assertEqual(len(out['questions']), len(data['examples']))
        self.assertTrue(all(set(r) == {'id', 'question'} for r in out['questions']))

    def test_readable_answers_match_data_and_include_every_source(self):
        data, cards = qa.load_qa()
        rendered = qa.render(data, cards)
        self.assertEqual(rendered, (qa.ROOT / 'references/kararlardan-soru-yanit.md').read_text(encoding='utf-8'))
        for card in cards.values():
            self.assertIn(card['source']['url'], rendered)

    def test_source_outcomes_are_preserved(self):
        data, cards = qa.load_qa()
        self.assertEqual({r['card_id']: r['outcome'] for r in data['examples']},
                         {k: v['outcome'] for k, v in cards.items()})


if __name__ == '__main__':
    unittest.main()
