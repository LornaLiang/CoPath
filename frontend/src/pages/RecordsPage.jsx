import {
  ApartmentOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  DownloadOutlined,
  MessageOutlined,
  RobotOutlined,
  TrophyOutlined,
} from '@ant-design/icons'
import { Button, Card, Collapse, Empty, Select, Space, Table, Tabs, Tag } from 'antd'

import MetricCard from '../components/MetricCard'
import PageHeader from '../components/PageHeader'
import PageState from '../components/PageState'
import useAsyncData from '../hooks/useAsyncData'
import { useAppData } from '../hooks/useAppData'
import { dialogueApi, learningApi, pathApi } from '../services/copathApi'

const eventTypeLabels = { learn: '学习', quiz: '测验', finish: '完成', pause: '暂停' }
const resultLabels = { completed: '已完成', correct: '正确', wrong: '错误' }

function RecordsPage() {
  const { currentStudent, loading: appLoading, error: appError, refresh } = useAppData()
  const studentId = currentStudent?.student_id
  const { data, loading, error, reload } = useAsyncData(
    () => studentId
      ? Promise.all([learningApi.listEvents(studentId), dialogueApi.list(studentId), pathApi.listSwitchLogs(studentId), learningApi.getSummary(studentId)]).then(([events, dialogues, switchLogs, summary]) => ({ events, dialogues, switchLogs, summary }))
      : Promise.resolve(null),
    [studentId],
  )

  if (appLoading || loading) return <PageState loading />
  if (appError || error) return <PageState error={appError || error} onRetry={appError ? refresh : reload} />
  if (!data || !currentStudent) return <PageState empty emptyDescription="当前学生尚无学习记录" />

  const eventColumns = [
    { title: '时间', dataIndex: 'created_at', width: 150, sorter: (a, b) => a.created_at.localeCompare(b.created_at) },
    { title: '知识点', dataIndex: 'node_name', filters: [...new Set(data.events.map((event) => event.node_name))].map((name) => ({ text: name, value: name })), onFilter: (value, record) => record.node_name === value },
    { title: '行为类型', dataIndex: 'event_type', render: (value) => <Tag color="blue">{eventTypeLabels[value] || value}</Tag> },
    { title: '结果', dataIndex: 'result', render: (value) => value ? <Tag color={value === 'wrong' ? 'error' : 'success'}>{resultLabels[value] || value}</Tag> : '—' },
    { title: '得分', dataIndex: 'score', sorter: (a, b) => (a.score || 0) - (b.score || 0), render: (value) => value == null ? '—' : `${Math.round(value * 100)}%` },
    { title: '学习时长', dataIndex: 'time_spent', render: (value) => value ? `${Math.round(value / 60)} 分钟` : '—' },
  ]
  const switchColumns = [{ title: '时间', dataIndex: 'created_at', width: 150 }, { title: '原路径', dataIndex: 'old_path_name' }, { title: '新路径', dataIndex: 'new_path_name' }, { title: '触发方式', dataIndex: 'trigger_type', render: (value) => <Tag color="purple">{value}</Tag> }, { title: '调整原因', dataIndex: 'reason' }]
  const dialogueItems = data.dialogues.map((dialogue) => ({ key: dialogue.dialogue_id, label: <div className="dialogue-collapse-label"><span><MessageOutlined /> {dialogue.user_message}</span><small>{dialogue.created_at}</small></div>, children: <div className="dialogue-record"><div><RobotOutlined /><p>{dialogue.ai_response}</p></div></div> }))
  const tabItems = [{ key: 'events', label: `学习事件 ${data.events.length}`, children: <Table rowKey="event_id" columns={eventColumns} dataSource={data.events} pagination={{ pageSize: 6, hideOnSinglePage: true }} size="middle" locale={{ emptyText: '暂无学习事件' }} /> }, { key: 'dialogues', label: `AI 对话 ${data.dialogues.length}`, children: data.dialogues.length ? <Collapse items={dialogueItems} className="dialogue-collapse" /> : <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无 AI 对话" /> }, { key: 'switches', label: `路径调整 ${data.switchLogs.length}`, children: <Table rowKey="switch_id" columns={switchColumns} dataSource={data.switchLogs} pagination={false} locale={{ emptyText: '暂无路径调整记录' }} /> }]
  const totalSeconds = data.events.reduce((total, event) => total + (event.time_spent || 0), 0)
  const completedEvents = data.events.filter((event) => ['completed', 'correct'].includes(event.result)).length

  const exportRecords = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `copath-records-${studentId}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="page records-page">
      <PageHeader title="学习记录" description={`${currentStudent.name} 的学习事件、对话与路径调整历史。`} extra={<Button icon={<DownloadOutlined />} onClick={exportRecords}>导出记录</Button>} />
      <div className="metrics-grid records-metrics"><MetricCard icon={<ClockCircleOutlined />} label="总学习时长" value={`${Math.round(totalSeconds / 60)} 分钟`} hint={`${data.events.length} 条事件`} /><MetricCard icon={<CheckCircleOutlined />} label="完成事件" value={`${completedEvents} 条`} hint={`完成率 ${data.events.length ? Math.round(completedEvents / data.events.length * 100) : 0}%`} tone="green" /><MetricCard icon={<MessageOutlined />} label="AI 对话" value={`${data.dialogues.length} 次`} hint="来自 dialogue_logs" tone="purple" /><MetricCard icon={<ApartmentOutlined />} label="路径调整" value={`${data.switchLogs.length} 次`} hint="来自 path_switch_logs" tone="orange" /></div>
      <Card className="soft-card record-filter-card"><Space wrap><span>时间范围</span><Select defaultValue="all" options={[{ value: 'all', label: '全部时间' }]} /><span>当前学生</span><Tag color="blue">{currentStudent.name}</Tag></Space></Card>
      <Card className="soft-card record-table-card"><Tabs items={tabItems} /></Card>
      <Card className="soft-card learning-summary-card"><div className="learning-summary-card__icon"><TrophyOutlined /></div><div><span>阶段性学习总结</span><h3>{data.summary.summary}</h3><p>{data.summary.next_suggestion}</p></div><Tag color="blue">数据库摘要</Tag></Card>
    </div>
  )
}

export default RecordsPage
