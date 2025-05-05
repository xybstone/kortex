# 服务模块初始化文件
# 导入各个服务模块
from services.auth_service import (
    verify_password, get_password_hash, get_user_by_email,
    create_user, update_user, authenticate_user, create_access_token
)
from utils.security import encrypt_text, decrypt_text

# 导入LLM配置服务模块
from services.llm_config_service import (
    # 供应商相关
    create_provider, get_providers, get_provider, update_provider, delete_provider,
    # 模型相关
    create_model, get_models, get_model, update_model, delete_model,
    # 角色相关
    create_role, get_roles, get_role, update_role, delete_role
)

# 导入对话服务模块
from services.conversation_service import (
    create_conversation, get_conversations, get_conversation, delete_conversation,
    get_messages, create_message, send_message_and_get_response
)

# 创建服务命名空间
class AuthService:
    pass

class NoteService:
    pass

class DatabaseService:
    pass

class LLMService:
    pass

class LLMConfigService:
    pass

class ConversationService:
    pass

# 创建服务实例
auth_service = AuthService()
note_service = NoteService()
database_service = DatabaseService()
llm_service = LLMService()
llm_config_service = LLMConfigService()
conversation_service = ConversationService()

# 将函数绑定到服务实例
auth_service.verify_password = verify_password
auth_service.get_password_hash = get_password_hash
auth_service.get_user_by_email = get_user_by_email
auth_service.create_user = create_user
auth_service.update_user = update_user
auth_service.authenticate_user = authenticate_user
auth_service.create_access_token = create_access_token

# 将LLM配置服务函数绑定到llm_config_service实例
# 供应商相关
llm_config_service.create_provider = create_provider
llm_config_service.get_providers = get_providers
llm_config_service.get_provider = get_provider
llm_config_service.update_provider = update_provider
llm_config_service.delete_provider = delete_provider
# 模型相关
llm_config_service.create_model = create_model
llm_config_service.get_models = get_models
llm_config_service.get_model = get_model
llm_config_service.update_model = update_model
llm_config_service.delete_model = delete_model
# 角色相关
llm_config_service.create_role = create_role
llm_config_service.get_roles = get_roles
llm_config_service.get_role = get_role
llm_config_service.update_role = update_role
llm_config_service.delete_role = delete_role

# 将对话服务函数绑定到conversation_service实例
conversation_service.create_conversation = create_conversation
conversation_service.get_conversations = get_conversations
conversation_service.get_conversation = get_conversation
conversation_service.delete_conversation = delete_conversation
conversation_service.get_messages = get_messages
conversation_service.create_message = create_message
conversation_service.send_message_and_get_response = send_message_and_get_response
