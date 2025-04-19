import { BrowserRouter , Routes, Route } from 'react-router-dom';
import { FC } from 'react';
import Home from './pages/Home';
import History from './pages/History';
import SettingPage from './pages/Setting';

const App:FC = ()=> {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/history" element={<History />} />
        <Route path="/settings" element={<SettingPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;