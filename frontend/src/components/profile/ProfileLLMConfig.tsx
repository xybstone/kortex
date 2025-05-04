import { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Tabs,
  Tab
} from '@mui/material';
import { useAuth } from '@/contexts/AuthContext';
import LLMProviders from './llm/LLMProviders';
import LLMModels from './llm/LLMModels';
import LLMRoles from './llm/LLMRoles';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`llm-config-tabpanel-${index}`}
      aria-labelledby={`llm-config-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface ProfileLLMConfigProps {
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

export default function ProfileLLMConfig({ onSuccess, onError }: ProfileLLMConfigProps) {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          大模型配置
        </Typography>
        <Typography variant="body1" color="text.secondary">
          管理您的大模型供应商、模型和角色
        </Typography>
      </Box>

      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          centered
        >
          <Tab label="供应商" />
          <Tab label="模型" />
          <Tab label="角色" />
        </Tabs>

        {/* 供应商面板 */}
        <TabPanel value={tabValue} index={0}>
          <LLMProviders onSuccess={onSuccess} onError={onError} />
        </TabPanel>

        {/* 模型面板 */}
        <TabPanel value={tabValue} index={1}>
          <LLMModels onSuccess={onSuccess} onError={onError} />
        </TabPanel>

        {/* 角色面板 */}
        <TabPanel value={tabValue} index={2}>
          <LLMRoles onSuccess={onSuccess} onError={onError} />
        </TabPanel>
      </Paper>
    </>
  );
}
