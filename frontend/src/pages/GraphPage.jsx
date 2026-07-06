import {
  ApartmentOutlined,
  BookOutlined,
  CheckCircleFilled,
  ExportOutlined,
  FullscreenOutlined,
  SearchOutlined,
  ThunderboltFilled,
} from '@ant-design/icons'
import { Button, Card, Descriptions, Empty, Input, Select, Space, Spin, Tag, message } from 'antd'
import { useCallback, useMemo, useState } from 'react'

import EChart from '../components/EChart'
import PageHeader from '../components/PageHeader'
import PageState from '../components/PageState'
import useAsyncData from '../hooks/useAsyncData'
import { useAppData } from '../hooks/useAppData'
import { graphApi } from '../services/copathApi'

const statusColors = { completed: '#2bbd7e', learning: '#2563eb', pending: '#9a73ef', not_in_path: '#d8dee9' }

function GraphPage() {
  const { currentStudent, currentPath, goals, loading: appLoading, error: appError, refresh } = useAppData()
  const studentId = currentStudent?.student_id
  const [detailLoading, setDetailLoading] = useState(false)
  const [search, setSearch] = useState('')

  const { data, loading, error, reload, setData } = useAsyncData(
    async () => {
      if (!studentId) return null
      const graph = await graphApi.get(studentId)
      const detail = await graphApi.getNode(graph.current_node)
      return { graph, detail }
    },
    [studentId],
  )

  const visibleNodes = useMemo(() => data?.graph.nodes.filter((node) => !search || node.name.toLowerCase().includes(search.toLowerCase()) || node.id.toLowerCase().includes(search.toLowerCase())) || [], [data, search])
  const visibleNodeIds = useMemo(() => new Set(visibleNodes.map((node) => node.id)), [visibleNodes])

  const graphOption = useMemo(() => ({
    tooltip: { formatter: ({ data: item }) => item.name || '' },
    animationDurationUpdate: 500,
    series: [{
      type: 'graph', layout: 'force', roam: true, draggable: true,
      label: { show: true, position: 'bottom', color: '#31405b', fontSize: 11, distance: 7 },
      force: { repulsion: 410, edgeLength: [80, 135], gravity: 0.08 }, edgeSymbol: ['none', 'arrow'], edgeSymbolSize: 7,
      lineStyle: { color: '#aab9cf', width: 1.4, curveness: 0.05 }, emphasis: { focus: 'adjacency', lineStyle: { width: 2.5 } },
      data: visibleNodes.map((node) => ({ ...node, symbolSize: node.status === 'learning' ? 57 : node.status === 'completed' ? 43 : 38, itemStyle: { color: statusColors[node.status], borderColor: node.status === 'learning' ? '#bfd4ff' : '#fff', borderWidth: node.status === 'learning' ? 8 : 4, shadowBlur: node.status === 'learning' ? 18 : 7, shadowColor: `${statusColors[node.status]}55` } })),
      links: (data?.graph.edges || []).filter((edge) => visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target)),
    }],
  }), [data, visibleNodes, visibleNodeIds])

  const onNodeClick = useCallback(async (params) => {
    if (params.dataType !== 'node') return
    setDetailLoading(true)
    try {
      const detail = await graphApi.getNode(params.data.id)
      setData((current) => ({ ...current, detail }))
    } catch (requestError) {
      message.error(requestError.message)
    } finally {
      setDetailLoading(false)
    }
  }, [setData])

  const exportGraph = () => {
    const blob = new Blob([JSON.stringify(data.graph, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `copath-graph-${studentId}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  if (appLoading || loading) return <PageState loading />
  if (appError || error) return <PageState error={appError || error} onRetry={appError ? refresh : reload} />
  if (!data || !currentPath) return <PageState empty emptyDescription="当前学生尚无知识图谱数据" />
  if (!data.graph.nodes.length) return <PageState empty emptyDescription="Neo4j 中暂无知识节点" />

  const goal = goals.find((item) => item.goal_id === currentStudent.current_goal_id)
  const detail = data.detail

  return (
    <div className="page graph-page">
      <PageHeader title="知识图谱" description="节点、依赖关系与当前路径高亮均读取自后端。" extra={<Space><Button icon={<FullscreenOutlined />} onClick={() => message.info('可拖拽和缩放图谱画布')}>适应画布</Button><Button icon={<ExportOutlined />} onClick={exportGraph}>导出</Button></Space>} />
      <div className="graph-status-strip"><div><CheckCircleFilled /> 当前目标 <strong>{goal?.title}</strong></div><div><ApartmentOutlined /> 当前路径 <strong>{currentPath.path_name}</strong></div><div><ThunderboltFilled /> 当前节点 <strong>{data.graph.nodes.find((node) => node.id === data.graph.current_node)?.name}</strong></div><div className="graph-legend"><span><i className="legend-dot legend-dot--green" /> 已掌握</span><span><i className="legend-dot legend-dot--blue" /> 学习中</span><span><i className="legend-dot legend-dot--purple" /> 路径节点</span><span><i className="legend-dot" /> 其他节点</span></div></div>
      <div className="graph-toolbar"><Input value={search} onChange={(event) => setSearch(event.target.value)} prefix={<SearchOutlined />} placeholder="搜索知识点" allowClear /><Select defaultValue="all" options={[{ value: 'all', label: '全部章节' }]} /></div>
      <div className="graph-layout">
        <Card className="soft-card graph-canvas-card" title="Python 递归知识网络">{visibleNodes.length ? <EChart option={graphOption} height={520} onChartClick={onNodeClick} /> : <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="没有匹配的知识点" />}<div className="graph-canvas-hint">拖拽画布查看关系 · 点击节点读取详情</div></Card>
        <Card className="soft-card graph-detail-card" title="知识点详情" loading={detailLoading}>
          {detail ? <><div className="graph-detail-card__hero"><span><BookOutlined /></span><div><small>当前选择</small><h3>{detail.name}</h3><Tag color={detail.node_id === data.graph.current_node ? 'blue' : 'default'}>{detail.node_id === data.graph.current_node ? '学习中' : '知识节点'}</Tag></div></div>
            <Descriptions column={1} size="small" colon={false} items={[{ key: 'chapter', label: '所属章节', children: detail.chapter }, { key: 'difficulty', label: '难度等级', children: `${detail.difficulty} / 5` }, { key: 'id', label: '节点 ID', children: detail.node_id }]} />
            <div className="graph-detail-section"><strong>知识点说明</strong><p>{detail.description}</p></div>
            <div className="graph-detail-section"><strong>前置知识</strong><div>{detail.prerequisites.length ? detail.prerequisites.map((item) => <Tag key={item.node_id}>{item.name}</Tag>) : <span className="muted-text">无</span>}</div></div>
            <div className="graph-detail-section"><strong>后继知识</strong><div>{detail.next_nodes.length ? detail.next_nodes.map((item) => <Tag color="blue" key={item.node_id}>{item.name}</Tag>) : <span className="muted-text">无</span>}</div></div>
            <div className="graph-detail-section"><strong>关联资源</strong>{detail.resources.length ? detail.resources.map((resource) => <div className="graph-resource" key={resource.resource_id}><BookOutlined /><span>{resource.title}</span></div>) : <p className="muted-text">暂无关联资源。</p>}</div></> : <Spin />}
        </Card>
      </div>
    </div>
  )
}

export default GraphPage
