import os
import re
import json
import csv
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry

class LogAnalyzer:
    def __init__(self, log_directory, output_directory, status_update_callback, start_date=None, end_date=None, export_csv=False, log_levels=None, keyword=None, log_format='Plain Text'):
        self.log_directory = log_directory
        self.output_directory = output_directory
        self.status_update_callback = status_update_callback
        self.start_date = start_date
        self.end_date = end_date
        self.export_csv = export_csv
        self.log_levels = log_levels if log_levels else ['ERROR', 'WARNING', 'INFO']
        self.keyword = keyword
        self.log_format = log_format
        self.patterns = {
            'ERROR': r'error|failed|critical',
            'WARNING': r'warning|caution',
            'INFO': r'info|started|completed'
        }

    def analyze_logs(self):
        results = {}
        for file_name in os.listdir(self.log_directory):
            file_path = os.path.join(self.log_directory, file_name)
            if os.path.isfile(file_path) and file_name.endswith(self.get_file_extension()):
                self.status_update_callback(f"Analyzing {file_name}...")
                with open(file_path, 'r') as log_file:
                    if self.log_format == 'JSON':
                        log_entries = json.load(log_file)
                        for entry in log_entries:
                            line = json.dumps(entry)
                            self.process_line(line, results)
                    elif self.log_format == 'CSV':
                        reader = csv.DictReader(log_file)
                        for row in reader:
                            line = json.dumps(row)
                            self.process_line(line, results)
                    else:
                        for line in log_file:
                            self.process_line(line, results)

        self.save_results(results)
        if self.export_csv:
            self.export_to_csv(results)

    def process_line(self, line, results):
        for category, pattern in self.patterns.items():
            if category in self.log_levels and re.search(pattern, line, re.IGNORECASE):
                if self.keyword and self.keyword.lower() not in line.lower():
                    continue
                timestamp = self.extract_timestamp(line)
                if self.is_within_date_range(timestamp):
                    entry = {'line': line.strip(), 'timestamp': timestamp}
                    results.setdefault(category, []).append(entry)

    def extract_timestamp(self, log_line):
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
        match = re.search(timestamp_pattern, log_line)
        return match.group(0) if match else "Unknown"

    def is_within_date_range(self, timestamp):
        if timestamp == "Unknown":
            return False
        log_date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        if self.start_date and log_date < datetime.combine(self.start_date, datetime.min.time()):
            return False
        if self.end_date and log_date > datetime.combine(self.end_date, datetime.max.time()):
            return False
        return True

    def save_results(self, results):
        output_file = os.path.join(self.output_directory, f"log_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(self.output_directory, exist_ok=True)
        with open(output_file, 'w') as output:
            json.dump(results, output, indent=4)
        self.status_update_callback(f"Analysis saved to {output_file}")
        messagebox.showinfo("Analysis Complete", f"Analysis saved to {output_file}")

    def export_to_csv(self, results):
        output_file = os.path.join(self.output_directory, f"log_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['Category', 'Timestamp', 'Log Entry']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for category, entries in results.items():
                for entry in entries:
                    writer.writerow({'Category': category, 'Timestamp': entry['timestamp'], 'Log Entry': entry['line']})
        self.status_update_callback(f"CSV export saved to {output_file}")
        messagebox.showinfo("CSV Export Complete", f"CSV export saved to {output_file}")

    def get_file_extension(self):
        if self.log_format == 'JSON':
            return '.json'
        elif self.log_format == 'CSV':
            return '.csv'
        else:
            return '.log'

class LogAnalyzerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LogAnalyzerPro")
        self.root.geometry("500x750")
        self.log_dir = None
        self.output_dir = None
        self.start_date = None
        self.end_date = None
        self.export_csv = tk.BooleanVar()
        self.enable_date_filter = tk.BooleanVar()
        self.log_levels = {'ERROR': tk.BooleanVar(value=True), 'WARNING': tk.BooleanVar(value=True), 'INFO': tk.BooleanVar(value=True)}
        self.keyword = tk.StringVar()
        self.log_format = tk.StringVar(value='Plain Text')

        # Apply styles
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Helvetica', 12), padding=10)
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TText', font=('Helvetica', 12))

        # Call method to create widgets
        self.create_widgets()

    def create_widgets(self):
        # Set up grid layout for centering buttons
        self.root.grid_rowconfigure(0, weight=1)  
        self.root.grid_rowconfigure(1, weight=1)  
        self.root.grid_rowconfigure(2, weight=1)  
        self.root.grid_rowconfigure(3, weight=1) 
        self.root.grid_rowconfigure(4, weight=1) 
        self.root.grid_rowconfigure(5, weight=1) 
        self.root.grid_rowconfigure(6, weight=1) 
        self.root.grid_rowconfigure(7, weight=1) 
        self.root.grid_rowconfigure(8, weight=1) 
        self.root.grid_rowconfigure(9, weight=3)  
        self.root.grid_columnconfigure(0, weight=1) 

        # Create a button to browse log directory
        self.browse_log_button = ttk.Button(self.root, text="Choose Log Directory", command=self.browse_log_dir, width=30)
        self.browse_log_button.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        # Create a button to browse output directory
        self.browse_output_button = ttk.Button(self.root, text="Choose Output Directory", command=self.browse_output_dir, width=30)
        self.browse_output_button.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        # Create date range pickers
        self.start_date_label = ttk.Label(self.root, text="Start Date:")
        self.start_date_label.grid(row=2, column=0, padx=10, pady=5, sticky='w')
        self.start_date_picker = DateEntry(self.root, width=30, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd-mm-yy', state='disabled')
        self.start_date_picker.grid(row=2, column=0, padx=10, pady=5, sticky='e')

        self.end_date_label = ttk.Label(self.root, text="End Date:")
        self.end_date_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')
        self.end_date_picker = DateEntry(self.root, width=30, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd-mm-yy', state='disabled')
        self.end_date_picker.grid(row=3, column=0, padx=10, pady=5, sticky='e')

        # Checkbox for enabling date filter
        self.date_filter_checkbox = ttk.Checkbutton(self.root, text="Enable Date Filter", variable=self.enable_date_filter, command=self.toggle_date_filter)
        self.date_filter_checkbox.grid(row=4, column=0, padx=10, pady=10, sticky='w')

        # Checkboxes for log levels
        self.log_level_frame = ttk.LabelFrame(self.root, text="Log Levels")
        self.log_level_frame.grid(row=5, column=0, padx=10, pady=10, sticky='nsew')
        for level in self.log_levels:
            ttk.Checkbutton(self.log_level_frame, text=level, variable=self.log_levels[level]).pack(anchor='w')
            
            # Entry for keyword search
        self.keyword_label = ttk.Label(self.root, text="Keyword Search:")
        self.keyword_label.grid(row=6, column=0, padx=10, pady=5, sticky='w')
        self.keyword_entry = ttk.Entry(self.root, textvariable=self.keyword, width=30)
        self.keyword_entry.grid(row=6, column=0, padx=10, pady=5, sticky='e')

        # Dropdown for log format selection
        self.log_format_label = ttk.Label(self.root, text="Log Format:")
        self.log_format_label.grid(row=7, column=0, padx=10, pady=5, sticky='w')
        self.log_format_dropdown = ttk.Combobox(self.root, textvariable=self.log_format, values=['Plain Text', 'JSON', 'CSV'], state='readonly', width=28)
        self.log_format_dropdown.grid(row=7, column=0, padx=10, pady=5, sticky='e')

        # Checkbox for CSV export
        self.csv_export_checkbox = ttk.Checkbutton(self.root, text="Export to CSV", variable=self.export_csv)
        self.csv_export_checkbox.grid(row=8, column=0, padx=10, pady=10, sticky='w')

        # Analyze Logs Button
        self.analyze_button = ttk.Button(self.root, text="Analyze Log Data", command=self.analyze_logs, width=30)
        self.analyze_button.grid(row=9, column=0, padx=10, pady=20, sticky='nsew')

        # Text box for console-like output
        self.console_box = tk.Text(self.root, height=5, width=60, wrap=tk.WORD, state=tk.DISABLED, font=('Helvetica', 12))
        self.console_box.grid(row=10, column=0, padx=10, pady=10, sticky='nsew')

    def browse_log_dir(self):
        directory = filedialog.askdirectory(title="Choose Log Directory")
        if directory:
            self.log_dir = directory
            self.update_console(f"Selected Log Directory: {directory}")

    def browse_output_dir(self):
        directory = filedialog.askdirectory(title="Choose Output Directory")
        if directory:
            self.output_dir = directory
            self.update_console(f"Selected Output Directory: {directory}")

    def toggle_date_filter(self):
        if self.enable_date_filter.get():
            self.start_date_picker.config(state='normal')
            self.end_date_picker.config(state='normal')
        else:
            self.start_date_picker.config(state='disabled')
            self.end_date_picker.config(state='disabled')

    def update_console(self, message):
        """Update the console output box."""
        self.console_box.config(state=tk.NORMAL)
        self.console_box.insert(tk.END, message + "\n")
        self.console_box.config(state=tk.DISABLED)
        self.console_box.yview(tk.END)  # Scroll to the end

    def analyze_logs(self):
        if not self.log_dir or not os.path.exists(self.log_dir):
            messagebox.showerror("Error", "Invalid log directory.")
            return

        if not self.output_dir:
            messagebox.showerror("Error", "Output directory is required.")
            return

        if self.enable_date_filter.get():
            self.start_date = self.start_date_picker.get_date()
            self.end_date = self.end_date_picker.get_date()
        else:
            self.start_date = None
            self.end_date = None

        selected_log_levels = [level for level, var in self.log_levels.items() if var.get()]
        keyword = self.keyword.get() if self.keyword.get() else None
        log_format = self.log_format.get()

        self.update_console("Starting log analysis...")
        analyzer = LogAnalyzer(self.log_dir, self.output_dir, self.update_console, self.start_date, self.end_date, self.export_csv.get(), selected_log_levels, keyword, log_format)
        analyzer.analyze_logs()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = LogAnalyzerGUI()
    gui.run()