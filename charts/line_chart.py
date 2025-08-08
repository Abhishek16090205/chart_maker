from charts.base_chart import BaseChart
import plotly.graph_objects as go
from typing import List
from schemas import Trace

class LineChart(BaseChart):
    def __init__(self, config):
        super().__init__(config)
        self.linestyle_map = {
            '-': 'solid',
            '--': 'dash',
            '-.': 'dashdot',
            ':': 'dot'
        }
        self.marker_symbol_map = {
            "o": "circle",
            "s": "square",
            "d": "diamond",
            "^": "triangle-up",
            "v": "triangle-down",
            "<": "triangle-left",
            ">": "triangle-right",
            "x": "x",
            "+": "cross",
            "*": "star",
            "p": "pentagon",
            "h": "hexagon",
        }

    def generate(self, traces: List[Trace], data: List[dict]) -> go.Figure:
        """
        Generate a line chart from a list of traces and CSV data.
        traces: List of Trace objects (with x_column, y_column, name, optional style)
        data: List of dicts (from CSV)
        """
        fig = go.Figure()

        # Get global line style config, default to empty if not present
        style = getattr(getattr(self.config, 'style', {}), 'line', None)
        if style is None:
            style = type('style', (), {
                'color': ["#1f77b4"],
                'linewidth': [2],
                'linestyle': ["-"],
                'marker': ["o"],
                'markersize': [8],
                'alpha': [1.0]
            })()

        for idx, trace in enumerate(traces):
            x = [row[trace.x_column] for row in data]
            y = [row[trace.y_column] for row in data]
            # Use trace-specific style if available, else fall back to global style
            trace_style = getattr(trace, 'per_trace_style', None)
            if trace_style is not None:
                line_color = getattr(trace_style, 'color', style.color[idx % len(style.color)])
                line_width = getattr(trace_style, 'linewidth', style.linewidth[idx % len(style.linewidth)])
                line_dash = self.linestyle_map.get(
                    getattr(trace_style, 'linestyle', style.linestyle[idx % len(style.linestyle)]),
                    "solid"
                )
                marker_symbol = self.marker_symbol_map.get(
                    getattr(trace_style, 'marker', style.marker[idx % len(style.marker)]),
                    "circle"
                )
                marker_size = getattr(trace_style, 'markersize', style.markersize[idx % len(style.markersize)])
                opacity = getattr(trace_style, 'alpha', style.alpha[idx % len(style.alpha)])
            else:
                line_color = style.color[idx % len(style.color)]
                line_width = style.linewidth[idx % len(style.linewidth)]
                line_dash = self.linestyle_map.get(
                    style.linestyle[idx % len(style.linestyle)],
                    "solid"
                )
                marker_symbol = self.marker_symbol_map.get(
                    style.marker[idx % len(style.marker)],
                    "circle"
                )
                marker_size = style.markersize[idx % len(style.markersize)]
                opacity = style.alpha[idx % len(style.alpha)]

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                name=trace.name or f"Series {idx+1}",
                mode="lines",
                line=dict(
                    color=line_color,
                    width=line_width,
                    dash=line_dash
                ),
                marker=dict(
                    symbol=marker_symbol,
                    size=marker_size,
                    opacity=opacity
                )
            ))

            # Add annotation if trace has annotation config
            if trace_style and hasattr(trace_style, 'annotation') and trace_style.annotation:
                ann = trace_style.annotation
                y_min = 0
                if fig.layout.yaxis and fig.layout.yaxis.range:
                    y_min = fig.layout.yaxis.range[0]

                for x_val, y_val in zip(x, y):
                    x_match = (
                        getattr(ann, 'show_x_values', None) is None or
                        getattr(ann, 'show_x_values', None) == "all" or
                        (isinstance(getattr(ann, 'show_x_values', None), list) and x_val in getattr(ann, 'show_x_values', None))
                    )
                    y_match = (
                        getattr(ann, 'show_y_values', None) is None or
                        getattr(ann, 'show_y_values', None) == "all" or
                        (isinstance(getattr(ann, 'show_y_values', None), list) and y_val in getattr(ann, 'show_y_values', None))
                    )
                    if x_match and y_match:
                        fig.add_annotation(
                            x=x_val,
                            y=y_val,
                            text=f"({x_val}, {y_val})",
                            showarrow=True,
                            font=dict(
                                size=getattr(ann, 'font_size', 12),
                                color=getattr(ann, 'font_color', '#000000')
                            ),
                            arrowcolor=getattr(ann, 'arrow_color', '#000000'),
                            yshift=10
                        )

                        if getattr(ann, 'show_line', False):
                            fig.add_shape(
                                type="line",
                                x0=x_val, y0=y_min,
                                x1=x_val, y1=y_val,
                                line=dict(
                                    color=getattr(ann, 'line_color', '#000000'),
                                    width=getattr(ann, 'line_width', 1),
                                    dash=getattr(ann, 'line_dash', 'solid')
                                ),
                                layer='below'
                            )

        fig = self.apply_common_layout(fig)
        return fig
