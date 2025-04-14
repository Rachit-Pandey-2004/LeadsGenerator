import { BrowserRouter , Routes, Route } from 'react-router-dom';
import { FC } from 'react';
import Home from './pages/Home';
import History from './pages/History';

const App:FC = ()=> {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/history" element={<History />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;