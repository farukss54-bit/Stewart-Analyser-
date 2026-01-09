# logger.py
# Stewart Asit-Baz Analizi - Logging Module v3.2
# Centralized logging configuration

import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime
import json


# =============================================================================
# LOGGER CONFIGURATION
# =============================================================================

def setup_logger(
    name: str = "stewart_analyzer",
    level: int = logging.INFO,
    log_to_file: bool = False,
    log_file: str = "stewart_analyzer.log"
) -> logging.Logger:
    """
    Setup and return configured logger.
    
    Usage:
        logger = setup_logger()
        logger.info("User uploaded file")
        logger.warning("Missing Ca/Mg - SIG approximate")
        logger.error("Analysis failed", extra={"input": sanitized_input})
    """
    
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logger()


# =============================================================================
# LOGGING HELPERS
# =============================================================================

def log_user_action(action: str, details: Optional[Dict[str, Any]] = None):
    """
    Log user action at INFO level.
    
    Examples:
        log_user_action("file_upload", {"filename": "data.csv", "rows": 100})
        log_user_action("analysis_start", {"mode": "advanced"})
        log_user_action("batch_complete", {"processed": 50, "errors": 2})
    """
    msg = f"USER_ACTION: {action}"
    if details:
        # Sanitize details
        safe_details = {k: str(v)[:100] for k, v in details.items()}
        msg += f" | {json.dumps(safe_details)}"
    logger.info(msg)


def log_calculation_warning(warning_type: str, details: Optional[Dict[str, Any]] = None):
    """
    Log calculation warning at WARNING level.
    
    Examples:
        log_calculation_warning("missing_ca_mg", {"sig_reliability": "approximate"})
        log_calculation_warning("hco3_mismatch", {"manual": 22, "calculated": 18})
        log_calculation_warning("assumed_default", {"param": "albumin", "value": 40})
    """
    msg = f"CALC_WARNING: {warning_type}"
    if details:
        safe_details = {k: str(v)[:100] for k, v in details.items()}
        msg += f" | {json.dumps(safe_details)}"
    logger.warning(msg)


def log_analysis_error(error_type: str, input_snapshot: Optional[Dict[str, Any]] = None):
    """
    Log analysis error at ERROR level.
    
    Input snapshot is sanitized to remove sensitive data.
    
    Examples:
        log_analysis_error("validation_failed", {"ph": 6.5, "reason": "out_of_range"})
        log_analysis_error("calculation_error", {"step": "sid_full", "error": str(e)})
    """
    msg = f"ANALYSIS_ERROR: {error_type}"
    if input_snapshot:
        # Sanitize - only include numeric parameters
        safe_snapshot = {}
        allowed_keys = ["ph", "pco2", "na", "cl", "k", "ca", "mg", "lactate", 
                       "albumin_gl", "po4", "be", "hco3"]
        for k in allowed_keys:
            if k in input_snapshot:
                safe_snapshot[k] = input_snapshot[k]
        msg += f" | Input: {json.dumps(safe_snapshot)}"
    logger.error(msg)


def log_batch_progress(current: int, total: int, status: str = "processing"):
    """
    Log batch processing progress at INFO level.
    
    Examples:
        log_batch_progress(10, 100, "processing")
        log_batch_progress(100, 100, "complete")
    """
    logger.info(f"BATCH: {status} | {current}/{total} ({current/total*100:.1f}%)")


# =============================================================================
# DEBUG HELPERS
# =============================================================================

def log_debug(component: str, message: str, data: Optional[Dict[str, Any]] = None):
    """
    Log debug information (only shown when DEBUG level is enabled).
    
    Examples:
        log_debug("SID", "Calculated SID values", {"simple": 38, "basic": 36})
        log_debug("validation", "Input validation result", {"is_valid": True})
    """
    msg = f"DEBUG [{component}]: {message}"
    if data:
        msg += f" | {json.dumps(data)}"
    logger.debug(msg)


# =============================================================================
# ANALYSIS LOGGING - Sprint 3 (#4)
# =============================================================================

def log_analysis_start(mode: str, input_summary: Optional[Dict[str, Any]] = None):
    """
    Log analysis start at INFO level.
    
    Examples:
        log_analysis_start("quick", {"ph": 7.25, "pco2": 30})
        log_analysis_start("advanced", {"ph": 7.40, "has_albumin": True})
    """
    msg = f"ANALYSIS_START: mode={mode}"
    if input_summary:
        safe_summary = {k: str(v)[:50] for k, v in input_summary.items()}
        msg += f" | {json.dumps(safe_summary)}"
    logger.info(msg)


