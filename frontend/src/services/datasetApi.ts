import api from './api';

// 数据集类型定义
export interface Dataset {
  id: number;
  name: string;
  description?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
  data_sources: DataSource[];
}

// 数据源基础类型
export interface DataSource {
  id: number;
  name: string;
  description?: string;
  type: string;
  dataset_id: number;
  processing_status: string;
  last_processed_at?: string;
  processing_error?: string;
  created_at: string;
  updated_at?: string;
}

// 数据库源类型
export interface DatabaseSource extends DataSource {
  connection_string?: string;
  database_type: string;
}

// 文件源类型
export interface FileSource extends DataSource {
  file_path: string;
  file_type: string;
  file_size?: number;
}

// URL源类型
export interface URLSource extends DataSource {
  url: string;
  crawl_depth: number;
}

// 创建数据集请求
export interface CreateDatasetRequest {
  name: string;
  description?: string;
}

// 更新数据集请求
export interface UpdateDatasetRequest {
  name?: string;
  description?: string;
}

// 创建数据库源请求
export interface CreateDatabaseSourceRequest {
  name: string;
  description?: string;
  connection_string?: string;
  database_type: string;
}

// 创建URL源请求
export interface CreateURLSourceRequest {
  name: string;
  description?: string;
  url: string;
  crawl_depth?: number;
}

// 数据集API服务
const datasetApi = {
  // 获取数据集列表
  getDatasets: async (): Promise<Dataset[]> => {
    const response = await api.get('/datasets/');
    return response.data;
  },

  // 获取单个数据集详情
  getDataset: async (id: number): Promise<Dataset> => {
    const response = await api.get(`/datasets/${id}`);
    return response.data;
  },

  // 创建数据集
  createDataset: async (dataset: CreateDatasetRequest): Promise<Dataset> => {
    const response = await api.post('/datasets/', dataset);
    return response.data;
  },

  // 更新数据集
  updateDataset: async (id: number, dataset: UpdateDatasetRequest): Promise<Dataset> => {
    const response = await api.put(`/datasets/${id}`, dataset);
    return response.data;
  },

  // 删除数据集
  deleteDataset: async (id: number): Promise<void> => {
    await api.delete(`/datasets/${id}`);
  },

  // 添加数据库源
  addDatabaseSource: async (datasetId: number, source: CreateDatabaseSourceRequest): Promise<Dataset> => {
    const response = await api.post(`/datasets/${datasetId}/database-sources`, source);
    return response.data;
  },

  // 添加文件源
  addFileSource: async (datasetId: number, name: string, description: string | null, file: File): Promise<FileSource> => {
    const formData = new FormData();
    formData.append('name', name);
    if (description) {
      formData.append('description', description);
    }
    formData.append('file', file);

    const response = await api.post(`/datasets/${datasetId}/file-sources`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // 添加URL源
  addURLSource: async (datasetId: number, source: CreateURLSourceRequest): Promise<Dataset> => {
    const response = await api.post(`/datasets/${datasetId}/url-sources`, source);
    return response.data;
  },

  // 删除数据源
  deleteDataSource: async (datasetId: number, sourceId: number): Promise<void> => {
    await api.delete(`/datasets/${datasetId}/data-sources/${sourceId}`);
  },

  // 关联笔记与数据集
  associateNote: async (datasetId: number, noteId: number): Promise<void> => {
    await api.post(`/datasets/${datasetId}/notes/${noteId}`);
  },

  // 解除笔记与数据集的关联
  disassociateNote: async (datasetId: number, noteId: number): Promise<void> => {
    await api.delete(`/datasets/${datasetId}/notes/${noteId}`);
  }
};

export default datasetApi;
