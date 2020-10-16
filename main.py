# MAIN - Lalmacigo
# -----------------------------------------------------------------------------

from main.ota_updater import OTAUpdater


def download_and_install_update_if_available():
    ota_updater = OTAUpdater('https://github.com/mastercba/Lalmacigo')
    ota_updater.download_and_install_update_if_available('TORRIMORA', 'santino989')

def start():
    from main import ota_updater
    #from main import time_date
    from main.almacigo import AlmacigoSRVC

#     ota_updater = OTAUpdater('https://github.com/mastercba/Lalmacigo')
#     ota_updater.using_network('TORRIMORA', 'santino989')
#     ota_updater.check_for_update_to_install_during_next_reboot()

    # Read version
#    lastest_ver = ota_updater.read_current_version()
    lastest_ver = '1.0'
    # Begin MAINcode
    almacigoPRJ = AlmacigoSRVC(lastest_ver)

def boot():
#     download_and_install_update_if_available()
    start()
    

boot()
# -----------------------------------------------------------------------------
