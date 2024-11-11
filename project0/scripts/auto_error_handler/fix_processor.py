
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List

class FixProcessor:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def apply_fix(self, fix: Dict[str, Any], context: Dict[str, Any]) -> bool:
        if not self._validate_fix(fix):
            return False

        try:
            fix_type = fix.get('type')
            if fix_type == 'code_fix':
                return self._apply_code_fix(fix['file'], fix['changes'])
            elif fix_type == 'env_setup':
                return self._apply_env_setup(fix['commands'])
            else:
                self.logger.error(f"Unknown fix type: {fix_type}")
                return False
        except Exception as e:
            self.logger.error(f"Fix application failed: {str(e)}")
            return False

    def _validate_fix(self, fix: Dict[str, Any]) -> bool:
        required_fields = {
            'code_fix': ['file', 'changes'],
            'env_setup': ['commands']
        }

        fix_type = fix.get('type')
        if fix_type not in required_fields:
            return False

        for field in required_fields[fix_type]:
            if field not in fix:
                return False

            if field == 'changes' and not isinstance(fix['changes'], list):
                return False
            elif field == 'commands' and not isinstance(fix['commands'], list):
                return False

        return True

    def _apply_code_fix(self, file_path: str, changes: List[Dict[str, Any]]) -> bool:
        try:
            path = Path(file_path)
            if not path.exists():
                self.logger.error(f"File not found: {file_path}")
                return False

            with open(path, 'r') as file:
                lines = file.readlines()

            for change in changes:
                line_num = change.get('line', 0)
                new_code = change.get('code', '')
                if 0 <= line_num < len(lines):
                    lines[line_num] = new_code + '\n'

            with open(path, 'w') as file:
                file.writelines(lines)
            return True

        except Exception as e:
            self.logger.error(f"Code fix failed: {str(e)}")
            return False

    def _apply_env_setup(self, commands: List[str]) -> bool:
        try:
            for cmd in commands:
                self.logger.info(f"Running: {cmd}")
                subprocess.check_call(cmd, shell=True)
            return True
        except Exception as e:
            self.logger.error(f"Environment setup failed: {str(e)}")
            return False