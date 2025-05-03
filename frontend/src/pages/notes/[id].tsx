import { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Button, 
  TextField,
  Paper,
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
  Checkbox
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import StorageIcon from '@mui/icons-material/Storage';
import Head from 'next/head';
import { useRouter } from 'next/router';
import MarkdownEditor from '@/components/MarkdownEditor';

// 模拟笔记数据
const mockNotes = [
  { id: 1, title: '项目计划', content: '# 项目计划\n\n这是一个项目计划文档...', updatedAt: '2023-05-10' },
  { id: 2, title: '会议记录', content: '# 会议记录\n\n今天的会议讨论了以下内容...', updatedAt: '2023-05-09' },
  { id: 3, title: '学习笔记', content: '# 学习笔记\n\n今天学习了以下内容...', updatedAt: '2023-05-08' },
  { id: 4, title: '想法收集', content: '# 想法收集\n\n最近有以下想法...', updatedAt: '2023-05-07' },
];

// 模拟数据库数据
const mockDatabases = [
  { id: 1, name: '项目数据', description: '项目相关数据' },
  { id: 2, name: '客户信息', description: '客户联系信息' },
  { id: 3, name: '产品目录', description: '产品信息和价格' },
];

export default function NotePage() {
  const router = useRouter();
  const { id } = router.query;
  
  const [note, setNote] = useState<any>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [databaseDialogOpen, setDatabaseDialogOpen] = useState(false);
  const [selectedDatabases, setSelectedDatabases] = useState<number[]>([]);
  
  // 获取笔记数据
  useEffect(() => {
    if (id) {
      const noteId = parseInt(id as string);
      const foundNote = mockNotes.find(note => note.id === noteId);
      
      if (foundNote) {
        setNote(foundNote);
        setTitle(foundNote.title);
        setContent(foundNote.content);
        // 模拟已关联的数据库
        setSelectedDatabases([1]);
      } else if (id === 'new') {
        setNote(null);
        setTitle('');
        setContent('');
        setIsEditing(true);
        setSelectedDatabases([]);
      } else {
        // 笔记不存在，返回列表页
        router.push('/notes');
      }
    }
  }, [id, router]);
  
  const handleSave = () => {
    // 在实际应用中，这里会调用API保存笔记
    console.log('保存笔记:', { title, content, databases: selectedDatabases });
    setIsEditing(false);
    
    // 如果是新建笔记，保存后跳转到笔记列表
    if (id === 'new') {
      router.push('/notes');
    }
  };
  
  const handleDelete = () => {
    // 在实际应用中，这里会调用API删除笔记
    console.log('删除笔记:', id);
    router.push('/notes');
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

  if (!note && id !== 'new') {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography>加载中...</Typography>
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
                <Button 
                  variant="outlined" 
                  onClick={() => {
                    if (id === 'new') {
                      router.push('/notes');
                    } else {
                      setIsEditing(false);
                      setTitle(note.title);
                      setContent(note.content);
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
                <Tooltip title="删除笔记">
                  <IconButton color="error" onClick={handleDelete}>
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </>
            )}
          </Box>
        </Box>
        
        <Divider sx={{ mb: 3 }} />
        
        {isEditing ? (
          <MarkdownEditor 
            initialValue={content} 
            onChange={setContent} 
          />
        ) : (
          <Paper elevation={0} sx={{ p: 3 }}>
            <MarkdownEditor 
              initialValue={content} 
              onChange={() => {}} 
            />
          </Paper>
        )}
        
        {/* 关联数据库对话框 */}
        <Dialog 
          open={databaseDialogOpen} 
          onClose={() => setDatabaseDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>关联数据库</DialogTitle>
          <DialogContent>
            <List>
              {mockDatabases.map((database) => (
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
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDatabaseDialogOpen(false)}>
              取消
            </Button>
            <Button 
              variant="contained" 
              onClick={() => {
                console.log('保存数据库关联:', selectedDatabases);
                setDatabaseDialogOpen(false);
              }}
            >
              保存
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </>
  );
}
