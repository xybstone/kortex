-- 添加wait_for_dependencies字段到processing_tasks表
ALTER TABLE processing_tasks 
ADD COLUMN IF NOT EXISTS wait_for_dependencies BOOLEAN DEFAULT TRUE;

-- 更新现有记录，设置默认值
UPDATE processing_tasks
SET wait_for_dependencies = TRUE
WHERE wait_for_dependencies IS NULL;
