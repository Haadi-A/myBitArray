from math import ceil
from typing import Iterable


class BitArray():
    def __init__(self, ):
        # Create a byte array with bytes less
        self.__maxSetBit = 0
        # self.__byteArray: bytearray = bytearray([11])
        self.__byteArray = bytearray(1)
        # self.__byteArray [0] = 40
        # print('Last non-zero byte indx: ', self.__getLastSetByte())
        # print(' val: ', self.__byteRpr[self.__getLastSetByte()])
        self.__unsetTailBits: int = 0

    def __len__(self) -> int:
        '''Returns the bit length of the bytearray'''

        lSBI = self.__getLastSetByteIndex()
        byteLastSetBitIndx = BitArray.__getByteLastSetBitIndx(self.__byteArray[lSBI])

        return ((lSBI - 1) * 8) + byteLastSetBitIndx + self.__unsetTailBits

    def __repr__(self) -> str:
        return ''.join('0'*(8-len(bin(byte)[2:])) + bin(byte)[2:] for byte in self.__byteArray)

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
        '''newSize: int -> Number of bytes for the new resized bytearray not the number of bits.'''
        buff, buffSize = self.__byteArray, len(self.__byteArray)
        if newSize > buffSize:
            self.__byteArray = bytearray(newSize)
            self.__byteArray[: buffSize] = buff
        elif newSize < buffSize:
            # TODO: IMPLEMENT ARRAY DOWNSIZING.
            pass

    def set(self, indx: int):
        # TODO: UPDATE TO CONSIDER WHEN __tailOffBits != 0.
        byteIndx, bitIndx = divmod(indx, 8)
        # print('byteIndx:', byteIndx, 'bitIndx:', bitIndx, sep=' ')
        if byteIndx + 1 > len(self.__byteArray):
            self.__resizeSelf(byteIndx + 1)

        self.__byteArray[byteIndx] |= 1 << (7 - bitIndx)
        # print(indx, ' : ', self.__str__())
        # stMr = '{0:2d} : {1:71s}'.format(indx, self.__str__())
        # print(stMr)

    @staticmethod
    def _setBitInByte(byte: int, indx: int) -> int:
        byteBitLen = byte.bit_length()
        print('\tbyte bit len: ', byteBitLen)
        if byteBitLen <= 8:
            byte |= 1 << (7 - indx)
            return byte
                # if byte == 0:
                # byte |= 1 << ((byteBitLen - 1) - indx)
                # return byte
            # if indx < byteBitLen:
            # else:
            #     raise IndexError(
            #         f"The index you provided: {indx} is out the range of the byte you provided with bit length: {byteBitLen}")
        else: 
            raise ValueError("Byte values must be within range: 0 - 255, byte value provided: ", byte)
    def clearBit_(self, indx: int):
        byteIndx, bitIndx = divmod(indx, 8)
        if 0 <= ceil(indx/8) <= len(self.__byteArray):
            highBitsByte = bin(255)[2:]
            suppressionMaske = highBitsByte[:bitIndx] + \
                '0' + highBitsByte[bitIndx+1:]
            suppressionMask = int(suppressionMaske, 2)
            # print(f"Suppression index: {bitIndx}, suppression maske: {suppressionMaske}, suppressionMask: {suppressionMask}")
            self.__byteArray[byteIndx] &= suppressionMask
            # stMr = '{0:2d} : {1:71s}'.format(indx, self.__str__())
            # print(stMr)
        else:
            raise IndexError(
                f"The provided index: {indx} is out of range of the bitArray of max indx: {len(self.__byteArray)}")

    def __getLastSetByteIndex(self) -> int:
        '''Returns index for the last set byte.'''
        # Flips the array and deducts the indx of the first non-zero byte from the max indx of the [byteRpr] bytearray
        for currIndx, byte in enumerate(self.__byteArray[::-1]):
            if byte > 0:
                return (len(self.__byteArray) - 1) - currIndx
        else:
            return 0

    @staticmethod
    def __getByteLastSetBitIndx(lastByte: int) -> int:
        if lastByte > 255:
            raise ValueError('Byte must be within range(0, 256)')

        lastByteStrRpr = bin(lastByte)[2:]
        lastByteStrRpr = ((8 - len(lastByteStrRpr)) * '0') + lastByteStrRpr
        flippedLastByte = lastByteStrRpr[::-1]

        for indx, bit in enumerate(flippedLastByte):
            if bit != '0':
                return 7 - indx
        else:
            return 0

    def appendBit(self, isSet: bool = True):
        if not isSet:
            self.__unsetTailBits
        else:

            lastSetByteIndx = self.__getLastSetByteIndex()
            availableBytesSpace = len(self.__byteArray) - (lastSetByteIndx + 1)
            lastNonZeroByteValStrRpr = bin(
                self.__byteArray[lastSetByteIndx])[2:]
            availableBitsSpace = 8 - len(lastNonZeroByteValStrRpr)
            if self.__unsetTailBits == 0:
                if self.__byteArray[lastSetByteIndx] < 255:
                    if self.__byteArray[lastSetByteIndx] == 0:
                        self.__byteArray[lastSetByteIndx] |= 1 << 7
                        return
                    else:
                        # lastSetBitIndx = (len(lastNonZeroByteValStrRpr) - 1) - lastNonZeroByteValStrRpr[::-1].find('1') <<-- Previous solution
                        lastSetBitIndx = BitArray.__getByteLastSetBitIndx(
                            self.__byteArray[lastSetByteIndx])
                        lastNonZeroByteValStrRpr = lastNonZeroByteValStrRpr[:lastSetBitIndx +
                                                                            1] + '1' + lastNonZeroByteValStrRpr[lastSetBitIndx + 2:]
                        self.__byteArray[lastSetByteIndx] = int(
                            lastNonZeroByteValStrRpr, 2)
                        return
                else:
                    self.__resizeSelf(len(self.__byteArray) + 1)
                    self.__byteArray[lastSetByteIndx + 1] |= 1 << 7
                    return
            else:
                # Check if the unsetTailBits can fit into the byte array
                # TODO: -----CONTINUE HERE
                # MAKE SURE UR BIT CHECKS ARE CORRECT....
                if ceil(self.__unsetTailBits / 8) < availableBytesSpace:
                    # if the unsetTailBits can fit into the last byte and still accomodate the appended bit:
                    if self.__unsetTailBits < availableBitsSpace:
                        if self.__unsetTailBits == 1:
                            if self.__byteArray[lastSetByteIndx] % 2 == 0:
                                self.__byteArray[lastSetByteIndx] = self.__byteArray[lastSetByteIndx] + 1
                            else:
                                self.__byteArray[lastSetByteIndx] = self.__byteArray[lastSetByteIndx] + 2
                        else:
                            pass
                        # print('No outstanding unset tail bits, setting the last bit..')

                    # Else if the unsetTailBits can not fit into only the last byte...

                # Else resize the bytearray to accomodate the no. of unset bits.
                else:
                    requiredBytes = len(self.__byteArray) + \
                        ceil(self.__unsetTailBits / 8) + 1
                    self.__resizeSelf(requiredBytes)
                    self.appendBit()


    def _availableFreeBitsSpace(self)-> int:
        '''Return the number of free **BITS** in the byte array.'''
        lSBI = self.__getLastSetByteIndex()
        bALeng = len(self.__byteArray)

        # If the last set index is the last element of the bytearray, the byte array is full.
        if bALeng == lSBI + 1: return 0
        
        freeByteSpc = bALeng - len(self.__byteArray[lSBI + 1:])
        lastByteFreeBitsSpace = self.__getByteLastSetBitIndx(self.__byteArray[lSBI])

        return 8 * freeByteSpc + lastByteFreeBitsSpace  


    def _appendBit(self, isSet: bool = True):
        # is unset
        if isSet == False:
            # increment the unsetTailBitCounter.
            self.__unsetTailBits += 1
        # is set
        else:
            # find the size of the new bits to be added.
            newBitsSize =  self.__unsetTailBits + 1
            
            # Check if the newBitsSize can be accomodated in the byte array ie:
            # The byte array has enough space to hold the newBitsSize.
            if (self._availableFreeBitsSpace() - newBitsSize) < 0:  # if not
                # resize the bytearray to have enough space for the new bits size.
                self.__resizeSelf(newSize=len(self.__byteArray) + ceil(newBitsSize / 8))

            lastSetByteIndx = self.__getLastSetByteIndex()
            # If there is no space in the last set byte to accomodate the appended bit:
            lastSetByteVal = self.__byteArray[lastSetByteIndx] 
            if self.__byteArray[lastSetByteIndx] == 255:
                # Move to the next empty byte.
                lastSetByteIndx += 1
                lastSetByteVal = self.__byteArray[lastSetByteIndx] 
                print("\t****Curr last set byte is full, moving to next byte at index: ", lastSetByteIndx - 1, " to next byte at index: ", lastSetByteIndx)
            lastByteAvailableSpace = 8 - self.__getByteLastSetBitIndx(lastByte=lastSetByteVal)    
              
            # are there unsetbits
            if self.__unsetTailBits == 0:  # no
                # print("\tLast set byte value: ", lastSetByteVal)
                # append a set bit to the appropriate last byte.
                lastSetBitInLastByte = BitArray.__getByteLastSetBitIndx(lastByte=self.__byteArray[lastSetByteIndx])
                # print("\there is last set bit in the last byte: ", lastSetBitInLastByte)
                bitToSet = 0 if lastSetByteVal == 0 else lastSetBitInLastByte + 1
                # print('\tBit to set: ', bitToSet)
                lastByteWithAppendedBit = BitArray._setBitInByte(byte=lastSetByteVal, indx=bitToSet)
                # print('\tModified last byte before save: ', lastByteWithAppendedBit)
                self.__byteArray[lastSetByteIndx] = lastByteWithAppendedBit
                # print('\tModified last byte after save: ', self.__byteArray[lastSetByteIndx])
                return
            else:# yes
                # can the last byte hold the all the unset bits and the last set bit 
                if lastByteAvailableSpace >= self.__unsetTailBits + 1 :# yes
                    print('Can the last byte hold the all the unset bits and the last set bit = tailsetBit:{0}, lastbyte bitLen: {1}. YES!'.format(self.__unsetTailBits, lastByteAvailableSpace))
                    print('Last byte value: ', self.__byteArray[self.__getLastSetByteIndex()], ' = ', bin(self.__byteArray[self.__getLastSetByteIndex()])[2:])
                    # insert the unset bits and append the last set bit.
                    self.__byteArray[lastSetByteIndx] = (lastSetByteVal << self.__unsetTailBits) + 1 
                    # Clear the unsetTailBitsCounter.
                    self.__unsetTailBits = 0
                    return
                else: # no
                    print('Can the last byte hold the all the unset bits and the last set bit = tailsetBit:{0}, lastbyte bitLen: {1}. NO!'.format(self.__unsetTailBits, lastByteAvailableSpace), )
                    # Find the number of bits which can fit into the last byte 
                    remainingUnsetBits = self.__unsetTailBits - lastByteAvailableSpace 
                    # Find the number of bytes and bits required to further store the full new bit data.
                    requiredBytes, remainderBits = divmod(remainingUnsetBits, 8)
                    offsetByteIndx = lastSetByteIndx + requiredBytes
                    
                    # 1-
                    # Insert the unset bits to the unset portion of the lastSetByte
                    self.__byteArray[lastSetByteIndx] = lastSetByteVal << lastByteAvailableSpace
                    
                    # 2-
                    # Fill the intermediate bytes with 0s
                    self.__byteArray[lastSetByteIndx + 1: offsetByteIndx + 1] = [0] * requiredBytes
                    
                    # 3-
                    # If there are no remaining unset bytes, append the last set bit.
                    if remainderBits == 0:
                        self.__byteArray[offsetByteIndx + 1] = 1 
                    # If there are a remaining bits.
                    elif remainderBits > 0:
                        # We are shifting right in order to provide padding at the most significant bit portion of the byte.
                        # Eg. byte = [0] remainderBits = 3
                        # byte |= 1 << (8 - 3)
                        # byte = [00010000] = [10000] 
                        righShiftNo = 8 - (remainderBits ) 
                        self.__byteArray[offsetByteIndx + 1] |= 1 << righShiftNo  
                self.__unsetTailBits = 0
                return

    def popBit(self): pass

    def insertBit(self, indx: int): pass

    def removeBit(self, indx: int): pass

    def extend(self, bits: Iterable[bool]): pass


