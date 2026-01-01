from SNMP_Modules.SNMP_Functions import SNMP_Get_Optics_Description, SNMP_Get_Optic_Module_PN, SNMP_Get_System_Description
#from collections import defaultdict
import os
import json
import pandas as pd
from datetime import datetime
from time import time, sleep

# Initialize a defaultdict with a list as the default factory
#Device_optics_dict = defaultdict(list)
Device_optics_dict = {}

# List of IP address ranges
network_rec_ranges = [
    (20, 11, 29),
    # (20, 111, 129),
    # (30, 11, 29),
    # (30, 111, 129),
    # (40, 11, 29),
    # (40, 111, 129)
]

uplinks_1 = [19,20]
uplinks_2 = [200,201,202,203]
uplinks_3 = [200,201]
uplinks_4 = [230,231,232,233,234,235,236,237,238,239,240,241]

Device_dict_to_Uplink_list = {

'PL-2000ADS': uplinks_1,
'PL-2000AD Metro': uplinks_1,
'PL-2000M': uplinks_1,
'PL-2000GM':  uplinks_1,
'PL-2000T': uplinks_2,
'FB4000T' : uplinks_2,
'PL-4000T': uplinks_2,
'PL-4000M': uplinks_3,
'PL-4000G': uplinks_4,

}

# start time of the script
scriptStart = time()

def Generate_optics_excel():
    # Loop over each range and print IP addresses
    for count, range_net_rec in enumerate(network_rec_ranges):
        network, start, end = range_net_rec
        rec_num = f"Rec_num_{count+1}_network_{network}"  # Creating the key for the range of recs

        # Initialize a list of the current rec to store dictionaries for each IP address
        Device_optics_list_current_rec = []

        for i in range(start, end + 1):
            DUT_IP = f"172.16.{network}.{i}"
            
            print("IP Address:", DUT_IP)
            DEVICE_TYPE = SNMP_Get_System_Description(DUT_IP)
            print(DEVICE_TYPE)
            if DEVICE_TYPE != None and DEVICE_TYPE!= 'PL-1000TN' and DEVICE_TYPE!= 'PL-2000' and 'PL-1000' not in DEVICE_TYPE:
                try:
                    # Initialize a dictionary to store data for this IP address
                    #Device_data = {'ip': DUT_IP, 'device_type': DEVICE_TYPE}
                    Device_data = {'ip': DUT_IP, 'device_type': DEVICE_TYPE, 'optics_pn_data': []}
                    
                    # Iterate over ports for the device and collect optic module PN
                    for port in Device_dict_to_Uplink_list[DEVICE_TYPE]:
                        Optic_Module_PN = SNMP_Get_Optic_Module_PN(Device_IP= DUT_IP, Port_Number = port)
                        if Optic_Module_PN!= '':  #insert this statement only if there was optic module inside this port
                            print(f"Optic module PN for port {port}:", Optic_Module_PN)
                            # Add the new IP address and its corresponding values to the dictionary
                            #Device_optics_dict[DUT_IP].append((DEVICE_TYPE, port, Optic_Module_PN))
                            
                            # Append port and optic module PN as a dictionary to the 'optics_data' list
                            Device_data['optics_pn_data'].append({'port': port, 'optic_pn': Optic_Module_PN})
                    
                    # Append the data for this IP address to the list only if it have optic_PN data
                    if Device_data['optics_pn_data']!= []:
                        Device_optics_list_current_rec.append(Device_data)

                except Exception as e:
                    print (e)
                    #print(f"No such IP : {DUT_IP}")
                    print("\n")
        print("\n")

        # Store the list of data for this rec (with network range) in the dictionary
        Device_optics_dict[rec_num] = Device_optics_list_current_rec

    # Print the resulting dictionary
    print(Device_optics_dict)
    print("\n")



    # current directory of the script
    current_script_dir = os.path.dirname(__file__)
    #print(current_script_dir)
    Json_optics_loc = current_script_dir +'\\Optics_Alpha_data.json'

    with open(Json_optics_loc, "w") as json_file:
        json.dump(Device_optics_dict, json_file, indent = 4) # after updating the dict with the new value- name, dump it again to the file as json


    #convert the dictionary with all the data to list of dict in a form of DataFrame that will generted to excel
    # List to store extracted data
    extracted_data = []

    # Iterate through each top-level key (e.g., "first", "second")
    for rec_key, device_list in Device_optics_dict.items():
        # Iterate through each device in the list
        for device in device_list:
            
            # Extract IP and device_type
            ip = device["ip"]
            device_type = device["device_type"]
            
            # Iterate through each optic data entry
            for optic_data in device["optics_pn_data"]:
                port = optic_data["port"]
                optic_pn = optic_data["optic_pn"]
                
                # Append a new row to the extracted data
                extracted_data.append({
                    "IP": ip,
                    "Device Type": device_type,
                    "Port": port,
                    "Optic PN": optic_pn
                })


    # Create DataFrame from the extracted data
    df = pd.DataFrame(extracted_data)

    Optic_excel_dir = "G:\\Docs\\Alpha_Optic_Modules"
    # date and time in order to create the excel file
    Date_time = datetime.now().strftime('%H%M%S_%Y%m%d_') 
    excel_file_path = Optic_excel_dir + '\\' + Date_time + 'Alpha_Optic_Modules.xlsx'

    # Create an Excel writer object
    writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Alpha_optics', index=False)

    # Get the workbook and sheet objects
    workbook = writer.book
    worksheet = writer.sheets['Alpha_optics']

    # Create a format for centering and wrapping text
    #cell_format = workbook.add_format({'align': 'center', 'text_wrap': True, 'shrink': True})

    # Apply the format to all cells
    #worksheet.set_column(0, df.shape[1] - 1, None, cell_format)  # Adjust column range if needed

    # Auto-size columns
    for idx, col in enumerate(df):  # loop through all columns
        series = df[col]
        max_len = max((series.astype(str).map(len).max(), len(str(col)))) + 1  # len of largest item
        worksheet.set_column(idx, idx, max_len)  # set column width
        
        # Center-align text
        cell_format = writer.book.add_format({'align': 'center'})
        worksheet.set_column(idx, idx, None, cell_format)

    # Add filter to header row (assuming header is in row 0)
    worksheet.autofilter(0, 0, 0, df.shape[1] - 1)  # Adjust range if header is not in row 0

    # Save the Excel file
    writer.save()

    print("Excel file has been created successfully.")

