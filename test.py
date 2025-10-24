
IS_DEBUG = False

def isNaar(n: int)-> bool:
    nArr: list[str] = list(str(n))
    if IS_DEBUG: print("n split is: ", nArr)
    nLen: int = len(nArr)
    if IS_DEBUG: print("n len: ", nLen)
    accum: int = 0
    
    for digit in nArr:
        digitToLenPow = int(digit) ** nLen
        if IS_DEBUG: print(digit, " ** ", nLen, ' = ', digitToLenPow)
        accum += digitToLenPow
        if IS_DEBUG: print('Curr accumlator value: ', accum)
    
    isNNarccisit: bool = accum == n
    if IS_DEBUG: print("Is N narcissit: ", isNNarccisit)
    return isNNarccisit



l: list[bool] = []
for i in range(10_000):
    l.append(isNaar(i))
    if l[-1] == True: 
        print(i, " : ", 'True')
        print('-'*50)

print("All is Nar: ", all(l))
print("Any is Nar: ", any(l))





            # # resize the bytearray and recall the appendBit.
            # print(f'last byte {self.__byteRpr[-1]}, {self.__lastIndxContainingByte()}')
            # if self.__byteRpr[lastIndxContainingByte] < 255:
            #     print(f'last byte {self.__byteRpr[-1]} in the array list: {self.__byteRpr}  is less than 255 proceeding to set...')
            #     if isSet:
            #         # Checking if the bytearray can accomodate the unset tail bits.
            #         if ceil(self.__unsetTailBits / 8) < availableBytesSpace:
            #             if lastIndxContainingByte + 1 < len(self.__byteRpr):

            #         else:
            #             # Checking if the bytearray has space for one more byte...
            #             if lastIndxContainingByte + 1 < len(self.__byteRpr):

            #         if self.__unsetTailBits < 8:
            #             # Fill empty bit slots with 0s until bits len is 8
            #             lastNonZeroByteValStrRpr += '0' * (8 - len(lastNonZeroByteValStrRpr))
            #             # Set the cut-off bit
            #             # TODO: FIX BYTE STARTING ORIENTATION.
            #             lastByteStrRpr = lastByteStrRpr[: self.__unsetTailBits] + '1'
            #             lastByte = int(lastByteStrRpr, 2)
            #             # Update the edited last byte. 
            #             self.__byteRpr[-1] = lastByte
            #             # reset off tail bits number to zero. 
            #             self.__unsetTailBits = 0
            #         elif self.__unsetTailBits >= 8:
            #             prevLen = len(self.__byteRpr)
            #             # resize the bytearray to accomodate the off tail bits and the last set bit.
            #             self.__resizeSelf(prevLen + (ceil(self.__unsetTailBits / 8) + 1))
            #             lastByteStrRpr = bin(self.__byteRpr[-1])[2:]
            #             # Find the number of the remaining unset bits
            #             lastByteFreeBits = lastByteStrRpr[::-1].find('1')
            #             # Take the last free bits out __tailOffBitsNo
            #             self.__unsetTailBits = self.__unsetTailBits - lastByteFreeBits
            #             # Now skip the number of bytes that would accomodate the number __tailOffBitsNo
            #             # To get the indx of the last byte when the unset tail bits are considered.
            #             selectedByte = prevLen + ceil(self.__unsetTailBits / 8)
            #             # Now set the appended bit at the last available bit 
            #             self.__byteRpr[selectedByte] |= 1 < (self.__unsetTailBits % 8)
            #             # reset off tail bits number to zero. 
            #             self.__unsetTailBits = 0  
            # else: 
            #     self.__resizeSelf(len(self.__byteRpr) + 1)
            #     print('Recalling self....')
            #     self.appendBit()

