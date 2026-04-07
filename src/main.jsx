import './main.css'; // 把 index.css 改成 main.css
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx' // 确保这里指向你的主组件

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)