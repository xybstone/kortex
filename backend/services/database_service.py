from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import UploadFile, HTTPException
import pandas as pd
import json
import os
import tempfile

from models.domain.database import Database, Table, Column
from models.schemas.database import (
    DatabaseCreate, DatabaseUpdate, DatabaseResponse,
    TableResponse, ColumnResponse
)

def create_database(db: Session, database: DatabaseCreate) -> DatabaseResponse:
    """创建新数据库"""
    db_database = Database(
        name=database.name,
        description=database.description,
        user_id=database.user_id
    )
    db.add(db_database)
    db.commit()
    db.refresh(db_database)
    
    # 转换为响应模型
    return DatabaseResponse(
        id=db_database.id,
        name=db_database.name,
        description=db_database.description,
        user_id=db_database.user_id,
        created_at=db_database.created_at,
        updated_at=db_database.updated_at
    )

def get_databases(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    user_id: Optional[int] = None
) -> List[DatabaseResponse]:
    """获取数据库列表"""
    query = db.query(Database)
    
    # 如果提供了用户ID，只返回该用户的数据库
    if user_id:
        query = query.filter(Database.user_id == user_id)
    
    # 如果提供了搜索关键词，在名称和描述中搜索
    if search:
        query = query.filter(
            (Database.name.ilike(f"%{search}%")) |
            (Database.description.ilike(f"%{search}%"))
        )
    
    # 获取分页结果
    databases = query.order_by(Database.name).offset(skip).limit(limit).all()
    
    # 转换为响应模型
    return [
        DatabaseResponse(
            id=database.id,
            name=database.name,
            description=database.description,
            user_id=database.user_id,
            created_at=database.created_at,
            updated_at=database.updated_at
        )
        for database in databases
    ]

def get_database(db: Session, database_id: int) -> Optional[DatabaseResponse]:
    """获取单个数据库详情"""
    database = db.query(Database).filter(Database.id == database_id).first()
    if not database:
        return None
    
    # 转换为响应模型
    return DatabaseResponse(
        id=database.id,
        name=database.name,
        description=database.description,
        user_id=database.user_id,
        created_at=database.created_at,
        updated_at=database.updated_at
    )

def update_database(
    db: Session, 
    database_id: int, 
    database_update: DatabaseUpdate
) -> Optional[DatabaseResponse]:
    """更新数据库"""
    db_database = db.query(Database).filter(Database.id == database_id).first()
    if not db_database:
        return None
    
    # 更新数据库信息
    update_data = database_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_database, key, value)
    
    db.commit()
    db.refresh(db_database)
    
    # 转换为响应模型
    return DatabaseResponse(
        id=db_database.id,
        name=db_database.name,
        description=db_database.description,
        user_id=db_database.user_id,
        created_at=db_database.created_at,
        updated_at=db_database.updated_at
    )

def delete_database(db: Session, database_id: int) -> None:
    """删除数据库"""
    db_database = db.query(Database).filter(Database.id == database_id).first()
    if db_database:
        db.delete(db_database)
        db.commit()

def get_tables(db: Session, database_id: int) -> List[TableResponse]:
    """获取数据库的表格列表"""
    tables = db.query(Table).filter(Table.database_id == database_id).all()
    
    # 转换为响应模型
    return [
        TableResponse(
            id=table.id,
            name=table.name,
            database_id=table.database_id,
            columns=[
                ColumnResponse(
                    id=column.id,
                    name=column.name,
                    type=column.type
                )
                for column in table.columns
            ]
        )
        for table in tables
    ]

def get_table(db: Session, table_id: int) -> Optional[TableResponse]:
    """获取单个表格详情"""
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        return None
    
    # 转换为响应模型
    return TableResponse(
        id=table.id,
        name=table.name,
        database_id=table.database_id,
        columns=[
            ColumnResponse(
                id=column.id,
                name=column.name,
                type=column.type
            )
            for column in table.columns
        ]
    )

async def import_database(
    db: Session,
    name: str,
    description: Optional[str],
    file: UploadFile,
    user_id: int
) -> DatabaseResponse:
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
    file_content = await file.read()
    
    # 根据文件类型处理数据
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    try:
        if file_extension == '.csv':
            # 处理CSV文件
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            df = pd.read_csv(temp_file_path)
            os.unlink(temp_file_path)
            
            # 创建表格
            table = Table(name=os.path.splitext(file.filename)[0], database_id=db_database.id)
            db.add(table)
            db.commit()
            db.refresh(table)
            
            # 创建列
            for column_name, dtype in df.dtypes.items():
                column = Column(
                    name=column_name,
                    type=str(dtype),
                    table_id=table.id
                )
                db.add(column)
            
            db.commit()
            
        elif file_extension in ['.xlsx', '.xls']:
            # 处理Excel文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            # 读取所有工作表
            excel_file = pd.ExcelFile(temp_file_path)
            os.unlink(temp_file_path)
            
            for sheet_name in excel_file.sheet_names:
                df = excel_file.parse(sheet_name)
                
                # 创建表格（使用工作表名称）
                table = Table(name=sheet_name, database_id=db_database.id)
                db.add(table)
                db.commit()
                db.refresh(table)
                
                # 创建列
                for column_name, dtype in df.dtypes.items():
                    column = Column(
                        name=column_name,
                        type=str(dtype),
                        table_id=table.id
                    )
                    db.add(column)
                
                db.commit()
                
        elif file_extension == '.json':
            # 处理JSON文件
            json_data = json.loads(file_content)
            
            # 如果是列表，创建单个表格
            if isinstance(json_data, list) and len(json_data) > 0:
                # 创建表格
                table = Table(name=os.path.splitext(file.filename)[0], database_id=db_database.id)
                db.add(table)
                db.commit()
                db.refresh(table)
                
                # 从第一个对象获取列
                if isinstance(json_data[0], dict):
                    for key in json_data[0].keys():
                        column = Column(
                            name=key,
                            type="string",  # 默认类型
                            table_id=table.id
                        )
                        db.add(column)
                    
                    db.commit()
            
            # 如果是对象，每个键创建一个表格
            elif isinstance(json_data, dict):
                for key, value in json_data.items():
                    # 创建表格
                    table = Table(name=key, database_id=db_database.id)
                    db.add(table)
                    db.commit()
                    db.refresh(table)
                    
                    # 如果值是列表且非空，从第一个对象获取列
                    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        for col_key in value[0].keys():
                            column = Column(
                                name=col_key,
                                type="string",  # 默认类型
                                table_id=table.id
                            )
                            db.add(column)
                        
                        db.commit()
        
        else:
            # 不支持的文件类型
            db.delete(db_database)
            db.commit()
            raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    except Exception as e:
        # 发生错误，回滚事务
        db.rollback()
        raise HTTPException(status_code=500, detail=f"导入数据库失败: {str(e)}")
    
    # 刷新数据库对象
    db.refresh(db_database)
    
    # 转换为响应模型
    return DatabaseResponse(
        id=db_database.id,
        name=db_database.name,
        description=db_database.description,
        user_id=db_database.user_id,
        created_at=db_database.created_at,
        updated_at=db_database.updated_at
    )
