import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Button,
  CircularProgress,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Tabs,
  Tab,
  Menu,
  MenuItem,
  Divider
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CancelIcon from '@mui/icons-material/Cancel';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DownloadIcon from '@mui/icons-material/Download';
import BarChartIcon from '@mui/icons-material/BarChart';
import AlarmIcon from '@mui/icons-material/Alarm';
import processingApi, { ProcessingTask } from '@/services/processingApi';
import DataVisualization from '../visualization/DataVisualization';
import ScheduleTaskDialog from './ScheduleTaskDialog';
import { exportData, batchExport } from '@/utils/exportUtils';

interface TaskListProps {
  dataSourceId?: number | undefined;
  onRefresh?: () => void;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'failed':
      return 'error';
    case 'running':
      return 'primary';
    case 'cancelled':
      return 'warning';
    default:
      return 'default';
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'pending':
      return '待处理';
    case 'running':
      return '处理中';
    case 'completed':
      return '已完成';
    case 'failed':
      return '失败';
    case 'cancelled':
      return '已取消';
    default:
      return status;
  }
};

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
      id={`task-tabpanel-${index}`}
      aria-labelledby={`task-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 2 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const TaskList: React.FC<TaskListProps> = ({ dataSourceId, onRefresh }) => {
  const [tasks, setTasks] = useState<ProcessingTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<ProcessingTask | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const params: any = { limit: 100 };
      if (dataSourceId) {
        params.data_source_id = dataSourceId;
      }
      const data = await processingApi.getTasks(params);
      setTasks(data);
      setError(null);
    } catch (err: any) {
      console.error('获取处理任务失败:', err);
      setError(err.response?.data?.detail || '获取处理任务失败，请稍后再试');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
    // 设置定时刷新
    const intervalId = setInterval(() => {
      fetchTasks();
    }, 5000); // 每5秒刷新一次

    return () => clearInterval(intervalId);
  }, [dataSourceId]);

  const handleRefresh = () => {
    fetchTasks();
    if (onRefresh) {
      onRefresh();
    }
  };

  const handleViewDetails = (task: ProcessingTask) => {
    setSelectedTask(task);
    setDetailsOpen(true);
  };

  const handleCancelTask = async (taskId: number) => {
    try {
      await processingApi.cancelTask(taskId);
      fetchTasks();
    } catch (err: any) {
      console.error('取消任务失败:', err);
      setError(err.response?.data?.detail || '取消任务失败，请稍后再试');
    }
  };

  const handleDeleteTask = async () => {
    if (!selectedTask) return;

    try {
      await processingApi.deleteTask(selectedTask.id);
      setConfirmDeleteOpen(false);
      fetchTasks();
    } catch (err: any) {
      console.error('删除任务失败:', err);
      setError(err.response?.data?.detail || '删除任务失败，请稍后再试');
    }
  };

  const confirmDelete = (task: ProcessingTask) => {
    setSelectedTask(task);
    setConfirmDeleteOpen(true);
  };

  // 处理标签切换
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // 处理导出数据
  const handleExportData = (format: 'json' | 'csv' | 'excel' | 'pdf' | 'txt') => {
    if (!selectedTask || !selectedTask.result) return;

    // 如果结果包含sample_data字段，使用它
    const data = selectedTask.result.sample_data || selectedTask.result;

    // 准备导出选项
    const options: any = {
      fileName: `task-${selectedTask.id}-result`,
      addTimestamp: true
    };

    // 添加PDF特定选项
    if (format === 'pdf') {
      options.pdfOptions = {
        title: selectedTask.name,
        orientation: 'landscape' as 'landscape' | 'portrait',
        pageSize: 'a4'
      };
    }

    // 添加Excel特定选项
    if (format === 'excel') {
      options.excelOptions = {
        sheetName: `Task-${selectedTask.id}`,
        includeHeader: true
      };
    }

    // 使用导出工具导出数据
    exportData(data, format, options);
  };

  // 处理批量导出
  const handleBatchExport = () => {
    if (!selectedTask || !selectedTask.result) return;

    // 如果结果包含sample_data字段，使用它
    const data = selectedTask.result.sample_data || selectedTask.result;

    // 准备批量导出项目
    const items = [
      {
        data,
        fileName: `task-${selectedTask.id}-result-json`,
        format: 'json' as const
      },
      {
        data,
        fileName: `task-${selectedTask.id}-result-csv`,
        format: 'csv' as const
      },
      {
        data,
        fileName: `task-${selectedTask.id}-result-excel`,
        format: 'excel' as const,
        options: {
          excelOptions: {
            sheetName: `Task-${selectedTask.id}`,
            includeHeader: true
          }
        }
      },
      {
        data,
        fileName: `task-${selectedTask.id}-result-pdf`,
        format: 'pdf' as const,
        options: {
          pdfOptions: {
            title: selectedTask.name,
            orientation: 'landscape' as 'landscape' | 'portrait',
            pageSize: 'a4'
          }
        }
      }
    ];

    // 批量导出
    batchExport(items, `task-${selectedTask.id}-all-formats`);

    // 关闭菜单
    handleExportMenuClose();
  };

  // 导出菜单状态
  const [exportMenuAnchorEl, setExportMenuAnchorEl] = useState<null | HTMLElement>(null);
  const exportMenuOpen = Boolean(exportMenuAnchorEl);

  // 打开导出菜单
  const handleExportMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setExportMenuAnchorEl(event.currentTarget);
  };

  // 关闭导出菜单
  const handleExportMenuClose = () => {
    setExportMenuAnchorEl(null);
  };

  if (loading && tasks.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" component="h2">
          处理任务
        </Typography>
        <Button
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
          size="small"
        >
          刷新
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {tasks.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            暂无处理任务
          </Typography>
        </Paper>
      ) : (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>名称</TableCell>
                <TableCell>类型</TableCell>
                <TableCell>状态</TableCell>
                <TableCell>进度</TableCell>
                <TableCell>创建时间</TableCell>
                <TableCell>操作</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tasks.map((task) => (
                <TableRow key={task.id}>
                  <TableCell>{task.name}</TableCell>
                  <TableCell>{task.task_type}</TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusText(task.status)}
                      color={getStatusColor(task.status) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {task.status === 'running' ? (
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <CircularProgress
                          variant="determinate"
                          value={task.progress}
                          size={24}
                          sx={{ mr: 1 }}
                        />
                        <Typography variant="body2">{task.progress}%</Typography>
                      </Box>
                    ) : (
                      <Typography variant="body2">
                        {task.status === 'completed' ? '100%' : task.progress + '%'}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {new Date(task.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Tooltip title="查看详情">
                      <IconButton
                        size="small"
                        onClick={() => handleViewDetails(task)}
                      >
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    {['completed', 'failed', 'cancelled'].includes(task.status) && (
                      <Tooltip title="设置调度">
                        <IconButton
                          size="small"
                          color="primary"
                          onClick={() => {
                            setSelectedTask(task);
                            setScheduleDialogOpen(true);
                          }}
                        >
                          <AlarmIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                    {task.status === 'pending' || task.status === 'running' ? (
                      <Tooltip title="取消任务">
                        <IconButton
                          size="small"
                          color="warning"
                          onClick={() => handleCancelTask(task.id)}
                        >
                          <CancelIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    ) : (
                      <Tooltip title="删除任务">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => confirmDelete(task)}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* 任务详情对话框 */}
      <Dialog
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedTask?.name}
          <Box sx={{ position: 'absolute', right: 8, top: 8 }}>
            {selectedTask?.result && (
              <>
                <Tooltip title="导出数据">
                  <IconButton
                    onClick={handleExportMenuOpen}
                    aria-controls={exportMenuOpen ? 'export-menu' : undefined}
                    aria-haspopup="true"
                    aria-expanded={exportMenuOpen ? 'true' : undefined}
                  >
                    <DownloadIcon />
                  </IconButton>
                </Tooltip>
                <Menu
                  id="export-menu"
                  anchorEl={exportMenuAnchorEl}
                  open={exportMenuOpen}
                  onClose={handleExportMenuClose}
                  MenuListProps={{
                    'aria-labelledby': 'export-button',
                  }}
                >
                  <MenuItem onClick={() => {
                    handleExportData('json');
                    handleExportMenuClose();
                  }}>
                    导出为JSON
                  </MenuItem>
                  <MenuItem onClick={() => {
                    handleExportData('csv');
                    handleExportMenuClose();
                  }}>
                    导出为CSV
                  </MenuItem>
                  <MenuItem onClick={() => {
                    handleExportData('excel');
                    handleExportMenuClose();
                  }}>
                    导出为Excel
                  </MenuItem>
                  <MenuItem onClick={() => {
                    handleExportData('pdf');
                    handleExportMenuClose();
                  }}>
                    导出为PDF
                  </MenuItem>
                  <MenuItem onClick={() => {
                    handleExportData('txt');
                    handleExportMenuClose();
                  }}>
                    导出为TXT
                  </MenuItem>
                  <Divider />
                  <MenuItem onClick={handleBatchExport}>
                    批量导出（所有格式）
                  </MenuItem>
                </Menu>
              </>
            )}
          </Box>
        </DialogTitle>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="任务详情标签页">
            <Tab label="详情" id="task-tab-0" aria-controls="task-tabpanel-0" />
            {selectedTask?.result && (
              <Tab label="可视化" id="task-tab-1" aria-controls="task-tabpanel-1" />
            )}
          </Tabs>
        </Box>
        <DialogContent dividers>
          {selectedTask && (
            <>
              <TabPanel value={tabValue} index={0}>
                <Box>
                  {selectedTask.description && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {selectedTask.description}
                    </Typography>
                  )}
                  <Box sx={{ mb: 2 }}>
                    <Chip
                      label={getStatusText(selectedTask.status)}
                      color={getStatusColor(selectedTask.status) as any}
                      sx={{ mr: 1 }}
                    />
                    {selectedTask.is_recurring && (
                      <Chip label="周期性任务" variant="outlined" />
                    )}
                  </Box>
                  <Typography variant="subtitle2">任务类型</Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>{selectedTask.task_type}</Typography>

                  <Typography variant="subtitle2">任务参数</Typography>
                  <Paper sx={{ p: 1, mb: 1, bgcolor: 'grey.100' }}>
                    <pre style={{ margin: 0, overflow: 'auto' }}>
                      {JSON.stringify(selectedTask.parameters || {}, null, 2)}
                    </pre>
                  </Paper>

                  {selectedTask.result && (
                    <>
                      <Typography variant="subtitle2">处理结果</Typography>
                      <Paper sx={{ p: 1, mb: 1, bgcolor: 'grey.100' }}>
                        <pre style={{ margin: 0, overflow: 'auto', maxHeight: '300px' }}>
                          {JSON.stringify(selectedTask.result, null, 2)}
                        </pre>
                      </Paper>
                    </>
                  )}

                  {selectedTask.error_message && (
                    <>
                      <Typography variant="subtitle2" color="error">错误信息</Typography>
                      <Paper sx={{ p: 1, mb: 1, bgcolor: 'error.light' }}>
                        <Typography variant="body2" color="error.contrastText">
                          {selectedTask.error_message}
                        </Typography>
                      </Paper>
                    </>
                  )}

                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2">创建时间</Typography>
                    <Typography variant="body2">
                      {new Date(selectedTask.created_at).toLocaleString()}
                    </Typography>

                    {selectedTask.started_at && (
                      <>
                        <Typography variant="subtitle2">开始时间</Typography>
                        <Typography variant="body2">
                          {new Date(selectedTask.started_at).toLocaleString()}
                        </Typography>
                      </>
                    )}

                    {selectedTask.completed_at && (
                      <>
                        <Typography variant="subtitle2">完成时间</Typography>
                        <Typography variant="body2">
                          {new Date(selectedTask.completed_at).toLocaleString()}
                        </Typography>
                      </>
                    )}
                  </Box>
                </Box>
              </TabPanel>

              {selectedTask.result && (
                <TabPanel value={tabValue} index={1}>
                  <Box>
                    <Typography variant="subtitle1" gutterBottom>
                      结果可视化
                    </Typography>
                    <DataVisualization
                      data={selectedTask.result.sample_data || selectedTask.result}
                      title={selectedTask.name}
                    />
                  </Box>
                </TabPanel>
              )}
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>关闭</Button>
        </DialogActions>
      </Dialog>

      {/* 确认删除对话框 */}
      <Dialog
        open={confirmDeleteOpen}
        onClose={() => setConfirmDeleteOpen(false)}
      >
        <DialogTitle>确认删除</DialogTitle>
        <DialogContent>
          <Typography>
            确定要删除任务 "{selectedTask?.name}" 吗？此操作不可撤销。
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDeleteOpen(false)}>取消</Button>
          <Button onClick={handleDeleteTask} color="error">删除</Button>
        </DialogActions>
      </Dialog>

      {/* 任务调度对话框 */}
      {selectedTask && (
        <ScheduleTaskDialog
          open={scheduleDialogOpen}
          onClose={() => setScheduleDialogOpen(false)}
          task={selectedTask}
          onScheduled={() => {
            setScheduleDialogOpen(false);
            fetchTasks();
          }}
        />
      )}
    </Box>
  );
};

export default TaskList;
