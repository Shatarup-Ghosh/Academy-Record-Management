import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import csv
import os
from tkinter import filedialog

class AcademyManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Academy Management System")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f0f2f5")
        
        # Create database connection
        self.conn = sqlite3.connect('academy.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create frames for each section
        self.dashboard_frame = self.create_dashboard_frame()
        self.students_frame = self.create_students_frame()
        self.courses_frame = self.create_courses_frame()
        self.enrollments_frame = self.create_enrollments_frame()
        self.grades_frame = self.create_grades_frame()
        
        # Add frames to notebook
        self.notebook.add(self.dashboard_frame, text='Dashboard')
        self.notebook.add(self.students_frame, text='Students')
        self.notebook.add(self.courses_frame, text='Courses')
        self.notebook.add(self.enrollments_frame, text='Enrollments')
        self.notebook.add(self.grades_frame, text='Grades')
        
        # Initialize data
        self.load_students()
        self.load_courses()
        self.load_enrollments()
        self.update_dashboard()
        
    def create_tables(self):
        # Create students table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                dob TEXT,
                address TEXT,
                enrollment_date TEXT DEFAULT CURRENT_DATE
            )
        ''')
        
        # Create courses table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                department TEXT,
                credits INTEGER DEFAULT 3,
                instructor TEXT,
                schedule TEXT,
                room TEXT
            )
        ''')
        
        # Create enrollments table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enrollment_date TEXT DEFAULT CURRENT_DATE,
                FOREIGN KEY (student_id) REFERENCES students (id),
                FOREIGN KEY (course_id) REFERENCES courses (id)
            )
        ''')
        
        # Create grades table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enrollment_id INTEGER NOT NULL,
                grade REAL,
                grade_date TEXT,
                FOREIGN KEY (enrollment_id) REFERENCES enrollments (id)
            )
        ''')
        
        self.conn.commit()
    
    # Dashboard Frame
    def create_dashboard_frame(self):
        frame = tk.Frame(self.root, bg="#f0f2f5")
        
        # Header
        header = tk.Label(frame, text="Academy Dashboard", font=("Arial", 24, "bold"), bg="#f0f2f5", fg="#2c3e50")
        header.pack(pady=20)
        
        # Stats frame
        stats_frame = tk.Frame(frame, bg="#f0f2f5")
        stats_frame.pack(pady=20, padx=20, fill='x')
        
        # Stats cards
        self.student_count_label = self.create_stat_card(stats_frame, "Total Students", "0", "#3498db")
        self.course_count_label = self.create_stat_card(stats_frame, "Available Courses", "0", "#2ecc71")
        self.enrollment_count_label = self.create_stat_card(stats_frame, "Active Enrollments", "0", "#e74c3c")
        
        # Recent activity frame
        activity_frame = tk.LabelFrame(frame, text="Recent Activity", font=("Arial", 12, "bold"), 
                                      bg="#f0f2f5", fg="#2c3e50", padx=15, pady=10)
        activity_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        # Activity listbox
        self.activity_listbox = tk.Listbox(activity_frame, height=8, font=("Arial", 10), 
                                         bg="white", fg="#333333", bd=0, highlightthickness=0)
        self.activity_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add sample activities
        self.activity_listbox.insert(tk.END, "System initialized successfully")
        self.activity_listbox.insert(tk.END, "Welcome to Academy Management System")
        
        return frame
    
    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg="white", bd=1, relief=tk.RAISED, padx=20, pady=15)
        card.pack(side=tk.LEFT, padx=10, ipadx=20, ipady=10)
        
        title_label = tk.Label(card, text=title, font=("Arial", 12), bg="white", fg="#7f8c8d")
        title_label.pack(anchor='w')
        
        value_label = tk.Label(card, text=value, font=("Arial", 24, "bold"), bg="white", fg=color)
        value_label.pack(anchor='w', pady=5)
        
        return value_label
    
    # Students Frame
    def create_students_frame(self):
        frame = tk.Frame(self.root, bg="#f0f2f5")
        
        # Header
        header = tk.Label(frame, text="Student Management", font=("Arial", 18, "bold"), bg="#f0f2f5", fg="#2c3e50")
        header.pack(pady=10)
        
        # Search and buttons frame
        search_frame = tk.Frame(frame, bg="#f0f2f5")
        search_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(search_frame, text="Search:", bg="#f0f2f5", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.student_search_entry = tk.Entry(search_frame, width=30, font=("Arial", 10))
        self.student_search_entry.pack(side=tk.LEFT, padx=5)
        self.student_search_entry.bind("<KeyRelease>", self.search_students)
        
        tk.Button(search_frame, text="Add Student", bg="#3498db", fg="white", font=("Arial", 10, "bold"), 
                 command=self.add_student).pack(side=tk.RIGHT, padx=5)
        tk.Button(search_frame, text="Export CSV", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), 
                 command=self.export_students_csv).pack(side=tk.RIGHT, padx=5)
        
        # Treeview for students
        columns = ("ID", "First Name", "Last Name", "Email", "Phone", "Enrollment Date")
        self.students_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.students_tree.heading(col, text=col)
            self.students_tree.column(col, width=120, anchor=tk.W)
        
        self.students_tree.column("ID", width=50)
        self.students_tree.column("Email", width=180)
        self.students_tree.column("Enrollment Date", width=120)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.students_tree.yview)
        self.students_tree.configure(yscrollcommand=scrollbar.set)
        
        self.students_tree.pack(fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        # Context menu for students
        self.student_menu = tk.Menu(self.root, tearoff=0)
        self.student_menu.add_command(label="View Details", command=self.view_student_details)
        self.student_menu.add_command(label="Edit Student", command=self.edit_student)
        self.student_menu.add_command(label="Delete Student", command=self.delete_student)
        self.students_tree.bind("<Button-3>", self.show_student_context_menu)
        
        return frame
    
    # Courses Frame
    def create_courses_frame(self):
        frame = tk.Frame(self.root, bg="#f0f2f5")
        
        # Header
        header = tk.Label(frame, text="Course Management", font=("Arial", 18, "bold"), bg="#f0f2f5", fg="#2c3e50")
        header.pack(pady=10)
        
        # Search and buttons frame
        search_frame = tk.Frame(frame, bg="#f0f2f5")
        search_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(search_frame, text="Search:", bg="#f0f2f5", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.course_search_entry = tk.Entry(search_frame, width=30, font=("Arial", 10))
        self.course_search_entry.pack(side=tk.LEFT, padx=5)
        self.course_search_entry.bind("<KeyRelease>", self.search_courses)
        
        tk.Button(search_frame, text="Add Course", bg="#3498db", fg="white", font=("Arial", 10, "bold"), 
                 command=self.add_course).pack(side=tk.RIGHT, padx=5)
        tk.Button(search_frame, text="Export CSV", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), 
                 command=self.export_courses_csv).pack(side=tk.RIGHT, padx=5)
        
        # Treeview for courses
        columns = ("ID", "Code", "Name", "Department", "Credits", "Instructor")
        self.courses_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.courses_tree.heading(col, text=col)
            self.courses_tree.column(col, width=120, anchor=tk.W)
        
        self.courses_tree.column("ID", width=50)
        self.courses_tree.column("Code", width=80)
        self.courses_tree.column("Credits", width=70)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.courses_tree.yview)
        self.courses_tree.configure(yscrollcommand=scrollbar.set)
        
        self.courses_tree.pack(fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        # Context menu for courses
        self.course_menu = tk.Menu(self.root, tearoff=0)
        self.course_menu.add_command(label="View Details", command=self.view_course_details)
        self.course_menu.add_command(label="Edit Course", command=self.edit_course)
        self.course_menu.add_command(label="Delete Course", command=self.delete_course)
        self.courses_tree.bind("<Button-3>", self.show_course_context_menu)
        
        return frame
    
    # Enrollments Frame
    def create_enrollments_frame(self):
        frame = tk.Frame(self.root, bg="#f0f2f5")
        
        # Header
        header = tk.Label(frame, text="Enrollment Management", font=("Arial", 18, "bold"), bg="#f0f2f5", fg="#2c3e50")
        header.pack(pady=10)
        
        # Controls frame
        controls_frame = tk.Frame(frame, bg="#f0f2f5")
        controls_frame.pack(fill='x', padx=20, pady=10)
        
        # Student selection
        tk.Label(controls_frame, text="Student:", bg="#f0f2f5").pack(side=tk.LEFT)
        self.enrollment_student_var = tk.StringVar()
        self.student_combobox = ttk.Combobox(controls_frame, textvariable=self.enrollment_student_var, width=30)
        self.student_combobox.pack(side=tk.LEFT, padx=5)
        
        # Course selection
        tk.Label(controls_frame, text="Course:", bg="#f0f2f5").pack(side=tk.LEFT, padx=(20, 0))
        self.enrollment_course_var = tk.StringVar()
        self.course_combobox = ttk.Combobox(controls_frame, textvariable=self.enrollment_course_var, width=30)
        self.course_combobox.pack(side=tk.LEFT, padx=5)
        
        # Enroll button
        tk.Button(controls_frame, text="Enroll Student", bg="#3498db", fg="white", 
                 command=self.enroll_student).pack(side=tk.RIGHT, padx=5)
        
        # Treeview for enrollments
        columns = ("ID", "Student", "Course", "Department", "Enrollment Date")
        self.enrollments_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.enrollments_tree.heading(col, text=col)
            self.enrollments_tree.column(col, width=120, anchor=tk.W)
        
        self.enrollments_tree.column("ID", width=50)
        self.enrollments_tree.column("Student", width=180)
        self.enrollments_tree.column("Course", width=180)
        self.enrollments_tree.column("Enrollment Date", width=120)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.enrollments_tree.yview)
        self.enrollments_tree.configure(yscrollcommand=scrollbar.set)
        
        self.enrollments_tree.pack(fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        # Context menu for enrollments
        self.enrollment_menu = tk.Menu(self.root, tearoff=0)
        self.enrollment_menu.add_command(label="Assign Grade", command=self.assign_grade)
        self.enrollment_menu.add_command(label="View Grades", command=self.view_grades)
        self.enrollment_menu.add_command(label="Unenroll", command=self.unenroll_student)
        self.enrollments_tree.bind("<Button-3>", self.show_enrollment_context_menu)
        
        return frame
    
    # Grades Frame
    def create_grades_frame(self):
        frame = tk.Frame(self.root, bg="#f0f2f5")
        
        # Header
        header = tk.Label(frame, text="Grade Management", font=("Arial", 18, "bold"), bg="#f0f2f5", fg="#2c3e50")
        header.pack(pady=10)
        
        # Filter frame
        filter_frame = tk.Frame(frame, bg="#f0f2f5")
        filter_frame.pack(fill='x', padx=20, pady=10)
        
        # Course filter
        tk.Label(filter_frame, text="Filter by Course:", bg="#f0f2f5").pack(side=tk.LEFT)
        self.grade_course_var = tk.StringVar()
        self.grade_course_combobox = ttk.Combobox(filter_frame, textvariable=self.grade_course_var, width=30)
        self.grade_course_combobox.pack(side=tk.LEFT, padx=5)
        self.grade_course_combobox.bind("<<ComboboxSelected>>", self.filter_grades)
        
        # Student filter
        tk.Label(filter_frame, text="Filter by Student:", bg="#f0f2f5").pack(side=tk.LEFT, padx=(20, 0))
        self.grade_student_var = tk.StringVar()
        self.grade_student_combobox = ttk.Combobox(filter_frame, textvariable=self.grade_student_var, width=30)
        self.grade_student_combobox.pack(side=tk.LEFT, padx=5)
        self.grade_student_combobox.bind("<<ComboboxSelected>>", self.filter_grades)
        
        # Treeview for grades
        columns = ("ID", "Student", "Course", "Grade", "Date")
        self.grades_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.grades_tree.heading(col, text=col)
            self.grades_tree.column(col, width=120, anchor=tk.W)
        
        self.grades_tree.column("ID", width=50)
        self.grades_tree.column("Student", width=180)
        self.grades_tree.column("Course", width=180)
        self.grades_tree.column("Grade", width=80)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.grades_tree.yview)
        self.grades_tree.configure(yscrollcommand=scrollbar.set)
        
        self.grades_tree.pack(fill='both', expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        return frame
    
    # Data loading methods
    def load_students(self):
        # Clear the treeview
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        # Fetch students from database
        self.cursor.execute("SELECT id, first_name, last_name, email, phone, enrollment_date FROM students")
        students = self.cursor.fetchall()
        
        # Insert into treeview
        for student in students:
            self.students_tree.insert("", tk.END, values=student)
            
        # Update comboboxes
        self.update_student_comboboxes()
        
    def load_courses(self):
        # Clear the treeview
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)
        
        # Fetch courses from database
        self.cursor.execute("SELECT id, code, name, department, credits, instructor FROM courses")
        courses = self.cursor.fetchall()
        
        # Insert into treeview
        for course in courses:
            self.courses_tree.insert("", tk.END, values=course)
            
        # Update comboboxes
        self.update_course_comboboxes()
        
    def load_enrollments(self):
        # Clear the treeview
        for item in self.enrollments_tree.get_children():
            self.enrollments_tree.delete(item)
        
        # Fetch enrollments from database
        self.cursor.execute('''
            SELECT e.id, s.first_name || ' ' || s.last_name, c.name, c.department, e.enrollment_date
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            JOIN courses c ON e.course_id = c.id
        ''')
        enrollments = self.cursor.fetchall()
        
        # Insert into treeview
        for enrollment in enrollments:
            self.enrollments_tree.insert("", tk.END, values=enrollment)
            
        # Load grades
        self.load_grades()
        
    def load_grades(self):
        # Clear the treeview
        for item in self.grades_tree.get_children():
            self.grades_tree.delete(item)
        
        # Fetch grades from database
        self.cursor.execute('''
            SELECT g.id, s.first_name || ' ' || s.last_name, c.name, g.grade, g.grade_date
            FROM grades g
            JOIN enrollments e ON g.enrollment_id = e.id
            JOIN students s ON e.student_id = s.id
            JOIN courses c ON e.course_id = c.id
        ''')
        grades = self.cursor.fetchall()
        
        # Insert into treeview
        for grade in grades:
            self.grades_tree.insert("", tk.END, values=grade)
        
    def update_student_comboboxes(self):
        self.cursor.execute("SELECT id, first_name || ' ' || last_name FROM students")
        students = self.cursor.fetchall()
        student_dict = {name: id for id, name in students}
        
        self.student_combobox['values'] = [name for id, name in students]
        self.grade_student_combobox['values'] = [name for id, name in students]
        
    def update_course_comboboxes(self):
        self.cursor.execute("SELECT id, name FROM courses")
        courses = self.cursor.fetchall()
        course_dict = {name: id for id, name in courses}
        
        self.course_combobox['values'] = [name for id, name in courses]
        self.grade_course_combobox['values'] = [name for id, name in courses]
        
    def update_dashboard(self):
        # Update student count
        self.cursor.execute("SELECT COUNT(*) FROM students")
        student_count = self.cursor.fetchone()[0]
        self.student_count_label.config(text=str(student_count))
        
        # Update course count
        self.cursor.execute("SELECT COUNT(*) FROM courses")
        course_count = self.cursor.fetchone()[0]
        self.course_count_label.config(text=str(course_count))
        
        # Update enrollment count
        self.cursor.execute("SELECT COUNT(*) FROM enrollments")
        enrollment_count = self.cursor.fetchone()[0]
        self.enrollment_count_label.config(text=str(enrollment_count))
    
    # Student management methods
    def add_student(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Student")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="First Name:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        first_name_entry = tk.Entry(dialog, width=30)
        first_name_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Last Name:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        last_name_entry = tk.Entry(dialog, width=30)
        last_name_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Email:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        email_entry = tk.Entry(dialog, width=30)
        email_entry.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Phone:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        phone_entry = tk.Entry(dialog, width=30)
        phone_entry.grid(row=3, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Date of Birth (YYYY-MM-DD):").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        dob_entry = tk.Entry(dialog, width=30)
        dob_entry.grid(row=4, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Address:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
        address_entry = tk.Entry(dialog, width=30)
        address_entry.grid(row=5, column=1, padx=10, pady=5)
        
        def save_student():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            email = email_entry.get()
            phone = phone_entry.get()
            dob = dob_entry.get()
            address = address_entry.get()
            
            if not first_name or not last_name or not email:
                messagebox.showerror("Error", "First name, last name, and email are required!")
                return
            
            try:
                self.cursor.execute('''
                    INSERT INTO students (first_name, last_name, email, phone, dob, address)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (first_name, last_name, email, phone, dob, address))
                self.conn.commit()
                self.load_students()
                self.update_dashboard()
                dialog.destroy()
                self.log_activity(f"Added student: {first_name} {last_name}")
                messagebox.showinfo("Success", "Student added successfully!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Email must be unique!")
        
        tk.Button(dialog, text="Save", width=10, command=save_student).grid(row=6, column=1, pady=20, sticky='e')
    
    def edit_student(self):
        selected_item = self.students_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a student to edit")
            return
            
        student_id = self.students_tree.item(selected_item)['values'][0]
        
        # Fetch student details
        self.cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
        student = self.cursor.fetchone()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Student")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="First Name:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        first_name_entry = tk.Entry(dialog, width=30)
        first_name_entry.grid(row=0, column=1, padx=10, pady=5)
        first_name_entry.insert(0, student[1])
        
        tk.Label(dialog, text="Last Name:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        last_name_entry = tk.Entry(dialog, width=30)
        last_name_entry.grid(row=1, column=1, padx=10, pady=5)
        last_name_entry.insert(0, student[2])
        
        tk.Label(dialog, text="Email:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        email_entry = tk.Entry(dialog, width=30)
        email_entry.grid(row=2, column=1, padx=10, pady=5)
        email_entry.insert(0, student[3])
        
        tk.Label(dialog, text="Phone:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        phone_entry = tk.Entry(dialog, width=30)
        phone_entry.grid(row=3, column=1, padx=10, pady=5)
        phone_entry.insert(0, student[4])
        
        tk.Label(dialog, text="Date of Birth (YYYY-MM-DD):").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        dob_entry = tk.Entry(dialog, width=30)
        dob_entry.grid(row=4, column=1, padx=10, pady=5)
        dob_entry.insert(0, student[5])
        
        tk.Label(dialog, text="Address:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
        address_entry = tk.Entry(dialog, width=30)
        address_entry.grid(row=5, column=1, padx=10, pady=5)
        address_entry.insert(0, student[6])
        
        def save_changes():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            email = email_entry.get()
            phone = phone_entry.get()
            dob = dob_entry.get()
            address = address_entry.get()
            
            if not first_name or not last_name or not email:
                messagebox.showerror("Error", "First name, last name, and email are required!")
                return
            
            try:
                self.cursor.execute('''
                    UPDATE students 
                    SET first_name=?, last_name=?, email=?, phone=?, dob=?, address=?
                    WHERE id=?
                ''', (first_name, last_name, email, phone, dob, address, student_id))
                self.conn.commit()
                self.load_students()
                self.update_dashboard()
                dialog.destroy()
                self.log_activity(f"Updated student: {first_name} {last_name}")
                messagebox.showinfo("Success", "Student updated successfully!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Email must be unique!")
        
        tk.Button(dialog, text="Save", width=10, command=save_changes).grid(row=6, column=1, pady=20, sticky='e')
    
    def delete_student(self):
        selected_item = self.students_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a student to delete")
            return
            
        student_id = self.students_tree.item(selected_item)['values'][0]
        student_name = self.students_tree.item(selected_item)['values'][1] + " " + \
                      self.students_tree.item(selected_item)['values'][2]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {student_name}?"):
            try:
                # First delete enrollments and grades for this student
                self.cursor.execute("DELETE FROM enrollments WHERE student_id=?", (student_id,))
                self.cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
                self.conn.commit()
                self.load_students()
                self.load_enrollments()
                self.update_dashboard()
                self.log_activity(f"Deleted student: {student_name}")
                messagebox.showinfo("Success", "Student deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting student: {str(e)}")
    
    def view_student_details(self):
        selected_item = self.students_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a student to view")
            return
            
        student_id = self.students_tree.item(selected_item)['values'][0]
        
        # Fetch student details
        self.cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
        student = self.cursor.fetchone()
        
        # Fetch enrollments
        self.cursor.execute('''
            SELECT c.code, c.name, e.enrollment_date 
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id=?
        ''', (student_id,))
        enrollments = self.cursor.fetchall()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Student Details")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Student info frame
        info_frame = tk.LabelFrame(dialog, text="Student Information", padx=10, pady=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        labels = ["ID:", "First Name:", "Last Name:", "Email:", "Phone:", "DOB:", "Address:", "Enrollment Date:"]
        for i, label in enumerate(labels):
            tk.Label(info_frame, text=label, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky='e', padx=5, pady=2)
            tk.Label(info_frame, text=student[i] if i < len(student) else "").grid(row=i, column=1, sticky='w', padx=5, pady=2)
        
        # Enrollments frame
        enroll_frame = tk.LabelFrame(dialog, text="Enrollments", padx=10, pady=10)
        enroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        if enrollments:
            columns = ("Course Code", "Course Name", "Enrollment Date")
            enroll_tree = ttk.Treeview(enroll_frame, columns=columns, show="headings", height=5)
            
            for col in columns:
                enroll_tree.heading(col, text=col)
                enroll_tree.column(col, width=120)
            
            for enrollment in enrollments:
                enroll_tree.insert("", tk.END, values=enrollment)
            
            scrollbar = ttk.Scrollbar(enroll_frame, orient="vertical", command=enroll_tree.yview)
            enroll_tree.configure(yscrollcommand=scrollbar.set)
            
            enroll_tree.pack(side=tk.LEFT, fill='both', expand=True)
            scrollbar.pack(side=tk.RIGHT, fill='y')
        else:
            tk.Label(enroll_frame, text="No enrollments found", font=("Arial", 10)).pack(pady=20)
    
    # Course management methods
    def add_course(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Course")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Course Code:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        code_entry = tk.Entry(dialog, width=30)
        code_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Course Name:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        name_entry = tk.Entry(dialog, width=30)
        name_entry.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Department:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        dept_entry = tk.Entry(dialog, width=30)
        dept_entry.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Credits:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        credits_entry = tk.Entry(dialog, width=30)
        credits_entry.grid(row=3, column=1, padx=10, pady=5)
        credits_entry.insert(0, "3")
        
        tk.Label(dialog, text="Instructor:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        instructor_entry = tk.Entry(dialog, width=30)
        instructor_entry.grid(row=4, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Schedule:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
        schedule_entry = tk.Entry(dialog, width=30)
        schedule_entry.grid(row=5, column=1, padx=10, pady=5)
        
        tk.Label(dialog, text="Room:").grid(row=6, column=0, padx=10, pady=5, sticky='e')
        room_entry = tk.Entry(dialog, width=30)
        room_entry.grid(row=6, column=1, padx=10, pady=5)
        
        def save_course():
            code = code_entry.get()
            name = name_entry.get()
            department = dept_entry.get()
            credits = credits_entry.get()
            instructor = instructor_entry.get()
            schedule = schedule_entry.get()
            room = room_entry.get()
            
            if not code or not name:
                messagebox.showerror("Error", "Course code and name are required!")
                return
            
            try:
                credits = int(credits) if credits else 3
            except ValueError:
                messagebox.showerror("Error", "Credits must be a number")
                return
            
            try:
                self.cursor.execute('''
                    INSERT INTO courses (code, name, department, credits, instructor, schedule, room)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (code, name, department, credits, instructor, schedule, room))
                self.conn.commit()
                self.load_courses()
                self.update_dashboard()
                dialog.destroy()
                self.log_activity(f"Added course: {code} - {name}")
                messagebox.showinfo("Success", "Course added successfully!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Course code must be unique!")
        
        tk.Button(dialog, text="Save", width=10, command=save_course).grid(row=7, column=1, pady=20, sticky='e')
    
    def edit_course(self):
        selected_item = self.courses_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a course to edit")
            return
            
        course_id = self.courses_tree.item(selected_item)['values'][0]
        
        # Fetch course details
        self.cursor.execute("SELECT * FROM courses WHERE id=?", (course_id,))
        course = self.cursor.fetchone()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Course")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Course Code:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        code_entry = tk.Entry(dialog, width=30)
        code_entry.grid(row=0, column=1, padx=10, pady=5)
        code_entry.insert(0, course[1])
        
        tk.Label(dialog, text="Course Name:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        name_entry = tk.Entry(dialog, width=30)
        name_entry.grid(row=1, column=1, padx=10, pady=5)
        name_entry.insert(0, course[2])
        
        tk.Label(dialog, text="Department:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        dept_entry = tk.Entry(dialog, width=30)
        dept_entry.grid(row=2, column=1, padx=10, pady=5)
        dept_entry.insert(0, course[3])
        
        tk.Label(dialog, text="Credits:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        credits_entry = tk.Entry(dialog, width=30)
        credits_entry.grid(row=3, column=1, padx=10, pady=5)
        credits_entry.insert(0, course[4])
        
        tk.Label(dialog, text="Instructor:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        instructor_entry = tk.Entry(dialog, width=30)
        instructor_entry.grid(row=4, column=1, padx=10, pady=5)
        instructor_entry.insert(0, course[5])
        
        tk.Label(dialog, text="Schedule:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
        schedule_entry = tk.Entry(dialog, width=30)
        schedule_entry.grid(row=5, column=1, padx=10, pady=5)
        schedule_entry.insert(0, course[6])
        
        tk.Label(dialog, text="Room:").grid(row=6, column=0, padx=10, pady=5, sticky='e')
        room_entry = tk.Entry(dialog, width=30)
        room_entry.grid(row=6, column=1, padx=10, pady=5)
        room_entry.insert(0, course[7])
        
        def save_changes():
            code = code_entry.get()
            name = name_entry.get()
            department = dept_entry.get()
            credits = credits_entry.get()
            instructor = instructor_entry.get()
            schedule = schedule_entry.get()
            room = room_entry.get()
            
            if not code or not name:
                messagebox.showerror("Error", "Course code and name are required!")
                return
            
            try:
                credits = int(credits) if credits else 3
            except ValueError:
                messagebox.showerror("Error", "Credits must be a number")
                return
            
            try:
                self.cursor.execute('''
                    UPDATE courses 
                    SET code=?, name=?, department=?, credits=?, instructor=?, schedule=?, room=?
                    WHERE id=?
                ''', (code, name, department, credits, instructor, schedule, room, course_id))
                self.conn.commit()
                self.load_courses()
                self.update_dashboard()
                dialog.destroy()
                self.log_activity(f"Updated course: {code} - {name}")
                messagebox.showinfo("Success", "Course updated successfully!")
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Course code must be unique!")
        
        tk.Button(dialog, text="Save", width=10, command=save_changes).grid(row=7, column=1, pady=20, sticky='e')
    
    def delete_course(self):
        selected_item = self.courses_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a course to delete")
            return
            
        course_id = self.courses_tree.item(selected_item)['values'][0]
        course_name = self.courses_tree.item(selected_item)['values'][2]
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete {course_name}?"):
            try:
                # First delete enrollments and grades for this course
                self.cursor.execute("DELETE FROM enrollments WHERE course_id=?", (course_id,))
                self.cursor.execute("DELETE FROM courses WHERE id=?", (course_id,))
                self.conn.commit()
                self.load_courses()
                self.load_enrollments()
                self.update_dashboard()
                self.log_activity(f"Deleted course: {course_name}")
                messagebox.showinfo("Success", "Course deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting course: {str(e)}")
    
    def view_course_details(self):
        selected_item = self.courses_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a course to view")
            return
            
        course_id = self.courses_tree.item(selected_item)['values'][0]
        
        # Fetch course details
        self.cursor.execute("SELECT * FROM courses WHERE id=?", (course_id,))
        course = self.cursor.fetchone()
        
        # Fetch enrollments for this course
        self.cursor.execute('''
            SELECT s.first_name || ' ' || s.last_name, e.enrollment_date 
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            WHERE e.course_id=?
        ''', (course_id,))
        enrollments = self.cursor.fetchall()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Course Details")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Course info frame
        info_frame = tk.LabelFrame(dialog, text="Course Information", padx=10, pady=10)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        labels = ["ID:", "Code:", "Name:", "Department:", "Credits:", "Instructor:", "Schedule:", "Room:"]
        for i, label in enumerate(labels):
            tk.Label(info_frame, text=label, font=("Arial", 10, "bold")).grid(row=i, column=0, sticky='e', padx=5, pady=2)
            tk.Label(info_frame, text=course[i] if i < len(course) else "").grid(row=i, column=1, sticky='w', padx=5, pady=2)
        
        # Enrollments frame
        enroll_frame = tk.LabelFrame(dialog, text="Enrolled Students", padx=10, pady=10)
        enroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        if enrollments:
            columns = ("Student Name", "Enrollment Date")
            enroll_tree = ttk.Treeview(enroll_frame, columns=columns, show="headings", height=5)
            
            for col in columns:
                enroll_tree.heading(col, text=col)
                enroll_tree.column(col, width=120)
            
            for enrollment in enrollments:
                enroll_tree.insert("", tk.END, values=enrollment)
            
            scrollbar = ttk.Scrollbar(enroll_frame, orient="vertical", command=enroll_tree.yview)
            enroll_tree.configure(yscrollcommand=scrollbar.set)
            
            enroll_tree.pack(side=tk.LEFT, fill='both', expand=True)
            scrollbar.pack(side=tk.RIGHT, fill='y')
        else:
            tk.Label(enroll_frame, text="No students enrolled", font=("Arial", 10)).pack(pady=20)
    
    # Enrollment methods
    def enroll_student(self):
        student_name = self.enrollment_student_var.get()
        course_name = self.enrollment_course_var.get()
        
        if not student_name or not course_name:
            messagebox.showerror("Error", "Please select both a student and a course")
            return
        
        # Get student ID
        self.cursor.execute("SELECT id FROM students WHERE first_name || ' ' || last_name = ?", (student_name,))
        student_id = self.cursor.fetchone()
        if not student_id:
            messagebox.showerror("Error", "Selected student not found")
            return
        student_id = student_id[0]
        
        # Get course ID
        self.cursor.execute("SELECT id FROM courses WHERE name = ?", (course_name,))
        course_id = self.cursor.fetchone()
        if not course_id:
            messagebox.showerror("Error", "Selected course not found")
            return
        course_id = course_id[0]
        
        # Check if already enrolled
        self.cursor.execute("SELECT * FROM enrollments WHERE student_id=? AND course_id=?", (student_id, course_id))
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Student is already enrolled in this course")
            return
        
        # Enroll student
        try:
            self.cursor.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)", (student_id, course_id))
            self.conn.commit()
            self.load_enrollments()
            self.update_dashboard()
            self.log_activity(f"Enrolled {student_name} in {course_name}")
            messagebox.showinfo("Success", "Student enrolled successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error enrolling student: {str(e)}")
    
    def unenroll_student(self):
        selected_item = self.enrollments_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select an enrollment to remove")
            return
            
        enrollment_id = self.enrollments_tree.item(selected_item)['values'][0]
        student_name = self.enrollments_tree.item(selected_item)['values'][1]
        course_name = self.enrollments_tree.item(selected_item)['values'][2]
        
        if messagebox.askyesno("Confirm", f"Unenroll {student_name} from {course_name}?"):
            try:
                # First delete grades for this enrollment
                self.cursor.execute("DELETE FROM grades WHERE enrollment_id IN (SELECT id FROM enrollments WHERE id=?)", (enrollment_id,))
                self.cursor.execute("DELETE FROM enrollments WHERE id=?", (enrollment_id,))
                self.conn.commit()
                self.load_enrollments()
                self.update_dashboard()
                self.log_activity(f"Unenrolled {student_name} from {course_name}")
                messagebox.showinfo("Success", "Student unenrolled successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error unenrolling student: {str(e)}")
    
    # Grade methods
    def assign_grade(self):
        selected_item = self.enrollments_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select an enrollment to assign a grade")
            return
            
        enrollment_id = self.enrollments_tree.item(selected_item)['values'][0]
        student_name = self.enrollments_tree.item(selected_item)['values'][1]
        course_name = self.enrollments_tree.item(selected_item)['values'][2]
        
        grade = simpledialog.askfloat("Assign Grade", 
                                     f"Enter grade for {student_name} in {course_name}:",
                                     parent=self.root, minvalue=0, maxvalue=100)
        
        if grade is not None:
            try:
                self.cursor.execute("INSERT INTO grades (enrollment_id, grade, grade_date) VALUES (?, ?, ?)",
                                   (enrollment_id, grade, datetime.now().strftime("%Y-%m-%d")))
                self.conn.commit()
                self.load_grades()
                self.log_activity(f"Assigned grade {grade} to {student_name} for {course_name}")
                messagebox.showinfo("Success", "Grade assigned successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Error assigning grade: {str(e)}")
    
    def view_grades(self):
        selected_item = self.enrollments_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select an enrollment to view grades")
            return
            
        enrollment_id = self.enrollments_tree.item(selected_item)['values'][0]
        student_name = self.enrollments_tree.item(selected_item)['values'][1]
        course_name = self.enrollments_tree.item(selected_item)['values'][2]
        
        # Fetch grades for this enrollment
        self.cursor.execute("SELECT grade, grade_date FROM grades WHERE enrollment_id=?", (enrollment_id,))
        grades = self.cursor.fetchall()
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Grades for {student_name} - {course_name}")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Grades frame
        grades_frame = tk.LabelFrame(dialog, text="Grades", padx=10, pady=10)
        grades_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        if grades:
            columns = ("Grade", "Date")
            grades_tree = ttk.Treeview(grades_frame, columns=columns, show="headings", height=5)
            
            for col in columns:
                grades_tree.heading(col, text=col)
                grades_tree.column(col, width=150)
            
            for grade in grades:
                grades_tree.insert("", tk.END, values=grade)
            
            scrollbar = ttk.Scrollbar(grades_frame, orient="vertical", command=grades_tree.yview)
            grades_tree.configure(yscrollcommand=scrollbar.set)
            
            grades_tree.pack(side=tk.LEFT, fill='both', expand=True)
            scrollbar.pack(side=tk.RIGHT, fill='y')
        else:
            tk.Label(grades_frame, text="No grades recorded", font=("Arial", 10)).pack(pady=20)
    
    def filter_grades(self, event=None):
        # Clear the treeview
        for item in self.grades_tree.get_children():
            self.grades_tree.delete(item)
        
        # Build query based on filters
        query = '''
            SELECT g.id, s.first_name || ' ' || s.last_name, c.name, g.grade, g.grade_date
            FROM grades g
            JOIN enrollments e ON g.enrollment_id = e.id
            JOIN students s ON e.student_id = s.id
            JOIN courses c ON e.course_id = c.id
            WHERE 1=1
        '''
        params = []
        
        course_name = self.grade_course_var.get()
        student_name = self.grade_student_var.get()
        
        if course_name:
            query += " AND c.name = ?"
            params.append(course_name)
        
        if student_name:
            query += " AND s.first_name || ' ' || s.last_name = ?"
            params.append(student_name)
        
        # Fetch filtered grades
        self.cursor.execute(query, tuple(params))
        grades = self.cursor.fetchall()
        
        # Insert into treeview
        for grade in grades:
            self.grades_tree.insert("", tk.END, values=grade)
    
    # Search methods
    def search_students(self, event):
        search_term = self.student_search_entry.get().lower()
        
        # Clear the treeview
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        # Fetch students from database
        self.cursor.execute("SELECT id, first_name, last_name, email, phone, enrollment_date FROM students")
        students = self.cursor.fetchall()
        
        # Filter and insert into treeview
        for student in students:
            # Convert all values to string and search
            if any(search_term in str(field).lower() for field in student):
                self.students_tree.insert("", tk.END, values=student)
    
    def search_courses(self, event):
        search_term = self.course_search_entry.get().lower()
        
        # Clear the treeview
        for item in self.courses_tree.get_children():
            self.courses_tree.delete(item)
        
        # Fetch courses from database
        self.cursor.execute("SELECT id, code, name, department, credits, instructor FROM courses")
        courses = self.cursor.fetchall()
        
        # Filter and insert into treeview
        for course in courses:
            if any(search_term in str(field).lower() for field in course):
                self.courses_tree.insert("", tk.END, values=course)
    
    # Export methods
    def export_students_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Students as CSV"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write header
                writer.writerow(["ID", "First Name", "Last Name", "Email", "Phone", "Date of Birth", "Address", "Enrollment Date"])
                
                # Fetch all students
                self.cursor.execute("SELECT * FROM students")
                students = self.cursor.fetchall()
                
                # Write data
                for student in students:
                    writer.writerow(student)
            
            self.log_activity("Exported students to CSV")
            messagebox.showinfo("Success", "Students exported to CSV successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting students: {str(e)}")
    
    def export_courses_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Courses as CSV"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write header
                writer.writerow(["ID", "Code", "Name", "Department", "Credits", "Instructor", "Schedule", "Room"])
                
                # Fetch all courses
                self.cursor.execute("SELECT * FROM courses")
                courses = self.cursor.fetchall()
                
                # Write data
                for course in courses:
                    writer.writerow(course)
            
            self.log_activity("Exported courses to CSV")
            messagebox.showinfo("Success", "Courses exported to CSV successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting courses: {str(e)}")
    
    # Context menu methods
    def show_student_context_menu(self, event):
        item = self.students_tree.identify_row(event.y)
        if item:
            self.students_tree.selection_set(item)
            self.student_menu.post(event.x_root, event.y_root)
    
    def show_course_context_menu(self, event):
        item = self.courses_tree.identify_row(event.y)
        if item:
            self.courses_tree.selection_set(item)
            self.course_menu.post(event.x_root, event.y_root)
    
    def show_enrollment_context_menu(self, event):
        item = self.enrollments_tree.identify_row(event.y)
        if item:
            self.enrollments_tree.selection_set(item)
            self.enrollment_menu.post(event.x_root, event.y_root)
    
    # Utility methods
    def log_activity(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.activity_listbox.insert(0, f"[{timestamp}] {message}")
        # Keep only the last 20 activities
        if self.activity_listbox.size() > 20:
            self.activity_listbox.delete(20, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = AcademyManagementSystem(root)
    root.mainloop()