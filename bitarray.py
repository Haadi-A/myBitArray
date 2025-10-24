from math import ceil
from typing import Iterable


class BitArray(list[bool]):
    def __init__(self, ):
        # Create a byte array with bytes less
        self.__byteArray = bytearray(1)
        self.__unsetTailBitsLen: int = 0
        '''Used to represent the number of off-bits appended to the end of the byte array but not yet reflected in the byte array.'''
        
        self.__representedBits: int = 0
        '''Used to represent the number of bits, be it on or off bits which are not unset tail bits: **[__unsetTailBits]**'''


    def __len__(self) -> int:
        '''Returns the bit length of the bytearray'''
        return self.__unsetTailBitsLen + self.__representedBits

    def __repr__(self) -> str:
        """
        Return a concatenated string of 8-bit binary representations for the instance's byte array.

        Each integer in self.__byteArray is converted to binary (without the '0b' prefix),
        left-padded with zeros to exactly 8 digits, and then all byte strings are joined
        into one continuous string.

        Returns:
            str: The concatenated 8-bit binary string representing the byte array.

        Notes:
            - Expects each element of self.__byteArray to be an integer in the range 0–255.
            - Primarily intended for a human-readable or debugging representation of the bytes.
        """
        return ''.join(format(byte, '08b') for byte in self.__byteArray)

    @property
    def unsetTailBitNo(self)-> int:return self.__unsetTailBitsLen

    @property
    def setBitsNo(self)-> int: return self.__representedBits
    

    @property
    def byteRpr(self) -> bytearray:
        return self.__byteArray

    def __str__(self) -> str:
        counter = 0
        bitsStr = ''
        for bitVal in self.__repr__():
            if counter == 8:
                bitsStr += '|' + bitVal
                counter = 0
            else:
                bitsStr += bitVal
            counter += 1

        return bitsStr

    def __resizeSelf(self, newSize: int):
        """
        Resize the internal byte buffer to a new size measured in bytes.

        Parameters
        ----------
        newSize : int
            The target size for the internal bytearray, expressed in bytes (not bits).

        Description
        -----------
        - When newSize is greater than the current buffer size, allocate a new
          bytearray of length newSize, copy the existing contents into the
          beginning of the new buffer, and replace the internal buffer with it.
          Any newly allocated bytes will be zero-initialized.
        - When newSize is equal to the current buffer size, no changes are made.
        - When newSize is smaller than the current buffer size, downsizing is
          currently not implemented (TODO) and the buffer remains unchanged.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            If newSize is not an integer.
        ValueError
            If newSize is negative.

        Notes
        -----
        This method operates on the number of bytes; callers should convert from
        bits to bytes before invoking if necessary.
        """
        '''newSize: int -> Number of bytes for the new resized bytearray not the number of bits.'''
        buff, buffSize = self.__byteArray, len(self.__byteArray)
        if newSize > buffSize:
            self.__byteArray = bytearray(newSize)
            self.__byteArray[: buffSize] = buff
        elif newSize < buffSize:
            # TODO: IMPLEMENT ARRAY DOWNSIZING.
            pass

    def set(self, indx: int):
        """
        Set the bit at the specified index to 1.

        Parameters
        ----------
        indx : int
            Zero-based index of the bit to set. Index 0 refers to the most-significant
            bit of the first byte in the underlying storage.

        Raises
        ------
        IndexError
            If indx is out of the valid range as determined by self.__len__().

        Behavior / Notes
        ----------------
        - The target byte and bit are computed as: byteIndx, bitIndx = divmod(indx, 8).
        - If the underlying bytearray is not large enough to contain the target byte,
          the internal resize method is invoked: self.__resizeSelf(byteIndx + 1).
        - Bits within a byte use big-endian ordering: the mask 1 << (7 - bitIndx)
          sets the corresponding bit (bitIndx == 0 sets the MSB).
        - This method currently assumes any trailing/partial-byte handling is managed
          elsewhere; see the TODO about self.__tailOffBits for cases with a non-full
          final byte which may require additional logic.
        """
        # TODO: UPDATE TO CONSIDER WHEN __tailOffBits != 0.
        byteIndx, bitIndx = divmod(indx, 8)
        if indx < self.__len__():
            if byteIndx + 1 > len(self.__byteArray):
                self.__resizeSelf(byteIndx + 1)

            self.__byteArray[byteIndx] |= 1 << (7 - bitIndx)
        else: 
            raise IndexError(f'The bitArray  assigment index: {indx} is out of range.') 

    @staticmethod
    def _setBitInByte(byte: int, indx: int) -> int:
        byteBitLen = byte.bit_length()
        if byteBitLen <= 8:
            byte |= 1 << (7 - indx)
            return byte
        else:
            raise ValueError(
                "Byte values must be within range: 0 - 255, byte value provided: ", byte)


    def clearBit(self, indx: int):
        """Clear the bit at the given index in this bit array.

        This method sets the bit at position `indx` to 0. Bits are addressed with
        index 0 being the first bit of the array and bits within a byte are treated
        MSB-first (i.e. bit position 0 corresponds to mask 1 << 7 in the byte).

        Behavior:
        - If `indx` is negative or greater than or equal to len(self), an IndexError
            is raised.
        - If `indx` is within the uncommitted tail region (indx >= self.__representedBits),
            the bit is already considered 0 and the method is a no-op.
        - Otherwise the corresponding byte in self.__byteArray is modified in-place
            to clear the targeted bit.

        Parameters
        ----------
        indx : int
                Zero-based index of the bit to clear.

        Returns
        -------
        None

        Raises
        ------
        IndexError
                If `indx` is out of the valid range [0, len(self) - 1].

        Side effects
        ------------
        - Mutates self.__byteArray when clearing a bit in the committed region.

        Complexity
        ----------
        O(1) time and O(1) additional space.
        """
        if indx < self.__len__():
            # Bit is already 0 in the uncommitted tail region. No action needed.
            if indx >= self.__representedBits: return
            byteIndx, bitIndx = divmod(indx, 8)
            clearMask = 255 ^ (1 << (7 - bitIndx))
            self.__byteArray[byteIndx] &= clearMask
        else:
            raise IndexError(
                f"The provided index: {indx} is out of range of the bitArray of max indx: {self.__len__() - 1}")

    def __getLastSetByteIndx(self) -> int:
        '''Returns index for the last set byte.'''
        # Flips the array and deducts the indx of the first non-zero byte from the max indx of the [byteRpr] bytearray
        for currIndx, byte in enumerate(self.__byteArray[::-1]):
            if byte > 0:
                return (len(self.__byteArray) - 1) - currIndx
        else:
            return 0

    @staticmethod
    def __getByteLastSetBitIndx(lastByte: int) -> int:
        '''
        Returns: -1 when byte is 0 ie. no set bit in the byte 
                but if there is any set bit in the byte, it will return the corresponding index for it. 
        '''
        if lastByte == 0:
            return -1
        elif lastByte > 255:
            raise ValueError('Byte must be within range(0, 256)')

        lastByteStrRpr = bin(lastByte)[2:]
        lastByteStrRpr = lastByteStrRpr + ((8 - len(lastByteStrRpr)) * '0')
        flippedLastByte = lastByteStrRpr[::-1]

        for indx, bit in enumerate(flippedLastByte):
            if bit != '0':
                return 7 - indx
        else:
            return 0

    def append(self, isSetBit: bool = True):
        """
        Append a single bit to the bit array.
        This method appends either a set bit (1) or an unset bit (0) to the end of the represented bit sequence,
        updating internal storage and counters as needed. Bits are packed into a Python bytearray in big-endian
        order within each byte (the most significant bit of a byte is written first).
        Behavior:
        - If isSetBit is False:
            - The append is treated as an appended unset (0) and the internal unset-tail counter
              (__unsetTailBitsLen) is incremented. The underlying bytearray may be resized so there
              is space to represent future bits.
        - If isSetBit is True:
            - The method will attempt to materialize the appended set bit (1) into the existing bytes.
            - If there are pending unset-tail bits, this set bit may cause those unset bits to be flushed
              into the bytearray together with the new set bit (possibly spanning multiple bytes).
            - If there is no space in the current last byte, the bytearray is expanded as necessary.
            - Internal helpers are used to find the last set byte, compute available free bits, set a
              bit inside a byte, and resize storage.
        Side effects / mutated attributes:
        - self.__byteArray: may be resized and/or updated to include the new bit(s).
        - self.__unsetTailBitsLen: incremented when appending an unset bit; cleared when pending unset bits
          are materialized due to a subsequent set bit append.
        - self.__representedBits: incremented whenever bits become part of the represented sequence.
        - Other internal indices/counters used by helper methods may also change.
        Parameters:
        - isSetBit (bool, optional): If True (default), append a set bit (1). If False, append an unset bit (0).
          The implementation treats truthy/falsy values similarly to bool, but the intended input is a boolean.
        Return:
        - None
        Complexity:
        - Amortized O(1) per append. A single append may trigger a resize and involve O(n) work where n is the
          number of bytes, but typical appends are constant-time when no resize is required.
        Notes / edge cases:
        - The method assumes internal invariants maintained by helper methods (e.g., __len__(), __resizeSelf(),
          _availableFreeBitsSpace(), __getLastSetByteIndx(), BitArray._setBitInByte(), and
          BitArray.__getByteLastSetBitIndx()).
        - Appending a set bit when there is a non-zero unset-tail will try to pack those unset bits into bytes
          before or while inserting the set bit; the precise packing follows the class's MSB-first byte convention.
        - The method does not return a value and should be used for its side effect of extending the bit array.
        """
        # is unset
        if isSetBit == False:
            # increment the unsetTailBitCounter.
            self.__unsetTailBitsLen += 1
            requiredBytesNo = ceil(self.__len__() / 8)
            # If bytearray cannot accomodate the off-bit in the bytearray, make space for the appended off-bit 
            if len(self.__byteArray) -  requiredBytesNo < 0:
                self.__resizeSelf(requiredBytesNo)
        # is set
        else:        
            availableFreeBits = self._availableFreeBitsSpace()

            # Check if there are free bits to hold the bit to be appended.
            if availableFreeBits <= 0:  # if not
                # resize the bytearray to have enough space for the appended bit.
                self.__resizeSelf(newSize=len(self.__byteArray) + 1)

            lastSetByteIndx = self.__getLastSetByteIndx()
            # If there is no space in the last set byte to accomodate the appended bit:
            lastSetByteVal = self.__byteArray[lastSetByteIndx]
            if self.__byteArray[lastSetByteIndx] == 255:
                # Move to the next empty byte.
                lastSetByteIndx += 1
                lastSetByteVal = self.__byteArray[lastSetByteIndx]
            lSBitI = BitArray.__getByteLastSetBitIndx(lastByte=lastSetByteVal)
            lastByteAvailableSpace = 8 - (lSBitI + 1)

            # are there unsetbits
            if self.__unsetTailBitsLen == 0:  # no
                # append a set bit to the appropriate last byte.
                lastSetBitInLastByte = BitArray.__getByteLastSetBitIndx(
                    lastByte=self.__byteArray[lastSetByteIndx])
                bitToSet = 0 if lastSetByteVal == 0 else lastSetBitInLastByte + 1
                lastByteWithAppendedBit = BitArray._setBitInByte(byte=lastSetByteVal, indx=bitToSet)
                
                self.__byteArray[lastSetByteIndx] = lastByteWithAppendedBit
                self.__representedBits += 1
                return
            else:  # yes
                # can the last byte hold the all the unset bits and the last set bit
                if lastByteAvailableSpace >= self.__unsetTailBitsLen + 1:  # yes
                    _, usedBits =divmod(self.__len__(), 8)
                    
                    self.__byteArray[lastSetByteIndx] = BitArray._setBitInByte(byte=lastSetByteVal, indx=usedBits) 
                    # Clear the unsetTailBitsCounter.
                    self.__representedBits += (self.__unsetTailBitsLen + 1)
                    self.__unsetTailBitsLen = 0
                    return
                else:  # no
                    # Find the number of bits which can fit into the last byte
                    remainingUnsetBits = self.__unsetTailBitsLen - lastByteAvailableSpace
                    # Find the number of bytes and bits required to further store the full new bit data.
                    requiredBytes, remainderBits = divmod(remainingUnsetBits, 8)
                    offsetByteIndx = lastSetByteIndx + requiredBytes

                    # Insert the unset bits to the unset portion of the lastSetByte
                    self.__byteArray[lastSetByteIndx] =  lastSetByteVal << (8 - lastSetByteVal.bit_length()) #<<-TODO: FIX: something ain't right here.

                    # 2-
                    # Fill the intermediate bytes with 0s
                    self.__byteArray[lastSetByteIndx + 1: offsetByteIndx + 1] = [0] * requiredBytes

                    # 3-
                    # If there are no remaining unset bytes, append the last set bit.
                    if remainderBits == 0:
                        self.__byteArray[offsetByteIndx + 1] = 1 << 7

                    # If there are a remaining bits.
                    elif remainderBits > 0:
                        # We are shifting right in order to provide padding at the most significant bit portion of the byte.
                        # Eg. byte = [0] remainder unset bits = 3
                        # byte |= 1 << (7 - 3)
                        # byte = [00010000] = [10000]
                        righShiftNo = 7 - remainderBits
                        self.__byteArray[offsetByteIndx +1] |= 1 << righShiftNo

                self.__representedBits += (self.__unsetTailBitsLen + 1)
                self.__unsetTailBitsLen = 0
                return

    def _availableFreeBitsSpace(self) -> int:
        '''Return the number of free **BITS** in the byte array.'''
        # Find the number of used bits 
        usedBitsLen = self.__len__()

        # Find the number of used bytes and remainder bits in the byte array.
        usedBytes, remainderUsedBits = divmod(usedBitsLen, 8)
        
        physicalByteArrayLen = len(self.__byteArray)
        # subtract the nubmer used bytes from the entire bytes to get the unused bytes.
        unusedBytes = physicalByteArrayLen - usedBytes
        
        # If there are no remainder bits, convert the free unused bytes to bits and return it
        if remainderUsedBits == 0:
            return unusedBytes * 8
        
        # if there are remainder bits 
        elif remainderUsedBits > 0:
            # Take out one byte and from the unused bytes and 
            unusedBytes -= 1

            # Find the number of unsed bits in the in the last used bytes.
            lastByteUnsedBits =  8 - remainderUsedBits 
            
            # Convert the free unused bytes to bits, add the unused bits to and return it.
            return unusedBytes * 8 + lastByteUnsedBits
        else:
            raise Exception("!!From _availableFreeBitsSpace(): There is a flaw in the free bits checking logic.")



    def popBit(self): pass

    def insertBit(self, indx: int): pass

    def removeBit(self, indx: int): pass

    def extend(self, bits: Iterable[bool]): pass

