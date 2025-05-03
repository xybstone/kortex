import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// LLM供应商相关API
export const llmProviderApi = {
  // 获取供应商列表
  getProviders: async (params?: { skip?: number; limit?: number; search?: string }) => {
    const response = await api.get('/llm-config/providers', { params });
    return response.data;
  },
  
  // 获取单个供应商
  getProvider: async (id: number) => {
    const response = await api.get(`/llm-config/providers/${id}`);
    return response.data;
  },
  
  // 创建供应商
  createProvider: async (data: any) => {
    const response = await api.post('/llm-config/providers', data);
    return response.data;
  },
  
  // 更新供应商
  updateProvider: async (id: number, data: any) => {
    const response = await api.put(`/llm-config/providers/${id}`, data);
    return response.data;
  },
  
  // 删除供应商
  deleteProvider: async (id: number) => {
    const response = await api.delete(`/llm-config/providers/${id}`);
    return response.data;
  },
};

// LLM模型相关API
export const llmModelApi = {
  // 获取模型列表
  getModels: async (params?: { skip?: number; limit?: number; search?: string; provider_id?: number }) => {
    const response = await api.get('/llm-config/models', { params });
    return response.data;
  },
  
  // 获取单个模型
  getModel: async (id: number) => {
    const response = await api.get(`/llm-config/models/${id}`);
    return response.data;
  },
  
  // 创建模型
  createModel: async (data: any) => {
    const response = await api.post('/llm-config/models', data);
    return response.data;
  },
  
  // 更新模型
  updateModel: async (id: number, data: any) => {
    const response = await api.put(`/llm-config/models/${id}`, data);
    return response.data;
  },
  
  // 删除模型
  deleteModel: async (id: number) => {
    const response = await api.delete(`/llm-config/models/${id}`);
    return response.data;
  },
};

// LLM角色相关API
export const llmRoleApi = {
  // 获取角色列表
  getRoles: async (params?: { skip?: number; limit?: number; search?: string; model_id?: number }) => {
    const response = await api.get('/llm-config/roles', { params });
    return response.data;
  },
  
  // 获取单个角色
  getRole: async (id: number) => {
    const response = await api.get(`/llm-config/roles/${id}`);
    return response.data;
  },
  
  // 创建角色
  createRole: async (data: any) => {
    const response = await api.post('/llm-config/roles', data);
    return response.data;
  },
  
  // 更新角色
  updateRole: async (id: number, data: any) => {
    const response = await api.put(`/llm-config/roles/${id}`, data);
    return response.data;
  },
  
  // 删除角色
  deleteRole: async (id: number) => {
    const response = await api.delete(`/llm-config/roles/${id}`);
    return response.data;
  },
  
  // 获取模型的默认角色
  getDefaultRole: async (modelId: number) => {
    const response = await api.get(`/llm-config/models/${modelId}/default-role`);
    return response.data;
  },
};

// 对话相关API
export const conversationApi = {
  // 获取笔记的对话列表
  getNoteConversations: async (noteId: number) => {
    const response = await api.get(`/conversations/note/${noteId}`);
    return response.data;
  },
  
  // 获取对话消息
  getConversationMessages: async (conversationId: number) => {
    const response = await api.get(`/conversations/${conversationId}/messages`);
    return response.data;
  },
  
  // 创建对话
  createConversation: async (data: { note_id: number; role_id: number }) => {
    const response = await api.post('/conversations', data);
    return response.data;
  },
  
  // 发送消息
  sendMessage: async (conversationId: number, message: string) => {
    const response = await api.post(`/conversations/${conversationId}/messages`, { message });
    return response.data;
  },
  
  // 删除对话
  deleteConversation: async (conversationId: number) => {
    const response = await api.delete(`/conversations/${conversationId}`);
    return response.data;
  },
};

export default api;
