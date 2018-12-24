#### *WTRobot.*

## Introduction:

WTRobot is a tool to minimize your dependencies on XPATHs for writing end to end automation. Which basically uses
Selenium as its core engine.

The tool follows a yml scripting which you will find below.

## Setup Instructions:
```
- Clone the repo.
- cd into the downloaded directory.
- Run following command
    > make
```

## Executing Script:
```
Just write all your test cases into script.yml file using cmds[1]
Also always make sure you activate your python env while running tool.
> source python3Env/bin/activate
> python engine.py run #to execute the demo script.
```

You need to specify few settings in config.json file.
1) menu_region
2) workspace_region
3) settings_region

[1] WTRobot scripting:- 

Website independent:- 
 - SEQUENCE  :- This also can be called as test case specifier. In this you have to specify the sequence of testcases that you will write. 
 
 - IMPORT  :- It is used to call test cases into one another.
  
 - GOTO  :- Goes to the link provided by user.
 
 - INPUT :- It is core functionality to give the input into text box.
 
 - PRINT :- It is simple print function to debug your scripting.
 
 - SLEEP :- By default it sleeps for 10 secs, you can also specify the time in front of this function.
 
 - SCREENSHOT :- You can also specify which screens you wish to capture. It is recommended to give a small 2-3 secs sleep before taking screenshots.  
 
 - CLICK :- You need to mention the text you wish to click on. If the text is present multiple times then you can also specify the region which you added in config.json.
 
 - HOVER :- You need to mention the text you wish to move your mouse on. If the text is present multiple times then you can also specify the region which you added in config.json.
  
 - I18N :- For now it takes out all the text present on the page and also maintain a new file with remaining english words.

Website Dependent:- It depends on sites made by patternfly with the menu region on left side as shown in this picture.
![Imgur](https://i.imgur.com/XB5Wt0G.jpg)
 - NAVIGATE :- This is a navigation simplification function. It basically uses HOVER and CLICK only in background.

For further reference you can go through the sample file called as script.yml.

QA:

Q: Why is script failing with "Message: newSession"?

A: You need to update your webdriver.

IF you are using Firefox then follow this steps.

Go on this link below and download the latest build of geckodriver according to your system configuration.
>  https://github.com/mozilla/geckodriver/releases

Unzip the tar and place the executable in ./selenium_drivers/ .


*Happy Coding :)*