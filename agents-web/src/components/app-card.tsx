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
import { Bot, Star, PlayCircle, Users } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export interface App {
  id: string;
  name: string;
  description: string;
  category: string;
  rating: number;
  users: number;
  isNew?: boolean;
}

interface AppCardProps {
  app: App;
}

export function AppCard({ app }: AppCardProps) {
  const navigate = useNavigate();

  return (
    <Card className="flex flex-col overflow-hidden transition-all hover:shadow-lg">
      <CardHeader className="border-b bg-muted/40 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              <Bot className="h-6 w-6 text-primary" />
            </div>
            <div>
              <CardTitle className="text-base">{app.name}</CardTitle>
              <CardDescription className="text-xs">
                {app.category}
              </CardDescription>
            </div>
          </div>
          {app.isNew && (
            <Badge variant="secondary" className="bg-green-500/10 text-green-600 hover:bg-green-500/20">
              NEW
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 p-4">
        <p className="text-sm text-muted-foreground line-clamp-3">
          {app.description}
        </p>
      </CardContent>
      <CardFooter className="flex items-center justify-between border-t bg-muted/10 p-4">
        <div className="flex items-center space-x-4 text-xs text-muted-foreground">
          <div className="flex items-center">
            <Star className="mr-1 h-3 w-3 fill-yellow-500 text-yellow-500" />
            {app.rating}
          </div>
          <div className="flex items-center">
            <Users className="mr-1 h-3 w-3" />
            {app.users > 1000 ? `${(app.users / 1000).toFixed(1)}k` : app.users}
          </div>
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

