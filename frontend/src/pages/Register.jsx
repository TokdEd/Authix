import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StarBorder from '../Rc_Animation/animations/StarBorder';
import DecryptedText from "../Rc_Animation/text-animations/DecryptedText";
import '../styles/register.css';

export default function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');

  const API_URL = process.env.REACT_APP_API_URL;

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      setError('兩次輸入的密碼不一致');
      return;
    }

    setError('');

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password,
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || '註冊失敗，請稍後重試');
        return;
      }

      navigate('/login');
    } catch (err) {
      console.error('Register error:', err);
      setError('註冊失敗，請稍後重試');
    }
  };

  return (
    <div className="register-container">
      <div className="register-form-wrapper">
        <h2>
          <DecryptedText
            text="REGISTER"
            speed={100}
            animateOn="view"
            maxIterations={20}
            characters="ABCD1234!?"
            parentClassName="all-letters"
            encryptedClassName="encrypted"
          />
        </h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <input
              type="text"
              name="name"
              placeholder="用戶名"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="email"
              name="email"
              placeholder="電子郵箱"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              name="password"
              placeholder="密碼"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              name="confirmPassword"
              placeholder="確認密碼"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <StarBorder as="button" type="submit" speed="2s">
              註冊
            </StarBorder>
          </div>
        </form>
        <div className="form-footer">
          <p>已有帳號？
            <span
              className="login-link"
              onClick={() => navigate('/login')}
            >
              立即登入
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}