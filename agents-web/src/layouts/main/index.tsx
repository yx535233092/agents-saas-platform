import { Outlet, Navigate, useLocation } from 'react-router-dom';
import { Header } from './header';
import { Footer } from './footer';
import { useAuthStore } from '@/stores/auth';

export const MainLayout = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // 仅在首页显示页脚
  const isHomePage = location.pathname === '/';
  // 对话类页面不需要滚动
  const isChatPage =
    location.pathname.startsWith('/apps/') ||
    location.pathname === '/chat-square';

  return (
    <div className={`flex flex-col ${isChatPage ? 'h-screen overflow-hidden' : 'min-h-screen'}`}>
      <Header />
      <main className={isChatPage ? 'flex-1 overflow-hidden' : 'flex-1'}>
        <Outlet />
      </main>
      {isHomePage && <Footer />}
    </div>
  );
};
