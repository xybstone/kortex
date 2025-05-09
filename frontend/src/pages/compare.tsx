import { useState, useRef } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  Grid,
  Divider,
  TextField,
  CircularProgress,
  Alert,
  Snackbar
} from '@mui/material';
import Head from 'next/head';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import MarkdownEditor from '@/components/MarkdownEditor';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import SaveIcon from '@mui/icons-material/Save';
import { noteApi } from '@/services/api';

// PDF导入组件
const PdfImporter = ({ onMarkdownGenerated }: { onMarkdownGenerated: (markdown: string) => void }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const selectedFile = files[0];
      // 检查文件类型
      if (selectedFile.type !== 'application/pdf') {
        setError('只支持PDF文件');
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('请选择一个PDF文件');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // 根据环境选择API URL
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/pdf/convert-to-markdown`, {
        method: 'POST',
        body: formData,
        headers: {
          // 不要设置Content-Type，让浏览器自动设置
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '上传失败');
      }

      const data = await response.json();
      onMarkdownGenerated(data.markdown);
    } catch (err) {
      console.error('上传PDF失败:', err);
      setError(err instanceof Error ? err.message : '上传PDF失败');
    } finally {
      setLoading(false);
    }
  };

  const handleButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        导入PDF
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Button
          variant="contained"
          startIcon={<UploadFileIcon />}
          onClick={handleButtonClick}
          disabled={loading}
        >
          选择PDF文件
        </Button>
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          style={{ display: 'none' }}
          ref={fileInputRef}
        />
        <Typography variant="body2" sx={{ ml: 2 }}>
          {file ? file.name : '未选择文件'}
        </Typography>
      </Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      <Button
        variant="contained"
        color="primary"
        startIcon={loading ? <CircularProgress size={24} /> : <CompareArrowsIcon />}
        onClick={handleUpload}
        disabled={!file || loading}
      >
        {loading ? '处理中...' : '转换为Markdown'}
      </Button>
    </Paper>
  );
};

export default function ComparePage() {
  const router = useRouter();
  const [leftContent, setLeftContent] = useState('');
  const [rightContent, setRightContent] = useState('');
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');

  const handleSaveAsNote = async () => {
    if (!title.trim()) {
      setSnackbarMessage('请输入笔记标题');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
      return;
    }

    if (!rightContent.trim()) {
      setSnackbarMessage('笔记内容不能为空');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
      return;
    }

    try {
      setLoading(true);
      const noteData = {
        title,
        content: rightContent,
      };

      const createdNote = await noteApi.createNote(noteData);
      setSnackbarMessage('笔记创建成功');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);

      // 创建成功后跳转到笔记详情页
      router.push(`/notes/${createdNote.id}`);
    } catch (error) {
      console.error('创建笔记失败:', error);
      setSnackbarMessage('创建笔记失败，请稍后重试');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  return (
    <Layout>
      <Head>
        <title>比较 | Kortex</title>
      </Head>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            比较与编辑
          </Typography>
          <Box>
            <TextField
              label="笔记标题"
              variant="outlined"
              size="small"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              sx={{ mr: 2, width: 300 }}
            />
            <Button
              variant="contained"
              color="primary"
              startIcon={loading ? <CircularProgress size={24} /> : <SaveIcon />}
              onClick={handleSaveAsNote}
              disabled={loading}
            >
              保存为笔记
            </Button>
          </Box>
        </Box>

        <PdfImporter onMarkdownGenerated={(markdown) => {
          setLeftContent(markdown);
          setRightContent(markdown); // 同时设置右侧编辑区域的内容
        }} />

        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Paper elevation={1} sx={{ height: 'calc(100vh - 300px)', p: 2 }}>
              <Typography variant="h6" gutterBottom>
                原始内容
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <MarkdownEditor
                initialValue={leftContent}
                readOnly={true}
                defaultEditMode={false}
              />
            </Paper>
          </Grid>
          <Grid item xs={6}>
            <Paper elevation={1} sx={{ height: 'calc(100vh - 300px)', p: 2 }}>
              <Typography variant="h6" gutterBottom>
                编辑内容
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <MarkdownEditor
                initialValue={rightContent}
                onChange={setRightContent}
                readOnly={false}
                defaultEditMode={true}
              />
            </Paper>
          </Grid>
        </Grid>

        <Snackbar
          open={snackbarOpen}
          autoHideDuration={6000}
          onClose={handleSnackbarClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert onClose={handleSnackbarClose} severity={snackbarSeverity}>
            {snackbarMessage}
          </Alert>
        </Snackbar>
      </Container>
    </Layout>
  );
}
