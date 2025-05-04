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

// 默认角色数据
const defaultRoles = [
  { id: 1, name: 'AI助手', model_id: 1 }
];

interface ChatPanelProps {
  noteId: number | string;
  onInsertText?: (text: string) => void;
}

export default function ChatPanel({ noteId, onInsertText }: ChatPanelProps) {
  const [selectedRole, setSelectedRole] = useState<number>(1);
  const [roles, setRoles] = useState(defaultRoles);
  const [selectedConversation, setSelectedConversation] = useState<number | null>(null);
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 获取笔记的对话列表
  useEffect(() => {
    if (noteId) {
      // 调用API获取对话列表
      const fetchConversations = async () => {
        try {
          // 在实际应用中，这里应该使用axios或fetch调用API
          // 暂时使用空数组代替mock数据
          const conversations: any[] = [];

          // 示例API调用代码（取消注释使用）:
          // const response = await fetch(`/api/conversations/note/${noteId}`);
          // const conversations = await response.json();

          if (conversations.length > 0) {
            setSelectedConversation(conversations[0].id);
            setSelectedRole(conversations[0].role_id);
          } else {
            setSelectedConversation(null);
            // 获取角色列表
            // const rolesResponse = await fetch('/api/llm-config/roles');
            // const roles = await rolesResponse.json();
            // 暂时使用第一个角色
            setSelectedRole(1);
          }
        } catch (error) {
          console.error('获取对话列表失败:', error);
          setSelectedConversation(null);
          setSelectedRole(1);
        }
      };

      fetchConversations();
    }
  }, [noteId]);

  // 获取对话的消息列表
  useEffect(() => {
    if (selectedConversation) {
      // 调用API获取消息列表
      const fetchMessages = async () => {
        try {
          // 在实际应用中，这里应该使用axios或fetch调用API
          // 暂时使用空数组代替mock数据
          setMessages([]);

          // 示例API调用代码（取消注释使用）:
          // const response = await fetch(`/api/conversations/${selectedConversation}/messages`);
          // const data = await response.json();
          // setMessages(data);
        } catch (error) {
          console.error('获取消息失败:', error);
          setMessages([]);
        }
      };

      fetchMessages();
    } else {
      setMessages([]);
    }
  }, [selectedConversation]);

  // 滚动到最新消息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!message.trim() || !selectedConversation) return;

    // 添加用户消息
    const userMessage = {
      id: Date.now(),
      conversation_id: selectedConversation,
      content: message,
      role: "user",
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    const userMessageContent = message;
    setMessage('');
    setIsLoading(true);

    try {
      // 在实际应用中，这里会调用API发送消息
      // 示例API调用代码:
      // const response = await fetch(`/api/conversations/${selectedConversation}/messages`, {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({
      //     content: userMessageContent,
      //     role: 'user'
      //   }),
      // });
      // const data = await response.json();

      // 模拟API调用延迟
      setTimeout(() => {
        // 添加AI响应
        const aiMessage = {
          id: Date.now() + 1,
          conversation_id: selectedConversation,
          content: `这是对"${userMessageContent}"的回复。在实际应用中，这里会调用大模型API获取响应。`,
          role: "assistant",
          created_at: new Date().toISOString()
        };

        setMessages(prev => [...prev, aiMessage]);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('发送消息失败:', error);
      setIsLoading(false);
    }
  };

  const handleCreateConversation = async () => {
    try {
      setIsLoading(true);
      // 在实际应用中，这里会调用API创建新对话
      // 示例API调用代码:
      // const response = await fetch('/api/conversations', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({
      //     note_id: Number(noteId),
      //     role_id: selectedRole
      //   }),
      // });
      // const data = await response.json();
      // setSelectedConversation(data.id);

      // 暂时使用模拟数据
      const newConversationId = Date.now();
      setSelectedConversation(newConversationId);

      // 模拟初始消息
      setTimeout(() => {
        const initialMessage = {
          id: Date.now(),
          conversation_id: newConversationId,
          content: `你好，我是AI助手，有什么可以帮助你的？`,
          role: "assistant",
          created_at: new Date().toISOString()
        };
        setMessages([initialMessage]);
        setIsLoading(false);
      }, 500);
    } catch (error) {
      console.error('创建对话失败:', error);
      setIsLoading(false);
    }
  };

  const handleDeleteConversation = async () => {
    if (!selectedConversation) return;

    try {
      setIsLoading(true);
      // 在实际应用中，这里会调用API删除对话
      // 示例API调用代码:
      // await fetch(`/api/conversations/${selectedConversation}`, {
      //   method: 'DELETE'
      // });

      // 删除后重新获取对话列表
      // const response = await fetch(`/api/conversations/note/${noteId}`);
      // const conversations = await response.json();

      // 暂时使用模拟逻辑
      setSelectedConversation(null);
      setSelectedRole(1);
      setMessages([]);
      setIsLoading(false);
    } catch (error) {
      console.error('删除对话失败:', error);
      setIsLoading(false);
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
              当前对话: AI助手
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
                {roles.map((role) => (
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
