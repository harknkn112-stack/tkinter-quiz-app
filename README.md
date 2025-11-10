# Python Tkinter Quiz Application

A comprehensive desktop quiz application built with Python, Tkinter, and SQLite3 that allows students to register, take timed quizzes, and view their performance results.

## 🚀 Features

### Core Functionality
- **Student Registration**: Collect student name and university with validation
- **Timed Quiz**: 10-question multiple-choice quiz with 10-minute countdown timer
- **Question Navigation**: Move between questions with Previous/Next buttons
- **Automatic Submission**: Quiz auto-submits when timer expires
- **Performance Results**: Detailed score breakdown and statistics
- **Answer Review**: Review all questions with correct/incorrect indicators
- **Comprehensive Logging**: Track all user actions and system events

### Technical Features
- **SQLite3 Database**: Persistent storage for questions and student data
- **Structured Logging**: Detailed event logging with rotation
- **Error Handling**: Robust error handling and user feedback
- **Validation**: Input validation and data integrity checks
- **Modular Design**: Clean separation of concerns with organized modules

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.7 or higher
- **Memory**: 512MB RAM minimum
- **Disk Space**: 50MB free space
- **Operating System**: Windows, macOS, or Linux

### Included Dependencies
- **Tkinter**: GUI framework (included with Python)
- **SQLite3**: Database engine (included with Python)
- **Standard Library**: All other dependencies are part of Python's standard library

## 🛠️ Installation

### Quick Start
1. **Download or clone** the application:
   ```bash
   git clone <repository-url>
   cd tkinter-quiz-app
   ```

2. **Check Python version**:
   ```bash
   python --version  # Should be 3.7 or higher
   ```

3. **Run the application**:
   ```bash
   python quiz_app.py
   ```

### Verify Installation
Check system dependencies before running:
```bash
python quiz_app.py --check-deps
```

## 📖 Usage Guide

### Running the Application

#### Basic Usage
```bash
# Start the quiz application
python quiz_app.py

# Show help and options
python quiz_app.py --help

# Check system dependencies
python quiz_app.py --check-deps

# Initialize application environment only
python quiz_app.py --setup
```

### Quiz Flow

#### 1. Registration
- Enter your **Full Name** (2-50 characters, letters and spaces only)
- Enter your **University** (2-100 characters, alphanumeric and common punctuation)
- Click **"Start Quiz"** to begin or **"Cancel"** to exit

#### 2. Taking the Quiz
- **Timer**: 10-minute countdown displayed prominently
- **Questions**: 10 multiple-choice questions (4 simple, 3 medium, 3 complex)
- **Navigation**: Use Previous/Next buttons or keyboard shortcuts
- **Answer Selection**: Click radio buttons or use number keys 1-4
- **Submission**: Click "End Exam" or wait for automatic submission

#### 3. Viewing Results
- **Score Display**: Total marks achieved out of possible marks
- **Performance Breakdown**: Correct, incorrect, and unanswered questions
- **Student Information**: Name, university, time taken, and exam date
- **Answer Review**: Detailed review of all questions and answers

### Keyboard Shortcuts

#### During Registration
- **Enter**: Submit registration form
- **Escape**: Cancel registration
- **Tab**: Navigate between fields

#### During Quiz
- **1-4**: Select answer options
- **Ctrl+Left Arrow**: Previous question
- **Ctrl+Right Arrow**: Next question
- **Ctrl+Enter**: Submit quiz

#### During Results
- **Escape**: Exit application
- **Ctrl+P**: Print results
- **Ctrl+R**: Review answers (if available)

## 📁 Project Structure

```
tkinter-quiz-app/
├── quiz_app.py              # Main application entry point
├── requirements.txt         # Dependencies (standard library only)
├── README.md               # This documentation file
├── database/               # Database management
│   ├── __init__.py
│   └── db_manager.py       # Database operations and schema
├── gui/                    # User interface components
│   ├── __init__.py
│   ├── main_app.py         # Main application controller
│   ├── registration.py     # Student registration screen
│   ├── quiz_screen.py      # Quiz interface
│   └── results.py          # Results display screen
├── models/                 # Data models
│   ├── __init__.py
│   ├── student.py          # Student data model
│   └── question.py         # Question data model
├── utils/                  # Utility modules
│   ├── __init__.py
│   ├── logger.py           # Logging configuration
│   ├── timer.py            # Quiz timer functionality
│   └── sample_data.py      # Sample questions for testing
├── quiz_database.db        # SQLite database (created on first run)
└── quiz_app.log           # Application log file
```

## 🗄️ Database Schema

### Questions Table
| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key, auto-increment |
| question | TEXT | Question text |
| option1 | TEXT | First answer choice |
| option2 | TEXT | Second answer choice |
| option3 | TEXT | Third answer choice |
| option4 | TEXT | Fourth answer choice |
| correct | TEXT | Correct answer |
| marks | INTEGER | Points awarded (1=Simple, 2=Medium, 3=Complex) |
| type | TEXT | Difficulty level ('simple', 'medium', 'complex') |

