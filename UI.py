import customtkinter
from tkinter import messagebox, ttk
import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import csv
from tkinter import filedialog
import threading
import plyer as p
import webbrowser

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Scraper")
        self.geometry(f"{1400}x{750}")

        # Threeview custom style
        style = ttk.Style()
        aktualTheme = style.theme_use("default")
        style.theme_create("dummy", parent=aktualTheme)
        style.theme_use("dummy")
        style.configure("Treeview",
                        background="#2a2d2e",
                        foreground="white",
                        rowheight=45,
                        fieldbackground="#343638",
                        bordercolor="#343638",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat")
        style.map("Treeview.Heading",
                  background=[('active', '#3484F0')])

        # configure grid layout (4x4)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        conn = sqlite3.connect("scaper_data.db")
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS universities(
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  university_name text,
                  department text,
                  url text,
                  modal_tag text,
                  modal_class text,
                  name_tag text,
                  name_class text,
                  email_tag text,
                  email_class text
                  ) """
                  )

        c.execute("""CREATE TABLE IF NOT EXISTS professors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    university_page TEXT,
                    university TEXT,
                    department TEXT,
                    research_areas TEXT,
                    related_content TEXT,
                    email TEXT
                  ) """
                  )

        conn.commit()
        conn.close()

        self.sidebar_frame = customtkinter.CTkFrame(
            self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="University Scraper", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(
            self.sidebar_frame, text="Export Universities", command=lambda: self.export_treeview_to_csv(self.treeU))
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(
            self.sidebar_frame, text="Export Professors", command=lambda: self.export_treeview_to_csv(self.treeP))
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.log_text = customtkinter.CTkTextbox(
            self.sidebar_frame, state="disabled")
        self.log_text.grid(row=3, column=0, padx=20, pady=10)
        self.label_line1 = customtkinter.CTkLabel(
            self.sidebar_frame, text="Project By:")
        self.label_line1.grid(row=5, column=0, padx=20)
        self.label_line2 = customtkinter.CTkLabel(
            self.sidebar_frame, text="Mohammad Abaeiani", font=("Arial", 24))
        self.label_line2.grid(row=6, column=0, padx=20)
        self.label_line3 = customtkinter.CTkLabel(
            self.sidebar_frame, text="(MagusDev)")
        self.label_line3.grid(row=7, column=0, padx=20, pady=(0, 30))

        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")
        self.tabview.add("Professors")  # add tab at the end
        self.tabview.add("Universities")  # add tab at the
        # self.tabview.add("Email")

        ######################### professors tab ##########################

        columns = ('id', 'name', 'university page', 'university',
                   'department', "research_areas", "realted_content", 'email')
        self.treeP = ttk.Treeview(master=self.tabview.tab(
            "Professors"), columns=columns, show='headings', height=3)
        self.treeP.heading("id", text="ID")
        self.treeP.heading('name', text='Name')
        self.treeP.heading('university page', text='Page')
        self.treeP.heading('university', text='University')
        self.treeP.heading('department', text='Department')
        self.treeP.heading('research_areas', text='Research Areas')
        self.treeP.heading('realted_content', text='Realted Content')
        self.treeP.heading('email', text='email')
        self.treeP.pack(expand=True, padx=20, pady=20, fill="both")

        self.keyword_label = customtkinter.CTkLabel(self.tabview.tab(
            "Professors"), text="Keywords: (seperated by ; , and newline)", font=("Arial", 20))
        self.keyword_label.pack(padx=10, pady=(10, 3))

        self.textbox = customtkinter.CTkTextbox(
            master=self.tabview.tab("Professors"), height=100, corner_radius=0)
        self.textbox.pack(padx=20, pady=10, fill='x')

        self.prof_btn_frame = customtkinter.CTkFrame(
            self.tabview.tab("Professors"))
        self.prof_btn_frame.pack(padx=20, pady=(10, 5))

        self.scrape_btn = customtkinter.CTkButton(
            master=self.prof_btn_frame, text="Scrape", command=self.scrape_all_entries)
        self.scrape_btn.grid(row=0, column=0, padx=10, pady=10)

        self.delete_profs_btn = customtkinter.CTkButton(
            master=self.prof_btn_frame, text="Delete Selected", command=self.remove_prof_records)
        self.delete_profs_btn.grid(row=0, column=1, padx=10, pady=10)

        self.filter_profs_btn = customtkinter.CTkButton(
            master=self.prof_btn_frame, text="Filter", command=self.filter_data)
        self.filter_profs_btn.grid(row=0, column=2, padx=10, pady=10)

        ############################ universities tab ##################
        self.tabview.tab("Universities").rowconfigure((0, 1, 2), weight=1)
        self.tabview.tab("Universities").columnconfigure(0, weight=1)
        columns = ('id', "University", "Department", "URL", "Modal Tag",
                   "Modal Class", "Name Tag", "Name Class", "Email Tag", "Email Class")
        self.treeU = ttk.Treeview(master=self.tabview.tab(
            "Universities"), columns=columns, show='headings', height=3)

        # define headings
        self.treeU.heading("id", text="ID")
        self.treeU.heading("University", text="University")
        self.treeU.heading("Department", text="Department")
        self.treeU.heading("URL", text="URL")
        self.treeU.heading("Modal Tag", text="Modal Tag")
        self.treeU.heading("Modal Class", text="Modal Class")
        self.treeU.heading("Name Tag", text="Name Tag")
        self.treeU.heading("Name Class", text="Name Class")
        self.treeU.heading("Email Tag", text="Email Tag")
        self.treeU.heading("Email Class", text="Email Class")
        self.treeU.pack(expand=True, padx=10, pady=10, fill="both")

        self.selected_label = customtkinter.CTkLabel(self.tabview.tab(
            "Universities"), text="Selected Universities:", font=("Arial", 20))
        self.selected_label.pack(padx=10, pady=(10, 3))

        self.treeSel = ttk.Treeview(master=self.tabview.tab(
            "Universities"), columns=columns, show='headings', height=3)

        # define headings
        self.treeSel.heading("id", text="ID")
        self.treeSel.heading("University", text="University")
        self.treeSel.heading("Department", text="Department")
        self.treeSel.heading("URL", text="URL")
        self.treeSel.heading("Modal Tag", text="Modal Tag")
        self.treeSel.heading("Modal Class", text="Modal Class")
        self.treeSel.heading("Name Tag", text="Name Tag")
        self.treeSel.heading("Name Class", text="Name Class")
        self.treeSel.heading("Email Tag", text="Email Tag")
        self.treeSel.heading("Email Class", text="Email Class")
        self.treeSel.pack(expand=True, padx=10, pady=10, fill="both")

        self.uni_frame = customtkinter.CTkFrame(
            self.tabview.tab("Universities"))
        self.uni_frame.pack(padx=20, pady=(20, 0))

        # Create labels for the entries
        self.Uname_label = customtkinter.CTkLabel(self.uni_frame, text="Name:")
        self.Uname_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.dep_label = customtkinter.CTkLabel(
            self.uni_frame, text="Department:")
        self.dep_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.url_label = customtkinter.CTkLabel(self.uni_frame, text="URL:")
        self.url_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.modaltag_label = customtkinter.CTkLabel(
            self.uni_frame, text="Modal Tag:")
        self.modaltag_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.modalclass_label = customtkinter.CTkLabel(
            self.uni_frame, text="Modal Class:")
        self.modalclass_label.grid(
            row=4, column=0, padx=10, pady=10, sticky="e")
        self.nametag_label = customtkinter.CTkLabel(
            self.uni_frame, text="Name Tag:")
        self.nametag_label.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.nameclass_label = customtkinter.CTkLabel(
            self.uni_frame, text="Name Class:")
        self.nameclass_label.grid(
            row=1, column=2, padx=10, pady=10, sticky="e")
        self.emailtag_label = customtkinter.CTkLabel(
            self.uni_frame, text="Email Tag:")
        self.emailtag_label.grid(row=2, column=2, padx=10, pady=10, sticky="e")
        self.emailclass_label = customtkinter.CTkLabel(
            self.uni_frame, text="Email Class:")
        self.emailclass_label.grid(
            row=3, column=2, padx=10, pady=10, sticky="e")

        # Create the entry widgets
        self.Uname_inp = customtkinter.CTkEntry(master=self.uni_frame)
        self.Uname_inp.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.dep_inp = customtkinter.CTkEntry(master=self.uni_frame)
        self.dep_inp.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.url_inp = customtkinter.CTkEntry(master=self.uni_frame)
        self.url_inp.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        self.modaltag_inp = customtkinter.CTkEntry(master=self.uni_frame)
        self.modaltag_inp.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        self.modalclass_inp = customtkinter.CTkEntry(master=self.uni_frame)
        self.modalclass_inp.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        self.nametag_inp = customtkinter.CTkEntry(master=self.uni_frame)
        self.nametag_inp.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        self.nameclass_inp = customtkinter.CTkEntry(master=self.uni_frame)
        self.nameclass_inp.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        self.emailtag_inp = customtkinter.CTkEntry(master=self.uni_frame)
        self.emailtag_inp.grid(row=2, column=3, padx=10, pady=10, sticky="w")
        self.emailclass_inp = customtkinter.CTkEntry(master=self.uni_frame)
        self.emailclass_inp.grid(row=3, column=3, padx=10, pady=10, sticky="w")

        self.clear_btn = customtkinter.CTkButton(
            master=self.uni_frame, text="Clear Inputs", command=self.clear_boxes)
        self.clear_btn.grid(row=4, column=2, columnspan=2,  padx=10, pady=10)

        self.uni_btn_frame = customtkinter.CTkFrame(
            self.tabview.tab("Universities"))
        self.uni_btn_frame.pack(padx=20, pady=20,)

        # submit button
        self.submit_uni_btn = customtkinter.CTkButton(
            master=self.uni_btn_frame, text="Add New University", command=self.submit_university_record)
        self.submit_uni_btn.grid(row=0, column=0, padx=10, pady=10)

        self.delete_uni_btn = customtkinter.CTkButton(
            master=self.uni_btn_frame, text="Delete Entries", command=self.remove_university_record)
        self.delete_uni_btn.grid(row=0, column=1,  padx=10, pady=10)

        self.update_uni_btn = customtkinter.CTkButton(
            master=self.uni_btn_frame, text="Update University", command=self.update_record)
        self.update_uni_btn.grid(row=0, column=3,  padx=10, pady=10)

        self.select_btn = customtkinter.CTkButton(
            master=self.uni_btn_frame, text="Add to Selection", command=self.copy_selected_items)
        self.select_btn.grid(row=0, column=5,  padx=10, pady=10)

        self.clear_btn = customtkinter.CTkButton(
            master=self.uni_btn_frame, text="Remove from Selection", command=self.remove_from_selection)
        self.clear_btn.grid(row=0, column=6,  padx=10, pady=10)

        self.treeU.bind("<<TreeviewSelect>>", self.select_record)

        ######################################################## E mail tab############################

        # self.email_text = customtkinter.CTkTextbox(
        #     self.tabview.tab("Email"), width=400, height=300)
        # self.email_text.pack(padx=10, pady=20)

        # self.entries_frame = customtkinter.CTkFrame(self.tabview.tab("Email"))
        # self.entries_frame.pack()

        # prof_frame = customtkinter.CTkFrame(self.entries_frame)
        # prof_frame.grid(row=0, column=0, padx=10, pady=5)

        # # Create entries to display the professor's credentials
        # self.name_label = customtkinter.CTkLabel(prof_frame, text="Name:")
        # self.name_entry = customtkinter.CTkEntry(prof_frame)
        # self.name_label.grid(row=0, column=0, padx=10, pady=5)
        # self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        # self.university_label = customtkinter.CTkLabel(
        #     prof_frame, text="University:")
        # self.university_entry = customtkinter.CTkEntry(prof_frame)
        # self.university_label.grid(row=1, column=0, padx=10, pady=5)
        # self.university_entry.grid(row=1, column=1, padx=10, pady=5)

        # self.department_label = customtkinter.CTkLabel(
        #     prof_frame, text="Department:")
        # self.department_entry = customtkinter.CTkEntry(prof_frame)
        # self.department_label.grid(row=2, column=0, padx=10, pady=5)
        # self.department_entry.grid(row=2, column=1, padx=10, pady=5)

        # self.keywords_label = customtkinter.CTkLabel(
        #     prof_frame, text="Keywords:")
        # self.keywords_entry = customtkinter.CTkEntry(prof_frame)
        # self.keywords_label.grid(row=3, column=0, padx=10, pady=5)
        # self.keywords_entry.grid(row=3, column=1, padx=10, pady=5)

        # self.link_label = customtkinter.CTkLabel(
        #     prof_frame, text="Page link")
        # self.link_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)
        # self.link_label.bind("<Button-1>", lambda e: self.open_url())

        # # Create a multiline textbox for the related content
        # self.content_text = customtkinter.CTkTextbox(
        #     self.entries_frame)
        # self.content_text.grid(row=0, column=1, padx=10, pady=10)

        # # Bind the treeP selection event to update the fields
        # self.treeP.bind("<<TreeviewSelect>>", self.update_fields)

    def submit_university_record(self):

        conn = sqlite3.connect("scaper_data.db")
        c = conn.cursor()

        c.execute("""INSERT INTO universities (university_name, department, url, modal_tag, modal_class, name_tag, name_class, email_tag, email_class)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (self.Uname_inp.get(), self.dep_inp.get(), self.url_inp.get(),
                   self.modaltag_inp.get(), self.modalclass_inp.get(), self.nametag_inp.get(),
                   self.nameclass_inp.get(), self.emailtag_inp.get(), self.emailclass_inp.get()))

        conn.commit()
        conn.close()

        self.clear_boxes()
        self.query_universities()
        print("stest")

    def clear_boxes(self):
        # clear textboxes
        self.Uname_inp.delete(0, customtkinter.END)
        self.dep_inp.delete(0, customtkinter.END)
        self.url_inp.delete(0, customtkinter.END)
        self.modaltag_inp.delete(0, customtkinter.END)
        self.modalclass_inp.delete(0, customtkinter.END)
        self.nametag_inp.delete(0, customtkinter.END)
        self.nameclass_inp.delete(0, customtkinter.END)
        self.emailtag_inp.delete(0, customtkinter.END)
        self.emailclass_inp.delete(0, customtkinter.END)

    def query_universities(self):
        conn = sqlite3.connect("scaper_data.db")
        c = conn.cursor()

        c.execute("SELECT * FROM universities")
        universities_data = c.fetchall()
        self.treeU.delete(*self.treeU.get_children())
        for record in universities_data:
            self.treeU.insert(parent='', index='end', values=(
                record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9]))
        conn.commit()
        conn.close()

    def query_professors(self):
        conn = sqlite3.connect("scaper_data.db")
        c = conn.cursor()

        c.execute("SELECT * FROM professors")
        profs_data = c.fetchall()
        self.treeP.delete(*self.treeP.get_children())
        for record in profs_data:
            self.treeP.insert(parent='', index='end', values=(
                record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7]))
        conn.commit()
        conn.close()

    def sidebar_button_event(self):
        print("sidebar_button click")

    def remove_university_record(self):
        selected_items = self.treeU.selection()
        for item in selected_items:
            id = self.treeU.item(item, 'values')[0]
            self.treeU.delete(item)
            conn = sqlite3.connect("scaper_data.db")
            c = conn.cursor()
            c.execute("DELETE FROM universities WHERE id=?", (id,))
            conn.commit()
            conn.close()
        self.query_universities()

    def remove_prof_records(self):
        selected_items = self.treeP.selection()
        conn = sqlite3.connect("scaper_data.db")
        c = conn.cursor()
        for item in selected_items:
            id = self.treeP.item(item, 'values')[0]
            self.treeP.delete(item)
            c.execute("DELETE FROM professors WHERE id=?", (id,))
        conn.commit()

        c.execute("SELECT COUNT(*) FROM professors")
        count = c.fetchone()[0]
        if count == 0:
            # Reset indexing
            c.execute("delete from sqlite_sequence where name='professors';")
        conn.commit()
        conn.close()
        self.query_professors

    def select_record(self, e):
        self.clear_boxes()
        selected = self.treeU.focus()
        values = self.treeU.item(selected, 'values')

        self.Uname_inp.insert(0, values[1])
        self.dep_inp.insert(0, values[2])
        self.url_inp.insert(0, values[3])
        self.modaltag_inp.insert(0, values[4])
        self.modalclass_inp.insert(0, values[5])
        self.nametag_inp.insert(0, values[6])
        self.nameclass_inp.insert(0, values[7])
        self.emailtag_inp.insert(0, values[8])
        self.emailclass_inp.insert(0, values[9])

    def update_record(self):
        selected = self.treeU.focus()
        id = self.treeU.item(selected, 'values')[0]
        print(id)
        # self.treeU.item(selected, text="", values=(self.Uname_inp.get(), self.dep_inp.get(), self.url_inp.get(), self.modaltag_inp.get(), self.modaltag_inp.get(), self.nametag_inp.get(), self.nameclass_inp.get(),self.emailtag_inp.get(), self.emailclass_inp.get()))

        conn = sqlite3.connect("scaper_data.db")
        c = conn.cursor()

        c.execute("""UPDATE universities SET university_name=?, department=?, url=?, modal_tag=?, modal_class=?, name_tag=?, name_class=?, email_tag=?, email_class=?
              WHERE id=?""",
                  (self.Uname_inp.get(), self.dep_inp.get(), self.url_inp.get(),
                   self.modaltag_inp.get(), self.modalclass_inp.get(), self.nametag_inp.get(),
                   self.nameclass_inp.get(), self.emailtag_inp.get(), self.emailclass_inp.get(),
                   id))  # Replace 'selected' with the appropriate primary key value

        conn.commit()
        conn.close()
        self.clear_boxes()
        self.query_universities()

    def copy_selected_items(self):
        selected_items = self.treeU.selection()
        for item in selected_items:
            values = self.treeU.item(item, 'values')
            self.treeSel.insert('', 'end', values=values)

    def remove_from_selection(self):
        selected_items = self.treeSel.selection()
        for item in selected_items:
            self.treeSel.delete(item)

    def scrape_all_entries(self):
        search_keywords = self.get_keywords()
        self.log_event("keywords: " + ", ".join(search_keywords))
        if not search_keywords:
            messagebox.showwarning("Warning", "Keywords list is empty.")
            return
        if not self.treeSel.get_children():
            messagebox.showwarning("Warning", "No university selected.")
            return

        for item_id in self.treeSel.get_children():
            item_values = self.treeSel.item(item_id, 'values')
            try:
                search_dict = {
                    "University": item_values[1] or None,
                    "Department": item_values[2] or None,
                    "url": item_values[3] or None,
                    "modal": {
                        "tag": item_values[4] or None,
                        "class": item_values[5] or None
                    },
                    "name": {
                        "tag": item_values[6] or None,
                        "class": item_values[7] or None
                    },
                    "email": {
                        "tag": item_values[8] or None,
                        "class": item_values[9] or None
                    }
                }

                self.log_event("Started scraping university" +
                               item_values[1] + " " + item_values[2])

                t1 = threading.Thread(target=self.scrape, args=(
                    search_keywords, search_dict))
                t1.start()
            except Exception as e:
                choice = messagebox.askquestion("Error", str(
                    e) + "\n\nDo you want to skip this university and continue?")
                if choice == "no":
                    return

    def extract_matches(self, url, keywords, search_dict):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        foundKeywords = ""
        foundContent = ""
        page_content = soup.get_text(strip=True)
        for keyword in keywords:
            if re.search(r'\b{}\b'.format(keyword), page_content, re.IGNORECASE):
                foundKeywords += keyword + ", "
                paragraphs = soup.find_all(
                    string=re.compile(r'\b{}\b'.format(keyword), re.IGNORECASE))
                related_content = ""
                for paragraph in paragraphs:
                    # print("Related Content:")
                    paragraph_text = paragraph.get_text(strip=True)
                    # print(paragraph_text)
                    if paragraph_text.lower() not in foundContent:
                        related_content += paragraph_text + '\n'
                foundContent += related_content

        if foundKeywords != "":
            name = soup.find(
                search_dict["name"]["tag"], class_=search_dict["name"]["class"]).get_text(strip=True)
            print("Name:", name)
            print("University Page: ", url)
            print("Keywords: ", foundKeywords)
            print("Related content: ", foundContent)
            email = soup.find(search_dict["email"]["tag"], class_=search_dict["email"]
                              ["class"], string=re.compile(r'[\w\.-]+@[\w\.-]+'))
            if email is not None:
                email = email.get_text(strip=True)
            print("Email: ", email)
            self.add_prof_to_database(
                name, url, search_dict["University"], search_dict["Department"], foundKeywords, foundContent, email)
            print()


