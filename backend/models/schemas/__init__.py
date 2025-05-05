from models.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from models.schemas.token import Token, TokenData
from models.schemas.note import NoteBase, NoteCreate, NoteUpdate, NoteResponse
from models.schemas.database import (
    DatabaseBase, DatabaseCreate, DatabaseUpdate, DatabaseResponse, DatabaseBrief,
    TableBase, TableBrief, TableResponse,
    ColumnBase, ColumnResponse
)
from models.schemas.llm import (
    LLMRequest, LLMResponse, DatabaseAnalysisRequest,
    LLMProviderBase, LLMProviderCreate, LLMProviderUpdate, LLMProviderResponse,
    LLMModelBase, LLMModelCreate, LLMModelUpdate, LLMModelResponse,
    LLMRoleBase, LLMRoleCreate, LLMRoleUpdate, LLMRoleResponse
)
from models.schemas.conversation import (
    MessageBase, MessageCreate, MessageResponse,
    ConversationBase, ConversationCreate, ConversationResponse
)

# 更新引用
NoteResponse.model_rebuild()
DatabaseResponse.model_rebuild()
TableResponse.model_rebuild()
ConversationResponse.model_rebuild()
LLMModelResponse.model_rebuild()
LLMRoleResponse.model_rebuild()
