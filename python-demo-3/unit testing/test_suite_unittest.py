# What is unit testing? Why do we do it?
'''
Testing is about checking and confirming the behavior of code.
There is expectation and reality, the difference between them is a "bug". 
We're looking for bugs

Units are the smallest chunk of testable code. In general this is a function. 

SUT - system under test, usually a larger collection of functions. We often test a larger system with indvidual
unit tests, this is a test suite.


Why unit test? To look for bugs, particularly bugs introduced recently in new code. It is very common
to have an automated pipeline for merging, building, and deploying with unit testing being a gateway that
would block bad code (code with failing tests) from being merged into the main codebase.
'''


import unittest

class TestMath(unittest.TestCase):

    def setUp(self):
        # runs before each test
        self.values = [1, 2, 3]

    def tearDown(self):
        # runs after each test
        pass

    def test_sum(self):
        # The Three A's of unit testing:
        # Arrange - get the test ready
        # Act - call that function
        # Assert
        self.assertEqual(sum(self.values), 6)

    def test_max(self):
        self.assertGreater(max(self.values), 2)

    def test_raises(self):
        with self.assertRaises(ZeroDivisionError):
            1 / 0

# Common assertions:
# assertEqual(a, b)
# assertTrue(x)
# assertFalse(x)
# assertIsNone(x)
# assertIn(a, b)
# assertRaises(Exception)

if __name__ == "__main__":
    unittest.main()