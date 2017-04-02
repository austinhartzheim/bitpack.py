import unittest
import base64

from bitpack import BitPack


class TestBitPackLen(unittest.TestCase):

    def test_len_without_initial_data(self):
        '''
        The __len__ method should return 0 when the class was
        initialized without any data provided.
        '''
        bp = BitPack()

        self.assertEqual(len(bp), 0)

    def test_len_returns_zero_for_empty_strint(self):
        '''
        The __len__ method should return zero for a BitPack initialized
        with an empty string.
        '''
        bp = BitPack('')

        self.assertEqual(len(bp), 0)

    def test_len_returns_length_of_provided_data(self):
        '''
        The __len__ method should return the length of the data
        provided during initialization.
        '''
        bp = BitPack(base64.encodestring(b'hello'))
        self.assertEqual(len(bp), 5)

        bp = BitPack(base64.encodestring(b'hello world'))
        self.assertEqual(len(bp), 11)


class TestBitPackByteAt(unittest.TestCase):

    def test_byte_at_happy_path(self):
        '''
        The byte_at method should return a numeric representation of
        the byte at a given index.
        '''
        bp = BitPack(base64.encodestring(b'\x00\x01\x02\x03\xff\xab'))
        self.assertEqual(bp.byte_at(0), 0)
        self.assertEqual(bp.byte_at(1), 1)
        self.assertEqual(bp.byte_at(2), 2)
        self.assertEqual(bp.byte_at(3), 3)
        self.assertEqual(bp.byte_at(4), 0xff)
        self.assertEqual(bp.byte_at(5), 0xab)

    def test_byte_at_raises_error_beyond_data_bounds(self):
        '''
        The byte_at method should raise an IndexError when attempting
        to read a byte beyond the bounds of the BitPack.
        '''
        bp = BitPack(base64.encodestring(b'\x00'))
        with self.assertRaises(IndexError):
            bp.byte_at(1)


class TestBitPackOr(unittest.TestCase):

    def test_or_happy_path(self):
        '''
        Applying the bitwise or operator to two bitpacks should result
        in a BitPack with the bitwise or of each byte.
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\xff\xab'))
        bp2 = BitPack(base64.encodestring(b'\x01\x00\xb5'))

        res = bp1 | bp2
        self.assertTrue(isinstance(res, BitPack))
        self.assertEqual(res.byte_at(0), 0x01)
        self.assertEqual(res.byte_at(1), 0xff)
        self.assertEqual(res.byte_at(2), 0xbf)

        res = bp2 | bp1
        self.assertTrue(isinstance(res, BitPack))
        self.assertEqual(res.byte_at(0), 0x01)
        self.assertEqual(res.byte_at(1), 0xff)
        self.assertEqual(res.byte_at(2), 0xbf)

    def test_or_result_length(self):
        '''
        The or operator should result in a BitPack with the length of
        the second parameter.
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\x01\x02\x03'))
        bp2 = BitPack(base64.encodestring(b'\x00\x00'))

        self.assertEqual(len(bp1 | bp2), 2)

    def test_or_with_empty_bitpack(self):
        '''
        Oring two BitPacks where the second pack is empty should return
        an empty BitPack.
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\x01\x02'))
        emptyPack = BitPack()

        self.assertEqual(len(bp1 | emptyPack), 0)

    def test_or_with_second_pack_too_long(self):
        '''
        Attempting to or two BitPacks where the length of the second
        BitPack would require reqding beyond the bounds of the first
        should raise an IndexError.
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\x01\x02'))
        bp2 = BitPack(base64.encodestring(b'\x00\x01\x02\x03'))
        bp3 = BitPack(base64.encodestring(b'\x00\x01'))

        with self.assertRaises(IndexError):
            bp1 | bp2

        with self.assertRaises(IndexError):
            bp1.bit_or(bp3, 2)


class TestBitPackBoolOr(unittest.TestCase):

    def test_bool_or_happy_path_with_one(self):
        '''
        The bool_or method should return true when either BitPack
        contains a one bit.
        '''
        bp_all_zeros = BitPack(base64.encodestring(b'\x00\x00\x00'))
        bp1 = BitPack(base64.encodestring(b'\x00\x01\x02'))

        self.assertTrue(bp_all_zeros.bool_or(bp1))
        self.assertTrue(bp1.bool_or(bp_all_zeros))

    def test_bool_or_happy_path_all_zeros(self):
        '''
        The bool_or method should return false when both BitPacks
        contain only zero bits.
        '''
        bp_all_zeros_1 = BitPack(base64.encodestring(b'\x00\x00\x00'))
        bp_all_zeros_2 = BitPack(base64.encodestring(b'\x00\x00\x00'))

        self.assertFalse(bp_all_zeros_1.bool_or(bp_all_zeros_2))
        self.assertFalse(bp_all_zeros_2.bool_or(bp_all_zeros_1))

    def test_bool_or_contains_one_bit_by_offset(self):
        '''
        The bool_or method should return true when a one bit is
        contained by offset.
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\x00\x01\x00'))
        bp2 = BitPack(base64.encodestring(b'\x00\x00'))

        self.assertTrue(bp1.bool_or(bp2, 1))

    def test_bool_or_with_empty_pack(self):
        '''
        The bool_or method should return true when called with an empty
        BitPack as a parameter.
        '''
        bp = BitPack(base64.encodestring(b'\x00\x01\x02'))
        empty_pack = BitPack()

        self.assertTrue(bp.bool_or(empty_pack))
        self.assertTrue(bp.bool_or(empty_pack, 1))

    def test_bool_or_when_source_empty(self):
        '''
        The bool_or method should return false when called on an empty
        BitPack.
        '''
        bp = BitPack(base64.encodestring(b'\x00\x01\x02'))
        empty_pack = BitPack()

        self.assertFalse(empty_pack.bool_or(bp))
        self.assertFalse(empty_pack.bool_or(bp, 1))

    def test_bool_or_when_reading_past_data_boundary(self):
        '''
        The bool_or method should return false if the operation would
        require reading past the data boundary.
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\x01\x02'))
        bp2 = BitPack(base64.encodestring(b'\x00\x01\x02\x04'))
        bp3 = BitPack(base64.encodestring(b'\x00\x01\x02'))

        self.assertFalse(bp1.bool_or(bp2))
        self.assertFalse(bp1.bool_or(bp3, 1))

    def test_bool_or_empty_pack_parameter_precendence(self):
        '''
        Returning true for an empty parameter should take precendence
        over returning false for calling bool_or on an empty BitPack.
        '''
        bp1 = BitPack()
        bp2 = BitPack()

        self.assertTrue(bp1.bool_or(bp2))


