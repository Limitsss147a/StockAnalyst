"""Risk scoring for stocks and portfolios (0-100 scale)."""

import numpy as np


def compute_risk_score(closes: list, beta: float = None) -> tuple[int, str]:
    """Compute a risk score (0=conservative, 100=very aggressive).

    Based on:
    - Annualized volatility
    - Maximum drawdown
    - Beta vs market
    """
    if len(closes) < 20:
        return 50, "Data tidak cukup untuk penilaian risiko"

    # Daily returns
    returns = np.diff(closes) / closes[:-1]

    # Annualized volatility
    vol = np.std(returns) * np.sqrt(252) * 100

    # Max drawdown
    cummax = np.maximum.accumulate(closes)
    drawdowns = (closes - cummax) / cummax * 100
    max_dd = abs(np.min(drawdowns))

    # Score components
    vol_score = min(40, vol * 1.5)  # vol 0-27% maps to 0-40
    dd_score = min(35, max_dd * 0.7)  # dd 0-50% maps to 0-35
    beta_score = 0
    if beta and beta > 0:
        beta_score = min(25, (beta - 0.5) * 25)  # beta 0.5-1.5 maps to 0-25
        beta_score = max(0, beta_score)

    total = int(vol_score + dd_score + beta_score)
    total = max(0, min(100, total))

    # Description
    if total < 20:
        desc = "Konservatif – Volatilitas rendah"
    elif total < 40:
        desc = "Moderat – Volatilitas di bawah rata-rata"
    elif total < 60:
        desc = "Menengah – Volatilitas rata-rata pasar"
    elif total < 80:
        desc = "Agresif – Volatilitas di atas rata-rata"
    else:
        desc = "Sangat Agresif – Volatilitas tinggi"

    return total, desc


def portfolio_risk_score(holdings_data: list) -> tuple[int, str]:
    """Compute aggregate risk score for a portfolio.

    holdings_data: list of dicts with 'weight' and 'risk_score' keys.
    """
    if not holdings_data:
        return 0, "Tidak ada data"

    total_weight = sum(h.get("weight", 0) for h in holdings_data)
    if total_weight == 0:
        return 50, "Bobot tidak tersedia"

    weighted_score = sum(
        h.get("risk_score", 50) * h.get("weight", 0) / total_weight
        for h in holdings_data
    )

    # Concentration penalty
    weights = [h.get("weight", 0) for h in holdings_data]
    if weights:
        max_weight = max(weights)
        if max_weight > 40:
            weighted_score += (max_weight - 40) * 0.5  # penalty for concentration

    score = int(max(0, min(100, weighted_score)))

    if score < 20:
        desc = "Portofolio Konservatif"
    elif score < 40:
        desc = "Portofolio Moderat"
    elif score < 60:
        desc = "Portofolio Seimbang"
    elif score < 80:
        desc = "Portofolio Agresif"
    else:
        desc = "Portofolio Sangat Agresif"

    return score, desc
