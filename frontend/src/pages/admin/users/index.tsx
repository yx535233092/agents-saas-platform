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
import { userService } from '@/services/users';
import { roleService } from '@/services/roles';
import { type User } from '@/types/user';
import { type Role } from '@/types/role';
import { Checkbox } from '@/components/ui/checkbox';
import { Plus, Pencil, Trash2, Loader2 } from 'lucide-react';

export default function UserPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<Partial<User> & { password?: string; role_id?: number }>({});
  const [isEditing, setIsEditing] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [usersData, rolesData] = await Promise.all([
        userService.list(),
        roleService.list()
      ]);
      setUsers(Array.isArray(usersData) ? usersData : usersData.results || []);
      setRoles(Array.isArray(rolesData) ? rolesData : rolesData.results || []);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpen = (user?: User) => {
    if (user) {
      setCurrentUser({ ...user, password: '', role_id: user.role_id }); // Don't show password
      setIsEditing(true);
    } else {
      setCurrentUser({ is_active: true, role_id: 1 }); // 默认角色ID为1
      setIsEditing(false);
    }
    setOpen(true);
  };

  const handleSave = async () => {
    try {
      if (isEditing && currentUser.id) {
        // 更新用户信息
        const updateData: any = {};
        if (currentUser.username !== undefined) updateData.username = currentUser.username;
        if (currentUser.password) updateData.password = currentUser.password;
        if (currentUser.is_active !== undefined) updateData.is_active = currentUser.is_active;
        if (currentUser.role_id !== undefined) updateData.role_id = currentUser.role_id;
        
        await userService.update(currentUser.id, updateData);
      } else {
        // 创建用户
        if (!currentUser.username || !currentUser.password) {
          alert('请填写用户名和密码');
          return;
        }
        await userService.create({
          username: currentUser.username,
          password: currentUser.password,
          role_id: currentUser.role_id || 1
        });
      }
      setOpen(false);
      fetchData();
    } catch (error: any) {
      console.error(error);
      const errorMsg = error?.response?.data?.detail || '保存失败';
      alert(errorMsg);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确认删除该用户吗？')) return;
    try {
      await userService.delete(id);
      fetchData();
    } catch (error) {
      console.error(error);
      alert('删除失败');
    }
  };

  const handleRoleChange = (roleId: number) => {
    setCurrentUser({
      ...currentUser,
      role_id: roleId
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">用户管理</h2>
        <Button onClick={() => handleOpen()}>
          <Plus className="mr-2 h-4 w-4" /> 新增用户
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>用户名</TableHead>
              <TableHead>角色</TableHead>
              <TableHead>状态</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={4} className="h-24 text-center">
                  <Loader2 className="mx-auto h-6 w-6 animate-spin" />
                </TableCell>
              </TableRow>
            ) : (
              users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.username}</TableCell>
                  <TableCell>
                    {user.role_id ? (
                      <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                        {roles.find(r => r.id === user.role_id)?.name || `角色ID: ${user.role_id}`}
                      </span>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell>
                    <span
                      className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                        user.is_active
                          ? 'bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20'
                          : 'bg-red-50 text-red-700 ring-1 ring-inset ring-red-600/20'
                      }`}
                    >
                      {user.is_active ? '启用' : '禁用'}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleOpen(user)}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-red-500 hover:text-red-600"
                      onClick={() => handleDelete(user.id)}
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

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{isEditing ? '编辑用户' : '新增用户'}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="username" className="text-right">
                用户名
              </Label>
              <Input
                id="username"
                value={currentUser.username || ''}
                onChange={(e) =>
                  setCurrentUser({ ...currentUser, username: e.target.value })
                }
                className="col-span-3"
                disabled={isEditing}
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="password" className="text-right">
                密码
              </Label>
              <Input
                id="password"
                type="password"
                placeholder={isEditing ? '不修改请留空' : ''}
                value={currentUser.password || ''}
                onChange={(e) =>
                  setCurrentUser({ ...currentUser, password: e.target.value })
                }
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="role" className="text-right">
                角色
              </Label>
              <select
                id="role"
                value={currentUser.role_id || 1}
                onChange={(e) => handleRoleChange(Number(e.target.value))}
                className="col-span-3 flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                {roles.map((role) => (
                  <option key={role.id} value={role.id}>
                    {role.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="active" className="text-right">
                状态
              </Label>
              <div className="col-span-3 flex items-center space-x-2">
                <Checkbox
                  id="active"
                  checked={currentUser.is_active}
                  onCheckedChange={(checked) =>
                    setCurrentUser({
                      ...currentUser,
                      is_active: checked as boolean
                    })
                  }
                />
                <label htmlFor="active" className="text-sm">
                  启用账户
                </label>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSave}>保存</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
