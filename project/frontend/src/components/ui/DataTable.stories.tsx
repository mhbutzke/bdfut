import type { Meta, StoryObj } from '@storybook/nextjs-vite'
import DataTable from './DataTable'

type SampleData = {
  id: number
  name: string
  country: string
  status: string
  updated: string
}

const meta: Meta<typeof DataTable<SampleData>> = {
  title: 'UI/DataTable',
  component: DataTable,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    title: {
      control: { type: 'text' },
    },
    emptyMessage: {
      control: { type: 'text' },
    },
  },
}

export default meta
type Story = StoryObj<typeof meta>

const sampleData: SampleData[] = [
  { id: 1, name: 'Brazil Serie A', country: 'Brazil', status: 'active', updated: '2025-01-13' },
  { id: 2, name: 'Premier League', country: 'England', status: 'active', updated: '2025-01-13' },
  { id: 3, name: 'La Liga', country: 'Spain', status: 'active', updated: '2025-01-12' },
  { id: 4, name: 'Bundesliga', country: 'Germany', status: 'inactive', updated: '2025-01-11' },
]

const columns = [
  { key: 'name' as keyof SampleData, label: 'League Name' },
  { key: 'country' as keyof SampleData, label: 'Country' },
  { key: 'status' as keyof SampleData, label: 'Status' },
  { key: 'updated' as keyof SampleData, label: 'Last Updated' },
]

export const Default: Story = {
  args: {
    data: sampleData,
    columns,
    title: 'Leagues Data',
  },
}

export const WithoutTitle: Story = {
  args: {
    data: sampleData,
    columns,
  },
}

export const Empty: Story = {
  args: {
    data: [],
    columns,
    title: 'Empty Table',
    emptyMessage: 'No data available',
  },
}

export const FixturesTable: Story = {
  args: {
    data: sampleData,
    columns: [
      { key: 'name' as keyof SampleData, label: 'Match' },
      { key: 'country' as keyof SampleData, label: 'Country' },
      { key: 'status' as keyof SampleData, label: 'Status' },
      { key: 'updated' as keyof SampleData, label: 'Date' },
    ],
    title: 'Recent Fixtures',
  },
}
