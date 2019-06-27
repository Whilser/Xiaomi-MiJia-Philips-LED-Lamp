# Xiaomi MiJia Philips LED Lamp Domoticz Plugin

This plugin is required to add the Xiaomi MiJia Philips LED Lamp to the list of supported devices Domoticz Home Automation System. The plugin was tested with python 3.5.x and Domoticz 4.x installed on Raspberry Pi.

![Philis Bulb](https://github.com/Whilser/Xiaomi-MiJia-Philips-LED-Lamp/raw/master/images/PhilipsBulb.png)

## Currently supported:

- [x] Philips Bulb
- [x] Philips ZhiRui downlight
- [x] Philips ZhiYi ceiling lamp
- [x] etc. Xiaomi MiJia Philips LED lamp (basic support)

## Установка / How to Install:

    sudo apt-get update && sudo apt-get upgrade -y
    sudo apt-get install python3 python3-dev python3-pip
    sudo apt-get install libffi-dev libssl-dev
    sudo pip3 install -U pip setuptools
    sudo pip3 install -U virtualenv
    cd domoticz/plugins
    git clone https://github.com/Whilser/Xiaomi-MiJia-Philips-LED-Lamp.git PhilipsLED
    cd PhilipsLED
    virtualenv -p python3 .env
    source .env/bin/activate
    pip3 install python-miio
    deactivate

    sudo service domoticz restart

## Обновление / How to update:

    cd domoticz/plugins/PhilipsLED
    git pull
    sudo service domoticz restart

To configure device, enter the IP Address and Token of your Philips Lamp. The `Scene` parameter creates a selector of the standard Philips lamp scenes. Set the scene parameter `show` to display scenes, otherwise set to `hide`. Plugin creates a Philips LED Lamp and a selector of the standard Philips lamp scenes as an option on request.

![Domoticz plugin](https://github.com/Whilser/Xiaomi-MiJia-Philips-LED-Lamp/raw/master/images/DomoticzUnit.png)

**This plugin is under development.**

# Плагин Xiaomi MiJia Philips LED Lamp для Domoticz

Плагин добавляет поддержку светодиодных ламп Xiaomi MiJia Philips LED Lamp в систему домашней автоматизации Domoticz. Для настройки плагина введите IP адрес и токен устройства. Параметр `Сцены` создает селекторный переключатель стандартных сцен Philips LED Lamp, установите его в положение `show` если планируете использовать сцены, в противном случае установите положение флажка в `hide`. Флажок `Debug` предназначен для выявления ошибок и отладки плагина. Для того, чтобы техническая информация не сыпалась в консоль, флажок Debug рекомандуется установить в положение `False`.
