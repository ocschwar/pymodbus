'''
Contains base classes for modbus request/response/error packets
'''
from pymodbus.mexceptions import NotImplementedException

#---------------------------------------------------------------------------#
# Logging
#---------------------------------------------------------------------------#
import logging
_logger = logging.getLogger('pymodbus.protocol')

#---------------------------------------------------------------------------#
# Base PDU's
#---------------------------------------------------------------------------#
class ModbusPDU:
    '''
    Base class for all Modbus mesages

    @param transaction_id This value is used to uniquely identify a request
    response pair.  It can be implemented as a simply counter

    @param protocol_id This is a constant set at 0 to indicate Modbus.  It is
    put here for ease of expansion.

    @param unit_id This is used to route the request to the correct child. In
    the TCP modbus, it is used for routing (or not used at all.  However, for
    the serial versions, it is used to specify which child to perform the
    requests against.

    @param check This is used for LRC/CRC in the serial modbus protocols
    '''

    def __init__(self):
        ''' Initializes the base data for a modbus request '''
        self.transaction_id     = 0
        self.protocol_id        = 0
        self.unit_id            = 0x00 # can also be 0xff
        self.check              = 0x0000

    def encode(self):
        ''' Encodes the message '''
        _logger.error("Method not implemented")
        raise NotImplementedException()

    def decode(self, data):
        '''
        Decodes data part of the message.
        @param data is a string object
        '''
        _logger.error("Method not implemented")
        raise NotImplementedException()

class ModbusRequest(ModbusPDU):
    ''' Base class for a modbus request PDU '''

    def __init__(self):
        ''' Proxy to the lower level initializer '''
        ModbusPDU.__init__(self)

    def doException(self, exception):
        '''
        Builds an error response based on the function
        @param exception The exception to return
        '''
        _logger.error("Exception Response F(%d) E(%d)" %
                (self.function_code, exception))
        return ExceptionResponse(self.function_code, exception)

class ModbusResponse(ModbusPDU):
    ''' Base class for a modbus response PDU '''

    def __init__(self):
        ''' Proxy to the lower level initializer '''
        ModbusPDU.__init__(self)

#---------------------------------------------------------------------------#
# Exception PDU's
#---------------------------------------------------------------------------#
class ModbusExceptions:
    '''
    This is simply an enumeration of the valid modbus exceptions
    '''
    IllegalFunction                 = 0x1
    IllegalAddress                  = 0x2
    IllegalValue                    = 0x3
    SlaveFailure                    = 0x4
    Acknowledge                     = 0x5
    SlaveBusy                       = 0x6
    MemoryParityError               = 0x8
    GatewayPathUnavailable          = 0xA
    GatewayNoResponse               = 0xB

class ExceptionResponse(ModbusResponse):
    ''' Base class for a modbus exception PDU '''
    ExceptionOffset = 0x80

    def __init__(self, function_code, exception_code=None):
        '''
        Initializes the modbus exception response
        @param function_code The function to build an exception response for
        @param exception_code The specific modbus exception to return
        '''
        ModbusResponse.__init__(self)
        self.function_code = function_code | self.ExceptionOffset
        self.exception_code = exception_code

    def encode(self):
        ''' Encodes a modbus exception response '''
        ret = chr(self.exception_code)
        return ret

    def decode(self, data):
        '''
        Decodes a modbus exception response
        @param data The packet data to decode
        '''
        self.exception_code = ord(data[0])

    def __str__(self):
        return "Exception Response (%d, %d)" % (self.function_code,
                self.exception_code)

class IllegalFunctionRequest(ModbusRequest):
    '''
    Defines the Modbus slave exception type 'Illegal Function'
    This exception code is returned if the slave:
    - does not implement the function code **or**
    - is not in a state that allows it to process the function
    '''
    ErrorCode = 1

    def __init__(self, function_code):
        ModbusRequest.__init__(self)
        self.function_code = function_code

    def decode(self, data):
        pass

    def execute(self, context):
        return ExceptionResponse(self.function_code, self.ErrorCode)

__all__ = [
        'ModbusRequest', 'ModbusResponse', 'ModbusExceptions',
        'ExceptionResponse', 'IllegalFunctionRequest',
]
