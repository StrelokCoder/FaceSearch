# IT ONLY WORKS ON LINUX WITH FIREFOX RIGHT NOW
In future windows and chromium support might be added(if someone helps me with that)

# Setup

#### Requirements
* Firefox
* Geckodriver(If firefox is downloaded with snap you should have geckodriver here "/snap/bin/geckodriver", if not you can [download it here](https://github.com/mozilla/geckodriver/releases))

#### How to install
1. Set geckodriver_path at config.ini to path where your geckodriver is located at
2. Download this repository and open it with terminal(right click on repository, than click open in terminal)
3. Run this command "pip install -r requirements.txt" in terminal you opened in previous step to install requirements
4. Next in same terminal run this command "python main.py" so program will automatically create folders and *.txt files that you need to use it, also default models for face recognition will be downloaded

# How to use

#### Running it
1. Open folder with console, than type "python main.py" and run
2. READ and type arguments to set which mode of the program you want to use
3. You could also change config.ini values

#### How to get facebook/instagram(not fully supported yet) profiles
* "https://www.facebook.com/profile_name" <- put profile_name inside facebook_profiles.txt, single profile per line
* "https://www.instagram.com/profile_name" <- put profile_name inside instagram_profiles.txt, single profile per line

# VERY IMPORTANT INFO ABOUT LICENSE!!!
Default models(buffalo_l), that are downloaded during installation aren't mine and they are subjected to this [license](https://github.com/deepinsight/insightface#License)