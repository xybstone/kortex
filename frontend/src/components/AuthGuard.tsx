import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/contexts/AuthContext';
import { CircularProgress, Box } from '@mui/material';

interface AuthGuardProps {
  children: React.ReactNode;
}

// 不需要认证的路由
const publicRoutes = ['/login', '/register'];

export default function AuthGuard({ children }: AuthGuardProps) {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // 如果不是公开路由且未认证，重定向到登录页
    if (!loading && !isAuthenticated && !publicRoutes.includes(router.pathname)) {
      router.push('/login');
    }
    
    // 如果已认证且访问登录或注册页，重定向到首页
    if (!loading && isAuthenticated && publicRoutes.includes(router.pathname)) {
      router.push('/notes');
    }
  }, [isAuthenticated, loading, router]);

  // 如果正在加载，显示加载指示器
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh'
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // 如果是公开路由或已认证，显示子组件
  if (publicRoutes.includes(router.pathname) || isAuthenticated) {
    return <>{children}</>;
  }

  // 默认返回null，等待重定向
  return null;
}
