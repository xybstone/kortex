import api from './api';

// 处理任务类型定义
export interface ProcessingTask {
  id: number;
  name: string;
  description?: string;
  task_type: string;
  data_source_id: number;
  status: string;
  priority: number;
  parameters?: any;
  result?: any;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  progress: number;
  is_recurring: boolean;

  // 调度信息
  schedule_type?: string;
  schedule_value?: string;
  next_run_time?: string;
  last_run_time?: string;
  run_count?: number;
  max_runs?: number;

  created_at: string;
  updated_at?: string;
  user_id?: number;
}

// 调度信息
export interface ScheduleInfo {
  schedule_type: string; // once, daily, weekly, monthly, cron
  schedule_value: string; // 调度值，如cron表达式或特定时间
  max_runs?: number; // 最大运行次数，为空表示无限制
}

// 创建处理任务请求
export interface CreateProcessingTaskRequest {
  name: string;
  description?: string;
  task_type: string;
  data_source_id: number;
  priority?: number;
  parameters?: any;
  is_recurring?: boolean;
  schedule_info?: ScheduleInfo;
}

// 更新处理任务请求
export interface UpdateProcessingTaskRequest {
  name?: string;
  description?: string;
  priority?: number;
  status?: string;
  parameters?: any;
  is_recurring?: boolean;
  schedule_info?: ScheduleInfo;
}

// 处理任务API服务
const processingApi = {
  // 获取处理任务列表
  getTasks: async (params?: {
    skip?: number;
    limit?: number;
    search?: string;
    status?: string;
    data_source_id?: number;
  }): Promise<ProcessingTask[]> => {
    const response = await api.get('/processing/', { params });
    return response.data;
  },

  // 获取单个处理任务详情
  getTask: async (id: number): Promise<ProcessingTask> => {
    const response = await api.get(`/processing/${id}`);
    return response.data;
  },

  // 创建处理任务
  createTask: async (task: CreateProcessingTaskRequest): Promise<ProcessingTask> => {
    const response = await api.post('/processing/', task);
    return response.data;
  },

  // 更新处理任务
  updateTask: async (id: number, task: UpdateProcessingTaskRequest): Promise<ProcessingTask> => {
    const response = await api.put(`/processing/${id}`, task);
    return response.data;
  },

  // 取消处理任务
  cancelTask: async (id: number): Promise<void> => {
    await api.post(`/processing/${id}/cancel`);
  },

  // 删除处理任务
  deleteTask: async (id: number): Promise<void> => {
    await api.delete(`/processing/${id}`);
  },

  // 设置任务调度
  scheduleTask: async (id: number, scheduleInfo: ScheduleInfo): Promise<ProcessingTask> => {
    const response = await api.post(`/processing/${id}/schedule`, scheduleInfo);
    return response.data;
  },

  // 取消任务调度
  cancelTaskSchedule: async (id: number): Promise<void> => {
    await api.post(`/processing/${id}/cancel-schedule`);
  }
};

export default processingApi;
