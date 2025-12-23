import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, Filter, LayoutGrid, List } from 'lucide-react';
import { AppCard, type App } from '@/components/app-card';
import { useState } from 'react';

// Mock Data
const MOCK_APPS: App[] = [
  // {
  //   id: '1',
  //   name: '法律法规助手',
  //   description: '根据用户给出的具体情景，给出对应的法律法规建议。',
  //   category: '专业服务',
  //   rating: 4.8,
  //   users: 12500,
  //   isNew: true
  // },
  {
    id: '2',
    name: '涉密研判助手',
    description: '研判文件内容是否涉密，给出涉密研判证据链与具体建议。',
    category: '专业服务',
    rating: 4.9,
    users: 8900
  }
];

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

  const filteredApps = MOCK_APPS.filter((app) => {
    const matchCategory =
      selectedCategory === '全部' || app.category === selectedCategory;
    const matchSearch =
      app.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      app.description.toLowerCase().includes(searchQuery.toLowerCase());
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
      {filteredApps.length > 0 ? (
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
