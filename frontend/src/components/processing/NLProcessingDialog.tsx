import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Divider,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SendIcon from '@mui/icons-material/Send';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import { DataSource } from '@/services/datasetApi';
import nlpApi from '@/services/nlpApi';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface NLProcessingDialogProps {
  open: boolean;
  onClose: () => void;
  dataSource: DataSource;
  onTaskCreated: () => void;
}

const NLProcessingDialog: React.FC<NLProcessingDialogProps> = ({
  open,
  onClose,
  dataSource,
  onTaskCreated
}) => {
  const [instruction, setInstruction] = useState('');
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [processingResult, setProcessingResult] = useState<any | null>(null);

  const handleClose = () => {
    if (!loading && !analyzing) {
      setInstruction('');
      setError(null);
      setAnalysisResult(null);
      setProcessingResult(null);
      onClose();
    }
  };

  const handleAnalyze = async () => {
    if (!instruction.trim()) {
      setError('请输入处理指令');
      return;
    }

    setAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const result = await nlpApi.analyzeInstruction({ instruction });
      setAnalysisResult(result);
    } catch (err: any) {
      console.error('分析指令失败:', err);
      setError(err.response?.data?.detail || '分析指令失败，请稍后再试');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSubmit = async () => {
    if (!instruction.trim()) {
      setError('请输入处理指令');
      return;
    }

    setLoading(true);
    setError(null);
    setProcessingResult(null);

    try {
      const result = await nlpApi.processInstruction({
        instruction,
        data_source_id: dataSource.id
      });

      setProcessingResult(result);

      if (result.success) {
        // 等待一段时间后关闭对话框，让用户看到成功信息
        setTimeout(() => {
          onTaskCreated();
          handleClose();
        }, 2000);
      }
    } catch (err: any) {
      console.error('处理指令失败:', err);
      setError(err.response?.data?.detail || '处理指令失败，请稍后再试');
    } finally {
      setLoading(false);
    }
  };

  // 示例提示
  const examples = [
    '清理users表中的重复记录',
    '分析sales表中的销售趋势',
    '提取PDF文件中的所有表格',
    '爬取网站的所有产品信息'
  ];

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '60vh' }
      }}
    >
      <DialogTitle>自然语言处理</DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            数据源: {dataSource.name} ({dataSource.type})
          </Typography>
          <Typography variant="body2" color="text.secondary">
            使用自然语言描述您想要执行的处理任务，系统将自动创建相应的处理任务。
          </Typography>
        </Box>

        <TextField
          label="处理指令"
          placeholder="例如：清理users表中的重复记录"
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          fullWidth
          multiline
          rows={4}
          margin="normal"
          disabled={loading || analyzing}
        />

        <Box sx={{ mt: 1, mb: 2 }}>
          <Typography variant="caption" color="text.secondary">
            示例:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 0.5 }}>
            {examples.map((example, index) => (
              <Chip
                key={index}
                label={example}
                size="small"
                onClick={() => setInstruction(example)}
                disabled={loading || analyzing}
              />
            ))}
          </Box>
        </Box>

        {analysisResult && (
          <Paper variant="outlined" sx={{ p: 2, mt: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              分析结果
            </Typography>
            <Box sx={{ mb: 1 }}>
              <Typography variant="body2">
                <strong>任务类型:</strong> {analysisResult.task_type}
              </Typography>
              <Typography variant="body2">
                <strong>置信度:</strong> {(analysisResult.confidence * 100).toFixed(1)}%
              </Typography>
            </Box>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>任务参数</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <pre style={{ overflow: 'auto' }}>
                  {JSON.stringify(analysisResult.parameters, null, 2)}
                </pre>
              </AccordionDetails>
            </Accordion>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>推理过程</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2">{analysisResult.reasoning}</Typography>
              </AccordionDetails>
            </Accordion>
          </Paper>
        )}

        {processingResult && (
          <Paper
            variant="outlined"
            sx={{
              p: 2,
              mt: 2,
              mb: 2,
              bgcolor: processingResult.success ? 'success.light' : 'error.light'
            }}
          >
            <Typography variant="subtitle1" gutterBottom>
              处理结果
            </Typography>
            {processingResult.success ? (
              <>
                <Typography variant="body2">
                  成功创建处理任务 (ID: {processingResult.task_id})
                </Typography>
                <Typography variant="body2">
                  任务类型: {processingResult.task_type}
                </Typography>
              </>
            ) : (
              <Typography variant="body2" color="error">
                {processingResult.error}
              </Typography>
            )}
          </Paper>
        )}
      </DialogContent>
      <DialogActions>
        <Button
          onClick={handleAnalyze}
          disabled={!instruction.trim() || loading || analyzing}
          startIcon={analyzing ? <CircularProgress size={20} /> : <LightbulbIcon />}
        >
          分析
        </Button>
        <Button onClick={handleClose} disabled={loading || analyzing}>
          取消
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={!instruction.trim() || loading || analyzing}
          startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
        >
          创建任务
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default NLProcessingDialog;
