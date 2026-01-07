import { Link, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { FolderOpen, Search, Settings, Plus, TrendingUp, LogOut } from 'lucide-react';
import { clsx } from 'clsx';
import { foldersApi } from '../../api/folders';
import { useAuth } from '../../context/AuthContext';

export function Sidebar() {
  const location = useLocation();
  const { logout } = useAuth();

  const { data: foldersData } = useQuery({
    queryKey: ['folders'],
    queryFn: () => foldersApi.list(),
  });

  const navItems = [
    { path: '/folders', icon: FolderOpen, label: 'Folders' },
    { path: '/search', icon: Search, label: 'Search' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  const handleLogout = async () => {
    await logout();
  };

  return (
    <aside className="flex h-full w-64 flex-col border-r border-gray-200 bg-white">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-4">
        <TrendingUp className="h-8 w-8 text-primary-600" />
        <span className="ml-2 text-lg font-bold text-gray-900">Investment RMS</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <ul className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);

            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={clsx(
                    'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium',
                    isActive
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>

        {/* Folders list */}
        <div className="mt-6">
          <div className="flex items-center justify-between px-3 py-2">
            <span className="text-xs font-semibold uppercase text-gray-500">
              Folders
            </span>
            <Link
              to="/folders/new"
              className="rounded p-1 hover:bg-gray-100"
              title="New Folder"
            >
              <Plus className="h-4 w-4 text-gray-500" />
            </Link>
          </div>

          <ul className="mt-1 space-y-1">
            {foldersData?.folders.map((folder) => {
              const isActive = location.pathname === `/folders/${folder.id}`;

              return (
                <li key={folder.id}>
                  <Link
                    to={`/folders/${folder.id}`}
                    className={clsx(
                      'flex items-center gap-2 rounded-md px-3 py-2 text-sm',
                      isActive
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    )}
                  >
                    <span className="truncate">{folder.name}</span>
                    {folder.active_idea_count > 0 && (
                      <span className="ml-auto flex h-5 min-w-[20px] items-center justify-center rounded-full bg-primary-100 px-1.5 text-xs font-medium text-primary-700">
                        {folder.active_idea_count}
                      </span>
                    )}
                  </Link>
                </li>
              );
            })}

            {(!foldersData?.folders || foldersData.folders.length === 0) && (
              <li className="px-3 py-2 text-sm text-gray-500">
                No folders yet
              </li>
            )}
          </ul>
        </div>
      </nav>

      {/* Footer */}
      <div className="border-t p-4">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-gray-600 hover:bg-gray-100"
        >
          <LogOut className="h-5 w-5" />
          Logout
        </button>
      </div>
    </aside>
  );
}
