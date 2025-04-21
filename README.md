# ![icon](https://github.com/user-attachments/assets/c6b454d4-dacb-4cf6-b15e-4b990c9c0313) 

## PoE2 Trade Request Helper for Linux | QT6

A little Window that shows incoming trade requests with the item and colorcoded prices to quickly glance if you should react immediately or can let a request sleep for a moment.

I just vibecoded this to be honest. It simply looks at the Client.txt logfile and uses regex to figure out what to show you.

# Screenshot
![screenshot](https://github.com/user-attachments/assets/a42e9f74-b199-431f-8112-b28f521346a1)

# Installation
Head over to the Releases and download the Appimage
https://github.com/RandomLegend/poe2-trade-helper-linux/releases/tag/Appimage

Double click it and you're done.

# Manual Installation of python script
1. Clone the github repo to a location you want.
```
git clone https://github.com/RandomLegend/poe2-trade-helper-linux
```
2. Change into the directory
```
cd poe2-trade-helper-linux
```
3. Install the python requirements
```
pip install -r requirements.txt
```

5. Run the Application using Python.
```
python3 poe-trade-notifier.py
```
# Configuration
In the the Settings menu you have to locate your Client.txt path. This is usually in:
/home/YOURUSERNAME/.local/share/Steam/steamapps/common/Path of Exile 2/logs/Client.txt

After that you can add rows for your colormappings of the prices.
The "price" column include the amount AND currency name. For example: 10 exalted or 2 divine and the color column can be doubleclicked to open a colorpicker.
