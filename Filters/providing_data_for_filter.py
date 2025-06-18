# import pandas as pd
# import numpy as np

# def get_filter_metadata_with_unique(df: pd.DataFrame) -> dict:
#     def to_python_type(obj):
#         if isinstance(obj, dict):
#             return {k: to_python_type(v) for k, v in obj.items()}
#         elif isinstance(obj, list):
#             return [to_python_type(v) for v in obj]
#         elif isinstance(obj, (np.integer, np.int64, np.int32)):
#             return int(obj)
#         elif isinstance(obj, (np.floating, np.float64, np.float32)):
#             return float(obj)
#         elif isinstance(obj, (np.ndarray,)):
#             return obj.tolist()
#         else:
#             return obj

#     metadata = {}
#     for col in df.columns:
#         col_data = df[col]
#         unique_vals = col_data.dropna().unique().tolist()
#         if len(unique_vals) > 100:
#             unique_vals = unique_vals[:200]
#         if pd.api.types.is_numeric_dtype(col_data):
#             metadata[col] = {
#                 "min": to_python_type(col_data.min()),
#                 "max": to_python_type(col_data.max()),
#                 "unique_values": to_python_type(unique_vals)
#             }
#         else:
#             metadata[col] = {
#                 "unique_values": to_python_type(unique_vals)
#             }
#     return metadata


