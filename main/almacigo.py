# almacigo.py


from machine import Pin, I2C, PWM
from time import sleep
from . import sim800
from . import ota_updater
from . import servicio
from . import ulcd1602
from . import water_quality
import machine, onewire, ds18x20, json
from . import pca9685
from math import pi

#display ,0 hh:mm 25.4C ...1
#display ,1 A:!**V:c #ST1250

# Create saved EEPROM data dictionary
svdEEPROM = {
    'tag'          : 'Lalmacigo',
    'tds'          : 0,            #tds al almacigo
    'temp'         : 0,            #temp de Agua
    'Aintentos'    : 0,            #num
    'Aespera'      : 0,            #dog
    'agua'         : 'na',         #agua? si,no,na
    'riego'        : 'na',
    'logProcess'   : '',
    'ver'          : '0.0',
    'numMZ'        : 0             #num mezclas
    }

# Create new modem object on the right Pins
modem = sim800.Modem(MODEM_PWKEY_PIN    = 4,
                     MODEM_RST_PIN      = 5,
                     MODEM_POWER_ON_PIN = 23,
                     MODEM_TX_PIN       = 26,
                     MODEM_RX_PIN       = 27)

# ESP32 Pin Layout
i2c = I2C(-1, sda=Pin(18), scl=Pin(19), freq=400000)        # i2c Pin
lcd = ulcd1602.LCD1602(i2c)                             # LCD1602 OBJ
#serv = pca9685.Servo(18,19,0x40)            #PCA9585 connted2pin18,19
serv = pca9685.pca9865(18,19)
ds_pin = machine.Pin(4)                                 # DS18b20 Pin
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))    # DS18B20 OBJ


# rutinas SMS
# -----------------------------------------------
def smslavar():
    #15:19/1-2Riegos
    print('LV')
    lcd.puts("#LV", 9, 1)
    servicio.riego()
    lcd.puts("   ", 9, 1)

def smsriego():
    #15:19/1-2Riegos
    print('RG')
    lcd.puts("#RG", 9, 1)
    servicio.riego()
    lcd.puts("   ", 9, 1)
    
def smsnutre():
    #15:19/OK!
    print('NT')
    lcd.puts("#NT", 9, 1)
    servicio.dosifica()
    lcd.puts("   ", 9, 1)

def smsnutrecamas():
    #15:19/OK!
    print('NC')
    lcd.puts("#NC", 9, 1)
    lcd.puts("w", 3, 1)
    servicio.nutreCamas()
    tds_now = water_quality.read_wqs()
    lcd.puts("   ", 9, 1)

def smswater():
    #15:19/OK!
    print('WT')
    lcd.puts("#WT", 9, 1)
    smsriego = servicio.llenarTanque()
    if not smsriego:
        print('no se pudo llenar tanque de agua')
        #lcd.lcd_print("fail", 2, 11)
        lcd.puts("!", 2, 1)       
        sleep(50)
    else:
        sleep(2)
    lcd.puts("   ", 9, 1)
    
def smsbandejas():
    #15:19/OK!
    print('BJ')
    lcd.puts("#BJ", 9, 1)
    servicio.vaciarBandejas()
    lcd.puts("   ", 9, 1)

def smsnuevonutriente():
    #15:19/OK!
    print('NN')
    lcd.puts("#NN", 9, 1)
    servicio.mezcla15min()
    lcd.puts("   ", 9, 1)

def smsmezcla():
    #15:19/OK!
    global svdEEPROM
    print('MZ')
    lcd.puts("m", 4, 1)
    lcd.puts("#MZ", 9, 1)
    mzsms = servicio.mezclarTanques()
    with open('svdEEPROM.json', 'r') as f:
        svdEEPROM = json.load(f)
    svdEEPROM['numMZ'] = svdEEPROM['numMZ'] + 1
    lcd.puts(str(svdEEPROM['numMZ']), 4, 1)
    with open('svdEEPROM.json', 'w') as f:
        json.dump(svdEEPROM, f)      
    lcd.puts("   ", 9, 1)

def smsversion():
    global svdEEPROM
    print('VR')
    lcd.puts("#VR", 9, 1)
    with open('svdEEPROM.json', 'r') as f:
        svdEEPROM = json.load(f)
    lcd.puts("v", 12, 0)    
    lcd.puts(str(svdEEPROM['ver']), 13, 0)   
    lcd.puts("   ", 9, 1)

