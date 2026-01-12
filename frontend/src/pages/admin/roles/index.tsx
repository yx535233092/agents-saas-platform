import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { roleService } from '@/services/roles';
import { type Role, type Permission } from '@/types/role';
import { Checkbox } from '@/components/ui/checkbox';
import { Plus, Pencil, Trash2, Loader2 } from 'lucide-react';

export default function RolePage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [currentRole, setCurrentRole] = useState<Partial<Role>>({});
  const [isEditing, setIsEditing] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [rolesData, permissionsData] = await Promise.all([
        roleService.list(),
        roleService.listPermissions(),
      ]);
      setRoles(Array.isArray(rolesData) ? rolesData : rolesData.results);
      setPermissions(Array.isArray(permissionsData) ? permissionsData : permissionsData.results);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpen = (role?: Role) => {
    if (role) {
      setCurrentRole({ ...role });
      setIsEditing(true);
    } else {
      setCurrentRole({ permission_ids: [] });
      setIsEditing(false);
    }
    setOpen(true);
  };

  const handleSave = async () => {
    try {
      if (isEditing && currentRole.id) {
        await roleService.update(currentRole.id, currentRole);
      } else {
        await roleService.create(currentRole);
      }
      setOpen(false);
      fetchData();
    } catch (error) {
      console.error(error);
      alert('保存失败');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确认删除该角色吗？')) return;
    try {
      await roleService.delete(id);
      fetchData();
    } catch (error) {
      console.error(error);
      alert('删除失败');
    }
  };

  const togglePermission = (permId: number) => {
    const currentPerms = currentRole.permission_ids || [];
    if (currentPerms.includes(permId)) {
      setCurrentRole({
        ...currentRole,
        permission_ids: currentPerms.filter((id) => id !== permId),
      });
    } else {
      setCurrentRole({
        ...currentRole,
        permission_ids: [...currentPerms, permId],
      });
    }
  };

  // Group permissions by content_type (simplified grouping)
  // For better UI, we might want to fetch content types names, but for now just list all
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">角色管理</h2>
        <Button onClick={() => handleOpen()}>
          <Plus className="mr-2 h-4 w-4" /> 新增角色
        </Button>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>角色名称</TableHead>
              <TableHead>权限数量</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={3} className="h-24 text-center">
                  <Loader2 className="mx-auto h-6 w-6 animate-spin" />
                </TableCell>
              </TableRow>
            ) : (
              roles.map((role) => (
                <TableRow key={role.id}>
                  <TableCell>{role.name}</TableCell>
                  <TableCell>{role.permissions?.length || 0}</TableCell>
                  <TableCell className="text-right">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleOpen(role)}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-red-500 hover:text-red-600"
                      onClick={() => handleDelete(role.id)}
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
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{isEditing ? '编辑角色' : '新增角色'}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                角色名称
              </Label>
              <Input
                id="name"
                value={currentRole.name || ''}
                onChange={(e) =>
                  setCurrentRole({ ...currentRole, name: e.target.value })
                }
                className="col-span-3"
              />
            </div>
            
            <div className="grid grid-cols-4 items-start gap-4">
              <Label className="mt-2 text-right">权限</Label>
              <div className="col-span-3 h-[300px] overflow-y-auto rounded-md border p-4">
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                  {permissions.map((perm) => (
                    <div key={perm.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={`perm-${perm.id}`}
                        checked={(currentRole.permission_ids || []).includes(
                          perm.id
                        )}
                        onCheckedChange={() => togglePermission(perm.id)}
                      />
                      <label
                        htmlFor={`perm-${perm.id}`}
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                        title={perm.codename}
                      >
                        {perm.name} ({perm.codename})
                      </label>
                    </div>
                  ))}
                </div>
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

