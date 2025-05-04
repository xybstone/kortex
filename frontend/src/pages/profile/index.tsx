import { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  Avatar,
  Alert,
  Snackbar
} from '@mui/material';
import Head from 'next/head';
import { useAuth } from '@/contexts/AuthContext';
import PersonIcon from '@mui/icons-material/Person';
import SettingsIcon from '@mui/icons-material/Settings';
import StorageIcon from '@mui/icons-material/Storage';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ProfileInfo from '@/components/profile/ProfileInfo';
import ProfileSettings from '@/components/profile/ProfileSettings';
import ProfileDatabases from '@/components/profile/ProfileDatabases';
import ProfileLLMConfig from '@/components/profile/ProfileLLMConfig';

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
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Profile() {
  const { user } = useAuth();
  const [tabValue, setTabValue] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [openSnackbar, setOpenSnackbar] = useState(false);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleCloseSnackbar = () => {
    setOpenSnackbar(false);
  };

  const handleSuccess = (message: string) => {
    setSuccess(message);
    setError('');
    setOpenSnackbar(true);
  };

  const handleError = (message: string) => {
    setError(message);
    setSuccess('');
    setOpenSnackbar(true);
  };

  return (
    <>
      <Head>
        <title>个人资料 | Kortex</title>
        <meta name="description" content="管理您的个人资料" />
      </Head>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
          <Avatar
            sx={{ width: 64, height: 64, bgcolor: 'primary.main', mr: 2 }}
          >
            {user?.full_name ? user.full_name[0].toUpperCase() : user?.email?.[0].toUpperCase()}
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1">
              个人资料
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {user?.email}
            </Typography>
          </Box>
        </Box>

        <Paper sx={{ width: '100%', mb: 2 }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"
          >
            <Tab icon={<PersonIcon />} label="个人信息" />
            <Tab icon={<SettingsIcon />} label="设置" />
            <Tab icon={<StorageIcon />} label="数据库管理" />
            <Tab icon={<SmartToyIcon />} label="大模型配置" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            <Box sx={{ px: { xs: 2, md: 4 } }}>
              <ProfileInfo onSuccess={handleSuccess} onError={handleError} />
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Box sx={{ px: { xs: 2, md: 4 } }}>
              <ProfileSettings onSuccess={handleSuccess} onError={handleError} />
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={2}>
            <Box sx={{ px: { xs: 2, md: 4 } }}>
              <ProfileDatabases onSuccess={handleSuccess} onError={handleError} />
            </Box>
          </TabPanel>

          <TabPanel value={tabValue} index={3}>
            <Box sx={{ px: { xs: 2, md: 4 } }}>
              <ProfileLLMConfig onSuccess={handleSuccess} onError={handleError} />
            </Box>
          </TabPanel>
        </Paper>

        {/* 成功/错误提示 */}
        <Snackbar
          open={openSnackbar}
          autoHideDuration={6000}
          onClose={handleCloseSnackbar}
        >
          <Alert
            onClose={handleCloseSnackbar}
            severity={error ? 'error' : 'success'}
            sx={{ width: '100%' }}
          >
            {error || success}
          </Alert>
        </Snackbar>
      </Container>
    </>
  );
}
