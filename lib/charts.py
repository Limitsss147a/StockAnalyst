"""Plotly chart renderers with green/red split traces and dark mode."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

CHART_VIEWS = ["Performance", "Price", "Candlestick", "Area"]

_GREEN = "#00d4aa"
_RED = "#ff4757"
_GREEN_FILL = "rgba(0,212,170,0.12)"
_RED_FILL = "rgba(255,71,87,0.12)"


def _split_traces(x, y, green=_GREEN, red=_RED, gfill=_GREEN_FILL, rfill=_RED_FILL,
                   hover_fmt="%{y:.2f}%", name=""):
    """Split a line at zero-crossings into green (≥0) and red (<0) filled segments."""
    traces = []
    if len(x) < 2:
        return traces

    x = list(x)
    y = list(y)
    seg_x, seg_y = [x[0]], [y[0]]
    is_pos = y[0] >= 0

    for i in range(1, len(y)):
        prev, cur = y[i - 1], y[i]
        crossed = (prev >= 0 and cur < 0) or (prev < 0 and cur >= 0)

        if crossed:
            denom = abs(prev) + abs(cur)
            frac = abs(prev) / denom if denom else 0.5
            # interpolate the x-value at zero
            if isinstance(x[0], (int, float, np.integer, np.floating)):
                cx = x[i - 1] + frac * (x[i] - x[i - 1])
            else:
                try:
                    delta = pd.Timestamp(x[i]) - pd.Timestamp(x[i - 1])
                    cx = pd.Timestamp(x[i - 1]) + frac * delta
                except Exception:
                    cx = x[i]

            seg_x.append(cx)
            seg_y.append(0.0)
            col = green if is_pos else red
            fill = gfill if is_pos else rfill
            traces.append(go.Scatter(
                x=seg_x, y=seg_y, fill="tozeroy",
                fillcolor=fill, line=dict(color=col, width=1.8),
                showlegend=False, hovertemplate=hover_fmt + "<extra></extra>",
                name=name,
            ))
            is_pos = not is_pos
            seg_x, seg_y = [cx, x[i]], [0.0, cur]
        else:
            seg_x.append(x[i])
            seg_y.append(cur)

    if seg_x:
        col = green if is_pos else red
        fill = gfill if is_pos else rfill
        traces.append(go.Scatter(
            x=seg_x, y=seg_y, fill="tozeroy",
            fillcolor=fill, line=dict(color=col, width=1.8),
            showlegend=False, hovertemplate=hover_fmt + "<extra></extra>",
            name=name,
        ))
    return traces


def _return_badge(fig, x_last, y_last, text, color):
    """Add a colored annotation badge at the last data point."""
    fig.add_annotation(
        x=x_last, y=y_last, text=f"  {text}  ",
        showarrow=True, arrowhead=0, arrowcolor=color,
        font=dict(color="white", size=12, family="Inter"),
        bgcolor=color, bordercolor=color, borderwidth=1, borderpad=4,
        ax=40, ay=-20, opacity=0.92,
    )


def render_price_chart(df: pd.DataFrame, view: str = "Performance",
                       title: str = "", baseline_price: float | None = None,
                       height: int = 500, show_volume: bool = True) -> go.Figure | None:
    """Render a price chart with the chosen view.

    Parameters
    ----------
    df : pd.DataFrame  – OHLCV dataframe with DatetimeIndex.
    view : str          – One of CHART_VIEWS.
    title : str         – Chart title.
    baseline_price : float | None – For 1D, use yesterday's close as baseline.
    height : int        – Chart pixel height.
    show_volume : bool  – Whether to overlay volume bars.
    """
    if df is None or df.empty:
        return None

    closes = df["Close"].dropna()
    if closes.empty:
        return None

    x_vals = closes.index
    base = baseline_price if baseline_price else closes.iloc[0]

    use_volume = show_volume and "Volume" in df.columns
    rows = 2 if use_volume else 1
    row_heights = [0.78, 0.22] if use_volume else [1]
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, row_heights=row_heights)

    if view == "Performance":
        pct = ((closes - base) / base) * 100
        traces = _split_traces(x_vals, pct.values, hover_fmt="%{y:.2f}%")
        for tr in traces:
            fig.add_trace(tr, row=1, col=1)
        fig.update_yaxes(title_text="Return (%)", row=1, col=1, zeroline=True,
                         zerolinecolor="rgba(255,255,255,0.2)", zerolinewidth=1)
        last_pct = pct.iloc[-1]
        _return_badge(fig, x_vals[-1], last_pct,
                      f"{last_pct:+.2f}%", _GREEN if last_pct >= 0 else _RED)

    elif view == "Price":
        color = _GREEN if closes.iloc[-1] >= base else _RED
        fig.add_trace(go.Scatter(
            x=x_vals, y=closes, mode="lines",
            line=dict(color=color, width=2),
            showlegend=False, hovertemplate="Rp%{y:,.0f}<extra></extra>",
        ), row=1, col=1)
        fig.update_yaxes(title_text="Harga", row=1, col=1)

    elif view == "Candlestick":
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            increasing_line_color=_GREEN, decreasing_line_color=_RED,
            increasing_fillcolor=_GREEN, decreasing_fillcolor=_RED,
            showlegend=False,
        ), row=1, col=1)
        fig.update_yaxes(title_text="Harga", row=1, col=1)

    elif view == "Area":
        delta = closes - base
        traces = _split_traces(x_vals, delta.values,
                               hover_fmt="Rp%{customdata:,.0f}<extra></extra>")
        for tr in traces:
            tr.customdata = closes.values  # show actual price on hover
            fig.add_trace(tr, row=1, col=1)
        fig.update_yaxes(title_text="Δ Harga", row=1, col=1, zeroline=True,
                         zerolinecolor="rgba(255,255,255,0.2)", zerolinewidth=1)

    # Volume subplot
    if use_volume:
        vol = df["Volume"].fillna(0)
        colors = [_GREEN if df["Close"].iloc[i] >= df["Open"].iloc[i] else _RED
                  for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df.index, y=vol, marker_color=colors, opacity=0.45,
            showlegend=False, hovertemplate="Vol: %{y:,.0f}<extra></extra>",
        ), row=rows, col=1)
        fig.update_yaxes(title_text="Volume", row=rows, col=1)

    fig.update_layout(
        template="plotly_dark",
        title=dict(text=title, font=dict(size=16, family="Inter")),
        height=height,
        margin=dict(l=10, r=10, t=45, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        font=dict(family="Inter"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)")

    return fig


def render_sparkline(closes, base_price=None, width=120, height=40):
    """Render a tiny sparkline as a plotly figure (for metric cards)."""
    if closes is None or len(closes) < 2:
        return None

    base = base_price if base_price else closes[0]
    pct = [(c - base) / base * 100 for c in closes]

    fig = go.Figure()
    traces = _split_traces(list(range(len(pct))), pct)
    for tr in traces:
        fig.add_trace(tr)

    fig.update_layout(
        template="plotly_dark",
        width=width, height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False, zeroline=True, zerolinecolor="rgba(255,255,255,0.15)"),
        showlegend=False,
        hovermode=False,
    )
    return fig


def render_gauge(value, title="", subtitle="", max_val=100, height=250):
    """Render a gauge chart (0-100 scale) with color bands."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title=dict(text=f"<b>{title}</b><br><span style='font-size:12px;color:#888'>{subtitle}</span>",
                   font=dict(size=16, family="Inter")),
        number=dict(font=dict(size=36, family="Inter", color="white")),
        gauge=dict(
            axis=dict(range=[0, max_val], tickwidth=1, tickcolor="#444"),
            bar=dict(color="rgba(255,255,255,0.85)", thickness=0.2),
            bgcolor="rgba(0,0,0,0)",
            steps=[
                dict(range=[0, 25], color="#ff4757"),
                dict(range=[25, 50], color="#ff8c42"),
                dict(range=[50, 75], color="#ffd32a"),
                dict(range=[75, 100], color="#00d4aa"),
            ],
            threshold=dict(line=dict(color="white", width=3), thickness=0.8, value=value),
        ),
    ))
    fig.update_layout(
        template="plotly_dark", height=height,
        margin=dict(l=30, r=30, t=60, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter"),
    )
    return fig


def render_sector_heatmap(sector_data: dict, title: str = "Kinerja Sektor"):
    """Horizontal bar chart for sector performance."""
    sectors = list(sector_data.keys())
    values = list(sector_data.values())
    colors = [_GREEN if v >= 0 else _RED for v in values]

    # Sort by value
    paired = sorted(zip(sectors, values, colors), key=lambda x: x[1])
    sectors, values, colors = zip(*paired) if paired else ([], [], [])

    fig = go.Figure(go.Bar(
        y=sectors, x=values, orientation="h",
        marker_color=colors, text=[f"{v:+.2f}%" for v in values],
        textposition="outside", textfont=dict(size=12, family="Inter"),
        hovertemplate="%{y}: %{x:+.2f}%<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_dark", title=title,
        height=max(300, len(sectors) * 38),
        margin=dict(l=10, r=10, t=45, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Return (%)", gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        font=dict(family="Inter"),
    )
    return fig


def render_technical_chart(df: pd.DataFrame, indicators: dict,
                           show_sma: bool = True, show_bb: bool = True,
                           show_macd: bool = True, show_rsi: bool = True,
                           title: str = "", height: int = 700) -> go.Figure | None:
    """Render a multi-panel technical analysis chart.

    Panels: Price+overlays, Volume, MACD, RSI.
    """
    if df is None or df.empty:
        return None

    # Determine active panels
    panels = ["price"]
    if "Volume" in df.columns:
        panels.append("volume")
    if show_macd:
        panels.append("macd")
    if show_rsi:
        panels.append("rsi")

    n = len(panels)
    heights_map = {
        1: [1],
        2: [0.7, 0.3],
        3: [0.55, 0.2, 0.25],
        4: [0.45, 0.15, 0.2, 0.2],
    }
    row_heights = heights_map.get(n, [1 / n] * n)

    fig = make_subplots(rows=n, cols=1, shared_xaxes=True,
                        vertical_spacing=0.02, row_heights=row_heights,
                        subplot_titles=[None] * n)

    x = df.index
    row = 1

    # ── Panel 1: Candlestick + overlays ──
    fig.add_trace(go.Candlestick(
        x=x, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        increasing_line_color=_GREEN, decreasing_line_color=_RED,
        increasing_fillcolor=_GREEN, decreasing_fillcolor=_RED,
        showlegend=False, name="Price",
    ), row=row, col=1)

    if show_sma:
        for key, color, dash in [
            ("sma20", "#f59e0b", None), ("sma50", "#3b82f6", None), ("sma200", "#a855f7", "dot"),
        ]:
            if key in indicators:
                fig.add_trace(go.Scatter(
                    x=x, y=indicators[key], mode="lines", name=key.upper(),
                    line=dict(color=color, width=1.2, dash=dash), opacity=0.85,
                ), row=row, col=1)

    if show_bb and "bb_upper" in indicators:
        fig.add_trace(go.Scatter(
            x=x, y=indicators["bb_upper"], mode="lines", name="BB Upper",
            line=dict(color="#888", width=0.8, dash="dash"), showlegend=False,
        ), row=row, col=1)
        fig.add_trace(go.Scatter(
            x=x, y=indicators["bb_lower"], mode="lines", name="BB Lower",
            line=dict(color="#888", width=0.8, dash="dash"), showlegend=False,
            fill="tonexty", fillcolor="rgba(136,136,136,0.06)",
        ), row=row, col=1)

    fig.update_yaxes(title_text="Harga", row=row, col=1)
    row += 1

    # ── Panel 2: Volume ──
    if "volume" in panels:
        vol = df["Volume"].fillna(0)
        colors = [_GREEN if df["Close"].iloc[i] >= df["Open"].iloc[i] else _RED
                  for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=x, y=vol, marker_color=colors, opacity=0.5,
            showlegend=False, name="Volume",
        ), row=row, col=1)
        fig.update_yaxes(title_text="Vol", row=row, col=1)
        row += 1

    # ── Panel 3: MACD ──
    if show_macd and "macd_line" in indicators:
        fig.add_trace(go.Scatter(
            x=x, y=indicators["macd_line"], mode="lines", name="MACD",
            line=dict(color="#3b82f6", width=1.3),
        ), row=row, col=1)
        fig.add_trace(go.Scatter(
            x=x, y=indicators["macd_signal"], mode="lines", name="Signal",
            line=dict(color="#f59e0b", width=1.3),
        ), row=row, col=1)
        hist = indicators["macd_hist"]
        hist_colors = [_GREEN if v >= 0 else _RED for v in hist]
        fig.add_trace(go.Bar(
            x=x, y=hist, marker_color=hist_colors, opacity=0.6,
            showlegend=False, name="MACD Hist",
        ), row=row, col=1)
        fig.update_yaxes(title_text="MACD", row=row, col=1, zeroline=True,
                         zerolinecolor="rgba(255,255,255,0.15)")
        row += 1

    # ── Panel 4: RSI ──
    if show_rsi and "rsi" in indicators:
        fig.add_trace(go.Scatter(
            x=x, y=indicators["rsi"], mode="lines", name="RSI",
            line=dict(color="#a855f7", width=1.5),
        ), row=row, col=1)
        # Overbought / Oversold lines
        fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,71,87,0.4)",
                      row=row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="rgba(0,212,170,0.4)",
                      row=row, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,71,87,0.05)",
                      line_width=0, row=row, col=1)
        fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0,212,170,0.05)",
                      line_width=0, row=row, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=row, col=1)

    fig.update_layout(
        template="plotly_dark",
        title=dict(text=title, font=dict(size=16, family="Inter")),
        height=height,
        margin=dict(l=10, r=10, t=45, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        font=dict(family="Inter"),
        legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center"),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)")
    return fig
