"""
Analytics Module for Quiz Application
Provides comprehensive analytics and reporting functionality.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json


class QuizAnalytics:
    """Comprehensive analytics and reporting for quiz performance."""

    def __init__(self, db_path: str = "quiz_database.db"):
        """
        Initialize analytics system.

        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
        self.connection = None
        self.connect_to_database()

    def connect_to_database(self) -> None:
        """Connect to the quiz database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable dictionary-like access
        except Exception as e:
            raise Exception(f"Failed to connect to database: {e}")

    def close_connection(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()

    def get_all_student_results(self) -> List[Dict[str, Any]]:
        """
        Get all student quiz results.

        Returns:
            List of student result dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT usn, name, university, date_of_exam, marks_scored
                FROM Student
                ORDER BY date_of_exam DESC
            """)

            results = []
            for row in cursor.fetchall():
                results.append(dict(row))

            return results
        except Exception as e:
            raise Exception(f"Failed to get student results: {e}")

    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        Get overall performance statistics.

        Returns:
            Dictionary with performance statistics
        """
        try:
            cursor = self.connection.cursor()

            # Basic statistics
            cursor.execute("SELECT COUNT(*) as total_students FROM Student")
            total_students = cursor.fetchone()['total_students']

            cursor.execute("SELECT AVG(marks_scored) as avg_score FROM Student WHERE marks_scored > 0")
            avg_score_result = cursor.fetchone()
            avg_score = avg_score_result['avg_score'] if avg_score_result['avg_score'] else 0

            cursor.execute("SELECT MAX(marks_scored) as max_score FROM Student")
            max_score = cursor.fetchone()['max_score'] or 0

            cursor.execute("SELECT MIN(marks_scored) as min_score FROM Student WHERE marks_scored > 0")
            min_score_result = cursor.fetchone()
            min_score = min_score_result['min_score'] if min_score_result['min_score'] else 0

            # Score distribution
            cursor.execute("""
                SELECT
                    CASE
                        WHEN marks_scored >= 16 THEN 'Excellent (80%+)'
                        WHEN marks_scored >= 12 THEN 'Good (60-79%)'
                        WHEN marks_scored >= 8 THEN 'Satisfactory (40-59%)'
                        ELSE 'Needs Improvement (<40%)'
                    END as performance_level,
                    COUNT(*) as count
                FROM Student
                WHERE marks_scored > 0
                GROUP BY performance_level
                ORDER BY marks_scored DESC
            """)

            score_distribution = {}
            for row in cursor.fetchall():
                score_distribution[row['performance_level']] = row['count']

            return {
                'total_students': total_students,
                'average_score': round(avg_score, 2),
                'highest_score': max_score,
                'lowest_score': min_score,
                'score_distribution': score_distribution,
                'participation_rate': total_students
            }
        except Exception as e:
            raise Exception(f"Failed to get performance statistics: {e}")

    def get_top_performers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top performing students.

        Args:
            limit: Maximum number of students to return

        Returns:
            List of top performer dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT usn, name, university, date_of_exam, marks_scored
                FROM Student
                WHERE marks_scored > 0
                ORDER BY marks_scored DESC, date_of_exam ASC
                LIMIT ?
            """, (limit,))

            top_performers = []
            for i, row in enumerate(cursor.fetchall(), 1):
                performer = dict(row)
                performer['rank'] = i
                top_performers.append(performer)

            return top_performers
        except Exception as e:
            raise Exception(f"Failed to get top performers: {e}")

    def get_university_performance(self) -> List[Dict[str, Any]]:
        """
        Get performance statistics by university.

        Returns:
            List of university performance dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT
                    university,
                    COUNT(*) as student_count,
                    AVG(marks_scored) as avg_score,
                    MAX(marks_scored) as max_score,
                    MIN(marks_scored) as min_score
                FROM Student
                WHERE marks_scored > 0
                GROUP BY university
                ORDER BY avg_score DESC
            """)

            university_stats = []
            for row in cursor.fetchall():
                university_stats.append({
                    'university': row['university'],
                    'student_count': row['student_count'],
                    'average_score': round(row['avg_score'], 2),
                    'highest_score': row['max_score'],
                    'lowest_score': row['min_score']
                })

            return university_stats
        except Exception as e:
            raise Exception(f"Failed to get university performance: {e}")

    def get_daily_activity(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily quiz activity for specified number of days.

        Args:
            days: Number of days to look back

        Returns:
            List of daily activity dictionaries
        """
        try:
            cursor = self.connection.cursor()

            # Get activity for the last N days
            cursor.execute(f"""
                SELECT
                    DATE(date_of_exam) as exam_date,
                    COUNT(*) as students_count,
                    AVG(marks_scored) as avg_score,
                    MAX(marks_scored) as max_score
                FROM Student
                WHERE date_of_exam >= DATE('now', '-{days} days')
                GROUP BY DATE(date_of_exam)
                ORDER BY exam_date DESC
            """)

            daily_activity = []
            for row in cursor.fetchall():
                daily_activity.append({
                    'date': row['exam_date'],
                    'students_count': row['students_count'],
                    'average_score': round(row['avg_score'], 2) if row['avg_score'] else 0,
                    'highest_score': row['max_score'] or 0
                })

            return daily_activity
        except Exception as e:
            raise Exception(f"Failed to get daily activity: {e}")

    def get_recent_activity(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get recent quiz activity.

        Args:
            hours: Number of hours to look back

        Returns:
            List of recent activity dictionaries
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"""
                SELECT usn, name, university, date_of_exam, marks_scored
                FROM Student
                WHERE date_of_exam >= datetime('now', '-{hours} hours')
                ORDER BY date_of_exam DESC
            """)

            recent_activity = []
            for row in cursor.fetchall():
                recent_activity.append(dict(row))

            return recent_activity
        except Exception as e:
            raise Exception(f"Failed to get recent activity: {e}")

    def export_analytics_to_json(self, file_path: str = None) -> str:
        """
        Export all analytics data to JSON format.

        Args:
            file_path: Optional file path to save JSON

        Returns:
            JSON string with all analytics data
        """
        try:
            analytics_data = {
                'export_date': datetime.now().isoformat(),
                'performance_statistics': self.get_performance_statistics(),
                'top_performers': self.get_top_performers(),
                'university_performance': self.get_university_performance(),
                'daily_activity': self.get_daily_activity(30),
                'recent_activity': self.get_recent_activity(24),
                'all_results': self.get_all_student_results()
            }

            json_data = json.dumps(analytics_data, indent=2, default=str)

            if file_path:
                with open(file_path, 'w') as f:
                    f.write(json_data)

            return json_data
        except Exception as e:
            raise Exception(f"Failed to export analytics: {e}")

    def generate_performance_report(self) -> str:
        """
        Generate a comprehensive performance report.

        Returns:
            Formatted report string
        """
        try:
            stats = self.get_performance_statistics()
            top_performers = self.get_top_performers(5)
            university_stats = self.get_university_performance()

            report = []
            report.append("=" * 60)
            report.append("QUIZ APPLICATION PERFORMANCE REPORT")
            report.append("=" * 60)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")

            # Overall Statistics
            report.append("OVERALL STATISTICS")
            report.append("-" * 30)
            report.append(f"Total Students: {stats['total_students']}")
            report.append(f"Average Score: {stats['average_score']:.2f}")
            report.append(f"Highest Score: {stats['highest_score']}")
            report.append(f"Lowest Score: {stats['lowest_score']}")
            report.append("")

            # Score Distribution
            report.append("SCORE DISTRIBUTION")
            report.append("-" * 30)
            for level, count in stats['score_distribution'].items():
                report.append(f"{level}: {count} students")
            report.append("")

            # Top Performers
            if top_performers:
                report.append("TOP PERFORMERS")
                report.append("-" * 30)
                for performer in top_performers:
                    report.append(f"{performer['rank']}. {performer['name']} ({performer['university']}) - {performer['marks_scored']} points")
                report.append("")

            # University Performance
            if university_stats:
                report.append("UNIVERSITY PERFORMANCE")
                report.append("-" * 30)
                for uni_stat in university_stats:
                    report.append(f"{uni_stat['university']}:")
                    report.append(f"  Students: {uni_stat['student_count']}")
                    report.append(f"  Average: {uni_stat['average_score']:.2f}")
                    report.append(f"  Range: {uni_stat['lowest_score']}-{uni_stat['highest_score']}")
                report.append("")

            report.append("=" * 60)

            return "\n".join(report)
        except Exception as e:
            raise Exception(f"Failed to generate performance report: {e}")

    def get_student_performance_trend(self, student_name: str) -> List[Dict[str, Any]]:
        """
        Get performance trend for a specific student.

        Args:
            student_name: Name of the student

        Returns:
            List of student's quiz results over time
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT usn, name, university, date_of_exam, marks_scored
                FROM Student
                WHERE name LIKE ?
                ORDER BY date_of_exam ASC
            """, (f"%{student_name}%",))

            student_results = []
            for row in cursor.fetchall():
                student_results.append(dict(row))

            return student_results
        except Exception as e:
            raise Exception(f"Failed to get student performance trend: {e}")

    def calculate_success_metrics(self) -> Dict[str, Any]:
        """
        Calculate success metrics and KPIs.

        Returns:
            Dictionary with success metrics
        """
        try:
            stats = self.get_performance_statistics()

            # Calculate success rate (students scoring above 50%)
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) as success_count
                FROM Student
                WHERE marks_scored >= 10  # 50% of 19 possible marks
            """)

            success_count = cursor.fetchone()['success_count']
            success_rate = (success_count / stats['total_students'] * 100) if stats['total_students'] > 0 else 0

            # Calculate engagement rate (students who completed vs started)
            # This assumes all students in the table completed the quiz
            engagement_rate = 100.0  # All records are completed quizzes

            return {
                'success_rate': round(success_rate, 2),
                'engagement_rate': engagement_rate,
                'average_performance': round((stats['average_score'] / 19) * 100, 2),  # Convert to percentage
                'high_performers_rate': round((stats['score_distribution'].get('Excellent (80%+)', 0) / stats['total_students']) * 100, 2) if stats['total_students'] > 0 else 0
            }
        except Exception as e:
            raise Exception(f"Failed to calculate success metrics: {e}")


def get_analytics() -> QuizAnalytics:
    """
    Get analytics instance.

    Returns:
        QuizAnalytics instance
    """
    return QuizAnalytics()