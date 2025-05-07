import axios from 'axios';
import { Dataset } from './datasetApi';

// 临时定义数据库类型，以便兼容现有代码
export interface Database {
  id: number;
  name: string;
  description?: string;
}

// 笔记类型定义
export interface Note {
  id: number;
  title: string;
  content: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
  databases?: Database[];
  datasets?: Dataset[];
}

// 创建笔记请求
export interface CreateNoteRequest {
  title: string;
  content: string;
  database_ids?: number[];
  dataset_ids?: number[];
}

// 更新笔记请求
export interface UpdateNoteRequest {
  title?: string;
  content?: string;
  database_ids?: number[];
  dataset_ids?: number[];
}

// 笔记API服务
const noteApi = {
  // 获取笔记列表
  getNotes: async (params?: { skip?: number; limit?: number; search?: string }): Promise<Note[]> => {
    const response = await axios.get('/api/notes', { params });
    return response.data;
  },

  // 获取单个笔记
  getNote: async (id: number): Promise<Note> => {
    const response = await axios.get(`/api/notes/${id}`);
    return response.data;
  },

  // 创建笔记
  createNote: async (data: CreateNoteRequest): Promise<Note> => {
    const response = await axios.post('/api/notes', data);
    return response.data;
  },

  // 更新笔记
  updateNote: async (id: number, data: UpdateNoteRequest): Promise<Note> => {
    const response = await axios.put(`/api/notes/${id}`, data);
    return response.data;
  },

  // 删除笔记
  deleteNote: async (id: number): Promise<void> => {
    await axios.delete(`/api/notes/${id}`);
  }
};

export default noteApi;
