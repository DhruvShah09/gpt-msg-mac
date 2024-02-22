import openai 
import os
import pandas as pd 
import numpy as np
import re
import subprocess
from datetime import datetime, timedelta

class Messages:
    def __init__(self):
        self.contacts = self.initialize_contacts("my_contacts.csv")
        self.last_message = {}
        self.msg_history = {}
        if not os.path.exists("messages"):
            os.mkdir("messages")
        self.fn_map, self.numerical_map = self.file_name_mapping("messages")  
        self.history_window = 2  
        
    def initialize_contacts(self, contacts_file):
        contacts = pd.read_csv(contacts_file)
        cols = contacts.columns[2:]
        phone_number_to_name = {}
        for i in range(len(contacts[cols[0]])):
            j = 0
            while j < len(cols):
                if type(contacts[cols[j]][i]) == str or np.isnan(contacts[cols[j]][i]) == False:
                    #parse phone number from contacts[cols[j]][i]
                    digits = re.findall(r'\d', contacts[cols[j]][i])
                    # Concatenate the digits together
                    digits = ''.join(digits)
                    if len(digits) > 10:
                        digits = digits[-10:]
                    phone_number_to_name[digits] = contacts["First name"][i] if type(contacts["First name"][i]) == str or np.isnan(contacts['First name'][i]) == False else contacts["Last name"][i] if type(contacts["Last name"]) == str or np.isnan(contacts["Last name"][i]) == False else "Unknown"
                    break
                j += 1
        return phone_number_to_name
    
    def has_only_digits_and_plus(self, input_string):
    # Define the regular expression pattern
        pattern = re.compile(r'^[0-9+]+$')
        # Check if the input string matches the pattern
        if re.match(pattern, input_string):
            return True
        else:
            return False

    def file_name_mapping(self, msg_dir_path):
        #filenames look like +1XXXXXXXXXX.txt or some country code + some number of digits, map the last 10 digits before the .txt to the name of the person
        file_name_mapping = {}
        numerical_map = {}
        for filename in os.listdir(msg_dir_path):
            #ignore all files with letters others than .txt in the filename
            #check if there are any letters in the filename 
            if not self.has_only_digits_and_plus(filename.rstrip('.txt')):
                continue
            if filename.endswith(".txt"):
                digits = re.findall(r'\d', filename)
                digits = ''.join(digits)
                if len(digits) > 10:
                    digits = digits[-10:]
                file_name_mapping[digits] = filename
                numerical_map[filename.rstrip('.txt')] = digits
        return file_name_mapping, numerical_map
    
    def clean_msg(self, msg):
        i = 0
        msg_list = msg.split('\n\n')
        for msg_block in msg_list:
            msg_block = msg_block.strip().split('\n')
            if len(msg_block) == 1:
                x = msg_list[0]
                msg_block = [x[0], x[1], msg_block[0]]
            if msg_block[1] == 'Me':
                msg_block[1] = 'Me'
            elif msg_block[1].strip() in self.numerical_map:
                if self.numerical_map[msg_block[1].strip()] in self.contacts:
                    msg_block[1] = self.contacts[self.numerical_map[msg_block[1].strip()]]
                else:
                    msg_block[1] = msg_block[1]
            else:
                msg_block[1] = msg_block[1]
            msg_list[i] = msg_block
            i += 1
        return msg_list
    
    def append_block(self, msg_block):
        r_str = ''
        for chunk in msg_block:
            r_str += chunk
        return r_str
    
    def update_message(self):
        try:
            for number, filename in self.fn_map.items():
                with open(os.path.join("messages", filename), "r") as f:
                    msg = f.read().strip()
                    msg = self.clean_msg(msg)
                    self.last_message[number] = msg[-1]
                    self.msg_history[number] = msg
            return True
        except:
            return False
    
    def format_date(self, days_ago):
        target_date = datetime.now() - timedelta(days=days_ago)
        formatted_date = target_date.strftime("%Y-%m-%d")
        return formatted_date
        
    def fetch_msg(self):
        #os specific utility function 
        try:
            if os.path.exists("messages"):
                os.system("rm -rf messages")
            command = ["imessage-exporter", "-f", "txt", "-s", self.format_date(self.history_window), "-omessages"]
            subprocess.run(command, stdout=subprocess.PIPE)
            self.fn_map, self.numerical_map = self.file_name_mapping("messages")
            return True
        except:
            return False

    def fetch_and_update_msgs(self):
        self.fetch_msg()
        self.update_message()    
    
        
    

    

     

    
    
    
    

    
    
    
            
                

if __name__ == '__main__':            
    R_gen = Messages()
    R_gen.fetch_and_update_msgs()
