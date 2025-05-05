from fastapi import Request
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    """记录请求和响应的中间件"""
    start_time = time.time()
    
    # 记录请求信息
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # 处理请求
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录响应信息
    logger.info(f"Response: {response.status_code} - Took {process_time:.4f}s")
    
    return response
