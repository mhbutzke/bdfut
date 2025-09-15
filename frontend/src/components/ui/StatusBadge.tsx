import { CheckCircle, XCircle, AlertCircle, Clock } from 'lucide-react'

type Status = 'success' | 'error' | 'warning' | 'pending'

interface StatusBadgeProps {
  status: Status
  label?: string
}

const statusConfig = {
  success: {
    icon: CheckCircle,
    className: 'bg-green-100 text-green-800',
    iconClassName: 'text-green-500',
  },
  error: {
    icon: XCircle,
    className: 'bg-red-100 text-red-800',
    iconClassName: 'text-red-500',
  },
  warning: {
    icon: AlertCircle,
    className: 'bg-yellow-100 text-yellow-800',
    iconClassName: 'text-yellow-500',
  },
  pending: {
    icon: Clock,
    className: 'bg-gray-100 text-gray-800',
    iconClassName: 'text-gray-500',
  },
}

export default function StatusBadge({ status, label }: StatusBadgeProps) {
  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.className}`}>
      <Icon className={`w-3 h-3 mr-1 ${config.iconClassName}`} />
      {label || status}
    </span>
  )
}
