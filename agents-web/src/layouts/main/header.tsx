import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Command, LayoutDashboard, LogOut, MessageSquare } from 'lucide-react';
import { useAuthStore } from '@/stores/auth';

export function Header() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-14 items-center px-4 md:px-6">
        <div className="mr-4 flex">
          <Link to="/" className="mr-6 flex items-center space-x-2">
            <Command className="h-6 w-6" />
            <span className="hidden font-bold sm:inline-block">ASP</span>
          </Link>
          <nav className="flex items-center space-x-6 text-sm font-medium">
            <Link
              to="/chat-square"
              className="transition-colors hover:text-foreground/80 text-foreground/60 flex items-center gap-1"
            >
              <MessageSquare className="h-4 w-4" />
              对话广场
            </Link>
            <Link
              to="/docs"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              文档中心
            </Link>
          </nav>
        </div>

        <div className="flex flex-1 items-center justify-end space-x-2">
          <nav className="flex items-center space-x-2">
            {isAuthenticated ? (
              <>
                <Link to="/admin/dashboard">
                  <Button variant="ghost" size="sm">
                    <LayoutDashboard className="mr-2 h-4 w-4" />
                    进入后台
                  </Button>
                </Link>
                <div className="text-sm text-muted-foreground mx-2">
                  {user?.username}
                </div>
                <Button variant="ghost" size="sm" onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  退出
                </Button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" size="sm">
                    登录
                  </Button>
                </Link>
                <Link to="/login">
                  <Button size="sm">免费试用</Button>
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
