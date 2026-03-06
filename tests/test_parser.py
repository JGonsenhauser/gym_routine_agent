import unittest
from gym_routine.parser import parse_adjustments

class TestParser(unittest.TestCase):
    def test_parse_increase(self):
        text = "Increase bench to 90"
        adjustments = parse_adjustments(text)
        self.assertEqual(len(adjustments), 1)
        self.assertEqual(adjustments[0]['exercise'], 'bench')
        self.assertEqual(adjustments[0]['weight'], 90)

    def test_parse_reps(self):
        text = "Did 10 reps on pull-ups"
        adjustments = parse_adjustments(text)
        self.assertEqual(len(adjustments), 1)
        self.assertEqual(adjustments[0]['exercise'], 'pull-ups')
        self.assertEqual(adjustments[0]['reps'], 10)

if __name__ == '__main__':
    unittest.main()