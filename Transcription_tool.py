from tkinter import *
from tkinter import filedialog
import winsound
import csv
import os
from pathlib import Path
import json
import ast

class Window(Frame):
    def __init__(self, master=None):
        # main frame
        Frame.__init__(self, master)

        # init global variables
        self.master = master
        self.input_file = None
        self.trans_text = None     #transcription
        self.correct_text = None
        self.file_dict = {}
        self.current_row = None
        self.contacts_in_list = None
        self.audio_path = None
        self.audio_file = None  #'\\mtl-autobackup\\QA\\Data_for_Accuracy\\v2\\ENU\\{user}\\{wav file}'
        self.audio_button = None   #play button
        self.skip_button = None
        self.save_button = None
        self.changeline_button = None
        self.contacts_full = ''
        self.regex_var = StringVar(value='.*')

        self.contacts_text = None  #contacts list
        self.next_var = IntVar()
        self.next_button = None
        self.out_file = None
        self.line_index = IntVar()
        self.start_row = 0

        self.init_window()

    def init_window(self):
        self.create_trans_frame()
        self.create_contacts_frame()
        self.create_menu()

    #-------------create frames and widgets--------------------
    def create_trans_frame(self):
        trans_frame = LabelFrame(self.master, text="Transcription")
        trans_frame.place(relx=0.0, rely=0.0, height=500, width=500)
        #trans_frame.grid(column=0, row=0, sticky='WENS')

        self.trans_text = Text(trans_frame)
        # self.trans_text.grid(column=0, row=0, sticky=N)
        self.trans_text.place(relx=0.0, rely=0.0, relheight=0.4, relwidth=1)

        self.correct_text = Text(trans_frame)
        # self.correct_text.grid(column=0, row=1,sticky=S)
        self.correct_text.place(relx=0.0, rely=0.4, relheight=0.4, relwidth=1)
        #correct_text.grid_propagate(False)

        #------------------audio frame-------------------------
        audio_frame = LabelFrame(trans_frame, text="Action", relief="sunken", width=300, height=100)
        # audio_frame.grid(column=0, row=4, columnspan=4, rowspan=1, sticky=EW)
        audio_frame.place(relx=0.0, rely=0.8, relheight=0.2, relwidth=1)

        self.next_button = Button(audio_frame)
        self.next_button.place(relx=0.2, rely=0.01, height=25, width=50)
        self.next_button.configure(text="Next", takefocus="", command=lambda: self.next_var.set(1))

        self.run_button = Button(audio_frame, text='Run', command=self.run)
        self.run_button.place(relx=0.4, rely=0.01, height=25, width=50)

        self.audio_button = Button(audio_frame, text='Play', command=self.play)
        self.audio_button.place(relx=0.6, rely=0.01, height=25, width=50)

        self.save_button = Button(audio_frame, text='Save', command=self.saveLine)
        self.save_button.place(relx=0.3, rely=0.01, height=25, width=50)

        self.changeline_button = Button(audio_frame, text='Go to line', command=self.change_row)
        self.changeline_button.place(relx=0.1, rely=0.5, relheight=0.3, relwidth=0.2)

        line_entry = Entry(audio_frame, bd=5, textvariable=self.line_index)
        line_entry.place(relx=0.3, rely=0.5, height=25, width=50)

    def create_contacts_frame(self):
        contacts_frame = LabelFrame(self.master, text="Contact List")
        contacts_frame.place(relx=0.5, rely=0.0, height=500, width=500)
        # contacts_frame.grid(column=1, row=0, sticky='WENS')
        self.contacts_text = Text(contacts_frame)
        self.contacts_text.place(relx=0.01, rely=0.01, relheight=0.9, relwidth=0.98)
        # self.contacts_text.grid(column=0, row=0)

        entry_regex = Entry(contacts_frame, textvariable=self.regex_var)
        entry_regex.place(relx=0.01, rely=0.93, relheight=0.05, relwidth=0.98)
        entry_regex.bind("<Return>", self.search_contacts)


    def create_menu(self):
        # create a menu on main frame(root)
        menu = Menu(self.master)
        self.master.config(menu=menu)
        file = Menu(menu)
        file.add_command(label='Load file', command=self.openFile)
        file.add_command(label='Save file', command=self.savesFile)
        file.add_command(label='Exit', command=lambda: exit())
        menu.add_cascade(label='File', menu=file)
    # END Frames and Widgets

    # Helper function
    def openFile(self):
        currdir = os.getcwd()
        #initialdir="C:/Users/Batman/Documents/Programming/tkinter/"
        self.input_file = filedialog.askopenfilename(initialdir=currdir, filetypes=(("Text File", "*.txt"), ("All Files","*.*")), title="Choose a file.")
        self.audio_path = filedialog.askdirectory(initialdir=currdir, title='Select a directory')  #(parent=root,
        self.input_to_dict()

    def change_row(self):
        self.start_row = self.line_index.get()

    def run(self):
        self.trans_text.delete('1.0', END)
        self.correct_text.delete('1.0', END)
        self.contacts_text.delete('1.0', END)

        # start = self.line_index.get()
        for row in range(self.start_row, len(list(self.file_dict))):
            self.next_button.wait_variable(self.next_var)
            self.trans_text.delete('1.0', END)
            self.correct_text.delete('1.0', END)
            self.contacts_text.delete('1.0', END)

            self.current_row = row
            transcription = self.file_dict[row]['transcription']
            user = self.file_dict[row]['user']
            wave = self.file_dict[row]['codedWvnm']
            wave = wave.replace('.txt', '.decoded.wav')

            self.trans_text.insert(INSERT, transcription)

            # update contact list from user
            contacts_in_list = self.file_dict[row]['transcription.contact.id']
            if len(contacts_in_list) != 0:
                contacts_in_list = ast.literal_eval(contacts_in_list)
            self.contacts_in_list = contacts_in_list


            for i in self.contacts_in_list:
                self.correct_text.insert(INSERT, i+'\n')

            # print('user is ' + user)
            # print('audio is ' + wave)

            user_file_dir = Path(self.audio_path)
            self.audio_file = str(user_file_dir / user / wave)
            # print('audio path is '+str(self.audio_file))

            contact_file = user_file_dir / user / 'phone_dev_1.cop'
            # print(contact_file)

            try:
                with open(contact_file, 'r') as f:
                    file_complete = f.read()
                    pattern = re.compile(r'\"(.+?)\"')
                    matches = pattern.findall(file_complete)
                    # print(file_complete)
                    self.contacts_text.delete('1.0', END)
                    for i in matches:
                        self.contacts_text.insert(INSERT, i + '\n')

            except FileNotFoundError:
                print("User doesn't exit")

            self.contacts_full = self.contacts_text.get('1.0', END)

    def input_to_dict(self):
        with open(self.input_file, 'r') as rf:
            file_type = re.findall(r'.*(\..*)', self.input_file)
            if file_type == '.csv':
                file = csv.DictReader(rf, delimiter = ',', quotechar = '|')
            else:
                file = csv.DictReader(rf, delimiter = '\t', quotechar = '|')

                list_header = file.fieldnames
                row_index = 0
                for row in file:
                    self.file_dict[row_index] = {}
                    for header in list_header:
                        try:
                            self.file_dict[row_index][header] = row[header]
                        except KeyError:
                            pass
                    row_index += 1

    def saveLine(self):
        self.file_dict[self.current_row]['transcription'] = self.trans_text.get("1.0", 'end-1c')
        print('current row is ' + str(self.current_row))
        print('changed row content is ' + str(self.file_dict[self.current_row]))
    #
    # def saveFile(self):
    #     name = filedialog.asksaveasfile(mode='w', defaultextension=".txt")
    #     csvfilename = os.path.join(dirname, 'TSVFile.tsv')
    #     csv.writer(open("output.csv", "w"))
    #
    #     dict_writer = csv.DictWriter(output_file, keys, delimiter='\t')
    #
    #     name.write(json.dumps(self.file_dict))
    #     name.close

    def savesFile(self):
        save_file = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Select file", filetypes=(("all files", "*.*"), ("tsv files", "*.tsv"), ("csv files", "*.csv"), ("txt files", "*.txt")))

        with open(save_file, 'w', encoding='utf-8') as f:
            keys1_list = list(self.file_dict)
            keys2_list = list(self.file_dict[keys1_list[0]])

            for key_2 in keys2_list:
                if keys2_list.index(key_2) != len(keys2_list) - 1:
                    f.write(key_2 + '\t')
                else:
                    f.write(key_2)

            f.write('\n')

            index_item = 0
            for key_1 in keys1_list:
                for key_2 in self.file_dict[key_1]:
                    tmp_list = list(self.file_dict[key_1])
                    tmp_value = self.file_dict[key_1][key_2]

                    if key_2 == 'codedWvnm':
                        tmp_value = re.sub(r'\.decoded\.wav', r'.txt', tmp_value)

                    if tmp_list.index(key_2) != len(tmp_list) - 1:
                        f.write(tmp_value + '\t')
                    else:
                        f.write(tmp_value)

                f.write('\n')

                index_item += 1

    def search_contacts(self, event):
        # print(self.contacts_full)
        full_contact_list = self.contacts_full.split('\n')
        # print(full_contact_list)

        self.contacts_text.delete('1.0', END)
        pattern = re.compile(self.regex_var.get(), re.I)
        for contact in full_contact_list:
            if contact != '':
                match = pattern.findall(contact)
                if match:
                    self.contacts_text.insert(INSERT, contact + '\n')

    def play(self):
        winsound.PlaySound(self.audio_file, winsound.SND_FILENAME)

    # END Helper function

if __name__ == '__main__':
    root = Tk()
    root.title("Check Transcription Tool")
    root.geometry("1000x600")
    app = Window(root)
    root.mainloop()



