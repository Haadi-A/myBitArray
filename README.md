Imagine we have a bit array with the structure as follows:
[100|10010|100] = [10000|00010010|00100]
[00000000]
[10000000]

Properties:
A combination of bit and bits position is used to represent data.

Terminology:
on-bit: 1
off-bit: 0
set-bit: Bit which a value regardless of whether its an on or off bit.
unset-bit: Bits with no values, eg. 11 = 1011 padding the high bits without values with 0s to form a byte. 
                                    [1011] = [10110000]
                                                  ^^^^-> These are the unset bits.

Rules:
1- You can only get, set or clear bits which have already been appended to the bitarray.
2- To add a new bit, you need to append it.
3- Unset bits also represent data.
    eg. 11 = [1011], the unset high bits represent 0 ie. [00001011]
    if its only the first high bit which is set and the remianing bits in the bytes aren't set, how would that be represented?
    [1-------] = [1] = [10000000]
        We would employ the [LENGTH METADATA] data to know up which portion of the byte array is set.
        So in the above example the length of the bitarray would be 1 although all the remaining bits have values ie. off-bits.
        [10000000]
          -------  = only the first bit is accessible the remaining bits can not be set, cleared, or got.


Problem: 
When byte structure is as follows, if an off-bit has been appeded to the the tail of the bytearray,
trying to append an on-bit, causes an IORE (Index out of range error) which is triggered by accessing the bytearray using the value of the [usedBytes] var..
funct state at this point:
    BytearrayStruct:  11111111|11111111|11111111|11111111|11111111|11111111|11111111|11111111
    usedBits=1 
    usedBytes: 8 
    unusedBytes: -1

lastByteUnsedBits =  (7 - BitArray.__getByteLastSetBitIndx(self.__byteArray[usedBytes]))
                                                                            ^^^^^^^^^
Question: How did the usedBytes get assigned this value = 8?

Articulation of problem: When a byte is full ie.: [11111111], 
                                                if an off-bit is appended to the bit array: [11111111] + 0, 
                                                and an on-bit is then added: [11111111] + 0 + 1,
                                                value of the used bit becomes: more than the available byte.


Algorithm for the append bit method:
1- If is off-bit: just increment counter for unsetailBits.
2- Else if is on-bit: 
        If there are no tailbits:
            append 1 to the end of the bytearray.
        Else if there are tail bits:
            Check if all the tailbits and the on-bit to be appended can NOT fit into the bytearray:
                resize the bytearray then 
            Append the off-bits and the last appended on-bit.

To append the off-bits and the last appended on-bit:
Find the bitspace in the last byte.
Can the lastByte bit space can acommodate newDataBits
    Shift the lastbyte byte by the number of tailbits then;
    create a setting mask and append the on-bit.
    set tail unset bits to 0;
    and update the length of the representedBits with the length of the added off-bits and the last appended on-bit.
Subtract the bit space from the newDataBitsSize.
Find the required bytes and remainder bits in the newDataBitsSize
Right shift the lastByte byte the number of available free bit space.
set the bytes at index bytearray[lastByte + required bytes + 1] to 0
Subtract the remainder bits from 8 to know how much bits to shift the bytearray[required bytes + 2] to.
Do bytearray[required bytes + 2] = 1 << (7 - remainderBits)
This would append the last byte while shifting the remiander off-bits.   

This refactor would be perfect except if it checked and handled whether or not the last byte before editing has unused bits that the bit count of the last byte is less than 8. 
Imagine we had a bytearray with the following structure: [11111111]|[1101] and we wanted to append a set bit preceded by 12 off-bits, so __representedBits = 12, __unsetTailBits = 12. 
Following the proposed logic, 
Step 1- Calculate targetIndex = __representedBits + __unsetTailBits = 24
 Step 2- Commit unset tail bits: 
    i - add __representedBits += __unsetTailBits = 12;  __representedBits = 24  
    ii-reset __unsetTailBits to 0, __unsetTailBits = 0
Step 3 - increment the committed length: __representedBits += 1; __representedBits = 25
Step 4 - resize the bytearray:
 currSize  = len(__byteArray) = 2 < __representedBits: __resize(ceil(__representedBits/8)) = 4; new byte array structure: [11111111][1101][0][0]
Step 5 - Set the bit: 
tagetByte, targetBit = divmod(targetIndx, 8); tagetByte = 3, targetBit = 0;
self.__byteArray[targetByte] |= 1 << (7 - targetBit)
[11111111][1101][0][0]
         0          1      2    3
                                    ^-> The last byte would be selected and the bit at the index (7 - targetBit) = (7 - 0) = 7; 
Shifting 1 seven times gets us: 128 = 0b10000000; doing 0 | 128 = 128; 
The final structure of the bytearray becomes:  [11111111][1101][0][10000000]

Everything is great except for the fact that the second byte [1101] = would be interpreted as having 4 padding bits before its value (ie. [00001101]) when that was not the intended effect as the off-bits should be appended to the tail of the second byte:  [11010000] = 208.