### Student Table
| Field | Type | Description |
|-------|------|-------------|
| usn | INTEGER | Primary key, auto-increment (Unique Student Number) |
| name | TEXT | Student name |
| university | TEXT | University name |
| date_of_exam | TEXT | Exam timestamp |
| marks_scored | INTEGER | Total marks achieved |

## 📊 Question Distribution

### Difficulty Levels
- **Simple Questions**: 4 questions × 1 mark = 4 marks
- **Medium Questions**: 3 questions × 2 marks = 6 marks
- **Complex Questions**: 3 questions × 3 marks = 9 marks
- **Total**: 10 questions = 19 possible marks

### Sample Questions
The application includes sample questions covering:
- Mathematics (basic arithmetic, algebra)
- General Knowledge (geography, history, science)
- Logic and Problem Solving

## 📝 Logging System

### Log File Location
- **Default**: `quiz_app.log` in application directory
- **Rotation**: 10MB maximum size, 5 backup files
- **Format**: `YYYY-MM-DD HH:MM:SS [LEVEL] Message`

### Logged Events
- **Student Registration**: Name, university, USN assignment
- **Quiz Start**: Student identification and timestamp
- **Navigation**: Question movement tracking
- **Answer Selection**: Selected answer logging
- **Submission**: Manual or automatic submission with score
- **Errors**: Database operations, GUI events, system errors

### Log Levels
- **INFO**: Normal application flow and user actions
- **ERROR**: Exception and error conditions
- **DEBUG**: Detailed development information

## 🔧 Configuration

### Customization Options

#### Timer Configuration
Edit `utils/timer.py` to modify:
- Quiz duration (default: 600 seconds = 10 minutes)
- Warning times (default: 120, 60, 30, 10 seconds)
- Display colors and formatting

#### Question Management
Edit `utils/sample_data.py` to:
- Add, modify, or remove questions
- Adjust difficulty distribution
- Change question categories

#### Logging Configuration
Edit `utils/logger.py` to:
- Change log file location
- Adjust log levels
- Modify log format
- Configure rotation settings

## 🧪 Testing

### Manual Testing
1. **Registration Testing**:
   - Valid input: Should proceed to quiz
   - Invalid input: Should show error messages
   - Empty fields: Should trigger validation errors

2. **Quiz Navigation Testing**:
   - Navigate through all questions
   - Use Previous/Next buttons
   - Test keyboard shortcuts
   - Verify answer saving

3. **Timer Testing**:
   - Verify countdown display
   - Test manual submission
   - Test automatic submission (use shorter timer for testing)

4. **Results Testing**:
   - Verify score calculation
   - Check result display accuracy
   - Test answer review functionality

### Running Tests
```bash
# Check system requirements
python quiz_app.py --check-deps

# Test with different question sets
# Modify sample_data.py and restart application
```

## 🐛 Troubleshooting

### Common Issues

#### Application Won't Start
1. **Check Python Version**: `python --version` (should be 3.7+)
2. **Check Tkinter**: `python -c "import tkinter"`
3. **File Permissions**: Ensure write access to application directory
4. **Disk Space**: Verify at least 50MB free space

#### Database Errors
1. **Delete Database File**: Remove `quiz_database.db` to recreate
2. **Check Permissions**: Ensure write access to directory
3. **Review Logs**: Check `quiz_app.log` for detailed error messages

#### GUI Display Issues
1. **Window Size**: Ensure screen resolution ≥ 800x600
2. **Tkinter Installation**: Reinstall Python with Tkinter support
3. **Display Scaling**: Check system display settings

#### Timer Issues
1. **System Time**: Verify system clock is accurate
2. **Background Processes**: Check for high CPU usage
3. **Threading**: Restart application if timer freezes

### Getting Help
1. **Check Logs**: Review `quiz_app.log` for error details
2. **System Check**: Run `python quiz_app.py --check-deps`
3. **Restart**: Close and restart the application
4. **Recreate Database**: Delete `quiz_database.db` and restart

## 🤝 Development

### Code Style
- **PEP 8 Compliance**: Follow Python style guidelines
- **Type Hints**: Use type annotations where appropriate
- **Documentation**: Include docstrings for all functions and classes
- **Error Handling**: Use try-catch blocks with proper logging

### Adding Features
1. **New Questions**: Edit `utils/sample_data.py`
2. **Additional Screens**: Create new files in `gui/` directory
3. **Database Changes**: Modify `database/db_manager.py`
4. **New Models**: Add files to `models/` directory

### Contributing
1. **Fork Repository**: Create your own version
2. **Make Changes**: Implement your features
3. **Test Thoroughly**: Ensure all functionality works
4. **Submit Pull Request**: Share your improvements

## 📄 License

This project is provided as-is for educational and development purposes. Feel free to modify and distribute according to your needs.

## 👥 Authors

- **Development Team**: Quiz Application Development Team
- **Version**: 1.0.0
- **Last Updated**: November 2024

---

## 📞 Support

For issues, questions, or contributions:
1. Check this README for solutions
2. Review the log files for error details
3. Test with the built-in dependency checker
4. Verify system requirements are met

**Thank you for using the Python Tkinter Quiz Application!**