import plotly.graph_objects as go
from typing import Optional
from app.schemas import ChartConfig

class BaseChart:
    def __init__(self, config: ChartConfig):
        self.config = config

    def _get_legend_position(self):
        mapping = {
            "top": dict(x=0.5, y=1.0, xanchor="center", yanchor="top"),
            "bottom": dict(x=0.5, y=0.0, xanchor="center", yanchor="bottom"),
            "left": dict(x=0.0, y=0.5, xanchor="left", yanchor="middle"),
            "right": dict(x=1.0, y=0.5, xanchor="right", yanchor="middle"),
            "top+right": dict(x=1.0, y=1.0, xanchor="right", yanchor="top"),
            "top+left": dict(x=0.0, y=1.0, xanchor="left", yanchor="top"),
            "bottom+right": dict(x=1.0, y=0.0, xanchor="right", yanchor="bottom"),
            "bottom+left": dict(x=0.0, y=0.0, xanchor="left", yanchor="bottom"),
            "left+top": dict(x=0.0, y=1.0, xanchor="left", yanchor="top"),
            "left+bottom": dict(x=0.0, y=0.0, xanchor="left", yanchor="bottom"),
            "right+top": dict(x=1.0, y=1.0, xanchor="right", yanchor="top"),
            "right+bottom": dict(x=1.0, y=0.0, xanchor="right", yanchor="bottom"),
        }
        legend = getattr(self.config, 'legend', None)
        if legend and hasattr(legend, 'position'):
            return mapping.get(legend.position, mapping["top"])
        return mapping["top"]

    def apply_common_layout(self, fig: go.Figure) -> go.Figure:
        """Applies title, axis labels, fonts, grids, legend, and annotations"""
        # Title
        title = getattr(self.config, 'title', None)
        if title and hasattr(title, 'text'):
            fig.update_layout(
                title=dict(
                    text=title.text,
                    font=dict(
                        family=getattr(title, 'font_family', 'Arial'),
                        size=getattr(title, 'font_size', 20),
                        color=getattr(title, 'font_color', '#000000')
                    )
                )
            )

        # X-axis
        x_label = getattr(self.config, 'x_label', None)
        if x_label and hasattr(x_label, 'text'):
            fig.update_xaxes(
                title=dict(
                    text=x_label.text,
                    font=dict(
                        family=getattr(x_label, 'font_family', 'Arial'),
                        size=getattr(x_label, 'font_size', 14),
                        color=getattr(x_label, 'font_color', '#000000')
                    )
                ),
                showgrid=getattr(getattr(self.config, 'grid', None), 'type', 'none') in ['both', 'vertical'],
                gridcolor=getattr(getattr(self.config, 'grid', None), 'color', '#e0e0e0'),
                tickangle=getattr(x_label, 'rotation', 0)
            )

        # Y-axis
        y_label = getattr(self.config, 'y_label', None)
        if y_label and hasattr(y_label, 'text'):
            fig.update_yaxes(
                title=dict(
                    text=y_label.text,
                    font=dict(
                        family=getattr(y_label, 'font_family', 'Arial'),
                        size=getattr(y_label, 'font_size', 14),
                        color=getattr(y_label, 'font_color', '#000000')
                    )
                ),
                showgrid=getattr(getattr(self.config, 'grid', None), 'type', 'none') in ['both', 'horizontal'],
                gridcolor=getattr(getattr(self.config, 'grid', None), 'color', '#e0e0e0'),
                tickangle=getattr(y_label, 'rotation', 0)
            )

        # Legend
        legend = getattr(self.config, 'legend', None)
        show_legend = getattr(legend, 'show', True)
        orientation = getattr(legend, 'orientation', 'v')
        fig.update_layout(
            showlegend=show_legend,
            legend=dict(
                orientation=orientation,
                **self._get_legend_position()
            )
        )

        # Annotations with optional vertical lines
        ann = getattr(self.config, 'annotations', None)
        if ann and getattr(ann, 'show_values', False):
            y_min = 0
            if fig.layout.yaxis and fig.layout.yaxis.range:
                y_min = fig.layout.yaxis.range[0]

            for trace in fig.data:
                x_vals = trace.x if hasattr(trace, 'x') else []
                y_vals = trace.y if hasattr(trace, 'y') else []

                for x, y in zip(x_vals, y_vals):
                    x_match = (
                        getattr(ann, 'show_x_values', None) is None or
                        getattr(ann, 'show_x_values', None) == "all" or
                        (isinstance(getattr(ann, 'show_x_values', None), list) and x in getattr(ann, 'show_x_values', None))
                    )

                    y_match = (
                        getattr(ann, 'show_y_values', None) is None or
                        getattr(ann, 'show_y_values', None) == "all" or
                        (isinstance(getattr(ann, 'show_y_values', None), list) and y in getattr(ann, 'show_y_values', None))
                    )

                    if x_match and y_match:
                        fig.add_annotation(
                            x=x,
                            y=y,
                            text=f"({x}, {y})",
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
                                x0=x, y0=y_min,
                                x1=x, y1=y,
                                line=dict(
                                    color=getattr(ann, 'line_color', '#000000'),
                                    width=getattr(ann, 'line_width', 1),
                                    dash=getattr(ann, 'line_dash', 'solid')
                                ),
                                layer='below'
                            )

        return fig
