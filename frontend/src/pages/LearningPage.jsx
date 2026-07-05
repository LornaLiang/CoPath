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
import {
  Avatar,
  Button,
  Card,
  Collapse,
  Input,
  Progress,
  Radio,
  Space,
  Tabs,
  Tag,
  message,
} from 'antd'
import { useState } from 'react'

import PageHeader from '../components/PageHeader'
import { mockDialogues, mockLearningCurrent, mockResources } from '../services/mockData'

const { TextArea } = Input

function LearningPage() {
  const [quizAnswer, setQuizAnswer] = useState()
  const [chatInput, setChatInput] = useState('')
  const [localMessages, setLocalMessages] = useState([])

  const sendMessage = () => {
    const value = chatInput.trim()
    if (!value) {
      message.warning('请输入问题')
      return
    }
    setLocalMessages((items) => [...items, value])
    setChatInput('')
    message.info('问题已加入 Mock 对话，真实发送将在 Milestone 5 联调')
  }

  const learningContent = (
    <div className="lesson-copy">
      <h3>1. 什么是调用栈？</h3>
      <p className="lesson-lead">调用栈是一种用于管理函数调用的数据结构。每次调用函数时，系统会压入一个栈帧；函数返回时，再从栈顶弹出。</p>
      <h3>2. 函数如何返回原来的位置？</h3>
      <pre className="code-block"><code>{`def greet(name):
    message = "Hello, " + name
    return message

result = greet("Tom")  # 栈帧保存返回位置
print(result)`}</code></pre>
      <div className="lesson-tip"><BulbOutlined /><span><strong>关键提示</strong>调用栈遵循“后进先出”，最新调用的函数会最先返回。</span></div>
    </div>
  )

  const tabItems = [
    { key: 'content', label: '学习内容', children: learningContent },
    { key: 'code', label: '示例代码', children: <div className="lesson-copy"><pre className="code-block"><code>{`def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)`}</code></pre><p>试着跟踪每一次函数调用，并记录每个栈帧中的 n。</p></div> },
    { key: 'quiz', label: '练习题', children: <div className="quiz-panel"><strong>执行 factorial(3) 时，调用栈中最多有几个 factorial 栈帧？</strong><Radio.Group value={quizAnswer} onChange={(event) => setQuizAnswer(event.target.value)}><Space direction="vertical"><Radio value="2">2 个</Radio><Radio value="3">3 个</Radio><Radio value="4">4 个</Radio></Space></Radio.Group><Button type="primary" disabled={!quizAnswer} onClick={() => message.success(quizAnswer === '3' ? '回答正确！' : '再想想递归终止条件')}>提交答案</Button></div> },
    { key: 'notes', label: '知识笔记', children: <div className="lesson-copy"><TextArea rows={8} placeholder="记录你对调用栈的理解…" /><Button onClick={() => message.success('笔记已暂存（Mock）')}>保存笔记</Button></div> },
  ]

  return (
    <div className="page learning-page">
      <PageHeader
        title="我的学习"
        description="沿着当前路径学习知识点，并随时向 AI 助手提问。"
        extra={<Space><Button icon={<LeftOutlined />} onClick={() => message.info('已定位到上一个节点（Mock）')}>上一个节点</Button><Button type="primary" onClick={() => message.info('请先完成当前知识点反馈（Mock）')}>下一个节点</Button></Space>}
      />

      <div className="learning-node-strip">
        <div className="learning-node-strip__icon"><CodeOutlined /></div>
        <div className="learning-node-strip__main">
          <span>当前知识点</span>
          <strong>调用栈 <small>Call Stack</small></strong>
          <p>{mockLearningCurrent.current_node.description}</p>
        </div>
        <div className="learning-node-strip__meta"><span>所属路径</span><b>基础补全路径</b></div>
        <div className="learning-node-strip__meta"><span>难度</span><Tag color="gold">进阶</Tag></div>
        <div className="learning-node-strip__meta"><span>前置知识</span><b>函数 · 返回值</b></div>
        <div className="learning-node-strip__progress"><Progress type="circle" percent={60} size={66} strokeColor="#21b879" /><small>节点进度</small></div>
      </div>

      <div className="learning-workspace">
        <div className="learning-main-column">
          <Card className="soft-card lesson-card">
            <Tabs items={tabItems} />
          </Card>

          <Card className="soft-card resource-card" title="推荐学习资源">
            <div className="resource-list">
              {mockResources.map((resource, index) => (
                <div className="resource-item" key={resource.resource_id}>
                  <span className={`resource-item__icon resource-item__icon--${index}`}>
                    {resource.resource_type === 'exercise' ? <PlayCircleOutlined /> : <FileTextOutlined />}
                  </span>
                  <div><strong>{resource.title}</strong><p>{resource.content}</p></div>
                  <Button size="small" onClick={() => message.info(`打开“${resource.title}”（Mock）`)}>查看</Button>
                </div>
              ))}
            </div>
          </Card>

          <Card className="soft-card feedback-card" title="这个知识点理解得怎么样？">
            <Space wrap>
              <Button icon={<CheckCircleOutlined />} onClick={() => message.success('已记录：我理解了（Mock）')}>我理解了</Button>
              <Button onClick={() => message.info('已记录：仍有困惑（Mock）')}>我还不理解</Button>
              <Button onClick={() => message.info('已记录：需要案例（Mock）')}>换个例子</Button>
              <Button onClick={() => message.info('已记录：希望降低难度（Mock）')}>降低难度</Button>
              <Button type="primary" onClick={() => message.success('已提交进入下一节点（Mock）')}>进入下一节点</Button>
            </Space>
          </Card>
        </div>

        <aside className="learning-aside">
          <Card className="soft-card chat-card" title={<Space><RobotOutlined /> AI 学习助手 <Tag color="blue">Mock</Tag></Space>}>
            <div className="chat-stream">
              <div className="chat-message chat-message--assistant">
                <Avatar icon={<RobotOutlined />} />
                <div>你好，我可以陪你一起拆解调用栈。哪里最让你困惑？</div>
              </div>
              <div className="chat-message chat-message--user"><div>{mockDialogues[0].user_message}</div></div>
              <div className="chat-message chat-message--assistant">
                <Avatar icon={<RobotOutlined />} />
                <div>{mockDialogues[0].ai_response}</div>
              </div>
              {localMessages.map((item, index) => <div className="chat-message chat-message--user" key={`${item}-${index}`}><div>{item}</div></div>)}
            </div>
            <Collapse ghost size="small" items={[{ key: 'signal', label: '查看学习状态信号', children: <pre className="signal-code">{JSON.stringify(mockDialogues[0].extracted_signal, null, 2)}</pre> }]} />
            <div className="chat-composer">
              <Input value={chatInput} onChange={(event) => setChatInput(event.target.value)} onPressEnter={sendMessage} placeholder="输入你的问题…" />
              <Button type="primary" icon={<SendOutlined />} onClick={sendMessage} />
            </div>
          </Card>

          <Card className="soft-card path-mini-card" title="当前路径">
            {['函数', '参数传递', '返回值', '调用栈', '递归'].map((node, index) => (
              <div className={`path-mini-node ${index === 3 ? 'path-mini-node--active' : ''}`} key={node}>
                <span>{index < 3 ? <CheckCircleOutlined /> : index === 3 ? <ThunderboltOutlined /> : index + 1}</span>
                <b>{node}</b>
              </div>
            ))}
          </Card>
        </aside>
      </div>
    </div>
  )
}

export default LearningPage
