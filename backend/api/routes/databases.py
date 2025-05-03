from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.core.dependencies import get_db
from backend.models.schemas import DatabaseCreate, DatabaseUpdate, DatabaseResponse, TableResponse
from backend.core.services import database_service

router = APIRouter()

@router.post("/", response_model=DatabaseResponse, status_code=status.HTTP_201_CREATED)
def create_database(database: DatabaseCreate, db: Session = Depends(get_db)):
    """创建新数据库"""
    return database_service.create_database(db=db, database=database)

@router.get("/", response_model=List[DatabaseResponse])
def get_databases(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取数据库列表"""
    return database_service.get_databases(db=db, skip=skip, limit=limit, search=search)

@router.get("/{database_id}", response_model=DatabaseResponse)
def get_database(database_id: int, db: Session = Depends(get_db)):
    """获取单个数据库详情"""
    db_database = database_service.get_database(db=db, database_id=database_id)
    if db_database is None:
        raise HTTPException(status_code=404, detail="数据库不存在")
    return db_database

@router.put("/{database_id}", response_model=DatabaseResponse)
def update_database(database_id: int, database: DatabaseUpdate, db: Session = Depends(get_db)):
    """更新数据库"""
    db_database = database_service.get_database(db=db, database_id=database_id)
    if db_database is None:
        raise HTTPException(status_code=404, detail="数据库不存在")
    return database_service.update_database(db=db, database_id=database_id, database=database)

@router.delete("/{database_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_database(database_id: int, db: Session = Depends(get_db)):
    """删除数据库"""
    db_database = database_service.get_database(db=db, database_id=database_id)
    if db_database is None:
        raise HTTPException(status_code=404, detail="数据库不存在")
    database_service.delete_database(db=db, database_id=database_id)
    return {"detail": "数据库已删除"}

@router.post("/import", response_model=DatabaseResponse)
async def import_database(
    name: str,
    description: Optional[str] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """导入数据库文件（Excel, CSV, JSON）"""
    return await database_service.import_database(
        db=db, 
        name=name, 
        description=description, 
        file=file
    )

@router.get("/{database_id}/tables", response_model=List[TableResponse])
def get_database_tables(database_id: int, db: Session = Depends(get_db)):
    """获取数据库中的表格列表"""
    db_database = database_service.get_database(db=db, database_id=database_id)
    if db_database is None:
        raise HTTPException(status_code=404, detail="数据库不存在")
    return database_service.get_database_tables(db=db, database_id=database_id)

@router.get("/{database_id}/tables/{table_id}/data")
def get_table_data(
    database_id: int, 
    table_id: int, 
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取表格数据"""
    return database_service.get_table_data(
        db=db, 
        database_id=database_id, 
        table_id=table_id, 
        skip=skip, 
        limit=limit
    )
