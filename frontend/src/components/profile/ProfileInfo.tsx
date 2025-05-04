import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Avatar,
  Divider,
  Alert,
  CircularProgress
} from '@mui/material';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';

interface ProfileInfoProps {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

export default function ProfileInfo({ onSuccess, onError }: ProfileInfoProps) {
  const { user } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 初始化表单数据
  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email || '');
    }
  }, [user]);

  // 处理个人信息更新
  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.put('http://localhost:8000/api/users/me', {
        full_name: fullName,
      });

      onSuccess('个人信息更新成功');
    } catch (err: any) {
      console.error('更新失败:', err);
      setError(err.response?.data?.detail || '更新失败，请稍后再试');
      onError(err.response?.data?.detail || '更新失败，请稍后再试');
    } finally {
      setLoading(false);
    }
  };

  // 处理密码更新
  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // 验证新密码
    if (newPassword !== confirmPassword) {
      setError('两次输入的新密码不一致');
      onError('两次输入的新密码不一致');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.put('http://localhost:8000/api/users/password', {
        current_password: currentPassword,
        new_password: newPassword,
      });

      onSuccess('密码更新成功');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      console.error('密码更新失败:', err);
      setError(err.response?.data?.detail || '密码更新失败，请检查当前密码是否正确');
      onError(err.response?.data?.detail || '密码更新失败，请检查当前密码是否正确');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Grid container spacing={4}>
      {/* 个人信息卡片 */}
      <Grid item xs={12} md={6}>
        <Paper elevation={3} sx={{ p: { xs: 3, md: 4 }, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Avatar
              sx={{ width: 64, height: 64, bgcolor: 'primary.main', mr: 2 }}
            >
              {user?.full_name ? user.full_name[0].toUpperCase() : user?.email[0].toUpperCase()}
            </Avatar>
            <Box>
              <Typography variant="h6">{user?.full_name || '用户'}</Typography>
              <Typography variant="body2" color="text.secondary">
                {user?.email}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ mb: 3 }} />

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleProfileUpdate}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="邮箱地址"
              name="email"
              value={email}
              disabled
              sx={{ mb: 3 }}
            />
            <TextField
              margin="normal"
              fullWidth
              id="fullName"
              label="全名"
              name="fullName"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              sx={{ mb: 3 }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                type="submit"
                variant="contained"
                disabled={loading}
                size="large"
              >
                {loading ? <CircularProgress size={24} /> : '更新个人信息'}
              </Button>
            </Box>
          </Box>
        </Paper>
      </Grid>

      {/* 修改密码卡片 */}
      <Grid item xs={12} md={6}>
        <Paper elevation={3} sx={{ p: { xs: 3, md: 4 }, borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom>
            修改密码
          </Typography>

          <Divider sx={{ mb: 3 }} />

          <Box component="form" onSubmit={handlePasswordUpdate}>
            <TextField
              margin="normal"
              required
              fullWidth
              name="currentPassword"
              label="当前密码"
              type="password"
              id="currentPassword"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              sx={{ mb: 3 }}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="newPassword"
              label="新密码"
              type="password"
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              sx={{ mb: 3 }}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="confirmPassword"
              label="确认新密码"
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              sx={{ mb: 3 }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                type="submit"
                variant="contained"
                disabled={loading}
                size="large"
              >
                {loading ? <CircularProgress size={24} /> : '更新密码'}
              </Button>
            </Box>
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
}
