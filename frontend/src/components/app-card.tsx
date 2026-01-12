import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Bot, Star, PlayCircle, Users, Shield, Lock, Search, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { Application } from '@/types/application';

// 图标映射
const IconMap = {
  shield: Shield,
  lock: Lock,
  search: Search,
  bot: Bot,
  sparkles: Sparkles
};

interface AppCardProps {
  app: Application;
}

export function AppCard({ app }: AppCardProps) {
  const navigate = useNavigate();
  const IconComponent = IconMap[app.icon as keyof typeof IconMap] || Bot;
  const appTypeLabel = app.app_type === 'secret_judgement' ? '专业服务' : '自定义应用';

  return (
    <Card className="flex flex-col overflow-hidden transition-all hover:shadow-lg">
      <CardHeader className="border-b bg-muted/40 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10`}>
              <IconComponent className={`h-6 w-6 ${app.icon_color || 'text-primary'}`} />
            </div>
            <div>
              <CardTitle className="text-base">{app.name}</CardTitle>
              <CardDescription className="text-xs">
                {appTypeLabel}
              </CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 p-4">
        <p className="text-sm text-muted-foreground line-clamp-3">
          {app.description || '暂无描述'}
        </p>
      </CardContent>
      <CardFooter className="flex items-center justify-between border-t bg-muted/10 p-4">
        <div className="flex items-center space-x-2 text-xs text-muted-foreground">
          <Badge variant="outline" className="text-xs">
            {app.response_format === 'sse' ? 'SSE' : app.response_format?.toUpperCase() || 'JSON'}
          </Badge>
        </div>
        <Button 
          size="sm" 
          className="h-8 gap-1"
          onClick={() => navigate(`/apps/${app.id}`)}
        >
          <PlayCircle className="h-3.5 w-3.5" />
          运行
        </Button>
      </CardFooter>
    </Card>
  );
}

