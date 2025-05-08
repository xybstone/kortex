from models.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from models.schemas.token import Token, TokenData
from models.schemas.note import NoteBase, NoteCreate, NoteUpdate, NoteResponse
from models.schemas.dataset import (
    DatasetBase, DatasetCreate, DatasetUpdate, DatasetResponse, DatasetBrief,
    DataSourceBase, DataSourceCreate, DataSourceUpdate, DataSourceResponse,
    DatabaseSourceCreate, DatabaseSourceUpdate, DatabaseSourceResponse,
    FileSourceCreate, FileSourceUpdate, FileSourceResponse,
    URLSourceCreate, URLSourceUpdate, URLSourceResponse,
    ProcessingTaskBase, ProcessingTaskCreate, ProcessingTaskUpdate, ProcessingTaskResponse,
    ScheduleInfo, DependencyInfo, TaskDependencyBase, TaskDependencyCreate, TaskDependencyResponse,
    TaskExecutionHistoryBase, TaskExecutionHistoryCreate, TaskExecutionHistoryResponse
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
ConversationResponse.model_rebuild()
LLMModelResponse.model_rebuild()
LLMRoleResponse.model_rebuild()
