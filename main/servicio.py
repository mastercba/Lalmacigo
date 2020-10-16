# servicio.py


from machine import Pin, I2C, PWM
from time import sleep
from . import ulcd1602
# https://github.com/mcauser/micropython-pcf8574
import json
from . import pca9685
from math import pi

riegoSRVC = ''
dogSRVC   = 0
numSRVC   = 0
aguaSRVC  = ''
lpSRVC = ''

adc = Pin(36, Pin.IN, Pin.PULL_UP)                 # ADC 36
i2cR = I2C(-1, sda=Pin(18), scl=Pin(19), freq=400000) # i2c Pin
lcdR = ulcd1602.LCD1602(i2cR)                 # LCD1602 OBJ
#serv = pca9685.Servo(18,19)                #PCA9585 - valve
serv = pca9685.pca9865(18,19)
WT = Pin(33, Pin.OUT, value=1)                 # Water Tank
RG = Pin(32, Pin.OUT, value=1)                      # RieGo
MZ = Pin(25, Pin.OUT, value=1)                     # MeZcla
NT = Pin(14, Pin.OUT, value=1)                  # NuTre A&B


class Riego:
    def __init__(self):
        print('start Riego....')
        #rutinaRiego()
#fila0  hh:mm 25.4C ...1
#fila1  A:!**V:c #ST1250        
# ---------------------------------------------------------
def rutinaRiego():
    global riegoSRVC
    global lpSRVC    
    global wdt_counter
    wdt_counter = 0                             # reset WDT
    if not llenarTanque():
        print('no se pudo llenar tanque de agua')
        lcdR.puts("  ", 10, 1)
        lcdR.puts("!", 2, 1)
        riegoSRVC = 'no'
        return   
    sleep(2)
    wdt_counter = 0                             # reset WDT
    lpSRVC = 'm'                
    lcdR.puts("m", 2, 1)    
    mezclarTanques()
    wdt_counter = 0                             # reset WDT
    sleep(2)    
    lpSRVC = 'n'                
    lcdR.puts("n", 2, 1)    
    dosifica()
    sleep(2)
    wdt_counter = 0                             # reset WDT
    lpSRVC = 'b'                
    lcdR.puts("b", 2, 1)
    vaciarBandejas()
    sleep(2)
    wdt_counter = 0                             # reset WDT
    lpSRVC = 'm'                
    lcdR.puts("m", 2, 1)   
    mezclarTanques()
    sleep(2)
    wdt_counter = 0                             # reset WDT
    lpSRVC = 'r'                
    lcdR.puts("r", 2, 1)  
    riego()
    sleep(2)
    riegoSRVC = 'si'
    lpSRVC = '*'                
    lcdR.puts("*", 2, 1)
    
# -----------------------------------------------    
def nutreCamas(): 
    #lcdR.puts("WT", 10, 1)
    global wdt_counter
    wdt_counter = 0                             # reset WDT
    if not llenarTanque():
        print('no se pudo llenar tanque de agua')
        lcdR.puts("  ", 10, 1)
        lcdR.puts("!", 3, 1)
        return
    wdt_counter = 0                             # reset WDT
    sleep(2)
    lcdR.puts("m", 3, 1)
    mezclarTanques()
    sleep(2)
    wdt_counter = 0                             # reset WDT
    lcdR.puts("n", 3, 1)    
    dosifica()    
    sleep(2)
    wdt_counter = 0                             # reset WDT    
    lcdR.puts("b", 3, 1)
    vaciarBandejas()    
    sleep(2)
    wdt_counter = 0                             # reset WDT    
    lcdR.puts("m", 3, 1)   
    mezclarTanques()    
    sleep(2)
    wdt_counter = 0                             # reset WDT    
    lcdR.puts("r", 3, 1)   
    riegoc()
    sleep(2)
    lcdR.puts("*", 3, 1)  
# -----------------------------------------------    
def closeValve():                            #OK!
    print('cerramos valvula')
    global wdt_counter
    wdt_counter = 0                  # reset WDT
    lcdR.puts(" ", 7, 1)
    sleep(2)# en segundos
    serv.setangle(0,0)
    sleep(5)# en segundos
    serv.alloff()
    lcdR.puts("c", 7, 1)
