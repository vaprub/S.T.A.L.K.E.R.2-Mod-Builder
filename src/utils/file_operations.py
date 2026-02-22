"""File and directory operation utilities"""

import shutil
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

def ensure_directory(path: Path) -> bool:
    """Ensure a directory exists"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False

def copy_file(source: Path, destination: Path) -> bool:
    """Copy a file to destination"""
    try:
        ensure_directory(destination.parent)
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        logger.error(f"Failed to copy {source} to {destination}: {e}")
        return False

def copy_directory(source: Path, destination: Path) -> bool:
    """Copy entire directory tree"""
    try:
        if destination.exists():
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
        return True
    except Exception as e:
        logger.error(f"Failed to copy directory {source} to {destination}: {e}")
        return False

def find_files(directory: Path, pattern: str) -> List[Path]:
    """Find files matching pattern in directory"""
    try:
        return list(directory.glob(pattern))
    except Exception as e:
        logger.error(f"Failed to find files in {directory}: {e}")
        return []

def read_file(file_path: Path, encoding: str = 'utf-8') -> Optional[str]:
    """Read file contents"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return None

def write_file(file_path: Path, content: str, encoding: str = 'utf-8') -> bool:
    """Write content to file"""
    try:
        ensure_directory(file_path.parent)
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"Failed to write to {file_path}: {e}")
        return False

def get_directory_size(path: Path) -> int:
    """Get total size of directory in bytes"""
    total = 0
    try:
        for entry in path.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except Exception as e:
        logger.error(f"Failed to calculate directory size: {e}")
    return total

def clean_directory(path: Path, keep_empty: bool = True) -> bool:
    """Clean directory contents"""
    try:
        if path.exists():
            shutil.rmtree(path)
        if keep_empty:
            path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to clean directory {path}: {e}")
        return False