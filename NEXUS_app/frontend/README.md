# 🎨 Nexus Platform Frontend

## 📋 Overview

The Nexus Platform Frontend is a comprehensive React/Next.js application designed to transform complex backend operations into intuitive, accessible, and performant user interfaces. Built with modern web technologies and advanced AI capabilities, it serves as the primary interface for forensic investigation and compliance management.

## 🏗️ Architecture

### Technology Stack
- **React 18** - Modern React with hooks and concurrent features
- **Next.js 14** - Full-stack React framework with App Router
- **TypeScript** - Type safety and better developer experience
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations and transitions
- **Recharts** - Data visualization library
- **React Hook Form** - Form management and validation
- **Zustand** - Lightweight state management
- **React Query** - Data fetching and caching

### Key Features
- **AI-Powered Avatar** - Friendly AI assistant in the top-right corner
- **Responsive Design** - Works seamlessly across all devices
- **Accessibility First** - WCAG 2.1 AA compliance
- **Real-time Updates** - WebSocket integration for live data
- **Advanced Data Visualization** - Interactive charts and dashboards
- **Progressive Disclosure** - Complex features revealed gradually

## 📁 Project Structure

```
NEXUS_app/frontend/
├── 📚 docs/                          # Documentation
│   ├── EXECUTIVE_SUMMARY.md         # Platform overview
│   ├── UI_UX_PAGES_GUIDE.md        # UI/UX documentation
│   └── FRENLY_AI_AGENT_GUIDE.md    # AI agent documentation
├── 🎨 design-system/                # Design system
│   ├── tokens/                      # Design tokens (colors, typography, spacing)
│   ├── components/                  # Core design components
│   ├── layouts/                     # Layout components
│   └── patterns/                    # UI patterns
├── 📄 pages/                        # Next.js pages
│   ├── index.tsx                   # Home page
│   ├── dashboard/                  # Dashboard pages
│   ├── guide/                     # Guide pages
│   └── auth/                      # Authentication pages
├── 🧩 components/                   # Application components
│   ├── layout/                    # Layout components (Layout, Header, Sidebar)
│   ├── ai/                        # AI components (Avatar, AIChatInterface)
│   ├── dashboard/                 # Dashboard components
│   ├── common/                    # Common components
│   └── ui/                        # UI components from design system
├── 📚 lib/                         # Utilities and configurations
├── 🎣 hooks/                       # Custom React hooks
├── 🏪 store/                       # State management
├── 🎨 styles/                      # Global styles
├── 📦 public/                      # Static assets
├── ⚙️ config/                      # Configuration files
├── 🗃️ archive/                     # Archived legacy files
└── 📋 package.json                # Dependencies and scripts
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm 8+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NEXUS_app/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run test         # Run tests
npm run test:watch   # Run tests in watch mode
```

## 🎨 Design System

### Core Components

#### Button Component
```tsx
import { Button } from '@/components/ui/Button';

<Button variant="primary" size="lg" icon={<PlusIcon />}>
  Add New Case
</Button>
```

#### Card Component
```tsx
import { Card } from '@/components/ui/Card';

<Card header="Case Details" footer="Last updated 2 hours ago">
  <p>Case content goes here...</p>
</Card>
```

#### DataTable Component
```tsx
import { DataTable } from '@/components/ui/DataTable';

<DataTable
  data={cases}
  columns={columns}
  searchable
  sortable
  pagination
/>
```

### Design Tokens

#### Colors
```tsx
// Primary colors
const primary = {
  50: '#eff6ff',
  500: '#3b82f6',
  900: '#1e3a8a'
};

// Semantic colors
const semantic = {
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6'
};
```

#### Typography
```tsx
// Font families
const fonts = {
  sans: ['Inter', 'sans-serif'],
  mono: ['JetBrains Mono', 'monospace']
};

// Font sizes
const fontSizes = {
  xs: '0.75rem',
  sm: '0.875rem',
  base: '1rem',
  lg: '1.125rem',
  xl: '1.25rem',
  '2xl': '1.5rem'
};
```

## 🤖 AI Avatar Integration

The Frenly AI Avatar is a floating widget positioned in the top-right corner of every page, providing contextual assistance and guidance.

### Features
- **Context-Aware Suggestions** - Provides relevant help based on current page and user role
- **Proactive Assistance** - Offers suggestions before users encounter problems
- **Workflow Guidance** - Guides users through complex workflows
- **Real-time Support** - Monitors user actions and provides instant feedback

