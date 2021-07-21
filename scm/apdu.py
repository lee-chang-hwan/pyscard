"""APDU module
"""


class APDU(object):
    """APDU class
    """

    #define static variables
    OFFSET_CLA = 0
    OFFSET_INS = 1
    OFFSET_P1 = 2
    OFFSET_P2 = 3
    OFFSET_LC = 4
    OFFSET_DATA = 5

    def __init__(self, apdu):
        """Constructor

        Args:
            apdu -- full command apdu(str or list).

        Raise:
            The apdu argument must be str or list.
            If it is not str or list, raise the TypeError.
        """
        self._apdu_buffer = []
        if type(apdu) is str:
            for i in range(0, len(apdu), 2):
                self._apdu_buffer.append(int(apdu[i:i+2], base=16))
        elif type(apdu) is list:
            self._apdu_buffer = apdu
        else:
            raise TypeError
        print(self._apdu_buffer)

    def get_apdu(self):
        """Returns the apdu buffer
        """
        return self._apdu_buffer

    def cla(self):
        """Gets the Class byte

        Returns:
            The Class byte
        """
        return self._apdu_buffer[APDU.OFFSET_CLA]

    def ins(self):
        """Gets the Instruction

        Returns:
            The Instruction
        """
        return self._apdu_buffer[APDU.OFFSET_INS]

    def p1(self):
        """Gets the P1

        Returns:
            The P1
        """
        return self._apdu_buffer[APDU.OFFSET_P1]

    def p2(self):
        """Gets the P2

        Returns:
            The P2
        """
        return self._apdu_buffer[APDU.OFFSET_P2]

    def response(self, resp, sw1, sw2):
        """Sets a response message

        Argss:
            response -- data of the resposne message
            sw1 -- status word1
            sw2 -- status word2
        """
        self.resp = resp
        self.sw1 = sw1
        self.sw2 = sw2

    def parse_response(self):
        """Parses data of the response message in the Command

        Returns:
            Parsed resposne data
        """
        raise NotImplementedError


class GetStatus(APDU):
    """GET STATUS Command class
    """

    def __init__(self, apdu):
        """Constructor

        Args:
            apdu -- full command apdu(str or list).

        Raise:
            The apdu argument must be str or list.
            If it is not str or list, raise the TypeError.
        """
        super().__init__(apdu)

    def parse_response(self):
        """Parses data of the response message in the Command

        Returns:
            Parsed resposne data(list)
        """
        rets = []
        if self.resp[0] == 0xE3:
            #GlobalPlatform Registry Data(TLV)
            raise NotImplementedError
        elif self.resp[0] >= 5 and self.resp[0] <= 10:
            try:
                if self.p1() != 0x80 and self.p1() != 0x40 \
                   and self.p1() != 0x20 and self.p1() != 0x10:
                    raise ValueError
                i = 0
                while True:
                    data = []
                    len_aid = self.resp[i]
                    i = i + 1
                    data.append(self.resp[i:i+len_aid])
                    i = i + len_aid
                    data.append(self.resp[i])
                    i = i + 1
                    data.append(self.resp[i])
                    i = i + 1
                    if self.p1() == 0x10:
                        ems = []
                        em_num = self.resp[i]
                        i = i + 1
                        for l in range(em_num):
                            len_aid = self.resp[i]
                            i = i + 1
                            ems.append(self.resp[i:i+len_aid])
                            i = i + len_aid
                        data.append(ems)
                    rets.append(data)
                    if i >= len(self.resp):
                        break
            except IndexError:
                raise ValueError
        else:
            raise ValueError
        return rets