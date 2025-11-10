#!/usr/bin/env python3
"""
Test Configuration Integration
Tests the configuration system integration with various components.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, '.')

def test_configuration_imports():
    """Test that all modules can import configuration properly."""
    print("Testing configuration imports...")

    try:
        from quiz_config import get_config, update_config, reset_config
        config = get_config()
        print("✓ quiz_config imports successfully")
        print(f"  Default duration: {config.quiz_duration_minutes} minutes")
        print(f"  Default questions: {config.total_questions}")
        print(f"  Face monitoring: {config.enable_face_monitoring}")
    except Exception as e:
        print(f"✗ Failed to import quiz_config: {e}")
        return False

    try:
        # Test importing from gui modules (without initializing Tkinter)
        sys.path.insert(0, 'gui')

        # Mock tkinter to avoid import errors
        import unittest.mock

        with unittest.mock.patch('tkinter'):
            with unittest.mock.patch('tkinter.ttk'):
                with unittest.mock.patch('tkinter.messagebox'):
                    # Test that main_app can import config
                    import main_app
                    print("✓ main_app imports configuration successfully")

                    # Test quiz_screen configuration import
                    import quiz_screen
                    print("✓ quiz_screen imports configuration successfully")

    except Exception as e:
        print(f"✗ Failed to import GUI modules with configuration: {e}")
        return False

    return True


def test_configuration_updates():
    """Test configuration updates and validation."""
    print("\nTesting configuration updates...")

    try:
        from quiz_config import update_config, get_config, reset_config

        # Test updating basic settings
        update_config(quiz_duration_minutes=15, total_questions=12)
        config = get_config()

        assert config.quiz_duration_minutes == 15, f"Expected 15, got {config.quiz_duration_minutes}"
        assert config.total_questions == 12, f"Expected 12, got {config.total_questions}"
        print("✓ Basic configuration updates work")

        # Test updating face monitoring settings
        update_config(
            enable_face_monitoring=False,
            camera_index=1,
            face_detection_interval=2.0
        )
        config = get_config()

        assert config.enable_face_monitoring == False, "Face monitoring should be disabled"
        assert config.camera_index == 1, f"Expected camera index 1, got {config.camera_index}"
        assert config.face_detection_interval == 2.0, f"Expected 2.0s interval, got {config.face_detection_interval}"
        print("✓ Face monitoring configuration updates work")

        # Test timer warnings
        update_config(timer_warning_times=[300, 180, 60, 30, 10])
        config = get_config()

        expected_warnings = [300, 180, 60, 30, 10]
        assert config.timer_warning_times == expected_warnings, f"Expected {expected_warnings}, got {config.timer_warning_times}"
        print("✓ Timer warning configuration updates work")

    except Exception as e:
        print(f"✗ Configuration update test failed: {e}")
        return False
    finally:
        # Reset to defaults
        try:
            from quiz_config import reset_config
            reset_config()
        except:
            pass

    return True


def test_configuration_persistence():
    """Test that configuration is saved and loaded properly."""
    print("\nTesting configuration persistence...")

    try:
        from quiz_config import update_config, get_config, reset_config, ConfigurationManager

        # Update configuration
        update_config(quiz_duration_minutes=20, total_questions=8)

        # Create new configuration manager instance
        new_manager = ConfigurationManager()
        loaded_config = new_manager.get_config()

        assert loaded_config.quiz_duration_minutes == 20, f"Expected 20, got {loaded_config.quiz_duration_minutes}"
        assert loaded_config.total_questions == 8, f"Expected 8, got {loaded_config.total_questions}"
        print("✓ Configuration persistence works")

    except Exception as e:
        print(f"✗ Configuration persistence test failed: {e}")
        return False
    finally:
        # Reset to defaults
        try:
            from quiz_config import reset_config
            reset_config()
        except:
            pass

    return True


def test_configuration_validation():
    """Test configuration validation."""
    print("\nTesting configuration validation...")

    try:
        from quiz_config import update_config, get_config
        import tempfile
        import json

        # Test that invalid values are caught
        try:
            update_config(quiz_duration_minutes=-5)
            print("✗ Should have failed with negative duration")
            return False
        except (ValueError, AssertionError):
            print("✓ Negative duration validation works")

        try:
            update_config(total_questions=0)
            print("✗ Should have failed with zero questions")
            return False
        except (ValueError, AssertionError):
            print("✓ Zero questions validation works")

        try:
            update_config(camera_index=-1)
            print("✗ Should have failed with negative camera index")
            return False
        except (ValueError, AssertionError):
            print("✓ Negative camera index validation works")

    except Exception as e:
        print(f"✗ Configuration validation test failed: {e}")
        return False
    finally:
        # Reset to defaults
        try:
            from quiz_config import reset_config
            reset_config()
        except:
            pass

    return True


def main():
    """Run all configuration tests."""
    print("QUIZ APPLICATION CONFIGURATION TESTS")
    print("=" * 50)

    tests = [
        test_configuration_imports,
        test_configuration_updates,
        test_configuration_persistence,
        test_configuration_validation
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print(f"\n{'='*50}")
    print(f"TESTS PASSED: {passed}/{total}")

    if passed == total:
        print("✓ All configuration tests passed!")
        print("✓ Configuration system is working correctly!")
        return 0
    else:
        print("✗ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())