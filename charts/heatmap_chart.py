from typing import List
import plotly.graph_objects as go
from schemas import Trace  # Make sure this is your Trace model with x_column, y_column, name
from charts.base_chart import BaseChart

class HeatmapChart(BaseChart):
    def __init__(self, config):
        super().__init__(config)

    def generate(self, traces: List[Trace], data: List[dict]) -> go.Figure:
        fig = go.Figure()
        style = getattr(self.config.style, "heatmap", None)
        if style is None:
            style = type('style', (), {
                "transpose": False,
                "colorscale": "Viridis",
                "colorbar_title": None,
                "zmin": None,
                "zmax": None,
                "showscale": True,
                "reversescale": False,
                "opacity": 1.0,
                "xgap": 0,
                "ygap": 0,
                "hoverinfo": "z",
                "zhoverformat": None,
                "heatmap_annotations_show": False,
                "heatmap_annotations_font_size": 12,
                "heatmap_annotations_font_color": "#000000"
            })()

        # For heatmap, we expect at least one trace and data
        if not traces or not data:
            return fig

        # Use the first trace for heatmap (since heatmap is typically for one trace)
        trace = traces[0]
        x_col = trace.x_column
        y_col = trace.y_column
        z_col = trace.z_column if hasattr(trace, 'z_column') else None

        # If no z_column, we can use a single column for a simple heatmap (not recommended, but possible)
        if not z_col:
            # For a simple heatmap, use x_col as x, y_col as y, and a dummy z (not meaningful)
            x_data = [row[x_col] for row in data]
            y_data = [row[y_col] for row in data]
            z_data = [[1] * len(data)]  # Dummy z data (not meaningful)
        else:
            # Group data by x and y to form a matrix for z
            x_data = sorted({row[x_col] for row in data})
            y_data = sorted({row[y_col] for row in data})
            x_index = {value: idx for idx, value in enumerate(x_data)}
            y_index = {value: idx for idx, value in enumerate(y_data)}
            z_data = [[None for _ in x_data] for _ in y_data]
            for row in data:
                x_idx = x_index.get(row[x_col])
                y_idx = y_index.get(row[y_col])
                if x_idx is not None and y_idx is not None:
                    z_data[y_idx][x_idx] = row[z_col]

        # Transpose if requested
        if getattr(style, "transpose", False) and z_data:
            z_data = [list(row) for row in zip(*z_data)]
            x_data, y_data = y_data, x_data

        fig.add_trace(go.Heatmap(
            z=z_data,
            x=x_data,
            y=y_data,
            colorscale=getattr(style, "colorscale", "Viridis"),
            colorbar=dict(title=style.colorbar_title) if getattr(style, "colorbar_title", None) else None,
            zmin=getattr(style, "zmin", None),
            zmax=getattr(style, "zmax", None),
            showscale=getattr(style, "showscale", True),
            reversescale=getattr(style, "reversescale", False),
            opacity=getattr(style, "opacity", 1.0),
            xgap=getattr(style, "xgap", 0),
            ygap=getattr(style, "ygap", 0),
            hoverinfo=getattr(style, "hoverinfo", "z"),
            zhoverformat=getattr(style, "zhoverformat", None)
        ))

        # Add annotations if enabled
        if getattr(style, "heatmap_annotations_show", False) and z_data:
            font_size = getattr(style, "heatmap_annotations_font_size", 12)
            font_color = getattr(style, "heatmap_annotations_font_color", "#000000")
            for i in range(len(z_data)):
                for j in range(len(z_data[0])):
                    if z_data[i][j] is not None:
                        fig.add_annotation(
                            x=x_data[j],
                            y=y_data[i],
                            text=str(z_data[i][j]),
                            showarrow=False,
                            font=dict(size=font_size, color=font_color)
                        )

        fig = self.apply_common_layout(fig)
        return fig

