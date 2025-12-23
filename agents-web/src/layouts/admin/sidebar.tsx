import {
  LayoutDashboard,
  Users,
  Settings,
  Shield,
  Building2,
  Lock,
  AppWindow,
  Bot
} from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils';

export function Sidebar() {
  const menuItems = [
    { icon: LayoutDashboard, label: '概览', href: '/admin/dashboard' },
    { icon: Users, label: '用户管理', href: '/admin/users' },
    { icon: Shield, label: '角色管理', href: '/admin/roles' },
    { icon: Building2, label: '部门管理', href: '/admin/departments' },
    { icon: Lock, label: '权限管理', href: '/admin/permissions' },
    { icon: AppWindow, label: '应用管理', href: '/admin/apps' },
    { icon: Bot, label: '模型配置', href: '/admin/model-configs' },
    { icon: Settings, label: '系统设置', href: '/admin/settings' }
  ];

  return (
    <aside className="hidden w-64 flex-col border-r bg-sidebar text-sidebar-foreground md:flex">
      <div className="flex h-14 items-center border-b px-4">
        <span className="text-lg font-bold">系统后台管理</span>
      </div>

      <div className="flex-1 overflow-y-auto py-4">
        <nav className="grid gap-1 px-2">
          {menuItems.map((item, index) => (
            <NavLink
              key={index}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
                  isActive && item.href !== '/'
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-muted-foreground'
                )
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </aside>
  );
}
