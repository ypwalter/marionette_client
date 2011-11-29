import unittest

class MarionetteTestCase(unittest.TestCase):

    def __init__(self, marionette, methodName='runTest'):
        self.marionette = marionette
        unittest.TestCase.__init__(self, methodName)


