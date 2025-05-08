import api from './api';

// 自然语言处理请求类型定义
export interface NLProcessingRequest {
  instruction: string;
  data_source_id: number;
}

// 自然语言处理响应类型定义
export interface NLProcessingResponse {
  success: boolean;
  task_id?: number;
  task_type?: string;
  parameters?: any;
  confidence?: number;
  reasoning?: string;
  error?: string;
}

// 自然语言分析请求类型定义
export interface NLAnalysisRequest {
  instruction: string;
}

// 自然语言分析响应类型定义
export interface NLAnalysisResponse {
  task_type: string;
  parameters: any;
  confidence: number;
  reasoning: string;
}

/**
 * 自然语言处理API
 */
const nlpApi = {
  /**
   * 处理自然语言指令
   * @param request 处理请求
   * @returns 处理响应
   */
  async processInstruction(request: NLProcessingRequest): Promise<NLProcessingResponse> {
    const response = await api.post<NLProcessingResponse>('/nlp/process', request);
    return response.data;
  },

  /**
   * 分析自然语言指令
   * @param request 分析请求
   * @returns 分析响应
   */
  async analyzeInstruction(request: NLAnalysisRequest): Promise<NLAnalysisResponse> {
    const response = await api.post<NLAnalysisResponse>('/nlp/analyze', request);
    return response.data;
  }
};

export default nlpApi;
