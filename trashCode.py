
    # def appendBit(self, isSet: bool = True):
    #     if not isSet:
    #         self.__unsetTailBits
    #     else:

    #         lastSetByteIndx = self.__getLastSetByteIndex()
    #         availableBytesSpace = len(self.__byteArray) - (lastSetByteIndx + 1)
    #         lastNonZeroByteValStrRpr = bin(
    #             self.__byteArray[lastSetByteIndx])[2:]
    #         availableBitsSpace = 8 - len(lastNonZeroByteValStrRpr)
    #         if self.__unsetTailBits == 0:
    #             if self.__byteArray[lastSetByteIndx] < 255:
    #                 if self.__byteArray[lastSetByteIndx] == 0:
    #                     self.__byteArray[lastSetByteIndx] |= 1 << 7
    #                     return
    #                 else:
    #                     # lastSetBitIndx = (len(lastNonZeroByteValStrRpr) - 1) - lastNonZeroByteValStrRpr[::-1].find('1') <<-- Previous solution
    #                     lastSetBitIndx = BitArray.__getByteLastSetBitIndx(
    #                         self.__byteArray[lastSetByteIndx])
    #                     lastNonZeroByteValStrRpr = lastNonZeroByteValStrRpr[:lastSetBitIndx +
    #                                                                         1] + '1' + lastNonZeroByteValStrRpr[lastSetBitIndx + 2:]
    #                     self.__byteArray[lastSetByteIndx] = int(
    #                         lastNonZeroByteValStrRpr, 2)
    #                     return
    #             else:
    #                 self.__resizeSelf(len(self.__byteArray) + 1)
    #                 self.__byteArray[lastSetByteIndx + 1] |= 1 << 7
    #                 return
    #         else:
    #             # Check if the unsetTailBits can fit into the byte array
    #             # TODO: -----CONTINUE HERE
    #             # MAKE SURE UR BIT CHECKS ARE CORRECT....
    #             if ceil(self.__unsetTailBits / 8) < availableBytesSpace:
    #                 # if the unsetTailBits can fit into the last byte and still accomodate the appended bit:
    #                 if self.__unsetTailBits < availableBitsSpace:
    #                     if self.__unsetTailBits == 1:
    #                         if self.__byteArray[lastSetByteIndx] % 2 == 0:
    #                             self.__byteArray[lastSetByteIndx] = self.__byteArray[lastSetByteIndx] + 1
    #                         else:
    #                             self.__byteArray[lastSetByteIndx] = self.__byteArray[lastSetByteIndx] + 2
    #                     else:
    #                         pass
    #                     # print('No outstanding unset tail bits, setting the last bit..')

    #                 # Else if the unsetTailBits can not fit into only the last byte...

    #             # Else resize the bytearray to accomodate the no. of unset bits.
    #             else:
    #                 requiredBytes = len(self.__byteArray) + \
    #                     ceil(self.__unsetTailBits / 8) + 1
    #                 self.__resizeSelf(requiredBytes)
    #                 self.appendBit()