def smsriegototal():
    global svdEEPROM
    print('RT')
    lcd.puts("#RT", 9, 1)
    svdEEPROM['riego'] = 'no'
    svdEEPROM['logProcess'] = 'w'
    with open('svdEEPROM.json', 'w') as f:
        json.dump(svdEEPROM, f)
    with open('svdEEPROM.json', 'r') as f:
        svdEEPROM = json.load(f)                
    lcd.puts(str(svdEEPROM['logProcess']), 2, 1)
    servicio.rutinaRiego()
    #set vars
    svdEEPROM['Aintentos'] = servicio.numSRVC
    with open('svdEEPROM.json', 'w') as f:
        json.dump(svdEEPROM, f)
    svdEEPROM['Aespera'] = servicio.dogSRVC
    with open('svdEEPROM.json', 'w') as f:
        json.dump(svdEEPROM, f)
    svdEEPROM['agua'] = servicio.aguaSRVC
    with open('svdEEPROM.json', 'w') as f:
        json.dump(svdEEPROM, f)
    svdEEPROM['riego'] = servicio.riegoSRVC
    with open('svdEEPROM.json', 'w') as f:
        json.dump(svdEEPROM, f)
    svdEEPROM['logProcess'] = servicio.lpSRVC
    with open('svdEEPROM.json', 'w') as f:
        json.dump(svdEEPROM, f)
    # tds
    svdEEPROM['tds'] = str(water_quality.read_wqs())
    with open('svdEEPROM.json', 'w') as f:
        json.dump(svdEEPROM, f)
    # temperatura
    svdEEPROM['temp'] = ds18b20()
    with open('svdEEPROM.json', 'w') as f:
        json.dump(svdEEPROM, f)            
    # reportamos
    data = dict()
    with open('svdEEPROM.json', 'r') as f:
        svdEEPROM = json.load(f)            
    #arma json dictionary data
    data['tag'] = str(svdEEPROM['tag'])
    data['tds'] = str(svdEEPROM['tds'])
    data['temp'] = str(svdEEPROM['temp']) 
    data['num'] = str(svdEEPROM['Aintentos'])
    data['dog'] = str(svdEEPROM['Aespera'])
    data['agua'] = svdEEPROM['agua']
    data['riego'] = svdEEPROM['riego']
    data['logProcess'] = svdEEPROM['logProcess']
    data['ver'] = str(svdEEPROM['ver'])
    data['numMZ'] = str(svdEEPROM['numMZ'])
    #Now running https POST...
    print('Now running https POST...')
    #lcd.puts("    ", 12, 0)
    #lcd.puts("post", 12, 0)
    url  = 'http://box2039.temp.domains/~quantid5/freskita/postalm.php'
    data = json.dumps(data)
    response = modem.http_request(url, 'POST', data, 'application/json')  
    lcd.puts("   ", 9, 1)
# -----------------------------------------------
                                          # codes
codes ={
    'MZ' : smsmezcla,                  #cheched!
    'RG' : smsriego,
    'NN' : smsnuevonutriente,
    'BJ' : smsbandejas,
    'WT' : smswater,    
    'NC' : smsnutrecamas,
    'NT' : smsnutre,
    'LV' : smslavar,
    'RT' : smsriegototal,
    'VR' : smsversion                  #cheched!
#    'ST' : smsreporte,
#    'SR' : smssensores,
    }


## Simple software WDT implementation
wdt_counter = 0

def wdt_callback():
    global wdt_counter
    wdt_counter += 1
    if (wdt_counter >= 2000):#90==1min /estaba en 750
        #sleep(5)
        machine.reset()

def wdt_feed():
    global wdt_counter
    wdt_counter = 0

wdt_timer = machine.Timer(-1)
wdt_timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=lambda t:wdt_callback())
## END Simple software WDT implementation


