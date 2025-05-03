import { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  List, 
  ListItem, 
  ListItemText, 
  Avatar, 
  IconButton, 
  Divider, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem,
  CircularProgress
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import DeleteIcon from '@mui/icons-material/Delete';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// 模拟角色数据
const mockRoles = [
  { id: 1, name: '通用助手', model_id: 1 },
  { id: 2, name: '程序员', model_id: 1 },
  { id: 3, name: '写作助手', model_id: 2 },
  { id: 4, name: '学术助手', model_id: 3 },
];

// 模拟对话数据
const mockConversations = [
  { id: 1, note_id: 1, role_id: 1 },
  { id: 2, note_id: 1, role_id: 3 },
];

// 模拟消息数据
const mockMessages = {
  1: [
    { id: 1, conversation_id: 1, content: "你好，我是通用助手，有什么可以帮助你的？", role: "assistant", created_at: "2023-05-10T10:00:00Z" },
    { id: 2, conversation_id: 1, content: "我想了解一下人工智能的基础知识", role: "user", created_at: "2023-05-10T10:01:00Z" },
    { id: 3, conversation_id: 1, content: "人工智能(AI)是计算机科学的一个分支，致力于创建能够模拟人类智能的系统。这些系统能够学习、推理、感知、规划和解决问题。\n\n主要的AI领域包括：\n\n1. **机器学习** - 使计算机能够从数据中学习，而无需明确编程\n2. **深度学习** - 使用神经网络进行复杂模式识别\n3. **自然语言处理** - 使计算机能够理解和生成人类语言\n4. **计算机视觉** - 使计算机能够解释和理解视觉信息\n\n人工智能已经在许多领域找到了应用，包括医疗保健、金融、制造业和客户服务等。", role: "assistant", created_at: "2023-05-10T10:02:00Z" },
  ],
  2: [
    { id: 4, conversation_id: 2, content: "你好，我是写作助手，有什么可以帮助你的？", role: "assistant", created_at: "2023-05-11T14:00:00Z" },
    { id: 5, conversation_id: 2, content: "我需要写一篇关于环保的文章，有什么建议？", role: "user", created_at: "2023-05-11T14:01:00Z" },
    { id: 6, conversation_id: 2, content: "为了写一篇关于环保的文章，我建议以下结构和内容：\n\n## 标题\n**\"保护地球，从我做起：日常生活中的环保实践\"**\n\n## 引言\n- 简述当前环境面临的挑战\n- 强调个人行动的重要性\n- 提出文章的主要目的：分享实用的环保方法\n\n## 主体部分\n\n### 1. 减少塑料使用\n- 使用可重复使用的购物袋\n- 避免一次性塑料制品\n- 选择无塑料包装的产品\n\n### 2. 节约能源\n- 使用节能灯具和电器\n- 合理设置空调温度\n- 不用时关闭电器电源\n\n### 3. 水资源保护\n- 修复漏水的水龙头\n- 收集雨水用于浇花\n- 减少洗澡时间\n\n### 4. 垃圾分类与回收\n- 学习正确的垃圾分类方法\n- 将可回收物品送去回收\n- 尝试堆肥厨余垃圾\n\n### 5. 绿色出行\n- 使用公共交通工具\n- 骑自行车或步行\n- 考虑拼车或电动汽车\n\n## 结论\n- 总结环保行动的集体影响\n- 鼓励读者从小事做起\n- 展望更可持续的未来\n\n希望这个框架对你有所帮助！", role: "assistant", created_at: "2023-05-11T14:02:00Z" },
  ]
};

interface ChatPanelProps {
  noteId: number | string;
  onInsertText?: (text: string) => void;
}

export default function ChatPanel({ noteId, onInsertText }: ChatPanelProps) {
  const [selectedRole, setSelectedRole] = useState<number>(0);
  const [selectedConversation, setSelectedConversation] = useState<number | null>(null);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // 获取笔记的对话列表
  useEffect(() => {
    if (noteId) {
      // 在实际应用中，这里会调用API获取对话列表
      const conversations = mockConversations.filter(c => c.note_id === Number(noteId));
      if (conversations.length > 0) {
        setSelectedConversation(conversations[0].id);
        setSelectedRole(conversations[0].role_id);
      } else {
        setSelectedConversation(null);
        setSelectedRole(mockRoles[0].id);
      }
    }
  }, [noteId]);
  
  // 获取对话的消息列表
  useEffect(() => {
    if (selectedConversation) {
      // 在实际应用中，这里会调用API获取消息列表
      setMessages(mockMessages[selectedConversation] || []);
    } else {
      setMessages([]);
    }
  }, [selectedConversation]);
  
  // 滚动到最新消息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSendMessage = () => {
    if (!message.trim()) return;
    
    // 添加用户消息
    const userMessage = {
      id: Date.now(),
      conversation_id: selectedConversation || 0,
      content: message,
      role: "user",
      created_at: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setIsLoading(true);
    
    // 模拟API调用延迟
    setTimeout(() => {
      // 添加AI响应
      const aiMessage = {
        id: Date.now() + 1,
        conversation_id: selectedConversation || 0,
        content: `这是对"${message}"的回复。在实际应用中，这里会调用大模型API获取响应。`,
        role: "assistant",
        created_at: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1000);
  };
  
  const handleCreateConversation = () => {
    // 在实际应用中，这里会调用API创建新对话
    const newConversationId = Date.now();
    
    // 模拟创建新对话
    mockConversations.push({
      id: newConversationId,
      note_id: Number(noteId),
      role_id: selectedRole
    });
    
    // 初始化对话消息
    const role = mockRoles.find(r => r.id === selectedRole);
    mockMessages[newConversationId] = [{
      id: Date.now(),
      conversation_id: newConversationId,
      content: `你好，我是${role?.name}，有什么可以帮助你的？`,
      role: "assistant",
      created_at: new Date().toISOString()
    }];
    
    setSelectedConversation(newConversationId);
  };
  
  const handleDeleteConversation = () => {
    if (!selectedConversation) return;
    
    // 在实际应用中，这里会调用API删除对话
    const index = mockConversations.findIndex(c => c.id === selectedConversation);
    if (index !== -1) {
      mockConversations.splice(index, 1);
      delete mockMessages[selectedConversation];
    }
    
    // 选择另一个对话或清空选择
    const conversations = mockConversations.filter(c => c.note_id === Number(noteId));
    if (conversations.length > 0) {
      setSelectedConversation(conversations[0].id);
      setSelectedRole(conversations[0].role_id);
    } else {
      setSelectedConversation(null);
      setSelectedRole(mockRoles[0].id);
    }
  };
  
  const handleInsertToNote = (text: string) => {
    if (onInsertText) {
      onInsertText(text);
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0' }}>
        <Typography variant="h6" gutterBottom>
          AI助手
        </Typography>
        
        {selectedConversation ? (
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography>
              当前对话: {mockRoles.find(r => r.id === mockConversations.find(c => c.id === selectedConversation)?.role_id)?.name}
            </Typography>
            <Box>
              <Button 
                variant="outlined" 
                size="small" 
                onClick={() => setSelectedConversation(null)}
                sx={{ mr: 1 }}
              >
                新对话
              </Button>
              <IconButton 
                size="small" 
                color="error" 
                onClick={handleDeleteConversation}
              >
                <DeleteIcon />
              </IconButton>
            </Box>
          </Box>
        ) : (
          <Box>
            <FormControl fullWidth size="small" sx={{ mb: 2 }}>
              <InputLabel>选择角色</InputLabel>
              <Select
                value={selectedRole}
                label="选择角色"
                onChange={(e) => setSelectedRole(Number(e.target.value))}
              >
                {mockRoles.map((role) => (
                  <MenuItem key={role.id} value={role.id}>
                    {role.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button 
              variant="contained" 
              fullWidth
              onClick={handleCreateConversation}
            >
              开始新对话
            </Button>
          </Box>
        )}
      </Box>
      
      {selectedConversation && (
        <>
          <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
            <List>
              {messages.map((msg) => (
                <ListItem 
                  key={msg.id} 
                  alignItems="flex-start"
                  sx={{ 
                    flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                    mb: 2 
                  }}
                >
                  <Avatar 
                    sx={{ 
                      bgcolor: msg.role === 'user' ? 'primary.main' : 'secondary.main',
                      mr: msg.role === 'user' ? 0 : 2,
                      ml: msg.role === 'user' ? 2 : 0
                    }}
                  >
                    {msg.role === 'user' ? <PersonIcon /> : <SmartToyIcon />}
                  </Avatar>
                  <Paper 
                    elevation={1} 
                    sx={{ 
                      p: 2, 
                      maxWidth: '80%',
                      bgcolor: msg.role === 'user' ? 'primary.light' : 'background.paper',
                      color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary'
                    }}
                  >
                    {msg.role === 'assistant' ? (
                      <Box className="markdown-preview">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                        {msg.content.length > 20 && (
                          <Button 
                            size="small" 
                            onClick={() => handleInsertToNote(msg.content)}
                            sx={{ mt: 1 }}
                          >
                            插入到笔记
                          </Button>
                        )}
                      </Box>
                    ) : (
                      <Typography>{msg.content}</Typography>
                    )}
                  </Paper>
                </ListItem>
              ))}
              {isLoading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              )}
              <div ref={messagesEndRef} />
            </List>
          </Box>
          
          <Box sx={{ p: 2, borderTop: '1px solid #e0e0e0' }}>
            <Box sx={{ display: 'flex' }}>
              <TextField
                fullWidth
                placeholder="输入消息..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                multiline
                maxRows={4}
                disabled={isLoading}
              />
              <Button
                variant="contained"
                endIcon={<SendIcon />}
                onClick={handleSendMessage}
                disabled={!message.trim() || isLoading}
                sx={{ ml: 1 }}
              >
                发送
              </Button>
            </Box>
          </Box>
        </>
      )}
    </Box>
  );
}
