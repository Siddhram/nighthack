import React, { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  BriefcaseIcon, 
  DocumentTextIcon, 
  ChartBarIcon,
  CloudArrowUpIcon 
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';

interface LayoutProps {
  children: ReactNode;
}

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Jobs', href: '/jobs', icon: BriefcaseIcon },
  { name: 'Resumes', href: '/resumes', icon: DocumentTextIcon },
  { name: 'Evaluations', href: '/evaluations', icon: ChartBarIcon },
  { name: 'Upload Resume', href: '/upload', icon: CloudArrowUpIcon },
];

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
        <div className="flex h-16 shrink-0 items-center px-6 border-b border-secondary-200">
          <div className="flex items-center">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600">
              <ChartBarIcon className="h-5 w-5 text-white" />
            </div>
            <div className="ml-3">
              <h1 className="text-lg font-semibold text-secondary-900">
                Resume AI
              </h1>
              <p className="text-xs text-secondary-500">Relevance System</p>
            </div>
          </div>
        </div>
        
        <nav className="flex flex-1 flex-col px-4 py-4">
          <ul role="list" className="flex flex-1 flex-col gap-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <li key={item.name}>
                  <Link
                    to={item.href}
                    className={clsx(
                      isActive
                        ? 'bg-primary-50 border-primary-200 text-primary-700'
                        : 'text-secondary-700 hover:text-primary-700 hover:bg-secondary-50',
                      'group flex gap-x-3 rounded-md p-3 text-sm leading-6 font-medium border border-transparent hover:border-secondary-200 transition-colors'
                    )}
                  >
                    <item.icon
                      className={clsx(
                        isActive ? 'text-primary-600' : 'text-secondary-400 group-hover:text-primary-600',
                        'h-5 w-5 shrink-0'
                      )}
                    />
                    {item.name}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>

      {/* Main content */}
      <div className="pl-64">
        <main className="py-8">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}