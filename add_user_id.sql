-- 添加user_id字段到processing_tasks表
ALTER TABLE processing_tasks 
ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id);

-- 更新现有记录，设置默认值为1（假设ID为1的用户是默认用户）
UPDATE processing_tasks
SET user_id = 1
WHERE user_id IS NULL;
