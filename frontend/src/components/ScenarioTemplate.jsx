import React, { useState } from 'react'

/**
 * 场景页面通用模板
 * 用于8个场景页面的基础结构
 */
const ScenarioTemplate = ({
  scenarioId,
  title,
  description,
  highlight,
  children
}) => {
  const [mode, setMode] = useState('demo') // demo | real
  const [dataMode, setDataMode] = useState('builtin') // builtin | manual
  const [roleMode, setRoleMode] = useState('authorized') // authorized | unauthorized

  return (
    <div className="space-y-6">
      {/* 场景标题 */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-bold text-gray-100">{title}</h1>
          <span className={`px-3 py-1 rounded-lg text-sm font-medium ${
            highlight === '主动式'
              ? 'bg-accent-500/20 text-accent-400 border border-accent-500/30'
              : 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
          }`}>
            主打: {highlight}
          </span>
        </div>
        <p className="text-gray-400">{description}</p>
      </div>

      {/* 顶部控制区 */}
      <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
        <div className="grid grid-cols-4 gap-4">
          {/* 数据模式 */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              数据模式
            </label>
            <select
              value={dataMode}
              onChange={(e) => setDataMode(e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-sm text-gray-200"
            >
              <option value="builtin">内置数据</option>
              <option value="manual">现场输入</option>
            </select>
          </div>

          {/* 触发方式 */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              触发方式
            </label>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-sm text-gray-200"
            >
              <option value="demo">演示触发</option>
              <option value="real">真实触发</option>
            </select>
          </div>

          {/* 角色切换 */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              权限角色
            </label>
            <select
              value={roleMode}
              onChange={(e) => setRoleMode(e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-sm text-gray-200"
            >
              <option value="authorized">有权限</option>
              <option value="unauthorized">无权限</option>
            </select>
          </div>

          {/* 开始按钮 */}
          <div className="flex items-end">
            <button className="w-full bg-gradient-to-r from-primary-500 to-accent-500 hover:from-primary-600 hover:to-accent-600 text-white font-semibold py-2 px-4 rounded transition-all">
              开始演示
            </button>
          </div>
        </div>
      </div>

      {/* 主内容区 - 由子组件定义 */}
      {children}

      {/* 底部三分屏对比（占位） */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-200">对比展示</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-slate-700 rounded-lg p-4">
            <h4 className="font-medium mb-2 text-gray-300">左: 无AI</h4>
            <p className="text-sm text-gray-400">人工处理方式...</p>
          </div>
          <div className="bg-slate-700 rounded-lg p-4">
            <h4 className="font-medium mb-2 text-gray-300">中: 常见AI</h4>
            <p className="text-sm text-gray-400">通用AI方案...</p>
          </div>
          <div className="bg-slate-700 rounded-lg p-4 border-2 border-primary-500">
            <h4 className="font-medium mb-2 text-primary-400">右: 本方案</h4>
            <p className="text-sm text-gray-400">企业级AI方案...</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ScenarioTemplate
