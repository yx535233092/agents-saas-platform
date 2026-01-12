import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import {
  Plus,
  Pencil,
  Trash2,
  Loader2,
  Shield,
  Lock,
  Search,
  Bot,
  Sparkles,
  Play,
  AlertCircle
} from 'lucide-react';
import {
  getApplications,
  createApplication,
  updateApplication,
  deleteApplication,
  testApplication
} from '@/services/applications';
import type { Application, ApplicationInput } from '@/types/application';
import {
  APP_TYPE_OPTIONS,
  HTTP_METHOD_OPTIONS,
  REQUEST_FORMAT_OPTIONS,
  RESPONSE_FORMAT_OPTIONS,
  APP_ICON_OPTIONS,
  APP_ICON_COLOR_OPTIONS
} from '@/types/application';

// 图标映射
const IconMap = {
  shield: Shield,
  lock: Lock,
  search: Search,
  bot: Bot,
  sparkles: Sparkles
};

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [currentApp, setCurrentApp] = useState<
    Partial<ApplicationInput & { id?: number }>
  >({});
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState<number | null>(null);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    message: string;
  } | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await getApplications();
      setApplications(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('获取应用列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpen = (app?: Application) => {
    if (app) {
      setCurrentApp({
        id: app.id,
        name: app.name,
        description: app.description,
        app_type: app.app_type,
        api_endpoint: app.api_endpoint,
        api_method: app.api_method,
        request_format: app.request_format,
        response_format: app.response_format,
        headers: app.headers,
        timeout: app.timeout,
        icon: app.icon,
        icon_color: app.icon_color,
        is_active: app.is_active,
        sort_order: app.sort_order
      });
      setIsEditing(true);
    } else {
      setCurrentApp({
        app_type: 'secret_judgement',
        api_method: 'POST',
        request_format: 'json',
        response_format: 'sse',
        icon: 'shield',
        icon_color: 'text-blue-500',
        is_active: true,
        sort_order: 0,
        timeout: 300
      });
      setIsEditing(false);
    }
    setOpen(true);
    setTestResult(null);
  };

  const handleSave = async () => {
    if (!currentApp.name || !currentApp.api_endpoint) {
      alert('请填写应用名称和 API 端点');
      return;
    }

    setSaving(true);
    try {
      const payload: ApplicationInput = {
        name: currentApp.name!,
        description: currentApp.description || '',
        app_type: currentApp.app_type || 'custom',
        api_endpoint: currentApp.api_endpoint!,
        api_method: currentApp.api_method || 'POST',
        request_format: currentApp.request_format || 'json',
        response_format: currentApp.response_format || 'json',
        headers: currentApp.headers || {},
        timeout: currentApp.timeout || 300,
        icon: currentApp.icon || 'bot',
        icon_color: currentApp.icon_color || 'text-blue-500',
        is_active: currentApp.is_active ?? true,
        sort_order: currentApp.sort_order || 0
      };

      if (isEditing && currentApp.id) {
        await updateApplication(currentApp.id, payload);
      } else {
        await createApplication(payload);
      }
      setOpen(false);
      fetchData();
    } catch (error) {
      console.error('保存失败:', error);
      alert('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确认删除该应用吗？')) return;
    try {
      await deleteApplication(id);
      fetchData();
    } catch (error) {
      console.error('删除失败:', error);
      alert('删除失败');
    }
  };

  const handleTest = async (id: number) => {
    setTesting(id);
    setTestResult(null);
    try {
      // 根据应用类型发送不同的测试数据
      const testData =
        applications.find((app) => app.id === id)?.app_type ===
        'secret_judgement'
          ? {
              doc_title: '测试文档',
              doc_content: '这是一段测试内容，用于验证涉密研判智能体的连接。'
            }
          : {};

      const result = await testApplication(id, testData);
      setTestResult({
        success: result.success,
        message: result.message
      });
    } catch (error: unknown) {
      setTestResult({
        success: false,
        message: error instanceof Error ? error.message : '测试失败'
      });
    } finally {
      setTesting(null);
    }
  };

  const getAppTypeLabel = (value: string) => {
    return APP_TYPE_OPTIONS.find((p) => p.value === value)?.label || value;
  };

  const parseHeaders = (headers: Record<string, string> | undefined): string => {
    if (!headers) return '';
    try {
      return JSON.stringify(headers, null, 2);
    } catch {
      return '';
    }
  };

  const handleHeadersChange = (value: string) => {
    try {
      const parsed = value.trim() ? JSON.parse(value) : {};
      setCurrentApp({ ...currentApp, headers: parsed });
    } catch {
      // 无效 JSON，暂时不更新
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">应用管理</h2>
          <p className="text-muted-foreground">
            管理三方智能体应用对接配置，支持接入涉密研判等智能体
          </p>
        </div>
        <Button onClick={() => handleOpen()}>
          <Plus className="mr-2 h-4 w-4" /> 新增应用
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">图标</TableHead>
              <TableHead>应用名称</TableHead>
              <TableHead>应用类型</TableHead>
              <TableHead>API 端点</TableHead>
              <TableHead>响应格式</TableHead>
              <TableHead>排序</TableHead>
              <TableHead>状态</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={8} className="h-24 text-center">
                  <Loader2 className="mx-auto h-6 w-6 animate-spin" />
                </TableCell>
              </TableRow>
            ) : applications.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={8}
                  className="h-24 text-center text-muted-foreground"
                >
                  暂无应用配置，点击右上角按钮添加
                </TableCell>
              </TableRow>
            ) : (
              applications.map((app) => {
                const IconComponent =
                  IconMap[app.icon as keyof typeof IconMap] || Bot;
                return (
                  <TableRow key={app.id}>
                    <TableCell>
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted">
                        <IconComponent
                          className={`h-4 w-4 ${app.icon_color || 'text-blue-500'}`}
                        />
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">{app.name}</TableCell>
                    <TableCell>
                      <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                        {getAppTypeLabel(app.app_type)}
                      </span>
                    </TableCell>
                    <TableCell>
                      <code className="rounded bg-muted px-1.5 py-0.5 text-sm">
                        {app.api_method} {app.api_endpoint}
                      </code>
                    </TableCell>
                    <TableCell>
                      <span className="text-xs text-muted-foreground">
                        {app.response_format?.toUpperCase() || 'JSON'}
                      </span>
                    </TableCell>
                    <TableCell>{app.sort_order}</TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                          app.is_active
                            ? 'bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20'
                            : 'bg-red-50 text-red-700 ring-1 ring-inset ring-red-600/20'
                        }`}
                      >
                        {app.is_active ? '启用' : '禁用'}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleTest(app.id)}
                        disabled={testing === app.id}
                        title="测试连接"
                      >
                        {testing === app.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Play className="h-4 w-4" />
                        )}
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleOpen(app)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-red-500 hover:text-red-600"
                        onClick={() => handleDelete(app.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      {testResult && (
        <div
          className={`rounded-md border p-4 ${
            testResult.success
              ? 'bg-green-50 border-green-200'
              : 'bg-red-50 border-red-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <AlertCircle
              className={`h-5 w-5 ${
                testResult.success ? 'text-green-600' : 'text-red-600'
              }`}
            />
            <span
              className={`font-medium ${
                testResult.success ? 'text-green-800' : 'text-red-800'
              }`}
            >
              {testResult.success ? '测试成功' : '测试失败'}
            </span>
          </div>
          <p
            className={`mt-2 text-sm ${
              testResult.success ? 'text-green-700' : 'text-red-700'
            }`}
          >
            {testResult.message}
          </p>
        </div>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {isEditing ? '编辑应用' : '新增应用'}
            </DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            {/* 基本信息 */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">应用名称 *</Label>
                <Input
                  id="name"
                  placeholder="如: 涉密研判智能体"
                  value={currentApp.name || ''}
                  onChange={(e) =>
                    setCurrentApp({ ...currentApp, name: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="app_type">应用类型 *</Label>
                <select
                  id="app_type"
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  value={currentApp.app_type || 'custom'}
                  onChange={(e) =>
                    setCurrentApp({
                      ...currentApp,
                      app_type: e.target.value as 'secret_judgement' | 'custom'
                    })
                  }
                >
                  {APP_TYPE_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">应用描述</Label>
              <Textarea
                id="description"
                placeholder="应用的详细描述..."
                value={currentApp.description || ''}
                onChange={(e) =>
                  setCurrentApp({
                    ...currentApp,
                    description: e.target.value
                  })
                }
                rows={2}
              />
            </div>

            {/* API 配置 */}
            <div className="space-y-4 border-t pt-4">
              <h3 className="font-semibold">API 配置</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="api_method">HTTP 方法 *</Label>
                  <select
                    id="api_method"
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={currentApp.api_method || 'POST'}
                    onChange={(e) =>
                      setCurrentApp({
                        ...currentApp,
                        api_method: e.target.value as 'POST' | 'GET' | 'PUT' | 'DELETE'
                      })
                    }
                  >
                    {HTTP_METHOD_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="timeout">超时时间（秒）</Label>
                  <Input
                    id="timeout"
                    type="number"
                    value={currentApp.timeout || 300}
                    onChange={(e) =>
                      setCurrentApp({
                        ...currentApp,
                        timeout: parseInt(e.target.value) || 300
                      })
                    }
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="api_endpoint">API 端点地址 *</Label>
                <Input
                  id="api_endpoint"
                  placeholder="如: http://localhost:8001/check"
                  value={currentApp.api_endpoint || ''}
                  onChange={(e) =>
                    setCurrentApp({
                      ...currentApp,
                      api_endpoint: e.target.value
                    })
                  }
                />
                {currentApp.app_type === 'secret_judgement' && (
                  <p className="text-xs text-muted-foreground">
                    涉密研判智能体默认端点: http://localhost:8001/check
                  </p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="request_format">请求格式</Label>
                  <select
                    id="request_format"
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={currentApp.request_format || 'json'}
                    onChange={(e) =>
                      setCurrentApp({
                        ...currentApp,
                        request_format: e.target.value as
                          | 'json'
                          | 'form-data'
                          | 'x-www-form-urlencoded'
                      })
                    }
                  >
                    {REQUEST_FORMAT_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="response_format">响应格式</Label>
                  <select
                    id="response_format"
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={currentApp.response_format || 'json'}
                    onChange={(e) =>
                      setCurrentApp({
                        ...currentApp,
                        response_format: e.target.value as 'json' | 'sse' | 'stream'
                      })
                    }
                  >
                    {RESPONSE_FORMAT_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="headers">自定义请求头 (JSON 格式)</Label>
                <Textarea
                  id="headers"
                  placeholder='{"Authorization": "Bearer token", "Content-Type": "application/json"}'
                  value={parseHeaders(currentApp.headers)}
                  onChange={(e) => handleHeadersChange(e.target.value)}
                  rows={3}
                />
                <p className="text-xs text-muted-foreground">
                  可选，JSON 格式的键值对，用于设置自定义请求头
                </p>
              </div>
            </div>

            {/* 显示配置 */}
            <div className="space-y-4 border-t pt-4">
              <h3 className="font-semibold">显示配置</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="icon">图标</Label>
                  <select
                    id="icon"
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={currentApp.icon || 'bot'}
                    onChange={(e) =>
                      setCurrentApp({ ...currentApp, icon: e.target.value })
                    }
                  >
                    {APP_ICON_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="icon_color">图标颜色</Label>
                  <select
                    id="icon_color"
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                    value={currentApp.icon_color || 'text-blue-500'}
                    onChange={(e) =>
                      setCurrentApp({
                        ...currentApp,
                        icon_color: e.target.value
                      })
                    }
                  >
                    {APP_ICON_COLOR_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* 其他配置 */}
            <div className="grid grid-cols-2 gap-4 border-t pt-4">
              <div className="space-y-2">
                <Label htmlFor="sort_order">排序 (越小越靠前)</Label>
                <Input
                  id="sort_order"
                  type="number"
                  value={currentApp.sort_order || 0}
                  onChange={(e) =>
                    setCurrentApp({
                      ...currentApp,
                      sort_order: parseInt(e.target.value) || 0
                    })
                  }
                />
              </div>
              <div className="flex items-center space-x-2 pt-6">
                <Checkbox
                  id="is_active"
                  checked={currentApp.is_active ?? true}
                  onCheckedChange={(checked) =>
                    setCurrentApp({
                      ...currentApp,
                      is_active: checked as boolean
                    })
                  }
                />
                <label htmlFor="is_active" className="text-sm">
                  启用该应用
                </label>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              保存
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

