import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  TextField,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import SummarizeIcon from '@mui/icons-material/Summarize';
import LabelIcon from '@mui/icons-material/Label';
import Head from 'next/head';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function LLM() {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [operation, setOperation] = useState('analyze');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDatabase, setSelectedDatabase] = useState('');
  const [selectedModel, setSelectedModel] = useState('1'); // 默认选择第一个模型
  const [models, setModels] = useState<Array<{id: number, name: string, provider: string, is_active: boolean}>>([]);
  const [loadingModels, setLoadingModels] = useState(false);

  // 模拟数据库列表
  const mockDatabases = [
    { id: '1', name: '项目数据' },
    { id: '2', name: '客户信息' },
    { id: '3', name: '产品目录' },
  ];

  // 获取模型列表
  useEffect(() => {
    const fetchModels = async () => {
      setLoadingModels(true);
      try {
        // 使用新的接口获取模型列表
        const response = await fetch('/api/llm/models');
        if (!response.ok) {
          throw new Error('获取模型列表失败');
        }
        const models = await response.json();
        setModels(models);
        if (models && models.length > 0) {
          setSelectedModel(models[0].id.toString());
        }
      } catch (error) {
        console.error('获取模型列表失败:', error);
        // 如果获取失败，使用默认模型列表
        const defaultModels = [
          {id: 1, name: "gpt-4", provider: "OpenAI", is_active: true},
          {id: 2, name: "gpt-3.5-turbo", provider: "OpenAI", is_active: true},
          {id: 3, name: "claude-3-opus", provider: "Anthropic", is_active: true},
          {id: 4, name: "deepseek-chat", provider: "DeepSeek", is_active: true}
        ];
        setModels(defaultModels);
        setSelectedModel("1");
      } finally {
        setLoadingModels(false);
      }
    };

    fetchModels();
  }, []);

  const handleSubmit = async () => {
    if (!inputText) return;

    setIsLoading(true);

    try {
      console.log(`开始提交${operation}请求，模型ID: ${selectedModel}`);
      let response;

      switch (operation) {
        case 'analyze':
          response = await fetch('/api/llm/analyze', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              content: inputText,
              model_id: parseInt(selectedModel),
              options: {}
            }),
          });
          break;
        case 'generate':
          response = await fetch('/api/llm/generate', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              content: inputText,
              model_id: parseInt(selectedModel),
              options: {}
            }),
          });
          break;
        case 'summarize':
          response = await fetch('/api/llm/summarize', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              content: inputText,
              model_id: parseInt(selectedModel),
              options: {}
            }),
          });
          break;
        case 'extract-keywords':
          response = await fetch('/api/llm/extract-keywords', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              content: inputText,
              model_id: parseInt(selectedModel),
              options: {}
            }),
          });
          break;
        case 'analyze-database':
          response = await fetch('/api/llm/analyze-database', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              database_id: parseInt(selectedDatabase),
              model_id: parseInt(selectedModel),
              prompt: inputText
            }),
          });
          break;
        default:
          throw new Error('未知操作类型');
      }

      // 先克隆响应，这样我们可以多次读取
      const responseClone = response.clone();
      console.log(`收到响应: 状态码=${response.status}, 状态文本=${response.statusText}`);
      // 打印一些重要的响应头
      console.log(`响应头: Content-Type=${response.headers.get('content-type')}, Content-Length=${response.headers.get('content-length')}`);

      if (!response.ok) {
        try {
          // 尝试解析错误响应为JSON
          const errorData = await response.json();
          throw new Error(errorData.detail || `请求失败: ${response.status} ${response.statusText}`);
        } catch (jsonError) {
          // 如果无法解析为JSON，则使用响应状态文本
          try {
            const errorText = await responseClone.text();
            console.error('服务器返回非JSON响应:', errorText);
          } catch (textError) {
            console.error('无法读取错误响应内容');
          }
          throw new Error(`请求失败: ${response.status} ${response.statusText}`);
        }
      }

      // 尝试解析响应为JSON
      let data;
      try {
        data = await responseClone.json();
      } catch (jsonError) {
        console.error('解析响应JSON失败:', jsonError);
        throw new Error('服务器返回了无效的JSON响应');
      }
      setOutputText(data.result);
    } catch (error: any) {
      console.error('API调用失败:', error);
      setOutputText(`## 错误\n\n请求处理失败: ${error.message || '未知错误'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const operationCards = [
    {
      id: 'analyze',
      title: '文本分析',
      description: '分析文本内容，提取关键观点和情感',
      icon: <AnalyticsIcon fontSize="large" />
    },
    {
      id: 'generate',
      title: '文本生成',
      description: '根据提示生成结构化内容',
      icon: <SendIcon fontSize="large" />
    },
    {
      id: 'summarize',
      title: '生成摘要',
      description: '为长文本生成简洁的摘要',
      icon: <SummarizeIcon fontSize="large" />
    },
    {
      id: 'extract-keywords',
      title: '提取关键词',
      description: '从文本中提取关键词和短语',
      icon: <LabelIcon fontSize="large" />
    },
    {
      id: 'analyze-database',
      title: '数据库分析',
      description: '分析数据库内容并生成见解',
      icon: <AnalyticsIcon fontSize="large" />
    },
  ];

  return (
    <>
      <Head>
        <title>大模型 | Kortex</title>
        <meta name="description" content="Kortex大模型集成" />
      </Head>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          大模型助手
        </Typography>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          {operationCards.map((card) => (
            <Grid item xs={12} sm={6} md={4} lg={2.4} key={card.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  cursor: 'pointer',
                  border: operation === card.id ? '2px solid #1976d2' : 'none',
                  '&:hover': {
                    boxShadow: 3,
                  },
                }}
                onClick={() => setOperation(card.id)}
              >
                <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                  <Box sx={{ color: operation === card.id ? 'primary.main' : 'text.secondary', mb: 1 }}>
                    {card.icon}
                  </Box>
                  <Typography gutterBottom variant="h6" component="h2">
                    {card.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {card.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                输入
              </Typography>

              {/* 模型选择 */}
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel id="model-select-label">选择模型</InputLabel>
                <Select
                  labelId="model-select-label"
                  value={selectedModel}
                  label="选择模型"
                  onChange={(e) => setSelectedModel(e.target.value)}
                  disabled={loadingModels}
                  startAdornment={
                    loadingModels ? (
                      <Box sx={{ display: 'flex', alignItems: 'center', pl: 1 }}>
                        <CircularProgress size={20} />
                      </Box>
                    ) : null
                  }
                >
                  {models.length === 0 && !loadingModels ? (
                    <MenuItem disabled value="">
                      <em>没有可用的模型</em>
                    </MenuItem>
                  ) : (
                    models.map((model) => (
                      <MenuItem
                        key={model.id}
                        value={model.id.toString()}
                        disabled={!model.is_active}
                      >
                        {model.name} ({model.provider})
                        {!model.is_active && " (禁用)"}
                      </MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>

              {operation === 'analyze-database' ? (
                <Box sx={{ mb: 2 }}>
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel id="database-select-label">选择数据库</InputLabel>
                    <Select
                      labelId="database-select-label"
                      value={selectedDatabase}
                      label="选择数据库"
                      onChange={(e) => setSelectedDatabase(e.target.value)}
                    >
                      {mockDatabases.map((db) => (
                        <MenuItem key={db.id} value={db.id}>{db.name}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  <TextField
                    fullWidth
                    multiline
                    rows={10}
                    variant="outlined"
                    placeholder="输入分析提示..."
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                  />
                </Box>
              ) : (
                <TextField
                  fullWidth
                  multiline
                  rows={15}
                  variant="outlined"
                  placeholder={
                    operation === 'analyze' ? "输入要分析的文本..." :
                    operation === 'generate' ? "输入生成提示..." :
                    operation === 'summarize' ? "输入要摘要的文本..." :
                    "输入要提取关键词的文本..."
                  }
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                />
              )}

              <Box sx={{ mt: 2, textAlign: 'right' }}>
                <Button
                  variant="contained"
                  endIcon={<SendIcon />}
                  onClick={handleSubmit}
                  disabled={
                    isLoading ||
                    !inputText ||
                    !selectedModel ||
                    models.length === 0 ||
                    (operation === 'analyze-database' && !selectedDatabase)
                  }
                  title={
                    !selectedModel || models.length === 0
                      ? "请先选择一个可用的模型"
                      : (operation === 'analyze-database' && !selectedDatabase)
                        ? "请选择数据库"
                        : !inputText
                          ? "请输入内容"
                          : "提交请求"
                  }
                >
                  {isLoading ? <CircularProgress size={24} /> : '提交'}
                </Button>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                输出
              </Typography>
              <Box sx={{ minHeight: '400px' }}>
                {isLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                    <CircularProgress />
                  </Box>
                ) : outputText ? (
                  <Box className="markdown-preview">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {outputText}
                    </ReactMarkdown>
                  </Box>
                ) : (
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'text.secondary' }}>
                    <Typography>输出结果将显示在这里</Typography>
                  </Box>
                )}
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </>
  );
}
