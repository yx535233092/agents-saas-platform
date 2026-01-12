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
import {
  Plus,
  Pencil,
  Trash2,
  Loader2,
  Sparkles,
  Zap,
  Brain,
  Cpu,
  Bot
} from 'lucide-react';
import {
  getModelConfigs,
  createModelConfig,
  updateModelConfig,
  deleteModelConfig
} from '@/services/model-configs';
import type { ModelConfig, ModelConfigInput } from '@/types/model-config';
import {
  PROVIDER_OPTIONS,
  ICON_OPTIONS,
  ICON_COLOR_OPTIONS
} from '@/types/model-config';

// 图标映射
const IconMap = {
  sparkles: Sparkles,
  zap: Zap,
  brain: Brain,
  cpu: Cpu,
  bot: Bot
};

export default function ModelConfigsPage() {
  const [configs, setConfigs] = useState<ModelConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [currentConfig, setCurrentConfig] = useState<
    Partial<ModelConfigInput & { id?: number }>
  >({});
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const data = await getModelConfigs();
      setConfigs(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('获取模型配置失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpen = (config?: ModelConfig) => {
    if (config) {
      setCurrentConfig({
        id: config.id,
        name: config.name,
        model_id: config.model_id,
        description: config.description,
        provider: config.provider,
        icon: config.icon,
        icon_color: config.icon_color,
        max_tokens: config.max_tokens,
        api_base_url: config.api_base_url,
        api_key: config.api_key,
        api_key_env: config.api_key_env,
        is_active: config.is_active,
        sort_order: config.sort_order
      });
      setIsEditing(true);
    } else {
      setCurrentConfig({
        is_active: true,
        provider: 'siliconflow',
        icon: 'sparkles',
        icon_color: 'text-blue-500',
        max_tokens: 4096,
        sort_order: 0,
        api_base_url: 'https://api.siliconflow.cn/v1'
      });
      setIsEditing(false);
    }
    setOpen(true);
  };

  const handleSave = async () => {
    if (!currentConfig.name || !currentConfig.model_id) {
      alert('请填写模型名称和模型标识');
      return;
    }

    setSaving(true);
    try {
      const payload: ModelConfigInput = {
        name: currentConfig.name!,
        model_id: currentConfig.model_id!,
        description: currentConfig.description || '',
        provider: currentConfig.provider || 'siliconflow',
        icon: currentConfig.icon || 'sparkles',
        icon_color: currentConfig.icon_color || 'text-blue-500',
        max_tokens: currentConfig.max_tokens || 4096,
        api_base_url: currentConfig.api_base_url || '',
        api_key: currentConfig.api_key || '',
        api_key_env: currentConfig.api_key_env || '',
        is_active: currentConfig.is_active ?? true,
        sort_order: currentConfig.sort_order || 0
      };

      if (isEditing && currentConfig.id) {
        await updateModelConfig(currentConfig.id, payload);
      } else {
        await createModelConfig(payload);
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
    if (!confirm('确认删除该模型配置吗？')) return;
    try {
      await deleteModelConfig(id);
      fetchData();
    } catch (error) {
      console.error('删除失败:', error);
      alert('删除失败');
    }
  };

  const getProviderLabel = (value: string) => {
    return PROVIDER_OPTIONS.find((p) => p.value === value)?.label || value;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">模型配置</h2>
          <p className="text-muted-foreground">管理对话广场中可用的 AI 模型</p>
        </div>
        <Button onClick={() => handleOpen()}>
          <Plus className="mr-2 h-4 w-4" /> 新增模型
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">图标</TableHead>
              <TableHead>模型名称</TableHead>
              <TableHead>模型标识</TableHead>
              <TableHead>供应商</TableHead>
              <TableHead>Max Tokens</TableHead>
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
            ) : configs.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={8}
                  className="h-24 text-center text-muted-foreground"
                >
                  暂无模型配置，点击右上角按钮添加
                </TableCell>
              </TableRow>
            ) : (
              configs.map((config) => {
                const IconComponent = IconMap[config.icon] || Sparkles;
                return (
                  <TableRow key={config.id}>
                    <TableCell>
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-muted">
                        <IconComponent
                          className={`h-4 w-4 ${config.icon_color}`}
                        />
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">{config.name}</TableCell>
                    <TableCell>
                      <code className="rounded bg-muted px-1.5 py-0.5 text-sm">
                        {config.model_id}
                      </code>
                    </TableCell>
                    <TableCell>
                      <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                        {getProviderLabel(config.provider)}
                      </span>
                    </TableCell>
                    <TableCell>{config.max_tokens.toLocaleString()}</TableCell>
                    <TableCell>{config.sort_order}</TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                          config.is_active
                            ? 'bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20'
                            : 'bg-red-50 text-red-700 ring-1 ring-inset ring-red-600/20'
                        }`}
                      >
                        {config.is_active ? '启用' : '禁用'}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleOpen(config)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-red-500 hover:text-red-600"
                        onClick={() => handleDelete(config.id)}
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

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{isEditing ? '编辑模型' : '新增模型'}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            {/* 基本信息 */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">模型名称 *</Label>
                <Input
                  id="name"
                  placeholder="如: GPT-4o"
                  value={currentConfig.name || ''}
                  onChange={(e) =>
                    setCurrentConfig({ ...currentConfig, name: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="model_id">模型标识 *</Label>
                <Input
                  id="model_id"
                  placeholder="如: gpt-4o"
                  value={currentConfig.model_id || ''}
                  onChange={(e) =>
                    setCurrentConfig({
                      ...currentConfig,
                      model_id: e.target.value
                    })
                  }
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">模型描述</Label>
              <Input
                id="description"
                placeholder="如: 最强大的多模态模型"
                value={currentConfig.description || ''}
                onChange={(e) =>
                  setCurrentConfig({
                    ...currentConfig,
                    description: e.target.value
                  })
                }
              />
            </div>

            {/* 供应商和显示配置 */}
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="provider">供应商</Label>
                <select
                  id="provider"
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  value={currentConfig.provider || 'siliconflow'}
                  onChange={(e) =>
                    setCurrentConfig({
                      ...currentConfig,
                      provider: e.target.value
                    })
                  }
                >
                  {PROVIDER_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="icon">图标</Label>
                <select
                  id="icon"
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  value={currentConfig.icon || 'sparkles'}
                  onChange={(e) =>
                    setCurrentConfig({ ...currentConfig, icon: e.target.value })
                  }
                >
                  {ICON_OPTIONS.map((opt) => (
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
                  value={currentConfig.icon_color || 'text-blue-500'}
                  onChange={(e) =>
                    setCurrentConfig({
                      ...currentConfig,
                      icon_color: e.target.value
                    })
                  }
                >
                  {ICON_COLOR_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* API 配置 */}
            <div className="space-y-2">
              <Label htmlFor="api_base_url">API Base URL</Label>
              <Input
                id="api_base_url"
                placeholder="如: https://api.siliconflow.cn/v1"
                value={currentConfig.api_base_url || ''}
                onChange={(e) =>
                  setCurrentConfig({
                    ...currentConfig,
                    api_base_url: e.target.value
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="api_key">API Key (直接填写，优先级高)</Label>
              <Input
                id="api_key"
                type="password"
                placeholder="sk-xxxxxxxx"
                value={currentConfig.api_key || ''}
                onChange={(e) =>
                  setCurrentConfig({
                    ...currentConfig,
                    api_key: e.target.value
                  })
                }
              />
              <p className="text-xs text-muted-foreground">
                直接填写 API Key，或留空使用下方环境变量
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="api_key_env">API Key 环境变量名 (备选)</Label>
              <Input
                id="api_key_env"
                placeholder="如: SILICONFLOW_API_KEY"
                value={currentConfig.api_key_env || ''}
                onChange={(e) =>
                  setCurrentConfig({
                    ...currentConfig,
                    api_key_env: e.target.value
                  })
                }
              />
              <p className="text-xs text-muted-foreground">
                当上方 API Key 为空时，从此环境变量读取
              </p>
            </div>

            {/* 其他配置 */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="max_tokens">Max Tokens</Label>
                <Input
                  id="max_tokens"
                  type="number"
                  value={currentConfig.max_tokens || 4096}
                  onChange={(e) =>
                    setCurrentConfig({
                      ...currentConfig,
                      max_tokens: parseInt(e.target.value) || 4096
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="sort_order">排序 (越小越靠前)</Label>
                <Input
                  id="sort_order"
                  type="number"
                  value={currentConfig.sort_order || 0}
                  onChange={(e) =>
                    setCurrentConfig({
                      ...currentConfig,
                      sort_order: parseInt(e.target.value) || 0
                    })
                  }
                />
              </div>
            </div>

            {/* 状态 */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="is_active"
                checked={currentConfig.is_active ?? true}
                onCheckedChange={(checked) =>
                  setCurrentConfig({
                    ...currentConfig,
                    is_active: checked as boolean
                  })
                }
              />
              <label htmlFor="is_active" className="text-sm">
                启用该模型
              </label>
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
