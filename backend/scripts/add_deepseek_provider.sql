-- 添加DeepSeek提供商
INSERT INTO llm_providers (name, description, base_url, user_id, is_public, created_at)
SELECT 'DeepSeek', 'DeepSeek AI API', 'https://api.deepseek.com', id, true, NOW()
FROM users
WHERE is_admin = true
LIMIT 1
ON CONFLICT (name) DO NOTHING;

-- 添加DeepSeek模型
INSERT INTO llm_models (name, provider_id, user_id, is_active, is_public, max_tokens, temperature, created_at)
SELECT 'deepseek-chat', p.id, u.id, true, true, 4096, 0.7, NOW()
FROM llm_providers p, users u
WHERE p.name = 'DeepSeek' AND u.is_admin = true
LIMIT 1
ON CONFLICT (name, provider_id) DO NOTHING;

INSERT INTO llm_models (name, provider_id, user_id, is_active, is_public, max_tokens, temperature, created_at)
SELECT 'deepseek-reasoner', p.id, u.id, true, true, 4096, 0.7, NOW()
FROM llm_providers p, users u
WHERE p.name = 'DeepSeek' AND u.is_admin = true
LIMIT 1
ON CONFLICT (name, provider_id) DO NOTHING;

-- 添加默认角色
INSERT INTO llm_roles (name, description, system_prompt, model_id, user_id, is_default, is_public, created_at)
SELECT '默认助手', 'DeepSeek 默认助手', '你是由DeepSeek AI开发的智能助手，可以回答用户的各种问题并提供帮助。', m.id, u.id, true, true, NOW()
FROM llm_models m, users u
WHERE m.name = 'deepseek-chat' AND u.is_admin = true
LIMIT 1
ON CONFLICT (name, model_id) DO NOTHING;

INSERT INTO llm_roles (name, description, system_prompt, model_id, user_id, is_default, is_public, created_at)
SELECT '推理助手', 'DeepSeek 推理助手', '你是由DeepSeek AI开发的推理助手，擅长分析问题并提供详细的推理过程。', m.id, u.id, true, true, NOW()
FROM llm_models m, users u
WHERE m.name = 'deepseek-reasoner' AND u.is_admin = true
LIMIT 1
ON CONFLICT (name, model_id) DO NOTHING;
