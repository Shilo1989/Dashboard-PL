Created by: Shilo Levavi 1/1/2023
My first dashboard for Alpha packetlight.
This page contain short access to the following:

    - All 6 PDU element
    - Recovery Wizard i have also made
    - Polatis page/ Polatis app I have made
    - Device panel IP
    - VOA Attenuation 4 ports

in order the file to opened at start up pc:
    -Type shell:startup in windows run - This opens the Startup folder. 
    - Copy and paste the shortcut to the app from the file location to this folder.

in order to add bat file as service:
sc create dashboard_alpha displayname= "DashboardTest" type= own binpath= "G:\Python\PacketLight Automation\pyscripts\Tests\Shilo\Dashboard_Alpha\run_dashboard.bat"
To delete this service from services.msc:
SC DELETE dashboard_py

new features:
15.3.23 -  add handle for new VIAVI VOA, set parameters, and get them with refresh to the web page.
           We have a json with all the data in Attenuation_table.json and we read and write to it.
6.7.23 - Add progress bar for version advance by date, and combo box to show reports by project.
25.2.24 - After Miluim, change VOA IP to the new network 172
20.5.24 - Add new IPexcel, and optic modules excel files

Ports API:
This dashboard - 5002
Polatis -5001
Alpha Devices panel -http://172.16.10.52:5000/