class AlmacigoSRVC:
    def __init__(self, lastest_ver):
        print('start...')
        lcd.puts("...7", 12, 0)                  # 1st task
        # Create data to save2EEPROM
        global svdEEPROM
        #with open('svdEEPROM.json', 'w') as f:
        #    json.dump(svdEEPROM, f)
        with open('svdEEPROM.json', 'r') as f:
            svdEEPROM = json.load(f)
        lcd.puts("...6", 12, 0)                  # 2nd task
        lcd.puts("00:00 00.0C", 0, 0)              # file 0
        lcd.puts("A:!!!V:", 0, 1)                  # file 1
        lcd.puts("...5", 12, 0)                  # 3rd task
        # registro mezclas y riego
        lcd.puts(str(svdEEPROM['numMZ']), 4, 1)               
        lcd.puts(str(svdEEPROM['logProcess']), 2, 1)
        # close valve
        closeV = servicio.closeValve()
        # set/save actual version
        self.lastest_ver = lastest_ver                # ver
        svdEEPROM['ver'] = str(self.lastest_ver)
        with open('svdEEPROM.json', 'w') as f:
            json.dump(svdEEPROM, f)
        lcd.puts("...4", 12, 0)                  # 4th task
        water_quality.set_K_wqs()      # Init Water Quality
        water_quality.set_params_wqs()
        water_quality.read_wqs()
        lcd.puts("     ", 11, 0)
        lcd.puts("...3", 12, 0)                  # 5th task
        # Initialize the modem
        modem.initialize()
        lcd.puts("...2", 12, 0)                  # 6th task
        # Connect the modem
        modem.connect(apn='internet.tigo.bo')
        lcd.puts("  ip", 11, 0)
        print('\nModem IP address: "{}"'.format(modem.get_ip_addr()))
        lcd.puts("...1", 12, 0)                  # 7th task
        # Are time&Date valid?
        modem.get_NTP_time_date()
        rx_time_date = modem.get_time_date()# read Time&Date
        print('Date = ', rx_time_date[8:16])
        rx_time = rx_time_date.split(',')[-1].split('-')[0]
        year = str(rx_time_date[8:10])
        if (year < "20"):
            lcd.puts("...0", 12, 0)              # 8th task
            lcd.puts("rst!", 12, 0)
            sleep(2)
            machine.reset()   
        lcd.puts("...0", 12, 0)                  # 9th task
        modem.set_cnmi()         # Enable CMTI notification
        modem.del_smss()               # Delete all SMS msg
        modem.set_text_mode()           # SEt SMS text mode                   
        lcd.puts("done", 12, 0)                 # done task
        sleep(2)
        process()                                    # main