class TestBitPackTestAnd(unittest.TestCase):

    def test_and_happy_path(self):
        '''
        The and method should return the bitwise and of the bytes of
        two BitPacks.
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\xff\xab'))
        bp2 = BitPack(base64.encodestring(b'\xff\x8b\xb5'))

        res = bp1 & bp2
        self.assertTrue(isinstance(res, BitPack))
        self.assertEqual(res.byte_at(0), 0x00)
        self.assertEqual(res.byte_at(1), 0x8b)
        self.assertEqual(res.byte_at(2), 0xa1)

        res = bp2 & bp1
        self.assertTrue(isinstance(res, BitPack))
        self.assertEqual(res.byte_at(0), 0x00)
        self.assertEqual(res.byte_at(1), 0x8b)
        self.assertEqual(res.byte_at(2), 0xa1)

    def test_and_result_length(self):
        '''
        The and method should return a BitPack of the length of the
        parameter BitPack.
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\x01\x03\x03'))
        bp2 = BitPack(base64.encodestring(b'\x05\x02'))

        self.assertEqual(len(bp1 & bp2), 2)

    def test_and_with_empty_bitpack_parameter(self):
        '''
        The and method should return an empty BitPack if the provided
        parameter BitPack is empty.
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\x01\x02'))
        empty_pack = BitPack()

        self.assertEqual(len(bp1 & empty_pack), 0)

    def test_and_data_bounds(self):
        '''
        The and method should raise an IndexError exception if an
        operation requires reading bast the end of the available
        data.
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\x01\x02'))
        bp2 = BitPack(base64.encodestring(b'\x00\x01\x02\x03'))
        bp3 = BitPack(base64.encodestring(b'\x00\x01'))

        with self.assertRaises(IndexError):
            bp1 & bp2

        with self.assertRaises(IndexError):
            bp1.bit_and(bp3, 2)


class TestBitPackBoolAnd(unittest.TestCase):

    def test_bool_and_common_one_bit(self):
        '''
        The bool_and method should return true if the two bitpacks have
        a common one bit.
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\x01\x80'))
        bp2 = BitPack(base64.encodestring(b'\x00\x00\xf0'))

        self.assertTrue(bp1.bool_and(bp2))
        self.assertTrue(bp2.bool_and(bp1))

    def test_bool_and_happy_path_with_index(self):
        '''
        The bool_and method should return true if the two bitpacks have
        a common one bit after the index is applied.
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\x01\x02\x03'))
        bp2 = BitPack(base64.encodestring(b'\x01\x02\x03'))

        self.assertTrue(bp1.bool_and(bp2, 1))

    def test_bool_and_empty_bitpack(self):
        '''
        The bool_and method should return true when the parameter
        BitPack is empty.
        '''
        bp = BitPack(base64.encodestring(b'\x00\x01\x02'))
        empty_pack = BitPack()

        self.assertTrue(bp.bool_and(empty_pack))
        self.assertTrue(bp.bool_and(empty_pack, 1))

    def test_bool_and_on_empty_bitpack(self):
        '''
        The bool_and method should return false when it is called on an
        empty BitPack.
        '''
        bp = BitPack(base64.encodestring(b'\x00\x01\x02'))
        empty_pack = BitPack()

        with self.assertRaises(IndexError):
            empty_pack.bool_and(bp)

        with self.assertRaises(IndexError):
            empty_pack.bool_and(bp, 1)

    def test_bool_and_data_boundary(self):
        '''
        The bool_and method should raise an IndexError e
        '''
        bp1 = BitPack(base64.encodestring(b'\x00\x01\x02'))
        bp2 = BitPack(base64.encodestring(b'\x00\x01\x02\x03'))
        bp3 = BitPack(base64.encodestring(b'\x01\x02\x03'))

        with self.assertRaises(IndexError):
            bp1.bool_and(bp2)

        with self.assertRaises(IndexError):
            bp1.bool_and(bp3, 1)


class TestBitPackBitAt(unittest.TestCase):

    def test_bit_at_happy_path(self):
        bp = BitPack(base64.encodestring(b'\x00\xf0'))

        self.assertFalse(bp.bit_at(0))
        self.assertFalse(bp.bit_at(0, 0))

        self.assertTrue(bp.bit_at(8))
        self.assertTrue(bp.bit_at(1, 0))

        self.assertFalse(bp.bit_at(12))
        self.assertFalse(bp.bit_at(1, 4))


class TestBitPackBase64(unittest.TestCase):

    def test_base64_happy_path(self):
        bp = BitPack(base64.encodestring(b'\x00\xf0'))

        self.assertEqual(bp.base64(), base64.encodestring(b'\x00\xf0'))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
