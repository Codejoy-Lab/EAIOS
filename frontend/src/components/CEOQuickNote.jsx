import React, { useState, useEffect } from 'react'
import axios from 'axios'

/**
 * CEO快记组件
 * 快速记录、AI自动分类、一键保存
 */
const CEOQuickNote = ({ isOpen, onClose }) => {
  const [noteContent, setNoteContent] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [notes, setNotes] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [showHistory, setShowHistory] = useState(false)

  // 分类标签配置
  const categoryConfig = {
    work_preference: { label: '工作偏好', color: 'bg-blue-500/20 text-blue-300', icon: '⚙️' },
    company_background: { label: '公司背景', color: 'bg-purple-500/20 text-purple-300', icon: '🏢' },
    business_decision: { label: '业务决策', color: 'bg-green-500/20 text-green-300', icon: '📊' },
    daily_thought: { label: '日常想法', color: 'bg-yellow-500/20 text-yellow-300', icon: '💡' },
    other: { label: '其他', color: 'bg-gray-500/20 text-gray-300', icon: '📝' }
  }

  // 加载历史快记
  useEffect(() => {
    if (isOpen && showHistory) {
      loadNotes()
    }
  }, [isOpen, showHistory])

  const loadNotes = async () => {
    try {
      const response = await axios.get('/api/ceo-notes/list', {
        params: {
          category: selectedCategory === 'all' ? undefined : selectedCategory,
          limit: 20
        }
      })
      setNotes(response.data)
    } catch (error) {
      console.error('加载快记失败:', error)
    }
  }

  const handleSave = async () => {
    if (!noteContent.trim()) {
      return
    }

    setIsSaving(true)
    try {
      const response = await axios.post('/api/ceo-notes/create', {
        content: noteContent,
        user_id: 'ceo_default'
      })

      console.log('✅ 快记已保存:', response.data)

      // 清空输入
      setNoteContent('')

      // 显示成功提示
      alert(`✅ 快记已保存\n分类: ${categoryConfig[response.data.category]?.label || '其他'}\n摘要: ${response.data.ai_summary}`)

      // 如果正在查看历史，刷新列表
      if (showHistory) {
        loadNotes()
      }
    } catch (error) {
      console.error('保存快记失败:', error)
      alert('保存失败，请稍后再试')
    } finally {
      setIsSaving(false)
    }
  }

  const handleKeyDown = (e) => {
    // Ctrl+Enter 或 Cmd+Enter 保存
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSave()
    }
  }

  const deleteNote = async (noteId) => {
    if (!confirm('确定要删除这条快记吗？')) {
      return
    }

    try {
      await axios.delete(`/api/ceo-notes/${noteId}`)
      loadNotes()
    } catch (error) {
      console.error('删除快记失败:', error)
      alert('删除失败')
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* 头部 */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-3xl">📝</span>
              <div>
                <h2 className="text-xl font-bold text-white">CEO快记</h2>
                <p className="text-sm text-white/70">快速记录，AI智能分类</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white text-2xl leading-none"
            >
              ×
            </button>
          </div>
        </div>

        {/* Tab切换 */}
        <div className="flex border-b border-slate-700">
          <button
            onClick={() => setShowHistory(false)}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              !showHistory
                ? 'text-primary-400 border-b-2 border-primary-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            ✍️ 新建快记
          </button>
          <button
            onClick={() => setShowHistory(true)}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              showHistory
                ? 'text-primary-400 border-b-2 border-primary-400'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            📚 历史记录
          </button>
        </div>

        {/* 内容区域 */}
        <div className="flex-1 overflow-y-auto p-6">
          {!showHistory ? (
            // 新建快记
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  记录内容
                </label>
                <textarea
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="快速记录你的想法、决策、灵感...&#10;&#10;💡 AI会自动帮你分类：&#10;- 工作偏好：决策风格、管理习惯&#10;- 公司背景：团队、业务模式&#10;- 业务决策：战略计划、重要事项&#10;- 日常想法：灵感、备忘&#10;&#10;⌨️ 快捷键：Ctrl+Enter 保存"
                  className="w-full h-64 px-4 py-3 bg-slate-900 border border-slate-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                  autoFocus
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="text-xs text-gray-400">
                  {noteContent.length} 字
                </div>
                <button
                  onClick={handleSave}
                  disabled={!noteContent.trim() || isSaving}
                  className="px-6 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-medium rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {isSaving ? '保存中...' : '💾 保存快记'}
                </button>
              </div>
            </div>
          ) : (
            // 历史记录
            <div className="space-y-4">
              {/* 分类筛选 */}
              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => {
                    setSelectedCategory('all')
                    loadNotes()
                  }}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                    selectedCategory === 'all'
                      ? 'bg-primary-500 text-white'
                      : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                  }`}
                >
                  全部
                </button>
                {Object.entries(categoryConfig).map(([key, config]) => (
                  <button
                    key={key}
                    onClick={() => {
                      setSelectedCategory(key)
                      loadNotes()
                    }}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                      selectedCategory === key
                        ? 'bg-primary-500 text-white'
                        : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
                    }`}
                  >
                    {config.icon} {config.label}
                  </button>
                ))}
              </div>

              {/* 快记列表 */}
              <div className="space-y-3">
                {notes.length === 0 ? (
                  <div className="text-center py-12 text-gray-400">
                    <div className="text-4xl mb-2">📭</div>
                    <div>暂无快记记录</div>
                  </div>
                ) : (
                  notes.map((note) => {
                    const config = categoryConfig[note.category] || categoryConfig.other
                    return (
                      <div
                        key={note.id}
                        className="bg-slate-900/50 rounded-lg p-4 border border-slate-700 hover:border-slate-600 transition-colors"
                      >
                        <div className="flex items-start justify-between gap-3 mb-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
                            {config.icon} {config.label}
                          </span>
                          <button
                            onClick={() => deleteNote(note.id)}
                            className="text-gray-400 hover:text-red-400 text-sm"
                          >
                            🗑️
                          </button>
                        </div>
                        <p className="text-gray-300 text-sm mb-2 whitespace-pre-wrap">
                          {note.content}
                        </p>
                        {note.ai_summary && (
                          <p className="text-xs text-gray-500 italic border-l-2 border-primary-500/30 pl-2">
                            AI摘要: {note.ai_summary}
                          </p>
                        )}
                        <div className="text-xs text-gray-500 mt-2">
                          {new Date(note.created_at).toLocaleString('zh-CN')}
                        </div>
                      </div>
                    )
                  })
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CEOQuickNote
