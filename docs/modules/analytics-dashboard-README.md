# Analytics Dashboard

A brutalist 3D monospace React UI for consuming the analytics API and displaying data about connected accounts.

## Features

- 🎨 **Brutalist 3D Design**: Terminal-inspired UI with 3D effects and monospace typography
- 📊 **Real-time Analytics**: Live metrics from YouTube, Instagram, and TikTok
- 🎯 **Cross-platform Stats**: Aggregated views, likes, comments, and shares
- 🚀 **3D Animations**: Smooth transitions and interactive elements
- 📱 **Responsive**: Works on desktop and mobile devices

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Three.js** with React Three Fiber for 3D effects
- **Lucide React** for icons

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Analytics API server running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Building for Production

```bash
# Build the application
npm run build

# Preview the build
npm run preview
```

## API Integration

The dashboard connects to the analytics API server. Make sure the backend is running:

```bash
# From the main project directory
make start-analytics
```

## Components

### Core Components

- **AnalyticsDashboard**: Main dashboard container
- **TerminalHeader**: Terminal-style header with status indicators
- **MetricCard**: Individual metric display cards
- **PlatformStats**: Platform-specific statistics
- **TopVideos**: Top performing videos list
- **LoadingScreen**: Animated loading screen

### Styling

The UI uses a custom Tailwind configuration with:

- **Terminal Colors**: Green (#00ff41), Red (#ff0040), Blue (#0080ff)
- **Brutalist Effects**: 3D box shadows and transforms
- **Monospace Font**: JetBrains Mono
- **Animations**: Glitch effects, pulse glows, and smooth transitions

## Development

### Project Structure

```
src/
├── components/          # React components
│   ├── AnalyticsDashboard.tsx
│   ├── TerminalHeader.tsx
│   ├── LoadingScreen.tsx
│   ├── MetricCard.tsx
│   ├── PlatformStats.tsx
│   └── TopVideos.tsx
├── services/            # API services
│   └── analyticsApi.ts
├── App.tsx             # Main app component
├── main.tsx            # Entry point
└── index.css           # Global styles with Tailwind
```

### Customizing

- **Colors**: Update `tailwind.config.js` for different color schemes
- **3D Effects**: Modify the `brutalist-box` classes in `index.css`
- **Animations**: Adjust Framer Motion animations in components
- **API Endpoints**: Update `analyticsApi.ts` for different backend URLs

## Deployment

The dashboard can be deployed to any static hosting service:

- **Vercel**: `vercel --prod`
- **Netlify**: Connect to GitHub repository
- **GitHub Pages**: Use `npm run build` and deploy `dist/` folder

## License

MIT License - see LICENSE file for details.