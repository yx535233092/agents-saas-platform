import { Outlet } from 'react-router-dom';

export const LoginLayout = () => {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-muted/40 p-4">
      <div className="w-full max-w-sm lg:max-w-4xl">
        <Outlet />
      </div>
    </div>
  );
};

