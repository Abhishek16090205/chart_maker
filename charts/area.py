from typing import List
import plotly.graph_objects as go
from schemas import Trace, ChartConfig  # Use Trace, not Dataset
from charts.base_chart import BaseChart

class AreaChart(BaseChart):
    def __init__(self, config: ChartConfig):
        super().__init__(config)

    def generate(self, traces: List[Trace], data: List[dict]) -> go.Figure:
        fig = go.Figure()
        style = getattr(getattr(self.config, 'style', {}), 'area', None)
        if style is None:
            style = type('style', (), {
                'stack_mode': 'none',
                'line_color': ['#1f77b4'],
                'line_width': [2],
                'line_dash': ['solid'],
                'fill_opacity': 0.5,
                'fill_pattern': None,
                'markers_show': False,
                'markers_size': 6
            })()
        
        stack_mode = getattr(style, 'stack_mode', 'none')

        for idx, trace in enumerate(traces):
            x = [row[trace.x_column] for row in data]
            y = [row[trace.y_column] for row in data]

            # Get style with index wrapping
            line_color = style.line_color[idx % len(style.line_color)] if hasattr(style, 'line_color') else '#1f77b4'
            line_width = style.line_width[idx % len(style.line_width)] if hasattr(style, 'line_width') else 2
            line_dash = style.line_dash[idx % len(style.line_dash)] if hasattr(style, 'line_dash') else 'solid'
            fill_opacity = getattr(style, 'fill_opacity', 0.5)
            fill_pattern = getattr(style, 'fill_pattern', None)
            marker_show = getattr(style, 'markers_show', False)
            marker_size = getattr(style, 'markers_size', 6)

            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='lines+markers' if marker_show else 'lines',
                name=trace.name or f'Series {idx+1}',
                line=dict(
                    color=line_color,
                    width=line_width,
                    dash=line_dash
                ),
                fill='tonexty' if idx > 0 and stack_mode in ['stack', 'percent'] else 'tozeroy',
                fillpattern=dict(shape=fill_pattern) if fill_pattern else None,
                opacity=fill_opacity,
                marker=dict(
                    size=marker_size,
                    symbol='circle',
                    opacity=fill_opacity
                ) if marker_show else None
            ))

        if stack_mode == 'percent':
            fig.update_layout(yaxis=dict(tickformat='%'))

        fig = self.apply_common_layout(fig)
        return fig