# string=re.compile(r'[\w\.-]+@[\w\.-]+')


    def scrape(self, keywords, search_dict):
        url = search_dict["url"]
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        for div in soup.find_all(search_dict["modal"]["tag"], class_=search_dict["modal"]["class"]):
            link = div.find('a', href=True)
            if link is not None:
                self.extract_matches(
                    urljoin(url, link['href']), keywords, search_dict)

        self.log_event("Finished scraping" +
                       search_dict["University"] + " " + search_dict["Department"])

    def get_keywords(self):
        text = self.textbox.get("1.0", "end")
        result = [item.strip()
                  for item in re.split(r',|;|\n', text) if item != '']
        return result

    def add_prof_to_database(self, name, url, university, department, keywords, content, email):
        conn = sqlite3.connect("scaper_data.db")
        c = conn.cursor()
        c.execute("""INSERT INTO professors (name, university_page, university, department, research_areas, related_content, email)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (name, url, university, department, keywords, content, email))

        prof_id = c.lastrowid
        conn.commit()
        conn.close()
        self.treeP.insert(parent='', index='end', values=(
            prof_id, name, url, university, department, keywords, content, email))

    def export_treeview_to_csv(self, treeview):

        file_path = filedialog.asksaveasfilename(defaultextension='.csv')
        if file_path:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                headers = [treeview.heading(column)['text']
                           for column in treeview['columns']]
                writer.writerow(headers)
                for item_id in treeview.get_children():
                    row = [treeview.item(item_id)['values'][column]
                           for column in range(len(headers))]
                    writer.writerow(row)

    def notify(self, msg):
        p.notification.notify(
            title="Desktop Notifier App",
            message=msg,
            app_name="Desktop Notifier",
            app_icon=None,
            timeout=3
        )

    def log_event(self, event):
        self.log_text.configure(state="normal")
        self.log_text.insert(customtkinter.END, event + "\n")
        self.log_text.configure(state="disabled")

    def filter_data(self):
        conn = sqlite3.connect("scaper_data.db")
        c = conn.cursor()

        c.execute("SELECT * FROM professors WHERE related_content LIKE '%research%' COLLATE NOCASE OR related_content LIKE '%lab%' COLLATE NOCASE")
        filtered_data = c.fetchall()

        conn.close()

        if filtered_data:
            self.treeP.delete(*self.treeP.get_children())
            for record in filtered_data:
                self.treeP.insert(parent='', index='end', values=(
                    record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7]))
        else:
            self.query_professors()

    def update_fields(self, event):
        selected_item = self.treeP.focus()
        values = self.treeP.item(selected_item)['values']
        # Update the entries with the selected professor's credentials
        self.name_entry.delete(0, customtkinter.END)
        self.name_entry.insert(0, values[1])

        self.university_entry.delete(0, customtkinter.END)
        self.university_entry.insert(0, values[3])

        self.department_entry.delete(0, customtkinter.END)
        self.department_entry.insert(0, values[4])

        self.keywords_entry.delete(0, customtkinter.END)
        self.keywords_entry.insert(0, values[5])

        self.content_text.delete("1.0", customtkinter.END)
        self.content_text.insert(customtkinter.END, values[6])
        self.fill_text()

    def open_url(self):
        selected_item = self.treeP.focus()
        url = self.treeP.item(selected_item)['values'][2]
        webbrowser.open(url)

    def fill_text(self):
        professor_name = self.name_entry.get()
        university_name = self.university_entry.get()

        text = f"Dear Prof. {professor_name},\n\nI'm Mohammad Abaeiani, a senior BSc. student majoring in Electrical Engineering(Electronics) with a minor in Computer Engineering from the University of Tehran, with a CGPA of 3.76 (17.57/20) and a TOEFL score of 101. I am interested in your research field, and I plan to apply for the {university_name} Phd program.\n\nI have a strong interest and experience in various fields, including computer graphics, computer vision, Human-Computer Interaction (HCI), Deep learning and social studies. I've worked as a microcontroller interface designer and participated in several game development projects, which have helped me gain a solid understanding of computer graphics principles. Furthermore, my bachelor's research project is focused on the Emo Galaxy game, where I utilized emotion recognition for gameplay advancement. This involved incorporating neural network models for emotion recognition and face tracking.\n\nI was wondering if there is a graduate position available for me to pursue my education under your supervision. Should you require additional information, do not hesitate to contact me. I've attached copies of my CV, Transcript, and TOEFL score sheet for your reference.\n\nI appreciate your time and look forward to hearing back from you.\n\nSincerely,\n\nMohammad"

        # Clear previous content
        self.email_text.delete(1.0, customtkinter.END)
        self.email_text.insert(customtkinter.END, text)


if __name__ == "__main__":
    app = App()
    app.query_universities()
    app.query_professors()
    app.mainloop()
