import { useState } from 'react';
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
  
  // 模拟数据库列表
  const mockDatabases = [
    { id: '1', name: '项目数据' },
    { id: '2', name: '客户信息' },
    { id: '3', name: '产品目录' },
  ];
  
  const handleSubmit = () => {
    if (!inputText) return;
    
    setIsLoading(true);
    
    // 模拟API调用
    setTimeout(() => {
      let result = '';
      
      switch (operation) {
        case 'analyze':
          result = `## 分析结果\n\n这段文本主要讨论了以下几个方面：\n\n1. 主题：人工智能在现代社会的应用\n2. 观点：人工智能正在改变各个行业的工作方式\n3. 情感：中性，偏向积极\n\n### 关键观点\n\n- 人工智能技术正在快速发展\n- 各行各业都在采用AI解决方案\n- 需要关注AI的伦理问题`;
          break;
        case 'generate':
          result = `# ${inputText}\n\n人工智能(AI)是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。这些系统能够学习、推理、感知、规划和解决问题。\n\n## 主要应用领域\n\n1. **医疗保健** - 疾病诊断、药物研发、个性化治疗\n2. **金融** - 风险评估、欺诈检测、算法交易\n3. **制造业** - 预测性维护、质量控制、供应链优化\n4. **客户服务** - 聊天机器人、个性化推荐、情感分析\n\n## 技术基础\n\n- 机器学习\n- 深度学习\n- 自然语言处理\n- 计算机视觉\n\n## 未来展望\n\nAI技术将继续发展，并在更多领域找到应用。然而，我们也需要关注伦理问题、隐私保护和就业影响等挑战。`;
          break;
        case 'summarize':
          result = `## 摘要\n\n该文本讨论了人工智能的发展及其对社会的影响。主要观点包括AI技术正在各行业广泛应用，带来效率提升和创新，但也引发了关于隐私、就业和伦理的担忧。作者认为需要平衡技术进步与社会影响，建立适当的监管框架。`;
          break;
        case 'extract-keywords':
          result = `## 关键词\n\n- 人工智能\n- 机器学习\n- 自动化\n- 效率提升\n- 技术创新\n- 伦理考量\n- 隐私保护\n- 就业影响\n- 监管框架\n- 社会变革`;
          break;
        case 'analyze-database':
          result = `## 数据库分析结果\n\n基于"${mockDatabases.find(db => db.id === selectedDatabase)?.name}"数据库的分析：\n\n### 主要发现\n\n1. 销售趋势呈现季节性波动，第四季度表现最佳\n2. 客户满意度与产品质量高度相关\n3. 价格变动对销量的影响因产品类别而异\n\n### 建议\n\n- 增加第四季度的库存和营销预算\n- 重点关注产品质量改进\n- 针对不同产品类别制定差异化定价策略`;
          break;
      }
      
      setOutputText(result);
      setIsLoading(false);
    }, 2000);
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
                  disabled={isLoading || !inputText || (operation === 'analyze-database' && !selectedDatabase)}
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
