#!/bin/bash

echo "开始初始化数据库..."

# 检查PostgreSQL容器是否运行
if ! docker ps | grep -q kortex-db; then
    echo "错误: PostgreSQL容器(kortex-db)未运行"
    exit 1
fi

echo "PostgreSQL容器正在运行"

# 创建初始化SQL脚本
cat > init.sql << EOF
-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 创建笔记表
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 创建数据库表
CREATE TABLE IF NOT EXISTS databases (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 检查是否已存在默认用户
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM users WHERE email = 'user@example.com') THEN
        -- 创建默认用户 (密码: password)
        INSERT INTO users (email, hashed_password, full_name, is_active, is_admin)
        VALUES ('user@example.com', '\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '测试用户', TRUE, FALSE);
    END IF;
END
\$\$;
EOF

# 将SQL脚本复制到容器中
docker cp init.sql kortex-db:/tmp/init.sql

# 在容器中执行SQL脚本
echo "执行SQL初始化脚本..."
docker exec -i kortex-db psql -U postgres -d kortex -f /tmp/init.sql

# 检查表是否创建成功
echo "验证数据库表..."
docker exec -i kortex-db psql -U postgres -d kortex -c "\dt"

# 检查用户是否创建成功
echo "验证默认用户..."
docker exec -i kortex-db psql -U postgres -d kortex -c "SELECT id, email, full_name FROM users"

# 清理临时文件
rm init.sql

echo "数据库初始化完成"
