import { useState } from 'react';
import { Command, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '@/services/auth';
import { useAuthStore } from '@/stores/auth';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuthStore();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const { access, refresh } = await authService.login({
        username,
        password
      });
      setTokens(access, refresh);

      const user = await authService.me();
      // @ts-expect-error some error
      setUser(user);

      navigate('/');
    } catch (err: any) {
      console.error(err);
      setError('登录失败，请检查账号密码');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 overflow-hidden rounded-xl border bg-background shadow-lg lg:grid-cols-2">
      {/* 左侧：表单区域 */}
      <div className="flex flex-col justify-center p-8 md:p-12">
        <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
          <div className="flex flex-col space-y-2 text-center">
            <h1 className="text-2xl font-semibold tracking-tight">欢迎回来</h1>
            <p className="text-sm text-muted-foreground">
              请输入您的账号密码以继续
            </p>
          </div>

          <div className="grid gap-6">
            <form onSubmit={handleLogin}>
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <label
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    htmlFor="username"
                  >
                    账号
                  </label>
                  <input
                    id="username"
                    placeholder="admin"
                    type="text"
                    autoCapitalize="none"
                    autoComplete="username"
                    autoCorrect="off"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                  />
                </div>
                <div className="grid gap-2">
                  <div className="flex items-center justify-between">
                    <label
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      htmlFor="password"
                    >
                      密码
                    </label>
                  </div>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                  />
                </div>
                {error && <div className="text-sm text-red-500">{error}</div>}
                <Button className="w-full" disabled={loading}>
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  登录
                </Button>
              </div>
            </form>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                  或者
                </span>
              </div>
            </div>

            <Button variant="outline" type="button" disabled>
              使用 GitHub 登录 (演示)
            </Button>
          </div>

          <p className="px-8 text-center text-sm text-muted-foreground">
            点击登录即代表您同意我们的{' '}
            <Link
              to="/terms"
              className="underline underline-offset-4 hover:text-primary"
            >
              服务条款
            </Link>{' '}
            和{' '}
            <Link
              to="/privacy"
              className="underline underline-offset-4 hover:text-primary"
            >
              隐私政策
            </Link>
            .
          </p>
        </div>
      </div>

      {/* 右侧：装饰区域 (在大屏幕显示) */}
      <div className="relative hidden flex-col bg-muted p-10 text-white lg:flex dark:border-l">
        <div className="absolute inset-0 bg-zinc-900" />
        <div className="relative z-20 flex items-center text-lg font-medium">
          <Command className="mr-2 h-6 w-6" />
          ASP - Agents Saas Platform
        </div>
        <div className="relative z-20 mt-auto">
          <blockquote className="space-y-2">
            <footer className="text-sm">x</footer>
          </blockquote>
        </div>
      </div>
    </div>
  );
}
