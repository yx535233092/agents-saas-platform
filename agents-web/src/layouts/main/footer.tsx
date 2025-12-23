import { Command } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t bg-muted/40 py-12">
      <div className="container mx-auto px-4 md:px-6">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          <div className="flex flex-col space-y-4">
            <div className="flex items-center space-x-2">
              <Command className="h-6 w-6" />
              <span className="font-bold">ASP</span>
            </div>
            <p className="text-sm text-muted-foreground">
              为企业打造的下一代智能体 SaaS 平台，让 AI 驱动您的业务增长。
            </p>
          </div>

          <div>
            <h3 className="mb-4 text-sm font-semibold">产品</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <a href="#" className="hover:text-foreground">
                  功能特性
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-foreground">
                  定价方案
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-foreground">
                  更新日志
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-foreground">
                  路线图
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="mb-4 text-sm font-semibold">资源</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <a href="#" className="hover:text-foreground">
                  开发文档
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-foreground">
                  API 参考
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-foreground">
                  社区论坛
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-foreground">
                  帮助中心
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="mb-4 text-sm font-semibold">公司</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <a href="#" className="hover:text-foreground">
                  关于我们
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-foreground">
                  加入我们
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-foreground">
                  法律条款
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-foreground">
                  联系方式
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t pt-8 md:flex-row">
          <p className="text-sm text-muted-foreground">
            © 2024 Agents SaaS Platform. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
