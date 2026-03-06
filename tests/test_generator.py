import unittest
from gym_routine.generator import generate_workout

class TestGenerator(unittest.TestCase):
    def test_generate_workout(self):
        workout = generate_workout(0)
        self.assertIn('exercises', workout)
        self.assertGreater(len(workout['exercises']), 0)
        self.assertIn('total_time_estimate_minutes', workout)

if __name__ == '__main__':
    unittest.main()