from .schemas import ChartRequest
from charts.line_chart import LineChart
from charts.bar_chart import BarChart
from charts.pie_chart import PieChart
from charts.histogram_chart import HistogramChart
from charts.area import AreaChart
from charts.distplot import DistplotChart
from charts.scatter_chart import ScatterChart
from charts.waterfall_chart import WaterfallChart
from charts.heatmap_chart import HeatmapChart
from charts.subplots import SubplotChart
from typing import List
import plotly.graph_objects as go


def create_chart(request: ChartRequest, data: List[dict]) -> go.Figure:
    if request.chart_type == "subplots":
        chart = SubplotChart(request.config)
        return chart.generate(data)
    else:
        # Instantiate the appropriate chart class
        if request.chart_type == "line":
            chart = LineChart(request.config)
        elif request.chart_type == "bar":
            chart = BarChart(request.config)
        elif request.chart_type == "pie":
            chart = PieChart(request.config)
        elif request.chart_type == "histogram":
            chart = HistogramChart(request.config)
        elif request.chart_type == "area":
            chart = AreaChart(request.config)
        elif request.chart_type == "distplot":
            chart = DistplotChart(request.config)
        elif request.chart_type == "scatter":
            chart = ScatterChart(request.config)
        elif request.chart_type == "waterfall":
            chart = WaterfallChart(request.config)
        elif request.chart_type == "heatmap":
            chart = HeatmapChart(request.config)
        else:
            raise ValueError(f"Unsupported chart type: {request.chart_type}")

        # For single charts, pass traces and data
        return chart.generate(request.traces, data)


from Filters.datafilter import async_apply_filters


def filter_data(raw_data, filters):
    return async_apply_filters(raw_data, filters)