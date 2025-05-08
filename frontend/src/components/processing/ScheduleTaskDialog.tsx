import React, { useState, useEffect } from 'react';
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
  Box,
  Typography,
  Alert,
  CircularProgress,
  Grid,
  Divider,
  Switch,
  FormControlLabel
} from '@mui/material';
import { SelectChangeEvent } from '@mui/material/Select';
import AlarmIcon from '@mui/icons-material/Alarm';
import processingApi, { ProcessingTask, ScheduleInfo } from '@/services/processingApi';

interface ScheduleTaskDialogProps {
  open: boolean;
  onClose: () => void;
  task: ProcessingTask;
  onScheduled: () => void;
}

const ScheduleTaskDialog: React.FC<ScheduleTaskDialogProps> = ({
  open,
  onClose,
  task,
  onScheduled
}) => {
  const [scheduleType, setScheduleType] = useState<string>('daily');
  const [scheduleValue, setScheduleValue] = useState<string>('1');
  const [maxRuns, setMaxRuns] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [nextRunTime, setNextRunTime] = useState<string | null>(null);

  // 初始化表单
  useEffect(() => {
    if (open && task) {
      // 如果任务已经有调度信息，使用它
      if (task.schedule_type) {
        setScheduleType(task.schedule_type);
      } else {
        setScheduleType('daily');
      }

      if (task.schedule_value) {
        setScheduleValue(task.schedule_value);
      } else {
        setScheduleValue('1');
      }

      if (task.max_runs) {
        setMaxRuns(task.max_runs.toString());
      } else {
        setMaxRuns('');
      }

      // 显示下次运行时间
      if (task.next_run_time) {
        setNextRunTime(new Date(task.next_run_time).toLocaleString());
      } else {
        setNextRunTime(null);
      }
    }
  }, [open, task]);

  // 处理调度类型变更
  const handleScheduleTypeChange = (event: SelectChangeEvent) => {
    setScheduleType(event.target.value);
    
    // 根据调度类型设置默认值
    if (event.target.value === 'daily') {
      setScheduleValue('1');
    } else if (event.target.value === 'weekly') {
      setScheduleValue('1');
    } else if (event.target.value === 'monthly') {
      setScheduleValue('1');
    } else if (event.target.value === 'cron') {
      setScheduleValue('0 0 * * *'); // 每天午夜
    } else {
      setScheduleValue('');
    }
  };

  // 处理调度值变更
  const handleScheduleValueChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setScheduleValue(event.target.value);
  };

  // 处理最大运行次数变更
  const handleMaxRunsChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // 只允许输入数字
    const value = event.target.value;
    if (value === '' || /^\d+$/.test(value)) {
      setMaxRuns(value);
    }
  };

  // 提交表单
  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);

      // 验证表单
      if (!scheduleType) {
        setError('请选择调度类型');
        setLoading(false);
        return;
      }

      if (!scheduleValue) {
        setError('请输入调度值');
        setLoading(false);
        return;
      }

      // 创建调度信息
      const scheduleInfo: ScheduleInfo = {
        schedule_type: scheduleType,
        schedule_value: scheduleValue,
        max_runs: maxRuns ? parseInt(maxRuns) : undefined
      };

      // 调用API设置任务调度
      await processingApi.scheduleTask(task.id, scheduleInfo);

      // 调用回调函数
      onScheduled();

      // 关闭对话框
      onClose();
    } catch (err: any) {
      console.error('设置任务调度失败:', err);
      setError(err.response?.data?.detail || '设置任务调度失败');
    } finally {
      setLoading(false);
    }
  };

  // 取消任务调度
  const handleCancelSchedule = async () => {
    try {
      setLoading(true);
      setError(null);

      // 调用API取消任务调度
      await processingApi.cancelTaskSchedule(task.id);

      // 调用回调函数
      onScheduled();

      // 关闭对话框
      onClose();
    } catch (err: any) {
      console.error('取消任务调度失败:', err);
      setError(err.response?.data?.detail || '取消任务调度失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取调度类型说明
  const getScheduleTypeHelperText = () => {
    switch (scheduleType) {
      case 'once':
        return '任务将只执行一次';
      case 'daily':
        return '任务将每隔指定天数执行一次';
      case 'weekly':
        return '任务将每隔指定周数执行一次';
      case 'monthly':
        return '任务将每隔指定月数执行一次';
      case 'cron':
        return '使用cron表达式定义复杂的调度规则';
      default:
        return '';
    }
  };

  // 获取调度值说明
  const getScheduleValueHelperText = () => {
    switch (scheduleType) {
      case 'daily':
        return '输入天数，例如：1表示每天，2表示每两天';
      case 'weekly':
        return '输入周数，例如：1表示每周，2表示每两周';
      case 'monthly':
        return '输入月数，例如：1表示每月，2表示每两月';
      case 'cron':
        return '输入cron表达式，例如：0 9 * * 1-5表示工作日上午9点';
      default:
        return '';
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center">
          <AlarmIcon sx={{ mr: 1 }} />
          设置任务调度
        </Box>
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Typography variant="subtitle1" gutterBottom>
          {task.name}
        </Typography>

        {nextRunTime && (
          <Alert severity="info" sx={{ mb: 2 }}>
            下次运行时间: {nextRunTime}
          </Alert>
        )}

        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>调度类型</InputLabel>
              <Select
                value={scheduleType}
                label="调度类型"
                onChange={handleScheduleTypeChange}
                disabled={loading}
              >
                <MenuItem value="once">一次性</MenuItem>
                <MenuItem value="daily">每天</MenuItem>
                <MenuItem value="weekly">每周</MenuItem>
                <MenuItem value="monthly">每月</MenuItem>
                <MenuItem value="cron">Cron表达式</MenuItem>
              </Select>
              <FormHelperText>{getScheduleTypeHelperText()}</FormHelperText>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              label="调度值"
              value={scheduleValue}
              onChange={handleScheduleValueChange}
              fullWidth
              disabled={loading}
              helperText={getScheduleValueHelperText()}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              label="最大运行次数"
              value={maxRuns}
              onChange={handleMaxRunsChange}
              fullWidth
              disabled={loading}
              helperText="留空表示无限制"
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        {task.is_recurring && (
          <Button
            onClick={handleCancelSchedule}
            color="error"
            disabled={loading}
            sx={{ mr: 'auto' }}
          >
            取消调度
          </Button>
        )}
        <Button onClick={onClose} disabled={loading}>
          取消
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : null}
        >
          保存
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ScheduleTaskDialog;
