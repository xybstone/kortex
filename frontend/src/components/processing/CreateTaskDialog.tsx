import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Switch,
  FormControlLabel,
  Box,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';
import { DataSource } from '@/services/datasetApi';
import processingApi, { CreateProcessingTaskRequest } from '@/services/processingApi';

interface CreateTaskDialogProps {
  open: boolean;
  onClose: () => void;
  dataSource: DataSource;
  onTaskCreated: () => void;
}

const getTaskTypeOptions = (sourceType: string) => {
  switch (sourceType) {
    case 'database':
      return [
        { value: 'database_clean', label: '数据清洗' },
        { value: 'database_analyze', label: '数据分析' },
        { value: 'database_transform', label: '数据转换' }
      ];
    case 'file':
      return [
        { value: 'file_embed', label: '文件嵌入' },
        { value: 'file_extract', label: '内容提取' },
        { value: 'file_convert', label: '格式转换' }
      ];
    case 'url':
      return [
        { value: 'url_crawl', label: '网页爬取' },
        { value: 'url_extract', label: '内容提取' },
        { value: 'url_monitor', label: '变更监控' }
      ];
    default:
      return [];
  }
};

const getDefaultParameters = (taskType: string) => {
  switch (taskType) {
    case 'database_clean':
      return {
        clean_rules: [
          { field: 'example_field', rule: 'remove_duplicates' }
        ]
      };
    case 'database_analyze':
      return {
        analysis_type: 'statistical'
      };
    case 'database_transform':
      return {
        transform_rules: [
          { field: 'example_field', transformation: 'to_uppercase' }
        ]
      };
    case 'file_embed':
      return {
        embed_model: 'default'
      };
    case 'file_extract':
      return {
        extract_type: 'text'
      };
    case 'file_convert':
      return {
        target_format: 'pdf'
      };
    case 'url_crawl':
      return {
        crawl_depth: 2
      };
    case 'url_extract':
      return {
        extract_rules: [
          { selector: '.content', attribute: 'text' }
        ]
      };
    case 'url_monitor':
      return {
        monitor_interval: 3600
      };
    default:
      return {};
  }
};

const CreateTaskDialog: React.FC<CreateTaskDialogProps> = ({
  open,
  onClose,
  dataSource,
  onTaskCreated
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [taskType, setTaskType] = useState('');
  const [priority, setPriority] = useState(0);
  const [isRecurring, setIsRecurring] = useState(false);
  const [parameters, setParameters] = useState('{}');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const taskTypeOptions = getTaskTypeOptions(dataSource.type);

  const handleTaskTypeChange = (event: any) => {
    const newTaskType = event.target.value;
    setTaskType(newTaskType);
    setParameters(JSON.stringify(getDefaultParameters(newTaskType), null, 2));
  };

  const handleSubmit = async () => {
    if (!name || !taskType) {
      setError('请填写必填字段');
      return;
    }

    let parsedParameters;
    try {
      parsedParameters = JSON.parse(parameters);
    } catch (err) {
      setError('参数格式不正确，请检查JSON格式');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const taskData: CreateProcessingTaskRequest = {
        name,
        description: description || undefined,
        task_type: taskType,
        data_source_id: dataSource.id,
        priority,
        parameters: parsedParameters,
        is_recurring: isRecurring
      };

      await processingApi.createTask(taskData);
      onTaskCreated();
      handleClose();
    } catch (err: any) {
      console.error('创建任务失败:', err);
      setError(err.response?.data?.detail || '创建任务失败，请稍后再试');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setName('');
    setDescription('');
    setTaskType('');
    setPriority(0);
    setIsRecurring(false);
    setParameters('{}');
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>创建处理任务</DialogTitle>
      <DialogContent dividers>
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            数据源: {dataSource.name} ({dataSource.type})
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <TextField
          label="任务名称"
          value={name}
          onChange={(e) => setName(e.target.value)}
          fullWidth
          required
          margin="normal"
        />

        <TextField
          label="任务描述"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          fullWidth
          multiline
          rows={2}
          margin="normal"
        />

        <FormControl fullWidth margin="normal" required>
          <InputLabel>任务类型</InputLabel>
          <Select
            value={taskType}
            onChange={handleTaskTypeChange}
            label="任务类型"
          >
            {taskTypeOptions.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
          <FormHelperText>
            选择适合该数据源的处理任务类型
          </FormHelperText>
        </FormControl>

        <TextField
          label="优先级"
          type="number"
          value={priority}
          onChange={(e) => setPriority(parseInt(e.target.value))}
          fullWidth
          margin="normal"
          helperText="数字越大优先级越高"
        />

        <FormControlLabel
          control={
            <Switch
              checked={isRecurring}
              onChange={(e) => setIsRecurring(e.target.checked)}
            />
          }
          label="周期性任务"
          sx={{ my: 1 }}
        />

        <TextField
          label="任务参数 (JSON格式)"
          value={parameters}
          onChange={(e) => setParameters(e.target.value)}
          fullWidth
          multiline
          rows={8}
          margin="normal"
          error={Boolean(parameters && parameters.trim() !== '' && !isValidJson(parameters))}
          helperText={
            parameters && parameters.trim() !== '' && !isValidJson(parameters)
              ? 'JSON格式不正确'
              : '任务参数，JSON格式'
          }
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          取消
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          创建
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// 辅助函数：验证JSON格式
function isValidJson(str: string) {
  try {
    JSON.parse(str);
    return true;
  } catch (e) {
    return false;
  }
}

export default CreateTaskDialog;
