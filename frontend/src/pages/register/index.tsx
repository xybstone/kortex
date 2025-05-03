import { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Link as MuiLink,
  Alert,
  CircularProgress
} from '@mui/material';
import Link from 'next/link';
import { useRouter } from 'next/router';
import Head from 'next/head';
import axios from 'axios';

export default function Register() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // 验证密码
    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    setLoading(true);

    try {
      await axios.post('http://localhost:8000/api/auth/register', {
        email,
        password,
        full_name: fullName
      });

      // 注册成功后自动登录
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const loginResponse = await axios.post('http://localhost:8000/api/auth/login', params);

      // 保存token到localStorage
      localStorage.setItem('token', loginResponse.data.access_token);

      // 重定向到首页
      router.push('/notes');
    } catch (err: any) {
      console.error('注册失败:', err);
      setError(err.response?.data?.detail || '注册失败，请稍后再试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>注册 | Kortex</title>
        <meta name="description" content="注册Kortex账号" />
      </Head>
      <Container component="main" maxWidth="xs">
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Typography component="h1" variant="h4" sx={{ mb: 4 }}>
            Kortex
          </Typography>
          <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
            <Typography component="h2" variant="h5" align="center" sx={{ mb: 3 }}>
              注册
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="邮箱地址"
                name="email"
                autoComplete="email"
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                id="fullName"
                label="姓名"
                name="fullName"
                autoComplete="name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="密码"
                type="password"
                id="password"
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="confirmPassword"
                label="确认密码"
                type="password"
                id="confirmPassword"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : '注册'}
              </Button>
              <Box sx={{ textAlign: 'center' }}>
                <Link href="/login" passHref>
                  <MuiLink variant="body2">
                    {"已有账号？立即登录"}
                  </MuiLink>
                </Link>
              </Box>
            </Box>
          </Paper>
        </Box>
      </Container>
    </>
  );
}
