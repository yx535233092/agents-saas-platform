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
  const [currentUser, setCurrentUser] = useState<Partial<User> & { password?: string }>({});
  const [isEditing, setIsEditing] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [usersData, rolesData] = await Promise.all([
        userService.list(),
        roleService.list()
      ]);
      setUsers(Array.isArray(usersData) ? usersData : usersData.results);
      setRoles(Array.isArray(rolesData) ? rolesData : rolesData.results);
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
      setCurrentUser({ ...user, password: '' }); // Don't show password
      setIsEditing(true);
    } else {
      setCurrentUser({ is_active: true, role_ids: [] });
      setIsEditing(false);
    }
    setOpen(true);
  };

  const handleSave = async () => {
    try {
      if (isEditing && currentUser.id) {
        await userService.update(currentUser.id, currentUser);
      } else {
        await userService.create(currentUser);
      }
      setOpen(false);
      fetchData();
    } catch (error) {
      console.error(error);
      alert('保存失败');
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

  const toggleRole = (roleId: number) => {
    const currentRoles = currentUser.role_ids || [];
    if (currentRoles.includes(roleId)) {
      setCurrentUser({
        ...currentUser,
        role_ids: currentRoles.filter((id) => id !== roleId)
      });
    } else {
      setCurrentUser({
        ...currentUser,
        role_ids: [...currentRoles, roleId]
      });
    }
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
              <TableHead>邮箱</TableHead>
              <TableHead>角色</TableHead>
              <TableHead>状态</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center">
                  <Loader2 className="mx-auto h-6 w-6 animate-spin" />
                </TableCell>
              </TableRow>
            ) : (
              users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.username}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {user.roles.map((role) => (
                        <span
                          key={role}
                          className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary"
                        >
                          {role}
                        </span>
                      ))}
                    </div>
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
              <Label htmlFor="email" className="text-right">
                邮箱
              </Label>
              <Input
                id="email"
                type="email"
                value={currentUser.email || ''}
                onChange={(e) =>
                  setCurrentUser({ ...currentUser, email: e.target.value })
                }
                className="col-span-3"
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
            <div className="grid grid-cols-4 items-start gap-4">
              <Label className="mt-2 text-right">角色</Label>
              <div className="col-span-3 grid grid-cols-2 gap-2">
                {roles.map((role) => (
                  <div key={role.id} className="flex items-center space-x-2">
                    <Checkbox
                      id={`role-${role.id}`}
                      checked={(currentUser.role_ids || []).includes(role.id)}
                      onCheckedChange={() => toggleRole(role.id)}
                    />
                    <label
                      htmlFor={`role-${role.id}`}
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      {role.name}
                    </label>
                  </div>
                ))}
              </div>
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
