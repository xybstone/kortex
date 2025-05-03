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
  IconButton,
  InputAdornment,
  CircularProgress,
  Alert
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { noteApi } from '@/services/api';

// 笔记类型定义
interface Note {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  user_id: number;
}

export default function Notes() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 获取笔记列表
  useEffect(() => {
    const fetchNotes = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await noteApi.getNotes();
        setNotes(data);
      } catch (err) {
        console.error('获取笔记列表失败:', err);
        setError('获取笔记列表失败，请稍后重试');
        // 如果API调用失败，使用空数组
        setNotes([]);
      } finally {
        setLoading(false);
      }
    };

    fetchNotes();
  }, []);

  // 根据搜索词过滤笔记
  const filteredNotes = notes.filter(note =>
    note.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    note.content.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      <Head>
        <title>笔记 | Kortex</title>
        <meta name="description" content="Kortex笔记列表" />
      </Head>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            我的笔记
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => router.push('/notes/new')}
          >
            新建笔记
          </Button>
        </Box>

        <TextField
          fullWidth
          variant="outlined"
          placeholder="搜索笔记..."
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

        {/* 错误提示 */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* 加载状态 */}
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            {filteredNotes.map((note) => (
              <Grid item xs={12} sm={6} md={4} key={note.id}>
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
                  onClick={() => router.push(`/notes/${note.id}`)}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Typography gutterBottom variant="h5" component="h2">
                      {note.title}
                    </Typography>
                    <Typography color="text.secondary">
                      {note.content.substring(0, 100)}...
                    </Typography>
                  </CardContent>
                  <CardActions sx={{ justifyContent: 'flex-end' }}>
                    <Typography variant="caption" color="text.secondary">
                      更新于 {note.updated_at ? new Date(note.updated_at).toLocaleDateString() : new Date(note.created_at).toLocaleDateString()}
                    </Typography>
                  </CardActions>
                </Card>
              </Grid>
            ))}

            {!loading && filteredNotes.length === 0 && (
              <Grid item xs={12}>
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="h6" color="text.secondary">
                    {searchTerm ? '没有找到匹配的笔记' : '还没有创建任何笔记'}
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => router.push('/notes/new')}
                    sx={{ mt: 2 }}
                  >
                    新建笔记
                  </Button>
                </Box>
              </Grid>
            )}
          </Grid>
        )}
      </Container>
    </>
  );
}
