import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import ChatMessage from '../components/ChatMessage'

const DEMO_CUSTOMERS = [
  { id: "U001", name: "张伟" },
  { id: "U002", name: "李娜" },
  { id: "U003", name: "王强" }
]

export default function S3CustomerService() {
  const [customerId, setCustomerId] = useState(DEMO_CUSTOMERS[0].id)
  const [chatInput, setChatInput] = useState("")
  const [chatMsgs, setChatMsgs] = useState({}) // 按customerId存储
  const [streaming, setStreaming] = useState(false)
  const [customerPoints, setCustomerPoints] = useState([])
  const [kbEntries, setKbEntries] = useState([])
  const [kbInput, setKbInput] = useState("")
  const [isDragging, setIsDragging] = useState(false)
  const [isAddingKB, setIsAddingKB] = useState(false)
  
  // Dashboard 统计
  const [stats, setStats] = useState({
    totalChats: 0,
    progressQueries: 0,
    productAnswers: 0,
    complaints: 0,
    autoPush: 0,
    transferHuman: 0,
    newPoints: 0,
    hitPoints: 0
  })
  
  const chatRef = useRef(null)
  const fileInputRef = useRef(null)
  const hasLoadedRef = useRef(false)

  // 从 localStorage 恢复所有客户的聊天记录（仅首次）
  useEffect(() => {
    if (hasLoadedRef.current) return
    hasLoadedRef.current = true
    
    const saved = localStorage.getItem('s3_chat_messages')
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        setChatMsgs(parsed)
        console.log('已恢复聊天记录:', Object.keys(parsed))
      } catch(e) {
        console.error('恢复聊天记录失败:', e)
      }
    }
  }, [])

  // 保存所有客户的聊天记录到 localStorage（跳过首次加载）
  useEffect(() => {
    if (!hasLoadedRef.current) return
    try {
      localStorage.setItem('s3_chat_messages', JSON.stringify(chatMsgs))
      console.log('已保存聊天记录到localStorage')
    } catch(e) {
      console.error('保存聊天记录失败:', e)
    }
  }, [chatMsgs])

  // 加载知识库
  useEffect(() => {
    loadKB()
  }, [])

  const loadKB = () => {
    axios.get("/api/s3/kb/list").then(res => {
      if (res.data.success) setKbEntries(res.data.entries)
    }).catch(() => {})
  }

  // 切换客户时刷新要点
  useEffect(() => {
    refreshPoints(customerId)
  }, [customerId])

  // 自动滚动
  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight
    }
  }, [chatMsgs, customerId])

  const getCurrentMessages = () => chatMsgs[customerId] || []
  const setCurrentMessages = (msgs) => {
    setChatMsgs(prev => ({ ...prev, [customerId]: msgs }))
  }

  function refreshPoints(id) {
    axios.get(`/api/s3/customer/points?customer_id=${id}&limit=3`)
      .then(res => {
        if (res.data && res.data.points) setCustomerPoints(res.data.points)
        else setCustomerPoints([])
      })
      .catch(() => setCustomerPoints([]))
  }

  const handleSend = async () => {
    if (!chatInput.trim() || streaming) return
    setStreaming(true)
    const msg = chatInput
    setChatInput("")
    
    const currentMsgs = getCurrentMessages()
    // 添加用户消息和空的agent消息（用于流式更新）
    const updatedMsgs = [...currentMsgs, { role: "user", content: msg }, { role: "agent", content: "", streaming: true }]
    setCurrentMessages(updatedMsgs)

    try {
      const response = await fetch("/api/s3/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: customerId,
          message: msg,
          conversation_history: currentMsgs.filter(m => m.role === "user" || m.role === "agent").map(m => ({role: m.role, content: m.content}))
        })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder("utf-8")
      let buffer = ""
      let accumulated = ""

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n\n")
        buffer = lines.pop() || ""

        for (let line of lines) {
          if (line.startsWith("data: ")) {
            const data = JSON.parse(line.slice(6))
            if (data.type === "content") {
              accumulated += data.content
              setChatMsgs(prev => {
                const currentCustomerMsgs = prev[customerId] || []
                const newMsgs = [...currentCustomerMsgs]
                if (newMsgs.length > 0) {
                  newMsgs[newMsgs.length - 1] = { role: "agent", content: accumulated, streaming: true }
                }
                return { ...prev, [customerId]: newMsgs }
              })
            } else if (data.type === "done") {
              setChatMsgs(prev => {
                const currentCustomerMsgs = prev[customerId] || []
                const newMsgs = [...currentCustomerMsgs]
                if (newMsgs.length > 0) {
                  newMsgs[newMsgs.length - 1] = { role: "agent", content: accumulated, streaming: false }
                }
                return { ...prev, [customerId]: newMsgs }
              })
            }
          }
        }
      }
      
      // 更新统计
      setStats(s => ({ ...s, totalChats: s.totalChats + 1, newPoints: s.newPoints + 1 }))
    } catch (e) {
      console.error("发送失败:", e)
      // 移除失败的空agent消息
      setChatMsgs(prev => {
        const currentCustomerMsgs = prev[customerId] || []
        return { ...prev, [customerId]: currentCustomerMsgs.slice(0, -1) }
      })
    }
    setStreaming(false)
    refreshPoints(customerId)
  }

  const handleClearCustomer = async () => {
    if (!confirm(`确认清除 ${DEMO_CUSTOMERS.find(c => c.id === customerId)?.name} 的所有聊天记录和企业大脑记忆？`)) return
    
    // 清除前端聊天记录
    setChatMsgs(prev => {
      const updated = { ...prev }
      delete updated[customerId]
      return updated
    })
    
    // 清除后端记忆
    try {
      await axios.delete(`/api/s3/customer/${customerId}/clear`)
      refreshPoints(customerId)
      alert("已清除该客户的所有数据")
    } catch(e) {
      alert("清除失败：" + e.message)
    }
  }

  const deletePoint = async (id) => {
    await axios.delete(`/api/memory/${id}`)
    refreshPoints(customerId)
  }

  const handleAddKB = async () => {
    if (!kbInput.trim() || isAddingKB) return
    
    setIsAddingKB(true)
    
    // 自动判断分类
    let category = "company"
    if (kbInput.includes("产品") || kbInput.includes("规格") || kbInput.includes("FAQ")) {
      category = "product_faq"
    } else if (kbInput.includes("售后") || kbInput.includes("退换") || kbInput.includes("质保")) {
      category = "policy"
    } else if (kbInput.includes("新品") || kbInput.includes("上市")) {
      category = "new_release"
    }
    
    const contentToAdd = kbInput
    
    try {
      await axios.post("/api/s3/kb/add", {
        category: category,
        title: kbInput.slice(0, 20) + (kbInput.length > 20 ? "..." : ""),
        content: kbInput
      })
      
      setKbInput("")
      
      // 立即刷新知识库列表
      await loadKB()
      
      // 检测新品关键词，自动推送
      if (category === "new_release") {
        setStats(s => ({ ...s, autoPush: s.autoPush + 3 }))
        // 给三个客户推送消息
        DEMO_CUSTOMERS.forEach(c => {
          setChatMsgs(prev => {
            const msgs = prev[c.id] || []
            return {
              ...prev,
              [c.id]: [...msgs, { role: "agent", content: `🎉 新品上市通知：${contentToAdd.slice(0, 50)}...` }]
            }
          })
        })
      }
    } catch(e) {
      alert("添加失败：" + (e.response?.data?.detail || e.message))
    } finally {
      setIsAddingKB(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      const reader = new FileReader()
      reader.onload = (ev) => {
        setKbInput(ev.target.result)
      }
      reader.readAsText(file)
    }
  }

  return (
    <div className="space-y-6">
      {/* 场景标题 */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-bold text-gray-100">S3 智能客服</h1>
          <span className="px-3 py-1 rounded-lg text-sm font-medium bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            认人+记历史+主动推荐
          </span>
        </div>
        <p className="text-gray-400">基于客户历史记忆的智能客服，能认人、能回忆、能推荐</p>
      </div>

      {/* 客户选择与操作 */}
      <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 flex items-center gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-300 mb-2">当前客户</label>
          <select
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2 text-gray-200"
          >
            {DEMO_CUSTOMERS.map(c => (
              <option key={c.id} value={c.id}>{c.name}（{c.id}）</option>
            ))}
          </select>
        </div>
        <div className="flex items-end">
          <button
            onClick={handleClearCustomer}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded text-sm"
          >
            清除当前客户数据
          </button>
        </div>
      </div>

      {/* 主体区域：左-历史要点 中-聊天 右-知识库 */}
      <div className="grid grid-cols-12 gap-4">
        {/* 左：历史要点 */}
        <div className="col-span-3 bg-slate-800 rounded-lg p-4 border border-slate-700">
          <h3 className="text-lg font-semibold mb-3 text-gray-200">客户历史要点</h3>
          <div className="text-xs text-gray-400 mb-3">
            （仅显示该客户在企业大脑中的记录）
          </div>
          {customerPoints.length === 0 && (
            <div className="text-gray-400 text-sm">暂无历史要点</div>
          )}
          {customerPoints.map((p) => (
            <div key={p.id} className="mb-3 bg-slate-700 rounded-lg p-3 border border-slate-600">
              <div className="text-sm text-gray-300 mb-2 whitespace-pre-wrap">{p.content}</div>
              <button
                onClick={() => deletePoint(p.id)}
                className="text-xs text-red-400 hover:text-red-300"
              >
                删除
              </button>
            </div>
          ))}
        </div>

        {/* 中：聊天区 */}
        <div className="col-span-6 bg-slate-800 rounded-lg border border-slate-700 flex flex-col">
          <div ref={chatRef} className="flex-1 overflow-y-auto p-4 min-h-[500px]">
            {getCurrentMessages().length === 0 && (
              <div className="text-center text-gray-400 mt-20">请输入问题开始对话</div>
            )}
            {getCurrentMessages().map((msg, idx) => (
              <ChatMessage
                key={idx}
                role={msg.role}
                content={msg.content}
                streaming={msg.streaming}
                agentName={msg.role === 'agent' ? '智能客服' : undefined}
                icon={msg.role === 'agent' ? '🎧' : undefined}
              />
            ))}
          </div>
          <div className="p-4 border-t border-slate-700">
            <div className="flex gap-2">
              <input
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                disabled={streaming}
                placeholder="请输入问题，例如：我的订单进度？"
                className="flex-1 bg-slate-700 border border-slate-600 rounded px-3 py-2 text-gray-200 placeholder-gray-500"
              />
              <button
                onClick={handleSend}
                disabled={streaming || !chatInput.trim()}
                className="px-6 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-semibold rounded transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                发送
              </button>
            </div>
          </div>
        </div>

        {/* 右：知识库 */}
        <div className="col-span-3 bg-slate-800 rounded-lg p-4 border border-slate-700 flex flex-col">
          <h3 className="text-lg font-semibold mb-3 text-gray-200">知识库（共享）</h3>
          
          {/* 已有知识库条目 */}
          <div className="flex-1 space-y-2 mb-4 overflow-y-auto max-h-60">
            {kbEntries.length === 0 && (
              <div className="text-gray-400 text-sm">暂无知识库条目</div>
            )}
            {kbEntries.map((e, idx) => (
              <div key={idx} className="bg-slate-700 rounded p-2 border border-slate-600">
                <div className="text-xs font-semibold text-gray-200 mb-1">{e.title || '知识条目'}</div>
                <div className="text-xs text-gray-400">{e.content.slice(0, 80)}...</div>
              </div>
            ))}
          </div>

          {/* 新增区域 */}
          <div className="space-y-2 border-t border-slate-700 pt-3">
            <label className="text-sm text-gray-300">新增知识库条目</label>
            <div
              className={`border-2 border-dashed rounded p-3 ${
                isDragging ? 'border-emerald-500 bg-emerald-500/10' : 'border-slate-600'
              }`}
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
            >
              <textarea
                value={kbInput}
                onChange={(e) => setKbInput(e.target.value)}
                placeholder="输入内容或拖拽文件到此处"
                rows={4}
                className="w-full bg-slate-700 border border-slate-600 rounded px-2 py-1 text-sm text-gray-200"
              />
            </div>
            <button
              onClick={handleAddKB}
              disabled={!kbInput.trim() || isAddingKB}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-2 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAddingKB ? '添加中...' : '添加到知识库'}
            </button>
            <div className="text-xs text-gray-400">
              💡 提示：若包含"新品"关键词，将自动推送给所有客户
            </div>
          </div>
        </div>
      </div>

      {/* Dashboard 数据版 */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-200">实时数据看板</h3>
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-slate-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-emerald-400">{stats.totalChats}</div>
            <div className="text-sm text-gray-400 mt-1">已处理咨询数</div>
          </div>
          <div className="bg-slate-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-blue-400">{stats.progressQueries}</div>
            <div className="text-sm text-gray-400 mt-1">进度查询成功数</div>
          </div>
          <div className="bg-slate-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-purple-400">{stats.productAnswers}</div>
            <div className="text-sm text-gray-400 mt-1">产品信息解答数</div>
          </div>
          <div className="bg-slate-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-yellow-400">{stats.complaints}</div>
            <div className="text-sm text-gray-400 mt-1">投诉受理数</div>
          </div>
          <div className="bg-slate-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-pink-400">{stats.autoPush}</div>
            <div className="text-sm text-gray-400 mt-1">自动推送条数</div>
          </div>
          <div className="bg-slate-700 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-red-400">{stats.transferHuman}</div>
            <div className="text-sm text-gray-400 mt-1">已转人工数</div>
          </div>
          <div className="bg-slate-700 rounded-lg p-4 text-center border-2 border-emerald-500">
            <div className="text-3xl font-bold text-emerald-400">{stats.newPoints}</div>
            <div className="text-sm text-emerald-300 mt-1">新增历史要点数</div>
          </div>
          <div className="bg-slate-700 rounded-lg p-4 text-center border-2 border-emerald-500">
            <div className="text-3xl font-bold text-emerald-400">{stats.hitPoints}</div>
            <div className="text-sm text-emerald-300 mt-1">命中历史要点数</div>
          </div>
        </div>
      </div>

      {/* 底部三分对比 */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 text-gray-200">对比展示</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-slate-700 rounded-lg p-4">
            <div className="text-3xl mb-2 text-center">🤷‍♂️</div>
            <h4 className="font-medium mb-2 text-gray-300 text-center">没有智能客服</h4>
            <p className="text-xs text-gray-400 mb-3">全靠人工，应答慢，难衔接客户上下文</p>
            <div className="bg-slate-800 rounded p-3 text-xs text-gray-300">
              用户：我的订单什么时候到？<br />
              客服：请稍等……<br />
              <span className="text-gray-500">（2分钟后）</span><br />
              客服：请问您的订单号？
            </div>
          </div>
          <div className="bg-slate-700 rounded-lg p-4">
            <div className="text-3xl mb-2 text-center">🤖</div>
            <h4 className="font-medium mb-2 text-gray-300 text-center">市面普通智能客服</h4>
            <p className="text-xs text-gray-400 mb-3">会答FAQ，但遗忘历史，多轮对话力不从心</p>
            <div className="bg-slate-800 rounded p-3 text-xs text-gray-300">
              用户：上次投诉的工单怎么样了？<br />
              客服：请提供您的工单号。<br />
              用户：就是上次回访的……<br />
              客服：未找到信息，请联系人工。
            </div>
          </div>
          <div className="bg-slate-700 rounded-lg p-4 border-2 border-emerald-500">
            <div className="text-3xl mb-2 text-center">🧠✨</div>
            <h4 className="font-medium mb-2 text-emerald-400 text-center">我们的智能客服</h4>
            <p className="text-xs text-emerald-300 mb-3">认人+记历史+主动提醒，体验进化一大步</p>
            <div className="bg-slate-800 rounded p-3 text-xs text-gray-300">
              用户：上次订的蓝牙耳机什么时候到？<br />
              客服：<span className="text-emerald-400 font-semibold">上次你订的蓝牙耳机（单号123）</span>
              我们已预约明天18:00送达，需提醒请回复"是"。<br />
              <span className="text-emerald-300">PS：你还关注过X型号，也有优惠哟！</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
