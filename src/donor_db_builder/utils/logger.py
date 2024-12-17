import sys
import os
from loguru import logger
from datetime import datetime
from typing import Optional


class Logger:
    @staticmethod
    def setup_logger(
            log_dir: str = 'logs',
            app_name: str = 'app',
            console: bool = True,
            log_file: bool = True
    ) -> None:
        """
        Configure logging for the application

        Args:
            log_dir: Directory to store log files
            app_name: Name of the application (used in log filename)
            console: Whether to output logs to console
            log_file: Whether to output logs to file
        """
        # Create logs directory if it doesn't exist
        if log_file and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Remove default logger
        logger.remove()

        # Add console logger if enabled
        if console:
            logger.add(
                sys.stdout,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
            )

        # Add file logger if enabled
        if log_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_filename = f'{log_dir}/{app_name}_{timestamp}.log'

            logger.add(
                log_filename,
                rotation="500 MB",
                retention="10 days",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
                backtrace=True,
                diagnose=True
            )

    @staticmethod
    def get_logger():
        """Get configured logger instance"""
        return logger