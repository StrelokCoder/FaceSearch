# Setup

#### Download
* As the step says download repository and unpack it, than follow step below.

#### How to setup browser
1. Before doing anything below you have to set your browser in config.ini at current_browser(firefox for firefox, chrome for chrome), so program will know which one to choose. After that go below and choose option based on your current web browser. Note: I tried to find way to automatically check for available browser, but it's either checking filesystem or try catch.

* Firefox - GeckoDriver(If you are a linux user and you have firefox installed with snap you should check if you already have it downloaded at "/snap/bin/geckodriver". If not you can [download it here](https://github.com/mozilla/geckodriver/releases). After getting it downloaded on your system, set it's path at config.ini, in setting: geckodriver_path = path_to_geckodriver_on_your_system)
* Chrome - ChromeDriver(You can [download it here](https://sites.google.com/a/chromium.org/chromedriver/downloads). After getting it downloaded on your system, set it's path at config.ini, in setting: chromedriver_path = path_to_chromedriver_on_your_system)

#### How to install
1. Open FaceSearch folder with terminal(If you are on linux right click on FaceSearch folder, than click open in terminal, if you are on windows I have no idea)
2. Run this command "pip install -r requirements.txt" in terminal you opened to install requirements
3. Next in same terminal run this command "python main.py" to start program, it will automatically create folders and *.txt files that you need to use it, also it will download default models for face recognition

# How to use

#### Running it
1. Open folder with console, than type "python main.py" and run
2. READ and type arguments to set which mode of the program you want to use
3. You can also change some config.ini values, but please read description of them

#### How to get facebook/instagram(not fully supported yet) profiles
* "https://www.facebook.com/profile_name" <- put profile_name inside facebook_profiles.txt, single profile per line
* "https://www.instagram.com/profile_name" <- put profile_name inside instagram_profiles.txt, single profile per line

# VERY IMPORTANT INFO ABOUT LICENSE!!!
Default models(buffalo_l), that are downloaded during installation aren't mine and in order to get information about their license [go here](https://github.com/deepinsight/insightface#License)