# Measure how long the script took to run
scriptStop = time()
scriptDuration = round((scriptStop - scriptStart)/60, 1)
print(f'All script duration is {scriptDuration} minutes')





'''
df = pd.DataFrame()
for rec_number, data_list in Device_optics_dict.items():
    print(rec_number)
    print(data_list)
    # Create a DataFrame for the data in this range
    range_df = pd.DataFrame(data_list)
    
    # Add a prefix to the columns to distinguish between ranges
    range_df = range_df.add_prefix(f"{rec_number}_")
    # Concatenate the range DataFrame with the main DataFrame
    df = pd.concat([df, range_df], axis=1)
    

# Define the Excel file path
excel_file_path = current_script_dir + '\\Alpha_Optics_Module.xlsx'

# Write the DataFrame to an Excel file
df.to_excel(excel_file_path, index=False)

print("Excel file has been created successfully.")


Date_time = datetime.now().strftime('%H%M%S_%Y%m%d_') 
excel_file_path = current_script_dir + '\\' + Date_time + 'Alpha_Optics_Module.xlsx'



# Create an Excel writer object
writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')

# Loop over each key-value pair in range_data_dict
for rec_number, data_list in Device_optics_dict.items():
    # Create a DataFrame for the data in this range
    range_df = pd.DataFrame(data_list)
    
    # Add a prefix to the columns to distinguish between ranges
    range_df = range_df.add_prefix(rec_number)
    
    # Write the DataFrame to a new sheet in the Excel file
    range_df.to_excel(writer, sheet_name=f"Rec_number_{rec_number}", index=False)

# Save the Excel file
writer.save()

print("Excel file has been created successfully.")


# Create an Excel writer object
with pd.ExcelWriter(excel_file_path, engine='xlsxwriter') as writer:
    # Loop over each key-value pair in range_data_dict
    for rec_number, data_list in Device_optics_dict.items():
        # Create a DataFrame for the data in this range
        range_df = pd.DataFrame(data_list)
        
        # Add a prefix to the columns to distinguish between ranges
        range_df = range_df.add_prefix(f"{rec_number}_")
        
        # Write the DataFrame to a new sheet in the Excel file
        range_df.to_excel(writer, sheet_name=rec_number, index=False)
        
        # Access the workbook and worksheet objects
        workbook  = writer.book
        worksheet = writer.sheets[rec_number]
        
        # Auto-size columns
        for idx, col in enumerate(range_df):  # loop through all columns
            series = range_df[col]
            max_len = max((series.astype(str).map(len).max(), len(str(col)))) + 1  # len of largest item
            worksheet.set_column(idx, idx, max_len)  # set column width

print("Excel file has been created successfully.")
'''
