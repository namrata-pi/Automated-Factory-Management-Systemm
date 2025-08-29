#cureentyly deployed in assembly
import tkinter as tk
from tkinter import ttk, messagebox
import time
from datetime import datetime
import json
import os
import pandas as pd
from tkinter import filedialog
import glob

# Global variables
assigned_tasks = []
completed_tasks = []
workers = ["Vinayak", "Annapurna", "Kavya", "Chaitra", "Pavitra",
           "Sahadev", "Arpita", "Neminath", "Abhishek"]


class DataManager:
    @staticmethod
    def save_data():
        """Save all application data to JSON file"""
        data = {
            'assigned_tasks': assigned_tasks,
            'completed_tasks': completed_tasks,
            'workers': workers
        }

        try:
            if not os.path.exists('data'):
                os.makedirs('data')
            # "//ASSEMBLY/Users/Public/assembly.json"
            filename = "//MSI/Public/assembly.json"
            # filename= "//ASSEMBLY/Users/Public/assembly.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save data: {str(e)}")

    @staticmethod
    def load_data():
        """Load application data from JSON file"""
        global assigned_tasks, completed_tasks, workers
        # "//ASSEMBLY/Users/Public/assembly.json"
        try:
            filename = "//MSI/Public/assembly.json"
            # filename = "//ASSEMBLY/Users/Public/assembly.json"
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
                    assigned_tasks = data.get('assigned_tasks', [])
                    completed_tasks = data.get('completed_tasks', [])
                    workers = data.get('workers', workers)
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load data: {str(e)}")


class WorkerWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Worker Task Management")
        self.top.geometry("1200x700")
        self.top.configure(bg='#f5f5f5')

        # Apply modern theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        self.create_widgets()

        # Initialize all frames first
        self.initialize_pending_tasks_tab()

        # Then update display
        self.update_display()

    def initialize_pending_tasks_tab(self):
        """Initialize the pending tasks tab components"""
        # Pending Tasks tab
        self.pending_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pending_frame, text="Pending Tasks")

        # Add scrollbar to pending tasks
        self.pending_canvas = tk.Canvas(self.pending_frame, bg='#f5f5f5', highlightthickness=0)
        self.pending_scroll = ttk.Scrollbar(self.pending_frame, orient="vertical",
                                            command=self.pending_canvas.yview)
        self.pending_scrollable_frame = ttk.Frame(self.pending_canvas)

        self.pending_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.pending_canvas.configure(
                scrollregion=self.pending_canvas.bbox("all")
            )
        )

        self.pending_canvas.create_window((0, 0), window=self.pending_scrollable_frame, anchor="nw")
        self.pending_canvas.configure(yscrollcommand=self.pending_scroll.set)

        self.pending_canvas.pack(side="left", fill="both", expand=True)
        self.pending_scroll.pack(side="right", fill="y")

    def update_pending_tasks(self):
        """Update the pending tasks display with tasks that have been started"""
        for widget in self.pending_scrollable_frame.winfo_children():
            widget.destroy()

        # Get all tasks that have a start time but aren't completed
        pending_tasks = []
        for task in assigned_tasks:
            if 'start_time' in task and any(task['start_time']):
                for i, start_time in enumerate(task['start_time']):
                    if start_time and task['completed_quantity'][i] < task['quantity'][i]:
                        pending_tasks.append({
                            'worker': task['worker'],
                            'part': task['part'],
                            'task': task['task'][i],
                            'quantity': task['quantity'][i],
                            'completed': task['completed_quantity'][i],
                            'start_time': start_time
                        })

        if not pending_tasks:
            empty_frame = ttk.Frame(self.pending_scrollable_frame)
            empty_frame.pack(pady=20)
            ttk.Label(empty_frame,
                      text="No pending tasks",
                      style='Header.TLabel').pack()
            return

        # Group by worker
        worker_pending = {}
        for task in pending_tasks:
            if task['worker'] not in worker_pending:
                worker_pending[task['worker']] = []
            worker_pending[task['worker']].append(task)

        sorted_workers = sorted(worker_pending.keys())
        num_workers = len(sorted_workers)
        num_cols = 5
        num_rows = (num_workers + num_cols - 1) // num_cols

        for row in range(num_rows):
            row_frame = ttk.Frame(self.pending_scrollable_frame)
            row_frame.pack(fill="x", padx=10, pady=(5, 0))

            for col in range(num_cols):
                worker_index = row * num_cols + col
                if worker_index < num_workers:
                    worker_name = sorted_workers[worker_index]
                    tasks_for_worker = worker_pending[worker_name]

                    worker_container = ttk.Frame(row_frame, style='Highlight.TFrame')
                    worker_container.pack(side="left", fill="y", expand=True, padx=5, pady=5)

                    ttk.Label(worker_container,
                              text=f"👤 {worker_name.upper()}",
                              style='WorkerHeader.TLabel').pack(fill="x", padx=10, pady=(5, 5))

                    for task_idx, task in enumerate(tasks_for_worker):
                        frame_style = 'TaskFrame.TFrame' if task_idx % 2 == 0 else 'Alternate.TFrame'
                        task_frame = ttk.Frame(worker_container, style=frame_style)
                        task_frame.pack(fill="x", padx=10, pady=5, ipadx=5, ipady=5)

                        ttk.Label(
                            task_frame,
                            text=f"🔧 Part: {task['part'].upper()}",
                            font=('Arial', 11, 'bold'),
                            style='Task.TLabel'
                        ).pack(anchor="w", padx=10, pady=(5, 0))

                        ttk.Label(
                            task_frame,
                            text=f"📌 Task: {task['task']}",
                            style='Task.TLabel'
                        ).pack(anchor="w", padx=10)

                        ttk.Label(
                            task_frame,
                            text=f"⏱️ Started: {task['start_time']}",
                            style='Task.TLabel'
                        ).pack(anchor="w", padx=10)

                        ttk.Label(
                            task_frame,
                            text=f"📊 Status: {task['completed']}/{task['quantity']}",
                            style='Task.TLabel'
                        ).pack(anchor="w", padx=10, pady=(0, 5))

    def configure_styles(self):
        """Configure custom styles for widgets"""
        self.style.configure('TFrame', background='#f5f5f5')
        self.style.configure('TLabel', background='#f5f5f5', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10), padding=5)
        self.style.configure('TNotebook', background='#f5f5f5')
        self.style.configure('TNotebook.Tab', font=('Arial', 11, 'bold'), padding=[10, 5])

        # Custom styles
        self.style.configure('Header.TLabel',
                             font=('Arial', 14, 'bold'),
                             foreground='#2c3e50',
                             background='#f5f5f5')

        self.style.configure('WorkerHeader.TLabel',
                             font=('Arial', 12, 'bold'),
                             foreground='#2c3e50',
                             background='#e8f4f8')

        self.style.configure('Task.TLabel',
                             font=('Arial', 10),
                             padding=5)

        self.style.configure('Highlight.TFrame',
                             background='#e8f4f8',
                             relief='groove',
                             borderwidth=2)

        self.style.configure('TaskFrame.TFrame',
                             background='#ffffff',
                             relief='flat',
                             borderwidth=1)

        self.style.configure('Alternate.TFrame',
                             background='#f9f9f9',  # Slightly different from white
                             relief='flat',
                             borderwidth=1)

        self.style.map('TButton',
                       foreground=[('active', 'white'), ('!disabled', 'black')],
                       background=[('active', '#3498db'), ('!disabled', '#ecf0f1')])

        self.style.configure('Small.TButton',
                             font=('Arial', 8),  # Smaller font
                             padding=[3, 1],  # Less padding
                             width=6)

    def create_widgets(self):
        """Create the worker view interface"""
        # Header
        header_frame = ttk.Frame(self.top)
        header_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(header_frame,
                  text="Worker Task Dashboard",
                  style='Header.TLabel').pack(side="left", padx=10)

        # Refresh button
        refresh_btn = ttk.Button(header_frame,
                                 text="🔄 Refresh",
                                 command=self.update_display)
        refresh_btn.pack(side="right", padx=10)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.top)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Assigned tasks tab
        self.assigned_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.assigned_frame, text="My Assigned Tasks")

        # Add scrollbar to assigned tasks
        self.assigned_canvas = tk.Canvas(self.assigned_frame, bg='#f5f5f5', highlightthickness=0)
        self.assigned_scroll = ttk.Scrollbar(self.assigned_frame, orient="vertical", command=self.assigned_canvas.yview)
        self.assigned_scrollable_frame = ttk.Frame(self.assigned_canvas)

        self.assigned_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.assigned_canvas.configure(
                scrollregion=self.assigned_canvas.bbox("all")
            )
        )

        # Bind mouse wheel to scroll
        self.assigned_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.assigned_canvas.create_window((0, 0), window=self.assigned_scrollable_frame, anchor="nw")
        self.assigned_canvas.configure(yscrollcommand=self.assigned_scroll.set)

        self.assigned_canvas.pack(side="left", fill="both", expand=True)
        self.assigned_scroll.pack(side="right", fill="y")

        # Completed tasks tab
        self.completed_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.completed_frame, text="My Completed Tasks")

        button_frame = ttk.Frame(self.completed_frame)
        button_frame.pack(fill="x", padx=10, pady=5)

        # Export to Excel button
        export_btn = ttk.Button(button_frame,
                                text="Export to Excel",
                                command=self.export_to_excel)
        export_btn.pack(side="left", padx=5)

        # Clear completed tasks button
        clear_btn = ttk.Button(button_frame,
                               text="Clear Completed Tasks",
                               command=self.clear_completed_tasks)
        clear_btn.pack(side="left", padx=5)

        # Add scrollbar to completed tasks
        self.completed_canvas = tk.Canvas(self.completed_frame, bg='#f5f5f5', highlightthickness=0)
        self.completed_scroll = ttk.Scrollbar(self.completed_frame, orient="vertical",
                                              command=self.completed_canvas.yview)
        self.completed_scrollable_frame = ttk.Frame(self.completed_canvas)

        self.completed_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.completed_canvas.configure(
                scrollregion=self.completed_canvas.bbox("all")
            )
        )

        # Bind mouse wheel to scroll
        self.completed_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.completed_canvas.create_window((0, 0), window=self.completed_scrollable_frame, anchor="nw")
        self.completed_canvas.configure(yscrollcommand=self.completed_scroll.set)

        self.completed_canvas.pack(side="left", fill="both", expand=True)
        self.completed_scroll.pack(side="right", fill="y")

    def export_to_excel(self):
        """Export completed tasks to Excel file with current date as sheet name"""
        if not completed_tasks:
            messagebox.showwarning("No Data", "There are no completed tasks to export")
            return

        try:
            # Create a DataFrame from completed tasks
            df = pd.DataFrame(completed_tasks)

            # Get current date for sheet name
            current_date = datetime.now().strftime("%Y-%m-%d")

            # Ask user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Save Completed Tasks As",
                initialfile=f"completed_tasks_{current_date}.xlsx"
            )

            # If user cancels the save dialog
            if not file_path:
                return

            # Create Excel writer object
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Write DataFrame to sheet named with current date
                df.to_excel(writer, sheet_name=current_date, index=False)

                # Auto-adjust column widths
                worksheet = writer.sheets[current_date]
                for column in worksheet.columns:
                    max_length = 0
                    column = [cell for cell in column]
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = (max_length + 2)
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

            messagebox.showinfo("Export Successful",
                                f"Completed tasks exported to:\n{file_path}\nSheet name: {current_date}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def clear_completed_tasks(self):
        """Clear all completed tasks"""
        global completed_tasks  # Move this to the top of the method

        if not completed_tasks:
            messagebox.showinfo("No Tasks", "There are no completed tasks to clear")
            return

        if messagebox.askyesno("Confirm Clear",
                               "Are you sure you want to clear ALL completed tasks?\nThis cannot be undone."):
            completed_tasks = []
            DataManager.save_data()
            self.update_completed_tasks()
            messagebox.showinfo("Cleared", "All completed tasks have been removed")

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling for both canvases"""
        if event.widget == self.assigned_canvas or event.widget == self.completed_canvas:
            # Determine which canvas to scroll
            canvas = event.widget
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def update_display(self):
        """Update the display with current task data"""
        self.update_assigned_tasks()
        self.update_completed_tasks()

        # Only update pending tasks if the frame exists
        if hasattr(self, 'pending_scrollable_frame'):
            self.update_pending_tasks()

    def delete_task(self, task_info):
        """Delete an assigned task"""
        if messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete this task?\n\n"
                f"Part: {task_info['part']}\n"
                f"Task: {task_info['task'][0]}\n"
                f"Worker: {task_info['worker']}"
        ):
            if task_info in assigned_tasks:
                assigned_tasks.remove(task_info)
                DataManager.save_data()
                self.update_display()
                messagebox.showinfo("Deleted", "Task successfully removed!")

    def update_assigned_tasks(self):
        """Update the assigned tasks display with worker boxes side-by-side"""
        # Clear existing widgets
        for widget in self.assigned_scrollable_frame.winfo_children():
            widget.destroy()

        if not assigned_tasks:
            empty_frame = ttk.Frame(self.assigned_scrollable_frame)
            empty_frame.pack(pady=20)
            ttk.Label(empty_frame,
                      text="No tasks currently assigned",
                      style='Header.TLabel').pack()
            return

        worker_tasks = {}
        for task in assigned_tasks:
            if task['worker'] not in worker_tasks:
                worker_tasks[task['worker']] = []
            worker_tasks[task['worker']].append(task)

        sorted_workers = sorted(worker_tasks.keys())
        num_workers = len(sorted_workers)
        num_cols = 3  # Number of worker columns per row
        num_rows = (num_workers + num_cols - 1) // num_cols

        for row in range(num_rows):
            row_frame = ttk.Frame(self.assigned_scrollable_frame)
            row_frame.pack(fill="x", padx=10, pady=(5, 0))

            for col in range(num_cols):
                worker_index = row * num_cols + col
                if worker_index < num_workers:
                    worker_name = sorted_workers[worker_index]
                    tasks_for_worker = worker_tasks[worker_name]

                    worker_container = ttk.Frame(row_frame, style='Highlight.TFrame')
                    worker_container.pack(side="left", fill="y", expand=True, padx=5, pady=5)

                    ttk.Label(worker_container,
                              text=f"👤 {worker_name.upper()}",
                              style='WorkerHeader.TLabel').pack(fill="x", padx=10, pady=(5, 5))

                    for task_idx, task in enumerate(tasks_for_worker):
                        frame_style = 'TaskFrame.TFrame' if task_idx % 2 == 0 else 'Alternate.TFrame'
                        part_frame = ttk.Frame(worker_container, style=frame_style)
                        part_frame.pack(fill="x", padx=10, pady=5, ipadx=5, ipady=5)

                        # Part header
                        ttk.Label(
                            part_frame,
                            text=f"🔧 Part: {task['part'].upper()}",
                            font=('Arial', 11, 'bold'),
                            style='Task.TLabel'
                        ).pack(anchor="w", padx=10, pady=(5, 0))

                        # Task details for each subtask
                        for i, (task_name, qty, completed) in enumerate(
                                zip(task['task'], task['quantity'], task['completed_quantity'])):
                            remaining = qty - completed
                            if remaining > 0:
                                task_row = ttk.Frame(part_frame)
                                task_row.pack(fill="x", padx=15, pady=5, ipadx=5, ipady=5)

                                # Task info (left side)
                                info_frame = ttk.Frame(task_row)
                                info_frame.pack(side="left", fill="x", expand=True)

                                ttk.Label(
                                    info_frame,
                                    text=f"📌 Task: {task_name}",
                                    style='Task.TLabel'
                                ).pack(anchor="w")

                                # Show start time if available
                                if 'start_time' in task and task['start_time'][i]:
                                    ttk.Label(
                                        info_frame,
                                        text=f"⏱️ Started: {task['start_time'][i]}",
                                        style='Task.TLabel'
                                    ).pack(anchor="w")

                                ttk.Label(
                                    info_frame,
                                    text=f"📊 Status: {completed}/{qty} (Remaining: {remaining})",
                                    style='Task.TLabel'
                                ).pack(anchor="w")

                                # Controls (right side)
                                ctrl_frame = ttk.Frame(task_row)
                                ctrl_frame.pack(side="right", padx=10)

                                # Delete button (always visible)
                                delete_btn = tk.Button(  # Using tk.Button instead of ttk for better emoji sizing
                                    ctrl_frame,
                                    text=" 🗑️ ",  # Note the spaces around emoji for padding
                                    command=lambda t=task: self.delete_task(t),
                                    font=('Segoe UI Emoji', 12),  # Special emoji font
                                    relief='groove',
                                    borderwidth=1,
                                    padx=2,
                                    pady=0
                                )
                                delete_btn.pack(side="left", padx=2)

                                # Start button (only if not started)
                                if 'start_time' not in task or not task['start_time'][i]:
                                    start_btn = tk.Button(
                                        ctrl_frame,
                                        text=" ▶️ ",
                                        command=lambda t=task, idx=i: self.start_task(t, idx),
                                        font=('Segoe UI Emoji', 12),
                                        relief='groove',
                                        borderwidth=1,
                                        padx=2,
                                        pady=0
                                    )
                                    start_btn.pack(side="left", padx=2)

                                # Completion controls (always visible)
                                # Completion controls
                                ttk.Label(ctrl_frame, text="Qty:", font=('Arial', 9)).pack(side="left")
                                entry = ttk.Entry(ctrl_frame, width=4, font=('Arial', 9))
                                entry.pack(side="left", padx=2)

                                complete_btn = tk.Button(
                                    ctrl_frame,
                                    text=" ✅ ",
                                    command=lambda t=task, idx=i, e=entry: self.mark_task_complete(t, idx, e.get()),
                                    font=('Segoe UI Emoji', 12),
                                    relief='groove',
                                    borderwidth=1,
                                    padx=2,
                                    pady=0
                                )
                                complete_btn.pack(side="left", padx=2)

    def start_task(self, task_info, task_index):
        """Record the start time for a task and remove Start button"""
        if 'start_time' not in task_info:
            task_info['start_time'] = [''] * len(task_info['task'])

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_info['start_time'][task_index] = current_time
        DataManager.save_data()

        # Update display to hide Start button
        self.update_display()

        messagebox.showinfo("Task Started", f"Start time recorded: {current_time}")


    def update_completed_tasks(self):
        """Update the completed tasks display with worker boxes side-by-side"""
        # Clear existing widgets
        for widget in self.completed_scrollable_frame.winfo_children():
            widget.destroy()

        if not completed_tasks:
            empty_frame = ttk.Frame(self.completed_scrollable_frame)
            empty_frame.pack(pady=20)
            ttk.Label(empty_frame,
                      text="No tasks completed yet",
                      style='Header.TLabel').pack()
            return

        worker_completed_tasks = {}
        for task in completed_tasks:
            if task['worker'] not in worker_completed_tasks:
                worker_completed_tasks[task['worker']] = []
            worker_completed_tasks[task['worker']].append(task)

        sorted_workers = sorted(worker_completed_tasks.keys())
        num_workers = len(sorted_workers)
        num_cols = 5
        num_rows = (num_workers + num_cols - 1) // num_cols

        for row in range(num_rows):
            row_frame = ttk.Frame(self.completed_scrollable_frame)
            row_frame.pack(fill="x", padx=10, pady=(5, 0))

            for col in range(num_cols):
                worker_index = row * num_cols + col
                if worker_index < num_workers:
                    worker_name = sorted_workers[worker_index]
                    tasks_for_worker = worker_completed_tasks[worker_name]

                    worker_container = ttk.Frame(row_frame, style='Highlight.TFrame')
                    worker_container.pack(side="left", fill="y", expand=True, padx=5, pady=5)

                    ttk.Label(worker_container,
                              text=f"👤 {worker_name.upper()}",
                              style='WorkerHeader.TLabel').pack(fill="x", padx=10, pady=(5, 5))

                    for task_idx, task in enumerate(tasks_for_worker):
                        frame_style = 'TaskFrame.TFrame' if task_idx % 2 == 0 else 'Alternate.TFrame'
                        task_frame = ttk.Frame(worker_container, style=frame_style)
                        task_frame.pack(fill="x", padx=10, pady=5, ipadx=5, ipady=5)

                        details = [
                            f"🔧 Part: {task['part'].upper()}",
                            f"📌 Task: {task['task_name']}",
                            f"✅ Completed: {task['completed_qty']}/{task['initial_qty']}",
                            f"⏱️ Started: {task['start_time']}",
                            f"🏁 Finished: {task['completion_time']}"
                        ]

                        for detail in details:
                            ttk.Label(
                                task_frame,
                                text=detail,
                                style='Task.TLabel'
                            ).pack(anchor="w", padx=10, pady=2)

    def mark_task_complete(self, task_info, task_index, qty_str):
        """Mark a task as completed"""
        try:
            qty = int(qty_str)
            remaining = task_info['quantity'][task_index] - task_info['completed_quantity'][task_index]

            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be positive")
                return
            if qty > remaining:
                messagebox.showerror("Error", f"Cannot complete more than remaining ({remaining})")
                return

            # Update task completion
            task_info['completed_quantity'][task_index] += qty
            completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            start_time = task_info.get('start_time', [''] * len(task_info['task']))[task_index]

            # Add to completed tasks
            completed_tasks.append({
                'worker': task_info['worker'],
                'part': task_info['part'],
                'task_name': task_info['task'][task_index],
                'initial_qty': task_info['quantity'][task_index],
                'completed_qty': qty,
                'start_time': start_time if start_time else "Not recorded",
                'completion_time': completion_time,
                'assignment_time': task_info['timestamp'][task_index].split('\n')[0]
            })

            # Remove task if fully completed
            if all(c >= q for c, q in zip(task_info['completed_quantity'], task_info['quantity'])):
                assigned_tasks.remove(task_info)

            DataManager.save_data()
            self.update_display()
            messagebox.showinfo("Success", f"Marked {qty} items as completed!")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")


class AdminPanel:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("Admin Panel - Task Assignment System")
        self.top.geometry("950x800")  # Slightly larger to accommodate bigger fonts
        self.top.configure(bg='#f0f2f5')

        # Variables
        self.part_var = tk.StringVar()
        self.task_var = tk.StringVar()
        self.worker_var = tk.StringVar()
        self.quantity_var = tk.StringVar()

        # Apply modern theme with larger fonts
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        self.create_widgets()

    def configure_styles(self):
        """Configure styles with increased font sizes"""
        # Base font size increased to 11 (from typical 10)
        self.style.configure('.', font=('Segoe UI', 11))

        # Specific style configurations with larger fonts
        self.style.configure('TFrame', background='#f0f2f5')
        self.style.configure('Header.TLabel',
                             font=('Segoe UI', 18, 'bold'),  # Increased from 16
                             foreground='#2c3e50',
                             background='#f0f2f5')
        self.style.configure('Section.TLabelframe',
                             font=('Segoe UI', 13, 'bold'),  # Increased from 11
                             borderwidth=0,
                             background='#f0f2f5')
        self.style.configure('Section.TLabelframe.Label',
                             foreground='#2c3e50',
                             background='#f0f2f5',
                             font=('Segoe UI', 13, 'bold'))  # Increased
        self.style.configure('TButton',
                             font=('Segoe UI', 11, 'bold'),  # Increased
                             padding=8)  # More padding for larger text
        self.style.configure('TRadiobutton',
                             font=('Segoe UI', 11),  # Increased
                             background='#f0f2f5')
        self.style.configure('TCombobox',
                             font=('Segoe UI', 11))  # Increased
        self.style.configure('TEntry',
                             font=('Segoe UI', 11))  # Increased
        self.style.configure('TLabel',
                             font=('Segoe UI', 11))  # Increased
        self.style.map('TButton',
                       foreground=[('active', 'white'), ('!disabled', 'white')],
                       background=[('active', '#3498db'), ('!disabled', '#2980b9')])

    def create_widgets(self):
        """Create the admin panel interface with larger fonts"""
        # Main container
        main_frame = ttk.Frame(self.top)
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)  # More padding

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 20))  # More padding

        ttk.Label(header_frame,
                  text=f"{get_greeting()}, Administrator",
                  style='Header.TLabel').pack(side='left')

        # Form container
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='both', expand=True)

        # Left column (Parts) - with larger fonts
        left_col = ttk.Frame(form_frame)
        left_col.pack(side='left', fill='both', expand=True, padx=10)

        # Parts selection with larger text
        parts_frame = ttk.LabelFrame(left_col, text="1. Select Component", style='Section.TLabelframe')
        parts_frame.pack(fill='both', expand=True, pady=10)  # More padding

        parts_container = ttk.Frame(parts_frame)
        parts_container.pack(fill='both', expand=True, padx=15, pady=15)  # More padding

        # Create scrollable parts list with larger items
        parts_canvas = tk.Canvas(parts_container, bg='#f0f2f5', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parts_container, orient='vertical', command=parts_canvas.yview)
        scrollable_frame = ttk.Frame(parts_canvas)

        scrollable_frame.bind(
            '<Configure>',
            lambda e: parts_canvas.configure(
                scrollregion=parts_canvas.bbox('all')
            )
        )

        parts_canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
        parts_canvas.configure(yscrollcommand=scrollbar.set)

        parts_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Add parts with larger font size
        for part in parts:
            rb = ttk.Radiobutton(scrollable_frame,
                                 text=part,
                                 variable=self.part_var,
                                 value=part,
                                 command=self.update_tasks)
            rb.pack(anchor='w', pady=3, padx=8)  # More padding for larger text

        # Right column (Form) - with larger fonts
        right_col = ttk.Frame(form_frame)
        right_col.pack(side='right', fill='both', expand=True, padx=10)

        # Task selection with larger text
        task_frame = ttk.LabelFrame(right_col, text="2. Select Operation", style='Section.TLabelframe')
        task_frame.pack(fill='x', pady=10)  # More padding

        ttk.Label(task_frame,
                  text="Available Operations:",
                  font=('Segoe UI', 11)).pack(anchor='w', padx=15, pady=(10, 5))  # Larger padding

        self.task_dropdown = ttk.Combobox(task_frame,
                                          textvariable=self.task_var,
                                          state='readonly',
                                          font=('Segoe UI', 11))  # Larger font
        self.task_dropdown.pack(fill='x', padx=15, pady=(0, 15), ipady=6)  # More padding

        # Worker selection with larger text
        worker_frame = ttk.LabelFrame(right_col, text="3. Assign To Worker", style='Section.TLabelframe')
        worker_frame.pack(fill='x', pady=10)  # More padding

        ttk.Label(worker_frame,
                  text="Select Worker:",
                  font=('Segoe UI', 11)).pack(anchor='w', padx=15, pady=(10, 5))  # Larger padding

        self.worker_dropdown = ttk.Combobox(worker_frame,
                                            textvariable=self.worker_var,
                                            values=workers + ["Add New Worker..."],
                                            state='readonly',
                                            font=('Segoe UI', 11))
        self.worker_dropdown.pack(fill='x', padx=15, pady=(0, 15), ipady=6)
        self.worker_dropdown.bind('<<ComboboxSelected>>', self._handle_worker_selection)  # More padding

        # Quantity entry with larger text
        qty_frame = ttk.LabelFrame(right_col, text="4. Set Quantity", style='Section.TLabelframe')
        qty_frame.pack(fill='x', pady=10)  # More padding

        ttk.Label(qty_frame,
                  text="Enter Quantity:",
                  font=('Segoe UI', 11)).pack(anchor='w', padx=15, pady=(10, 5))  # Larger padding

        self.quantity_entry = ttk.Entry(qty_frame,
                                        textvariable=self.quantity_var,
                                        font=('Segoe UI', 11))  # Larger font
        self.quantity_entry.pack(fill='x', padx=15, pady=(0, 15), ipady=6)  # More padding

        # Assign button with larger text
        btn_frame = ttk.Frame(right_col)
        btn_frame.pack(fill='x', pady=20)  # More padding

        assign_btn = ttk.Button(btn_frame,
                                text="ASSIGN TASK",
                                command=self.assign_task,
                                style='TButton')
        assign_btn.pack(ipady=10, ipadx=30)  # Larger button

        # Status bar with larger text
        status_frame = ttk.Frame(main_frame, style='TFrame')
        status_frame.pack(fill='x', pady=(15, 0))  # More padding

        self.status_label = ttk.Label(status_frame,
                                      text="Ready",
                                      foreground="#27ae60",
                                      font=('Segoe UI', 10))  # Slightly larger than standard
        self.status_label.pack(side='left', padx=10)

    def _handle_worker_selection(self, event=None):
        """Handle when a worker is selected from dropdown"""
        if self.worker_var.get() == "Add New Worker...":
            # Show custom worker dialog
            custom_worker = self._get_custom_worker()
            if custom_worker:  # If user didn't cancel
                # Add to workers list
                workers.append(custom_worker.lower())  # Save in lowercase as per your JSON
                workers.sort()  # Keep sorted
                DataManager.save_data()

                # Update dropdown values
                self.worker_dropdown['values'] = workers + ["Add New Worker..."]
                self.worker_var.set(custom_worker)
                self.status_label.config(
                    text=f"New worker added: {custom_worker}",
                    foreground="#27ae60")
            else:
                self.worker_var.set("")  # Reset if cancelled
                self.status_label.config(
                    text="No new worker added",
                    foreground="#e74c3c")

    def _get_custom_worker(self):
        """Show dialog to get custom worker name from user"""
        dialog = tk.Toplevel(self.top)
        dialog.title("Add New Worker")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.top)
        dialog.grab_set()

        ttk.Label(dialog,
                  text="Enter new worker name:",
                  font=('Segoe UI', 11)).pack(pady=10)

        worker_entry = ttk.Entry(dialog, font=('Segoe UI', 11))
        worker_entry.pack(fill='x', padx=20, pady=10)
        worker_entry.focus_set()

        result = None

        def on_ok():
            nonlocal result
            worker_text = worker_entry.get().strip()
            if worker_text:
                result = worker_text
            dialog.destroy()

        def on_cancel():
            nonlocal result
            result = None
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="OK", command=on_ok).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side='right', padx=10)

        dialog.wait_window()
        return result

    def update_tasks(self):
        """Update available tasks - shows dropdown for normal parts, dialog for 'Others'"""
        selected_part = self.part_var.get()
        if not selected_part:
            return

        self.task_var.set("")

        # Always show the task dropdown
        self.task_dropdown.pack(fill='x', padx=15, pady=(0, 15), ipady=6)

        # Get standard tasks for the selected part
        available_tasks = task_mapping.get(selected_part, [])

        # Add "Other Task..." option to the dropdown
        available_tasks.append("Other Task...")
        self.task_dropdown['values'] = available_tasks

        # Set up trace for when task selection changes
        if hasattr(self, '_task_trace'):
            self.task_var.trace_remove('write', self._task_trace)
        self._task_trace = self.task_var.trace('w', self._handle_task_selection)

        if available_tasks:
            self.status_label.config(
                text=f"Selected: {selected_part} - {len(available_tasks) - 1} operations available",
                foreground="#27ae60")
        else:
            self.status_label.config(
                text=f"Selected: {selected_part} - No standard operations",
                foreground="#e74c3c")

    def _handle_task_selection(self, *args):
        """Handle when a task is selected from dropdown"""
        if self.task_var.get() == "Other Task...":
            # Show custom task dialog
            custom_task = self._get_custom_task()
            if custom_task:  # If user didn't cancel
                self.task_var.set(custom_task)
                self.status_label.config(
                    text=f"Custom task added: {custom_task}",
                    foreground="#27ae60")
            else:
                self.task_var.set("")  # Reset if cancelled
                self.status_label.config(
                    text="No custom task entered",
                    foreground="#e74c3c")

    def _get_custom_task(self):
        """Show dialog to get custom task name from user"""
        dialog = tk.Toplevel(self.top)
        dialog.title("Enter Custom Task")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.top)
        dialog.grab_set()

        ttk.Label(dialog,
                  text="Enter custom task name:",
                  font=('Segoe UI', 11)).pack(pady=10)

        task_entry = ttk.Entry(dialog, font=('Segoe UI', 11))
        task_entry.pack(fill='x', padx=20, pady=10)
        task_entry.focus_set()

        result = None

        def on_ok():
            nonlocal result
            task_text = task_entry.get().strip()
            if task_text:
                result = task_text
            dialog.destroy()

        def on_cancel():
            nonlocal result
            result = None
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="OK", command=on_ok).pack(side='left', padx=10)
        ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side='right', padx=10)

        dialog.wait_window()
        return result

    def assign_task(self):
        """Assign a new task to a worker"""
        part = self.part_var.get()
        task = self.task_var.get()
        worker = self.worker_var.get()
        qty_str = self.quantity_var.get()

        if not all([part, task, worker, qty_str]):
            self.status_label.config(text="Error: All fields are required", foreground="#e74c3c")
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            qty = int(qty_str)
            if qty <= 0:
                self.status_label.config(text="Error: Quantity must be positive", foreground="#e74c3c")
                messagebox.showerror("Error", "Quantity must be positive")
                return

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Find existing task for this worker/part or create new
            existing = next((t for t in assigned_tasks
                             if t['worker'] == worker and t['part'] == part), None)

            if existing:
                if task in existing['task']:
                    idx = existing['task'].index(task)
                    existing['quantity'][idx] += qty
                    existing['timestamp'][idx] += f"\n{timestamp}"
                    action = "updated"
                else:
                    existing['task'].append(task)
                    existing['quantity'].append(qty)
                    existing['timestamp'].append(timestamp)
                    existing['completed_quantity'].append(0)
                    existing['completion_time'].append('')
                    action = "appended"
            else:
                assigned_tasks.append({
                    "part": part,
                    "task": [task],
                    "worker": worker,
                    "quantity": [qty],
                    "timestamp": [timestamp],
                    "completed_quantity": [0],
                    "completion_time": ['']
                })
                action = "assigned"

            success_msg = f"Task {action.upper()}: {worker} → {task} (Qty: {qty})"
            self.status_label.config(text=success_msg, foreground="#27ae60")
            messagebox.showinfo("Success",
                                f"Task successfully {action}!\n\n{part}\n{task}\nWorker: {worker}\nQuantity: {qty}")
            DataManager.save_data()

            # Clear quantity field only
            self.quantity_var.set("")

        except ValueError:
            self.status_label.config(text="Error: Quantity must be a valid number", foreground="#e74c3c")
            messagebox.showerror("Error", "Please enter a valid number for quantity")


def get_greeting():
    """Return appropriate greeting based on time of day"""
    hour = time.localtime().tm_hour
    if hour < 12:
        return "Good Morning"
    elif hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"


def main():
    """Main application entry point"""
    # Load existing data
    DataManager.load_data()

    # Create main window
    root = tk.Tk()
    root.title("Astr Factory Management System")
    root.geometry("400x300")

    # Login frame
    ttk.Label(root, text="Astr Factory Management System",
              font=("Arial", 14, "bold"), foreground="blue").pack(pady=20)

    login_frame = ttk.Frame(root)
    login_frame.pack()

    # Username
    ttk.Label(login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
    username_var = tk.StringVar()
    username_entry = ttk.Entry(login_frame, textvariable=username_var)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

    # Password
    ttk.Label(login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
    password_var = tk.StringVar()
    password_entry = ttk.Entry(login_frame, textvariable=password_var, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    # Login button
    def login(event=None):
        if username_var.get() == "admin" and password_var.get() == "password":
            AdminPanel(root)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    login_btn = ttk.Button(root, text="Login", command=login)
    login_btn.pack(pady=10)

    # ttk.Button(root, text="Login", command=login).pack(pady=10)
    ttk.Button(root, text="Worker View", command=lambda: WorkerWindow(root)).pack()
    password_entry.bind('<Return>', login)  # Pressing Enter in password field will trigger login
    username_entry.bind('<Return>', lambda e: password_entry.focus())

    root.mainloop()


# Parts and task mapping
parts = ["slide", "BRL", "SLDcatch", "TBR", "DISC", "TGR", "MRL", "MAG BASE",
         "MANUAL SFTY", "MAG CASE", "FRAME", "Grip pannel", "CHASSIS",
         "SLD CVR", "FP", "EXTR", "Detent", "TDL",
         "Sub Assemblies","Overall Assembly","Checks","Dispatch","Test","Others"]

task_mapping = {
    "slide": [
        "Hand Deburr (setup 1)", "QC/ GAUGES AND FIXTURES", "Hand deburr", "Buffing", "CFM",
        "VMM", "Tapping", "Firing Pin Slot Polishing", "FP Hole Inspection Camera",
        "Final Component QC/ Assembly checks", "Vacuum Hardening", "Cleaning",
        "Machining Top Surface", "wirecut", "polishing top surface & lapping",
        "Laser Marking", "overall assembly", "Serial Marking", "Cerakote",
        "rails /breach/firing pin slot/lapping"
    ],
    "BRL": [
        "Batch Qty", "Hand Deburr (setup 1)", "Proof Marking", "Buffing", "Hand Deburr (setup 2)",
        "CFM (12pcs in 40 Mins)", "VMM", "CHAMBER AND FEEDRAMP POLISH", "Cleaning",
        "Serial Marking", "Assembly Check", "QPQ", "Lapping", "QC Checks"
    ],

    "SLDcatch": [
        "Cutting to Size - QC", "SERIAL MARKING", "Grinding & Buffing", "Hand Deburr (setup 1)",
        "Final Component QC/ Assembly checks", "CFM (XXXX/ XX PCS)",
        "Stress Relieving & Vacuum Hardening (XXXX DAYS)", "Cleaning (ACID WASH)",
        "QC Checks", "Final Component QC/ Assembly checks"
    ],

    "TBR": [
        "Hand Deburr (setup 1)", "QC/ GAUGES AND FIXTURES", "Hand Deburr (setup 2)", "Buffing & Grinding",
        "Hand deburr", "VMM", "Final Component QC/ Assembly checks", "Stress Relieving & Vacuum Hardening (XXXX DAYS )",
        "Cleaning (ACID WASH)", "QC Checks"
    ],

    "DISC": [
        "QC/ GAUGES AND FIXTURES", "Hand Deburr", "VMS", "Grinding & Buffing", "CFM",
        "Final Component QC/ Assembly checks",
        "Stress Relieving & Vacuum Hardening (XXXX DAYS )", "Cleaning (ACID WASH)", "QC Checks"
    ],
    "TGR": [
        "Hand Deburr (setup 1)", 'Buffing', 'Chamfer', 'Polish', 'vibratory', 'MAGNETIC DEBURR', 'Hardanodyzing',
        'CERAKOTE'
    ],
    "MRL": [
        "Hand Deburr (setup 1)", "Buffing", "QC/ GAUGES AND FIXTURES", 'CFM(XXXX/ XX PCS)',
        'Final Component QC/ Assembly checks', 'Stress Relieving & Vacuum Hardening (XXXX DAYS )',
        'Cleaning (ACID WASH)', 'QC Checks', 'Cerakote'
    ],
    "MAG BASE": [
        "QC AND GAUGES    Asembly Checks", "Grinding", "Buffing", 'DEBURR    POLISHING', 'Tapping',
        'Vibratory Magnetic', 'Hardanodizing', 'QC'
    ],
    "MANUAL SFTY": [
        'Hand Deburr (setup 1)', 'QC/ GAUGES AND FIXTURES', 'Hand Deburr (setup 2)', 'Buffing and Grinding',
        'Final Component QC/ Assembly checks', 'CFM (XXXX/ XX PCS)', 'Stress Relieving & Vacuum Hardening (XXXX DAYS )',
        'Cleaning (ACID WASH)', 'QC Checks', 'Cerakote'
    ],
    "MAG CASE": [
        'Blank Laser Cutting', 'L Bend', 'U Bend',  'Ribs Forming', 'Closing end Bend', 'Tig Welding',
        'Weld residue (inner side), oter rear face grinding and bottom extra portion grind', 'Rear face Grinding',
        'Filing', 'Slot Cutting', 'Restrike for feed lip correction', 'Rail Trimming', 'Belt Grinding', 'Buffing',
        'CFM', 'Cleaning with WD40', 'Feeding check with sample gun', 'Quality Checks', 'Cleaning with WD40',
        'Laser Serial Numbering', 'ENP Coating'
    ],
    "FRAME": [
        'DEBUR', 'POLISH', 'Polishing', 'VIBRATORY', 'Tapping', 'MAGNETIC', 'HARDANODISING'
    ],
    "Grip pannel": [
        'RM Cutting', 'Hand Deburr', 'Buffing', 'Vibratic', 'Cerakote'
    ],
    "CHASSIS": [
        'Material QC', 'Cutting to Size - QC', 'Stress Relieving', 'Hand Deburr (setup 1)', 'QC/ GAUGES AND FIXTURES',
        'Hand Deburr (setup 2)', 'QC/ GAUGES AND FIXTURES', 'Hand deburr', 'CFM', 'VMM',
        'Final Component QC/ Assembly checks', 'Tapping (3M tap)', 'Stress Relieving & Vacuum Hardening (XXXX DAYS )',
        'Cleaning (ACID WASH)', 'After Hardning Machining', 'Deburr', 'CFM', 'Cerakote', 'QC Checks',
        'Final Component QC/ Assembly checks'
    ],
    "SLD CVR": [
        "Checks", "Grinding", "Hand Deburr (setup 1)", "CFM (XXXX/ XX PCS)", "VMM",
        "Final Component QC/ Assembly checks", "Cleaning (ACID WASH)", "QC Checks"
    ],
    "FP": [
        "Material QC", "Cutting to Size - QC", "Hand Deburr (setup 1)", "QC/ GAUGES AND FIXTURES",
        "Grinding", "Hand Deburr (setup 2)", "QC/ GAUGES AND FIXTURESVMMCFM (XXXX/ XX PCS)",
        "Final Component QC/ Assembly checks"
    ],
    "EXTR": [
        "Material QC", "Cutting to Size - QC", "Hand Deburr (setup 1)", "Grinding & Buffing",
        "VMMFinal Component QC/ Assembly checks", "CFM (XXXX/ XX PCS)", "Cleaning (ACID WASH)", "QC Checks"
    ],
    "Detent": [
        "Hardening", "Machining", "Cutting", "Assembly Checks"
    ],
    "TDL": [
        "Material QC", "Cutting to Size - QC", "Stress Relieving", "Hand Deburr (setup 1)",
        "QC/ GAUGES AND FIXTURES", "Serial Marking", "Hand Deburr", "Buffing",
        "Final Component QC/ Assembly checks", "CFM (XXXX/ XX PCS)", "Cleaning (ACID WASH)",
        "QC ChecksFinal Component QC/ Assembly checks"
    ],
    "Others": [],
    "Checks":[
        "Feeding Checks","Pre-Firing Checks","Post-Firing Checks","Dispatch Checks"
    ],
    "Dispatch":[
        "Assembled Gun Dispatch","Hardening","Plating","Hardanodizing","QPQ","Wirecut"
    ],
    "Test":[
        "Calibration","Proof Test"
    ]

}

if __name__ == "__main__":
    main()
