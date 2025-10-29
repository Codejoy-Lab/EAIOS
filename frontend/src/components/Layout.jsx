import React from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'

const Layout = () => {
  const location = useLocation()

  const pages = [
    { path: '/', label: '介绍', id: 'intro' },
    { path: '/s1-marketing', label: 'S1 全域营销', id: 's1' },
    { path: '/s2-sales', label: 'S2 智能销售', id: 's2' },
    { path: '/s3-customer-service', label: 'S3 智能客服', id: 's3' },
    { path: '/s4-content', label: 'S4 内容生产', id: 's4' },
    { path: '/s5-process', label: 'S5 流程优化', id: 's5' },
    { path: '/s6-analytics', label: 'S6 数据分析', id: 's6' },
    { path: '/s7-compliance', label: 'S7 风控合规', id: 's7' },
    { path: '/s8-decision', label: 'S8 决策军师', id: 's8' },
    { path: '/closing', label: '总结', id: 'closing' },
  ]

  return (
    <div className="min-h-screen bg-slate-900 text-gray-100">
      {/* 顶部导航栏 */}
      <nav className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex-shrink-0">
              <Link to="/" className="text-xl font-bold text-primary-500">
                EAIOS
              </Link>
              <span className="ml-2 text-sm text-gray-400">
                企业级Agent演示平台
              </span>
            </div>

            {/* 页面导航 */}
            <div className="flex space-x-2 overflow-x-auto">
              {pages.map((page) => (
                <Link
                  key={page.id}
                  to={page.path}
                  className={`px-3 py-2 rounded-md text-sm font-medium whitespace-nowrap transition-colors ${
                    location.pathname === page.path
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-300 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  {page.label}
                </Link>
              ))}
            </div>

            {/* 记忆管理入口 */}
            <div>
              <Link
                to="/memory"
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === '/memory'
                    ? 'bg-accent-600 text-white'
                    : 'bg-slate-700 text-gray-300 hover:bg-accent-500 hover:text-white'
                }`}
              >
                记忆管理
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* 页面导航提示 */}
      <div className="fixed bottom-4 right-4 bg-slate-800 rounded-lg p-3 shadow-lg border border-slate-700">
        <div className="text-xs text-gray-400">
          当前页面: {pages.find(p => p.path === location.pathname)?.label || '未知'}
        </div>
        <div className="text-xs text-gray-500 mt-1">
          共 {pages.length} 页
        </div>
      </div>
    </div>
  )
}

export default Layout
