import os
import uuid
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime
from typing import List, Union
from schemas import CategoricalFilter, NumericalFilter
from miniodb import put_object, ensure_bucket
from mongodb import save_filters

FILTERED_BUCKET = "filter-data"
TEMP_DIR = "/tmp"

import numpy as np
import pandas as pd

def vectorized_filter(df: pd.DataFrame, filters: list) -> pd.DataFrame:
    print(filters)
    mask = np.ones(len(df), dtype=bool)
    for f in filters:
        if not hasattr(f, 'column') or f.column not in df.columns:
            continue  # Skip or raise an error if you prefer
        if isinstance(f, CategoricalFilter):
            mask &= df[f.column].isin(f.selected_values).values

        elif isinstance(f, NumericalFilter):
            try:
                if f.operator == '>':
                    mask &= (df[f.column] > f.value).values
                elif f.operator == '<':
                    mask &= (df[f.column] < f.value).values
                elif f.operator == '>=':
                    mask &= (df[f.column] >= f.value).values
                elif f.operator == '<=':
                    mask &= (df[f.column] <= f.value).values
                elif f.operator == '==':
                    mask &= (df[f.column] == f.value).values
                elif f.operator == '!=':
                    mask &= (df[f.column] != f.value).values
                elif f.operator == 'between':
                    if isinstance(f.value, (tuple, list)) and len(f.value) == 2:
                        lower, upper = f.value
                        mask &= (df[f.column] >= lower).values & (df[f.column] <= upper).values
                    else:
                        raise ValueError("'between' operator requires a tuple/list of (lower, upper) values.")
                else:
                    raise ValueError(f"Unknown operator: {f.operator}")
            except Exception as e:
                raise ValueError(f"Error applying filter {f.column}: {str(e)}")
    return df[mask]


async def async_apply_filters(
    df: pd.DataFrame,
    filters: List[Union[CategoricalFilter, NumericalFilter]]
) -> pd.DataFrame:
    import asyncio
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, vectorized_filter, df, filters)

async def filter_and_store(
    df: pd.DataFrame,
    filters: List[Union[CategoricalFilter, NumericalFilter]],
    input_bucket: str,
    input_object_name: str
):
    filtered_df = await async_apply_filters(df, filters)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    filtered_object_name = f"filtered_{timestamp}_{unique_id}.csv"
    os.makedirs(TEMP_DIR, exist_ok=True)
    temp_path = os.path.join(TEMP_DIR, filtered_object_name)

    filtered_df.to_csv(temp_path, index=False)
    ensure_bucket(FILTERED_BUCKET)
    put_object(FILTERED_BUCKET, filtered_object_name, temp_path)

    metadata = {
        "filter_id": unique_id,
        "input_bucket": input_bucket,
        "input_object_name": input_object_name,
        "bucket": FILTERED_BUCKET,
        "object_name": filtered_object_name,
        "filters_applied": [f.model_dump() for f in filters],
        "matched_count": len(filtered_df),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "status": "completed"
    }
    await save_filters(metadata)
    os.remove(temp_path)
    return filtered_df, metadata