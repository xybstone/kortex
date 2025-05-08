import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
  Paper,
  Tabs,
  Tab,
  IconButton,
  ButtonGroup
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ChatIcon from '@mui/icons-material/Chat';
import Head from 'next/head';
import { useRouter } from 'next/router';
import datasetApi, { DataSource, DatabaseSource, FileSource, URLSource } from '@/services/datasetApi';
import TaskList from '@/components/processing/TaskList';
import CreateTaskDialog from '@/components/processing/CreateTaskDialog';
import NLProcessingDialog from '@/components/processing/NLProcessingDialog';

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
      id={`source-tabpanel-${index}`}
      aria-labelledby={`source-tab-${index}`}
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

export default function DataSourceDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [dataSource, setDataSource] = useState<DataSource | null>(null);
  const [dataset, setDataset] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [createTaskDialogOpen, setCreateTaskDialogOpen] = useState(false);
  const [nlProcessingDialogOpen, setNLProcessingDialogOpen] = useState(false);

  // 获取数据源详情
  useEffect(() => {
    const fetchDataSource = async () => {
      if (!id) return;

      setLoading(true);
      try {
        // 获取数据源详情
        // 注意：这里需要先获取数据集列表，然后找到包含该数据源的数据集
        const datasets = await datasetApi.getDatasets();

        let foundDataSource: DataSource | null = null;
        let foundDataset = null;

        // 遍历所有数据集，查找数据源
        for (const dataset of datasets) {
          const source = dataset.data_sources.find(source => source.id === Number(id));
          if (source) {
            foundDataSource = source;
            foundDataset = dataset;
            break;
          }
        }

        if (foundDataSource && foundDataset) {
          setDataSource(foundDataSource);
          setDataset(foundDataset);
          setError(null);
        } else {
          setError('数据源不存在');
        }
      } catch (err: any) {
        console.error('获取数据源详情失败:', err);
        setError(err.response?.data?.detail || '获取数据源详情失败，请稍后再试');
      } finally {
        setLoading(false);
      }
    };

    fetchDataSource();
  }, [id]);

  // 处理标签切换
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
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
            <Typography variant="body1" sx={{ mb: 1 }}>
              <strong>类型:</strong> {dbSource.database_type}
            </Typography>
            {dbSource.connection_string && (
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>连接字符串:</strong> {dbSource.connection_string}
              </Typography>
            )}
          </>
        );
      case 'file':
        const fileSource = source as FileSource;
        return (
          <>
            <Typography variant="body1" sx={{ mb: 1 }}>
              <strong>文件类型:</strong> {fileSource.file_type}
            </Typography>
            {fileSource.file_size && (
              <Typography variant="body1" sx={{ mb: 1 }}>
                <strong>文件大小:</strong> {(fileSource.file_size / 1024).toFixed(2)} KB
              </Typography>
            )}
            <Typography variant="body1" sx={{ mb: 1 }}>
              <strong>文件路径:</strong> {fileSource.file_path}
            </Typography>
          </>
        );
      case 'url':
        const urlSource = source as URLSource;
        return (
          <>
            <Typography variant="body1" sx={{ mb: 1 }}>
              <strong>URL:</strong> {urlSource.url}
            </Typography>
            <Typography variant="body1" sx={{ mb: 1 }}>
              <strong>爬取深度:</strong> {urlSource.crawl_depth}
            </Typography>
          </>
        );
      default:
        return (
          <Typography variant="body1">
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

  if (error || !dataSource || !dataset) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error || '数据源不存在'}
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => router.back()}
        >
          返回
        </Button>
      </Container>
    );
  }

  return (
    <>
      <Head>
        <title>{dataSource.name} | 数据源 | Kortex</title>
        <meta name="description" content={`Kortex数据源: ${dataSource.name}`} />
      </Head>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* 顶部导航和操作 */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              onClick={() => router.push(`/datasets/${dataset.id}`)}
              sx={{ mr: 1 }}
            >
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="h4" component="h1">
              {dataSource.name}
            </Typography>
          </Box>
          <ButtonGroup variant="contained">
            <Button
              startIcon={<PlayArrowIcon />}
              onClick={() => setCreateTaskDialogOpen(true)}
            >
              创建处理任务
            </Button>
            <Button
              startIcon={<ChatIcon />}
              onClick={() => setNLProcessingDialogOpen(true)}
              color="secondary"
            >
              自然语言处理
            </Button>
          </ButtonGroup>
        </Box>

        {/* 数据源信息 */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            数据源信息
          </Typography>
          <Typography variant="body1" sx={{ mb: 1 }}>
            <strong>类型:</strong> {getDataSourceTypeText(dataSource.type)}
          </Typography>
          {dataSource.description && (
            <Typography variant="body1" sx={{ mb: 1 }}>
              <strong>描述:</strong> {dataSource.description}
            </Typography>
          )}
          {getDataSourceDetails(dataSource)}
          <Typography variant="body1" sx={{ mb: 1 }}>
            <strong>处理状态:</strong> {dataSource.processing_status}
          </Typography>
          <Typography variant="body1" sx={{ mb: 1 }}>
            <strong>创建时间:</strong> {new Date(dataSource.created_at).toLocaleString()}
          </Typography>
          {dataSource.last_processed_at && (
            <Typography variant="body1" sx={{ mb: 1 }}>
              <strong>最后处理时间:</strong> {new Date(dataSource.last_processed_at).toLocaleString()}
            </Typography>
          )}
          {dataSource.processing_error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>处理错误:</strong> {dataSource.processing_error}
              </Typography>
            </Alert>
          )}
        </Paper>

        {/* 标签页 */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="数据源标签页">
            <Tab label="处理任务" id="source-tab-0" aria-controls="source-tabpanel-0" />
          </Tabs>
        </Box>

        {/* 处理任务标签页 */}
        <TabPanel value={tabValue} index={0}>
          <TaskList dataSourceId={dataSource.id} onRefresh={() => {
            // 刷新数据源数据
            if (dataset) {
              datasetApi.getDataset(dataset.id).then(data => {
                const updatedSource = data.data_sources.find(source => source.id === dataSource.id);
                if (updatedSource) {
                  setDataSource(updatedSource);
                }
              });
            }
          }} />
        </TabPanel>

        {/* 创建处理任务对话框 */}
        <CreateTaskDialog
          open={createTaskDialogOpen}
          onClose={() => setCreateTaskDialogOpen(false)}
          dataSource={dataSource}
          onTaskCreated={() => {
            setCreateTaskDialogOpen(false);
            // 刷新数据源数据
            if (dataset) {
              datasetApi.getDataset(dataset.id).then(data => {
                const updatedSource = data.data_sources.find(source => source.id === dataSource.id);
                if (updatedSource) {
                  setDataSource(updatedSource);
                }
              });
            }
          }}
        />

        {/* 自然语言处理对话框 */}
        <NLProcessingDialog
          open={nlProcessingDialogOpen}
          onClose={() => setNLProcessingDialogOpen(false)}
          dataSource={dataSource}
          onTaskCreated={() => {
            setNLProcessingDialogOpen(false);
            // 刷新数据源数据
            if (dataset) {
              datasetApi.getDataset(dataset.id).then(data => {
                const updatedSource = data.data_sources.find(source => source.id === dataSource.id);
                if (updatedSource) {
                  setDataSource(updatedSource);
                }
              });
            }
          }}
        />
      </Container>
    </>
  );
}
