import { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Input,
  FormHelperText,
  Alert,
  Snackbar,
  CircularProgress,
  InputAdornment
} from '@mui/material';
import Head from 'next/head';
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

export default function DatabasesManagement() {
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
  const [success, setSuccess] = useState('');
  const [openSnackbar, setOpenSnackbar] = useState(false);

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
      } finally {
        setLoading(false);
      }
    };

    fetchDatabases();
  }, []);

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
      setSuccess('数据库导入成功');
      setOpenSnackbar(true);
    } catch (err: any) {
      console.error('导入数据库失败:', err);
      setError(err.response?.data?.detail || '导入数据库失败，请稍后再试');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setOpenSnackbar(false);
  };

  return (
    <>
      <Head>
        <title>数据库管理 | Kortex</title>
        <meta name="description" content="管理您的数据库" />
      </Head>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            我的数据库
          </Typography>
          <Box>
            <Button 
              variant="outlined" 
              startIcon={<UploadFileIcon />}
              onClick={() => setImportDialogOpen(true)}
              sx={{ mr: 2 }}
            >
              导入数据
            </Button>
            <Button 
              variant="contained" 
              startIcon={<AddIcon />}
              onClick={() => router.push('/databases/new')}
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
          sx={{ mb: 3 }}
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
                    cursor: 'pointer'
                  }}
                  onClick={() => router.push(`/databases/${database.id}`)}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography gutterBottom variant="h5" component="h2">
                      {database.name}
                    </Typography>
                    <Typography color="text.secondary" paragraph>
                      {database.description || '无描述'}
                    </Typography>
                    <Typography variant="body2">
                      {database.tables || 0} 个表格
                    </Typography>
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'flex-end' }}>
                    <Typography variant="caption" color="text.secondary">
                      更新于 {new Date(database.updated_at || database.created_at).toLocaleDateString()}
                    </Typography>
                  </CardActions>
                </Card>
              </Grid>
            ))}
            
            {filteredDatabases.length === 0 && (
              <Grid item xs={12}>
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="h6" color="text.secondary">
                    没有找到匹配的数据库
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Button 
                      variant="outlined" 
                      startIcon={<UploadFileIcon />}
                      onClick={() => setImportDialogOpen(true)}
                      sx={{ mr: 2 }}
                    >
                      导入数据
                    </Button>
                    <Button 
                      variant="contained" 
                      startIcon={<AddIcon />}
                      onClick={() => router.push('/databases/new')}
                    >
                      新建数据库
                    </Button>
                  </Box>
                </Box>
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
        >
          <DialogTitle>导入数据</DialogTitle>
          <DialogContent>
            <FormControl fullWidth margin="normal">
              <InputLabel htmlFor="database-name">数据库名称</InputLabel>
              <Input
                id="database-name"
                value={newDatabaseName}
                onChange={(e) => setNewDatabaseName(e.target.value)}
              />
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel htmlFor="database-description">描述（可选）</InputLabel>
              <Input
                id="database-description"
                value={newDatabaseDescription}
                onChange={(e) => setNewDatabaseDescription(e.target.value)}
                multiline
                rows={2}
              />
            </FormControl>
            
            <FormControl fullWidth margin="normal">
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
              >
                选择文件
              </Button>
              <FormHelperText>
                {selectedFile ? `已选择: ${selectedFile.name}` : '支持Excel、CSV、JSON格式'}
              </FormHelperText>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setImportDialogOpen(false)}>
              取消
            </Button>
            <Button 
              variant="contained" 
              onClick={handleImportSubmit}
              disabled={!newDatabaseName || !selectedFile || loading}
            >
              {loading ? <CircularProgress size={24} /> : '导入'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* 成功提示 */}
        <Snackbar
          open={openSnackbar}
          autoHideDuration={6000}
          onClose={handleCloseSnackbar}
        >
          <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
            {success}
          </Alert>
        </Snackbar>
      </Container>
    </>
  );
}
