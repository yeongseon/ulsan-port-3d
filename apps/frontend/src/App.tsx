import { Routes, Route } from 'react-router-dom';

export default function App() {
  return (
    <div className="h-screen w-screen bg-port-bg text-white flex items-center justify-center">
      <Routes>
        <Route path="/" element={<MainView />} />
      </Routes>
    </div>
  );
}

function MainView() {
  return (
    <div className="text-center">
      <h1 className="text-3xl font-bold mb-2">울산항 3D 관제 시스템</h1>
      <p className="text-port-muted">System initializing...</p>
    </div>
  );
}
