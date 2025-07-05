"""
DieAI Knowledge Library
A comprehensive Python library for mathematics and science knowledge processing.
"""

__version__ = "1.0.0"
__author__ = "DieAI Team"
__email__ = "info@dieai.com"

from .knowledge_base import KnowledgeBase
from .math_solver import MathSolver
from .science_facts import ScienceFacts
from .unit_converter import UnitConverter

__all__ = ['KnowledgeBase', 'MathSolver', 'ScienceFacts', 'UnitConverter']