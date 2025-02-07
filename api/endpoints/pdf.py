from fastapi import APIRouter, UploadFile, File
import cognee
import asyncio
import pathlib

router = APIRouter()

@router.post("/process_pdf")
async def process_pdf(file: UploadFile = File(...)):
    """处理PDF文件并将内容添加到Cognee"""
    file_location = f"temp/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    dataset_name = "pdf_dataset"
    await cognee.add([file_location], dataset_name)
    await cognee.cognify()

    return {"message": "PDF processed and added to Cognee"}
