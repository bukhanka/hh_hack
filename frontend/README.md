# 📰 Financial News RADAR - Frontend

Modern Next.js frontend for the Financial News RADAR system - AI-powered hot news detection and analysis for financial markets.

## 🎨 Features

- **Modern Dashboard** - Beautiful, responsive interface with real-time updates
- **Interactive Story Cards** - Expandable cards with detailed analysis
- **Hotness Visualization** - Radar charts and metric bars for 5-dimensional scoring
- **Timeline View** - Visual timeline of news events with source attribution
- **Draft Preview** - Formatted article drafts ready for publication
- **Smooth Animations** - Framer Motion powered transitions and interactions

## 🛠️ Tech Stack

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icons
- **Axios** - API communication

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- FastAPI backend running (default: http://localhost:8000)

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Edit .env.local if your backend is on a different URL
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📁 Project Structure

```
frontend/
├── app/
│   ├── page.tsx          # Main dashboard page
│   ├── layout.tsx        # Root layout
│   └── globals.css       # Global styles
├── components/
│   ├── ControlPanel.tsx  # Scan configuration panel
│   ├── StoryCard.tsx     # News story display card
│   ├── HotnessChart.tsx  # Radar chart for hotness metrics
│   ├── HotnessMetrics.tsx # Bar charts for metrics
│   └── StatsDisplay.tsx  # Statistics cards
├── lib/
│   ├── api.ts            # API client
│   └── types.ts          # TypeScript types
└── public/               # Static assets
```

## 🎯 Features in Detail

### Multi-dimensional Hotness Analysis
- **Unexpectedness** - How surprising is this news?
- **Materiality** - Impact on price/volatility
- **Velocity** - Speed of news spread
- **Breadth** - Number of affected assets
- **Credibility** - Source reliability

### Deep Research Integration
- Stories with hotness ≥ 0.7 get comprehensive deep research
- 20+ additional sources
- Detailed market impact analysis
- Enhanced draft articles

### Real-time Updates
- Health check monitoring
- Cached results loading
- Processing status feedback

## 🔌 API Integration

The frontend communicates with the FastAPI backend through these endpoints:

- `GET /api/health` - Backend health check
- `POST /api/process` - Process news and get hot stories
- `GET /api/last-result` - Retrieve last cached result

## 🎨 Customization

### Colors

Edit `tailwind.config.ts` to customize the color scheme:

```typescript
theme: {
  extend: {
    colors: {
      // Add your custom colors
    }
  }
}
```

### API URL

Change the backend URL in `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://your-backend-url:8000
```

## 📱 Responsive Design

The interface is fully responsive and works on:
- Desktop (1920px+)
- Laptop (1024px+)
- Tablet (768px+)
- Mobile (320px+)

## 🐛 Troubleshooting

### Backend Connection Error

If you see "Backend Offline":
1. Ensure FastAPI backend is running on port 8000
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS is enabled in FastAPI

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

## 📄 License

Part of the Financial News RADAR system.

## 🤝 Contributing

This is a hackathon project. For production use, consider:
- Adding authentication
- Implementing real-time WebSocket updates
- Adding more visualization options
- Implementing story bookmarking
- Adding export functionality
