import {
  AimOutlined,
  BookOutlined,
  CheckCircleFilled,
  RobotOutlined,
  SearchOutlined,
  ThunderboltOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { Button, Card, Empty, Input, Select, Space, Tag, message } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import PageHeader from '../components/PageHeader'
import PageState from '../components/PageState'
import useAsyncData from '../hooks/useAsyncData'
import { useAppData } from '../hooks/useAppData'
import { goalApi, learningApi, profileApi } from '../services/copathApi'

const levelLabels = { beginner: '入门', intermediate: '进阶', advanced: '挑战' }
const preferenceLabels = { basic: '基础型', example: '案例型', fast: '快速型' }
const speedLabels = { slow: '较慢', medium: '中等', fast: '较快' }
const goalIcons = [<AimOutlined />, <BookOutlined />, <ThunderboltOutlined />]

function GoalsPage() {
  const navigate = useNavigate()
  const { currentStudent, goals, loading: appLoading, error: appError, refresh } = useAppData()
  const studentId = currentStudent?.student_id
  const [selectedGoal, setSelectedGoal] = useState(null)
  const [search, setSearch] = useState('')
  const [level, setLevel] = useState('all')
  const [submitting, setSubmitting] = useState(false)

  const { data, loading, error, reload } = useAsyncData(
    () => studentId
      ? Promise.all([profileApi.get(studentId), learningApi.getSummary(studentId)]).then(([profile, summary]) => ({ profile, summary }))
      : Promise.resolve(null),
    [studentId],
  )

  useEffect(() => {
    if (goals.length && !selectedGoal) setSelectedGoal(currentStudent?.current_goal_id || goals[0].goal_id)
  }, [goals, selectedGoal, currentStudent])

  const visibleGoals = useMemo(() => goals.filter((goal) => {
    const matchesSearch = !search || `${goal.title}${goal.description}${goal.target_node_id}`.toLowerCase().includes(search.toLowerCase())
    return matchesSearch && (level === 'all' || goal.recommended_level === level)
  }), [goals, search, level])

  const selectGoal = async (goToPaths = false) => {
    if (!studentId || !selectedGoal) return
    setSubmitting(true)
    try {
      const result = await goalApi.select(studentId, selectedGoal)
      await refresh()
      message.success(`已选择“${goals.find((item) => item.goal_id === result.goal_id)?.title || result.goal_id}”`)
      if (goToPaths) navigate('/paths')
    } catch (requestError) {
      message.error(requestError.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (appLoading || loading) return <PageState loading />
  if (appError || error) return <PageState error={appError || error} onRetry={appError ? refresh : reload} />
  if (!data || !currentStudent) return <PageState empty emptyDescription="当前学生数据为空" />
  if (!goals.length) return <PageState empty emptyDescription="暂无可选择的学习目标" />

  return (
    <div className="page goals-page">
      <PageHeader title="学习目标" description="选择你想掌握的知识点，候选路径由后端数据提供。" extra={<Tag color="blue">当前课程 · Python 程序设计</Tag>} />

      <div className="goals-overview-grid">
        <Card className="soft-card student-summary-card" bordered>
          <div className="student-summary-card__avatar"><UserOutlined /></div>
          <div className="student-summary-card__main"><span>当前学习者</span><strong>{currentStudent.name}</strong><small>{data.profile.recent_state}</small></div>
          <div className="student-summary-card__tags"><Tag>速度 · {speedLabels[data.profile.learning_speed]}</Tag><Tag color="geekblue">偏好 · {preferenceLabels[data.profile.learning_preference]}</Tag></div>
        </Card>
        <div className="insight-box goal-insight"><span><RobotOutlined /></span><div><strong>当前学习建议</strong><p>{data.summary.next_suggestion}</p></div></div>
      </div>

      <div className="goal-toolbar">
        <Input value={search} onChange={(event) => setSearch(event.target.value)} prefix={<SearchOutlined />} placeholder="搜索目标或知识点" allowClear />
        <Space><Select value={level} onChange={setLevel} options={[{ value: 'all', label: '全部难度' }, { value: 'beginner', label: '入门' }, { value: 'intermediate', label: '进阶' }, { value: 'advanced', label: '挑战' }]} /></Space>
      </div>

      <div className="goal-card-grid">
        {!visibleGoals.length ? <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="没有符合筛选条件的学习目标" /> : null}
        {visibleGoals.map((goal, index) => {
          const selected = goal.goal_id === selectedGoal
          return (
            <button type="button" className={`goal-card ${selected ? 'goal-card--selected' : ''}`} key={goal.goal_id} onClick={() => setSelectedGoal(goal.goal_id)}>
              <div className={`goal-card__icon goal-card__icon--${index % 3}`}>{goalIcons[index % goalIcons.length]}</div>
              <div className="goal-card__body">
                <div className="goal-card__title-row"><strong>{goal.title}</strong>{goal.goal_id === currentStudent.current_goal_id ? <Tag color="blue">当前目标</Tag> : null}</div>
                <span>目标知识点 · {goal.target_node_id}</span>
                <p>{goal.description}</p>
                <div className="goal-card__meta"><Tag>{levelLabels[goal.recommended_level] || goal.recommended_level}</Tag><small>目标 ID · {goal.goal_id}</small></div>
              </div>
              {selected ? <CheckCircleFilled className="goal-card__check" /> : null}
            </button>
          )
        })}
      </div>

      <div className="page-actions"><Button loading={submitting} onClick={() => selectGoal(false)}>确认选择</Button><Button loading={submitting} type="primary" icon={<ThunderboltOutlined />} onClick={() => selectGoal(true)}>查看候选路径</Button></div>
    </div>
  )
}

export default GoalsPage
