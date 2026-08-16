from dataclasses import dataclass


@dataclass(frozen=True)
class OpennessPolicy:
    # Unobserved alternative/backup sites considered in optimistic sensitivity.
    m_plus: int = 0

    # Baseline is deliberately closed with respect to hidden common mandatory
    # dependencies unless documentary evidence supports them.
    m_minus: int = 0


def decision_label(c_low: float, c_high: float, eta: float | None, *,
                   global_envelope: bool, width_gate: float = 0.25) -> str:
    """
    Priority:
    1) global threshold decision
    2) conditional threshold decision
    3) width diagnostic when eta is undefined
    """
    if eta is not None:
        prefix = "robust" if global_envelope else "conditional"
        if c_low >= eta:
            return f"{prefix}_pass"
        if c_high < eta:
            return f"{prefix}_fail"
        return f"{prefix}_indeterminate"

    width = c_high - c_low
    return "descriptively_identifiable" if width <= width_gate else "point_conclusion_not_supported"
