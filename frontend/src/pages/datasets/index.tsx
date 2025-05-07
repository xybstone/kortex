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
  TextField,
  InputAdornment,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Input,
  FormHelperText,
  CircularProgress,
  Alert,
  Chip,
  Stack
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import StorageIcon from '@mui/icons-material/Storage';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import LinkIcon from '@mui/icons-material/Link';
import Head from 'next/head';
import { useRouter } from 'next/router';
import datasetApi, { Dataset } from '@/services/datasetApi';

export default function Datasets() {
  const router = useRouter();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newDatasetName, setNewDatasetName] = useState('');
  const [newDatasetDescription, setNewDatasetDescription] = useState('');

  // 获取数据集列表
  useEffect(() => {
    const fetchDatasets = async () => {
      setLoading(true);
      try {
        const data = await datasetApi.getDatasets();
        setDatasets(data);
        setError(null);
      } catch (err: any) {
        console.error('获取数据集列表失败:', err);
        setError(err.response?.data?.detail || '获取数据集列表失败，请稍后再试');
      } finally {
        setLoading(false);
      }
    };

    fetchDatasets();
  }, []);

  // 根据搜索词过滤数据集
  const filteredDatasets = datasets.filter(dataset =>
    dataset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (dataset.description && dataset.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // 创建新数据集
  const handleCreateDataset = async () => {
    if (!newDatasetName) return;

    try {
      const newDataset = await datasetApi.createDataset({
        name: newDatasetName,
        description: newDatasetDescription || undefined
      });

      setDatasets([...datasets, newDataset]);
      setCreateDialogOpen(false);
      setNewDatasetName('');
      setNewDatasetDescription('');

      // 跳转到新创建的数据集详情页
      router.push(`/datasets/${newDataset.id}`);
    } catch (err: any) {
      console.error('创建数据集失败:', err);
      setError(err.response?.data?.detail || '创建数据集失败，请稍后再试');
    }
  };

  // 获取数据源类型图标
  const getDataSourceIcon = (type: string) => {
    switch (type) {
      case 'database':
        return <StorageIcon fontSize="small" />;
      case 'file':
        return <InsertDriveFileIcon fontSize="small" />;
      case 'url':
        return <LinkIcon fontSize="small" />;
      default:
        return <StorageIcon fontSize="small" />; // 默认使用存储图标
    }
  };

  // 获取数据源类型文本
  const getDataSourceTypeText = (type: string) => {
    switch (type) {
      case 'database':
        return '数据库';
      case 'file':
        return '文件';
      case 'url':
        return '网址';
      default:
        return type;
    }
  };

  return (
    <>
      <Head>
        <title>数据集 | Kortex</title>
        <meta name="description" content="Kortex数据集管理" />
      </Head>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            我的数据集
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            新建数据集
          </Button>
        </Box>

        <TextField
          fullWidth
          variant="outlined"
          placeholder="搜索数据集..."
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

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {filteredDatasets.map((dataset) => (
              <Grid item xs={12} sm={6} md={4} key={dataset.id}>
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
                  onClick={() => router.push(`/datasets/${dataset.id}`)}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography gutterBottom variant="h5" component="h2">
                      {dataset.name}
                    </Typography>
                    <Typography color="text.secondary" paragraph>
                      {dataset.description || '无描述'}
                    </Typography>
                    <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
                      {dataset.data_sources && dataset.data_sources.length > 0 ? (
                        dataset.data_sources.slice(0, 3).map((source) => (
                          <Chip
                            key={source.id}
                            icon={getDataSourceIcon(source.type)}
                            label={getDataSourceTypeText(source.type)}
                            size="small"
                            variant="outlined"
                          />
                        ))
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          暂无数据源
                        </Typography>
                      )}
                      {dataset.data_sources && dataset.data_sources.length > 3 && (
                        <Chip
                          label={`+${dataset.data_sources.length - 3}`}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </Stack>
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'flex-end' }}>
                    <Typography variant="caption" color="text.secondary">
                      更新于 {new Date(dataset.updated_at || dataset.created_at).toLocaleDateString()}
                    </Typography>
                  </CardActions>
                </Card>
              </Grid>
            ))}

            {filteredDatasets.length === 0 && (
              <Grid item xs={12}>
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="h6" color="text.secondary">
                    没有找到匹配的数据集
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="contained"
                      startIcon={<AddIcon />}
                      onClick={() => setCreateDialogOpen(true)}
                    >
                      新建数据集
                    </Button>
                  </Box>
                </Box>
              </Grid>
            )}
          </Grid>
        )}

        {/* 创建数据集对话框 */}
        <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>新建数据集</DialogTitle>
          <DialogContent>
            <FormControl fullWidth margin="normal">
              <InputLabel htmlFor="dataset-name">数据集名称</InputLabel>
              <Input
                id="dataset-name"
                value={newDatasetName}
                onChange={(e) => setNewDatasetName(e.target.value)}
                required
              />
            </FormControl>
            <FormControl fullWidth margin="normal">
              <InputLabel htmlFor="dataset-description">描述（可选）</InputLabel>
              <Input
                id="dataset-description"
                value={newDatasetDescription}
                onChange={(e) => setNewDatasetDescription(e.target.value)}
                multiline
                rows={3}
              />
              <FormHelperText>简要描述这个数据集的用途和内容</FormHelperText>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreateDialogOpen(false)}>取消</Button>
            <Button
              onClick={handleCreateDataset}
              variant="contained"
              disabled={!newDatasetName}
            >
              创建
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </>
  );
}
