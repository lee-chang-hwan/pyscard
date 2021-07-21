"""Globalplatform module
"""

NO_DERIVATION = "none"
CPG201 = 'cpg201'
CPG211 = 'cpg211'


class GP(object):
    """GlobalPlatform class
    """

    def __init__(self, cnt):
        """Construct a new GlobalPlatform.

        Args:
            cnt -- the scm.system.Connector instance
        """
        pass

    def mutual_auth(self, **kwlist):
        """Perform mutual auth between a card and a terminal.

        Keyword arguments:
            enc -- the encryption key
            mac -- the message authentication code key
            dek -- the data encryption key
            rule -- the derivation rule (default NO_DERIVATION)

        Returns:
            True/ False -- If mutual auth is success, it will return True.
            sw1 -- Status word1
            sw2 -- Status word2

        Raise:
            RuntimeError -- runtime error
            NotImplementedError -- supports only SCP02
        """
        pass