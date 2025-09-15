import type { Meta, StoryObj } from '@storybook/nextjs-vite'
import { Database, BarChart3, Calendar, Globe, TrendingUp, Users } from 'lucide-react'
import MetricCard from './MetricCard'

const meta: Meta<typeof MetricCard> = {
  title: 'UI/MetricCard',
  component: MetricCard,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    title: {
      control: { type: 'text' },
    },
    value: {
      control: { type: 'text' },
    },
    trend: {
      control: { type: 'object' },
    },
    description: {
      control: { type: 'text' },
    },
  },
}

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  args: {
    title: 'Total Users',
    value: '1,234',
    icon: Users,
  },
}

export const WithTrend: Story = {
  args: {
    title: 'Revenue',
    value: '$12,345',
    icon: TrendingUp,
    trend: {
      value: 12.5,
      isPositive: true,
    },
  },
}

export const WithDescription: Story = {
  args: {
    title: 'Active Sessions',
    value: '89',
    icon: BarChart3,
    description: 'Current active user sessions',
  },
}

export const NegativeTrend: Story = {
  args: {
    title: 'Error Rate',
    value: '2.3%',
    icon: Database,
    trend: {
      value: 5.2,
      isPositive: false,
    },
    description: 'System error rate over last 24h',
  },
}

export const DashboardMetrics: Story = {
  render: () => (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 w-full max-w-6xl">
      <MetricCard
        title="Total Countries"
        value="195"
        icon={Globe}
        trend={{ value: 0, isPositive: true }}
        description="Countries in database"
      />
      <MetricCard
        title="Total Leagues"
        value="847"
        icon={BarChart3}
        trend={{ value: 12.5, isPositive: true }}
        description="Football leagues tracked"
      />
      <MetricCard
        title="Active Seasons"
        value="1,234"
        icon={Calendar}
        trend={{ value: 8.3, isPositive: true }}
        description="Current football seasons"
      />
      <MetricCard
        title="Total Fixtures"
        value="45,678"
        icon={Database}
        trend={{ value: 15.7, isPositive: true }}
        description="Matches collected"
      />
    </div>
  ),
}
