import { http } from '@/lib/http';
import type { LoginResponse } from '@/types/auth';
import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || '/api';

export const authService = {
  // 统一认证系统使用 OAuth2PasswordRequestForm，需要 application/x-www-form-urlencoded 格式
  // nginx配置: location /api/auth/ { proxy_pass http://127.0.0.1:8000/api/v1/; }
  // 问题：nginx收到 /api/auth/auth/token，但认证系统也收到 /api/auth/auth/token，说明nginx没有正确替换
  // 解决方案：修改nginx配置，使用 rewrite 或者调整 proxy_pass
  // 或者修改前端请求路径，直接请求 /api/auth/token，然后nginx转发到 /api/v1/token
  // 但实际路由是 /api/v1/auth/token，所以需要调整
  login: async (data: { username: string; password: string }) => {
    // 使用 URLSearchParams 发送登录请求（OAuth2PasswordRequestForm 格式）
    const params = new URLSearchParams();
    params.append('username', data.username);
    params.append('password', data.password);

    // nginx配置: location /api/auth/ { proxy_pass http://127.0.0.1:8000/api/v1/; }
    // 如果nginx没有正确替换路径，需要修改nginx配置使用rewrite
    // 或者修改前端请求路径
    // 当前请求: /api/auth/auth/token -> 应该转发到 /api/v1/auth/token
    // 如果nginx没有正确替换，可以尝试直接请求 /api/auth/token，然后nginx转发到 /api/v1/token
    // 但实际路由是 /api/v1/auth/token，所以需要nginx配置 rewrite
    const url = `${baseURL}/auth/auth/token`;
    console.log('Login request URL:', url);

    // 直接使用 axios 发送请求，因为需要 application/x-www-form-urlencoded 格式
    const response = await axios.post<LoginResponse>(url, params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    return response.data;
  },

  register: (data: { username: string; password: string }) =>
    http.post('/auth/auth/register', {
      username: data.username,
      password: data.password
    }),

  me: () => http.get('/auth/users/me'),

  logout: () => http.post('/auth/auth/logout')
};
