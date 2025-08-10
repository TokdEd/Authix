// frontend/src/App.jsx

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';       // 您提供的登入頁面
import Register from './pages/Register'; // 您提供的註冊頁面

// 建立一個簡單的登入後頁面作為跳轉目標
const StockMarket = () => {
    const username = localStorage.getItem('username');
    return (
        <div style={{ padding: '50px', textAlign: 'center' }}>
            <h1>歡迎, {username || '使用者'}!</h1>
            <p>您已成功登入。</p>
        </div>
    );
};

function App() {
    return (
        <Router>
            <Routes>
                {/* 預設路徑導向登入頁 */}
                <Route path="/" element={<Navigate to="/login" />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/stock-market" element={<StockMarket />} />
            </Routes>
        </Router>
    );
}

export default App;