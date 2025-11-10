# Quiz Application Configuration Guide

## Overview

The Quiz Application now includes a comprehensive configuration system that allows you to customize quiz parameters without modifying the source code. The configuration is stored in `quiz_config.json` and can be easily modified or programmatically updated.

## Configuration File

The configuration is automatically created and managed in `quiz_config.json`. You can edit this file directly or use the provided Python API.

## Key Configuration Options

### Timer Settings
- **quiz_duration_minutes**: Total quiz time in minutes (default: 10)
- **timer_warning_times**: List of seconds before end to show warnings (default: [120, 60, 30, 10])
- **auto_submit_on_timeout**: Automatically submit when timer expires (default: true)

### Question Settings
- **total_questions**: Number of questions in the quiz (default: 10)
- **question_distribution**: Questions by difficulty (default: {"simple": 4, "medium": 3, "complex": 3})
- **enable_question_randomization**: Randomize question order (default: true)

### Face Monitoring
- **enable_face_monitoring**: Enable/disable face detection (default: true)
- **camera_index**: Camera device to use (default: 0)
- **face_detection_interval**: Seconds between face checks (default: 1.0)
- **face_absence_threshold**: Consecutive misses before alerting (default: 3)

### UI Settings
- **window_width/height**: Window dimensions (default: 800x600)
- **show_progress_indicator**: Show question progress (default: true)
- **show_question_counter**: Show "Question X of Y" (default: true)

## How to Use

### Method 1: Edit the JSON File Directly

Simply open `quiz_config.json` and modify the values:

```json
{
  "quiz_duration_minutes": 15,
  "total_questions": 12,
  "enable_face_monitoring": false,
  "timer_warning_times": [300, 180, 60, 30, 10]
}
```

### Method 2: Use the Python API

```python
from quiz_config import update_config, get_config

# Update configuration
update_config(
    quiz_duration_minutes=15,
    total_questions=12,
    enable_face_monitoring=False
)

# Get current configuration
config = get_config()
print(f"Duration: {config.quiz_duration_minutes} minutes")
```

### Method 3: Environment Variables

You can set configuration via environment variables:

```bash
export QUIZ_DURATION_MINUTES=20
export TOTAL_QUESTIONS=15
export ENABLE_FACE_MONITORING=false

python quiz_app.py
```

## Common Configuration Scenarios

### Longer Quiz (20 minutes, 15 questions)
```python
update_config(
    quiz_duration_minutes=20,
    total_questions=15,
    question_distribution={'simple': 6, 'medium': 5, 'complex': 4},
    timer_warning_times=[300, 180, 120, 60, 30, 10]
)
```

### Short Quiz (5 minutes, 5 questions)
```python
update_config(
    quiz_duration_minutes=5,
    total_questions=5,
    question_distribution={'simple': 2, 'medium': 2, 'complex': 1},
    timer_warning_times=[60, 30, 10]
)
```

### Disable Face Monitoring
```python
update_config(
    enable_face_monitoring=False
)
```

### Custom Timer Warnings
```python
update_config(
    timer_warning_times=[600, 300, 120, 60, 30, 10, 5]  # Warnings at 10min, 5min, 2min, 1min, 30sec, 10sec, 5sec
)
```

## Configuration Validation

The system validates configuration values:
- Quiz duration must be positive
- Total questions must be positive
- Camera index must be non-negative
- Window dimensions must be reasonable

## Resetting Configuration

To reset to default values:

```python
from quiz_config import reset_config
reset_config()
```

## Viewing Current Configuration

```python
from quiz_config import get_config, export_config_summary

config = get_config()
print("Current configuration:")
print(config.__dict__)

# Or get a formatted summary
print(export_config_summary())
```

## Important Notes

1. **Question Distribution**: The sum of `question_distribution` should equal `total_questions`
2. **Face Monitoring**: Requires a camera and OpenCV. Will be automatically disabled if not available.
3. **Timer Warnings**: Times are in seconds before the quiz ends
4. **Database**: The configuration affects how many questions are loaded from the database

## Troubleshooting

### Configuration Not Loading
- Ensure `quiz_config.json` is readable and valid JSON
- Check that the application has permission to write to the file

### Face Monitoring Issues
- Set `enable_face_monitoring: false` if camera is not available
- Check `camera_index` value if using multiple cameras

### Timer Warnings Not Showing
- Verify `timer_warning_times` contains the desired seconds
- Ensure `show_timer_countdown` is enabled

## Example Configuration Files

### Testing Configuration
```json
{
  "quiz_duration_minutes": 1,
  "total_questions": 3,
  "enable_face_monitoring": false,
  "enable_question_randomization": false,
  "auto_submit_on_timeout": true
}
```

### Production Configuration
```json
{
  "quiz_duration_minutes": 10,
  "total_questions": 10,
  "enable_face_monitoring": true,
  "camera_index": 0,
  "face_detection_interval": 1.0,
  "face_absence_threshold": 3,
  "timer_warning_times": [120, 60, 30, 10],
  "auto_submit_on_timeout": true,
  "window_width": 800,
  "window_height": 600
}
```

### Accessibility Configuration
```json
{
  "quiz_duration_minutes": 20,
  "total_questions": 8,
  "enable_face_monitoring": false,
  "show_marks_per_question": true,
  "timer_warning_times": [600, 300, 180, 120, 60, 30],
  "window_width": 1000,
  "window_height": 700
}
```