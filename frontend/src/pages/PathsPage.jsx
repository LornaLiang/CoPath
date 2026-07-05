import {
  ApartmentOutlined,
  BulbOutlined,
  CheckCircleFilled,
  ClockCircleOutlined,
  CompassOutlined,
  RobotOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons'
import { Button, Card, Col, Progress, Radio, Row, Space, Steps, Table, Tag, message } from 'antd'
import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import EChart from '../components/EChart'
import PageHeader from '../components/PageHeader'
import { mockCurrentPath, mockPaths, mockSwitchLogs } from '../services/mockData'

const pathIconMap = {
  basic: <CompassOutlined />,
  example: <ApartmentOutlined />,
  fast: <ThunderboltOutlined />,
}

function PathsPage() {
  const navigate = useNavigate()
  const [selectedPath, setSelectedPath] = useState('P001')
  const selected = mockPaths.find((path) => path.path_id === selectedPath)

  const trendOption = useMemo(() => ({
    grid: { left: 8, right: 10, top: 12, bottom: 18, containLabel: true },
    xAxis: { type: 'category', data: ['函数', '参数', '返回值', '调用栈', '递归'], axisLine: { lineStyle: { color: '#dce4ef' } }, axisLabel: { color: '#8793a7', fontSize: 10 } },
    yAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { color: '#edf1f6' } }, axisLabel: { show: false } },
    tooltip: { trigger: 'axis' },
    series: [{ type: 'line', smooth: true, data: [82, 74, 55, 30, 18], symbolSize: 7, lineStyle: { width: 3, color: '#2563eb' }, itemStyle: { color: '#2563eb' }, areaStyle: { color: 'rgba(37,99,235,.08)' } }],
  }), [])

  const switchColumns = [
    { title: '时间', dataIndex: 'created_at', width: 140 },
    { title: '原路径', dataIndex: 'old_path_name' },
    { title: '新路径', dataIndex: 'new_path_name' },
    { title: '触发方式', dataIndex: 'trigger_type', render: () => <Tag color="purple">AI 对话</Tag> },
    { title: '调整说明', dataIndex: 'reason' },
  ]

  return (
    <div className="page paths-page">
      <PageHeader
        title="学习路径"
        description="同一目标提供多种学习方式；你可以比较路径并查看当前学习进度。"
        extra={<Button type="primary" onClick={() => navigate('/learning')}>进入学习</Button>}
      />

      <div className="path-overview-strip">
        <div><span>当前目标</span><strong>掌握递归</strong></div>
        <div><span>推荐路径</span><strong>基础补全路径</strong></div>
        <div><span>当前节点</span><strong>调用栈</strong></div>
        <div><span>路径状态</span><Tag color="success">进行中</Tag></div>
        <div className="path-overview-strip__progress"><span>整体进度</span><Progress percent={60} size="small" /></div>
      </div>

      <Row gutter={16}>
        <Col span={8}>
          <Card className="soft-card path-picker" title="候选路径">
            <Radio.Group value={selectedPath} onChange={(event) => setSelectedPath(event.target.value)}>
              {mockPaths.map((path) => (
                <Radio.Button value={path.path_id} key={path.path_id} className={path.is_current ? 'path-option--recommended' : ''}>
                  <span className={`path-option__icon path-option__icon--${path.path_type}`}>{pathIconMap[path.path_type]}</span>
                  <span className="path-option__copy">
                    <strong>{path.path_name}</strong>
                    <small>{path.subtitle}</small>
                  </span>
                  {path.is_current ? <Tag color="success">当前推荐</Tag> : null}
                </Radio.Button>
              ))}
            </Radio.Group>

            <div className="path-comparison">
              <div><span>预计时长</span><b>{selected.duration}</b></div>
              <div><span>难度曲线</span><b>{selected.difficulty}</b></div>
              <div><span>知识节点</span><b>{selected.nodes.length} 个</b></div>
            </div>
            <Button block disabled={selected.is_current} onClick={() => message.success(`已提交切换至“${selected.path_name}”（Mock）`)}>
              {selected.is_current ? '当前正在使用' : '选择这条路径'}
            </Button>
          </Card>
        </Col>

        <Col span={16}>
          <Card className="soft-card current-path-card" title={<Space><CheckCircleFilled className="text-green" /> 当前路径 · {mockCurrentPath.path_name}</Space>}>
            <Steps
              current={3}
              responsive={false}
              items={mockCurrentPath.nodes.map((node) => ({ title: node.name, description: node.status === 'learning' ? '当前学习' : node.status === 'completed' ? '已掌握' : '待学习' }))}
            />
            <div className="current-path-card__insight">
              <RobotOutlined />
              <div><strong>推荐理由</strong><p>{mockCurrentPath.reason}</p></div>
            </div>
          </Card>

          <Row gutter={16} className="path-detail-row">
            <Col span={16}>
              <Card className="soft-card" title="掌握度趋势">
                <EChart option={trendOption} height={178} />
              </Card>
            </Col>
            <Col span={8}>
              <Card className="soft-card path-facts" title="路径详情">
                <p><ClockCircleOutlined /> 预计时长 <strong>8–10 小时</strong></p>
                <p><BulbOutlined /> 已学节点 <strong>3 / 5</strong></p>
                <p><ApartmentOutlined /> 路径调整 <strong>1 次</strong></p>
                <p><CompassOutlined /> 当前阶段 <strong>前置补全</strong></p>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>

      <Card className="soft-card path-log-card" title="路径切换记录">
        <Table rowKey="switch_id" columns={switchColumns} dataSource={mockSwitchLogs} pagination={false} size="small" />
      </Card>
    </div>
  )
}

export default PathsPage
