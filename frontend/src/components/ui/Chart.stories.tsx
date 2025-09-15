import type { Meta, StoryObj } from '@storybook/nextjs-vite'
import Chart from './Chart'

const meta: Meta<typeof Chart> = {
  title: 'UI/Chart',
  component: Chart,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: { type: 'select' },
      options: ['line', 'bar', 'pie'],
    },
    title: {
      control: { type: 'text' },
    },
    color: {
      control: { type: 'color' },
    },
    height: {
      control: { type: 'number' },
    },
  },
}

export default meta
type Story = StoryObj<typeof meta>

const sampleData = [
  { name: 'Jan', value: 400 },
  { name: 'Feb', value: 300 },
  { name: 'Mar', value: 600 },
  { name: 'Apr', value: 800 },
  { name: 'May', value: 500 },
  { name: 'Jun', value: 700 },
]

const pieData = [
  { name: 'Countries', value: 195 },
  { name: 'Leagues', value: 847 },
  { name: 'Seasons', value: 1234 },
  { name: 'Fixtures', value: 45678 },
]

export const LineChart: Story = {
  args: {
    data: sampleData,
    type: 'line',
    title: 'Monthly Data',
    color: '#3B82F6',
  },
}

export const BarChart: Story = {
  args: {
    data: sampleData,
    type: 'bar',
    title: 'Monthly Data',
    color: '#10B981',
  },
}

export const PieChart: Story = {
  args: {
    data: pieData,
    type: 'pie',
    title: 'Data Distribution',
  },
}

export const DashboardCharts: Story = {
  render: () => (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 w-full max-w-6xl">
      <Chart
        data={sampleData}
        type="line"
        title="API Calls Over Time"
        color="#3B82F6"
        height={300}
      />
      <Chart
        data={sampleData}
        type="bar"
        title="Data Processing Volume"
        color="#10B981"
        height={300}
      />
      <Chart
        data={pieData}
        type="pie"
        title="Database Content Distribution"
        height={300}
      />
      <Chart
        data={[
          { name: 'Success', value: 95 },
          { name: 'Warning', value: 3 },
          { name: 'Error', value: 2 },
        ]}
        type="pie"
        title="System Health"
        height={300}
      />
    </div>
  ),
}
