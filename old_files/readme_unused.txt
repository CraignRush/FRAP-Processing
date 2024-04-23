# Not sure, if still needed:
## Specific Prequisties for Mac-Users

- Install the lastest XQartz X11 server and run it

* Activate the option ‘[Allow connections from network clients](https://blogs.oracle.com/oraclewebcentersuite/running-gui-applications-on-native-docker-containers-for-mac)’ in XQuartz settings
* After installation, open `Preferences > Security` and make sure both boxes are checked.
* Quit & restart XQuartz (to activate the setting)
* Open `System Preferences > Network`. You can find your ip address here.
* Open a CMD window and execute

  ```shell
  xhost +
  set-variable -name DISPLAY -value 10.39.0.21:%your_display_number%.0

  ```

## Specific prequisites for Windows users

(from the instructions under [https://dev.to/darksmile92/run-gui-app-in-linux-docker-container-on-windows-host-4kde](https://dev.to/darksmile92/run-gui-app-in-linux-docker-container-on-windows-host-4kde))

* Install [VcXsrv Windows X Server](https://sourceforge.net/projects/vcxsrv/)
* Start XLaunch from the start-menu (as admin)
* Select _Multiple Windows_
* Select a desired _Display Number_
* Select _Start no client_
* Tick all boxes
* Save configuration under C:/User/_youruser_
* Open the PowerShell
* Get your internet IP of your PC via

  ```
  ipconfig
  ```

  * you'll probably see something like: IPv4-Adresse.... 10.xxxxxxx
* Execute this:
* ```
  set-variable -name DISPLAY -value 10.39.0.21:%your_display_number%.0
  ```

## How to start the docker container

1. Install docker
2. Download the image
   ```
   (docker pull ubuntu:18.0)
   docker pull python:3.9-slim-bullseye   
   ```
3. 
4. Open a command line window
5. Naviagat to the folder {YOUR_PATH_HERE}/docker
6. Build the container by
   ``docker build -t test-model . ``
7. Run the container with
   ``docker run -ti -v "/_pathToYourProcessingStacks:/app_home/data" -e DISPLAY=$DISPLAY test-model``
