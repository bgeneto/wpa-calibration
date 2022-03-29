# Websockets Serial Console

Web interface for serial console writen in Python (using tornado and websockets). 

User can receive and send data to a serial device.

## Install 
```bash
git clone https://github.com/bgeneto/WebsocketsSerialConsole.git
cd WebsocketsSerialConsole
python3 -m pip install -r requirements.txt
```
## Usage
```bash
python3 server.py
```
Please configure your serial device and web server settings (serial port, baud rate, ip...) in `config.ini` file. 
This file is created automaticaly (with default values) in the first run. 

WARNING: it may be required to run this (`server.py`) script as `sudo` if using lower ports (eg. 80, 443) for the tornado web server. So install packages also with `sudo` if this is the case.
