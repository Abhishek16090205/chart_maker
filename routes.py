from fastapi import APIRouter, HTTPException
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import pandas as pd
from .schemas import ChartRequest
from .chart_service import create_chart
import json
from app.schemas import CategoricalFilter, NumericalFilter
from app.miniodb import get_object, put_object
from fastapi import APIRouter, Form, HTTPException, Query
from Filters.datafilter import filter_and_store, CategoricalFilter, NumericalFilter
import io
from minio import Minio
from pydantic import ValidationError
from typing import Dict, List
from .mongodb import check_mongodb_connection
from app.miniodb import get_object


router = APIRouter()

@router.get("/health/mongo")
async def health_check():
     return await check_mongodb_connection()

def read_file(file_bytes: bytes, object_name: str) -> pd.DataFrame:
    if object_name.lower().endswith('.csv'):
        df = pd.read_csv(io.BytesIO(file_bytes))
    elif object_name.lower().endswith(('.xls', '.xlsx')):
        df = pd.read_excel(io.BytesIO(file_bytes))
    else:
        raise ValueError('Unsupported file format')
    return df

@router.get("/columns")
def get_chart_columns(
    bucket: str = Query(...),
    object_name: str = Query(...)
):
    try:
        file_bytes = get_object(bucket, object_name)
        df = read_file(file_bytes, object_name)
        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
        categorical_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()
        return {
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns
        }
    except Exception as e:
        raise HTTPException(500, detail=f"Could not read columns: {str(e)}")
    

@router.get("/get-unique-values")
def filter_metadata(
    bucket: str = Query(...),
    object_name: str = Query(...),
    column: str = Query(...) 
):
    try:
        csv_bytes = get_object(bucket, object_name)
        df = read_file(csv_bytes, object_name)
        if column not in df.columns:
           return []
        unique_vals = df[column].dropna().unique().tolist()
        return [str(v) for v in unique_vals]
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    
    
@router.post("/filter")
async def filter_data(
    bucket: str = Form(...),
    object_name: str = Form(...),
    filters: str = Form(...)  
):
    try:
        file_bytes = get_object(bucket, object_name)
        file_stream = io.BytesIO(file_bytes)

        if object_name.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_stream)
        else:
            df = pd.read_csv(file_stream)

        filters_list = json.loads(filters)
        if not isinstance(filters_list, list):
            raise HTTPException(400, detail="filters must be a list of dictionaries.")

        filter_objs = []
        for f in filters_list:
            if not isinstance(f, dict):
                raise HTTPException(400, detail="Each filter must be a dictionary.")
            filter_type = f.get("type")
            if filter_type == "categorical":
                try:
                    filter_objs.append(CategoricalFilter(**f))
                except ValidationError as ve:
                    raise HTTPException(400, detail=f"Invalid categorical filter: {str(ve)}")
            elif filter_type == "numerical":
                try:
                    if f.get("operator") == "between":
                        if not isinstance(f.get("value"), (list, tuple)) or len(f.get("value")) != 2:
                            raise HTTPException(400, detail="'between' operator requires a list/tuple of two values.")
                    filter_objs.append(NumericalFilter(**f))
                except ValidationError as ve:
                    raise HTTPException(400, detail=f"Invalid numerical filter: {str(ve)}")
            else:
                raise HTTPException(400, detail=f"Unknown filter type: {filter_type}")
        filtered_df, metadata = await filter_and_store(df, filter_objs, bucket, object_name)

        return {
            "Filtered Data": filtered_df,
            "minio_object": metadata.get("object_name"),
            "message": "Filtered CSV saved and metadata stored"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@router.post("/get-all-columns")
async def get_all_columns(file: UploadFile = File(...)) -> List[str]:
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    return df.columns.tolist()

@router.post("/chart")
async def generate_chart(
    file: UploadFile = File(...),
    config: str = Form(...)
):
    try:
        df = pd.read_csv(file.file)
        data = df.to_dict('records')
        config_obj = json.loads(config)
        chart_req = ChartRequest(**config_obj)
        fig = create_chart(chart_req, data)
        return fig.to_json()
    except json.JSONDecodeError:
        raise HTTPException(400, "Invalid chart config JSON")
    except pd.errors.ParserError:
        raise HTTPException(400, "Invalid CSV file")
    except Exception as e:
        raise HTTPException(500, f"Chart generation failed: {str(e)}")
