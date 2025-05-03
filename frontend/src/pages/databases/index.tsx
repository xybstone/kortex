import { useState } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  CardActions,
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Input,
  FormHelperText
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import Head from 'next/head';
import { useRouter } from 'next/router';

// 模拟数据库数据
const mockDatabases = [
  { id: 1, name: '项目数据', description: '项目相关数据', tables: 3, updatedAt: '2023-05-10' },
  { id: 2, name: '客户信息', description: '客户联系信息', tables: 1, updatedAt: '2023-05-09' },
  { id: 3, name: '产品目录', description: '产品信息和价格', tables: 2, updatedAt: '2023-05-08' },
  { id: 4, name: '销售记录', description: '销售交易记录', tables: 4, updatedAt: '2023-05-07' },
];

export default function Databases() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [importDialogOpen, setImportDialogOpen] = useState(false);
  const [newDatabaseName, setNewDatabaseName] = useState('');
  const [newDatabaseDescription, setNewDatabaseDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  // 根据搜索词过滤数据库
  const filteredDatabases = mockDatabases.filter(db => 
    db.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    db.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleImportSubmit = () => {
    // 在实际应用中，这里会调用API导入数据库
    console.log('导入数据库:', { name: newDatabaseName, description: newDatabaseDescription, file: selectedFile });
    setImportDialogOpen(false);
    setNewDatabaseName('');
    setNewDatabaseDescription('');
    setSelectedFile(null);
  };

  return (
    <>
      <Head>
        <title>数据库 | Kortex</title>
        <meta name="description" content="Kortex数据库管理" />
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
                    {database.description}
                  </Typography>
                  <Typography variant="body2">
                    {database.tables} 个表格
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'flex-end' }}>
                  <Typography variant="caption" color="text.secondary">
                    更新于 {database.updatedAt}
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
              disabled={!newDatabaseName || !selectedFile}
            >
              导入
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </>
  );
}
