# systems/n64/n64_constants.py

from typing import List

# File Extensions
EEP_EXT: str = ".eep"
SRA_EXT: str = ".sra"
FLA_EXT: str = ".fla"
MPK_EXT: str = ".mpk"
SRM_EXT: str = ".srm"

# File Sizes (bytes)
SIZE_EEP: int = 2048
SIZE_SRA: int = 32768
SIZE_FLA: int = 131072
SIZE_MPK: int = 131072
SIZE_SRM: int = 296960

# Offsets for SRM conversions
SIZE_SRA_SRM_OFFSET: int = 133120
SIZE_FLA_SRM_OFFSET: int = SIZE_SRM - SIZE_FLA
SIZE_MPK_SRM_OFFSET: int = 2048

# File Type Labels
EEP_LABEL: str = " EEPROM (.eep) "
SRA_LABEL: str = " SRAM (.sra) "
FLA_LABEL: str = " FlashRAM (.fla) "
MPK_LABEL: str = " Controller Pak (.mpk) "
SRM_LABEL: str = " Retroarch Save (.srm) "

# Source / Target System Labels
NATIVE_LABEL: str = " Native / Cart Dump "
PJ64_LABEL: str = " Project64/Mupen64 "
RA_LABEL: str = " Retroarch "
WII_LABEL: str = " Wii/WiiU/Everdrive64 "

# Lists for UI dropdowns
FILE_TYPES: List[str] = [EEP_LABEL, SRA_LABEL, FLA_LABEL, MPK_LABEL, SRM_LABEL]
SOURCE_LIST: List[str] = [NATIVE_LABEL, PJ64_LABEL, RA_LABEL, WII_LABEL]
TARGET_LIST: List[str] = [NATIVE_LABEL, PJ64_LABEL, RA_LABEL, WII_LABEL]
