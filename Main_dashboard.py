'''
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
'''

from flask import Flask, render_template, request, redirect, url_for
import webbrowser
import os
from Testing_Equipment.VIAVI_VOA.VOA_Basic_Functions import VOA_Attn
from SNMP_Modules.SNMP_Functions import SNMP_Set_SMM_Owner_Mode
import json
from QC_REST_Functions import get_Release_QC
import glob
#from pyscripts.Tests.Shilo.inventory_optics.Alpha_optic_modules import Generate_optics_excel
from Alpha_optic_modules import Generate_optics_excel
#from pyscripts.Find_Cli.Finding_CliPort_thread_mapping import Cli_Mapping

IP = '172.16.10.108' #VOA IP
TCP_PORT = 8100
Json_Att_values = 'G:\\Docs\\Dashboard_Data' + '\\Attenuation_table.json'
#Json_Att_values = 'C:\\GitLab_new\\automation\\pyscripts\\Tests\\Shilo\\Dashboard_Alpha' +'\\Attenuation_table.json'
#Json_Att_values = 'G:\\Python\\PacketLight Automation\\pyscripts\\Tests\\Shilo\\Dashboard_Alpha' +'\\Attenuation_table.json'

# for QC GET REST 
almUserName = "shilo"
almPassword = "sl171989"
almURL = "http://lotus:8080/qcbin/"
Optic_excel_dir = "G:\\Docs\\Alpha_Optic_Modules"

Port_number = 5002
LOCAL_HOST = f'http://127.0.0.1:{Port_number}/'
Browser_Lcl_Hst = webbrowser.open(LOCAL_HOST, new=1, autoraise=True)
app = Flask(__name__)
app.config["DEBUG"] = True
print (__file__[:-3])

print("Start running Dashboard!!\n")


#def receiveScpi(self, scpiCmd:'str', timeout:'int'=5)-> 'str':
def Update_att(voa_num: 'int', voa_val: 'str'):
    with open(Json_Att_values) as json_file: # try to open file for editing, without override data
        IP_Dict = json.load(json_file) # open json file and convert it to dict in order to update values there
        
        key_owner = IP_Dict['Attenuation_voa'][voa_num-1]
        print(f'Setting Att of voa {key_owner["VOA_num"]} to {voa_val} dB!!!')
        key_owner.update({"Att_value":voa_val}) #method to update dictionary value by key- value
        
    with open(Json_Att_values, "w") as json_file:
        json.dump(IP_Dict, json_file, indent = 4) # after updating the dict with the new attenuation value, dump it again to the file as json
    

    #print("Now the new updated devices dictionary is:")
    #print(IP_Dict['Devices'])

def Update_att_read(rel_data, *args):
    print(rel_data)
    with open(Json_Att_values) as json_file: # try to open file for editing, without override data
        voa_read_dict = json.load(json_file) # open json file and convert it to dict in order to update values there
        
        voa_attribute = voa_read_dict['Attenuation_voa']
        release_attribute = voa_read_dict['Release_version']
        #print(f'Setting Att of voa {key_owner["VOA_num"]} to {voa_val} dB!!!')
    for i,voa_val in enumerate(*args):    
        voa_attribute[i].update({"Att_value":voa_val}) # method to update dictionary value by key-value pairs
    
    for i in range(len(release_attribute)): 
        for rel in rel_data: 
            if release_attribute[i]["Product"] in rel[0]:
                release_attribute[i].update({"Start_date":rel[1]}) # method to update release dates dictionary value by key-value pairs
                release_attribute[i].update({"End_date":rel[2]})
                break

    with open(Json_Att_values, "w") as json_file:
        json.dump(voa_read_dict, json_file, indent = 4) # after updating the dict with the new value- name, dump it again to the file as json

    return voa_read_dict

@app.route('/get_newest_file') # new function that call to Generate_optics_excel func in another file and generate new Optoc modules excel
def get_newest_file():
    Generate_optics_excel()
    return redirect(url_for('index'))

@app.route("/", methods=['POST'])
#@app.route("/", methods=['GET', 'POST'])
    
