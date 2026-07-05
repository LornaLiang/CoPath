import {
  ApartmentOutlined,
  BookOutlined,
  CheckCircleFilled,
  ExportOutlined,
  FullscreenOutlined,
  SearchOutlined,
  ThunderboltFilled,
} from '@ant-design/icons'
import { Button, Card, Descriptions, Input, Select, Space, Tag, message } from 'antd'
import { useCallback, useMemo, useState } from 'react'

import EChart from '../components/EChart'
import PageHeader from '../components/PageHeader'
import { mockGraphEdges, mockGraphNodes, mockResources } from '../services/mockData'

const statusColors = {
  completed: '#2bbd7e',
  learning: '#2563eb',
  pending: '#9a73ef',
  not_in_path: '#d8dee9',
}

function GraphPage() {
  const [selectedNodeId, setSelectedNodeId] = useState('call_stack')
  const selectedNode = mockGraphNodes.find((node) => node.id === selectedNodeId)

  const graphOption = useMemo(() => ({
    tooltip: { formatter: ({ data }) => data.name || '' },
    animationDurationUpdate: 500,
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      label: { show: true, position: 'bottom', color: '#31405b', fontSize: 11, distance: 7 },
      force: { repulsion: 410, edgeLength: [80, 135], gravity: 0.08 },
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: 7,
      lineStyle: { color: '#aab9cf', width: 1.4, curveness: 0.05 },
      emphasis: { focus: 'adjacency', lineStyle: { width: 2.5 } },
      data: mockGraphNodes.map((node) => ({
        ...node,
        symbolSize: node.status === 'learning' ? 57 : node.status === 'completed' ? 43 : 38,
        itemStyle: {
          color: statusColors[node.status],
          borderColor: node.status === 'learning' ? '#bfd4ff' : '#fff',
          borderWidth: node.status === 'learning' ? 8 : 4,
          shadowBlur: node.status === 'learning' ? 18 : 7,
          shadowColor: `${statusColors[node.status]}55`,
        },
      })),
      links: mockGraphEdges,
    }],
  }), [])

  const onNodeClick = useCallback((params) => {
    if (params.dataType === 'node') setSelectedNodeId(params.data.id)
  }, [])

  const prerequisites = mockGraphEdges.filter((edge) => edge.target === selectedNodeId).map((edge) => mockGraphNodes.find((node) => node.id === edge.source)?.name).filter(Boolean)
  const nextNodes = mockGraphEdges.filter((edge) => edge.source === selectedNodeId).map((edge) => mockGraphNodes.find((node) => node.id === edge.target)?.name).filter(Boolean)

  return (
    <div className="page graph-page">
      <PageHeader
        title="知识图谱"
        description="探索课程知识点之间的前置关系，当前学习路径已高亮显示。"
        extra={<Space><Button icon={<FullscreenOutlined />} onClick={() => message.info('画布已适应当前视图（Mock）')}>适应画布</Button><Button icon={<ExportOutlined />} onClick={() => message.success('知识图谱导出任务已创建（Mock）')}>导出</Button></Space>}
      />

      <div className="graph-status-strip">
        <div><CheckCircleFilled /> 当前目标 <strong>掌握递归</strong></div>
        <div><ApartmentOutlined /> 当前路径 <strong>基础补全路径</strong></div>
        <div><ThunderboltFilled /> 当前节点 <strong>调用栈</strong></div>
        <div className="graph-legend">
          <span><i className="legend-dot legend-dot--green" /> 已掌握</span>
          <span><i className="legend-dot legend-dot--blue" /> 学习中</span>
          <span><i className="legend-dot legend-dot--purple" /> 路径节点</span>
          <span><i className="legend-dot" /> 其他节点</span>
        </div>
      </div>

      <div className="graph-toolbar">
        <Input prefix={<SearchOutlined />} placeholder="搜索知识点" allowClear />
        <Select defaultValue="all" options={[{ value: 'all', label: '全部章节' }, { value: 'function', label: '函数与递归' }, { value: 'advanced', label: '递归进阶' }]} />
      </div>

      <div className="graph-layout">
        <Card className="soft-card graph-canvas-card" title="Python 递归知识网络">
          <EChart option={graphOption} height={520} onChartClick={onNodeClick} />
          <div className="graph-canvas-hint">拖拽画布查看关系 · 点击节点查看详情</div>
        </Card>

        <Card className="soft-card graph-detail-card" title="知识点详情">
          <div className="graph-detail-card__hero">
            <span><BookOutlined /></span>
            <div><small>当前选择</small><h3>{selectedNode.name}</h3><Tag color={selectedNode.status === 'learning' ? 'blue' : 'default'}>{selectedNode.status === 'learning' ? '学习中' : '知识节点'}</Tag></div>
          </div>
          <Descriptions column={1} size="small" colon={false} items={[
            { key: 'chapter', label: '所属章节', children: selectedNode.difficulty >= 4 ? '函数与递归' : 'Python 基础' },
            { key: 'difficulty', label: '难度等级', children: `${selectedNode.difficulty} / 5` },
            { key: 'mastery', label: '掌握状态', children: selectedNode.status === 'completed' ? '已掌握' : selectedNode.status === 'learning' ? '正在学习' : '尚未学习' },
          ]} />
          <div className="graph-detail-section"><strong>知识点说明</strong><p>{selectedNode.name}是递归学习路径中的重要知识点，用于理解程序执行过程与知识之间的依赖关系。</p></div>
          <div className="graph-detail-section"><strong>前置知识</strong><div>{prerequisites.length ? prerequisites.map((item) => <Tag key={item}>{item}</Tag>) : <span className="muted-text">无</span>}</div></div>
          <div className="graph-detail-section"><strong>后继知识</strong><div>{nextNodes.length ? nextNodes.map((item) => <Tag color="blue" key={item}>{item}</Tag>) : <span className="muted-text">无</span>}</div></div>
          <div className="graph-detail-section"><strong>关联资源</strong>{selectedNodeId === 'call_stack' ? mockResources.map((resource) => <div className="graph-resource" key={resource.resource_id}><BookOutlined /><span>{resource.title}</span></div>) : <p className="muted-text">选择当前学习节点可查看推荐资源。</p>}</div>
        </Card>
      </div>
    </div>
  )
}

export default GraphPage
