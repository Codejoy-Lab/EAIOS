import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import ScenarioTemplate from '../components/ScenarioTemplate'
import ChatMessage from '../components/ChatMessage'
import AgentDetailModal from '../components/AgentDetailModal'

// Agent状态卡片组件（可点击）
const AgentCard = ({ name, icon, status, message, output, onClick }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'idle':
        return {
          bgColor: 'bg-slate-700/50',
          dotColor: 'bg-gray-400',
          textColor: 'text-gray-400',
          pulse: false
        }
      case 'working':
        return {
          bgColor: 'bg-yellow-900/30 border-yellow-600/30',
          dotColor: 'bg-yellow-400',
          textColor: 'text-yellow-300',
          pulse: true
        }
      case 'completed':
        return {
          bgColor: 'bg-green-900/30 border-green-600/30',
          dotColor: 'bg-green-400',
          textColor: 'text-green-300',
          pulse: false
        }
      default:
        return {
          bgColor: 'bg-slate-700/50',
          dotColor: 'bg-gray-400',
          textColor: 'text-gray-400',
          pulse: false
        }
    }
  }

  const config = getStatusConfig()

  return (
    <div
      className={`${config.bgColor} rounded-lg p-3 border border-slate-600 transition-all cursor-pointer hover:border-primary-500/50`}
      onClick={onClick}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">{icon}</span>
        <span className="text-xs font-semibold text-gray-300">{name}</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="relative">
          <div className={`w-2 h-2 rounded-full ${config.dotColor}`}></div>
          {config.pulse && (
            <div className={`absolute inset-0 w-2 h-2 rounded-full ${config.dotColor} animate-ping opacity-75`}></div>
          )}
        </div>
        <span className={`text-xs ${config.textColor}`}>{message}</span>
      </div>
    </div>
  )
}

