import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, Filter, LayoutGrid, List, Loader2 } from 'lucide-react';
import { AppCard } from '@/components/app-card';
import { useState, useEffect } from 'react';
import { getPublicApplications } from '@/services/applications';
import type { Application } from '@/types/application';

const CATEGORIES = [
  '全部',
  '办公效率',
  '开发辅助',
  '市场营销',
  '数据分析',
  '教育培训',
  '专业服务'
];

export default function LandingPage() {
  const [selectedCategory, setSelectedCategory] = useState('全部');
  const [searchQuery, setSearchQuery] = useState('');
  const [apps, setApps] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchApps = async () => {
      setLoading(true);
      try {
        const data = await getPublicApplications();
        // 只显示启用的应用
        const activeApps = data.filter((app) => app.is_active);
        // 按排序字段排序
        activeApps.sort((a, b) => a.sort_order - b.sort_order);
        setApps(activeApps);
      } catch (error) {
        console.error('获取应用列表失败:', error);
        setApps([]);
      } finally {
        setLoading(false);
      }
    };

    fetchApps();
  }, []);

  const filteredApps = apps.filter((app) => {
    const matchCategory =
      selectedCategory === '全部' || 
      (app.app_type === 'secret_judgement' && selectedCategory === '专业服务') ||
      (app.app_type === 'custom' && selectedCategory !== '专业服务');
    const matchSearch =
      app.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (app.description || '').toLowerCase().includes(searchQuery.toLowerCase());
    return matchCategory && matchSearch;
  });

  return (
    <div className="container mx-auto py-8">
      {/* Header Section */}
      <div className="mb-10 flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">应用广场</h1>
          <p className="mt-2 text-muted-foreground">
            探索并使用企业内部丰富的 AI 智能体应用，提升工作效率。
          </p>
        </div>
        <div className="flex w-full items-center gap-2 md:w-auto">
          <Button variant="outline" size="icon">
            <LayoutGrid className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon">
            <List className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(category)}
              className="rounded-full"
            >
              {category}
            </Button>
          ))}
        </div>
        <div className="relative w-full md:w-72">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="搜索应用..."
            className="w-full pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* App Grid */}
      {loading ? (
        <div className="flex h-64 items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-muted-foreground">加载应用中...</p>
          </div>
        </div>
      ) : filteredApps.length > 0 ? (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filteredApps.map((app) => (
            <AppCard key={app.id} app={app} />
          ))}
        </div>
      ) : (
        <div className="flex h-64 flex-col items-center justify-center rounded-lg border border-dashed text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-muted">
            <Filter className="h-6 w-6 text-muted-foreground" />
          </div>
          <h3 className="mt-4 text-lg font-semibold">没有找到相关应用</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            请尝试调整搜索关键词或筛选条件
          </p>
          <Button
            variant="link"
            onClick={() => {
              setSearchQuery('');
              setSelectedCategory('全部');
            }}
            className="mt-2"
          >
            重置筛选
          </Button>
        </div>
      )}
    </div>
  );
}
