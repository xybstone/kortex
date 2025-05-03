import { useState } from 'react';
import { Container, Typography, Box, Button, Grid } from '@mui/material';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';

export default function Home() {
  const router = useRouter();

  return (
    <>
      <Head>
        <title>Kortex - 在线笔记工具</title>
        <meta name="description" content="支持Markdown编辑、数据库管理和大模型集成的在线笔记工具" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <Box
          sx={{
            bgcolor: 'background.paper',
            pt: 8,
            pb: 6,
          }}
        >
          <Container maxWidth="md">
            <Typography
              component="h1"
              variant="h2"
              align="center"
              color="text.primary"
              gutterBottom
            >
              Kortex
            </Typography>
            <Typography variant="h5" align="center" color="text.secondary" paragraph>
              一个在线笔记工具，支持Markdown编辑、数据库管理和大模型集成
            </Typography>
            <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center', gap: 2 }}>
              <Button 
                variant="contained" 
                color="primary" 
                size="large"
                onClick={() => router.push('/notes')}
              >
                开始使用
              </Button>
              <Button 
                variant="outlined" 
                color="primary" 
                size="large"
                onClick={() => router.push('/about')}
              >
                了解更多
              </Button>
            </Box>
          </Container>
        </Box>
        
        <Container sx={{ py: 8 }} maxWidth="md">
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Markdown笔记编辑器
                </Typography>
                <Typography color="text.secondary">
                  类似于Obsidian的笔记编辑体验，支持Markdown格式
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  数据库管理
                </Typography>
                <Typography color="text.secondary">
                  支持创建、导入和管理数据库，轻松处理结构化数据
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center', p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  大模型集成
                </Typography>
                <Typography color="text.secondary">
                  利用AI分析数据并生成笔记内容，提高工作效率
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </main>
      <footer>
        <Box sx={{ bgcolor: 'background.paper', p: 6 }} component="footer">
          <Typography variant="body2" color="text.secondary" align="center">
            {'© '}
            {new Date().getFullYear()}
            {' Kortex. All rights reserved.'}
          </Typography>
        </Box>
      </footer>
    </>
  );
}
