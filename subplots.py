from plotly.subplots import make_subplots
import plotly.graph_objects as go
from typing import List
from app.schemas import Trace  # Or use your subplot spec model if different

class SubplotChart:
    def __init__(self, config):
        self.config = config

    def generate(self, data: List[dict]) -> go.Figure:
        # Safely get subplot configuration and specs
        subplot_cfg = getattr(self.config, 'subplots', None)
        specs = getattr(self.config, 'subplot_specs', None)
        if subplot_cfg is None or specs is None:
            raise ValueError("Missing subplot configuration or subplot specs")

        # Safely get subplot layout attributes with defaults
        rows = getattr(subplot_cfg, 'rows', 1)
        cols = getattr(subplot_cfg, 'cols', 1)
        subplot_titles = getattr(subplot_cfg, 'subplot_titles', []) or []
        horizontal_spacing = getattr(subplot_cfg, 'horizontal_spacing', 0.05)
        vertical_spacing = getattr(subplot_cfg, 'vertical_spacing', 0.05)

        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=subplot_titles,
            horizontal_spacing=horizontal_spacing,
            vertical_spacing=vertical_spacing
        )

        for idx, (row_data, subplot) in enumerate(zip(data, specs)):
            row = (idx // cols) + 1
            col = (idx % cols) + 1

            # Safely get x and y columns and name
            x = row_data.get(getattr(subplot, 'x_column', None), []) if hasattr(subplot, 'x_column') else []
            y = row_data.get(getattr(subplot, 'y_column', None), []) if hasattr(subplot, 'y_column') else []
            name = getattr(subplot, 'name', f"Series {idx+1}")
            chart_type = getattr(subplot, 'chart_type', 'line')

            # Create trace based on chart type
            if chart_type == "line":
                trace = go.Scatter(x=x, y=y, name=name, mode="lines")
            elif chart_type == "bar":
                trace = go.Bar(x=x, y=y, name=name)
            elif chart_type == "scatter":
                trace = go.Scatter(x=x, y=y, name=name, mode="markers")
            else:
                trace = go.Scatter(x=x, y=y, name=name, mode="lines")

            fig.add_trace(trace, row=row, col=col)

            # Update x-axis labels if available
            if hasattr(subplot, 'x_label') and subplot.x_label:
                fig.update_xaxes(
                    title_text=getattr(subplot.x_label, 'text', ''),
                    title_font=dict(
                        size=getattr(subplot.x_label, 'font_size', 12),
                        color=getattr(subplot.x_label, 'font_color', '#000000')
                    ),
                    tickangle=getattr(subplot.x_label, 'rotation', 0),
                    row=row, col=col
                )

            # Update y-axis labels if available
            if hasattr(subplot, 'y_label') and subplot.y_label:
                fig.update_yaxes(
                    title_text=getattr(subplot.y_label, 'text', ''),
                    title_font=dict(
                        size=getattr(subplot.y_label, 'font_size', 12),
                        color=getattr(subplot.y_label, 'font_color', '#000000')
                    ),
                    tickangle=getattr(subplot.y_label, 'rotation', 0),
                    row=row, col=col
                )

        # Update overall layout title if present
        if hasattr(self.config, 'title') and self.config.title and hasattr(self.config.title, 'text'):
            fig.update_layout(title_text=self.config.title.text)

        return fig