print("In main")
bitAObj: BitArray = BitArray()
# print('--', bitAObj)
# bitAObj._appendBit() #type: ignore
# print('--', bitAObj)


n = 6
for i in range(1, n + 1):
    print('Runs: ', i)
    # print('Before: ', bitAObj)
    # print(bin(i)[2:])
    if i<32: bitAObj._appendBit()
    else: bitAObj._appendBit(False)
    # print('After: ', bitAObj)
    print(bitAObj)

print('-Before adding unset bit: ', bitAObj)
bitAObj._appendBit(False)
print('- After adding unset bit: ', bitAObj)
print('-Before adding tail set bit: ', bitAObj)
bitAObj._appendBit()
print('- After adding tail set bit: ', bitAObj)
# print('byte bit manipulation')
# for i in range(1, 7):
    # bitAObj.set(i)
    # print(bin(BitArray._setBitInByte(n, i))[2:])

    # print(bitAObj)

# print(bitAObj)
# bitAObj.appendBit()
# baoStr = bitAObj.__str__().replace('|', '').replace('0', '')
# baoStr = len(baoStr)
# print(baoStr)


# print(bitAObj)
# bitAObj.appendBit()
# bitAObj.appendBit()
# print(bitAObj)
# bitAObj.appendBit()
# for i in range(n):
#     bitAObj.clearBit_(i)

    # def genBitMask(self, indx: int) -> int:
    #     acc: int = 0
    #     for place in range(indx):
    #         if place != (7-bitIndx):
    #             acc += 2 ** place

    # def setBit(self, indx: int):
    #     if 0 <= indx <= self.__currOccupiedBytesNo:
    #         byteIndx, bitIndx = divmod(indx, 8)
    #         # print(f"For indx: {indx}, byteIndx is: {byteIndx} and bit indx is: {bitIndx}")
    #         # andMask = 1 << (7-bitIndx)
    #         # print(f"And mask: ", bin(andMask))
    #         self.__byteRpr[byteIndx] |=  1 << (7-bitIndx)
    #         print(indx, '-', self.__repr__(), len(self.__repr__()))

    #     else: raise IndexError(f"The provided index: {indx} is out of range of the bitArray of max indx: {self.__currOccupiedBytesNo}")

    # def clearBit(self, indx: int):
    #     if 0 < indx < self.__currOccupiedBytesNo - 1:
    #         byteIndx, bitIndx = divmod(indx, 8)
    #         self.__byteRpr[byteIndx] &= genBitMask(bitIndx)
    #         self.__repr__()
    #     else: raise IndexError(f"The provided index: {indx} is out of range of the bitArray of max indx: {self.__currOccupiedBytesNo}")

    # def append(self, isBitSet:bool):
    #     if self.__byteFilledBits + 1 > 8:
    #         self.__currOccupiedBytesNo += 1
    #         byteArrBuff = self.__byteRpr
    #         self.__byteRpr = bytearray(self.__currOccupiedBytesNo+1)
    #         self.__byteRpr = byteArrBuff

    #     self.__currOccupiedBytesNo += 1
    #     self.__byteFilledBits
    #     if isBitSet:
    #         self.__byteRpr[len(self.__byteRpr)-1] + 1


# for i in range(13):
#     bitAObj.setBit(i)
#     print(i, '-', bitAObj)

# bitAObj.append(1)


# if '__name__' == '__main__':
#    print("In main")
#    bitAObj:BitArray = BitArray()
#    bitObj.setBit(10)
#    bitAObj.append(1)
