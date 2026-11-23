"""
Módulo: shared/document_types.py
¿Qué? Tipos de documento de identidad válidos en Colombia (coinciden con el select del frontend).
¿Para qué? Es vocabulario común: lo usan el registro (identity) y el registro por
           invitación (team). Vive en shared para que ninguno de los dos dependa del otro.
"""

from enum import Enum


class DocumentType(str, Enum):
    """Tipos de documento válidos — coinciden con el select del frontend."""

    CC = "CC"
    CE = "CE"
    TI = "TI"
    PP = "PP"
    NIT = "NIT"
