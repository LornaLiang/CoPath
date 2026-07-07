import {
  ApartmentOutlined,
  BulbOutlined,
  CheckCircleFilled,
  CompassOutlined,
  RobotOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons'
import { Button, Card, Col, Empty, Modal, Progress, Radio, Row, Space, Steps, Table, Tag, message } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import EChart from '../components/EChart'
import PageHeader from '../components/PageHeader'
import PageState from '../components/PageState'
import useAsyncData from '../hooks/useAsyncData'
import { useAppData } from '../hooks/useAppData'
import { pathApi, profileApi } from '../services/copathApi'

const pathIconMap = { basic: <CompassOutlined />, example: <ApartmentOutlined />, fast: <ThunderboltOutlined /> }
const pathTypeLabels = { basic: '基础型', example: '案例型', fast: '快速型' }

function PathsPage() {
  const navigate = useNavigate()
  const { currentStudent, currentPath, goals, loading: appLoading, error: appError, refresh } = useAppData()
  const studentId = currentStudent?.student_id
  const goalId = currentStudent?.current_goal_id
  const [selectedPath, setSelectedPath] = useState(null)
  const [switching, setSwitching] = useState(false)
  const [pendingSuggestion, setPendingSuggestion] = useState(null)
  const [switchEvaluation, setSwitchEvaluation] = useState(null)

  const { data, loading, error, reload } = useAsyncData(
    () => studentId && goalId
      ? Promise.all([pathApi.listCandidates(studentId, goalId), pathApi.listSwitchLogs(studentId), profileApi.getMastery(studentId), pathApi.getPlan(studentId), pathApi.getPendingAdjustment(studentId)]).then(([candidates, logs, mastery, plan, pending]) => ({ candidates, logs, mastery, plan, pending }))
      : Promise.resolve(null),
    [studentId, goalId],
  )

  useEffect(() => {
    const active = data?.candidates.find((path) => path.is_current)
    if (active) setSelectedPath(active.path_id)
    setPendingSuggestion(data?.pending || null)
  }, [data])

  const selected = data?.candidates.find((path) => path.path_id === selectedPath)
  const goal = goals.find((item) => item.goal_id === goalId)
  const currentIndex = Math.max(0, currentPath?.nodes.findIndex((node) => node.status === 'learning') ?? 0)
  const completed = currentPath?.nodes.filter((node) => node.status === 'completed').length || 0
  const total = currentPath?.nodes.length || 0

  const trendOption = useMemo(() => ({
    grid: { left: 8, right: 10, top: 12, bottom: 18, containLabel: true },
    xAxis: { type: 'category', data: data?.mastery.map((item) => item.name) || [], axisLine: { lineStyle: { color: '#dce4ef' } }, axisLabel: { color: '#8793a7', fontSize: 10 } },
    yAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { color: '#edf1f6' } }, axisLabel: { show: false } },
    tooltip: { trigger: 'axis' },
    series: [{ type: 'line', smooth: true, data: data?.mastery.map((item) => Math.round(item.mastery * 100)) || [], symbolSize: 7, lineStyle: { width: 3, color: '#2563eb' }, itemStyle: { color: '#2563eb' }, areaStyle: { color: 'rgba(37,99,235,.08)' } }],
  }), [data])

  const switchPath = async () => {
    if (!selected || selected.is_current) return
    setSwitching(true)
    try {
      const evaluation = await pathApi.evaluateSwitch(studentId, selected.path_id)
      if (!evaluation.recommended) {
        setSwitchEvaluation({ evaluation, path: selected })
        return
      }
      await pathApi.switch(studentId, selected.path_id, '学生在学习路径页面手动切换。')
      await refresh()
      await reload()
      message.success(`已切换至“${selected.path_name}”`)
    } catch (requestError) {
      message.error(requestError.message)
    } finally {
      setSwitching(false)
    }
  }

  const overrideSwitch = async () => {
    if (!switchEvaluation) return
    setSwitching(true)
    try {
      await pathApi.evaluateSwitch(studentId, switchEvaluation.path.path_id, true)
      await refresh()
      await reload()
      message.warning(`已覆盖系统建议并切换至“${switchEvaluation.path.path_name}”`)
      setSwitchEvaluation(null)
    } catch (requestError) {
      message.error(requestError.message)
    } finally {
      setSwitching(false)
    }
  }

  const acceptSuggestion = async () => {
    if (!pendingSuggestion) return
    setSwitching(true)
    try {
      await pathApi.confirmAdjustment(studentId, pendingSuggestion.suggestion_id)
      await refresh()
      await reload()
      setPendingSuggestion(null)
      message.success('已按建议切换路径')
    } catch (requestError) {
      message.error(requestError.message)
    } finally {
      setSwitching(false)
    }
  }

  const rejectSuggestion = async () => {
    if (!pendingSuggestion) return
    setSwitching(true)
    try {
      await pathApi.rejectAdjustment(studentId, pendingSuggestion.suggestion_id)
      await reload()
      setPendingSuggestion(null)
      message.info('已暂不切换，继续当前路径')
    } catch (requestError) {
      message.error(requestError.message)
    } finally {
      setSwitching(false)
    }
  }

  const switchColumns = [
    { title: '时间', dataIndex: 'created_at', width: 145 },
    { title: '原路径', dataIndex: 'old_path_name' },
    { title: '新路径', dataIndex: 'new_path_name' },
    { title: '触发方式', dataIndex: 'trigger_type', render: (value) => <Tag color={value === 'manual' ? 'blue' : 'purple'}>{value}</Tag> },
    { title: '调整说明', dataIndex: 'reason' },
  ]

  if (appLoading || loading) return <PageState loading />
  if (appError || error) return <PageState error={appError || error} onRetry={appError ? refresh : reload} />
  if (!data || !currentPath) return <PageState empty emptyDescription="当前学生尚无学习路径" />
  if (!data.candidates.length) return <PageState empty emptyDescription="当前目标尚无候选路径" />

  return (
    <div className="page paths-page">
      <PageHeader title="学习路径" description="候选路径与当前进度均来自 FastAPI 和 SQLite。" extra={<Button type="primary" onClick={() => navigate('/learning')}>进入学习</Button>} />

      <div className="path-overview-strip">
        <div><span>当前目标</span><strong>{goal?.title || goalId}</strong></div><div><span>推荐路径</span><strong>{pathTypeLabels[data.plan.selected_path]}</strong></div><div><span>当前节点</span><strong>{currentPath.nodes[currentIndex]?.name}</strong></div><div><span>路径状态</span><Tag color="success">{currentPath.status}</Tag></div><div className="path-overview-strip__progress"><span>整体进度</span><Progress percent={total ? Math.round(completed / total * 100) : 0} size="small" /></div>
      </div>

      {pendingSuggestion ? (
        <Card className="soft-card adjustment-card path-adjustment-card" title={<Space><RobotOutlined /> 待确认路径调整建议</Space>}>
          <div className="adjustment-card__summary"><span>建议切换到</span><strong>{pendingSuggestion.suggested_path_name}</strong><Tag color={pendingSuggestion.risk_level === 'high' ? 'red' : pendingSuggestion.risk_level === 'medium' ? 'orange' : 'green'}>风险 · {pendingSuggestion.risk_level}</Tag></div>
          <p>{pendingSuggestion.reason}</p>
          <Space wrap><Button type="primary" loading={switching} onClick={acceptSuggestion}>接受切换</Button><Button loading={switching} onClick={rejectSuggestion}>暂不切换</Button><Button onClick={() => setSelectedPath(data.candidates.find((path) => path.path_type === pendingSuggestion.suggested_path_type)?.path_id || selectedPath)}>查看其他路径</Button></Space>
        </Card>
      ) : null}

      <Row gutter={16}>
        <Col span={8}>
          <Card className="soft-card path-picker" title="候选路径">
            <Radio.Group value={selectedPath} onChange={(event) => setSelectedPath(event.target.value)}>
              {data.candidates.map((path) => (
                <Radio.Button value={path.path_id} key={path.path_id} className={path.is_current ? 'path-option--recommended' : ''}>
                  <span className={`path-option__icon path-option__icon--${path.path_type}`}>{pathIconMap[path.path_type]}</span><span className="path-option__copy"><strong>{path.path_name}</strong><small>{pathTypeLabels[path.path_type]} · {path.nodes.length} 个节点</small></span>{path.is_current ? <Tag color="success">当前</Tag> : null}
                </Radio.Button>
              ))}
            </Radio.Group>
            {selected ? <div className="path-comparison"><div><span>路径类型</span><b>{pathTypeLabels[selected.path_type]}</b></div><div><span>知识节点</span><b>{selected.nodes.length} 个</b></div><div><span>当前状态</span><b>{selected.is_current ? '使用中' : '候选'}</b></div></div> : null}
            <Button block loading={switching} disabled={!selected || selected.is_current} onClick={switchPath}>{selected?.is_current ? '当前正在使用' : '切换到这条路径'}</Button>
          </Card>
        </Col>

        <Col span={16}>
          <Card className="soft-card current-path-card" title={<Space><CheckCircleFilled className="text-green" /> 当前路径 · {currentPath.path_name}</Space>}>
            <Steps current={currentIndex} responsive={false} items={currentPath.nodes.map((node) => ({ title: node.name, description: node.status === 'learning' ? '当前学习' : node.status === 'completed' ? '已掌握' : '待学习' }))} />
            <div className="current-path-card__insight"><RobotOutlined /><div><strong>AI + 系统决策</strong><p>{data.plan.reason}</p></div></div>
          </Card>
          <Row gutter={16} className="path-detail-row"><Col span={16}><Card className="soft-card" title="知识掌握度">{data.mastery.length ? <EChart option={trendOption} height={178} /> : <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无掌握度数据" />}</Card></Col><Col span={8}><Card className="soft-card path-facts" title="路径详情"><p><BulbOutlined /> 已学节点 <strong>{completed} / {total}</strong></p><p><ApartmentOutlined /> 路径调整 <strong>{data.logs.length} 次</strong></p><p><CompassOutlined /> 本次决策 <strong>{data.plan.adjustments.length} 项</strong></p><p><CompassOutlined /> 当前阶段 <strong>{currentPath.nodes[currentIndex]?.name}</strong></p></Card></Col></Row>
        </Col>
      </Row>

      <Card className="soft-card path-log-card" title="路径切换记录"><Table rowKey="switch_id" columns={switchColumns} dataSource={data.logs} pagination={false} size="small" locale={{ emptyText: '暂无路径切换记录' }} /></Card>
      <Modal
        title="系统不建议直接切换"
        open={Boolean(switchEvaluation)}
        onCancel={() => setSwitchEvaluation(null)}
        footer={switchEvaluation ? [
          <Button key="override" danger loading={switching} onClick={overrideSwitch}>仍然切换</Button>,
          <Button key="suggested" type="primary" onClick={() => setSwitchEvaluation(null)}>先按建议学习</Button>,
          <Button key="cancel" onClick={() => setSwitchEvaluation(null)}>取消</Button>,
        ] : null}
      >
        {switchEvaluation ? (
          <div className="switch-risk-modal">
            <p><strong>风险等级：</strong>{switchEvaluation.evaluation.risk_level}</p>
            <p><strong>不建议原因：</strong>{switchEvaluation.evaluation.not_recommended_reason}</p>
            <p><strong>推荐替代动作：</strong>{switchEvaluation.evaluation.alternative_action}</p>
          </div>
        ) : null}
      </Modal>
    </div>
  )
}

export default PathsPage
