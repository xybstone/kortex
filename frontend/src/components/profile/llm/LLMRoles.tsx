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
import axios from 'axios';
import DeleteConfirmDialog from './DeleteConfirmDialog';

// 定义接口
interface LLMProvider {
  id: number;
  name: string;
}

interface LLMModel {
  id: number;
  name: string;
  provider_id: number;
}

interface LLMRole {
  id: number;
  name: string;
  description?: string;
  system_prompt: string;
  model_id: number;
  is_default: boolean;
  is_public: boolean;
}

interface LLMRolesProps {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

export default function LLMRoles({ onSuccess, onError }: LLMRolesProps) {
  // 数据状态
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [models, setModels] = useState<LLMModel[]>([]);
  const [roles, setRoles] = useState<LLMRole[]>([]);

  // 加载和错误状态
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 对话框状态
  const [roleDialogOpen, setRoleDialogOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  // 编辑项
  const [editingRole, setEditingRole] = useState<LLMRole | null>(null);
  const [deleteItem, setDeleteItem] = useState<{type: string, id: number} | null>(null);

  // 表单状态
  const [roleForm, setRoleForm] = useState({
    name: '',
    description: '',
    system_prompt: '',
    model_id: 0,
    is_default: false,
    is_public: false
  });

  // 加载数据
  useEffect(() => {
    fetchProviders();
  }, []);

  useEffect(() => {
    if (providers.length > 0) {
      fetchModels();
    }
  }, [providers]);

  useEffect(() => {
    if (models.length > 0) {
      fetchRoles();
    }
  }, [models]);

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
        {id: 3, name: "Gemini", description: "Google Gemini API", base_url: "https://generativelanguage.googleapis.com", is_public: true}
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
        {id: 3, name: "claude-3-opus", provider_id: 2, api_key: "sk_ant-***********", is_active: true, is_public: true, max_tokens: 100000, temperature: 0.7}
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

  // 获取角色列表
  const fetchRoles = async () => {
    setLoading(true);
    setError('');

    try {
      // 使用模拟数据，因为后端API需要认证
      // const response = await axios.get('http://localhost:8000/api/llm-config/roles');
      // setRoles(response.data);

      // 模拟数据
      const mockRoles = [
        {id: 1, name: "通用助手", description: "通用AI助手", system_prompt: "你是一个有用的AI助手。", model_id: 1, is_default: true, is_public: true},
        {id: 2, name: "程序员", description: "编程助手", system_prompt: "你是一个专业的程序员，擅长解决编程问题。", model_id: 1, is_default: false, is_public: true},
        {id: 3, name: "写作助手", description: "写作辅助", system_prompt: "你是一个专业的写作助手，擅长文学创作和文章润色。", model_id: 2, is_default: true, is_public: true}
      ];
      setRoles(mockRoles);
    } catch (err: any) {
      console.error('获取角色列表失败:', err);
      setError(err.response?.data?.detail || '获取角色列表失败');
      onError(err.response?.data?.detail || '获取角色列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 角色相关处理函数
  const handleAddRole = () => {
    setEditingRole(null);
    setRoleForm({
      name: '',
      description: '',
      system_prompt: '',
      model_id: models[0]?.id || 0,
      is_default: false,
      is_public: false
    });
    setRoleDialogOpen(true);
  };

  const handleEditRole = (role: LLMRole) => {
    setEditingRole(role);
    setRoleForm({
      name: role.name,
      description: role.description || '',
      system_prompt: role.system_prompt,
      model_id: role.model_id,
      is_default: role.is_default,
      is_public: role.is_public
    });
    setRoleDialogOpen(true);
  };

  const handleDeleteRole = (role: LLMRole) => {
    setDeleteItem({ type: 'role', id: role.id });
    setDeleteConfirmOpen(true);
  };

  const handleRoleSubmit = async () => {
    try {
      if (editingRole) {
        // 更新角色
        await axios.put(`http://localhost:8000/api/llm-config/roles/${editingRole.id}`, roleForm);

        // 更新本地状态
        setRoles(roles.map(r =>
          r.id === editingRole.id ? { ...r, ...roleForm } : r
        ));

        onSuccess('角色更新成功');
      } else {
        // 创建新角色
        const response = await axios.post('http://localhost:8000/api/llm-config/roles', roleForm);

        // 更新本地状态
        setRoles([...roles, response.data]);

        onSuccess('角色创建成功');
      }

      setRoleDialogOpen(false);
    } catch (err: any) {
      console.error('保存角色失败:', err);
      onError(err.response?.data?.detail || '操作失败，请稍后再试');
    }
  };

  // 删除确认处理
  const handleConfirmDelete = async () => {
    if (!deleteItem) return;

    try {
      await axios.delete(`http://localhost:8000/api/llm-config/roles/${deleteItem.id}`);
      setRoles(roles.filter(r => r.id !== deleteItem.id));
      onSuccess('角色删除成功');
    } catch (err: any) {
      console.error('删除失败:', err);
      onError(err.response?.data?.detail || '删除失败，请稍后再试');
    } finally {
      setDeleteConfirmOpen(false);
      setDeleteItem(null);
    }
  };

  // 获取供应商名称
  const getProviderName = (providerId: number) => {
    const provider = providers.find(p => p.id === providerId);
    return provider ? provider.name : '未知供应商';
  };

  // 获取模型名称
  const getModelName = (modelId: number) => {
    const model = models.find(m => m.id === modelId);
    return model ? model.name : '未知模型';
  };

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddRole}
          disabled={models.length === 0}
        >
          添加角色
        </Button>
      </Box>

      {models.length === 0 ? (
        <Alert severity="warning">
          请先添加模型
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
          {roles.map((role) => (
            <ListItem key={role.id} divider>
              <ListItemText
                primary={
                  <>
                    {role.name}
                    {role.is_default && (
                      <Typography component="span" color="primary" sx={{ ml: 1 }}>
                        (默认)
                      </Typography>
                    )}
                  </>
                }
                secondary={
                  <>
                    {role.description}
                    <br />
                    模型: {getModelName(role.model_id)}
                    <br />
                    系统提示词: {role.system_prompt.substring(0, 50)}...
                  </>
                }
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => handleEditRole(role)}>
                  <EditIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteRole(role)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
          {roles.length === 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              暂无角色，请添加角色
            </Alert>
          )}
        </List>
      )}

      {/* 角色对话框 */}
      <Dialog
        open={roleDialogOpen}
        onClose={() => setRoleDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {editingRole ? '编辑角色' : '添加角色'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="角色名称"
            fullWidth
            value={roleForm.name}
            onChange={(e) => setRoleForm({...roleForm, name: e.target.value})}
            required
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="描述"
            fullWidth
            value={roleForm.description}
            onChange={(e) => setRoleForm({...roleForm, description: e.target.value})}
            multiline
            rows={2}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>模型</InputLabel>
            <Select
              value={roleForm.model_id}
              onChange={(e) => setRoleForm({...roleForm, model_id: Number(e.target.value)})}
              label="模型"
            >
              {models.map((model) => (
                <MenuItem key={model.id} value={model.id}>
                  {model.name} ({getProviderName(model.provider_id)})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            label="系统提示词"
            fullWidth
            value={roleForm.system_prompt}
            onChange={(e) => setRoleForm({...roleForm, system_prompt: e.target.value})}
            multiline
            rows={4}
            sx={{ mb: 2 }}
          />
          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={roleForm.is_default}
                  onChange={(e) => setRoleForm({...roleForm, is_default: e.target.checked})}
                />
              }
              label="设为默认角色"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={roleForm.is_public}
                  onChange={(e) => setRoleForm({...roleForm, is_public: e.target.checked})}
                />
              }
              label="公开（其他用户可见）"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRoleDialogOpen(false)}>取消</Button>
          <Button onClick={handleRoleSubmit} variant="contained">保存</Button>
        </DialogActions>
      </Dialog>

      {/* 删除确认对话框 */}
      <DeleteConfirmDialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        onConfirm={handleConfirmDelete}
        itemType="role"
        message="确定要删除这个角色吗？"
      />
    </>
  );
}
