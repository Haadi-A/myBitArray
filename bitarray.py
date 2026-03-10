from math import ceil
from typing import Iterable
IS_DEBUG_MODE = True

class BitArray(list[bool]):
    def __init__(self, strRpr:str= ''):
        self.__byteArray = bytearray(1) if strRpr == '' else self.__initByteArray(strRpr)

        # Create a byte array with bytes less
        self.__unsetTailBitsLen: int = 0
        '''Used to represent the number of off-bits appended to the end of the byte array but not yet reflected in the byte array.'''
        
        self.__representedBits: int = 0
        '''Used to represent the number of bits, be it on or off bits which are not unset tail bits: **[__unsetTailBits]**'''


    def __initByteArray(self, strRpr: str)-> bytearray:

        # strRprLen = len(strRpr)
        intervaledStr = self.intervaledCharInserter(strRpr)
        # print(f'__initByteArray(): Delineated str: ', intervaledStr)
        splittedStrRpr = intervaledStr.split('|')
        if splittedStrRpr[-1] == '': splittedStrRpr.pop()
        # print(f'__initByteArray(): SplittedString: ', splittedStrRpr, 'elements len: ', len(''.join(splittedStrRpr)))

        # print(f'__initByteArray(): BA:               [', end='')
        print(f"splitted string chars len: {len(splittedStrRpr)} {splittedStrRpr}")
        bytesItrbl = [int(byte, 2) for byte in splittedStrRpr]
        
        ba = bytearray(bytesItrbl)
        return ba 
           

    @property
    def repBits(self)-> int: return self.__representedBits
    
    @property
    def unsetBits(self)-> int: return self.__unsetTailBitsLen

    def __len__(self) -> int:
        '''Returns the bit length of the bytearray'''
        lSByteIndx = self.__getLastSetByteIndx()
        lSByteBitsNo = self._getByteLastSetBitIndx(self.__byteArray[lSByteIndx]) + 1
        return lSByteIndx * 8  + \
                lSByteBitsNo + self.__unsetTailBitsLen 

    def __repr__(self) -> str:
        """
        Return a concatenated string of 8-bit binary representations for the instance's byte array.

        Each integer in self.__byteArray is converted to binary (without the '0b' prefix),
        left-padded with zeros to exactly 8 digits, and then all byte strings are joined
        into one continuous string.

        Returns:
            str: The concatenated 8-bit binary string representing the byte array.

        Notes: 
            - Expects each element of self.__byteArray to be an integer in the range 0-255.
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
    

    @staticmethod
    def intervaledCharInserter(undelinieatedStr: str, sep: str = '|', interval: int = 8)-> str:
        # itrbl = list(itrbl)
        # Ignore input if char len < 9
        if len(undelinieatedStr) < 9: return undelinieatedStr + sep 
        iPrv, iNxt = 0, interval
        editedItrbl:list[str] = []
        itrblLen = len(undelinieatedStr)
        # print("intervaled char inserter: here is the itrbl: ", undelinieatedStr, ' itrbl len: ', itrblLen)
        if itrblLen <= interval: return undelinieatedStr
        
        while True:
            # print(f'iPrv: {iPrv}, iNxt: {iNxt}')
            if iNxt > itrblLen:
                if iPrv < itrblLen:
                #    print("$$$$: Curr slice's: ", undelinieatedStr[iPrv:])
                   editedItrbl.append(''.join(undelinieatedStr[iPrv:]))
                # print("G-", editedItrbl)
                return ''.join(editedItrbl)

            # print("Curr slice's: ", undelinieatedStr[iPrv:iNxt])
            nStr = ''.join(undelinieatedStr[iPrv:iNxt]) + sep
            editedItrbl.append(nStr)
            iPrv = iNxt 
            iNxt += 8

        # print("here is the editedItrbl: ", editedItrbl)
        # editedItrbl[-1] = editedItrbl[-1][:-1]
        # # print("G-", editedItrbl)
        # lkl = ''.join(editedItrbl)
        # print("here is the editedItrbl: ", lkl, ' Element len: ', len(''.join(''.join(lkl).split('|'))))
        # return lkl 

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
        if 0 < indx and indx > 7:
            raise IndexError('Index :{0} is out of range of the byte index range: 0 - 7'.format(indx))
        elif byteBitLen <= 8:
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

    @staticmethod
    def _getByteLastSetBitIndx(lastByte: int) -> int:
        '''
        Returns: -1 when byte is 0 ie. no set bit in the byte 
                but if there is any set bit in the byte, it will return the corresponding index for it. 
        '''
        if lastByte == 0:
            return -1
        elif lastByte > 255:
            raise ValueError('Byte must be within range(0, 256)')

        # lastByteStrRpr = bin(lastByte)[2:]
        # lastByteStrRpr = ((8 - len(lastByteStrRpr)) * '0') + lastByteStrRpr 
        lastByteStrRpr = format(lastByte, '08b') 
        flippedLastByte = lastByteStrRpr[::-1]

        for indx, bit in enumerate(flippedLastByte):
            if bit == '1':
                return 7 - indx
        else:
            return 0
    

    def canholdXbytes(self, bytesLen: int)-> bool:
        if len(self.__byteArray) >= bytesLen:return True
        else: return False


    def append(self, isSetBit: bool=True):
        # before appending check whether appended bit is an on or off-bit?
        # If its an on-bit:
        if IS_DEBUG_MODE: print('Unset tail bits: ', self.__unsetTailBitsLen)
        if isSetBit:
            if IS_DEBUG_MODE: print('Is on-bit')
            # Check whether or not the bytearray can hold the tail unset bits and the last on-bitt?
            newBitsLen = self.__unsetTailBitsLen + 1
            byteArrayNewSize: int = (self.__getLastSetByteIndx() + 1) + ceil(newBitsLen / 8)

            # No it can't:
            if not self.canholdXbytes(byteArrayNewSize):
                # resize the array to have enough space for both the unset tail bits and the last on-bit.
                self.__resizeSelf(byteArrayNewSize)
                
            # Check whether or not there are tail unset bits.
            # Yes there are:
            if self.__unsetTailBitsLen > 0:
                # get required byte-bit pair.
                requiredByteIndx, requiredBits = self.__getByteBitPair() 
                if requiredBits == 8: 
                    requiredByteIndx += 1
                    lSByte = self.__byteArray[requiredByteIndx]
                    requiredBits = 0
                if IS_DEBUG_MODE: print('returned byte-bit pair: ', requiredByteIndx, requiredBits)
                
                # in the requiredByte set the bit at required bits + 1
                lSBCorrectByte = self._setBitInByte(self.__byteArray[requiredByteIndx], requiredBits)
                if IS_DEBUG_MODE: print('lSBCorrectByte', bin(lSBCorrectByte)[2:]) 
                self.__byteArray[requiredByteIndx] = lSBCorrectByte 
                self.__unsetTailBitsLen = 0

            # No there aren't:
            else:
                if IS_DEBUG_MODE: print('Branch D: ')
                # Set the [last set bit] + 1 in the [last set byte].
                lSByteIndx = self.__getLastSetByteIndx()
                if IS_DEBUG_MODE: print('lSByteIndx:', lSByteIndx) 
                lSByte = self.__byteArray[lSByteIndx]
                requiredBits = self._getByteLastSetBitIndx(lSByte) + 1
                if requiredBits == 8: 
                    lSByteIndx += 1
                    lSByte = 0
                    requiredBits = 0
                if IS_DEBUG_MODE: print('calculated byte-bit pair: ', lSByteIndx, requiredBits)
                self.__byteArray[lSByteIndx] = self._setBitInByte(lSByte, requiredBits) 

        # If its an off bit:
        else:
            if IS_DEBUG_MODE: print('Is off-bit')
            # Just increment the counter for the tail unset bits.
            self.__unsetTailBitsLen += 1
        

    def __getByteBitPair(self)-> tuple[int, int]:
        # Find the last set byte
        lSByteIndx = self.__getLastSetByteIndx()
        lSByte = self.__byteArray[lSByteIndx]
        if IS_DEBUG_MODE: print('lSByteIndx: ', lSByteIndx)
        # Find the free bit-space in the last set byte
        lSByteSetBitsNo = self._getByteLastSetBitIndx(lSByte)+1
        if IS_DEBUG_MODE:  print('lSByteSetBitsNo: ', lSByteSetBitsNo)
        freeBitSpace = 8 - lSByteSetBitsNo 
        # Subtract the free bit-space from the tail unset bits length.
        remTailUnsetBits = (self.__unsetTailBitsLen) - freeBitSpace 

        if remTailUnsetBits < 0:
            requiredBits = lSByteSetBitsNo + self.__unsetTailBitsLen
            if IS_DEBUG_MODE: print('branch a0: ', lSByteIndx, requiredBits)
            # Set the required byte-bit pair
            return (lSByteIndx, requiredBits)
        elif remTailUnsetBits == 0:
            if IS_DEBUG_MODE: print('branch a: ', lSByteIndx+1, 0)
            # Set the required byte-bit pair
            return (lSByteIndx+1, 0)
        elif remTailUnsetBits <= 8:
            # Set the required byte-bit pair
            if IS_DEBUG_MODE: print('branch b: ', lSByteIndx+1, remTailUnsetBits)
            return (lSByteIndx + 1, remTailUnsetBits)
        else:
            # Find how many bytes you are gonna need for the remaining unset bits length,
            # that is excluding the bits already subtracted from the last set byte.
            # Set the required byte-bit pair
            requiredBytes, requiredBits = divmod(remTailUnsetBits, 8)
            requiredBytes = requiredBytes + 1 if requiredBits > 0 else requiredBytes  
            print('branch c: ', requiredBytes, requiredBits)
            return (requiredBytes, requiredBits+1)


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


    def _byteArrayUnusedBitsNo(self)-> int:
        bytearrayBitsLen = len(self.__byteArray) * 8 
        # print(f'!!From free space checker:  bytearray len: {bytearrayBitsLen} representedBits: {self.__representedBits}')
        return bytearrayBitsLen - self.__representedBits 



    def popBit(self): pass
    
    def clear(self) -> None:
        self.__byteArray = bytearray()
        self.__unsetTailBitsLen = 0
        self.__representedBits = 0
        return super().clear()
    
    def insertBit(self, indx: int): pass

    def removeBit(self, indx: int): pass

    def extend(self, bits: Iterable[bool]): pass


if __name__ == '__main__':
    pass