"""
PhysioCore: Shared Constants
Version: v9.0 (post Endocrine–Blood separation)

Purpose:
- Shared numeric constants
- State enums
- Safety bounds
- Unit metadata

RULE:
This file MUST NOT contain:
- physiology logic
- decay models
- blood volume
- time evolution behavior
"""

import math

# =========================================================
# Mathematical constants
# =========================================================

LOG_2 = math.log(2)

# =========================================================
# Time constants (unit conversion only)
# =========================================================

SEC_PER_MIN = 60.0
MIN_PER_HOUR = 60.0
HOUR_PER_DAY = 24.0

# =========================================================
# Endocrine gland operational states
# =========================================================

STATE_DORMANT = 0      # baseline secretion only
STATE_ACTIVE = 1       # stimulated
STATE_FATIGUE = 2      # low inventory / reduced output
STATE_EXHAUSTED = 3    # inventory depleted

GLAND_STATE_LABELS = {
    STATE_DORMANT: "dormant",
    STATE_ACTIVE: "active",
    STATE_FATIGUE: "fatigue",
    STATE_EXHAUSTED: "exhausted",
}

# =========================================================
# Numeric safety bounds (global)
# =========================================================

# Concentration / mass safety
GLOBAL_MAX_MASS_PG = 1e12
GLOBAL_MIN_MASS_PG = 0.0

# Floating-point protection
EPSILON = 1e-9

# =========================================================
# Endocrine-specific tuning limits
# =========================================================

# Inventory thresholds
FATIGUE_THRESHOLD_PCT = 0.15     # <15% → fatigue
EXHAUSTED_THRESHOLD_PCT = 0.01   # <1%  → exhausted

# Adaptation bounds
ADAPTATION_MIN = 0.1
ADAPTATION_MAX = 1.0

# Drive (d_remaining) bounds
DRIVE_MIN = 0.0
DRIVE_MAX = 10.0

# =========================================================
# Unit metadata (display / logging only)
# =========================================================

UNITS = {
    "mass": "pg",
    "concentration": "pg/mL",
    "time": "seconds",
    "inventory": "pg",
    "percentage": "%"
}
