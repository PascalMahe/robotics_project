import logging
import math
import unittest
import sys

import numpy as np

from compute_position import compute_final_coordinates, go_to_dest


test_logger = logging.getLogger("test_logger")
stdout_formatter = logging.Formatter(
    '%(funcName)s l.%(lineno)d | %(message)s')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(stdout_formatter)
stdout_handler.setLevel(logging.DEBUG)
test_logger.addHandler(stdout_handler)

class TestComputePosition(unittest.TestCase):


    # def test_1(self):
    #     commands_str = "up 100; forward 50; left 30; down 20; back 10; right 25"
    #     final_position, final_orientation = compute_final_coordinates(commands_str)
    #     self.assertEqual(final_position, (40.0, -5.0, 80.0))
    #     self.assertEqual(final_orientation, 0)

    
    def test_cw(self):
        commands_str = "cw 180"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (0.0, 0.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 180)

        commands_str = "cw 90"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (0.0, 0.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 90)

        commands_str = "cw 90; cw 180"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (0.0, 0.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 270)
        
        commands_str = "cw 90; forward 10; cw 180"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (0.0, 10.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 270)

        commands_str = "cw 90; right 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-10.0, 0.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 90)

        commands_str = "cw 90; left 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (10.0, 0.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 90)
        
        commands_str = "cw 90; right 10; cw 180; left 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-20.0, 0.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 270)

        commands_str = "cw 90; forward 10; cw 180; left 5"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-5.0, 10.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 270)
        

        commands_str = "cw 45; right 10; cw 45; left 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (2.9290, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 90)
        
        commands_str = "cw 45; right 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 45)
        
        commands_str = "cw 135; right 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 135)
        
        commands_str = "cw 225; right 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 225)
        
        commands_str = "cw 315; right 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 315)

        commands_str = "cw 45; left 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 45)
        
        commands_str = "cw 135; left 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 135)
        
        commands_str = "cw 225; left 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 225)
        
        commands_str = "cw 315; left 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 315)

        commands_str = "cw 45; forward 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 45)
        
        commands_str = "cw 135; forward 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 135)
        
        commands_str = "cw 225; forward 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 225)
        
        commands_str = "cw 315; forward 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 315)
        
        commands_str = "cw 45; back 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 45)
        
        test_logger.setLevel(logging.DEBUG)
        commands_str = "cw 135; back 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 135)
        
        commands_str = "cw 225; back 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 225)
        
        commands_str = "cw 315; back 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 315)
        
    
    def test_ccw(self):
        # testing simple position calculation
        commands_str = "ccw 180"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (0.0, 0.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 180)

        commands_str = "ccw 90"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (0.0, 0.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 270)

        commands_str = "ccw 90; ccw 180"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (0.0, 0.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 90)
        
        commands_str = "ccw 90; forward 10; ccw 180"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (0.0, -10.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 90)

        # testing each move in turn
        commands_str = "ccw 45; right 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 315)
        
        commands_str = "ccw 135; right 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 225)
        
        commands_str = "ccw 225; right 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 135)
        
        commands_str = "ccw 315; right 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 45)

        commands_str = "ccw 45; left 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 315)
        
        commands_str = "ccw 135; left 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 225)
        
        commands_str = "ccw 225; left 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 135)
        
        commands_str = "ccw 315; left 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 45)

        commands_str = "ccw 45; forward 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 315)
        
        commands_str = "ccw 135; forward 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 225)
        
        commands_str = "ccw 225; forward 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 135)
        
        commands_str = "ccw 315; forward 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 45)
        
        commands_str = "ccw 45; back 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 315)
        
        commands_str = "ccw 135; back 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, 7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 225)
        
        commands_str = "ccw 225; back 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 135)
        
        commands_str = "ccw 315; back 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (-7.0710, -7.0710, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 45)

        # composite
        commands_str = "ccw 90; forward 10; ccw 180; left 5"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (5.0, -10.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 90)
        
    def test_square(self):
        
        # first square: only right angles
        # counter-clockwise, widdershins for ENglish enthusiasts :p
        commands_str = "ccw 90; forward 10; ccw 90; forward 10; ccw 90; forward 10; ccw 90; forward 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (0.0, 0.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 0)

        # clockwise
        commands_str = "cw 90; back 10; cw 90; back 10; cw 90; back 10; cw 90; back 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (0.0, 0.0, 0.0), atol=10e-4)
        self.assertEqual(final_orientation, 0)

        # second square: first, turn 30°
        commands_str = "cw 30; forward 10; ccw 90; forward 10; ccw 90; forward 10; ccw 90; forward 10; ccw 120; up 10"
        final_position, final_orientation = compute_final_coordinates(commands_str)
        np.testing.assert_allclose(final_position, (0.0, 0.0, 10.0), atol=10e-4)
        self.assertEqual(final_orientation, 0)

    def test_go_to_dest(self):
        
        test_logger.setLevel(logging.DEBUG)
        commands_str = go_to_dest((0.0, 0.0, 10.0), 0)
        self.assertEquals("up 10" , commands_str)

if __name__ == '__main__':
    unittest.main()