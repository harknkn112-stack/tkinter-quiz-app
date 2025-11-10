"""
Analytics Screen for Quiz Application
Provides comprehensive analytics and reporting functionality.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Callable
import json
from datetime import datetime
from utils.analytics import QuizAnalytics
from utils.logger import get_logger


class AnalyticsScreen:
    """Analytics screen for displaying quiz performance data and reports."""

    def __init__(self, master: tk.Tk,
                 on_back: Optional[Callable[[], None]] = None):
        """
        Initialize analytics screen.

        Args:
            master: Parent tkinter window
            on_back: Callback when user wants to go back
        """
        self.master = master
        self.on_back = on_back
        self.logger = get_logger()
        self.analytics = QuizAnalytics()

        # Create analytics frame
        self.frame = ttk.Frame(master, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Configure styles
        self.setup_styles()

        # Create widgets
        self.create_widgets()

        # Load initial data
        self.refresh_analytics()

    def setup_styles(self) -> None:
        """Configure ttk styles for the analytics screen."""
        style = ttk.Style()

        # Title style
        style.configure("Analytics.TLabel",
                       font=("Arial", 16, "bold"),
                       foreground="#2c3e50")

        # Section header style
        style.configure("Section.TLabel",
                       font=("Arial", 12, "bold"),
                       foreground="#34495e")

        # Button styles
        style.configure("Action.TButton",
                       font=("Arial", 10, "bold"),
                       padding=(15, 8))

        style.configure("Export.TButton",
                       font=("Arial", 10),
                       padding=(12, 6))

    def create_widgets(self) -> None:
        """Create all widgets for the analytics screen."""
        # Main container with notebook for tabs
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_container,
            text="Quiz Analytics Dashboard",
            style="Analytics.TLabel"
        )
        title_label.pack(pady=(0, 20))

        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Create tabs
        self.create_overview_tab()
        self.create_performance_tab()
        self.create_universities_tab()
        self.create_activity_tab()
        self.create_exports_tab()

        # Bottom button frame
        self.create_button_frame(main_container)

    def create_overview_tab(self) -> None:
        """Create overview statistics tab."""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Overview")

        # Scrollable frame for overview
        canvas = tk.Canvas(overview_frame, bg="white")
        scrollbar = ttk.Scrollbar(overview_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Overview statistics widgets
        self.overview_stats_frame = ttk.LabelFrame(scrollable_frame, text="Overall Statistics", padding="20")
        self.overview_stats_frame.pack(fill=tk.X, padx=20, pady=20)

        self.overview_labels = {}
        self.create_overview_widgets()

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_overview_widgets(self) -> None:
        """Create overview statistics widgets."""
        stats_to_show = [
            ("total_students", "Total Students", "0"),
            ("average_score", "Average Score", "0.0"),
            ("highest_score", "Highest Score", "0"),
            ("lowest_score", "Lowest Score", "0"),
            ("success_rate", "Success Rate (>50%)", "0.0%"),
            ("engagement_rate", "Engagement Rate", "100.0%")
        ]

        for i, (key, label, default) in enumerate(stats_to_show):
            row_frame = ttk.Frame(self.overview_stats_frame)
            row_frame.pack(fill=tk.X, pady=5)

            label_widget = ttk.Label(row_frame, text=f"{label}:", font=("Arial", 11, "bold"), width=20)
            label_widget.pack(side=tk.LEFT)

            value_widget = ttk.Label(row_frame, text=default, font=("Arial", 11))
            value_widget.pack(side=tk.LEFT)

            self.overview_labels[key] = value_widget

    def create_performance_tab(self) -> None:
        """Create performance analysis tab."""
        performance_frame = ttk.Frame(self.notebook)
        self.notebook.add(performance_frame, text="Performance")

        # Top performers section
        top_frame = ttk.LabelFrame(performance_frame, text="Top Performers", padding="20")
        top_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Treeview for top performers
        columns = ("Rank", "Name", "University", "Score", "Date")
        self.top_performers_tree = ttk.Treeview(top_frame, columns=columns, show="headings", height=10)

        # Configure columns
        for col in columns:
            self.top_performers_tree.heading(col, text=col)
            self.top_performers_tree.column(col, width=120)

        self.top_performers_tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(top_frame, orient="vertical", command=self.top_performers_tree.yview)
        tree_scrollbar.pack(side="right", fill="y")
        self.top_performers_tree.configure(yscrollcommand=tree_scrollbar.set)

    def create_universities_tab(self) -> None:
        """Create university performance tab."""
        universities_frame = ttk.Frame(self.notebook)
        self.notebook.add(universities_frame, text="Universities")

        # University performance section
        uni_frame = ttk.LabelFrame(universities_frame, text="University Performance", padding="20")
        uni_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Treeview for university stats
        columns = ("University", "Students", "Average", "Highest", "Lowest")
        self.university_tree = ttk.Treeview(uni_frame, columns=columns, show="headings", height=10)

        # Configure columns
        self.university_tree.heading("University", text="University")
        self.university_tree.heading("Students", text="Students")
        self.university_tree.heading("Average", text="Avg Score")
        self.university_tree.heading("Highest", text="Highest")
        self.university_tree.heading("Lowest", text="Lowest")

        self.university_tree.column("University", width=200)
        self.university_tree.column("Students", width=100)
        self.university_tree.column("Average", width=100)
        self.university_tree.column("Highest", width=100)
        self.university_tree.column("Lowest", width=100)

        self.university_tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for treeview
        uni_scrollbar = ttk.Scrollbar(uni_frame, orient="vertical", command=self.university_tree.yview)
        uni_scrollbar.pack(side="right", fill="y")
        self.university_tree.configure(yscrollcommand=uni_scrollbar.set)

    def create_activity_tab(self) -> None:
        """Create activity timeline tab."""
        activity_frame = ttk.Frame(self.notebook)
        self.notebook.add(activity_frame, text="Activity")

        # Daily activity section
        daily_frame = ttk.LabelFrame(activity_frame, text="Recent Activity (Last 30 Days)", padding="20")
        daily_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Treeview for daily activity
        columns = ("Date", "Students", "Average Score", "Highest Score")
        self.activity_tree = ttk.Treeview(daily_frame, columns=columns, show="headings", height=10)

        # Configure columns
        self.activity_tree.heading("Date", text="Date")
        self.activity_tree.heading("Students", text="Students")
        self.activity_tree.heading("Average Score", text="Avg Score")
        self.activity_tree.heading("Highest Score", text="Highest")

        self.activity_tree.column("Date", width=120)
        self.activity_tree.column("Students", width=100)
        self.activity_tree.column("Average Score", width=120)
        self.activity_tree.column("Highest Score", width=100)

        self.activity_tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for treeview
        activity_scrollbar = ttk.Scrollbar(daily_frame, orient="vertical", command=self.activity_tree.yview)
        activity_scrollbar.pack(side="right", fill="y")
        self.activity_tree.configure(yscrollcommand=activity_scrollbar.set)

    def create_exports_tab(self) -> None:
        """Create exports and reports tab."""
        exports_frame = ttk.Frame(self.notebook)
        self.notebook.add(exports_frame, text="Reports")

        # Report generation section
        report_frame = ttk.LabelFrame(exports_frame, text="Generate Reports", padding="20")
        report_frame.pack(fill=tk.X, padx=20, pady=20)

        # Buttons for different reports
        button_container = ttk.Frame(report_frame)
        button_container.pack(fill=tk.X)

        ttk.Button(
            button_container,
            text="Generate Performance Report",
            style="Action.TButton",
            command=self.generate_performance_report
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_container,
            text="Export to JSON",
            style="Export.TButton",
            command=self.export_to_json
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_container,
            text="Print Report",
            style="Export.TButton",
            command=self.print_report
        ).pack(side=tk.LEFT)

        # Text area for displaying reports
        text_frame = ttk.LabelFrame(exports_frame, text="Report Preview", padding="20")
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.report_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Courier", 10)
        )
        self.report_text.pack(fill=tk.BOTH, expand=True)

    def create_button_frame(self, parent: ttk.Frame) -> None:
        """Create bottom button frame."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        # Refresh button
        ttk.Button(
            button_frame,
            text="Refresh Data",
            style="Action.TButton",
            command=self.refresh_analytics
        ).pack(side=tk.LEFT)

        # Back button
        if self.on_back:
            ttk.Button(
                button_frame,
                text="Back to Main",
                command=self.on_back_clicked
            ).pack(side=tk.RIGHT)

    def refresh_analytics(self) -> None:
        """Refresh all analytics data."""
        try:
            # Update overview statistics
            self.update_overview_statistics()

            # Update top performers
            self.update_top_performers()

            # Update university performance
            self.update_university_performance()

            # Update activity data
            self.update_activity_data()

            self.logger.info("Analytics data refreshed successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh analytics: {e}")
            self.logger.log_application_error(e, "refresh_analytics")

    def update_overview_statistics(self) -> None:
        """Update overview statistics display."""
        try:
            stats = self.analytics.get_performance_statistics()
            metrics = self.analytics.calculate_success_metrics()

            # Update labels
            self.overview_labels["total_students"].config(text=str(stats['total_students']))
            self.overview_labels["average_score"].config(text=f"{stats['average_score']:.2f}")
            self.overview_labels["highest_score"].config(text=str(stats['highest_score']))
            self.overview_labels["lowest_score"].config(text=str(stats['lowest_score']))
            self.overview_labels["success_rate"].config(text=f"{metrics['success_rate']:.1f}%")
            self.overview_labels["engagement_rate"].config(text=f"{metrics['engagement_rate']:.1f}%")

        except Exception as e:
            raise Exception(f"Failed to update overview statistics: {e}")

    def update_top_performers(self) -> None:
        """Update top performers display."""
        try:
            # Clear existing items
            for item in self.top_performers_tree.get_children():
                self.top_performers_tree.delete(item)

            # Add top performers
            top_performers = self.analytics.get_top_performers(20)
            for performer in top_performers:
                self.top_performers_tree.insert("", tk.END, values=(
                    performer['rank'],
                    performer['name'],
                    performer['university'],
                    performer['marks_scored'],
                    performer['date_of_exam']
                ))

        except Exception as e:
            raise Exception(f"Failed to update top performers: {e}")

    def update_university_performance(self) -> None:
        """Update university performance display."""
        try:
            # Clear existing items
            for item in self.university_tree.get_children():
                self.university_tree.delete(item)

            # Add university statistics
            university_stats = self.analytics.get_university_performance()
            for uni_stat in university_stats:
                self.university_tree.insert("", tk.END, values=(
                    uni_stat['university'],
                    uni_stat['student_count'],
                    f"{uni_stat['average_score']:.2f}",
                    uni_stat['highest_score'],
                    uni_stat['lowest_score']
                ))

        except Exception as e:
            raise Exception(f"Failed to update university performance: {e}")

    def update_activity_data(self) -> None:
        """Update activity timeline display."""
        try:
            # Clear existing items
            for item in self.activity_tree.get_children():
                self.activity_tree.delete(item)

            # Add daily activity
            daily_activity = self.analytics.get_daily_activity(30)
            for activity in daily_activity:
                self.activity_tree.insert("", tk.END, values=(
                    activity['date'],
                    activity['students_count'],
                    f"{activity['average_score']:.2f}",
                    activity['highest_score']
                ))

        except Exception as e:
            raise Exception(f"Failed to update activity data: {e}")

    def generate_performance_report(self) -> None:
        """Generate and display performance report."""
        try:
            report = self.analytics.generate_performance_report()
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(1.0, report)

            # Switch to reports tab
            self.notebook.select(4)  # Reports tab is index 4

            self.logger.info("Performance report generated")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")

    def export_to_json(self) -> None:
        """Export analytics data to JSON file."""
        try:
            from tkinter import filedialog

            file_path = filedialog.asksaveasfilename(
                title="Export Analytics Data",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if file_path:
                self.analytics.export_analytics_to_json(file_path)
                messagebox.showinfo("Export Successful", f"Analytics exported to {file_path}")
                self.logger.info(f"Analytics exported to {file_path}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export analytics: {e}")

    def print_report(self) -> None:
        """Print the current report."""
        try:
            report_content = self.report_text.get(1.0, tk.END).strip()
            if not report_content:
                messagebox.showwarning("No Report", "Please generate a report first.")
                return

            # Simple print functionality (would need actual printing implementation)
            messagebox.showinfo("Print", "Print functionality would be implemented here.\n\nReport has been prepared for printing.")
            self.logger.info("Report printing requested")

        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print report: {e}")

    def on_back_clicked(self) -> None:
        """Handle back button click."""
        try:
            self.analytics.close_connection()
            if self.on_back:
                self.on_back()
        except Exception as e:
            self.logger.log_application_error(e, "analytics_back")

    def get_frame(self) -> ttk.Frame:
        """
        Get the main frame widget.

        Returns:
            Main analytics frame
        """
        return self.frame

    def show_frame(self) -> None:
        """Show the analytics frame."""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide_frame(self) -> None:
        """Hide the analytics frame."""
        self.frame.pack_forget()