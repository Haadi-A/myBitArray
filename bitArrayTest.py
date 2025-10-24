import unittest
import timeit
from math import ceil
from bitarray import BitArray # Assuming your class is in forgemini.py

# --- Configuration ---
# Large number of operations for performance testing
NUM_OPS = 100000 

# --- Helper Functions for Diagnostics ---

def get_memory_usage_mb():
    """Returns the current process memory usage in MB."""
    import os, psutil
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

# --- Test Class Implementation ---

class TestBitArray(unittest.TestCase):
    
    # --------------------------------------------------------------------------
    # I. LOGICAL CORRECTNESS TESTS
    # --------------------------------------------------------------------------

    def test_a_append_unset_bits_correctness(self):
        """
        Tests the core challenge: accurate representation of trailing unset (0) bits.
        This verifies that __unsetTailBits and __setbitsLen maintain the correct logical length.
        """
        ba = BitArray()

        # 1. Append a full set byte (8 bits)
        for _ in range(8):
            ba.append(isSetBit=True)
        self.assertEqual(len(ba), 8, "Length after 8 set bits must be 8.")
        self.assertEqual(ba.setBitsNo, 8, "__setbitsLen should be 8.")
        self.assertEqual(ba.unsetTailBitNo, 0, "__unsetTailBits should be 0.")
        self.assertEqual(ba.byteRpr, bytearray([255]), "Byte representation must be [255].")

        # 2. Append 3 trailing unset bits (0s)
        for _ in range(3):
            ba.append(isSetBit=False)
        self.assertEqual(len(ba), 11, "Length after 3 unset bits must be 11.")
        self.assertEqual(ba.setBitsNo, 8, "__setbitsLen must remain 8.")
        self.assertEqual(ba.unsetTailBitNo, 3, "__unsetTailBits must be 3.")
        # The bytearray should still only contain one byte [255] as no padding byte is added yet.
        self.assertEqual(len(ba.byteRpr), 1, "Bytearray size should still be 1 after 3 unset bits.")
        # No this is by design of mine. The for doing so is to first and most importantly, to make space for the unsetTailBits 
        # and secondly, to indicate that there are unset tail bits when the string representation is printed.
        # Is this a bad design choice? 
        # 3. Append 5 more unset bits (total 8 unset bits, forcing a new 0-byte to be created)
        # This will trigger the logic to resize and potentially add a byte for the zero-padding.
        for _ in range(5):
            ba.append(isSetBit=False)
        self.assertEqual(len(ba), 16, "Length after 8 total unset bits must be 16.")
        self.assertEqual(ba.setBitsNo, 8, "__setbitsLen must remain 8.")
        self.assertEqual(ba.unsetTailBitNo, 8, "__unsetTailBits must be 8.")
        # Check if the internal array resized to accommodate the full byte of unset bits.
        # It should now be two bytes: [255, 0]
        required_bytes = ceil(len(ba) / 8)
        self.assertEqual(len(ba.byteRpr), required_bytes, "Bytearray size must match required bytes for 16 bits.")


    def test_b_append_set_bits_with_tail(self):
        """
        Tests appending a set bit (1) when there are existing unset tail bits.
        This is where the structure must resolve the padding bytes.
        """
        ba = BitArray()
        # 1. Setup: 8 set bits + 4 unset tail bits (Total length 12)
        for _ in range(8): ba.append(isSetBit=True) # byte 1 = 0xFF
        for _ in range(4): ba.append(isSetBit=False) # __unsetTailBits = 4

        # 2. Action: Append one set bit (1)
        # The last set bit (1) should consume the 4 unset bits and require 1 more bit from the new byte.
        ba.append(isSetBit=True)
        # 3. Assertions
        # Total length: 8 (set) + 4 (unset) + 1 (new set) = 13
        self.assertEqual(len(ba), 13, "Total length must be 13.")
        self.assertEqual(ba.setBitsNo, 9, "__setbitsLen must be 9.") 
        # ^^--- Problem when a set bit is appended to the bitarray after tail unsetbits have been appended, 
        # the tail unset bits get clear and added to the set bit(s), 
        # because a set bit has been appended to the tail of the bitarray rendering the previously unset TAIL bit(s)
        #  not the tail bits anymore but sealed by a set bit.
        # eg. [11111111]|[0] which is conceptually represented as follows -> 
        # [11111111]|[0000], why because the __setBitsLen = 8 and __unsetTailBitsLen = 4.
        # But when a set bit is appeded to the tail of the bitarray, its represented as follows:
        # eg. [11111111]|[1000] which is conceptually represented as follows -> 
        # [11111111]|[00001000], why because the __setBitsLen = 13 and __unsetTailBitsLen = 0.
        # From the documentation of the [__setbitsLen] variable I explicitly stated that it is: 
        # Used to represent the number of bits, be it on or OFF bits which are not unset tail bits: **[__unsetTailBits]**
        # So since a tail set bit has been appended, the __unsetTailBitsLen == 0 because they are no more tail but anteceeded by a set bit, 
        # and they become setBits although they are off-bits.

        # Is this design choice flawed?
        self.assertEqual(ba.unsetTailBitNo, 0, "Unset tail bits must be cleared to 0.")
        
        # Internal byte representation should be two bytes
        # Byte 1: 11111111 (255)
        # Byte 2: 10000000 (128) <- The new set bit plus padding
        self.assertEqual(len(ba.byteRpr), 2, "Bytearray size must be 2 after resolution.")
        self.assertEqual(ba.byteRpr[0], 255, "First byte must be 255.")
        self.assertEqual(ba.byteRpr[1], 128, "Second byte must represent the single set bit at the MSB position.")


    def test_c_set_and_clear_correctness(self):
        """
        Tests the set and clear operations, ensuring they don't corrupt the byte representation.
        """
        ba = BitArray()
        # 1. Setup: 16 bits (0xFF 0x00)
        for _ in range(8): ba.append(isSetBit=True)
        for _ in range(8): ba.append(isSetBit=False)
        
        # 2. Action: Set a bit in the second byte
        ba.set(12) # Index 12 is the 5th bit of the second byte (0-indexed)

        # 3. Assertions
        # Byte 2 was 00000000. Index 12 is bit 4 (7 - 4 = 3, so 1 << 3 = 8)
        self.assertEqual(ba.byteRpr[1], 8, "Setting bit 12 (4th index of byte 2) failed.")

        # 4. Action: Clear a bit in the first byte
        ba.clearBit(3) # Index 3 is the 4th bit of the first byte (0-indexed)

        # 5. Assertions
        # Byte 1 was 11111111 (255). Clearing the 4th bit (MSB index 4) should result in 247 (11110111)
        self.assertEqual(ba.byteRpr[0], 247, "Clearing bit 3 failed.")
        # Problem with the above assert.
        # If you wanna clear the 4th bit of the first byte which is represented before clearing as follows:[11111111] = 255
        # Considering the clear bit takes the index which is 0-indexed: 
        # The bit at the index 3 would be the fourth bit in the first byte not the fifth bit as you previously alluded to.
        # So clearing the 4th bit becomes: [11101111]  which is 239 in decimal not not [11101111] which is 247, which is asserted for in the test. 
        # Or I'm I missing something. 
    
    # --------------------------------------------------------------------------
    # II. PERFORMANCE AND EFFICIENCY TESTS
    # --------------------------------------------------------------------------

    def test_d_performance_and_memory_efficiency(self):
        """
        Benchmarks append performance and checks for excessive memory overhead.
        """
        print(f"\n--- Performance & Memory Benchmarks (N={NUM_OPS:,}) ---")
        
        # Baseline: Memory check before execution
        # initial_mem = get_memory_usage_mb()

        # 1. Performance Test: Appending Set Bits
        start_time_set = timeit.default_timer()
        ba_set = BitArray()
        for _ in range(NUM_OPS):
            ba_set.append(isSetBit=True)
        end_time_set = timeit.default_timer()
        time_set = end_time_set - start_time_set

        # 2. Performance Test: Appending Unset Bits
        start_time_unset = timeit.default_timer()
        ba_unset = BitArray()
        for _ in range(NUM_OPS):
            ba_unset.append(isSetBit=False)
        end_time_unset = timeit.default_timer()
        time_unset = end_time_unset - start_time_unset
        
        # 3. Memory Test: Check final object size
        # final_mem = get_memory_usage_mb()
        
        # --- Reporting ---
        print(f"  Append Set Bits Time: {time_set:.4f}s")
        print(f"  Append Unset Bits Time: {time_unset:.4f}s")
        print(f"  Set Bits Final Byte Size: {len(ba_set.byteRpr)} bytes")
        print(f"  Unset Bits Final Byte Size: {len(ba_unset.byteRpr)} bytes")

        # --- Assertions (Efficiency Checks) ---

        # 4. Logical Check: The final size of the bytearray should be roughly N/8 + 1 for both.
        expected_bytes = ceil(NUM_OPS / 8)
        
        # Memory Check: If the logic is correct, the physical byte array should be compact.
        self.assertLessEqual(len(ba_set.byteRpr), expected_bytes + 1,
            f"Set bits memory check failed. Expected approx {expected_bytes} bytes, got {len(ba_set.byteRpr)}.")
            
        # The unset array should also be compact, although it may have a large __unsetTailBits count.
        # Its physical bytearray size should only be 1 if it only contains unset tail bits (until it must allocate space).
        # We check the total logical length vs required bytes.
        self.assertLessEqual(len(ba_unset.byteRpr), expected_bytes + 1,
            f"Unset bits memory check failed. Expected approx {expected_bytes} bytes, got {len(ba_unset.byteRpr)}.")

        # Performance Check: Appending unset bits should be much faster if it relies purely on
        # updating the counter (__unsetTailBits) rather than modifying the bytearray every time.
        # The ratio check is a strong indicator of a fundamental performance flaw.
        # This checks if the complex logic inside appendBit(isSet=True) is slowing it down.
        # We expect isSet=False to be near-instant relative to isSet=True, 
        # which has to do bit shifts and bytearray writes.
        performance_ratio = time_set / (time_unset + 1e-9) # Avoid division by zero
        
        if performance_ratio < 2.0:
             print("\n!!! PERFORMANCE WARNING !!!")
             print("The appendBit(isSet=False) time is too slow compared to set bits.")
             print(f"Set/Unset Time Ratio: {performance_ratio:.2f}. This suggests the unset logic is not just updating a counter.")
             
    def test_e_resize_and_index_out_of_range(self):
        """
        Tests resizing logic and ensures appropriate IndexError is raised.
        """
        ba = BitArray()
        # Ensure initial size is 1 byte
        self.assertEqual(len(ba.byteRpr), 1)

        # Append enough bits to force resizing (e.g., 20 bits)
        for _ in range(20): ba.append(isSetBit=True)
        
        # 1. Assert Resize (should be 3 bytes: 20/8 = 2.5 -> ceil(2.5) = 3)
        self.assertEqual(len(ba.byteRpr), 3, "Resizing failed: Expected 3 bytes for 20 bits.")

        # 2. Assert IndexError for set()
        with self.assertRaises(IndexError, msg="set() failed to raise IndexError for out-of-range index."):
            # Current max index is 19. Trying to set index 20.
            ba.set(20)

        # 3. Assert IndexError for clearBit()
        with self.assertRaises(IndexError, msg="clearBit() failed to raise IndexError for out-of-range index."):
            ba.clearBit(20)

if __name__ == '__main__':
    # Run all tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
