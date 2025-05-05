
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
  Snackbar
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import StorageIcon from '@mui/icons-material/Storage';
import ChatIcon from '@mui/icons-material/Chat';
import Head from 'next/head';
import { useRouter } from 'next/router';
import MarkdownEditor from '@/components/MarkdownEditor';
import ChatPanel from '@/components/ChatPanel';
import { noteApi, databaseApi } from '@/services/api';

// 笔记类型定义
interface Note {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  user_id: number;
  databases?: Database[];
}

// 数据库类型定义
interface Database {
  id: number;
  name: string;
  description?: string;
}



export default function NotePage() {
  const router = useRouter();
  const { id } = router.query;

  const [note, setNote] = useState<Note | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [databaseDialogOpen, setDatabaseDialogOpen] = useState(false);
  const [selectedDatabases, setSelectedDatabases] = useState<number[]>([]);
  const [chatDrawerOpen, setChatDrawerOpen] = useState(false);
  const editorRef = useRef<any>(null);

  // 状态管理
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [databases, setDatabases] = useState<Database[]>([]);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  // 获取数据库列表
  useEffect(() => {
    const fetchDatabases = async () => {
      try {
        const data = await databaseApi.getDatabases();
        setDatabases(data);
      } catch (err) {
        console.error('获取数据库列表失败:', err);
        // 使用空数组
        setDatabases([]);
      }
    };

    fetchDatabases();
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
              setSelectedDatabases(data.databases.map((db: Database) => db.id));
            } else {
              setSelectedDatabases([]);
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
        database_ids: selectedDatabases
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

  const handleSaveDatabaseAssociations = async () => {
    try {
      if (id !== 'new') {
        // 更新笔记的数据库关联
        await noteApi.updateNote(parseInt(id as string), { database_ids: selectedDatabases });
        setSnackbarMessage('数据库关联已保存');
        setSnackbarSeverity('success');
        setSnackbarOpen(true);
      }
      setDatabaseDialogOpen(false);
    } catch (err) {
      console.error('保存数据库关联失败:', err);
      setSnackbarMessage('保存数据库关联失败，请稍后重试');
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
                <Tooltip title="关联数据库">
                  <IconButton
                    color="primary"
                    onClick={() => setDatabaseDialogOpen(true)}
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

        {/* 关联数据库对话框 */}
        <Dialog
          open={databaseDialogOpen}
          onClose={() => setDatabaseDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>关联数据库</DialogTitle>
          <DialogContent>
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
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDatabaseDialogOpen(false)}>
              取消
            </Button>
            <Button
              variant="contained"
              onClick={handleSaveDatabaseAssociations}
              disabled={databases.length === 0}
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
