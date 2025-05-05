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
  description?: string;
  base_url?: string;
  is_public: boolean;
}

interface LLMProvidersProps {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

export default function LLMProviders({ onSuccess, onError }: LLMProvidersProps) {
  // 数据状态
  const [providers, setProviders] = useState<LLMProvider[]>([]);

  // 加载和错误状态
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 对话框状态
  const [providerDialogOpen, setProviderDialogOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  // 编辑项
  const [editingProvider, setEditingProvider] = useState<LLMProvider | null>(null);
  const [deleteItem, setDeleteItem] = useState<{type: string, id: number} | null>(null);

  // 表单状态
  const [providerForm, setProviderForm] = useState({
    name: '',
    description: '',
    base_url: '',
    is_public: false
  });

  // 加载数据
  useEffect(() => {
    fetchProviders();
  }, []);

  // 获取供应商列表
  const fetchProviders = async () => {
    setLoading(true);
    setError('');

    try {
      // 从后端API获取真实数据
      const response = await axios.get('http://localhost:8000/api/llm-config/providers');
      setProviders(response.data);
    } catch (err: any) {
      console.error('获取供应商列表失败:', err);
      setError(err.response?.data?.detail || '获取供应商列表失败');
      onError(err.response?.data?.detail || '获取供应商列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 供应商相关处理函数
  const handleAddProvider = () => {
    setEditingProvider(null);
    setProviderForm({
      name: '',
      description: '',
      base_url: '',
      is_public: false
    });
    setProviderDialogOpen(true);
  };

  const handleEditProvider = (provider: LLMProvider) => {
    setEditingProvider(provider);
    setProviderForm({
      name: provider.name,
      description: provider.description || '',
      base_url: provider.base_url || '',
      is_public: provider.is_public
    });
    setProviderDialogOpen(true);
  };

  const handleDeleteProvider = (provider: LLMProvider) => {
    setDeleteItem({ type: 'provider', id: provider.id });
    setDeleteConfirmOpen(true);
  };

  const handleProviderSubmit = async () => {
    try {
      if (editingProvider) {
        // 更新供应商
        await axios.put(`http://localhost:8000/api/llm-config/providers/${editingProvider.id}`, providerForm);

        // 更新本地状态
        setProviders(providers.map(p =>
          p.id === editingProvider.id ? { ...p, ...providerForm } : p
        ));

        onSuccess('供应商更新成功');
      } else {
        // 创建新供应商
        const response = await axios.post('http://localhost:8000/api/llm-config/providers', providerForm);

        // 更新本地状态
        setProviders([...providers, response.data]);

        onSuccess('供应商创建成功');
      }

      setProviderDialogOpen(false);
    } catch (err: any) {
      console.error('保存供应商失败:', err);
      onError(err.response?.data?.detail || '操作失败，请稍后再试');
    }
  };

  // 删除确认处理
  const handleConfirmDelete = async () => {
    if (!deleteItem) return;

    try {
      await axios.delete(`http://localhost:8000/api/llm-config/providers/${deleteItem.id}`);
      setProviders(providers.filter(p => p.id !== deleteItem.id));
      onSuccess('供应商删除成功');
    } catch (err: any) {
      console.error('删除失败:', err);
      onError(err.response?.data?.detail || '删除失败，请稍后再试');
    } finally {
      setDeleteConfirmOpen(false);
      setDeleteItem(null);
    }
  };

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddProvider}
        >
          添加供应商
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      ) : (
        <List>
          {providers.map((provider) => (
            <ListItem key={provider.id} divider>
              <ListItemText
                primary={provider.name}
                secondary={
                  <>
                    {provider.description}
                    {provider.base_url && (
                      <>
                        <br />
                        API地址: {provider.base_url}
                      </>
                    )}
                    <br />
                    状态: {provider.is_public ? '公开' : '私有'}
                  </>
                }
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => handleEditProvider(provider)}>
                  <EditIcon />
                </IconButton>
                <IconButton edge="end" onClick={() => handleDeleteProvider(provider)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
          {providers.length === 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              暂无供应商，请添加供应商
            </Alert>
          )}
        </List>
      )}

      {/* 供应商对话框 */}
      <Dialog
        open={providerDialogOpen}
        onClose={() => setProviderDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {editingProvider ? '编辑供应商' : '添加供应商'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="供应商名称"
            fullWidth
            value={providerForm.name}
            onChange={(e) => setProviderForm({...providerForm, name: e.target.value})}
            required
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="描述"
            fullWidth
            value={providerForm.description}
            onChange={(e) => setProviderForm({...providerForm, description: e.target.value})}
            multiline
            rows={2}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="API基础URL"
            fullWidth
            value={providerForm.base_url}
            onChange={(e) => setProviderForm({...providerForm, base_url: e.target.value})}
            placeholder="例如: https://api.openai.com/v1"
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={
              <Switch
                checked={providerForm.is_public}
                onChange={(e) => setProviderForm({...providerForm, is_public: e.target.checked})}
              />
            }
            label="公开（其他用户可见）"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProviderDialogOpen(false)}>取消</Button>
          <Button onClick={handleProviderSubmit} variant="contained">保存</Button>
        </DialogActions>
      </Dialog>

      {/* 删除确认对话框 */}
      <DeleteConfirmDialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        onConfirm={handleConfirmDelete}
        itemType="provider"
        message="确定要删除这个供应商吗？相关的模型和角色也会被删除。"
      />
    </>
  );
}
