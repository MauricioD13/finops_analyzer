"""Middleware package for finops_analyzer"""

from .delete_files import file_deletion_middleware

__all__ = ["file_deletion_middleware"]
