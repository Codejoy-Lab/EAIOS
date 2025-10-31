import React, { useState, useEffect } from 'react'
import axios from 'axios'

/**
 * 业务事项看板组件
 * 展示企业重要事项、待办、跟进任务等
 */
const BusinessItemsBoard = () => {
  const [items, setItems] = useState([])
  const [stats, setStats] = useState(null)
  const [filter, setFilter] = useState({ status: 'all', priority: 'all', type: 'all' })
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newItem, setNewItem] = useState({
    title: '',
    description: '',
    type: 'todo',
    priority: 'medium'
  })

  // 类型配置
  const typeConfig = {
    decision: { label: '决策', icon: '📊', color: 'bg-purple-500/20 text-purple-300' },
    todo: { label: '待办', icon: '✅', color: 'bg-blue-500/20 text-blue-300' },
    follow_up: { label: '跟进', icon: '🔍', color: 'bg-yellow-500/20 text-yellow-300' },
    metric: { label: '指标', icon: '📈', color: 'bg-green-500/20 text-green-300' },
    alert: { label: '告警', icon: '⚠️', color: 'bg-red-500/20 text-red-300' }
  }

  // 优先级配置
  const priorityConfig = {
    low: { label: '低', color: 'text-gray-400' },
    medium: { label: '中', color: 'text-blue-400' },
    high: { label: '高', color: 'text-orange-400' },
    urgent: { label: '紧急', color: 'text-red-400' }
  }

  // 状态配置
  const statusConfig = {
    pending: { label: '待处理', color: 'bg-gray-500/20 text-gray-300' },
    in_progress: { label: '进行中', color: 'bg-blue-500/20 text-blue-300' },
    completed: { label: '已完成', color: 'bg-green-500/20 text-green-300' },
    cancelled: { label: '已取消', color: 'bg-red-500/20 text-red-300' }
  }

  useEffect(() => {
    loadItems()
    loadStats()
  }, [filter])

  const loadItems = async () => {
    try {
      const params = {}
      if (filter.status !== 'all') params.status = filter.status
      if (filter.priority !== 'all') params.priority = filter.priority
      if (filter.type !== 'all') params.type = filter.type

      const response = await axios.get('/api/business-items/list', { params })
      setItems(response.data)
    } catch (error) {
      console.error('加载业务事项失败:', error)
    }
  }

  const loadStats = async () => {
    try {
      const response = await axios.get('/api/business-items/stats/summary')
      setStats(response.data)
    } catch (error) {
      console.error('加载统计信息失败:', error)
    }
  }

  const createItem = async () => {
    if (!newItem.title.trim()) {
      alert('请输入标题')
      return
    }

    try {
      await axios.post('/api/business-items/create', {
        ...newItem,
        source: 'manual',
        tags: []
      })

      setNewItem({ title: '', description: '', type: 'todo', priority: 'medium' })
      setShowCreateModal(false)
      loadItems()
      loadStats()
    } catch (error) {
      console.error('创建事项失败:', error)
      alert('创建失败')
    }
  }

  const updateStatus = async (itemId, newStatus) => {
    try {
      await axios.put(`/api/business-items/${itemId}`, { status: newStatus })
      loadItems()
      loadStats()
    } catch (error) {
      console.error('更新状态失败:', error)
    }
  }

  const deleteItem = async (itemId) => {
    if (!confirm('确定要删除这个事项吗？')) {
      return
    }

    try {
      await axios.delete(`/api/business-items/${itemId}`)
      loadItems()
      loadStats()
    } catch (error) {
      console.error('删除事项失败:', error)
    }
  }

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* 统计卡片 */}
      {stats && (
        <div className="grid grid-cols-4 gap-3">
          <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
            <div className="text-xs text-gray-400 mb-1">总事项</div>
            <div className="text-2xl font-bold text-white">{stats.total}</div>
          </div>
          <div className="bg-orange-900/20 rounded-lg p-3 border border-orange-600/30">
            <div className="text-xs text-orange-300 mb-1">高优先级待处理</div>
            <div className="text-2xl font-bold text-orange-400">{stats.high_priority_pending}</div>
          </div>
          <div className="bg-red-900/20 rounded-lg p-3 border border-red-600/30">
            <div className="text-xs text-red-300 mb-1">逾期</div>
            <div className="text-2xl font-bold text-red-400">{stats.overdue}</div>
          </div>
          <div className="bg-green-900/20 rounded-lg p-3 border border-green-600/30">
            <div className="text-xs text-green-300 mb-1">已完成</div>
            <div className="text-2xl font-bold text-green-400">{stats.by_status?.completed || 0}</div>
          </div>
        </div>
      )}

      {/* 筛选和操作栏 */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex gap-2 flex-wrap">
          {/* 状态筛选 */}
          <select
            value={filter.status}
            onChange={(e) => setFilter({ ...filter, status: e.target.value })}
            className="px-3 py-1.5 bg-slate-800 border border-slate-600 rounded text-sm text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">全部状态</option>
            {Object.entries(statusConfig).map(([key, config]) => (
              <option key={key} value={key}>{config.label}</option>
            ))}
          </select>

          {/* 优先级筛选 */}
          <select
            value={filter.priority}
            onChange={(e) => setFilter({ ...filter, priority: e.target.value })}
            className="px-3 py-1.5 bg-slate-800 border border-slate-600 rounded text-sm text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">全部优先级</option>
            {Object.entries(priorityConfig).map(([key, config]) => (
              <option key={key} value={key}>{config.label}</option>
            ))}
          </select>

          {/* 类型筛选 */}
          <select
            value={filter.type}
            onChange={(e) => setFilter({ ...filter, type: e.target.value })}
            className="px-3 py-1.5 bg-slate-800 border border-slate-600 rounded text-sm text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">全部类型</option>
            {Object.entries(typeConfig).map(([key, config]) => (
              <option key={key} value={key}>{config.icon} {config.label}</option>
            ))}
          </select>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-1.5 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded transition-colors"
        >
          ➕ 新建事项
        </button>
      </div>

      {/* 事项列表 */}
      <div className="flex-1 overflow-y-auto space-y-2">
        {items.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <div className="text-4xl mb-2">📋</div>
            <div>暂无业务事项</div>
          </div>
        ) : (
          items.map((item) => {
            const typeConf = typeConfig[item.type] || typeConfig.todo
            const statusConf = statusConfig[item.status] || statusConfig.pending
            const priorityConf = priorityConfig[item.priority] || priorityConfig.medium

            return (
              <div
                key={item.id}
                className="bg-slate-800/50 rounded-lg p-3 border border-slate-700 hover:border-slate-600 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${typeConf.color}`}>
                        {typeConf.icon} {typeConf.label}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusConf.color}`}>
                        {statusConf.label}
                      </span>
                      <span className={`text-xs font-medium ${priorityConf.color}`}>
                        {priorityConf.label}
                      </span>
                    </div>
                    <h4 className="font-medium text-gray-200 mb-1">{item.title}</h4>
                    {item.description && (
                      <p className="text-sm text-gray-400 line-clamp-2">{item.description}</p>
                    )}
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                      <span>{new Date(item.created_at).toLocaleDateString('zh-CN')}</span>
                      {item.source && <span>来源: {item.source}</span>}
                    </div>
                  </div>

                  <div className="flex gap-1">
                    {item.status === 'pending' && (
                      <button
                        onClick={() => updateStatus(item.id, 'in_progress')}
                        className="px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
                        title="开始处理"
                      >
                        ▶️
                      </button>
                    )}
                    {item.status === 'in_progress' && (
                      <button
                        onClick={() => updateStatus(item.id, 'completed')}
                        className="px-2 py-1 text-xs bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
                        title="标记完成"
                      >
                        ✓
                      </button>
                    )}
                    <button
                      onClick={() => deleteItem(item.id)}
                      className="px-2 py-1 text-xs bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
                      title="删除"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>

      {/* 创建事项弹窗 */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-800 rounded-2xl shadow-2xl w-full max-w-md">
            <div className="bg-gradient-to-r from-primary-600 to-blue-600 p-4 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-white">新建业务事项</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-white/80 hover:text-white text-2xl leading-none"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-4 space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">标题 *</label>
                <input
                  type="text"
                  value={newItem.title}
                  onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="输入事项标题"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">描述</label>
                <textarea
                  value={newItem.description}
                  onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                  rows={3}
                  placeholder="详细描述（可选）"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">类型</label>
                  <select
                    value={newItem.type}
                    onChange={(e) => setNewItem({ ...newItem, type: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {Object.entries(typeConfig).map(([key, config]) => (
                      <option key={key} value={key}>{config.icon} {config.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">优先级</label>
                  <select
                    value={newItem.priority}
                    onChange={(e) => setNewItem({ ...newItem, priority: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    {Object.entries(priorityConfig).map(([key, config]) => (
                      <option key={key} value={key}>{config.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  onClick={createItem}
                  className="flex-1 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded transition-colors"
                >
                  创建
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-gray-300 font-medium rounded transition-colors"
                >
                  取消
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default BusinessItemsBoard