const S8Decision = () => {
  // 消息历史
  const [decisionMessages, setDecisionMessages] = useState([])
  const [meetingMessages, setMeetingMessages] = useState([])

  // Agent状态管理
  const [agentStatus, setAgentStatus] = useState({
    summary: { status: 'idle', message: '等待中', output: null, description: '负责汇总经营数据和关键指标' },
    risk: { status: 'idle', message: '等待中', output: null, description: '负责识别异常和风险' },
    recommendation: { status: 'idle', message: '等待中', output: null, description: '负责生成行动建议' }
  })

  // Agent详情弹窗
  const [selectedAgent, setSelectedAgent] = useState(null)

  // 其他状态
  const [meetingInput, setMeetingInput] = useState('')
  const [decisionInput, setDecisionInput] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [hasAutoStarted, setHasAutoStarted] = useState(false)

  // WebSocket
  const ws = useRef(null)
  const decisionChatRef = useRef(null)
  const meetingChatRef = useRef(null)

  // 自动滚动到底部
  const scrollToBottom = (ref) => {
    if (ref.current) {
      ref.current.scrollTop = ref.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollToBottom(decisionChatRef)
  }, [decisionMessages])

  useEffect(() => {
    scrollToBottom(meetingChatRef)
  }, [meetingMessages])

  // 初始化WebSocket
  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000/api/s8/ws')

    ws.current.onopen = () => {
      console.log('✅ WebSocket连接成功')
    }

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('📨 收到WebSocket消息:', data.type, data)

        if (data.type === 'report_updated') {
          console.log('🔄 处理report_updated事件')
          handleReportUpdated(data.data)
        } else if (data.type === 'node_status') {
          console.log('📊 处理node_status事件:', data.data)
          handleNodeStatus(data.data)
        } else if (data.type === 'pong') {
          // Ignore pong messages
        } else {
          console.log('❓ 未知的WebSocket消息类型:', data.type)
        }
      } catch (error) {
        console.error('❌ WebSocket消息处理错误:', error)
      }
    }

    ws.current.onerror = (error) => {
      console.error('❌ WebSocket错误:', error)
    }

    ws.current.onclose = () => {
      console.log('🔌 WebSocket连接关闭')
    }

    // 发送心跳
    const heartbeat = setInterval(() => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send('ping')
      }
    }, 30000)

    return () => {
      clearInterval(heartbeat)
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [])

  // 自动启动工作流（防止React StrictMode重复执行）
  const workflowStartedRef = useRef(false)
  useEffect(() => {
    if (!workflowStartedRef.current) {
      workflowStartedRef.current = true
      // 延迟500ms后自动开始
      setTimeout(() => {
        startWorkflow()
      }, 500)
    }
  }, [])

  // 开始工作流
  const startWorkflow = async () => {
    // Decision Agent发送欢迎消息
    addDecisionMessage('system', '决策军师 S8 已上线')

    setTimeout(() => {
      addDecisionMessage('agent', '早上好！让我先帮您看看今天的经营情况...', 'S8 决策军师', '🧠')
    }, 300)

    // 开始生成报告
    setTimeout(() => {
      generateReport()
    }, 800)
  }

  // 添加Decision消息
  const addDecisionMessage = (role, content, agentName = null, icon = null) => {
    setDecisionMessages(prev => [...prev, { role, content, agentName, icon, timestamp: Date.now() }])
  }

  // 添加Meeting消息
  const addMeetingMessage = (role, content, agentName = null, icon = null) => {
    setMeetingMessages(prev => [...prev, { role, content, agentName, icon, timestamp: Date.now() }])
  }

  // 生成报告
  const generateReport = async () => {
    setIsGenerating(true)
    resetAgentStatus()

    try {
      const response = await axios.post('/api/s8/generate', {
        input_data: {}
      })

      const report = response.data.report
      console.log('报告生成成功:', report)

      // 显示报告结果
      const reportSummary = formatReportSummary(report)
      addDecisionMessage('agent', reportSummary, 'S8 决策军师', '🧠')
    } catch (error) {
      console.error('生成报告失败:', error)
      addDecisionMessage('agent', '❌ 生成报告失败: ' + error.message, 'S8 决策军师', '🧠')
    } finally {
      setIsGenerating(false)
    }
  }

  // 格式化报告摘要 - 自然对话风格
  const formatReportSummary = (report) => {
    let messages = []

    // 开场白
    messages.push(`好的，我已经分析完今天的经营数据了。`)

    // 经营摘要
    if (report.summary) {
      messages.push(`\n${report.summary.summary_text}`)
    }

    // 风险提示
    if (report.risks && report.risks.risks && report.risks.risks.length > 0) {
      messages.push(`\n不过我注意到有几个需要关注的风险：`)
      report.risks.risks.forEach((risk, idx) => {
        const severityText = risk.severity === 'high' ? '比较严重' : risk.severity === 'medium' ? '需要注意' : '影响较小'
        messages.push(`\n${idx + 1}. ${risk.title}（${severityText}）\n   ${risk.description}`)
      })
    }

    // 行动建议
    if (report.recommendations && report.recommendations.actions && report.recommendations.actions.length > 0) {
      messages.push(`\n基于这些情况，我建议您今天重点关注这几件事：`)
      report.recommendations.actions.forEach((action, idx) => {
        messages.push(`\n${idx + 1}. ${action.title}\n   原因：${action.reason}`)
      })
      messages.push(`\n以上建议都是基于最新的数据和企业记忆库的信息，您觉得怎么样？`)
    }

    return messages.join('')
  }

  // 处理用户提问（决策军师） - 流式版本
  const handleSendDecision = async () => {
    if (!decisionInput.trim() || isGenerating) return

    // 用户消息
    addDecisionMessage('user', decisionInput)
    const userQuestion = decisionInput
    setDecisionInput('')
    setIsGenerating(true)

    // 创建占位消息用于流式更新
    addDecisionMessage('agent', '', 'S8 决策军师', '🧠')

    try {
      // 构建对话历史
      const conversationHistory = decisionMessages
        .filter(msg => msg.role === 'user' || msg.role === 'agent')
        .map(msg => ({
          role: msg.role === 'agent' ? 'assistant' : 'user',
          content: msg.content
        }))

      console.log('🚀 开始流式对话...')

      // 使用fetch进行SSE流式请求
      const response = await fetch('/api/s8/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userQuestion,
          conversation_history: conversationHistory
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let accumulatedContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))

              if (data.type === 'content') {
                // 累积内容并更新最后一条消息
                accumulatedContent += data.content
                setDecisionMessages(prev => {
                  const newMessages = [...prev]
                  newMessages[newMessages.length - 1] = {
                    ...newMessages[newMessages.length - 1],
                    content: accumulatedContent
                  }
                  return newMessages
                })
              } else if (data.type === 'done') {
                console.log('✅ 流式接收完成')
              } else if (data.type === 'error') {
                console.error('❌ 服务器错误:', data.error)
                throw new Error(data.error)
              }
            } catch (e) {
              console.warn('解析SSE消息失败:', line, e)
            }
          }
        }
      }
    } catch (error) {
      console.error('对话失败:', error)
      // 更新最后一条消息为错误提示
      setDecisionMessages(prev => {
        const newMessages = [...prev]
        newMessages[newMessages.length - 1] = {
          ...newMessages[newMessages.length - 1],
          content: '抱歉，我遇到了一些技术问题，请稍后再试。'
        }
        return newMessages
      })
    } finally {
      setIsGenerating(false)
    }
  }

  // 处理会议记录
  const handleSendMeeting = async () => {
    if (!meetingInput.trim()) return

    // 用户消息
    addMeetingMessage('user', meetingInput)
    const userInput = meetingInput
    setMeetingInput('')

    try {
      // 会议助手开始处理
      addMeetingMessage('system', '会议助手正在处理...')

      const response = await axios.post('/api/s8/meeting/process', {
        notes: userInput
      })

      console.log('会议记录处理成功:', response.data)

      // 会议助手回复
      const memoryCount = response.data.memory_ids.length
      addMeetingMessage('agent', `✅ 已成功提取 ${memoryCount} 条关键信息并写入企业记忆库`, '会议助手', '📝')

      if (response.data.conflicts && response.data.conflicts.length > 0) {
        addMeetingMessage('agent', `⚠️ 检测到 ${response.data.conflicts.length} 个决策冲突`, '会议助手', '📝')
      }
    } catch (error) {
      console.error('处理会议记录失败:', error)
      addMeetingMessage('agent', '❌ 处理会议记录失败: ' + error.message, '会议助手', '📝')
    }
  }

  // 处理报告更新通知
  const handleReportUpdated = async (data) => {
    console.log('报告已更新:', data)

    // Decision Agent发出消息
    addDecisionMessage('system', '检测到新的会议记录')
    addDecisionMessage('agent', '我看到刚才会议助手提取了一些新信息，让我重新分析一下...', 'S8 决策军师', '🧠')

    // 重置Agent状态
    resetAgentStatus()

    // 加载新报告
    try {
      const response = await axios.get('/api/s8/report/current')

      if (response.data.success) {
        const newReport = response.data.report
        const reportSummary = formatReportSummary(newReport)

        // 添加过渡语
        let updateMessage = '好的，基于这些新的会议信息，我更新了分析：\n\n'
        updateMessage += reportSummary

        // 如果有对比信息，说明变更原因
        if (data.comparison && data.comparison.revision_summary) {
          updateMessage += `\n\n这次主要是因为：${data.comparison.revision_summary}`
        }

        addDecisionMessage('agent', updateMessage, 'S8 决策军师', '🧠')
      }
    } catch (error) {
      console.error('加载报告失败:', error)
      addDecisionMessage('agent', '抱歉，更新报告时遇到了一些问题。', 'S8 决策军师', '🧠')
    }
  }

  // 处理节点状态更新
  const handleNodeStatus = (data) => {
    const { node, status, message, output } = data
    setAgentStatus(prev => ({
      ...prev,
      [node]: {
        ...prev[node],
        status,
        message,
        output: output || prev[node].output
      }
    }))
  }

  // 重置Agent状态
  const resetAgentStatus = () => {
    setAgentStatus(prev => ({
      summary: { ...prev.summary, status: 'idle', message: '等待中', output: null },
      risk: { ...prev.risk, status: 'idle', message: '等待中', output: null },
      recommendation: { ...prev.recommendation, status: 'idle', message: '等待中', output: null }
    }))
  }

  // 打开Agent详情
  const handleAgentClick = (agentType) => {
    const agentData = {
      summary: { name: '汇总助手', icon: '📊', ...agentStatus.summary },
      risk: { name: '风险助手', icon: '⚠️', ...agentStatus.risk },
      recommendation: { name: '建议助手', icon: '💡', ...agentStatus.recommendation }
    }
    setSelectedAgent(agentData[agentType])
  }

  return (
    <ScenarioTemplate
      scenarioId="S8"
      title="AI决策军师"
      description="双Agent协同：决策军师 + 会议助手，实时对话式决策支持"
      highlight="企业大脑"
    >
      <div className="grid grid-cols-3 gap-6" style={{ height: 'calc(100vh - 220px)' }}>
        {/* 左侧：决策军师聊天界面 (2/3) */}
        <div className="col-span-2 flex flex-col gap-4 min-h-0">
          {/* Agent团队状态 */}
          <div className="bg-gradient-to-r from-slate-800/50 to-slate-900/50 rounded-lg p-4 border border-slate-700 flex-shrink-0">
            <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
              <span>👥</span>
              <span>Agent 团队协同 (点击查看详情)</span>
            </h3>
            <div className="grid grid-cols-3 gap-3">
              <AgentCard
                name="汇总助手"
                icon="📊"
                status={agentStatus.summary.status}
                message={agentStatus.summary.message}
                output={agentStatus.summary.output}
                onClick={() => handleAgentClick('summary')}
              />
              <AgentCard
                name="风险助手"
                icon="⚠️"
                status={agentStatus.risk.status}
                message={agentStatus.risk.message}
                output={agentStatus.risk.output}
                onClick={() => handleAgentClick('risk')}
              />
              <AgentCard
                name="建议助手"
                icon="💡"
                status={agentStatus.recommendation.status}
                message={agentStatus.recommendation.message}
                output={agentStatus.recommendation.output}
                onClick={() => handleAgentClick('recommendation')}
              />
            </div>
          </div>

          {/* 决策军师聊天区域 */}
          <div className="flex-1 min-h-0 bg-slate-800/50 rounded-lg border border-slate-700/50 flex flex-col overflow-hidden">
            {/* 头部 */}
            <div className="px-5 py-3 border-b border-slate-700/50 bg-slate-800/80 backdrop-blur-sm flex items-center gap-3">
              <span className="text-xl">🧠</span>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-200 text-sm">S8 决策军师</h3>
                <p className="text-xs text-gray-500">自动分析经营数据，生成决策建议</p>
              </div>
            </div>

            {/* 消息列表 */}
            <div ref={decisionChatRef} className="flex-1 overflow-y-auto">
              {decisionMessages.length === 0 && (
                <div className="flex items-center justify-center h-full text-gray-500 text-sm">
                  正在初始化...
                </div>
              )}
              {decisionMessages.map((msg, idx) => (
                <ChatMessage
                  key={idx}
                  role={msg.role}
                  content={msg.content}
                  agentName={msg.agentName}
                  icon={msg.icon}
                  streaming={isGenerating && idx === decisionMessages.length - 1}
                />
              ))}
            </div>

            {/* 输入框 */}
            <div className="border-t border-slate-700/50 bg-slate-800/80 backdrop-blur-sm p-3">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={decisionInput}
                  onChange={(e) => setDecisionInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSendDecision()
                    }
                  }}
                  placeholder="向决策军师提问... (Enter发送)"
                  className="flex-1 bg-slate-700/50 border border-slate-600/50 rounded-lg px-4 py-2.5 text-gray-200 text-sm placeholder-gray-500 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/20 transition-all"
                  disabled={isGenerating}
                />
                <button
                  onClick={handleSendDecision}
                  disabled={!decisionInput.trim() || isGenerating}
                  className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-700 disabled:text-gray-500 text-white text-sm font-medium rounded-lg transition-all disabled:cursor-not-allowed shadow-sm hover:shadow-md"
                >
                  发送
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 右侧：会议助手聊天界面 (1/3) */}
        <div className="flex flex-col gap-4 min-h-0">
          <div className="flex-1 min-h-0 bg-slate-800/50 rounded-lg border border-slate-700/50 flex flex-col overflow-hidden">
            {/* 头部 */}
            <div className="px-5 py-3 border-b border-slate-700/50 bg-slate-800/80 backdrop-blur-sm flex items-center gap-3">
              <span className="text-xl">📝</span>
              <div className="flex-1">
                <h3 className="font-semibold text-gray-200 text-sm">会议助手</h3>
                <p className="text-xs text-gray-500">提取会议关键信息</p>
              </div>
            </div>

            {/* 消息列表 */}
            <div ref={meetingChatRef} className="flex-1 overflow-y-auto">
              {meetingMessages.length === 0 && (
                <div className="flex items-center justify-center h-full text-center text-gray-500 text-sm px-6">
                  <div>
                    <p className="mb-1.5">在下方输入会议记录</p>
                    <p className="text-xs text-gray-600">会议助手将自动提取关键信息</p>
                  </div>
                </div>
              )}
              {meetingMessages.map((msg, idx) => (
                <ChatMessage
                  key={idx}
                  role={msg.role}
                  content={msg.content}
                  agentName={msg.agentName}
                  icon={msg.icon}
                />
              ))}
            </div>

            {/* 输入框 */}
            <div className="border-t border-slate-700/50 bg-slate-800/80 backdrop-blur-sm p-3">
              <textarea
                value={meetingInput}
                onChange={(e) => setMeetingInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.ctrlKey) {
                    e.preventDefault()
                    handleSendMeeting()
                  }
                }}
                placeholder="粘贴会议记录... (Ctrl+Enter发送)"
                className="w-full bg-slate-700/50 border border-slate-600/50 rounded-lg px-4 py-2.5 text-gray-200 text-sm placeholder-gray-500 min-h-[100px] resize-none focus:outline-none focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/20 transition-all"
              />
              <div className="flex gap-2 mt-2">
                <button
                  onClick={handleSendMeeting}
                  disabled={!meetingInput.trim()}
                  className="flex-1 px-4 py-2.5 bg-violet-600 hover:bg-violet-700 disabled:bg-slate-700 disabled:text-gray-500 text-white text-sm font-medium rounded-lg transition-all disabled:cursor-not-allowed shadow-sm hover:shadow-md"
                >
                  发送
                </button>
                <button
                  onClick={() => setMeetingInput(exampleMeetingNotes)}
                  className="px-4 py-2.5 bg-slate-700/50 hover:bg-slate-600 border border-slate-600/50 text-gray-300 text-sm rounded-lg transition-all"
                  title="加载示例"
                >
                  示例
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Agent详情弹窗 */}
      {selectedAgent && (
        <AgentDetailModal
          agent={selectedAgent}
          onClose={() => setSelectedAgent(null)}
        />
      )}
    </ScenarioTemplate>
  )
}

// 示例会议记录
const exampleMeetingNotes = `市场部10月29日紧急会议纪要

参与人：张总、市场部李经理、内容团队负责人

会议要点：
1. Q4营销策略调整：明确主推三大产品线（AI客服、智能营销、数据分析）
2. 重点渠道调整为小红书和抖音，预算分配比例4:3:3
3. 近期发现小红书内容同质化严重，转化率从3.5%降至2.8%
4. 立即行动：加强内容差异化，避免与竞品重复

决议：李经理负责在11月5日前完成内容策略优化`

export default S8Decision
