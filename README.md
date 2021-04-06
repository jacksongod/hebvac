# hebvac

## Intro
The script help find HEB vaccine slot. It drives chrome browser and find the earliest available slot with requirements defined. Proceeds to the final schedule page. Send Imessage to alert user to complete personal info to schedule the appointment.


## Requirements 
- MacOS.
- Messages app is set up for sending messages (For alerting)
- python3 (tested on Python 3.8.5)
- Chrome browser and [ChromeDriver](https://chromedriver.chromium.org/downloads)
- VPN recommended. 

## Instructions 
1. Install requirement:
```
pip3 install -r requirements.txt
```

3. Copy config_template.yaml  as config.yaml
4. Modify config.yaml with intended requirements 
    - There are 3 filters for cities , distance and vaccine types. use_* key are to enabled them . 
    - Multiple filters are AND together . 
    - It uses applescript to send messages. A existing conversion entered phone number/ ID needs to be opened in Messages app before hand for that script to work. 
    - my_zipcode for origin for distance 
    - chrome_driver_path points to ChromeDriver executable.
5. Run
```
python3 selenium_hebvac.py
```