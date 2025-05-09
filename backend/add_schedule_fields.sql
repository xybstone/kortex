-- 添加调度相关字段到processing_tasks表
ALTER TABLE processing_tasks 
ADD COLUMN IF NOT EXISTS schedule_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS schedule_value VARCHAR(255),
ADD COLUMN IF NOT EXISTS next_run_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS last_run_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS run_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS max_runs INTEGER;

-- 更新现有记录，设置默认值
UPDATE processing_tasks
SET schedule_type = 'once',
    schedule_value = '',
    run_count = 0
WHERE schedule_type IS NULL;