# ----------------------------------------------------------
def process():
    global svdEEPROM
    lcd.puts("     ", 11, 0)                     # cls task
    while True:
        wdt_feed()                              # reset WDT
        system_clk = modem.get_time_date() # read Time&Date
        # print('Date = ', system_clk[8:16])
        sys_time = system_clk.split(',')[-1].split('-')[0]
        # print('System TIME: {}'.format(sys_time))
        hr = str(sys_time.split(':')[0])
        minu = str(sys_time.split(':')[1])

        lcd.puts(":", 2, 0)     #:
        lcd.puts(hr, 0, 0)      #hora
        lcd.puts(minu, 3, 0)    #minute
        
                                             # dairy setups            
        if int(hr) == 21 and int(minu) == 0:
            with open('svdEEPROM.json', 'r') as f:
                svdEEPROM = json.load(f)
            svdEEPROM['numMZ'] = 0
            lcd.puts(str(svdEEPROM['numMZ']), 4, 1)
            with open('svdEEPROM.json', 'w') as f:
                json.dump(svdEEPROM, f)
            sleep(65)                # wait a little longer
            #newFirmware()  # CHECK/DOWNLOAD/INSTALL/REBOOT
            # rutina de servicio noche 21:00
            #lcd.lcd_print("                ", 4, 0)
            
                                          # time to routine
        #if ((hr[0]=="0") and (int(hr[1])==4) and (minu == "30")):                                 
        #if ((int(hr[0])==1) and (int(hr[1])==0) and (minu == "05")):    ok!
        if ((hr[0]=="0") and (int(hr[1])==4) and (minu == "30")):
            #fila0  hh:mm 25.4C ...1
            #fila1  A:!**V:c #ST1250
            svdEEPROM['riego'] = 'no'
            svdEEPROM['logProcess'] = 'w'
            with open('svdEEPROM.json', 'w') as f:
                json.dump(svdEEPROM, f)
            with open('svdEEPROM.json', 'r') as f:
                svdEEPROM = json.load(f)                
            lcd.puts(str(svdEEPROM['logProcess']), 2, 1)
            servicio.rutinaRiego()
            #set vars
            svdEEPROM['Aintentos'] = servicio.numSRVC
            with open('svdEEPROM.json', 'w') as f:
                json.dump(svdEEPROM, f)
            svdEEPROM['Aespera'] = servicio.dogSRVC
            with open('svdEEPROM.json', 'w') as f:
                json.dump(svdEEPROM, f)
            svdEEPROM['agua'] = servicio.aguaSRVC
            with open('svdEEPROM.json', 'w') as f:
                json.dump(svdEEPROM, f)
            svdEEPROM['riego'] = servicio.riegoSRVC
            with open('svdEEPROM.json', 'w') as f:
                json.dump(svdEEPROM, f)
            svdEEPROM['logProcess'] = servicio.lpSRVC
            with open('svdEEPROM.json', 'w') as f:
                json.dump(svdEEPROM, f)
            # tds
            svdEEPROM['tds'] = str(water_quality.read_wqs())
            with open('svdEEPROM.json', 'w') as f:
                json.dump(svdEEPROM, f)
            # temperatura
            svdEEPROM['temp'] = ds18b20()
            with open('svdEEPROM.json', 'w') as f:
                json.dump(svdEEPROM, f)            
            # reportamos
            data = dict()
            with open('svdEEPROM.json', 'r') as f:
                svdEEPROM = json.load(f)            
            #arma json dictionary data
            data['tag'] = str(svdEEPROM['tag'])
            data['tds'] = str(svdEEPROM['tds'])
            data['temp'] = str(svdEEPROM['temp']) 
            data['num'] = str(svdEEPROM['Aintentos'])
            data['dog'] = str(svdEEPROM['Aespera'])
            data['agua'] = svdEEPROM['agua']
            data['riego'] = svdEEPROM['riego']
            data['logProcess'] = svdEEPROM['logProcess']
            data['ver'] = str(svdEEPROM['ver'])
            data['numMZ'] = str(svdEEPROM['numMZ'])
            #Now running https POST...
            print('Now running https POST...')
            #lcd.puts("    ", 12, 0)
            #lcd.puts("post", 12, 0)
            url  = 'http://box2039.temp.domains/~quantid5/freskita/postalm.php'
            data = json.dumps(data)
            response = modem.http_request(url, 'POST', data, 'application/json')
            #sleep(55)
            #lcd.puts("    ", 12, 0)
            #lcd.puts("done", 12, 0)
            # report sent successfully!   
                
                                               # data rcved        
        sms_rqst = modem.check_sms_rcv()       
        vals = list(sms_rqst.values())
        if vals[1] != '0':
            work = codes[vals[0]]
            work()
            
                                                   # mezcla
        if int(hr) in range(10,23,3) and (minu == "15"):
            lcd.puts("m", 4, 1)
            lcd.puts("MZ", 10, 1)
            mz = servicio.mezclarTanques()
            with open('svdEEPROM.json', 'r') as f:
                svdEEPROM = json.load(f)
            svdEEPROM['numMZ'] = svdEEPROM['numMZ'] + 1
            lcd.puts(str(svdEEPROM['numMZ']), 4, 1)
            with open('svdEEPROM.json', 'w') as f:
                json.dump(svdEEPROM, f)
            lcd.puts("  ", 10, 1)
            

        ds18b20()                    # read&LCD1602 ds18b20
        #water_quality.read_wqs()             # waterquality                  
# ----------------------------------------------------------

# NewUPdate2install?
def newFirmware():
    from main import ota_updater
    ota_updater = ota_updater.OTAUpdater('https://github.com/mastercba/almacigo')
    ota_updater.download_and_install_update_if_available('TORRIMORA', 'santino989')
    ota_updater.check_for_update_to_install_during_next_reboot()   

# DS18B20
def ds18b20():
    roms = ds_sensor.scan()
    ds_sensor.convert_temp()
    for rom in roms:
      temp = ("%.1f" % round(ds_sensor.read_temp(rom), 1))  
      lcd.puts(temp, 6, 0)          # ds18b20->lcd2004
      #lcd.lcd_print("C", 10, 0)
    return temp
    