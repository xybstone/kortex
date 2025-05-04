import { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
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
  Divider,
  Alert,
  Snackbar,
  CircularProgress,
  Tooltip
} from '@mui/material';
import Head from 'next/head';
import { useAuth } from '@/contexts/AuthContext';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import axios from 'axios';

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

interface LLMRole {
  id: number;
  name: string;
  description?: string;
  system_prompt: string;
  model_id: number;
  is_default: boolean;
  is_public: boolean;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`llm-config-tabpanel-${index}`}
      aria-labelledby={`llm-config-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function LLMConfig() {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);

  // 数据状态
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [models, setModels] = useState<LLMModel[]>([]);
  const [roles, setRoles] = useState<LLMRole[]>([]);

  // 加载和错误状态
  const [loading, setLoading] = useState({
    providers: false,
    models: false,
    roles: false
  });
  const [error, setError] = useState({
    providers: '',
    models: '',
    roles: ''
  });

  // 对话框状态
  const [providerDialogOpen, setProviderDialogOpen] = useState(false);
  const [modelDialogOpen, setModelDialogOpen] = useState(false);
  const [roleDialogOpen, setRoleDialogOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);

  // 编辑项
  const [editingProvider, setEditingProvider] = useState<LLMProvider | null>(null);
  const [editingModel, setEditingModel] = useState<LLMModel | null>(null);
  const [editingRole, setEditingRole] = useState<LLMRole | null>(null);
  const [deleteItem, setDeleteItem] = useState<{type: string, id: number} | null>(null);

  // 表单状态
  const [providerForm, setProviderForm] = useState({
    name: '',
    description: '',
    base_url: '',
    is_public: false
  });

  const [modelForm, setModelForm] = useState({
    name: '',
    provider_id: 0,
    api_key: '',
    is_active: true,
    is_public: false,
    max_tokens: 4096,
    temperature: 0.7
  });

  const [roleForm, setRoleForm] = useState({
    name: '',
    description: '',
    system_prompt: '',
    model_id: 0,
    is_default: false,
    is_public: false
  });

  // 显示API密钥
  const [showApiKey, setShowApiKey] = useState<{[key: number]: boolean}>({});

  // 提示消息
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error' | 'info' | 'warning'
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
    setLoading(prev => ({ ...prev, providers: true }));
    setError(prev => ({ ...prev, providers: '' }));

    try {
      const response = await axios.get('http://localhost:8000/api/llm-config/providers');
      setProviders(response.data);
    } catch (err: any) {
      console.error('获取供应商列表失败:', err);
      setError(prev => ({ ...prev, providers: err.response?.data?.detail || '获取供应商列表失败' }));
      // 使用空数组
      setProviders([]);
    } finally {
      setLoading(prev => ({ ...prev, providers: false }));
    }
  };

  // 获取模型列表
  const fetchModels = async () => {
    setLoading(prev => ({ ...prev, models: true }));
    setError(prev => ({ ...prev, models: '' }));

    try {
      const response = await axios.get('http://localhost:8000/api/llm-config/models');
      setModels(response.data);
    } catch (err: any) {
      console.error('获取模型列表失败:', err);
      setError(prev => ({ ...prev, models: err.response?.data?.detail || '获取模型列表失败' }));
      // 使用空数组
      setModels([]);
    } finally {
      setLoading(prev => ({ ...prev, models: false }));
    }
  };

  // 获取角色列表
  const fetchRoles = async () => {
    setLoading(prev => ({ ...prev, roles: true }));
    setError(prev => ({ ...prev, roles: '' }));

    try {
      const response = await axios.get('http://localhost:8000/api/llm-config/roles');
      setRoles(response.data);
    } catch (err: any) {
      console.error('获取角色列表失败:', err);
      setError(prev => ({ ...prev, roles: err.response?.data?.detail || '获取角色列表失败' }));
      // 使用空数组
      setRoles([]);
    } finally {
      setLoading(prev => ({ ...prev, roles: false }));
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
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

        setSnackbar({
          open: true,
          message: '供应商更新成功',
          severity: 'success'
        });
      } else {
        // 创建新供应商
        const response = await axios.post('http://localhost:8000/api/llm-config/providers', providerForm);

        // 更新本地状态
        setProviders([...providers, response.data]);

        setSnackbar({
          open: true,
          message: '供应商创建成功',
          severity: 'success'
        });
      }

      setProviderDialogOpen(false);
    } catch (err: any) {
      console.error('保存供应商失败:', err);
      setSnackbar({
        open: true,
        message: err.response?.data?.detail || '操作失败，请稍后再试',
        severity: 'error'
      });
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

  // 关闭提示消息
  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <>
      <Head>
        <title>大模型配置 | Kortex</title>
        <meta name="description" content="Kortex大模型配置" />
      </Head>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          大模型配置
        </Typography>

        {/* 提示消息 */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        >
          <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
            {snackbar.message}
          </Alert>
        </Snackbar>

        <Paper sx={{ width: '100%', mb: 2 }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            centered
          >
            <Tab label="供应商" />
            <Tab label="模型" />
            <Tab label="角色" />
          </Tabs>

          {/* 供应商面板 */}
          <TabPanel value={tabValue} index={0}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAddProvider}
              >
                添加供应商
              </Button>
            </Box>

            {loading.providers ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : error.providers ? (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error.providers}
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
          </TabPanel>

          {/* 模型面板 */}
          <TabPanel value={tabValue} index={1}>
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
            ) : loading.models ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : error.models ? (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error.models}
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
          </TabPanel>

          {/* 角色面板 */}
          <TabPanel value={tabValue} index={2}>
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
            ) : loading.roles ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : error.roles ? (
              <Alert severity="error" sx={{ mt: 2 }}>
                {error.roles}
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
          </TabPanel>

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
          <Dialog
            open={deleteConfirmOpen}
            onClose={() => setDeleteConfirmOpen(false)}
          >
            <DialogTitle>确认删除</DialogTitle>
            <DialogContent>
              <Typography>
                {deleteItem?.type === 'provider' && '确定要删除这个供应商吗？相关的模型和角色也会被删除。'}
                {deleteItem?.type === 'model' && '确定要删除这个模型吗？相关的角色也会被删除。'}
                {deleteItem?.type === 'role' && '确定要删除这个角色吗？'}
              </Typography>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDeleteConfirmOpen(false)}>取消</Button>
              <Button onClick={handleConfirmDelete} color="error" variant="contained">
                删除
              </Button>
            </DialogActions>
          </Dialog>
        </Paper>
      </Container>
    </>
  );
}
