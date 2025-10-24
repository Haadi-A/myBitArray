Imagine we have a bit array with the structure as follows:
[100|10010|100] = [10000|00010010|00100]
[00000000]
[10000000]

Properties:
A combination of bit and bits position is used to represent data.

Terminology:
on-bit: 1
off-bit: 0
unset-bit: Bits with no values, eg. 11 = 1011 padding the high bits without values with 0s to form a byte. 
                                        [1011] = [00001011]
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
                                                 