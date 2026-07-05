import {
  AimOutlined,
  BookOutlined,
  CheckCircleFilled,
  ClockCircleOutlined,
  RobotOutlined,
  SearchOutlined,
  ThunderboltOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { Button, Card, Input, Rate, Select, Space, Tag, message } from 'antd'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import PageHeader from '../components/PageHeader'
import { mockGoals, mockStudent } from '../services/mockData'

const levelLabels = {
  beginner: '入门',
  intermediate: '进阶',
  advanced: '挑战',
}

const goalIcons = [<AimOutlined />, <BookOutlined />, <ThunderboltOutlined />]

function GoalsPage() {
  const navigate = useNavigate()
  const [selectedGoal, setSelectedGoal] = useState('G001')

  const confirmGoal = () => {
    const goal = mockGoals.find((item) => item.goal_id === selectedGoal)
    message.success(`已选择“${goal.title}”（Mock）`)
  }

  return (
    <div className="page goals-page">
      <PageHeader
        title="学习目标"
        description="选择你想要掌握的知识点，系统将生成多条个性化学习路径。"
        extra={<Tag color="blue">当前课程 · Python 基础</Tag>}
      />

      <div className="goals-overview-grid">
        <Card className="soft-card student-summary-card" bordered>
          <div className="student-summary-card__avatar"><UserOutlined /></div>
          <div className="student-summary-card__main">
            <span>当前学习者</span>
            <strong>{mockStudent.name}</strong>
            <small>{mockStudent.recent_state}</small>
          </div>
          <div className="student-summary-card__tags">
            <Tag>速度 · 中等</Tag>
            <Tag color="geekblue">偏好 · 基础型</Tag>
          </div>
        </Card>

        <div className="insight-box goal-insight">
          <span><RobotOutlined /></span>
          <div>
            <strong>AI 学习目标建议</strong>
            <p>你已掌握函数基础，但调用栈和返回值仍较薄弱，建议优先学习“递归”。</p>
          </div>
        </div>
      </div>

      <div className="goal-toolbar">
        <Input prefix={<SearchOutlined />} placeholder="搜索目标或知识点" allowClear />
        <Space>
          <Select defaultValue="all" options={[{ value: 'all', label: '全部领域' }, { value: 'python', label: 'Python 基础' }]} />
          <Select defaultValue="all" options={[{ value: 'all', label: '全部难度' }, { value: 'easy', label: '入门' }, { value: 'hard', label: '进阶与挑战' }]} />
        </Space>
      </div>

      <div className="goal-card-grid">
        {mockGoals.map((goal, index) => {
          const selected = goal.goal_id === selectedGoal
          return (
            <button
              type="button"
              className={`goal-card ${selected ? 'goal-card--selected' : ''}`}
              key={goal.goal_id}
              onClick={() => setSelectedGoal(goal.goal_id)}
            >
              <div className={`goal-card__icon goal-card__icon--${index % 3}`}>
                {goalIcons[index % goalIcons.length]}
              </div>
              <div className="goal-card__body">
                <div className="goal-card__title-row">
                  <strong>{goal.title}</strong>
                  {goal.recommended ? <Tag color="blue">推荐</Tag> : null}
                </div>
                <span>目标知识点 · {goal.target_name}</span>
                <p>{goal.description}</p>
                <div className="goal-card__meta">
                  <Tag>{levelLabels[goal.recommended_level]}</Tag>
                  <Rate disabled value={goal.difficulty} count={5} />
                  <small><ClockCircleOutlined /> {goal.duration}</small>
                </div>
              </div>
              {selected ? <CheckCircleFilled className="goal-card__check" /> : null}
            </button>
          )
        })}
      </div>

      <div className="page-actions">
        <Button onClick={confirmGoal}>确认选择</Button>
        <Button type="primary" icon={<ThunderboltOutlined />} onClick={() => { confirmGoal(); navigate('/paths') }}>
          开始路径规划
        </Button>
      </div>
    </div>
  )
}

export default GoalsPage
