import time
from smartcard.CardType import AnyCardType
from smartcard.CardConnection import CardConnection
from smartcard.CardType import ATRCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.util import toHexString, toBytes

def trace_command(apdu):
    print('sending ' + toHexString(apdu))

def trace_response( response, sw1, sw2 ):
    if None==response: response=[]
    print('response: ', toHexString(response), ' status words: ', "%02x %02x" % (sw1, sw2))

#cardtype = ATRCardType(toBytes("3B 6B 00 00 00 31 C0 64 1F 27 01 00 00 90 00"))
#cardtype = ATRCardType(toBytes("3B 6E 00 00 80 31 80 66 B0 84 0C 01 6E 01 83 00 90 00"))
cardtype = AnyCardType()
cardrequest = CardRequest(timeout=10, cardType=cardtype)
cardservice = cardrequest.waitforcard()

observer=ConsoleCardConnectionObserver()
cardservice.connection.addObserver( observer )

cardservice.connection.connect()
print("ATR : " + toHexString(cardservice.connection.getATR()))

time.sleep(1)

GET_RESPONSE = [0x00,0xC0,0x00,0x00]
SELECT_FACE_APPLET = [0x00,0xA4,0x04,0x00,0x0C,0xD4,0x10,0x06,0x20,0x21,0x55,0x4E,0x6C,0x4F,0x4E,0x46,0x00]
apdu = SELECT_FACE_APPLET
#trace_command(apdu)
response, sw1, sw2 = cardservice.connection.transmit(apdu)
#trace_response( response, sw1, sw2 )
if sw1 == 0x61:
  apdu = GET_RESPONSE + [sw2]
  #trace_command(apdu)
  response, sw1, sw2 = cardservice.connection.transmit(apdu)
  #trace_response( response, sw1, sw2 )



