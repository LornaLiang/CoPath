import {
  BulbOutlined,
  CheckCircleOutlined,
  CodeOutlined,
  FileTextOutlined,
  LeftOutlined,
  PlayCircleOutlined,
  RobotOutlined,
  SendOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons'
import { Avatar, Button, Card, Collapse, Empty, Input, Progress, Radio, Space, Tabs, Tag, message } from 'antd'
import { useMemo, useState } from 'react'

import PageHeader from '../components/PageHeader'
import PageState from '../components/PageState'
import useAsyncData from '../hooks/useAsyncData'
import { useAppData } from '../hooks/useAppData'
import { dialogueApi, learningApi, resourceApi } from '../services/copathApi'

const { TextArea } = Input

function LearningPage() {
  const { currentStudent, currentPath, health, loading: appLoading, error: appError, refresh } = useAppData()
  const studentId = currentStudent?.student_id
  const [quizAnswer, setQuizAnswer] = useState()
  const [chatInput, setChatInput] = useState('')
  const [localMessages, setLocalMessages] = useState([])
  const [sending, setSending] = useState(false)

  const { data, loading, error, reload } = useAsyncData(
    () => studentId
      ? Promise.all([learningApi.getCurrent(studentId), resourceApi.getCurrent(studentId), dialogueApi.list(studentId)]).then(([learning, resources, dialogues]) => ({ learning, resources, dialogues }))
      : Promise.resolve(null),
    [studentId],
  )

  const currentNode = data?.learning.current_node
  const latestSignal = localMessages.findLast?.((item) => item.signal)?.signal || data?.dialogues.at(-1)?.extracted_signal || {}

  const sendMessage = async () => {
    const value = chatInput.trim()
    if (!value || !currentNode) return message.warning('请输入问题')
    setSending(true)
    setLocalMessages((items) => [...items, { role: 'user', content: value }])
    setChatInput('')
    try {
      const response = await dialogueApi.chat(studentId, currentNode.node_id, value)
      setLocalMessages((items) => [...items, { role: 'assistant', content: response.reply, signal: response.signal }])
      if (response.path_adjusted) {
        await refresh()
        await reload()
        setLocalMessages([])
        message.info('系统已根据学习状态更新学习路径')
      }
    } catch (requestError) {
      message.error(requestError.message)
    } finally {
      setSending(false)
    }
  }

  const submitQuiz = async () => {
    const correct = quizAnswer === '3'
    try {
      await learningApi.saveEvent({ student_id: studentId, node_id: currentNode.node_id, event_type: 'quiz', result: correct ? 'correct' : 'wrong', score: correct ? 1 : 0, time_spent: 60 })
      message[correct ? 'success' : 'warning'](correct ? '回答正确，学习事件已保存' : '答案不正确，学习事件已保存')
      await reload()
      await refresh()
    } catch (requestError) {
      message.error(requestError.message)
    }
  }

  const submitFeedback = async (feedbackType) => {
    try {
      const response = await learningApi.submitFeedback({ student_id: studentId, node_id: currentNode.node_id, feedback_type: feedbackType })
      message.success(response.message)
    } catch (requestError) {
      message.error(requestError.message)
    }
  }

  const learningContent = useMemo(() => (
    <div className="lesson-copy">
      <h3>知识点说明</h3><p className="lesson-lead">{currentNode?.description}</p>
      <h3>Python 示例</h3><pre className="code-block"><code>{`def trace_call(value):
    if value <= 1:
        return value
    return trace_call(value - 1)

result = trace_call(3)`}</code></pre>
      <div className="lesson-tip"><BulbOutlined /><span><strong>学习提示</strong>结合推荐资源观察每一次函数调用和返回的位置。</span></div>
    </div>
  ), [currentNode])

  if (appLoading || loading) return <PageState loading />
  if (appError || error) return <PageState error={appError || error} onRetry={appError ? refresh : reload} />
  if (!data || !currentPath || !currentNode) return <PageState empty emptyDescription="当前学生尚无可学习节点" />

  const tabItems = [
    { key: 'content', label: '学习内容', children: learningContent },
    { key: 'code', label: '示例代码', children: <div className="lesson-copy"><pre className="code-block"><code>{`def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)`}</code></pre><p>跟踪每一次调用，并记录调用栈中的 n。</p></div> },
    { key: 'quiz', label: '练习题', children: <div className="quiz-panel"><strong>执行 factorial(3) 时，调用栈中最多有几个 factorial 栈帧？</strong><Radio.Group value={quizAnswer} onChange={(event) => setQuizAnswer(event.target.value)}><Space direction="vertical"><Radio value="2">2 个</Radio><Radio value="3">3 个</Radio><Radio value="4">4 个</Radio></Space></Radio.Group><Button type="primary" disabled={!quizAnswer} onClick={submitQuiz}>提交答案</Button></div> },
    { key: 'notes', label: '知识笔记', children: <div className="lesson-copy"><TextArea rows={8} placeholder={`记录你对${currentNode.name}的理解…`} /><Button onClick={() => message.success('笔记已在当前页面暂存')}>保存笔记</Button></div> },
  ]

  return (
    <div className="page learning-page">
      <PageHeader title="我的学习" description="当前知识点、资源和对话均来自后端数据库。" extra={<Space><Button icon={<LeftOutlined />} onClick={() => message.info('当前 API 暂未提供回退节点操作')}>上一个节点</Button><Button type="primary" onClick={() => submitFeedback('next_node')}>下一个节点</Button></Space>} />

      <div className="learning-node-strip">
        <div className="learning-node-strip__icon"><CodeOutlined /></div><div className="learning-node-strip__main"><span>当前知识点</span><strong>{currentNode.name} <small>{currentNode.node_id}</small></strong><p>{currentNode.description}</p></div><div className="learning-node-strip__meta"><span>所属路径</span><b>{currentPath.path_name}</b></div><div className="learning-node-strip__meta"><span>路径状态</span><Tag color="green">{currentPath.status}</Tag></div><div className="learning-node-strip__meta"><span>节点位置</span><b>{data.learning.path_progress.completed + 1} / {data.learning.path_progress.total}</b></div><div className="learning-node-strip__progress"><Progress type="circle" percent={data.learning.path_progress.percent} size={66} strokeColor="#21b879" /><small>路径进度</small></div>
      </div>

      <div className="learning-workspace">
        <div className="learning-main-column">
          <Card className="soft-card lesson-card"><Tabs items={tabItems} /></Card>
          <Card className="soft-card resource-card" title="推荐学习资源"><div className="resource-list">{data.resources.length ? data.resources.map((resource, index) => <div className="resource-item" key={resource.resource_id}><span className={`resource-item__icon resource-item__icon--${index % 2}`}>{resource.resource_type === 'exercise' ? <PlayCircleOutlined /> : <FileTextOutlined />}</span><div><strong>{resource.title}</strong><p>{resource.content}</p></div><Button size="small" onClick={() => message.info(resource.url || resource.content)}>查看</Button></div>) : <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="当前节点暂无学习资源" />}</div></Card>
          <Card className="soft-card feedback-card" title="这个知识点理解得怎么样？"><Space wrap><Button icon={<CheckCircleOutlined />} onClick={() => submitFeedback('understood')}>我理解了</Button><Button onClick={() => submitFeedback('still_confused')}>我还不理解</Button><Button onClick={() => submitFeedback('need_example')}>换个例子</Button><Button onClick={() => submitFeedback('lower_difficulty')}>降低难度</Button><Button type="primary" onClick={() => submitFeedback('next_node')}>进入下一节点</Button></Space></Card>
        </div>

        <aside className="learning-aside">
          <Card className="soft-card chat-card" title={<Space><RobotOutlined /> AI 学习助手 <Tag color={health?.ai === 'available' ? 'blue' : 'default'}>{health?.ai || 'unknown'}</Tag></Space>}>
            <div className="chat-stream">
              {data.dialogues.length === 0 ? <div className="chat-message chat-message--assistant"><Avatar icon={<RobotOutlined />} /><div>当前没有历史对话。</div></div> : null}
              {data.dialogues.flatMap((dialogue) => [{ role: 'user', content: dialogue.user_message, key: `u-${dialogue.dialogue_id}` }, { role: 'assistant', content: dialogue.ai_response, key: `a-${dialogue.dialogue_id}` }]).concat(localMessages.map((item, index) => ({ ...item, key: `local-${index}` }))).map((item) => <div className={`chat-message chat-message--${item.role}`} key={item.key}>{item.role === 'assistant' ? <Avatar icon={<RobotOutlined />} /> : null}<div>{item.content}</div></div>)}
            </div>
            <Collapse ghost size="small" items={[{ key: 'signal', label: '查看最近学习状态信号', children: <pre className="signal-code">{JSON.stringify(latestSignal, null, 2)}</pre> }]} />
            <div className="chat-composer"><Input value={chatInput} onChange={(event) => setChatInput(event.target.value)} onPressEnter={sendMessage} placeholder="输入你的问题…" /><Button loading={sending} type="primary" icon={<SendOutlined />} onClick={sendMessage} /></div>
          </Card>
          <Card className="soft-card path-mini-card" title="当前路径">{currentPath.nodes.map((node, index) => <div className={`path-mini-node ${node.status === 'learning' ? 'path-mini-node--active' : ''}`} key={node.node_id}><span>{node.status === 'completed' ? <CheckCircleOutlined /> : node.status === 'learning' ? <ThunderboltOutlined /> : index + 1}</span><b>{node.name}</b></div>)}</Card>
        </aside>
      </div>
    </div>
  )
}

export default LearningPage
