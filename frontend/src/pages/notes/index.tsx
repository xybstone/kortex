import { useState } from 'react';
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
  InputAdornment
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import Head from 'next/head';
import { useRouter } from 'next/router';

// 模拟笔记数据
const mockNotes = [
  { id: 1, title: '项目计划', content: '# 项目计划\n\n这是一个项目计划文档...', updatedAt: '2023-05-10' },
  { id: 2, title: '会议记录', content: '# 会议记录\n\n今天的会议讨论了以下内容...', updatedAt: '2023-05-09' },
  { id: 3, title: '学习笔记', content: '# 学习笔记\n\n今天学习了以下内容...', updatedAt: '2023-05-08' },
  { id: 4, title: '想法收集', content: '# 想法收集\n\n最近有以下想法...', updatedAt: '2023-05-07' },
];

export default function Notes() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  
  // 根据搜索词过滤笔记
  const filteredNotes = mockNotes.filter(note => 
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
                    更新于 {note.updatedAt}
                  </Typography>
                </CardActions>
              </Card>
            </Grid>
          ))}
          
          {filteredNotes.length === 0 && (
            <Grid item xs={12}>
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary">
                  没有找到匹配的笔记
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
      </Container>
    </>
  );
}
