import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardHeader,
  CardActions,
  IconButton,
  Divider,
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
  Stack,
  Tabs,
  Tab,
  TextField,
  MenuItem,
  Select,
  Paper
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import StorageIcon from '@mui/icons-material/Storage';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import LinkIcon from '@mui/icons-material/Link';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import Head from 'next/head';
import { useRouter } from 'next/router';
import datasetApi, {
  Dataset,
  DataSource,
  DatabaseSource,
  FileSource,
  URLSource,
  CreateDatabaseSourceRequest,
  CreateURLSourceRequest,
  UpdateDatasetRequest
} from '@/services/datasetApi';
import TaskList from '@/components/processing/TaskList';
import CreateTaskDialog from '@/components/processing/CreateTaskDialog';

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
      id={`dataset-tabpanel-${index}`}
      aria-labelledby={`dataset-tab-${index}`}
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

export default function DatasetDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);

  // 对话框状态
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [addSourceDialogOpen, setAddSourceDialogOpen] = useState(false);
  const [deleteSourceDialogOpen, setDeleteSourceDialogOpen] = useState(false);
  const [createTaskDialogOpen, setCreateTaskDialogOpen] = useState(false);
  const [selectedSourceId, setSelectedSourceId] = useState<number | null>(null);
  const [selectedSource, setSelectedSource] = useState<DataSource | null>(null);

  // 表单状态
  const [datasetName, setDatasetName] = useState('');
  const [datasetDescription, setDatasetDescription] = useState('');
  const [sourceType, setSourceType] = useState('database');
  const [sourceName, setSourceName] = useState('');
  const [sourceDescription, setSourceDescription] = useState('');
  const [databaseType, setDatabaseType] = useState('postgresql');
  const [connectionString, setConnectionString] = useState('');
  const [url, setUrl] = useState('');
  const [crawlDepth, setCrawlDepth] = useState(1);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // 获取数据集详情
  useEffect(() => {
    const fetchDataset = async () => {
      if (!id) return;

      setLoading(true);
      try {
        const data = await datasetApi.getDataset(Number(id));
        setDataset(data);
        setDatasetName(data.name);
        setDatasetDescription(data.description || '');
        setError(null);
      } catch (err: any) {
        console.error('获取数据集详情失败:', err);
        setError(err.response?.data?.detail || '获取数据集详情失败，请稍后再试');
      } finally {
        setLoading(false);
      }
    };

    fetchDataset();
  }, [id]);

  // 处理标签切换
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // 更新数据集
  const handleUpdateDataset = async () => {
    if (!dataset || !datasetName) return;

    try {
      const updateData: UpdateDatasetRequest = {
        name: datasetName,
        description: datasetDescription || undefined
      };

      const updatedDataset = await datasetApi.updateDataset(dataset.id, updateData);
      setDataset(updatedDataset);
      setEditDialogOpen(false);
      setError(null);
    } catch (err: any) {
      console.error('更新数据集失败:', err);
      setError(err.response?.data?.detail || '更新数据集失败，请稍后再试');
    }
  };

  // 删除数据集
  const handleDeleteDataset = async () => {
    if (!dataset) return;

    try {
      await datasetApi.deleteDataset(dataset.id);
      router.push('/datasets');
    } catch (err: any) {
      console.error('删除数据集失败:', err);
      setError(err.response?.data?.detail || '删除数据集失败，请稍后再试');
      setDeleteDialogOpen(false);
    }
  };

  // 添加数据源
  const handleAddSource = async () => {
    if (!dataset || !sourceName) return;

    try {
      let updatedDataset: Dataset | null = null;

      if (sourceType === 'database') {
        // 添加数据库源
        const databaseSource: CreateDatabaseSourceRequest = {
          name: sourceName,
          description: sourceDescription || undefined,
          database_type: databaseType,
          connection_string: connectionString || undefined
        };

        updatedDataset = await datasetApi.addDatabaseSource(dataset.id, databaseSource);
      } else if (sourceType === 'url') {
        // 添加URL源
        const urlSource: CreateURLSourceRequest = {
          name: sourceName,
          description: sourceDescription || undefined,
          url: url,
          crawl_depth: crawlDepth
        };

        updatedDataset = await datasetApi.addURLSource(dataset.id, urlSource);
      } else if (sourceType === 'file' && selectedFile) {
        // 添加文件源
        await datasetApi.addFileSource(dataset.id, sourceName, sourceDescription, selectedFile);
        // 重新获取数据集以获取更新后的数据源列表
        updatedDataset = await datasetApi.getDataset(dataset.id);
      }

      if (updatedDataset) {
        setDataset(updatedDataset);
      }

      // 重置表单
      setSourceName('');
      setSourceDescription('');
      setConnectionString('');
      setUrl('');
      setCrawlDepth(1);
      setSelectedFile(null);
      setAddSourceDialogOpen(false);
      setError(null);
    } catch (err: any) {
      console.error('添加数据源失败:', err);
      setError(err.response?.data?.detail || '添加数据源失败，请稍后再试');
    }
  };

  // 删除数据源
  const handleDeleteSource = async () => {
    if (!dataset || selectedSourceId === null) return;

    try {
      await datasetApi.deleteDataSource(dataset.id, selectedSourceId);

      // 更新数据集数据
      const updatedDataset = await datasetApi.getDataset(dataset.id);
      setDataset(updatedDataset);

      setDeleteSourceDialogOpen(false);
      setSelectedSourceId(null);
      setError(null);
    } catch (err: any) {
      console.error('删除数据源失败:', err);
      setError(err.response?.data?.detail || '删除数据源失败，请稍后再试');
      setDeleteSourceDialogOpen(false);
    }
  };

  // 处理文件选择
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    }
  };

  // 获取数据源类型图标
  const getDataSourceIcon = (type: string) => {
    switch (type) {
      case 'database':
        return <StorageIcon />;
      case 'file':
        return <InsertDriveFileIcon />;
      case 'url':
        return <LinkIcon />;
      default:
        return <StorageIcon />; // 默认使用存储图标
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

  // 获取数据源详情
  const getDataSourceDetails = (source: DataSource) => {
    switch (source.type) {
      case 'database':
        const dbSource = source as DatabaseSource;
        return (
          <>
            <Typography variant="body2" color="text.secondary">
              类型: {dbSource.database_type}
            </Typography>
            {dbSource.connection_string && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                连接字符串: {dbSource.connection_string}
              </Typography>
            )}
          </>
        );
      case 'file':
        const fileSource = source as FileSource;
        return (
          <>
            <Typography variant="body2" color="text.secondary">
              文件类型: {fileSource.file_type}
            </Typography>
            {fileSource.file_size && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                文件大小: {(fileSource.file_size / 1024).toFixed(2)} KB
              </Typography>
            )}
          </>
        );
      case 'url':
        const urlSource = source as URLSource;
        return (
          <>
            <Typography variant="body2" color="text.secondary">
              URL: {urlSource.url}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              爬取深度: {urlSource.crawl_depth}
            </Typography>
          </>
        );
      default:
        return (
          <Typography variant="body2" color="text.secondary">
            未知数据源类型
          </Typography>
        );
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error && !dataset) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => router.push('/datasets')}
        >
          返回数据集列表
        </Button>
      </Container>
    );
  }

  if (!dataset) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          数据集不存在
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => router.push('/datasets')}
        >
          返回数据集列表
        </Button>
      </Container>
    );
  }

  return (
    <>
      <Head>
        <title>{dataset.name} | 数据集 | Kortex</title>
        <meta name="description" content={`Kortex数据集: ${dataset.name}`} />
      </Head>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* 顶部导航和操作 */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              onClick={() => router.push('/datasets')}
              sx={{ mr: 1 }}
            >
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="h4" component="h1">
              {dataset.name}
            </Typography>
          </Box>
          <Box>
            <IconButton
              onClick={() => setEditDialogOpen(true)}
              sx={{ mr: 1 }}
            >
              <EditIcon />
            </IconButton>
            <IconButton
              onClick={() => setDeleteDialogOpen(true)}
              color="error"
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        </Box>

        {/* 描述 */}
        {dataset.description && (
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {dataset.description}
          </Typography>
        )}

        {/* 错误提示 */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* 标签页 */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="数据集标签页">
            <Tab label="数据源" id="dataset-tab-0" aria-controls="dataset-tabpanel-0" />
            <Tab label="处理任务" id="dataset-tab-1" aria-controls="dataset-tabpanel-1" />
            <Tab label="关联笔记" id="dataset-tab-2" aria-controls="dataset-tabpanel-2" />
          </Tabs>
        </Box>

        {/* 数据源标签页 */}
        <TabPanel value={tabValue} index={0}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setAddSourceDialogOpen(true)}
            >
              添加数据源
            </Button>
          </Box>

          {dataset.data_sources.length === 0 ? (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography variant="body1" color="text.secondary">
                暂无数据源，点击"添加数据源"按钮添加
              </Typography>
            </Paper>
          ) : (
            <Grid container spacing={3}>
              {dataset.data_sources.map((source) => (
                <Grid item xs={12} sm={6} key={source.id}>
                  <Card
                    sx={{
                      cursor: 'pointer',
                      '&:hover': {
                        boxShadow: 6
                      }
                    }}
                    onClick={() => router.push(`/datasets/sources/${source.id}`)}
                  >
                    <CardHeader
                      avatar={getDataSourceIcon(source.type)}
                      title={source.name}
                      subheader={getDataSourceTypeText(source.type)}
                      action={
                        <IconButton
                          aria-label="删除"
                          onClick={(e) => {
                            e.stopPropagation(); // 阻止事件冒泡
                            setSelectedSourceId(source.id);
                            setDeleteSourceDialogOpen(true);
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      }
                    />
                    <CardContent>
                      {source.description && (
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {source.description}
                        </Typography>
                      )}
                      {getDataSourceDetails(source)}
                      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Chip
                          label={source.processing_status}
                          color={source.processing_status === 'completed' ? 'success' :
                                 source.processing_status === 'failed' ? 'error' :
                                 source.processing_status === 'processing' ? 'primary' : 'default'}
                          size="small"
                        />
                        <Button
                          size="small"
                          startIcon={<PlayArrowIcon />}
                          onClick={(e) => {
                            e.stopPropagation(); // 阻止事件冒泡
                            setSelectedSource(source);
                            setCreateTaskDialogOpen(true);
                          }}
                        >
                          创建任务
                        </Button>
                      </Box>
                    </CardContent>
                    <CardActions sx={{ justifyContent: 'flex-end' }}>
                      <Typography variant="caption" color="text.secondary">
                        添加于 {new Date(source.created_at).toLocaleDateString()}
                      </Typography>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </TabPanel>

        {/* 处理任务标签页 */}
        <TabPanel value={tabValue} index={1}>
          <TaskList dataSourceId={undefined} onRefresh={() => {
            // 刷新数据集数据
            if (dataset) {
              datasetApi.getDataset(dataset.id).then(data => {
                setDataset(data);
              });
            }
          }} />
        </TabPanel>

        {/* 关联笔记标签页 */}
        <TabPanel value={tabValue} index={2}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              关联笔记功能将在笔记编辑页面中实现
            </Typography>
          </Paper>
        </TabPanel>

        {/* 编辑数据集对话框 */}
        <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>编辑数据集</DialogTitle>
          <DialogContent>
            <FormControl fullWidth margin="normal">
              <InputLabel htmlFor="dataset-name">数据集名称</InputLabel>
              <Input
                id="dataset-name"
                value={datasetName}
                onChange={(e) => setDatasetName(e.target.value)}
                required
              />
            </FormControl>
            <FormControl fullWidth margin="normal">
              <InputLabel htmlFor="dataset-description">描述（可选）</InputLabel>
              <Input
                id="dataset-description"
                value={datasetDescription}
                onChange={(e) => setDatasetDescription(e.target.value)}
                multiline
                rows={3}
              />
              <FormHelperText>简要描述这个数据集的用途和内容</FormHelperText>
            </FormControl>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEditDialogOpen(false)}>取消</Button>
            <Button
              onClick={handleUpdateDataset}
              variant="contained"
              disabled={!datasetName}
            >
              保存
            </Button>
          </DialogActions>
        </Dialog>

        {/* 删除数据集确认对话框 */}
        <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
          <DialogTitle>删除数据集</DialogTitle>
          <DialogContent>
            <Typography>
              确定要删除数据集"{dataset.name}"吗？此操作不可撤销，所有关联的数据源也将被删除。
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteDialogOpen(false)}>取消</Button>
            <Button onClick={handleDeleteDataset} color="error">
              删除
            </Button>
          </DialogActions>
        </Dialog>

        {/* 添加数据源对话框 */}
        <Dialog open={addSourceDialogOpen} onClose={() => setAddSourceDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>添加数据源</DialogTitle>
          <DialogContent>
            <FormControl fullWidth margin="normal">
              <InputLabel id="source-type-label">数据源类型</InputLabel>
              <Select
                labelId="source-type-label"
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                label="数据源类型"
              >
                <MenuItem value="database">数据库</MenuItem>
                <MenuItem value="file">文件</MenuItem>
                <MenuItem value="url">网址</MenuItem>
              </Select>
            </FormControl>

            <FormControl fullWidth margin="normal">
              <InputLabel htmlFor="source-name">名称</InputLabel>
              <Input
                id="source-name"
                value={sourceName}
                onChange={(e) => setSourceName(e.target.value)}
                required
              />
            </FormControl>

            <FormControl fullWidth margin="normal">
              <InputLabel htmlFor="source-description">描述（可选）</InputLabel>
              <Input
                id="source-description"
                value={sourceDescription}
                onChange={(e) => setSourceDescription(e.target.value)}
                multiline
                rows={2}
              />
            </FormControl>

            {/* 数据库特有字段 */}
            {sourceType === 'database' && (
              <>
                <FormControl fullWidth margin="normal">
                  <InputLabel id="database-type-label">数据库类型</InputLabel>
                  <Select
                    labelId="database-type-label"
                    value={databaseType}
                    onChange={(e) => setDatabaseType(e.target.value as string)}
                    label="数据库类型"
                  >
                    <MenuItem value="postgresql">PostgreSQL</MenuItem>
                    <MenuItem value="mysql">MySQL</MenuItem>
                    <MenuItem value="sqlite">SQLite</MenuItem>
                    <MenuItem value="mongodb">MongoDB</MenuItem>
                    <MenuItem value="other">其他</MenuItem>
                  </Select>
                </FormControl>

                <FormControl fullWidth margin="normal">
                  <InputLabel htmlFor="connection-string">连接字符串（可选）</InputLabel>
                  <Input
                    id="connection-string"
                    value={connectionString}
                    onChange={(e) => setConnectionString(e.target.value)}
                  />
                  <FormHelperText>例如: postgresql://user:password@localhost:5432/dbname</FormHelperText>
                </FormControl>
              </>
            )}

            {/* 文件特有字段 */}
            {sourceType === 'file' && (
              <FormControl fullWidth margin="normal">
                <Input
                  id="file-upload"
                  type="file"
                  onChange={handleFileChange}
                />
                <FormHelperText>支持PDF、Markdown、CSV、Excel等文件格式</FormHelperText>
              </FormControl>
            )}

            {/* URL特有字段 */}
            {sourceType === 'url' && (
              <>
                <FormControl fullWidth margin="normal">
                  <InputLabel htmlFor="url">URL</InputLabel>
                  <Input
                    id="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    required
                  />
                  <FormHelperText>例如: https://example.com</FormHelperText>
                </FormControl>

                <FormControl fullWidth margin="normal">
                  <InputLabel htmlFor="crawl-depth">爬取深度</InputLabel>
                  <Input
                    id="crawl-depth"
                    type="number"
                    value={crawlDepth}
                    onChange={(e) => setCrawlDepth(parseInt(e.target.value))}
                    inputProps={{ min: 1, max: 5 }}
                  />
                  <FormHelperText>1-5之间的整数，表示爬取的链接层级</FormHelperText>
                </FormControl>
              </>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setAddSourceDialogOpen(false)}>取消</Button>
            <Button
              onClick={handleAddSource}
              variant="contained"
              disabled={!sourceName || (sourceType === 'file' && !selectedFile) || (sourceType === 'url' && !url)}
            >
              添加
            </Button>
          </DialogActions>
        </Dialog>

        {/* 删除数据源确认对话框 */}
        <Dialog open={deleteSourceDialogOpen} onClose={() => setDeleteSourceDialogOpen(false)}>
          <DialogTitle>删除数据源</DialogTitle>
          <DialogContent>
            <Typography>
              确定要删除这个数据源吗？此操作不可撤销。
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteSourceDialogOpen(false)}>取消</Button>
            <Button onClick={handleDeleteSource} color="error">
              删除
            </Button>
          </DialogActions>
        </Dialog>

        {/* 创建处理任务对话框 */}
        {selectedSource && (
          <CreateTaskDialog
            open={createTaskDialogOpen}
            onClose={() => setCreateTaskDialogOpen(false)}
            dataSource={selectedSource}
            onTaskCreated={() => {
              setCreateTaskDialogOpen(false);
              // 刷新数据集数据
              if (dataset) {
                datasetApi.getDataset(dataset.id).then(data => {
                  setDataset(data);
                });
              }
              // 切换到处理任务标签页
              setTabValue(1);
            }}
          />
        )}
      </Container>
    </>
  );
}
