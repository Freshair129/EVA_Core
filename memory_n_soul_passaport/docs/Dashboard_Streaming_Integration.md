# Dashboard Streaming Integration Guide

## Overview
MSP now provides **real-time streaming buffers** optimized for dashboard visualization, separate from audit trail buffers.

## Streaming Metrics

### 1. Physiological Stream (30 Hz)
High-frequency cardiovascular and endocrine data:

#### Core Hormones (5 Primary)
```python
hormones = [
    "ESC_H01_ADRENALINE",   # Fight-or-flight response
    "ESC_H02_CORTISOL",     # Stress regulation
    "ESC_H05_DOPAMINE",     # Reward/motivation
    "ESC_H06_SEROTONIN",    # Mood stability
    "ESC_H09_OXYTOCIN"      # Social bonding
]
```

#### Cardiovascular
- `heart_rate` (BPM)

**Buffer Size**: 900 samples (30 seconds @ 30 Hz)
**Update**: Every 33ms
**Source**: Physio Core (Blood Engine + Hemodynamics)

### 2. Cognitive State (Per-Turn)
```python
cognitive_metrics = {
    "emotion_label": "EVA Matrix output",
    "memory_color": "RMS color encoding"
}
```

**Buffer Size**: 20 states
**Update**: Per conversation turn
**Display**: Color-coded timeline

## Integration Pattern

### Physio Core → MSP
```python
# In Physio Core (30 Hz loop)
msp.register_dashboard_metric(
    metric_name="ESC_H01_ADRENALINE",
    value=current_adrenaline_level,
    category="physiological_stream"
)
```

### EVA Matrix → MSP
```python
# After Matrix computation (per-turn)
msp.register_dashboard_metric(
    metric_name="emotion_label",
    value="Calm",
    category="cognitive_state"
)
```

### RMS → MSP
```python
# After memory encoding
msp.register_dashboard_metric(
    metric_name="memory_color",
    value="#4A90E2",  # Blue (calm)
    category="cognitive_state"
)
```

## Dashboard Snapshot API

### Get Streaming Data
```python
dashboard_data = msp.get_dashboard_snapshot(
    include_streaming=True,
    time_window=30  # Last 30 seconds
)

# Output structure:
{
    "timestamp": "2026-01-02T19:30:00Z",
    "streaming_metrics": {
        "ESC_H01_ADRENALINE": {
            "values": [10.2, 10.5, 10.8, ...],  # 900 samples
            "timestamps": [1234.567, 1234.600, ...],
            "unit": "pg/mL",
            "chart_type": "line"
        },
        "heart_rate": {
            "values": [72, 72, 73, ...],
            "unit": "BPM"
        }
    },
    "cognitive_state": {
        "emotion_label": {
            "history": ["Calm", "Curious", "Engaged", ...],
            "current": "Engaged"
        },
        "memory_color": {
            "history": ["#4A90E2", "#5BC0DE", ...],
            "current": "#5BC0DE"
        }
    }
}
```

## Visualization Examples

### Line Chart (Hormones)
- X-axis: Time (rolling 30-second window)
- Y-axis: Hormone concentration
- Multiple lines for each hormone (color-coded)

### Timeline (Cognitive State)
- Horizontal bands showing emotion/color changes
- Click to see turn details

## Performance Notes
- **Circular buffers** for efficient memory usage
- **No compression** for real-time access
- **Separate from audit logs** (different storage)
