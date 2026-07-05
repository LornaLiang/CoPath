import { Typography } from 'antd'

function PageHeader({ title, description, extra }) {
  return (
    <div className="page-heading">
      <div>
        <Typography.Title level={2}>{title}</Typography.Title>
        <Typography.Paragraph>{description}</Typography.Paragraph>
      </div>
      {extra ? <div className="page-heading__extra">{extra}</div> : null}
    </div>
  )
}

export default PageHeader
