import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';

// 定义用户类型
interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_admin: boolean;
}

// 定义认证上下文类型
interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

// 创建认证上下文
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 认证上下文提供者组件
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // 检查用户是否已登录
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        // 设置默认请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        // 获取当前用户信息
        const response = await axios.get('http://localhost:8000/api/auth/me');
        setUser(response.data);
      } catch (err) {
        console.error('获取用户信息失败:', err);
        localStorage.removeItem('token');
        delete axios.defaults.headers.common['Authorization'];
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // 登录
  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);

    try {
      // OAuth2 要求使用 username 和 password 字段，并且使用 x-www-form-urlencoded 格式
      const params = new URLSearchParams();
      params.append('username', email);
      params.append('password', password);

      const response = await axios.post('http://localhost:8000/api/auth/login', params);

      // 保存token到localStorage
      const token = response.data.access_token;
      localStorage.setItem('token', token);

      // 设置默认请求头
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      // 获取用户信息
      const userResponse = await axios.get('http://localhost:8000/api/auth/me');
      setUser(userResponse.data);

      // 重定向到首页
      router.push('/notes');
    } catch (err: any) {
      console.error('登录失败:', err);
      setError(err.response?.data?.detail || '登录失败，请检查邮箱和密码');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // 注册
  const register = async (email: string, password: string, fullName?: string) => {
    setLoading(true);
    setError(null);

    try {
      await axios.post('http://localhost:8000/api/auth/register', {
        email,
        password,
        full_name: fullName
      });

      // 注册成功后自动登录
      await login(email, password);
    } catch (err: any) {
      console.error('注册失败:', err);
      setError(err.response?.data?.detail || '注册失败，请稍后再试');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // 登出
  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    router.push('/login');
  };

  // 计算是否已认证
  const isAuthenticated = !!user;

  // 提供上下文值
  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAuthenticated
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// 自定义钩子，用于访问认证上下文
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
