# BDFut Frontend Dashboard 🎨

Dashboard de monitoramento para o sistema ETL BDFut, construído com Next.js, TypeScript e Supabase.

## 🚀 Tecnologias

- **Next.js 14** - Framework React com App Router
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Estilização utilitária
- **Supabase** - Banco de dados e autenticação
- **React Query** - Gerenciamento de estado e cache
- **Lucide React** - Ícones

## 📁 Estrutura do Projeto

```
frontend/
├── src/
│   ├── app/                 # App Router (Next.js 14)
│   │   ├── page.tsx        # Página inicial
│   │   ├── etl/            # Página de ETL Jobs
│   │   ├── data-quality/   # Página de qualidade de dados
│   │   ├── metrics/        # Página de métricas
│   │   └── layout.tsx      # Layout principal
│   ├── components/
│   │   ├── layout/         # Componentes de layout
│   │   └── ui/             # Componentes reutilizáveis
│   ├── hooks/              # Custom hooks
│   ├── lib/                # Configurações e utilitários
│   └── config/             # Configurações
├── public/                  # Arquivos estáticos
└── package.json
```

## 🛠️ Setup e Instalação

### 1. Instalar Dependências

```bash
cd frontend
npm install
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env.local` na raiz do projeto frontend:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Development settings
NEXT_PUBLIC_APP_ENV=development
```

### 3. Executar em Desenvolvimento

```bash
npm run dev
```

O dashboard estará disponível em `http://localhost:3000`

## 📊 Funcionalidades

### Dashboard Principal (`/`)
- Visão geral do sistema
- Métricas principais (países, ligas, temporadas, fixtures)
- Status do sistema
- Fixtures recentes

### ETL Jobs (`/etl`)
- Monitoramento dos jobs de ETL
- Status dos pipelines
- Dados de ligas e temporadas

### Data Quality (`/data-quality`)
- Métricas de qualidade dos dados
- Checks de qualidade
- Regras de validação

### Metrics (`/metrics`)
- Métricas de performance
- Atividade por hora
- Saúde do sistema

## 🎨 Componentes

### Layout Components
- `Header` - Cabeçalho com navegação
- `Sidebar` - Barra lateral de navegação
- `Layout` - Layout principal da aplicação

### UI Components
- `MetricCard` - Card para exibir métricas
- `DataTable` - Tabela de dados reutilizável
- `StatusBadge` - Badge de status com ícones

## 🔌 Integração com Supabase

### Configuração
O cliente Supabase é configurado em `src/lib/supabase.ts` com tipos TypeScript para o banco de dados.

### Hooks de Dados
- `useCountries()` - Buscar países
- `useLeagues()` - Buscar ligas
- `useSeasons()` - Buscar temporadas
- `useRecentFixtures()` - Buscar fixtures recentes
- `useStats()` - Estatísticas gerais

## 🎯 Próximos Passos

### TASK-FE-002: Biblioteca de Componentes
- [ ] Expandir componentes UI
- [ ] Implementar Storybook
- [ ] Adicionar testes de componentes

### TASK-FE-003: Sistema de Rotas
- [ ] Implementar autenticação
- [ ] Proteção de rotas
- [ ] Middleware de autenticação

### TASK-FE-004: Gerenciamento de Estado
- [ ] Implementar React Query completo
- [ ] Cache inteligente
- [ ] Estados de loading/error

### TASK-FE-005: Dashboard Avançado
- [ ] Gráficos interativos
- [ ] Filtros avançados
- [ ] Exportação de dados

### TASK-FE-006: Autenticação
- [ ] Login/logout
- [ ] Controle de acesso
- [ ] Gestão de sessão

## 🚀 Deploy

### Build para Produção

```bash
npm run build
npm start
```

### Variáveis de Ambiente de Produção

```env
NEXT_PUBLIC_SUPABASE_URL=production_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=production_supabase_key
NEXT_PUBLIC_APP_ENV=production
```

## 📝 Notas de Desenvolvimento

- O projeto usa App Router do Next.js 14
- TypeScript está configurado com tipos estritos
- Tailwind CSS para estilização rápida
- React Query para cache e sincronização de dados
- Componentes responsivos e acessíveis