def log_analysis_complete(
    mode: str,
    duration_ms: Optional[float] = None,
    result_summary: Optional[Dict[str, Any]] = None
):
    """
    Log analysis completion at INFO level.
    
    Examples:
        log_analysis_complete("quick", 45.2, {"dominant": "sid_acidosis", "be": -8})
        log_analysis_complete("advanced", 120.5, {"sig": 5.2, "flags": ["SIG_HIGH"]})
    """
    msg = f"ANALYSIS_COMPLETE: mode={mode}"
    if duration_ms is not None:
        msg += f" | duration={duration_ms:.1f}ms"
    if result_summary:
        safe_summary = {k: str(v)[:100] for k, v in result_summary.items()}
        msg += f" | {json.dumps(safe_summary)}"
    logger.info(msg)


def log_extreme_value(param: str, value: float, threshold_type: str, clinical_note: str = ""):
    """
    Log extreme value detection at WARNING level.
    
    Args:
        param: Parameter name (ph, pco2, lactate, etc.)
        value: The extreme value detected
        threshold_type: "low" or "high"
        clinical_note: Optional clinical significance note
    
    Examples:
        log_extreme_value("ph", 6.92, "low", "Şiddetli asidemi - acil müdahale")
        log_extreme_value("lactate", 15.0, "high", "Şok düzeyinde laktat")
    """
    msg = f"EXTREME_VALUE: {param}={value} ({threshold_type})"
    if clinical_note:
        msg += f" | Note: {clinical_note}"
    logger.warning(msg)


def log_mechanism_result(
    dominant_mechanism: Optional[str],
    significant_mechanisms: Optional[list] = None,
    pattern_flags: Optional[list] = None
):
    """
    Log mechanism analysis result at INFO level.
    
    Examples:
        log_mechanism_result("sid_acidosis", ["lactate"], ["hyperchloremic"])
        log_mechanism_result("unmeasured_anion", None, ["sig_elevated", "masked_acidosis"])
    """
    msg = f"MECHANISM_RESULT: dominant={dominant_mechanism or 'none'}"
    if significant_mechanisms:
        msg += f" | significant={significant_mechanisms}"
    if pattern_flags:
        msg += f" | patterns={pattern_flags}"
    logger.info(msg)


def log_sid_calculation(sid_simple: float, sid_basic: Optional[float], sid_full: Optional[float]):
    """
    Log SID calculation results at DEBUG level.
    
    Examples:
        log_sid_calculation(38.0, 36.5, 40.2)
        log_sid_calculation(32.0, None, None)  # Missing lactate
    """
    msg = f"SID_CALC: simple={sid_simple}"
    if sid_basic is not None:
        msg += f" | basic={sid_basic}"
    if sid_full is not None:
        msg += f" | full={sid_full}"
    logger.debug(msg)


def log_compensation_assessment(
    primary_disorder: str,
    expected_value: Optional[float],
    observed_value: float,
    compensation_status: str
):
    """
    Log compensation assessment at DEBUG level.
    
    Examples:
        log_compensation_assessment("metabolic_acidosis", 25.0, 28.0, "Uygun kompanzasyon")
        log_compensation_assessment("respiratory_acidosis", 28.0, 24.0, "Ek metabolik asidoz")
    """
    msg = f"COMPENSATION: primary={primary_disorder}"
    if expected_value is not None:
        msg += f" | expected={expected_value} | observed={observed_value}"
    msg += f" | status={compensation_status}"
    logger.debug(msg)


# =============================================================================
# STREAMLIT INTEGRATION
# =============================================================================

class StreamlitLogHandler(logging.Handler):
    """
    Custom log handler that displays warnings/errors in Streamlit.
    
    Usage:
        logger.addHandler(StreamlitLogHandler())
    """
    
    def __init__(self):
        super().__init__()
        self.setLevel(logging.WARNING)
    
    def emit(self, record):
        try:
            import streamlit as st
            
            msg = self.format(record)
            
            if record.levelno >= logging.ERROR:
                st.error(f"âš ï¸ {msg}")
            elif record.levelno >= logging.WARNING:
                # Don't show internal warnings to user unless critical
                pass
        except Exception:
            pass  # Streamlit not available


def enable_streamlit_logging():
    """Enable Streamlit log display for errors"""
    logger.addHandler(StreamlitLogHandler())
