import unittest as ut
import XBeeInt as xbi


class XBeeIntTest(ut.TestCase):

    def __init__(self):
        self._mPositiveCase = {
            "type": "XBeeInt",
            "name": "Start Delimiter",
            "offset": 0,
            "length": 1
        }

    def test_constructor(self):

        xbint = xbi.XBeeInt()
        self.assertEqual(xbint._mOffset, -1)
        self.assertEqual(xbint._mLength, 0)
        self.assertEqual(len(xbint._mEnumeration), 0)

    def test_read(self):

        xbint = xbi.XBeeInt()

        # test a positive case
        xbi.read(self._mPostiveCase)
        self.assertEqual(xbi._mOffset, 0)
        self.assertEqual(xbi._mLength, 1)
        self.assertEqual(xbi._mName, "Start Delimiter")
        self.assertEqual(xbi._mType, "XBeeInt")
