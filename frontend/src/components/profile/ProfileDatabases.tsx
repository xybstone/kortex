
import { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  CardActions, 
  Typography, 
  Grid, 
  TextField, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  FormControl, 
  InputLabel, 
  Paper,
  Input,
  FormHelperText,
  Alert,
  CircularProgress,
  InputAdornment
} from '@mui/material';
import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';
import AddIcon from '@mui/icons-material/Add';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import SearchIcon from '@mui/icons-material/Search';
import axios from 'axios';

// 数据库类型定义
interface Database {
  id: number;
  name: string;
  description?: string;
  tables?: number;
  created_at: string;
  updated_at?: string;
}

interface ProfileDatabasesProps {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

export default function ProfileDatabases({ onSuccess, onError }: ProfileDatabasesProps) {
  const router = useRouter();
  const { user } = useAuth();
  const [databases, setDatabases] = useState<Database[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [newDatabaseName, setNewDatabaseName] = useState('');
  const [newDatabaseDescription, setNewDatabaseDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 获取用户的数据库列表
  useEffect(() => {
    const fetchDatabases = async () => {
      setLoading(true);
      try {
        const response = await axios.get('http://localhost:8000/api/databases');
        setDatabases(response.data);
      } catch (err: any) {
        console.error('获取数据库列表失败:', err);
        setError(err.response?.data?.detail || '获取数据库列表失败，请稍后再试');
        onError(err.response?.data?.detail || '获取数据库列表失败，请稍后再试');
      } finally {
        setLoading(false);
      }
    };

    fetchDatabases();
  }, [onError]);

  // 根据搜索词过滤数据库
  const filteredDatabases = databases.filter(db =>
    db.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (db.description && db.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleImportSubmit = async () => {
    if (!newDatabaseName || !selectedFile) return;

    setLoading(true);
    setError('');

    try {
      // 创建FormData对象
      const formData = new FormData();
      formData.append('name', newDatabaseName);
      if (newDatabaseDescription) {
        formData.append('description', newDatabaseDescription);
      }
      formData.append('file', selectedFile);

      // 发送请求
      const response = await axios.post('http://localhost:8000/api/databases/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // 更新数据库列表
      setDatabases([...databases, response.data]);

      // 关闭对话框并重置表单
      setImportDialogOpen(false);
      setNewDatabaseName('');
      setNewDatabaseDescription('');
      setSelectedFile(null);

      // 显示成功消息
      onSuccess('数据库导入成功');
    } catch (err: any) {
      console.error('导入数据库失败:', err);
      setError(err.response?.data?.detail || '导入数据库失败，请稍后再试');
      onError(err.response?.data?.detail || '导入数据库失败，请稍后再试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h5" component="h2" fontWeight="medium">
          我的数据库
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<UploadFileIcon />}
            onClick={() => setImportDialogOpen(true)}
            sx={{ mr: 2 }}
            size="large"
          >
            导入数据
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => router.push('/databases/new')}
            size="large"
          >
            新建数据库
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <TextField
        fullWidth
        variant="outlined"
        placeholder="搜索数据库..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        sx={{ mb: 4 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {filteredDatabases.map((database) => (
            <Grid item xs={12} sm={6} md={4} key={database.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  '&:hover': {
                    boxShadow: 6,
                  },
                  cursor: 'pointer',
                  borderRadius: 2,
                  overflow: 'hidden'
                }}
                onClick={() => router.push(`/databases/${database.id}`)}
              >
                <CardContent sx={{ flexGrow: 1, p: 3 }}>
                  <Typography gutterBottom variant="h5" component="h2" fontWeight="medium">
                    {database.name}
                  </Typography>
                  <Typography color="text.secondary" paragraph>
                    {database.description || '无描述'}
                  </Typography>
                  <Typography variant="body2">
                    {database.tables || 0} 个表格
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'flex-end', px: 3, pb: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    更新于 {new Date(database.updated_at || database.created_at).toLocaleDateString()}
                  </Typography>
                </CardActions>
              </Card>
            </Grid>
          ))}

          {filteredDatabases.length === 0 && (
            <Grid item xs={12}>
              <Paper
                elevation={1}
                sx={{
                  textAlign: 'center',
                  py: 6,
                  px: 4,
                  borderRadius: 2,
                  bgcolor: 'background.default'
                }}
              >
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  没有找到匹配的数据库
                </Typography>
                <Box sx={{ mt: 3 }}>
                  <Button
                    variant="outlined"
                    startIcon={<UploadFileIcon />}
                    onClick={() => setImportDialogOpen(true)}
                    sx={{ mr: 2 }}
                    size="large"
                  >
                    导入数据
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => router.push('/databases/new')}
                    size="large"
                  >
                    新建数据库
                  </Button>
                </Box>
              </Paper>
            </Grid>
          )}
        </Grid>
      )}

      {/* 导入数据对话框 */}
      <Dialog
        open={importDialogOpen}
        onClose={() => setImportDialogOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 2 }
        }}
      >
        <DialogTitle sx={{ pb: 1, pt: 3, px: 3 }}>
          <Typography variant="h5" component="h2" fontWeight="medium">
            导入数据
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ px: 3, pb: 3 }}>
          <FormControl fullWidth margin="normal" sx={{ mt: 2, mb: 3 }}>
            <InputLabel htmlFor="database-name">数据库名称</InputLabel>
            <Input
              id="database-name"
              value={newDatabaseName}
              onChange={(e) => setNewDatabaseName(e.target.value)}
            />
          </FormControl>

          <FormControl fullWidth margin="normal" sx={{ mb: 3 }}>
            <InputLabel htmlFor="database-description">描述（可选）</InputLabel>
            <Input
              id="database-description"
              value={newDatabaseDescription}
              onChange={(e) => setNewDatabaseDescription(e.target.value)}
              multiline
              rows={2}
            />
          </FormControl>

          <FormControl fullWidth margin="normal" sx={{ mb: 1 }}>
            <Input
              id="file-input"
              type="file"
              onChange={handleFileChange}
              sx={{ display: 'none' }}
            />
            <Button
              variant="outlined"
              component="label"
              htmlFor="file-input"
              startIcon={<UploadFileIcon />}
              fullWidth
              size="large"
              sx={{ py: 1.5 }}
            >
              选择文件
            </Button>
            <FormHelperText sx={{ mt: 1 }}>
              {selectedFile ? `已选择: ${selectedFile.name}` : '支持Excel、CSV、JSON格式'}
            </FormHelperText>
          </FormControl>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button
            onClick={() => setImportDialogOpen(false)}
            size="large"
          >
            取消
          </Button>
          <Button
            variant="contained"
            onClick={handleImportSubmit}
            disabled={!newDatabaseName || !selectedFile || loading}
            size="large"
          >
            {loading ? <CircularProgress size={24} /> : '导入'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