# -----------------------------------------------
def openValve():                             #OK!
    print('abrimos valvula')
    global wdt_counter
    wdt_counter = 0                  # reset WDT
    lcdR.puts(" ", 7, 1)
    sleep(2)# en segundos
    serv.setangle(0,-55)
    sleep(5)# en segundos
    serv.alloff()
    lcdR.puts("o", 7, 1)
# -----------------------------------------------    
def mezclarTanques():                        #OK!
    print('mezclar tanques')
    global wdt_counter
    wdt_counter = 0                  # reset WDT
    #lcdR.puts("MZ", 10, 1)    
    MZ.off()                             # MZ ON
    sleep(300)# en segundos 300
    MZ.on()                             # MZ OFF
    #lcdR.puts("  ", 10, 1)
# -----------------------------------------------
def dosifica():                              #OK!
    print('dosifica AB')
    global wdt_counter
    wdt_counter = 0                  # reset WDT
    NT.off()                             # NT ON
    sleep(15)# en segundos
    NT.on()                             # NT OFF
# -----------------------------------------------
def vaciarBandejas():                        #OK!
    #Close Valve
    openValve()
    #wait....
    global wdt_counter
    wdt_counter = 0                  # reset WDT
    MZ.off()                             # MZ ON
    sleep(450)# en segundos450
    MZ.on()
    wdt_counter = 0                  # reset WDT
    sleep(5) 
    MZ.off()                             # MZ ON
    sleep(450)# en segundos450
    MZ.on()     
    #Open Valve
    closeValve()
# -----------------------------------------------
def riego():                                 #OK!
    print('riego')
    global wdt_counter
    wdt_counter = 0                  # reset WDT
    sleep(2)
    RG.off()                             # RG ON
    sleep(280)#60=1minuto280
    RG.on()                             # RG OFF
    sleep(2)
# -----------------------------------------------
def riegoc():
    print('riegoCama')
    global wdt_counter
    wdt_counter = 0                  # reset WDT
    sleep(2)
    RG.off()                             # RG ON
    sleep(450)#60=1minuto
    RG.on()                             # RG OFF
    sleep(2)   
# -----------------------------------------------
def mezcla15min():
    print('nuevo nutriente')
    global wdt_counter
    wdt_counter = 0                  # reset WDT
    MZ.off()                             # MZ ON
    sleep(450)# en segundos
    MZ.on()
    wdt_counter = 0                  # reset WDT
    sleep(5) 
    MZ.off()                             # MZ ON
    sleep(450)# en segundos
    MZ.on()    
# -----------------------------------------------
def llenarTanque():
    global wdt_counter
    wdt_counter = 0                  # reset WDT
    global aguaSRVC
    global dogSRVC
    global numSRVC
    global riegoSRVC
    global lpSRVC
    print('llenamos tanque de agua')
    dogSRVC = 1
    numSRVC = 1
    lcdR.puts(str(numSRVC),12,0)
    lcdR.puts("/",13,0)
    lcdR.puts(str(dogSRVC),14,0)
    WT.off()
    sleep(2)
    MZ.off()
    while adc.value() == 1:            # 1:vacio
        print("{}vacio".format(adc.value()))
        dogSRVC = dogSRVC + 1
        print(dogSRVC)
        lcdR.puts(str(numSRVC),12,0)
        lcdR.puts("/",13,0)
        lcdR.puts(str(dogSRVC),14,0)
        sleep(1) #2
        if dogSRVC == 50:
            lcdR.puts("  ",14,0)
            if numSRVC == 4:
                print('FAIL!')
                lcdR.puts("!", 2, 1)
                WT.on()
                sleep(2)
                MZ.on()
                aguaSRVC = 'no'
                lpSRVC = '!'

                return False       #tanque vacio
            
            numSRVC=numSRVC+1
            dogSRVC=1
            WT.on()               # Turn OFF &..
            sleep(2)
            MZ.on()
            #MZ.off()
            sleep(10)    # wait a litlle longer
            WT.off()                # try again
            sleep(2)
            MZ.off()

    WT.on()               
    sleep(2)
    MZ.on()
    #MZ.off()
    sleep(2)
    #lcdR.puts("    ", 12, 0)
    aguaSRVC = 'si'
    return True                    #tanque lleno

