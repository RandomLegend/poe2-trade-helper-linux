# poe2-trade-helper-linux
PoE2 Trade Request Helper for Linux | QT6

A little Window that shows incoming trade requests with the item and colorcoded prices to quickly glance if you should react immediately or can let a request sleep for a moment.

I just vibecoded this to be honest. It simply looks at the Client.txt logfile and uses regex to figure out what to show you.

# Screenshot
![screenshot](https://github.com/user-attachments/assets/a42e9f74-b199-431f-8112-b28f521346a1)

# Installation
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

5. Edit the config.json file to change your colormaps and, if needed, correct your Client.txt logfiles path.

6. Run the Application using Python.
```
python3 poe.py
```
