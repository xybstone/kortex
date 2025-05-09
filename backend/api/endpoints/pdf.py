from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import uuid
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入Marker库
try:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_from_rendered
    logger.info("成功导入Marker库")
except ImportError as e:
    logger.error(f"导入Marker库失败: {str(e)}")
    raise

router = APIRouter()

@router.post("/convert-to-markdown")
async def convert_pdf_to_markdown(
    file: UploadFile = File(...)
):
    """将PDF文件转换为Markdown格式"""
    # 检查文件类型
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="只支持PDF文件")

    # 创建临时文件保存上传的PDF
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.pdf")

    logger.info(f"临时文件路径: {temp_file_path}")

    try:
        # 保存上传的文件
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        logger.info(f"文件已保存，大小: {os.path.getsize(temp_file_path)} 字节")

        # 使用Marker库转换PDF为Markdown
        logger.info("开始转换PDF为Markdown")
        logger.info("创建模型字典...")
        artifact_dict = create_model_dict()
        logger.info("模型字典创建完成")

        logger.info("初始化PDF转换器...")
        converter = PdfConverter(
            artifact_dict=artifact_dict,
        )
        logger.info("PDF转换器初始化完成")

        logger.info(f"开始转换PDF文件: {temp_file_path}")
        rendered = converter(temp_file_path)
        logger.info("PDF转换完成")

        # 从渲染结果中提取文本
        logger.info("提取转换结果")
        markdown_text, _, images = text_from_rendered(rendered)

        logger.info(f"转换完成，Markdown长度: {len(markdown_text)}, 图片数量: {len(images) if images else 0}")

        # 返回转换后的Markdown文本
        return {
            "markdown": markdown_text,
            "filename": file.filename,
            "images_count": len(images) if images else 0
        }

    except Exception as e:
        # 记录错误
        logger.error(f"PDF转换错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF转换失败: {str(e)}")

    finally:
        # 清理临时文件
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                logger.info(f"临时文件已删除: {temp_file_path}")
        except Exception as e:
            logger.error(f"删除临时文件失败: {str(e)}")
