import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography
} from '@mui/material';

interface DeleteConfirmDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  itemType: 'provider' | 'model' | 'role';
  message?: string;
}

export default function DeleteConfirmDialog({
  open,
  onClose,
  onConfirm,
  itemType,
  message
}: DeleteConfirmDialogProps) {
  // 根据类型获取默认消息
  const getDefaultMessage = () => {
    switch (itemType) {
      case 'provider':
        return '确定要删除这个供应商吗？相关的模型和角色也会被删除。';
      case 'model':
        return '确定要删除这个模型吗？相关的角色也会被删除。';
      case 'role':
        return '确定要删除这个角色吗？';
      default:
        return '确定要删除吗？';
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
    >
      <DialogTitle>确认删除</DialogTitle>
      <DialogContent>
        <Typography>
          {message || getDefaultMessage()}
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>取消</Button>
        <Button onClick={onConfirm} color="error" variant="contained">
          删除
        </Button>
      </DialogActions>
    </Dialog>
  );
}
