import { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  CardActions,
  Tabs,
  Tab,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
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
  Tooltip,
  Alert
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import Head from 'next/head';

// 模拟数据
const mockProviders = [
  { id: 1, name: 'OpenAI', description: 'OpenAI API', base_url: 'https://api.openai.com/v1' },
  { id: 2, name: 'Anthropic', description: 'Anthropic Claude API', base_url: 'https://api.anthropic.com' },
  { id: 3, name: 'Gemini', description: 'Google Gemini API', base_url: 'https://generativelanguage.googleapis.com' },
];

const mockModels = [
  { id: 1, name: 'gpt-4', provider_id: 1, api_key: '***********', is_active: true, max_tokens: 8192, temperature: 0.7 },
  { id: 2, name: 'gpt-3.5-turbo', provider_id: 1, api_key: '***********', is_active: true, max_tokens: 4096, temperature: 0.7 },
  { id: 3, name: 'claude-3-opus', provider_id: 2, api_key: '***********', is_active: true, max_tokens: 100000, temperature: 0.7 },
  { id: 4, name: 'claude-3-sonnet', provider_id: 2, api_key: '***********', is_active: true, max_tokens: 200000, temperature: 0.7 },
  { id: 5, name: 'gemini-pro', provider_id: 3, api_key: '***********', is_active: false, max_tokens: 8192, temperature: 0.7 },
];

const mockRoles = [
  { id: 1, name: '通用助手', description: '通用AI助手', system_prompt: '你是一个有用的AI助手。', model_id: 1, is_default: true },
  { id: 2, name: '程序员', description: '编程助手', system_prompt: '你是一个专业的程序员，擅长解决编程问题。', model_id: 1, is_default: false },
  { id: 3, name: '写作助手', description: '写作辅助', system_prompt: '你是一个专业的写作助手，擅长文学创作和文章润色。', model_id: 2, is_default: true },
  { id: 4, name: '学术助手', description: '学术研究', system_prompt: '你是一个学术研究助手，擅长科学研究和学术写作。', model_id: 3, is_default: true },
];

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
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export default function LLMConfig() {
  const [tabValue, setTabValue] = useState(0);
  const [providers, setProviders] = useState(mockProviders);
  const [models, setModels] = useState(mockModels);
  const [roles, setRoles] = useState(mockRoles);
  
  // 对话框状态
  const [providerDialogOpen, setProviderDialogOpen] = useState(false);
  const [modelDialogOpen, setModelDialogOpen] = useState(false);
  const [roleDialogOpen, setRoleDialogOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  
  // 编辑项
  const [editingProvider, setEditingProvider] = useState<any>(null);
  const [editingModel, setEditingModel] = useState<any>(null);
  const [editingRole, setEditingRole] = useState<any>(null);
  const [deleteItem, setDeleteItem] = useState<{type: string, id: number} | null>(null);
  
  // 表单状态
  const [providerForm, setProviderForm] = useState({
    name: '',
    description: '',
    base_url: ''
  });
  
  const [modelForm, setModelForm] = useState({
    name: '',
    provider_id: 0,
    api_key: '',
    is_active: true,
    max_tokens: 4096,
    temperature: 0.7
  });
  
  const [roleForm, setRoleForm] = useState({
    name: '',
    description: '',
    system_prompt: '',
    model_id: 0,
    is_default: false
  });
  
  // 显示API密钥
  const [showApiKey, setShowApiKey] = useState<{[key: number]: boolean}>({});
  
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  // 供应商相关处理函数
  const handleAddProvider = () => {
    setEditingProvider(null);
    setProviderForm({
      name: '',
      description: '',
      base_url: ''
    });
    setProviderDialogOpen(true);
  };
  
  const handleEditProvider = (provider: any) => {
    setEditingProvider(provider);
    setProviderForm({
      name: provider.name,
      description: provider.description || '',
      base_url: provider.base_url || ''
    });
    setProviderDialogOpen(true);
  };
  
  const handleDeleteProvider = (provider: any) => {
    setDeleteItem({type: 'provider', id: provider.id});
    setDeleteConfirmOpen(true);
  };
  
  const handleSaveProvider = () => {
    if (editingProvider) {
      // 更新供应商
      const updatedProviders = providers.map(p => 
        p.id === editingProvider.id ? {...p, ...providerForm} : p
      );
      setProviders(updatedProviders);
    } else {
      // 添加新供应商
      const newProvider = {
        id: Math.max(...providers.map(p => p.id), 0) + 1,
        ...providerForm
      };
      setProviders([...providers, newProvider]);
    }
    setProviderDialogOpen(false);
  };
  
  // 模型相关处理函数
  const handleAddModel = () => {
    setEditingModel(null);
    setModelForm({
      name: '',
      provider_id: providers[0]?.id || 0,
      api_key: '',
      is_active: true,
      max_tokens: 4096,
      temperature: 0.7
    });
    setModelDialogOpen(true);
  };
  
  const handleEditModel = (model: any) => {
    setEditingModel(model);
    setModelForm({
      name: model.name,
      provider_id: model.provider_id,
      api_key: model.api_key,
      is_active: model.is_active,
      max_tokens: model.max_tokens,
      temperature: model.temperature
    });
    setModelDialogOpen(true);
  };
  
  const handleDeleteModel = (model: any) => {
    setDeleteItem({type: 'model', id: model.id});
    setDeleteConfirmOpen(true);
  };
  
  const handleSaveModel = () => {
    if (editingModel) {
      // 更新模型
      const updatedModels = models.map(m => 
        m.id === editingModel.id ? {...m, ...modelForm} : m
      );
      setModels(updatedModels);
    } else {
      // 添加新模型
      const newModel = {
        id: Math.max(...models.map(m => m.id), 0) + 1,
        ...modelForm
      };
      setModels([...models, newModel]);
    }
    setModelDialogOpen(false);
  };
  
  // 角色相关处理函数
  const handleAddRole = () => {
    setEditingRole(null);
    setRoleForm({
      name: '',
      description: '',
      system_prompt: '',
      model_id: models[0]?.id || 0,
      is_default: false
    });
    setRoleDialogOpen(true);
  };
  
  const handleEditRole = (role: any) => {
    setEditingRole(role);
    setRoleForm({
      name: role.name,
      description: role.description || '',
      system_prompt: role.system_prompt,
      model_id: role.model_id,
      is_default: role.is_default
    });
    setRoleDialogOpen(true);
  };
  
  const handleDeleteRole = (role: any) => {
    setDeleteItem({type: 'role', id: role.id});
    setDeleteConfirmOpen(true);
  };
  
  const handleSaveRole = () => {
    if (editingRole) {
      // 更新角色
      const updatedRoles = roles.map(r => 
        r.id === editingRole.id ? {...r, ...roleForm} : r
      );
      setRoles(updatedRoles);
    } else {
      // 添加新角色
      const newRole = {
        id: Math.max(...roles.map(r => r.id), 0) + 1,
        ...roleForm
      };
      setRoles([...roles, newRole]);
    }
    setRoleDialogOpen(false);
  };
  
  // 删除确认
  const handleConfirmDelete = () => {
    if (!deleteItem) return;
    
    if (deleteItem.type === 'provider') {
      setProviders(providers.filter(p => p.id !== deleteItem.id));
    } else if (deleteItem.type === 'model') {
      setModels(models.filter(m => m.id !== deleteItem.id));
    } else if (deleteItem.type === 'role') {
      setRoles(roles.filter(r => r.id !== deleteItem.id));
    }
    
    setDeleteConfirmOpen(false);
    setDeleteItem(null);
  };
  
  // 切换API密钥可见性
  const toggleApiKeyVisibility = (modelId: number) => {
    setShowApiKey(prev => ({
      ...prev,
      [modelId]: !prev[modelId]
    }));
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
      <Head>
        <title>大模型配置 | Kortex</title>
        <meta name="description" content="Kortex大模型配置" />
      </Head>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          大模型配置
        </Typography>
        
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
            
            <List>
              {providers.map((provider) => (
                <ListItem key={provider.id} divider>
                  <ListItemText
                    primary={provider.name}
                    secondary={
                      <>
                        {provider.description}
                        <br />
                        {provider.base_url && `API地址: ${provider.base_url}`}
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
        </Paper>
        
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
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="API基础URL"
              fullWidth
              value={providerForm.base_url}
              onChange={(e) => setProviderForm({...providerForm, base_url: e.target.value})}
              placeholder="https://api.example.com"
              helperText="可选，留空使用默认URL"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setProviderDialogOpen(false)}>取消</Button>
            <Button 
              onClick={handleSaveProvider}
              variant="contained"
              disabled={!providerForm.name}
            >
              保存
            </Button>
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
              type="password"
              value={modelForm.api_key}
              onChange={(e) => setModelForm({...modelForm, api_key: e.target.value})}
              sx={{ mb: 2 }}
            />
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6}>
                <TextField
                  margin="dense"
                  label="最大Token数"
                  fullWidth
                  type="number"
                  value={modelForm.max_tokens}
                  onChange={(e) => setModelForm({...modelForm, max_tokens: Number(e.target.value)})}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  margin="dense"
                  label="温度"
                  fullWidth
                  type="number"
                  inputProps={{ step: 0.1, min: 0, max: 1 }}
                  value={modelForm.temperature}
                  onChange={(e) => setModelForm({...modelForm, temperature: Number(e.target.value)})}
                />
              </Grid>
            </Grid>
            <FormControlLabel
              control={
                <Switch
                  checked={modelForm.is_active}
                  onChange={(e) => setModelForm({...modelForm, is_active: e.target.checked})}
                />
              }
              label="启用"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setModelDialogOpen(false)}>取消</Button>
            <Button 
              onClick={handleSaveModel}
              variant="contained"
              disabled={!modelForm.name || !modelForm.provider_id}
            >
              保存
            </Button>
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
              multiline
              rows={4}
              value={roleForm.system_prompt}
              onChange={(e) => setRoleForm({...roleForm, system_prompt: e.target.value})}
              required
              sx={{ mb: 2 }}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={roleForm.is_default}
                  onChange={(e) => setRoleForm({...roleForm, is_default: e.target.checked})}
                />
              }
              label="设为默认角色"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setRoleDialogOpen(false)}>取消</Button>
            <Button 
              onClick={handleSaveRole}
              variant="contained"
              disabled={!roleForm.name || !roleForm.model_id || !roleForm.system_prompt}
            >
              保存
            </Button>
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
              {deleteItem?.type === 'provider' && '删除供应商将同时删除关联的模型和角色，确定要删除吗？'}
              {deleteItem?.type === 'model' && '删除模型将同时删除关联的角色，确定要删除吗？'}
              {deleteItem?.type === 'role' && '确定要删除这个角色吗？'}
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteConfirmOpen(false)}>取消</Button>
            <Button onClick={handleConfirmDelete} color="error">
              删除
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </>
  );
}
