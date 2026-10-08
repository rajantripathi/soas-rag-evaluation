import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

from run_title_masking_ablation import mask_title, norm, build_passages  # noqa: E402


class TitleMaskingTests(unittest.TestCase):
    def test_masks_uzbek_apostrophe_variants(self):
        text = "O'zbek tili turkiy til. O‘zbek tili davlat tili."
        self.assertEqual(mask_title('Oʻzbek tili', text), 'turkiy til. davlat tili.')

    def test_masks_disambiguated_title_and_base_form(self):
        text = 'Mercury is the smallest planet. Mercury (planet) orbits.'
        self.assertEqual(mask_title('Mercury (planet)', text), 'is the smallest planet. orbits.')

    def test_is_case_insensitive_and_keeps_other_text(self):
        self.assertEqual(mask_title('Art Deco', 'ART DECO style; art   deco era'), 'style; era')

    def test_does_not_remove_substrings(self):
        self.assertEqual(mask_title('Art', 'Earth and art.'), 'Earth and .')
        self.assertEqual(mask_title('2 (son)', '2026 and 2.'), '2026 and .')
        self.assertEqual(mask_title('Toshkent', 'Toshkentda Toshkent.'), 'Toshkentda .')

    def test_fixed_window_does_not_refill(self):
        class Tokenizer:
            def encode(self, text, **kwargs):
                return text.split()
            def decode(self, tokens, **kwargs):
                return ' '.join(tokens)
        corpus = [dict(doc_id='en:1', language='en', title='Art', text='Art ' * 480 + 'later')]
        self.assertEqual(build_passages(corpus, 'title_masked', Tokenizer())[0]['text'], 'later')
        self.assertEqual(build_passages(corpus, 'title_masked_fixed_window', Tokenizer())[0]['text'], '')

    def test_norm_unifies_apostrophes(self):
        self.assertIn(norm('Oʻzbekiston'), norm("O'zbekiston nima?"))


if __name__ == '__main__':
    unittest.main()
