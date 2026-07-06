import { Button, Card, Empty, Result, Skeleton } from 'antd'

function PageState({ loading, error, onRetry, empty = false, emptyDescription = '暂无可展示的数据' }) {
  if (loading) {
    return <Card className="soft-card page-state"><Skeleton active avatar paragraph={{ rows: 4 }} /></Card>
  }

  if (error) {
    return (
      <Card className="soft-card page-state">
        <Result
          status="error"
          title="页面数据加载失败"
          subTitle={error.message}
          extra={onRetry ? <Button type="primary" onClick={() => onRetry().catch(() => {})}>重新加载</Button> : null}
        />
      </Card>
    )
  }

  if (empty) {
    return (
      <Card className="soft-card page-state">
        <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={emptyDescription} />
      </Card>
    )
  }

  return null
}

export default PageState
