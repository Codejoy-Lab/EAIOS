import React, { useState, useEffect } from 'react'
import axios from 'axios'

const MemoryManagement = () => {
  const [memories, setMemories] = useState([])
  const [loading, setLoading] = useState(false)
  const [newMemory, setNewMemory] = useState({
    content: '',
    type: 'global',
    source: '手动输入'
  })

  // 加载记忆列表
  const loadMemories = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/memory/list')
      setMemories(response.data.memories || [])
    } catch (error) {
      console.error('加载记忆失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 添加记忆
  const handleAddMemory = async () => {
    if (!newMemory.content.trim()) {
      alert('请输入记忆内容')
      return
    }

    try {
      await axios.post('/api/memory/add', newMemory)
      setNewMemory({ content: '', type: 'global', source: '手动输入' })
      loadMemories()
      alert('记忆添加成功')
    } catch (error) {
      console.error('添加记忆失败:', error)
      alert('添加记忆失败')
    }
  }

  // 勾选/取消勾选记忆
  const handleToggleMemory = async (memoryId, currentEnabled) => {
    try {
      await axios.post('/api/memory/toggle', {
        memory_id: memoryId,
        enabled: !currentEnabled
      })
      loadMemories()
    } catch (error) {
      console.error('更新记忆状态失败:', error)
    }
  }

  // 删除记忆
  const handleDeleteMemory = async (memoryId) => {
    if (!confirm('确定删除这条记忆吗？')) return

    try {
      await axios.delete(`/api/memory/${memoryId}`)
      loadMemories()
    } catch (error) {
      console.error('删除记忆失败:', error)
    }
  }

  useEffect(() => {
    loadMemories()
  }, [])

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h1 className="text-3xl font-bold text-gray-100 mb-2">记忆管理</h1>
        <p className="text-gray-400">
          管理企业AI的记忆库，勾选的记忆将被Agent自动召回并使用
        </p>
      </div>

      {/* 添加新记忆 */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-semibold mb-4 text-gray-200">添加新记忆</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              记忆内容
            </label>
            <textarea
              value={newMemory.content}
              onChange={(e) => setNewMemory({ ...newMemory, content: e.target.value })}
              placeholder="例如：公司最新规定客服必须按照某某流程回答客户问题"
              className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-3 text-gray-200 min-h-[100px]"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                记忆类型
              </label>
              <select
                value={newMemory.type}
                onChange={(e) => setNewMemory({ ...newMemory, type: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-gray-200"
              >
                <option value="global">全局记忆</option>
                <option value="scenario">场景记忆</option>
                <option value="interaction">交互记忆</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                来源
              </label>
              <input
                type="text"
                value={newMemory.source}
                onChange={(e) => setNewMemory({ ...newMemory, source: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-gray-200"
              />
            </div>
          </div>

          <button
            onClick={handleAddMemory}
            className="w-full bg-gradient-to-r from-primary-500 to-accent-500 hover:from-primary-600 hover:to-accent-600 text-white font-semibold py-3 px-4 rounded transition-all"
          >
            添加记忆
          </button>
        </div>
      </div>

      {/* 记忆列表 */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-200">记忆列表</h2>
          <button
            onClick={loadMemories}
            className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-gray-300 rounded transition-colors"
          >
            刷新
          </button>
        </div>

        {loading ? (
          <div className="text-center py-8 text-gray-400">加载中...</div>
        ) : memories.length === 0 ? (
          <div className="text-center py-8 text-gray-400">暂无记忆，请添加</div>
        ) : (
          <div className="space-y-3">
            {memories.map((memory) => (
              <div
                key={memory.id}
                className={`bg-slate-700 rounded-lg p-4 border ${
                  memory.enabled
                    ? 'border-primary-500/50'
                    : 'border-slate-600'
                }`}
              >
                <div className="flex items-start gap-3">
                  {/* 勾选框 */}
                  <input
                    type="checkbox"
                    checked={memory.enabled}
                    onChange={() => handleToggleMemory(memory.id, memory.enabled)}
                    className="mt-1 w-5 h-5 cursor-pointer"
                  />

                  {/* 内容 */}
                  <div className="flex-1">
                    <p className={`text-gray-200 mb-2 ${!memory.enabled && 'opacity-50'}`}>
                      {memory.content}
                    </p>
                    <div className="flex items-center gap-3 text-xs text-gray-400">
                      <span className="px-2 py-1 bg-slate-600 rounded">
                        {memory.memory_type}
                      </span>
                      <span>来源: {memory.metadata?.source || '未知'}</span>
                      <span>{new Date(memory.created_at).toLocaleString('zh-CN')}</span>
                    </div>
                  </div>

                  {/* 删除按钮 */}
                  <button
                    onClick={() => handleDeleteMemory(memory.id)}
                    className="px-3 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded text-sm transition-colors"
                  >
                    删除
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 使用说明 */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-3 text-gray-200">使用说明</h3>
        <ul className="space-y-2 text-gray-400 text-sm">
          <li className="flex items-start gap-2">
            <span className="text-primary-400">•</span>
            <span>勾选的记忆会被Agent自动召回和使用</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-400">•</span>
            <span>取消勾选后，该记忆将不再影响Agent的回答</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-400">•</span>
            <span>全局记忆对所有场景生效，场景记忆仅对特定场景生效</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-primary-400">•</span>
            <span>在场景页面可以看到Agent引用了哪些记忆（来源证明）</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

export default MemoryManagement
