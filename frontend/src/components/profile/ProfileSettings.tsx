import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Switch,
  FormControlLabel,
  Divider,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert
} from '@mui/material';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';

interface ProfileSettingsProps {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

export default function ProfileSettings({ onSuccess, onError }: ProfileSettingsProps) {
  const { user } = useAuth();
  const [darkMode, setDarkMode] = useState(false);
  const [language, setLanguage] = useState('zh-CN');
  const [autoSave, setAutoSave] = useState(true);
  const [error, setError] = useState('');

  // 处理设置保存
  const handleSaveSettings = async () => {
    setError('');

    try {
      // 这里应该调用API保存设置
      // 目前模拟成功
      onSuccess('设置已保存');
    } catch (err: any) {
      console.error('保存设置失败:', err);
      setError(err.response?.data?.detail || '保存设置失败，请稍后再试');
      onError(err.response?.data?.detail || '保存设置失败，请稍后再试');
    }
  };

  return (
    <Grid container spacing={4}>
      {error && (
        <Grid item xs={12}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        </Grid>
      )}

      {/* 界面设置 */}
      <Grid item xs={12} md={6}>
        <Paper elevation={3} sx={{ p: { xs: 3, md: 4 }, borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom>
            界面设置
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <FormControlLabel
            control={
              <Switch
                checked={darkMode}
                onChange={(e) => setDarkMode(e.target.checked)}
              />
            }
            label="深色模式"
            sx={{ mb: 3, display: 'block' }}
          />

          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel id="language-select-label">语言</InputLabel>
            <Select
              labelId="language-select-label"
              id="language-select"
              value={language}
              label="语言"
              onChange={(e) => setLanguage(e.target.value)}
            >
              <MenuItem value="zh-CN">简体中文</MenuItem>
              <MenuItem value="en-US">English (US)</MenuItem>
            </Select>
          </FormControl>
        </Paper>
      </Grid>

      {/* 编辑器设置 */}
      <Grid item xs={12} md={6}>
        <Paper elevation={3} sx={{ p: { xs: 3, md: 4 }, borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom>
            编辑器设置
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <FormControlLabel
            control={
              <Switch
                checked={autoSave}
                onChange={(e) => setAutoSave(e.target.checked)}
              />
            }
            label="自动保存"
            sx={{ mb: 3, display: 'block' }}
          />
        </Paper>
      </Grid>

      {/* 数据设置 */}
      <Grid item xs={12}>
        <Paper elevation={3} sx={{ p: { xs: 3, md: 4 }, borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom>
            数据设置
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="body1" gutterBottom fontWeight="medium">
                  数据导出
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  导出您的所有笔记和数据库
                </Typography>
                <Button variant="outlined" size="large">导出数据</Button>
              </Box>
            </Grid>

            <Grid item xs={12} md={6}>
              <Box>
                <Typography variant="body1" gutterBottom fontWeight="medium">
                  清除数据
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  清除所有本地缓存数据
                </Typography>
                <Button variant="outlined" color="error" size="large">
                  清除缓存
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Grid>

      <Grid item xs={12}>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
          <Button
            variant="contained"
            onClick={handleSaveSettings}
            size="large"
          >
            保存设置
          </Button>
        </Box>
      </Grid>
    </Grid>
  );
}
