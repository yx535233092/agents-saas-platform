import { createBrowserRouter, Navigate } from 'react-router-dom';
import { MainLayout } from '@/layouts/main';
import { AdminLayout } from '@/layouts/admin';
import { LoginLayout } from '@/layouts/login';
import DashboardPage from '@/pages/admin/dashboard';
import LoginPage from '@/pages/login';
import LandingPage from '@/pages/main/landing';
import AppChatPage from '@/pages/main/chat';
import ChatSquarePage from '@/pages/main/chat-square';
import UserPage from '@/pages/admin/users';
import RolePage from '@/pages/admin/roles';
import ModelConfigsPage from '@/pages/admin/model-configs';

// 懒加载页面占位符
const DeptPage = () => <div>部门管理</div>;
const PermPage = () => <div>权限管理</div>;
const AppPage = () => <div>应用管理</div>;
const SettingsPage = () => <div>系统设置</div>;

export const router = createBrowserRouter([
  // 前台官网 (Main Layout)
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true, // 默认首页
        element: <LandingPage />
      },
      {
        path: 'apps/:id',
        element: <AppChatPage />
      },
      {
        path: 'chat-square',
        element: <ChatSquarePage />
      },
      {
        path: 'docs',
        element: <div>文档页 (Construction)</div>
      }
    ]
  },

  // 登录 (Login Layout)
  {
    path: '/login',
    element: <LoginLayout />,
    children: [
      {
        index: true,
        element: <LoginPage />
      }
    ]
  },

  // 后台 (Admin Layout)
  {
    path: '/admin',
    element: <AdminLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="dashboard" replace />
      },
      {
        path: 'dashboard',
        element: <DashboardPage />
      },
      {
        path: 'users',
        element: <UserPage />
      },
      {
        path: 'roles',
        element: <RolePage />
      },
      {
        path: 'departments',
        element: <DeptPage />
      },
      {
        path: 'permissions',
        element: <PermPage />
      },
      {
        path: 'apps',
        element: <AppPage />
      },
      {
        path: 'model-configs',
        element: <ModelConfigsPage />
      },
      {
        path: 'settings',
        element: <SettingsPage />
      }
    ]
  }
]);
