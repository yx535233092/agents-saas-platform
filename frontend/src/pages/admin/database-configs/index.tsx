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
  Play,
  AlertCircle,
  Database
} from 'lucide-react';
import { databaseConfigService } from '@/services/database-configs';
import type { DatabaseConfig, DatabaseConfigInput } from '@/types/database-config';
import { DB_TYPE_OPTIONS } from '@/types/database-config';

export default function DatabaseConfigsPage() {
  const [configs, setConfigs] = useState<DatabaseConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [currentConfig, setCurrentConfig] = useState<
    Partial<DatabaseConfigInput & { id?: number }>
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
      const data = await databaseConfigService.list();
      setConfigs(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('获取数据库配置列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpen = (config?: DatabaseConfig) => {
    if (config) {
      setCurrentConfig({
        id: config.id,
        name: config.name,
        description: config.description,
        db_type: config.db_type,
        host: config.host,
        port: config.port,
        database: config.database,
        username: config.username,
        password: '', // 不显示密码
        connection_string: config.connection_string,
        extra_params: config.extra_params,
        is_active: config.is_active,
        is_default: config.is_default,
        sort_order: config.sort_order
      });
      setIsEditing(true);
    } else {
      setCurrentConfig({
        db_type: 'sqlite',
        is_active: true,
        is_default: false,
        sort_order: 0
      });
      setIsEditing(false);
    }
    setOpen(true);
    setTestResult(null);
  };

  const handleSave = async () => {
    if (!currentConfig.name || !currentConfig.db_type) {
      alert('请填写必填字段');
      return;
    }

    setSaving(true);
    try {
      if (isEditing && currentConfig.id) {
        await databaseConfigService.update(currentConfig.id, currentConfig);
      } else {
        await databaseConfigService.create(currentConfig as DatabaseConfigInput);
      }
      setOpen(false);
      fetchData();
    } catch (error) {
      console.error('保存失败:', error);
      alert(error instanceof Error ? error.message : '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定要删除这个数据库配置吗？')) {
      return;
    }

    try {
      await databaseConfigService.delete(id);
      fetchData();
    } catch (error) {
      console.error('删除失败:', error);
      alert(error instanceof Error ? error.message : '删除失败');
    }
  };

  const handleTest = async (id: number) => {
    setTesting(id);
    setTestResult(null);
    try {
      const result = await databaseConfigService.testConnection(id);
      setTestResult({
        success: result.success,
        message: result.message
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: error instanceof Error ? error.message : '测试失败'
      });
    } finally {
      setTesting(null);
    }
  };

  const handleTestDirect = async () => {
    if (!currentConfig.name || !currentConfig.db_type) {
      alert('请先填写配置信息');
      return;
    }

    setTesting(-1);
    setTestResult(null);
    try {
      const result = await databaseConfigService.testConnectionDirect(
        currentConfig as DatabaseConfigInput
      );
      setTestResult({
        success: result.success,
        message: result.message
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: error instanceof Error ? error.message : '测试失败'
      });
    } finally {
      setTesting(null);
    }
  };

  const getDbTypeLabel = (value: string) => {
    return DB_TYPE_OPTIONS.find((p) => p.value === value)?.label || value;
  };

  const showConnectionString = currentConfig.db_type === 'sqlite';
  const showHostPort = currentConfig.db_type !== 'sqlite';

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">数据库管理</h2>
          <p className="text-muted-foreground">
            管理数据库连接配置，支持 SQLite、PostgreSQL、MySQL、MSSQL 等数据库
          </p>
        </div>
        <Button onClick={() => handleOpen()}>
          <Plus className="mr-2 h-4 w-4" /> 新增配置
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>配置名称</TableHead>
              <TableHead>数据库类型</TableHead>
              <TableHead>连接信息</TableHead>
              <TableHead>排序</TableHead>
              <TableHead>状态</TableHead>
              <TableHead>默认</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center">
                  <Loader2 className="mx-auto h-6 w-6 animate-spin" />
                </TableCell>
              </TableRow>
            ) : configs.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={7}
                  className="h-24 text-center text-muted-foreground"
                >
                  暂无数据库配置，点击右上角按钮添加
                </TableCell>
              </TableRow>
            ) : (
              configs.map((config) => (
                <TableRow key={config.id}>
                  <TableCell className="font-medium">{config.name}</TableCell>
                  <TableCell>
                    <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                      {getDbTypeLabel(config.db_type)}
                    </span>
                  </TableCell>
                  <TableCell>
                    <code className="rounded bg-muted px-1.5 py-0.5 text-sm">
                      {config.db_type === 'sqlite'
                        ? config.database || config.connection_string || 'N/A'
                        : `${config.host || 'N/A'}:${config.port || 'N/A'}/${config.database || 'N/A'}`}
                    </code>
                  </TableCell>
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
                  <TableCell>
                    {config.is_default && (
                      <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-600/20">
                        默认
                      </span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleTest(config.id)}
                      disabled={testing === config.id}
                      title="测试连接"
                    >
                      {testing === config.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                    </Button>
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
              ))
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
              {isEditing ? '编辑数据库配置' : '新增数据库配置'}
            </DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            {/* 基本信息 */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">配置名称 *</Label>
                <Input
                  id="name"
                  placeholder="如: 本地测试数据库"
                  value={currentConfig.name || ''}
                  onChange={(e) =>
                    setCurrentConfig({ ...currentConfig, name: e.target.value })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="db_type">数据库类型 *</Label>
                <select
                  id="db_type"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  value={currentConfig.db_type || 'sqlite'}
                  onChange={(e) =>
                    setCurrentConfig({
                      ...currentConfig,
                      db_type: e.target.value as any
                    })
                  }
                >
                  {DB_TYPE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">配置描述</Label>
              <Textarea
                id="description"
                placeholder="可选：描述此数据库配置的用途"
                value={currentConfig.description || ''}
                onChange={(e) =>
                  setCurrentConfig({
                    ...currentConfig,
                    description: e.target.value
                  })
                }
              />
            </div>

            {/* SQLite 配置 */}
            {showConnectionString && (
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="database">数据库文件路径</Label>
                  <Input
                    id="database"
                    placeholder="如: /path/to/database.db 或 ./data.db"
                    value={currentConfig.database || ''}
                    onChange={(e) =>
                      setCurrentConfig({
                        ...currentConfig,
                        database: e.target.value
                      })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="connection_string">或连接字符串</Label>
                  <Input
                    id="connection_string"
                    placeholder="完整的连接字符串（可选）"
                    value={currentConfig.connection_string || ''}
                    onChange={(e) =>
                      setCurrentConfig({
                        ...currentConfig,
                        connection_string: e.target.value
                      })
                    }
                  />
                </div>
              </div>
            )}

            {/* 其他数据库类型配置 */}
            {showHostPort && (
              <>
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="host">主机地址 *</Label>
                    <Input
                      id="host"
                      placeholder="如: localhost 或 192.168.1.100"
                      value={currentConfig.host || ''}
                      onChange={(e) =>
                        setCurrentConfig({
                          ...currentConfig,
                          host: e.target.value
                        })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="port">端口 *</Label>
                    <Input
                      id="port"
                      type="number"
                      placeholder={
                        currentConfig.db_type === 'postgresql'
                          ? '5432'
                          : currentConfig.db_type === 'mysql'
                          ? '3306'
                          : '1433'
                      }
                      value={currentConfig.port || ''}
                      onChange={(e) =>
                        setCurrentConfig({
                          ...currentConfig,
                          port: e.target.value ? parseInt(e.target.value) : undefined
                        })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="database">数据库名 *</Label>
                    <Input
                      id="database"
                      placeholder="数据库名称"
                      value={currentConfig.database || ''}
                      onChange={(e) =>
                        setCurrentConfig({
                          ...currentConfig,
                          database: e.target.value
                        })
                      }
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">用户名</Label>
                    <Input
                      id="username"
                      placeholder="数据库用户名"
                      value={currentConfig.username || ''}
                      onChange={(e) =>
                        setCurrentConfig({
                          ...currentConfig,
                          username: e.target.value
                        })
                      }
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">密码</Label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="数据库密码"
                      value={currentConfig.password || ''}
                      onChange={(e) =>
                        setCurrentConfig({
                          ...currentConfig,
                          password: e.target.value
                        })
                      }
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="connection_string">连接字符串（可选）</Label>
                  <Input
                    id="connection_string"
                    placeholder="完整的连接字符串，如果提供则忽略上面的单独字段"
                    value={currentConfig.connection_string || ''}
                    onChange={(e) =>
                      setCurrentConfig({
                        ...currentConfig,
                        connection_string: e.target.value
                      })
                    }
                  />
                </div>
              </>
            )}

            {/* 其他选项 */}
            <div className="grid grid-cols-3 gap-4">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_active"
                  checked={currentConfig.is_active || false}
                  onCheckedChange={(checked) =>
                    setCurrentConfig({
                      ...currentConfig,
                      is_active: checked as boolean
                    })
                  }
                />
                <Label htmlFor="is_active" className="cursor-pointer">
                  启用
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_default"
                  checked={currentConfig.is_default || false}
                  onCheckedChange={(checked) =>
                    setCurrentConfig({
                      ...currentConfig,
                      is_default: checked as boolean
                    })
                  }
                />
                <Label htmlFor="is_default" className="cursor-pointer">
                  设为默认
                </Label>
              </div>
              <div className="space-y-2">
                <Label htmlFor="sort_order">排序</Label>
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

          <DialogFooter>
            <Button
              variant="outline"
              onClick={handleTestDirect}
              disabled={testing === -1}
            >
              {testing === -1 ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  测试中...
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  测试连接
                </>
              )}
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  保存中...
                </>
              ) : (
                '保存'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

