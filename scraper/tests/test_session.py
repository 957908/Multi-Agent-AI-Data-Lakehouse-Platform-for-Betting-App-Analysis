"""
File: test_session.py
Purpose:
    Unit tests for SessionManager persistence.
Author: R. Rayri Sharma
Company: SentinelX Labs
Project: SentinelX Trust AI – Multi-Agent AI Data Lakehouse Platform for Betting Site Intelligence
Created By: R. Rayri Sharma
Reviewed By: Tech Lead & Solution Architect (HQ Chat)
Version: 1.2
"""

# Standard Library
import sys
import unittest
from pathlib import Path

# Add scraper/scraper to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "scraper"))

# Local Imports
from core.session import SessionManager


class TestSessionManager(unittest.TestCase):
    """
    Test suite for SessionManager.
    """

    def test_session_manager_save_and_clear(self):
        """
        Verifies that SessionManager can identify state paths, 
        check session existence, and clear stored session files.
        """
        manager = SessionManager(session_dir="tests/test_auth")
        site = "test_site"
        
        try:
            # Initial check should be false
            self.assertFalse(manager.has_session(site))
            
            # Check standard path naming using Path comparison
            expected_path = Path("tests/test_auth") / f"{site}_state.json"
            self.assertEqual(Path(manager.get_state_path(site)).resolve(), expected_path.resolve())
            
            # Simulate creating a state file
            state_file = expected_path
            state_file.parent.mkdir(parents=True, exist_ok=True)
            state_file.write_text('{"cookies": []}', encoding="utf-8")
            
            self.assertTrue(manager.has_session(site))
            
            # Clear the state file
            manager.clear_session(site)
            self.assertFalse(manager.has_session(site))
            self.assertFalse(state_file.exists())
            
        finally:
            # Cleanup test directory
            test_dir = Path("tests/test_auth")
            if test_dir.exists():
                for f in test_dir.iterdir():
                    f.unlink()
                test_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
