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
    def representedBitsNo(self)-> int: return self.__representedBits
    

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
        # TODO: UPDATE TO CONSIDER WHEN TAIL OFF-BITS != 0
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


    def _byteArrayUnusedBitsNo(self)-> int:
        bytearrayBitsLen = len(self.__byteArray) * 8 
        return bytearrayBitsLen - self.__representedBits 


    # Algorithm for the append bit method:
    def append(self, isSet: bool=True):
        # 1- If is off-bit: just increment counter for unsetailBits.
        if not isSet:
            self.__unsetTailBitsLen += 1
            return 
        # 2- Else if is on-bit: 
        else:
            availableFreeBits = self._byteArrayUnusedBitsNo()

            # Check and resize bytearray if it can't hold the new data.
            if availableFreeBits <= 0:  # if not
                # resize the bytearray to have enough space for the appended bit.
                self.__resizeSelf(newSize=len(self.__byteArray) + 1)  #TODO: FIX

            # Used values:
            lastSetByteIndx = self.__getLastSetByteIndx()
            lastSetByteVal = self.__byteArray[lastSetByteIndx]

            #If there are no tailbits:
            if self.__unsetTailBitsLen == 0:
                # append 1 to the end of the bytearray.
                if lastSetByteVal.bit_length() == 8:
                    # print('Last byte bit length is :', lastSetByteVal.bit_length(), ' Moving to the next byte...')
                    lastSetByteIndx += 1
                    lastSetByteVal = self.__byteArray[lastSetByteIndx]
                self.__byteArray[lastSetByteIndx] = lastSetByteVal << 1 | 1
                self.__representedBits += 1
                return
            #Else if there are tail bits:
            else:
                newDataSize = self.__unsetTailBitsLen + 1
                #Append the off-bits and the last appended on-bit.

                # To append the off-bits and the last appended on-bit:
                # Find the bitspace in the last byte.
                lastByteUnusedBits = 8 - lastSetByteVal.bit_length()
                # If the lastByte bit space can acommodate newDataBits
                if lastByteUnusedBits >= newDataSize:
                    #Shift the lastbyte byte by the number of newDataSize  to create space for the unsetTailBits and the last setBit;
                    # And append the last set bit.
                    lastSetByteVal = (lastSetByteVal << newDataSize) | 1
                    self.__byteArray[lastSetByteIndx] = lastSetByteVal    
                    #and update the length of the representedBits with the length of the added off-bits and the last appended on-bit.
                    self.__representedBits += self.__unsetTailBitsLen + 1
                    self.__unsetTailBitsLen = 0
                    return
                else:
                    # Find the number of bits which can fit into the last byte
                    remainingUnsetBits = self.__unsetTailBitsLen - lastByteUnusedBits #TODO: rename var
                    # Find the number of bytes and bits required to further store the full new bit data.
                    requiredBytes, remainderBits = divmod(remainingUnsetBits, 8)
                    offsetByteIndx = lastSetByteIndx + requiredBytes

                    # Insert the unset bits to the unset portion of the lastSetByte
                    self.__byteArray[lastSetByteIndx] =  lastSetByteVal << (8 - lastSetByteVal.bit_length()) 
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
                        self.__byteArray[offsetByteIndx +1] |= 1 << (7 - remainderBits)

                    self.__representedBits += self.__unsetTailBitsLen + 1
                    self.__unsetTailBitsLen = 0
                    return  
    
    def popBit(self): pass

    def insertBit(self, indx: int): pass

    def remove(self, indx: int): pass

    def extend(self, bits: Iterable[bool]): pass


