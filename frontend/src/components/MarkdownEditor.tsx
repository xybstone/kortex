import { useState, useEffect } from 'react';
import { Box, Paper, Toolbar, IconButton, Tooltip, Divider } from '@mui/material';
import FormatBoldIcon from '@mui/icons-material/FormatBold';
import FormatItalicIcon from '@mui/icons-material/FormatItalic';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered';
import CodeIcon from '@mui/icons-material/Code';
import TableChartIcon from '@mui/icons-material/TableChart';
import ImageIcon from '@mui/icons-material/Image';
import LinkIcon from '@mui/icons-material/Link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownEditorProps {
  initialValue?: string;
  onChange?: (value: string) => void;
}

export default function MarkdownEditor({ initialValue = '', onChange }: MarkdownEditorProps) {
  const [markdownText, setMarkdownText] = useState(initialValue);

  useEffect(() => {
    if (onChange) {
      onChange(markdownText);
    }
  }, [markdownText, onChange]);

  const insertMarkdown = (prefix: string, suffix: string = '') => {
    const textarea = document.getElementById('markdown-textarea') as HTMLTextAreaElement;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = markdownText.substring(start, end);
    const beforeText = markdownText.substring(0, start);
    const afterText = markdownText.substring(end);

    const newText = beforeText + prefix + selectedText + suffix + afterText;
    setMarkdownText(newText);

    // 重新设置光标位置
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(
        start + prefix.length,
        end + prefix.length
      );
    }, 0);
  };

  const formatHandlers = {
    bold: () => insertMarkdown('**', '**'),
    italic: () => insertMarkdown('*', '*'),
    bulletList: () => insertMarkdown('- '),
    numberedList: () => insertMarkdown('1. '),
    code: () => insertMarkdown('```\n', '\n```'),
    table: () => insertMarkdown('| Column 1 | Column 2 | Column 3 |\n| --- | --- | --- |\n| Row 1 | Data | Data |\n| Row 2 | Data | Data |\n'),
    image: () => insertMarkdown('![Alt text](image-url)'),
    link: () => insertMarkdown('[Link text](url)'),
  };

  return (
    <Box className="markdown-editor">
      <Paper elevation={0} className="editor-pane">
        <Toolbar variant="dense" sx={{ mb: 1 }}>
          <Tooltip title="加粗">
            <IconButton onClick={formatHandlers.bold}>
              <FormatBoldIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="斜体">
            <IconButton onClick={formatHandlers.italic}>
              <FormatItalicIcon />
            </IconButton>
          </Tooltip>
          <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
          <Tooltip title="无序列表">
            <IconButton onClick={formatHandlers.bulletList}>
              <FormatListBulletedIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="有序列表">
            <IconButton onClick={formatHandlers.numberedList}>
              <FormatListNumberedIcon />
            </IconButton>
          </Tooltip>
          <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
          <Tooltip title="代码块">
            <IconButton onClick={formatHandlers.code}>
              <CodeIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="表格">
            <IconButton onClick={formatHandlers.table}>
              <TableChartIcon />
            </IconButton>
          </Tooltip>
          <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
          <Tooltip title="图片">
            <IconButton onClick={formatHandlers.image}>
              <ImageIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="链接">
            <IconButton onClick={formatHandlers.link}>
              <LinkIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
        <textarea
          id="markdown-textarea"
          className="editor-textarea"
          value={markdownText}
          onChange={(e) => setMarkdownText(e.target.value)}
          placeholder="在此输入Markdown文本..."
        />
      </Paper>
      <Paper elevation={0} className="preview-pane">
        <div className="markdown-preview">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {markdownText}
          </ReactMarkdown>
        </div>
      </Paper>
    </Box>
  );
}
