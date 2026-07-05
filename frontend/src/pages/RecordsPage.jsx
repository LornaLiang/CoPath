import {
  ApartmentOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  DownloadOutlined,
  MessageOutlined,
  RobotOutlined,
  TrophyOutlined,
} from '@ant-design/icons'
import { Button, Card, Collapse, Select, Space, Table, Tabs, Tag, message } from 'antd'

import MetricCard from '../components/MetricCard'
import PageHeader from '../components/PageHeader'
import { mockDialogues, mockLearningEvents, mockSwitchLogs } from '../services/mockData'

const eventTypeLabels = { learn: '学习', quiz: '测验', finish: '完成', pause: '暂停' }
const resultLabels = { completed: '已完成', correct: '正确', wrong: '错误' }

function RecordsPage() {
  const eventColumns = [
    { title: '时间', dataIndex: 'created_at', width: 150, sorter: (a, b) => a.created_at.localeCompare(b.created_at) },
    { title: '知识点', dataIndex: 'node_name', filters: [{ text: '函数', value: '函数' }, { text: '调用栈', value: '调用栈' }], onFilter: (value, record) => record.node_name === value },
    { title: '行为类型', dataIndex: 'event_type', render: (value) => <Tag color="blue">{eventTypeLabels[value]}</Tag> },
    { title: '结果', dataIndex: 'result', render: (value) => value ? <Tag color={value === 'wrong' ? 'error' : 'success'}>{resultLabels[value] || value}</Tag> : '—' },
    { title: '得分', dataIndex: 'score', sorter: (a, b) => (a.score || 0) - (b.score || 0), render: (value) => value == null ? '—' : `${Math.round(value * 100)}%` },
    { title: '学习时长', dataIndex: 'time_spent', render: (value) => value ? `${Math.round(value / 60)} 分钟` : '—' },
  ]

  const switchColumns = [
    { title: '时间', dataIndex: 'created_at', width: 150 },
    { title: '原路径', dataIndex: 'old_path_name' },
    { title: '新路径', dataIndex: 'new_path_name' },
    { title: '触发方式', dataIndex: 'trigger_type', render: () => <Tag color="purple">AI 对话</Tag> },
    { title: '调整原因', dataIndex: 'reason' },
  ]

  const dialogueItems = mockDialogues.map((dialogue) => ({
    key: dialogue.dialogue_id,
    label: <div className="dialogue-collapse-label"><span><MessageOutlined /> {dialogue.user_message}</span><small>{dialogue.created_at}</small></div>,
    children: (
      <div className="dialogue-record">
        <div><RobotOutlined /><p>{dialogue.ai_response}</p></div>
        <Collapse ghost size="small" items={[{ key: 'signal', label: '结构化学习状态信号', children: <pre className="signal-code">{JSON.stringify(dialogue.extracted_signal, null, 2)}</pre> }]} />
      </div>
    ),
  }))

  const tabItems = [
    { key: 'events', label: `学习事件 ${mockLearningEvents.length}`, children: <Table rowKey="event_id" columns={eventColumns} dataSource={mockLearningEvents} pagination={{ pageSize: 5, hideOnSinglePage: true }} size="middle" /> },
    { key: 'dialogues', label: `AI 对话 ${mockDialogues.length}`, children: <Collapse items={dialogueItems} className="dialogue-collapse" /> },
    { key: 'switches', label: `路径调整 ${mockSwitchLogs.length}`, children: <Table rowKey="switch_id" columns={switchColumns} dataSource={mockSwitchLogs} pagination={false} /> },
  ]

  return (
    <div className="page records-page">
      <PageHeader
        title="学习记录"
        description="查看学习事件、AI 对话与路径调整的完整历史。"
        extra={<Button icon={<DownloadOutlined />} onClick={() => message.success('学习记录导出任务已创建（Mock）')}>导出记录</Button>}
      />

      <div className="metrics-grid records-metrics">
        <MetricCard icon={<ClockCircleOutlined />} label="总学习时长" value="3.8 小时" hint="本周 +1.6 小时" />
        <MetricCard icon={<CheckCircleOutlined />} label="完成事件" value="12 条" hint="完成率 75%" tone="green" />
        <MetricCard icon={<MessageOutlined />} label="AI 对话" value="4 次" hint="识别 2 个薄弱点" tone="purple" />
        <MetricCard icon={<ApartmentOutlined />} label="路径调整" value="2 次" hint="均有完整解释" tone="orange" />
      </div>

      <Card className="soft-card record-filter-card">
        <Space wrap>
          <span>时间范围</span>
          <Select defaultValue="all" options={[{ value: 'all', label: '全部时间' }, { value: 'week', label: '最近 7 天' }, { value: 'month', label: '最近 30 天' }]} />
          <span>学习内容</span>
          <Select defaultValue="all" options={[{ value: 'all', label: '全部知识点' }, { value: 'call_stack', label: '调用栈' }, { value: 'recursion', label: '递归' }]} />
        </Space>
      </Card>

      <Card className="soft-card record-table-card">
        <Tabs items={tabItems} />
      </Card>

      <Card className="soft-card learning-summary-card">
        <div className="learning-summary-card__icon"><TrophyOutlined /></div>
        <div>
          <span>阶段性学习总结</span>
          <h3>函数基础较稳定，当前主要薄弱点是调用栈和返回值。</h3>
          <p>建议继续采用基础补全路径，完成调用栈可视化练习后再进入递归。该总结为 Milestone 4 Mock 展示。</p>
        </div>
        <Tag color="blue">AI 总结 · Mock</Tag>
      </Card>
    </div>
  )
}

export default RecordsPage
