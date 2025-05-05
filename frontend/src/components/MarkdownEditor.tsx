import { useState, useEffect, useRef } from 'react';
import { Box, Paper, Toolbar, IconButton, Tooltip, Divider, ToggleButtonGroup, ToggleButton } from '@mui/material';
import FormatBoldIcon from '@mui/icons-material/FormatBold';
import FormatItalicIcon from '@mui/icons-material/FormatItalic';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered';
import CodeIcon from '@mui/icons-material/Code';
import TableChartIcon from '@mui/icons-material/TableChart';
import ImageIcon from '@mui/icons-material/Image';
import LinkIcon from '@mui/icons-material/Link';
import VisibilityIcon from '@mui/icons-material/Visibility';
import EditIcon from '@mui/icons-material/Edit';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownEditorProps {
  initialValue?: string;
  onChange?: (value: string) => void;
  ref?: React.RefObject<any>;
  readOnly?: boolean;
  defaultEditMode?: boolean;
}

export default function MarkdownEditor({
  initialValue = '',
  onChange,
  ref,
  readOnly = false,
  defaultEditMode = false
}: MarkdownEditorProps) {
  const [markdownText, setMarkdownText] = useState(initialValue);
  const [viewMode, setViewMode] = useState<'edit' | 'preview'>(
    readOnly ? 'preview' : (defaultEditMode ? 'edit' : 'preview')
  );
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (onChange) {
      onChange(markdownText);
    }
  }, [markdownText, onChange]);

  // 当initialValue变化时更新编辑器内容
  useEffect(() => {
    setMarkdownText(initialValue);
  }, [initialValue]);

  // 当readOnly或defaultEditMode属性变化时更新视图模式
  useEffect(() => {
    if (readOnly) {
      setViewMode('preview');
    } else if (defaultEditMode) {
      setViewMode('edit');
    }
  }, [readOnly, defaultEditMode]);

  const handleViewModeChange = (event: React.MouseEvent<HTMLElement>, newMode: 'edit' | 'preview' | null) => {
    if (newMode !== null) {
      setViewMode(newMode);
    }
  };

  const insertMarkdown = (prefix: string, suffix: string = '') => {
    if (readOnly || viewMode === 'preview') return;

    const textarea = textareaRef.current;
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
      <Paper elevation={0} className="editor-container">
        <Toolbar variant="dense" sx={{ mb: 1, display: 'flex', justifyContent: 'space-between' }}>
          {/* 格式化工具栏 */}
          <Box sx={{ display: viewMode === 'edit' ? 'flex' : 'none', alignItems: 'center' }}>
            <Tooltip title="加粗">
              <IconButton onClick={formatHandlers.bold} disabled={readOnly}>
                <FormatBoldIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="斜体">
              <IconButton onClick={formatHandlers.italic} disabled={readOnly}>
                <FormatItalicIcon />
              </IconButton>
            </Tooltip>
            <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
            <Tooltip title="无序列表">
              <IconButton onClick={formatHandlers.bulletList} disabled={readOnly}>
                <FormatListBulletedIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="有序列表">
              <IconButton onClick={formatHandlers.numberedList} disabled={readOnly}>
                <FormatListNumberedIcon />
              </IconButton>
            </Tooltip>
            <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
            <Tooltip title="代码块">
              <IconButton onClick={formatHandlers.code} disabled={readOnly}>
                <CodeIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="表格">
              <IconButton onClick={formatHandlers.table} disabled={readOnly}>
                <TableChartIcon />
              </IconButton>
            </Tooltip>
            <Divider orientation="vertical" flexItem sx={{ mx: 1 }} />
            <Tooltip title="图片">
              <IconButton onClick={formatHandlers.image} disabled={readOnly}>
                <ImageIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="链接">
              <IconButton onClick={formatHandlers.link} disabled={readOnly}>
                <LinkIcon />
              </IconButton>
            </Tooltip>
          </Box>

          {/* 视图模式切换 */}
          {!readOnly && (
            <ToggleButtonGroup
              value={viewMode}
              exclusive
              onChange={handleViewModeChange}
              aria-label="视图模式"
              size="small"
              sx={{ ml: 'auto' }}
            >
              <ToggleButton value="edit" aria-label="编辑模式">
                <Tooltip title="编辑模式">
                  <EditIcon fontSize="small" />
                </Tooltip>
              </ToggleButton>
              <ToggleButton value="preview" aria-label="预览模式">
                <Tooltip title="预览模式">
                  <VisibilityIcon fontSize="small" />
                </Tooltip>
              </ToggleButton>
            </ToggleButtonGroup>
          )}
        </Toolbar>

        <Box className="editor-content">
          {/* 编辑区域 - 仅在编辑模式显示 */}
          {viewMode === 'edit' && (
            <Box className="editor-input" sx={{ width: '100%' }}>
              <textarea
                ref={textareaRef}
                id="markdown-textarea"
                className="editor-textarea"
                value={markdownText}
                onChange={(e) => setMarkdownText(e.target.value)}
                placeholder="在此输入Markdown文本..."
                readOnly={readOnly}
              />
            </Box>
          )}

          {/* 预览区域 - 仅在预览模式显示 */}
          {viewMode === 'preview' && (
            <Box className="editor-preview" sx={{ width: '100%' }}>
              <div className="markdown-preview">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {markdownText}
                </ReactMarkdown>
              </div>
            </Box>
          )}
        </Box>
      </Paper>
    </Box>
  );
}
