import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import axios from 'axios';
import DeleteConfirmDialog from './DeleteConfirmDialog';

// 定义接口
interface LLMProvider {
  id: number;
  name: string;
  description?: string;
  base_url?: string;
  is_public: boolean;
}

interface LLMModel {
  id: number;
  name: string;
  provider_id: number;
  api_key?: string;
  is_active: boolean;
  is_public: boolean;
  max_tokens: number;
  temperature: number;
}

interface LLMModelsProps {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

export default function LLMModels({ onSuccess, onError }: LLMModelsProps) {
  // 数据状态
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [models, setModels] = useState<LLMModel[]>([]);

  // 加载和错误状态
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 对话框状态
  const [modelDialogOpen, setModelDialogOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  // 编辑项
  const [editingModel, setEditingModel] = useState<LLMModel | null>(null);
  const [deleteItem, setDeleteItem] = useState<{type: string, id: number} | null>(null);

  // 表单状态
  const [modelForm, setModelForm] = useState({
    name: '',
    provider_id: 0,
    api_key: '',
    is_active: true,
    is_public: false,
    max_tokens: 4096,
    temperature: 0.7
  });

  // 显示API密钥
  const [showApiKey, setShowApiKey] = useState<{[key: number]: boolean}>({});

  // 加载数据
  useEffect(() => {
    fetchProviders();
  }, []);

  useEffect(() => {
    if (providers.length > 0) {
      fetchModels();
    }
  }, [providers]);

  // 获取供应商列表
  const fetchProviders = async () => {
    setLoading(true);
    setError('');

    try {
      // 使用模拟数据，因为后端API需要认证
      // const response = await axios.get('http://localhost:8000/api/llm-config/providers');
      // setProviders(response.data);

      // 模拟数据
      const mockProviders = [
        {id: 1, name: "OpenAI", description: "OpenAI API", base_url: "https://api.openai.com/v1", is_public: true},
        {id: 2, name: "Anthropic", description: "Anthropic Claude API", base_url: "https://api.anthropic.com", is_public: true},
        {id: 3, name: "Gemini", description: "Google Gemini API", base_url: "https://generativelanguage.googleapis.com", is_public: true},
        {id: 4, name: "DeepSeek", description: "DeepSeek AI API", base_url: "https://api.deepseek.com", is_public: true}
      ];
      setProviders(mockProviders);
    } catch (err: any) {
      console.error('获取供应商列表失败:', err);
      setError(err.response?.data?.detail || '获取供应商列表失败');
      onError(err.response?.data?.detail || '获取供应商列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取模型列表
  const fetchModels = async () => {
    setLoading(true);
    setError('');

    try {
      // 使用模拟数据，因为后端API需要认证
      // const response = await axios.get('http://localhost:8000/api/llm-config/models');
      // setModels(response.data);

      // 模拟数据
      const mockModels = [
        {id: 1, name: "gpt-4", provider_id: 1, api_key: "sk-***********", is_active: true, is_public: true, max_tokens: 8192, temperature: 0.7},
        {id: 2, name: "gpt-3.5-turbo", provider_id: 1, api_key: "sk-***********", is_active: true, is_public: true, max_tokens: 4096, temperature: 0.7},
        {id: 3, name: "claude-3-opus", provider_id: 2, api_key: "sk_ant-***********", is_active: true, is_public: true, max_tokens: 100000, temperature: 0.7},
        {id: 4, name: "deepseek-chat", provider_id: 4, api_key: "sk-***********", is_active: true, is_public: true, max_tokens: 4096, temperature: 0.7},
        {id: 5, name: "deepseek-reasoner", provider_id: 4, api_key: "sk-***********", is_active: true, is_public: true, max_tokens: 4096, temperature: 0.7}
      ];
      setModels(mockModels);
    } catch (err: any) {
      console.error('获取模型列表失败:', err);
      setError(err.response?.data?.detail || '获取模型列表失败');
      onError(err.response?.data?.detail || '获取模型列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 模型相关处理函数
  const handleAddModel = () => {
    setEditingModel(null);
    setModelForm({
      name: '',
      provider_id: providers[0]?.id || 0,
      api_key: '',
      is_active: true,
      is_public: false,
      max_tokens: 4096,
      temperature: 0.7
    });
    setModelDialogOpen(true);
  };

  const handleEditModel = (model: LLMModel) => {
    setEditingModel(model);
    setModelForm({
      name: model.name,
      provider_id: model.provider_id,
      api_key: model.api_key || '',
      is_active: model.is_active,
      is_public: model.is_public,
      max_tokens: model.max_tokens,
      temperature: model.temperature
    });
    setModelDialogOpen(true);
  };

  const handleDeleteModel = (model: LLMModel) => {
    setDeleteItem({ type: 'model', id: model.id });
    setDeleteConfirmOpen(true);
  };

  const handleModelSubmit = async () => {
    try {
      if (editingModel) {
        // 更新模型
        await axios.put(`http://localhost:8000/api/llm-config/models/${editingModel.id}`, modelForm);

        // 更新本地状态
        setModels(models.map(m =>
          m.id === editingModel.id ? { ...m, ...modelForm } : m
        ));

        onSuccess('模型更新成功');
      } else {
        // 创建新模型
        const response = await axios.post('http://localhost:8000/api/llm-config/models', modelForm);

        // 更新本地状态
        setModels([...models, response.data]);

        onSuccess('模型创建成功');
      }

      setModelDialogOpen(false);
    } catch (err: any) {
      console.error('保存模型失败:', err);
      onError(err.response?.data?.detail || '操作失败，请稍后再试');
    }
  };

  // 删除确认处理
  const handleConfirmDelete = async () => {
    if (!deleteItem) return;

    try {
      await axios.delete(`http://localhost:8000/api/llm-config/models/${deleteItem.id}`);
      setModels(models.filter(m => m.id !== deleteItem.id));
      onSuccess('模型删除成功');
    } catch (err: any) {
      console.error('删除失败:', err);
      onError(err.response?.data?.detail || '删除失败，请稍后再试');
    } finally {
      setDeleteConfirmOpen(false);
      setDeleteItem(null);
    }
  };

  // 切换API密钥可见性
  const toggleApiKeyVisibility = (modelId: number) => {
    setShowApiKey({
      ...showApiKey,
      [modelId]: !showApiKey[modelId]
    });
  };

  // 获取供应商名称
  const getProviderName = (providerId: number) => {
    const provider = providers.find(p => p.id === providerId);
    return provider ? provider.name : '未知供应商';
  };

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddModel}
          disabled={providers.length === 0}
        >
          添加模型
        </Button>
      </Box>

      {providers.length === 0 ? (
        <Alert severity="warning">
          请先添加供应商
        </Alert>
      ) : loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      ) : (
        <List>
          {models.map((model) => (
            <ListItem key={model.id} divider>
              <ListItemText
                primary={model.name}
                secondary={
                  <>
                    供应商: {getProviderName(model.provider_id)}
                    <br />
                    API密钥: {showApiKey[model.id] ? model.api_key : '••••••••••••'}
                    <br />
                    状态: {model.is_active ? '启用' : '禁用'}
                    <br />
                    最大Token: {model.max_tokens}, 温度: {model.temperature}
                  </>
                }
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => toggleApiKeyVisibility(model.id)}>
                  {showApiKey[model.id] ? <VisibilityOffIcon /> : <VisibilityIcon />}
                </IconButton>
                <IconButton edge="end" onClick={() => handleEditModel(model)}>
                  <EditIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteModel(model)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
          {models.length === 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              暂无模型，请添加模型
            </Alert>
          )}
        </List>
      )}

      {/* 模型对话框 */}
      <Dialog
        open={modelDialogOpen}
        onClose={() => setModelDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {editingModel ? '编辑模型' : '添加模型'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="模型名称"
            fullWidth
            value={modelForm.name}
            onChange={(e) => setModelForm({...modelForm, name: e.target.value})}
            required
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>供应商</InputLabel>
            <Select
              value={modelForm.provider_id}
              onChange={(e) => setModelForm({...modelForm, provider_id: Number(e.target.value)})}
              label="供应商"
            >
              {providers.map((provider) => (
                <MenuItem key={provider.id} value={provider.id}>
                  {provider.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            label="API密钥"
            fullWidth
            value={modelForm.api_key}
            onChange={(e) => setModelForm({...modelForm, api_key: e.target.value})}
            type="password"
            sx={{ mb: 2 }}
          />
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              margin="dense"
              label="最大Token"
              type="number"
              value={modelForm.max_tokens}
              onChange={(e) => setModelForm({...modelForm, max_tokens: Number(e.target.value)})}
              sx={{ flex: 1 }}
            />
            <TextField
              margin="dense"
              label="温度"
              type="number"
              value={modelForm.temperature}
              onChange={(e) => setModelForm({...modelForm, temperature: Number(e.target.value)})}
              inputProps={{ step: 0.1, min: 0, max: 1 }}
              sx={{ flex: 1 }}
            />
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={modelForm.is_active}
                  onChange={(e) => setModelForm({...modelForm, is_active: e.target.checked})}
                />
              }
              label="启用"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={modelForm.is_public}
                  onChange={(e) => setModelForm({...modelForm, is_public: e.target.checked})}
                />
              }
              label="公开（其他用户可见）"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setModelDialogOpen(false)}>取消</Button>
          <Button onClick={handleModelSubmit} variant="contained">保存</Button>
        </DialogActions>
      </Dialog>

      {/* 删除确认对话框 */}
      <DeleteConfirmDialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        onConfirm={handleConfirmDelete}
        itemType="model"
        message="确定要删除这个模型吗？相关的角色也会被删除。"
      />
    </>
  );
}
