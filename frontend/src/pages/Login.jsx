import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StarBorder from '../Rc_Animation/animations/StarBorder';
import DecryptedText from "../Rc_Animation/text-animations/DecryptedText";
import '../styles/login.css';

export default function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
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
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Login failed. Please try again.');
        return;
      }

      const data = await response.json();

      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user_id', data.user_id);
      localStorage.setItem('username', data.username);

      navigate('/stock-market');
    } catch (err) {
      console.error('Login error:', err);
      setError('An unexpected error occurred. Please try again later.');
    }
  };

  return (
    <div className="login-container">
      <div className="login-form-wrapper">
        <h2>
          <DecryptedText
            text="LOGIN"
            speed={100}
            animateOn="view"
            maxIterations={20}
            characters="ABCD1234!?"
            parentClassName="all-letters"
            encryptedClassName="encrypted"
          />
        </h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <input
              type="email"
              name="email"
              placeholder="Email Address"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <StarBorder
              as="button"
              type="submit"
              color="cyan"
              speed="2s"
            >
              Login
            </StarBorder>
          </div>
        </form>
        <div className="form-footer">
          <p>Don't have an account?
            <span
              className="register-link"
              onClick={() => navigate('/register')}
            >
              Register Now
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}