### Usage
```tsx
import Avatar from '@/components/ai/Avatar';

<Avatar
  isVisible={true}
  context={{
    currentPage: '/dashboard',
    userRole: 'investigator',
    workflowStep: 'evidence-analysis'
  }}
  onInteraction={(action) => {
    // Handle avatar interactions
    console.log('Avatar action:', action);
  }}
/>
```

## 📱 Responsive Design

### Breakpoints
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: 1024px - 1440px
- **Large Desktop**: 1440px+

### Mobile-First Approach
All components are designed mobile-first and progressively enhanced for larger screens.

```tsx
// Example responsive component
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Content */}
</div>
```

## ♿ Accessibility

### WCAG 2.1 AA Compliance
- **Color Contrast**: Minimum 4.5:1 ratio for all text
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Proper ARIA labels and roles
- **Focus Management**: Clear focus indicators

### Implementation
```tsx
// Accessible button example
<button
  aria-label="Add new case"
  aria-describedby="add-case-help"
  className="focus:ring-2 focus:ring-blue-500 focus:outline-none"
>
  <PlusIcon aria-hidden="true" />
  Add Case
</button>
```

## ⚡ Performance

### Optimization Strategies
- **Code Splitting** - Lazy load components and routes
- **Bundle Optimization** - Minimize JavaScript and CSS
- **Image Optimization** - WebP format, responsive images
- **Caching** - Efficient data and asset caching
- **Virtual Scrolling** - Handle large datasets efficiently

### Performance Monitoring
```tsx
// Performance monitoring example
import { usePerformance } from '@/hooks/usePerformance';

const Component = () => {
  const { measurePerformance } = usePerformance();
  
  useEffect(() => {
    measurePerformance('component-render');
  }, []);
};
```

## 🧪 Testing

### Test Structure
```
__tests__/
├── components/           # Component tests
├── pages/               # Page tests
├── hooks/               # Hook tests
├── utils/               # Utility tests
└── __mocks__/           # Mock files
```

### Running Tests
```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Environment Variables
```bash
# Production environment variables
NEXT_PUBLIC_API_URL=https://api.nexus-platform.com
NEXT_PUBLIC_WS_URL=wss://api.nexus-platform.com/ws
NEXT_PUBLIC_APP_VERSION=1.0.0
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 📚 Documentation

### Available Documentation
- **[Executive Summary](docs/EXECUTIVE_SUMMARY.md)** - High-level platform overview
- **[UI/UX Guide](docs/UI_UX_PAGES_GUIDE.md)** - Detailed frontend architecture and design system
- **[Frenly AI Agent Guide](docs/FRENLY_AI_AGENT_GUIDE.md)** - AI agent implementation and features

### Component Documentation
Each component includes comprehensive documentation with:
- Props interface
- Usage examples
- Accessibility notes
- Performance considerations

## 🤝 Contributing

### Development Workflow
1. Create feature branch from `main`
2. Implement changes with tests
3. Run linting and tests
4. Submit pull request
5. Code review and merge

### Code Standards
- **TypeScript** - Strict mode enabled
- **ESLint** - Airbnb configuration
- **Prettier** - Code formatting
- **Conventional Commits** - Commit message format

## 🔧 Troubleshooting

### Common Issues

#### Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### TypeScript Errors
```bash
# Check TypeScript configuration
npx tsc --noEmit
```

#### Performance Issues
```bash
# Analyze bundle size
npm run analyze
```

## 📞 Support

### Getting Help
- **Documentation** - Check the docs folder for comprehensive guides
- **Issues** - Create GitHub issues for bugs and feature requests
- **Discussions** - Use GitHub discussions for questions
- **AI Assistant** - Use the Frenly AI Avatar for contextual help

### Resources
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Framer Motion Documentation](https://www.framer.com/motion/)

---

## 🎉 Summary

The Nexus Platform Frontend provides a comprehensive, modern, and accessible interface for complex forensic investigation and compliance management workflows. With its AI-powered assistance, responsive design, and performance optimization, it delivers an exceptional user experience while maintaining the highest standards of accessibility and usability.

Built with modern web technologies and best practices, the frontend serves as a solid foundation for continued development and enhancement of the Nexus Platform ecosystem.
