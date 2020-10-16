# pca9685.py

# MicroPython PCA9865 16 servo controller driver for ESP32.
#NOTE: I tried writing 16 bit values for PWM but it crashed the controller requiring a power cycle to reset.
#guy carver version
import machine
from time import sleep_us

class pca9865(object):
  '''16 servo contoller. Use index 0-15 for the servo #.'''

  _ADDRESS = 0x40
  _MODE1 = const(0)
  _PRESCALE = const(0xFE)

  _LED0_ON_L = const(0x6)                       #We only use LED0 and offset 0-16 from it.
#  _LED0_ON_H = const(0x7)
#  _LED0_OFF_L = const(0x8)
#  _LED0_OFF_H = const(0x9)

#  _ALLLED_ON_L = const(0xFA)
#  _ALLLED_ON_H = const(0xFB)
#  _ALLLED_OFF_L = const(0xFC)
#  _ALLLED_OFF_H = const(0xFD)

  _DEFAULTFREQ = const(60)
  _MINPULSE = const(120)
  _MAXPULSE = const(600)

  def __init__(self, aSDA, aSCL) :
    '''aSDA is I2C SDA pin #, aSCL is I2C SCL pin #.'''
    super(pca9865, self).__init__()
    self.i2c = machine.I2C(scl = machine.Pin(aSCL), sda = machine.Pin(aSDA))
    self._buffer = bytearray(4)
    self._b1 = bytearray(1)
    sleep_us(50)
    self.reset()
    self.minmax(_MINPULSE, _MAXPULSE)

  def minmax( self, aMin, aMax ) :
    '''Set min/max and calculate range.'''
    self._min = aMin
    self._max = aMax
    self._range = aMax - aMin

  def read( self, aLoc ) :
    '''Read 8 bit value and return.'''
    self.i2c.readfrom_mem_into(self._ADDRESS, aLoc, self._b1)
    return self._b1[0]

  def writebuffer( self, aBuffer, aLoc ) :
    """Write buffer to given address."""
    self.i2c.writeto_mem(self._ADDRESS, aLoc, aBuffer)

  def write( self, aVal, aLoc ) :
    """Write 8 bit integer aVal to given address aLoc."""
    self._b1[0] = aVal
    self.writebuffer(self._b1, aLoc)

  def reset( self ):
    '''Reset the controller and set default frequency.'''
    self.write(0, _MODE1)
    self.setfreq(_DEFAULTFREQ)

  def setfreq( self, aFreq ) :
    '''Set frequency for all servos.  A good value is 60hz (default).'''
    aFreq *= 0.9  #Correct for overshoot in frequency setting.
    prescalefloat = (6103.51562 / aFreq) - 1  #25000000 / 4096 / freq.
    prescale = int(prescalefloat + 0.5)

    oldmode = self.read(_MODE1)
    newmode = (oldmode & 0x7F) | 0x10
    self.write(newmode, _MODE1)
    self.write(prescale, _PRESCALE)
    self.write(oldmode, _MODE1)
    sleep_us(50)
    self.write(oldmode | 0xA1, _MODE1)  #This sets the MODE1 register to turn on auto increment.

  def setpwm( self, aServo, aOn, aOff ) :
    '''aServo = 0-15.
       aOn = 16 bit on value.
       aOff = 16 bit off value.
    '''
    if 0 <= aServo <= 15 :
      #Data = on-low, on-high, off-low and off-high.  That's 4 bytes each servo.
      loc = _LED0_ON_L + (aServo * 4)
#    print(loc)
      self._buffer[0] = aOn
      self._buffer[1] = aOn >> 8
      self._buffer[2] = aOff
      self._buffer[3] = aOff >> 8
      self.writebuffer(self._buffer, loc)
    else:
      raise Exception('Servo index {} out of range.'.format(str(aServo)))

  def off( self, aServo ) :
    '''Turn off a servo.'''
    self.setpwm(aServo, 0, 0)

  def alloff( self ) :
    '''Turn all servos off.'''
    for x in range(0, 16):
      self.off(x)

  def set( self, aServo, aPerc ) :
    '''Set the 0-100%. If < 0 turns servo off.'''
    if aPerc < 0 :
      self.off(aServo)
    else:
      val = self._min + ((self._range * aPerc) // 100)
      self.setpwm(aServo, 0, val)

  def setangle( self, aServo, aAngle ) :
    '''Set angle -90 to +90.  < -90 is off.'''
    #((a + 90.0) * 100.0) / 180.0
    perc = int((aAngle + 90.0) * 0.5556)  #Convert angle +/- 90 to 0-100%
    self.set(aServo, perc)



# https://github.com/OutOfTheBots/ESP32_PCA9685
#robot.set_servo(-pi/2, 0) ** -pi/2 (-90 degrees)
#-pi/4 (-45 degrees) ** pi/4 (45 degress) ** pi/2 (90 degress)
# robot.deinit() #deinit the I2C bus


#import machine, time
#from machine import Pin, I2C
#from ustruct import pack
#from math import pi

#class Servo:
#    def __init__(self, sda, scl, slave=0x40, bus_speed=1000000):
#        self.slave = slave  
#        #self.i2c = machine.I2C(0, speed=bus_speed, sda=18, scl=19)
#        #self.i2c = machine.I2C(0, sda=Pin(18), scl=Pin(19))
#        self.i2c = machine.I2C(scl=machine.Pin(scl), sda=machine.Pin(sda))
#        self.i2c.init(Pin(scl),Pin(sda))
#        self.i2c.writeto_mem(slave, 0x00, b'\x10') #set mode1 to sleep    
#        time.sleep_us(5)    
#        prescale = int((25000000/ (4096*50))+0.5)    
#        self.i2c.writeto_mem(slave, 0xfe, pack('B',prescale)) #setprescale   
#        self.i2c.writeto_mem(slave, 0x00, b'\xa1') #set mode1   
#        time.sleep_us(5)    
#        self.step = 200/(pi/2) #step size for radians   
#        for servo in range(16):  #set all servos to popsition 0    
#          on_time = servo*220      
#          off_time = on_time + 340    
#          self.i2c.writeto_mem(self.slave, 0x06 + (servo*4), pack('<HH', on_time, off_time))
#        
#    def set_servo(self, pos, servo):
#        off_time = (servo * 220) + 340 - (int(pos * self.step))     
#        self.i2c.writeto_mem(self.slave, 0x08 + (servo*4), pack('<H',off_time))
        
#    def stop(self):
#        self.i2c.stop()
        
#    def poscero(self, pos):
#        for servo in range(16):   
#          on_time = servo*220      
#          off_time = on_time + 340    
#          self.i2c.writeto_mem(self.slave, 0x06 + (servo*4), pack('<HH', on_time, off_time))