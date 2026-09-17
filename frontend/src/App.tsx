import { Route, Routes } from 'react-router-dom';
import Navigation from './components/Navigation/Navigation';
import Dashboard from './components/Dashboard/Dashboard';
import Portfolio from './components/Portfolio/Portfolio';
import Options from './components/Options/Options';
import SentimentAnalysis from './components/SentimentAnalysis/SentimentAnalysis';
import TradeHistory from './components/TradeHistory/TradeHistory';

function App() {
  return (
    <>
      <Navigation />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/options" element={<Options />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/sentiment" element={<SentimentAnalysis />} />
        <Route path="/history" element={<TradeHistory />} />
        <Route path="*" element={<Dashboard />} />
      </Routes>
    </>
  );
}

export default App;