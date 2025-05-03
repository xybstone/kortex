from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from fastapi import UploadFile, HTTPException
import pandas as pd
import json
import os
from pathlib import Path
import uuid

from backend.models.models import Database, Table, Column, Row, Cell
from backend.models.schemas import DatabaseCreate, DatabaseUpdate
from backend.core.config import settings

async def create_database(db: Session, database: DatabaseCreate) -> Database:
    """创建新数据库"""
    db_database = Database(
        name=database.name,
        description=database.description,
        user_id=database.user_id
    )
    db.add(db_database)
    db.commit()
    db.refresh(db_database)
    return db_database

def get_databases(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    user_id: Optional[int] = None
) -> List[Database]:
    """获取数据库列表"""
    query = db.query(Database)
    
    # 如果提供了用户ID，只返回该用户的数据库
    if user_id:
        query = query.filter(Database.user_id == user_id)
    
    # 如果提供了搜索关键词，在名称和描述中搜索
    if search:
        query = query.filter(
            Database.name.ilike(f"%{search}%") | 
            Database.description.ilike(f"%{search}%")
        )
    
    return query.offset(skip).limit(limit).all()

def get_database(db: Session, database_id: int) -> Optional[Database]:
    """获取单个数据库详情"""
    return db.query(Database).filter(Database.id == database_id).first()

def update_database(db: Session, database_id: int, database: DatabaseUpdate) -> Database:
    """更新数据库"""
    db_database = db.query(Database).filter(Database.id == database_id).first()
    
    # 更新数据库基本信息
    for key, value in database.dict(exclude_unset=True).items():
        setattr(db_database, key, value)
    
    db.commit()
    db.refresh(db_database)
    return db_database

def delete_database(db: Session, database_id: int) -> None:
    """删除数据库"""
    # 删除数据库中的所有表格及其数据
    tables = db.query(Table).filter(Table.database_id == database_id).all()
    for table in tables:
        # 删除表格中的所有行和单元格
        rows = db.query(Row).filter(Row.table_id == table.id).all()
        for row in rows:
            db.query(Cell).filter(Cell.row_id == row.id).delete()
        db.query(Row).filter(Row.table_id == table.id).delete()
        
        # 删除表格中的所有列
        db.query(Column).filter(Column.table_id == table.id).delete()
    
    # 删除所有表格
    db.query(Table).filter(Table.database_id == database_id).delete()
    
    # 删除数据库
    db.query(Database).filter(Database.id == database_id).delete()
    db.commit()

async def import_database(
    db: Session, 
    name: str, 
    description: Optional[str], 
    file: UploadFile,
    user_id: int
) -> Database:
    """导入数据库文件（Excel, CSV, JSON）"""
    # 创建数据库记录
    db_database = Database(
        name=name,
        description=description,
        user_id=user_id
    )
    db.add(db_database)
    db.commit()
    db.refresh(db_database)
    
    # 保存上传的文件
    file_extension = os.path.splitext(file.filename)[1].lower()
    file_path = settings.UPLOAD_DIR / f"{uuid.uuid4()}{file_extension}"
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # 根据文件类型读取数据
        if file_extension == ".csv":
            df = pd.read_csv(file_path)
            table_name = os.path.splitext(os.path.basename(file.filename))[0]
            await _create_table_from_dataframe(db, db_database.id, table_name, df)
        
        elif file_extension in [".xlsx", ".xls"]:
            # 读取Excel中的所有工作表
            excel_file = pd.ExcelFile(file_path)
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                await _create_table_from_dataframe(db, db_database.id, sheet_name, df)
        
        elif file_extension == ".json":
            with open(file_path, "r") as json_file:
                data = json.load(json_file)
                
            if isinstance(data, list):
                # 列表形式的JSON，创建单个表格
                df = pd.DataFrame(data)
                table_name = os.path.splitext(os.path.basename(file.filename))[0]
                await _create_table_from_dataframe(db, db_database.id, table_name, df)
            
            elif isinstance(data, dict):
                # 字典形式的JSON，可能包含多个表格
                for key, value in data.items():
                    if isinstance(value, list):
                        df = pd.DataFrame(value)
                        await _create_table_from_dataframe(db, db_database.id, key, df)
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_extension}"
            )
        
        return db_database
    
    finally:
        # 清理临时文件
        if os.path.exists(file_path):
            os.remove(file_path)

async def _create_table_from_dataframe(
    db: Session, 
    database_id: int, 
    table_name: str, 
    df: pd.DataFrame
) -> Table:
    """从DataFrame创建表格"""
    # 创建表格
    db_table = Table(
        name=table_name,
        database_id=database_id
    )
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    
    # 创建列
    columns = []
    for col_name in df.columns:
        col_type = _get_column_type(df[col_name])
        db_column = Column(
            name=col_name,
            type=col_type,
            table_id=db_table.id
        )
        db.add(db_column)
        columns.append(db_column)
    
    db.commit()
    
    # 刷新列对象以获取ID
    for column in columns:
        db.refresh(column)
    
    # 创建行和单元格
    for _, row_data in df.iterrows():
        db_row = Row(table_id=db_table.id)
        db.add(db_row)
        db.commit()
        db.refresh(db_row)
        
        # 创建单元格
        for i, col_name in enumerate(df.columns):
            value = row_data[col_name]
            if pd.isna(value):
                value = None
            else:
                value = str(value)
            
            db_cell = Cell(
                row_id=db_row.id,
                column_id=columns[i].id,
                value=value
            )
            db.add(db_cell)
    
    db.commit()
    return db_table

def _get_column_type(series: pd.Series) -> str:
    """根据数据推断列类型"""
    if series.dtype == 'int64':
        return 'integer'
    elif series.dtype == 'float64':
        return 'float'
    elif series.dtype == 'bool':
        return 'boolean'
    elif pd.api.types.is_datetime64_any_dtype(series):
        return 'datetime'
    else:
        return 'text'

def get_database_tables(db: Session, database_id: int) -> List[Table]:
    """获取数据库中的表格列表"""
    return db.query(Table).filter(Table.database_id == database_id).all()

def get_table_data(
    db: Session, 
    database_id: int, 
    table_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> Dict[str, Any]:
    """获取表格数据"""
    # 验证表格属于指定的数据库
    table = db.query(Table).filter(
        Table.id == table_id,
        Table.database_id == database_id
    ).first()
    
    if not table:
        raise HTTPException(
            status_code=404,
            detail="表格不存在或不属于指定数据库"
        )
    
    # 获取列信息
    columns = db.query(Column).filter(Column.table_id == table_id).all()
    
    # 获取行数据
    rows = db.query(Row).filter(Row.table_id == table_id).offset(skip).limit(limit).all()
    
    # 获取单元格数据
    result_data = []
    for row in rows:
        row_data = {}
        cells = db.query(Cell).filter(Cell.row_id == row.id).all()
        
        for cell in cells:
            # 找到对应的列
            column = next((c for c in columns if c.id == cell.column_id), None)
            if column:
                row_data[column.name] = cell.value
        
        result_data.append(row_data)
    
    # 获取总行数
    total_rows = db.query(Row).filter(Row.table_id == table_id).count()
    
    return {
        "table": {
            "id": table.id,
            "name": table.name,
            "database_id": table.database_id
        },
        "columns": [{"id": c.id, "name": c.name, "type": c.type} for c in columns],
        "data": result_data,
        "total": total_rows,
        "page": skip // limit + 1 if limit > 0 else 1,
        "limit": limit
    }
