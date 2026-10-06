import { Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Overview from './pages/Overview';
import Predict from './pages/Predict';
import Models from './pages/Models';
import Discover from './pages/Discover';
import Dataset from './pages/Dataset';

export default function App() {
  return (
    <div className="min-h-screen bg-[var(--color-bg-base)] flex flex-col">
      <Navigation />
      <main className="flex-1 max-w-[1440px] w-full mx-auto p-6 md:p-10">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/predict" element={<Predict />} />
          <Route path="/models" element={<Models />} />
          <Route path="/discover" element={<Discover />} />
          <Route path="/dataset" element={<Dataset />} />
        </Routes>
      </main>
    </div>
  );
}
