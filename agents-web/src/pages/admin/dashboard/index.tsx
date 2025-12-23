import {
  Users,
  Activity,
  Bot,
  Zap,
  TrendingUp,
  Cpu,
  MessageSquare
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

// Mock Data
const CHART_DATA = [
  { name: 'Mon', calls: 4000, tokens: 2400 },
  { name: 'Tue', calls: 3000, tokens: 1398 },
  { name: 'Wed', calls: 2000, tokens: 9800 },
  { name: 'Thu', calls: 2780, tokens: 3908 },
  { name: 'Fri', calls: 1890, tokens: 4800 },
  { name: 'Sat', calls: 2390, tokens: 3800 },
  { name: 'Sun', calls: 3490, tokens: 4300 }
];

const RECENT_APPS = [
  {
    name: '周报生成助手',
    category: '办公效率',
    status: '运行中',
    calls: '12.5k',
    avatar: '📝'
  },
  {
    name: '代码审查专家',
    category: '开发辅助',
    status: '运行中',
    calls: '8.9k',
    avatar: '💻'
  },
  {
    name: 'SQL 生成器',
    category: '数据分析',
    status: '维护中',
    calls: '5.6k',
    avatar: '📊'
  },
  {
    name: '营销文案大师',
    category: '市场营销',
    status: '运行中',
    calls: '23k',
    avatar: '📢'
  },
  {
    name: '法律咨询助手',
    category: '专业服务',
    status: '离线',
    calls: '3.2k',
    avatar: '⚖️'
  }
];

export default function DashboardPage() {
  const stats = [
    {
      title: '总调用次数 (API Calls)',
      value: '1,234,567',
      change: '+12.5%',
      icon: Activity,
      color: 'text-blue-500'
    },
    {
      title: '活跃智能体 (Active Agents)',
      value: '42',
      change: '+4',
      icon: Bot,
      color: 'text-purple-500'
    },
    {
      title: 'Token 消耗量',
      value: '89.2M',
      change: '+23.1%',
      icon: Zap,
      color: 'text-yellow-500'
    },
    {
      title: '总用户数',
      value: '2,350',
      change: '+18.2%',
      icon: Users,
      color: 'text-emerald-500'
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">智能体概览</h2>
        <p className="text-muted-foreground">
          实时监控平台智能体运行状态与资源消耗。
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, i) => (
          <div
            key={i}
            className="rounded-xl border bg-card text-card-foreground shadow-sm"
          >
            <div className="flex flex-row items-center justify-between space-y-0 p-6 pb-2">
              <h3 className="text-sm font-medium tracking-tight">
                {stat.title}
              </h3>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </div>
            <div className="p-6 pt-0">
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">
                较上周{' '}
                <span className="font-medium text-emerald-500">
                  {stat.change}
                </span>
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Charts & Lists */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Main Chart */}
        <div className="col-span-4 rounded-xl border bg-card text-card-foreground shadow-sm">
          <div className="flex flex-col space-y-1.5 p-6">
            <h3 className="font-semibold leading-none tracking-tight">
              调用趋势 (7天)
            </h3>
            <p className="text-sm text-muted-foreground">
              API 调用量与 Token 消耗对比
            </p>
          </div>
          <div className="h-[300px] p-6 pt-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={CHART_DATA}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="name"
                  stroke="#888888"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  stroke="#888888"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `${value}`}
                />
                <Tooltip
                  cursor={{ fill: 'transparent' }}
                  contentStyle={{
                    backgroundColor: 'hsl(var(--popover))',
                    borderColor: 'hsl(var(--border))',
                    borderRadius: 'var(--radius)'
                  }}
                />
                <Bar
                  dataKey="calls"
                  fill="hsl(var(--primary))"
                  radius={[4, 4, 0, 0]}
                  name="调用次数"
                />
                <Bar
                  dataKey="tokens"
                  fill="hsl(var(--muted-foreground))"
                  radius={[4, 4, 0, 0]}
                  name="Token (x10)"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Apps List */}
        <div className="col-span-3 rounded-xl border bg-card text-card-foreground shadow-sm">
          <div className="flex flex-col space-y-1.5 p-6">
            <h3 className="font-semibold leading-none tracking-tight">
              热门应用
            </h3>
            <p className="text-sm text-muted-foreground">
              本周使用率最高的智能体
            </p>
          </div>
          <div className="p-6 pt-0">
            <div className="space-y-6">
              {RECENT_APPS.map((app, i) => (
                <div key={i} className="flex items-center">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/10 text-lg">
                    {app.avatar}
                  </div>
                  <div className="ml-4 space-y-1">
                    <p className="text-sm font-medium leading-none">
                      {app.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {app.category}
                    </p>
                  </div>
                  <div className="ml-auto flex flex-col items-end">
                    <div className="font-medium">{app.calls}</div>
                    <div
                      className={`text-xs ${
                        app.status === '运行中'
                          ? 'text-emerald-500'
                          : app.status === '维护中'
                          ? 'text-yellow-500'
                          : 'text-muted-foreground'
                      }`}
                    >
                      {app.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Secondary Metrics */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 text-blue-600">
              <Cpu className="h-6 w-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">99.9%</div>
              <div className="text-xs text-muted-foreground">系统可用性</div>
            </div>
          </div>
        </div>
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-purple-100 text-purple-600">
              <MessageSquare className="h-6 w-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">145ms</div>
              <div className="text-xs text-muted-foreground">平均响应延迟</div>
            </div>
          </div>
        </div>
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-orange-100 text-orange-600">
              <TrendingUp className="h-6 w-6" />
            </div>
            <div>
              <div className="text-2xl font-bold">4.8/5</div>
              <div className="text-xs text-muted-foreground">应用平均评分</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
