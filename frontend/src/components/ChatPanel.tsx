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
  CircularProgress,
  Snackbar,
  Alert
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import DeleteIcon from '@mui/icons-material/Delete';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { conversationApi, llmRoleApi } from '@/services/api';

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

  // 错误提示
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // 获取笔记的对话列表
  useEffect(() => {
    if (noteId && noteId !== 'new') {
      // 调用API获取对话列表
      const fetchConversations = async () => {
        try {
          // 获取对话列表
          const conversations = await conversationApi.getNoteConversations(Number(noteId));

          if (conversations.length > 0) {
            setSelectedConversation(conversations[0].id);
            setSelectedRole(conversations[0].role_id);
          } else {
            setSelectedConversation(null);
            // 获取角色列表
            try {
              const rolesData = await llmRoleApi.getRoles();
              if (rolesData.length > 0) {
                setRoles(rolesData);
                setSelectedRole(rolesData[0].id);
              }
            } catch (roleError) {
              console.error('获取角色列表失败:', roleError);
              // 使用默认角色
            }
          }
        } catch (error) {
          console.error('获取对话列表失败:', error);
          setErrorMessage('获取对话列表失败，请稍后重试');
          setSelectedConversation(null);
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
          const data = await conversationApi.getConversationMessages(selectedConversation);
          setMessages(data);
        } catch (error) {
          console.error('获取消息失败:', error);
          setErrorMessage('获取消息失败，请稍后重试');
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

    // 保存用户消息内容并清空输入框
    const userMessageContent = message;
    setMessage('');
    setIsLoading(true);

    try {
      // 调用API发送消息
      const response = await conversationApi.sendMessage(selectedConversation, userMessageContent);

      // 重新获取消息列表以显示最新的对话
      const updatedMessages = await conversationApi.getConversationMessages(selectedConversation);
      setMessages(updatedMessages);
    } catch (error) {
      console.error('发送消息失败:', error);
      setErrorMessage('发送消息失败，请稍后重试');

      // 如果API调用失败，至少显示用户的消息
      const userMessage = {
        id: Date.now(),
        conversation_id: selectedConversation,
        content: userMessageContent,
        role: "user",
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateConversation = async () => {
    if (!noteId || noteId === 'new') {
      setErrorMessage('请先保存笔记后再创建对话');
      return;
    }

    try {
      setIsLoading(true);
      // 调用API创建新对话
      const data = await conversationApi.createConversation({
        note_id: Number(noteId),
        role_id: selectedRole
      });

      // 设置当前对话ID
      setSelectedConversation(data.id);

      // 获取初始消息
      const initialMessages = await conversationApi.getConversationMessages(data.id);
      setMessages(initialMessages);
    } catch (error) {
      console.error('创建对话失败:', error);
      setErrorMessage('创建对话失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteConversation = async () => {
    if (!selectedConversation) return;

    try {
      setIsLoading(true);
      // 调用API删除对话
      await conversationApi.deleteConversation(selectedConversation);

      // 删除后重新获取对话列表
      if (noteId && noteId !== 'new') {
        const conversations = await conversationApi.getNoteConversations(Number(noteId));
        if (conversations.length > 0) {
          setSelectedConversation(conversations[0].id);
          setSelectedRole(conversations[0].role_id);
          const messages = await conversationApi.getConversationMessages(conversations[0].id);
          setMessages(messages);
        } else {
          setSelectedConversation(null);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error('删除对话失败:', error);
      setErrorMessage('删除对话失败，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  // 关闭错误提示
  const handleCloseError = () => {
    setErrorMessage(null);
  };

  const handleInsertToNote = (text: string) => {
    if (onInsertText) {
      onInsertText(text);
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 错误提示 */}
      <Snackbar
        open={!!errorMessage}
        autoHideDuration={6000}
        onClose={handleCloseError}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
          {errorMessage}
        </Alert>
      </Snackbar>

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
                onKeyDown={(e) => {
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