def Wizard_click():
    
    if request.form.get('Wizard')== 'Wizard':  
        print ('I just clicked on Recovery Wizard!')
        #os.system('G:\Python\QA_Testers_scripts\Recovery_wizard\Recovery_wizard.py')
        os.startfile(r'G:\\Python\\QA_Testers_scripts\\Recovery_wizard\\Recovery_wizard.py') # run wizard file on different server
        return redirect(url_for('index'))
    
    if request.form.get('Polatis_API')== 'Polatis_API':  
        print ('I just clicked on Polatis API!')
        #os.system('G:\Python\QA_Testers_scripts\Recovery_wizard\Recovery_wizard.py')
        os.startfile(r'G:\\Python\\PacketLight Automation\\pyscripts\\Tests\\Shilo\\Polatis_API\\polatis_api.py') # run wizard file on different server
        return redirect(url_for('index'))
    
    if request.form.get('Open_IP_excel')== 'Open_IP_excel':  
        print ('I just clicked on open the Lab_IP excel file!')
        #os.startfile(r'G:\\Docs\\General Doc\\LAB_IP address tracing.xlsx') # open the lab IP excel file
        #os.startfile(r'G:\\New_LAB_IPs.xlsx') # open the new lab IP excel file
        os.startfile(r'G:\\All LAB IPs_newest.xlsx') # open the new lab IP excel file - new file
        return redirect(url_for('index'))
    
    if request.form.get('Open_Optic_excel')== 'Open_Optic_excel':  
        print ('I just clicked on open the Optic_modules excel file!')
        # List all files in the directory
        # file_type = r"\*xlsx"
        # files = glob.glob(Optic_excel_dir + file_type)
        # # Get the newest file based on the last modified time
        # newest_file = max(files, key=os.path.getmtime)
        # print(newest_file)
        # os.startfile(newest_file) # open the Optic modules excel file

        os.startfile(r'G:\\Docs\\PL-Optics-plugin-devices.xlsx') # open Ronen's Optic modules excel file
        return redirect(url_for('index'))
    # if request.form.get('pdu')== 'pdu':  
    #     print ('I just clicked on PDU')
    #     login_url = url_for('http://20.0.6.6/', username='admin', password='password1')
    # return render_template('Dashboard_index.html', login_url=login_url)



    if request.form.get('Submit_VOA'):  
        submit_value = request.form.get("Submit_VOA")
        submit_value_num = int(submit_value.split("_")[-1]) # get the number of which submit were clicked (1/2/3/4)
        Attn_set_value = request.form.get(f'Attn_{submit_value_num}') # the value we get from the user, casting to float and send to update function
        
        print(f'Setting VOA {submit_value_num} to {Attn_set_value} dB')
        voa = VOA_Attn(port= submit_value_num, ip=IP, tcp_port=TCP_PORT)
        voa.set_Beam_block(state = 'on')
        voa.write_attenuation(Attn_set_value)
        voa.disconnect()
        Update_att(voa_num = submit_value_num, voa_val = Attn_set_value) 
            
        return redirect(url_for('index'))
    
    if request.form.get('Submit_SMM'):  
        
        Device_ip_smm_mode = request.form.get('Device_ip_smm') # the IP to perform on it change smm mode to gui owner
        print(f'Change smm mode to IP {Device_ip_smm_mode} to Gui owner')
        try:
            SNMP_Set_SMM_Owner_Mode(Device_ip_smm_mode, 'gui')
        except:
            print("Can't change SMM mode for this device IP") 

        return redirect(url_for('index'))
    

    if request.form.get('submit_QC'):   # Add the QC graph combo box per device
        # do nothing

        return redirect(url_for('index'))
        
        #return render_template('Attn_index.html', messages = messages_values, messages_span_res= messages_span_res)
        #return render_template('Dashboard_index.html', **voa_values)



@app.route("/", methods=['GET'])
def index():
    
    #connect to voa and read all 4 values
    voa = VOA_Attn(port= 1, ip=IP, tcp_port=TCP_PORT)
    all_at_list = voa.read_all_attenuation() # retrieve att values from all voa ports
    voa.disconnect()

    all_att_no_zeros = [s.rstrip("0").rstrip(".") for s in all_at_list] # method to remove trailing zeros or dot in the list of values string
    print(all_att_no_zeros)
    
    
    with open(Json_Att_values) as json_file: # try to open file for editing, without override data
        dashboard_dict = json.load(json_file) # open json file and convert it to dict in order to update values there

    Rel_list_tup = []
    # for item in dashboard_dict["Release_version"]:
    #     #product = item["Product"]
    #     rel_id = item["Project_id"]
    #     if rel_id is not None:
    #         Release_response = get_Release_QC(URL = almURL, username= almUserName, password = almPassword, domain = 'PACKETLIGHT',project = 'Main', release_id = rel_id)
    #         Rel_list_tup.append(Release_response)
        

    '''
    Rel_list_tup = []
    Release_4000M = get_Release_QC(URL = almURL, username= almUserName, password = almPassword, domain = 'PACKETLIGHT',project = 'Main', release_id = 1017) # id for 4000M rel is 1017
    Rel_list_tup.append(Release_4000M)
    print(Release_4000M)

    Release_4000T = get_Release_QC(URL = almURL, username= almUserName, password = almPassword, domain = 'PACKETLIGHT',project = 'Main', release_id = 1016) # id for 4000T rel is 1016
    Rel_list_tup.append(Release_4000T)
    print(Release_4000T)

    Release_2000AD = get_Release_QC(URL = almURL, username= almUserName, password = almPassword, domain = 'PACKETLIGHT',project = 'Main', release_id = 1014) 
    Rel_list_tup.append(Release_2000AD)
    print(Release_2000AD)
    '''

    VOA_Version_Dict = Update_att_read(Rel_list_tup ,all_att_no_zeros) # Updete the json file with the new att and release values and retrieve it as dict to use in the future
    lis_dict_ver = VOA_Version_Dict['Release_version']
    
    #return render_template('Dashboard_index_new.html', messages = all_att_no_zeros) # it is for the former format without all QC alpha data
    #return render_template('Dashboard_index_new.html', messages = all_att_no_zeros, list_dict_version = lis_dict_ver, json_test= json.dumps(dashboard_dict))
    return render_template('Dashboard_index_new.html', list_dict_version = lis_dict_ver, json_test= json.dumps(VOA_Version_Dict))
    #return render_template('Dashboard_index.html', json_test= json.dumps(VOA_Dict))
    

if __name__ == "__main__":
    #app.run()
    #app.run(debug=True)
    app.run(host="0.0.0.0", debug=True, port= Port_number, use_reloader=False)
    #app.run(host="localhost", port=8000, threaded=True)
