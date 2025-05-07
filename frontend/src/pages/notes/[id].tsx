
import { useState, useEffect, useRef } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  TextField,
  Divider,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Checkbox,
  CircularProgress,
  Alert,
  Snackbar,
  Tab,
  Tabs
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import StorageIcon from '@mui/icons-material/Storage';
import DatasetIcon from '@mui/icons-material/Dataset';
import ChatIcon from '@mui/icons-material/Chat';
import Head from 'next/head';
import { useRouter } from 'next/router';
import MarkdownEditor from '@/components/MarkdownEditor';
import ChatPanel from '@/components/ChatPanel';
import noteApi from '@/services/noteApi';
import datasetApi from '@/services/datasetApi';

// 接口定义使用导入的类型
import { Note, CreateNoteRequest, UpdateNoteRequest } from '@/services/noteApi';
import { Dataset } from '@/services/datasetApi';

// 临时定义数据库类型，以便兼容现有代码
interface Database {
  id: number;
  name: string;
  description?: string;
}

// 标签面板属性
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

// 标签面板组件
function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`association-tabpanel-${index}`}
      aria-labelledby={`association-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 2 }}>
          {children}
        </Box>
      )}
    </div>
  );
}



export default function NotePage() {
  const router = useRouter();
  const { id } = router.query;

  const [note, setNote] = useState<Note | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [associationDialogOpen, setAssociationDialogOpen] = useState(false);
  const [associationTabValue, setAssociationTabValue] = useState(0);
  const [selectedDatabases, setSelectedDatabases] = useState<number[]>([]);
  const [selectedDatasets, setSelectedDatasets] = useState<number[]>([]);
  const [chatDrawerOpen, setChatDrawerOpen] = useState(false);
  const editorRef = useRef<any>(null);

  // 状态管理
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [databases, setDatabases] = useState<Database[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  // 获取数据集列表
  useEffect(() => {
    const fetchData = async () => {
      try {
        // 获取数据集列表
        const dsData = await datasetApi.getDatasets();
        setDatasets(dsData);

        // 使用空数组代替数据库列表
        setDatabases([]);
      } catch (err) {
        console.error('获取数据失败:', err);
        // 使用空数组
        setDatabases([]);
        setDatasets([]);
      }
    };

    fetchData();
  }, []);

  // 获取笔记数据
  useEffect(() => {
    if (id) {
      if (id === 'new') {
        setNote(null);
        setTitle('');
        setContent('');
        setIsEditing(true);
        setSelectedDatabases([]);
        setSelectedDatasets([]);
      } else {
        const fetchNote = async () => {
          try {
            setLoading(true);
            setError(null);
            const noteId = parseInt(id as string);
            const data = await noteApi.getNote(noteId);
            setNote(data);
            setTitle(data.title);
            setContent(data.content);

            // 设置已关联的数据库
            if (data.databases) {
              setSelectedDatabases(data.databases.map((db) => db.id));
            } else {
              setSelectedDatabases([]);
            }

            // 设置已关联的数据集
            if (data.datasets) {
              setSelectedDatasets(data.datasets.map((ds) => ds.id));
            } else {
              setSelectedDatasets([]);
            }
          } catch (err) {
            console.error('获取笔记详情失败:', err);
            setError('获取笔记详情失败，请稍后重试');
            // 笔记不存在，返回列表页
            router.push('/notes');
          } finally {
            setLoading(false);
          }
        };

        fetchNote();
      }
    }
  }, [id, router]);

  const handleSave = async () => {
    try {
      setLoading(true);

      // 验证标题不能为空
      if (!title.trim()) {
        setSnackbarMessage('笔记标题不能为空');
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
        setLoading(false);
        return;
      }

      const noteData = {
        title,
        content,
        database_ids: selectedDatabases,
        dataset_ids: selectedDatasets
      };

      if (id === 'new') {
        // 创建新笔记
        const createdNote = await noteApi.createNote(noteData);
        setSnackbarMessage('笔记创建成功');
        setSnackbarSeverity('success');
        setSnackbarOpen(true);

        // 创建成功后跳转到笔记详情页
        router.push(`/notes/${createdNote.id}`);
      } else {
        // 更新现有笔记
        const updatedNote = await noteApi.updateNote(parseInt(id as string), noteData);
        setNote(updatedNote);
        setSnackbarMessage('笔记保存成功');
        setSnackbarSeverity('success');
        setSnackbarOpen(true);
        setIsEditing(false);
      }
    } catch (err) {
      console.error('保存笔记失败:', err);
      setSnackbarMessage('保存笔记失败，请稍后重试');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    try {
      setLoading(true);
      await noteApi.deleteNote(parseInt(id as string));
      setSnackbarMessage('笔记删除成功');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);

      // 删除成功后返回笔记列表
      router.push('/notes');
    } catch (err) {
      console.error('删除笔记失败:', err);
      setSnackbarMessage('删除笔记失败，请稍后重试');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
      setLoading(false);
    }
  };

  const confirmDelete = () => {
    setDeleteDialogOpen(true);
  };

  // 处理数据库选择切换
  const handleDatabaseToggle = (databaseId: number) => {
    const currentIndex = selectedDatabases.indexOf(databaseId);
    const newSelectedDatabases = [...selectedDatabases];

    if (currentIndex === -1) {
      newSelectedDatabases.push(databaseId);
    } else {
      newSelectedDatabases.splice(currentIndex, 1);
    }

    setSelectedDatabases(newSelectedDatabases);
  };

  // 处理数据集选择切换
  const handleDatasetToggle = (datasetId: number) => {
    const currentIndex = selectedDatasets.indexOf(datasetId);
    const newSelectedDatasets = [...selectedDatasets];

    if (currentIndex === -1) {
      newSelectedDatasets.push(datasetId);
    } else {
      newSelectedDatasets.splice(currentIndex, 1);
    }

    setSelectedDatasets(newSelectedDatasets);
  };

  // 处理关联标签页切换
  const handleAssociationTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setAssociationTabValue(newValue);
  };

  // 保存关联
  const handleSaveAssociations = async () => {
    try {
      if (id !== 'new') {
        // 更新笔记的数据库和数据集关联
        await noteApi.updateNote(parseInt(id as string), {
          database_ids: selectedDatabases,
          dataset_ids: selectedDatasets
        });
        setSnackbarMessage('关联已保存');
        setSnackbarSeverity('success');
        setSnackbarOpen(true);
      }
      setAssociationDialogOpen(false);
    } catch (err) {
      console.error('保存关联失败:', err);
      setSnackbarMessage('保存关联失败，请稍后重试');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    }
  };



  const handleInsertText = (text: string) => {
    // 如果不在编辑模式，先切换到编辑模式
    if (!isEditing) {
      setIsEditing(true);
      // 使用setTimeout确保状态更新后再插入文本
      setTimeout(() => {
        setContent(prev => prev + '\n\n' + text);
      }, 100);
    } else {
      // 已经在编辑模式，直接插入文本
      setContent(prev => prev + '\n\n' + text);
    }

    // 显示提示消息
    setSnackbarMessage('文本已插入到笔记');
    setSnackbarSeverity('success');
    setSnackbarOpen(true);
  };

  // 加载状态
  if (loading && id !== 'new') {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  // 错误状态
  if (error && id !== 'new') {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button
          variant="contained"
          startIcon={<ArrowBackIcon />}
          onClick={() => router.push('/notes')}
        >
          返回笔记列表
        </Button>
      </Container>
    );
  }

  // 笔记不存在
  if (!note && id !== 'new') {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography>笔记不存在或已被删除</Typography>
        <Button
          variant="contained"
          startIcon={<ArrowBackIcon />}
          onClick={() => router.push('/notes')}
          sx={{ mt: 2 }}
        >
          返回笔记列表
        </Button>
      </Container>
    );
  }

  return (
    <>
      <Head>
        <title>{id === 'new' ? '新建笔记' : title} | Kortex</title>
      </Head>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton onClick={() => router.push('/notes')} sx={{ mr: 1 }}>
              <ArrowBackIcon />
            </IconButton>
            {isEditing ? (
              <TextField
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                variant="standard"
                placeholder="笔记标题"
                sx={{ fontSize: '1.5rem', width: '300px' }}
              />
            ) : (
              <Typography variant="h4" component="h1">
                {title}
              </Typography>
            )}
          </Box>
          <Box>
            {isEditing ? (
              <>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSave}
                  sx={{ mr: 1 }}
                >
                  保存
                </Button>
                <Tooltip title={chatDrawerOpen ? "关闭AI助手" : "打开AI助手"}>
                  <IconButton
                    color={chatDrawerOpen ? "secondary" : "primary"}
                    onClick={() => setChatDrawerOpen(!chatDrawerOpen)}
                    sx={{ mr: 1 }}
                  >
                    <ChatIcon />
                  </IconButton>
                </Tooltip>
                <Button
                  variant="outlined"
                  onClick={() => {
                    if (id === 'new') {
                      router.push('/notes');
                    } else {
                      setIsEditing(false);
                      setTitle(note?.title || '');
                      setContent(note?.content || '');
                    }
                  }}
                >
                  取消
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="contained"
                  onClick={() => setIsEditing(true)}
                  sx={{ mr: 1 }}
                >
                  编辑
                </Button>
                <Tooltip title="关联数据源">
                  <IconButton
                    color="primary"
                    onClick={() => setAssociationDialogOpen(true)}
                    sx={{ mr: 1 }}
                  >
                    <StorageIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title={chatDrawerOpen ? "关闭AI助手" : "打开AI助手"}>
                  <IconButton
                    color={chatDrawerOpen ? "secondary" : "primary"}
                    onClick={() => setChatDrawerOpen(!chatDrawerOpen)}
                    sx={{ mr: 1 }}
                  >
                    <ChatIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="删除笔记">
                  <IconButton color="error" onClick={confirmDelete}>
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </>
            )}
          </Box>
        </Box>

        <Divider sx={{ mb: 3 }} />

        <Box sx={{ display: 'flex', height: 'calc(100vh - 200px)' }}>
          {/* AI助手面板 - 左侧 */}
          {chatDrawerOpen && (
            <Box sx={{ width: 350, mr: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
              <ChatPanel
                noteId={id !== 'new' ? parseInt(id as string) : 0}
                onInsertText={handleInsertText}
              />
            </Box>
          )}

          {/* 编辑器主体 */}
          <Box sx={{ flexGrow: 1 }}>
            <MarkdownEditor
              initialValue={content}
              onChange={isEditing ? setContent : undefined}
              ref={editorRef}
              readOnly={!isEditing}
              defaultEditMode={isEditing}
            />
          </Box>
        </Box>

        {/* 关联数据源对话框 */}
        <Dialog
          open={associationDialogOpen}
          onClose={() => setAssociationDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>关联数据源</DialogTitle>
          <DialogContent>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
              <Tabs value={associationTabValue} onChange={handleAssociationTabChange}>
                <Tab label="数据库" id="association-tab-0" aria-controls="association-tabpanel-0" />
                <Tab label="数据集" id="association-tab-1" aria-controls="association-tabpanel-1" />
              </Tabs>
            </Box>

            {/* 数据库标签页 */}
            <TabPanel value={associationTabValue} index={0}>
              {databases.length === 0 ? (
                <Typography color="text.secondary" sx={{ py: 2 }}>
                  暂无可用的数据库，请先创建数据库
                </Typography>
              ) : (
                <List>
                  {databases.map((database) => (
                    <ListItem key={database.id}>
                      <Checkbox
                        edge="start"
                        checked={selectedDatabases.indexOf(database.id) !== -1}
                        onChange={() => handleDatabaseToggle(database.id)}
                      />
                      <ListItemText
                        primary={database.name}
                        secondary={database.description}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </TabPanel>

            {/* 数据集标签页 */}
            <TabPanel value={associationTabValue} index={1}>
              {datasets.length === 0 ? (
                <Typography color="text.secondary" sx={{ py: 2 }}>
                  暂无可用的数据集，请先创建数据集
                </Typography>
              ) : (
                <List>
                  {datasets.map((dataset) => (
                    <ListItem key={dataset.id}>
                      <Checkbox
                        edge="start"
                        checked={selectedDatasets.indexOf(dataset.id) !== -1}
                        onChange={() => handleDatasetToggle(dataset.id)}
                      />
                      <ListItemText
                        primary={dataset.name}
                        secondary={dataset.description}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </TabPanel>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAssociationDialogOpen(false)}>
              取消
            </Button>
            <Button
              variant="contained"
              onClick={handleSaveAssociations}
              disabled={databases.length === 0 && datasets.length === 0}
            >
              保存
            </Button>
          </DialogActions>
        </Dialog>

        {/* 删除确认对话框 */}
        <Dialog
          open={deleteDialogOpen}
          onClose={() => setDeleteDialogOpen(false)}
        >
          <DialogTitle>确认删除</DialogTitle>
          <DialogContent>
            <Typography>
              确定要删除笔记 "{title}" 吗？此操作不可撤销。
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)}>
              取消
            </Button>
            <Button
              variant="contained"
              color="error"
              onClick={() => {
                setDeleteDialogOpen(false);
                handleDelete();
              }}
            >
              删除
            </Button>
          </DialogActions>
        </Dialog>

        {/* 提示消息 */}
        <Snackbar
          open={snackbarOpen}
          autoHideDuration={3000}
          onClose={() => setSnackbarOpen(false)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert
            onClose={() => setSnackbarOpen(false)}
            severity={snackbarSeverity}
            sx={{ width: '100%' }}
          >
            {snackbarMessage}
          </Alert>
        </Snackbar>
      </Container>
    </>
  );
}
