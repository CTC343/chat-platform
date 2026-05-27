// 认证模块 - 处理登录注册逻辑
document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const toggleLink = document.getElementById('toggle-form');
  const subtitle = document.getElementById('subtitle');
  const errorMessage = document.getElementById('error-message');
  const successMessage = document.getElementById('success-message');

  let isLoginMode = true;

  // 检查是否已登录
  if (api.token) {
    checkAuth();
  }

  // 切换登录/注册表单
  toggleLink.addEventListener('click', (e) => {
    e.preventDefault();
    isLoginMode = !isLoginMode;
    
    if (isLoginMode) {
      loginForm.style.display = 'flex';
      registerForm.style.display = 'none';
      subtitle.textContent = '登录您的账号';
      toggleLink.textContent = '没有账号？立即注册';
    } else {
      loginForm.style.display = 'none';
      registerForm.style.display = 'flex';
      subtitle.textContent = '注册新账号';
      toggleLink.textContent = '已有账号？立即登录';
    }
    
    hideMessages();
  });

  // 登录表单提交
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
      await api.login(username, password);
      window.location.href = '/chat.html';
    } catch (error) {
      showError(error.message);
    }
  });

  // 注册表单提交
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideMessages();
    
    const username = document.getElementById('reg-username').value;
    const nickname = document.getElementById('reg-nickname').value;
    const password = document.getElementById('reg-password').value;
    const confirm = document.getElementById('reg-confirm').value;
    
    if (password !== confirm) {
      showError('两次输入的密码不一致');
      return;
    }
    
    if (password.length < 6) {
      showError('密码长度不能少于6位');
      return;
    }
    
    try {
      await api.register(username, password, nickname);
      showSuccess('注册成功！请等待管理员审核后即可登录。');
      
      // 3秒后切换到登录
      setTimeout(() => {
        isLoginMode = true;
        loginForm.style.display = 'flex';
        registerForm.style.display = 'none';
        subtitle.textContent = '登录您的账号';
        toggleLink.textContent = '没有账号？立即注册';
        hideMessages();
      }, 3000);
    } catch (error) {
      showError(error.message);
    }
  });

  // 检查认证状态
  async function checkAuth() {
    try {
      await api.getCurrentUser();
      window.location.href = '/chat.html';
    } catch (error) {
      api.setToken(null);
    }
  }

  // 显示错误消息
  function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    successMessage.style.display = 'none';
  }

  // 显示成功消息
  function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';
    errorMessage.style.display = 'none';
  }

  // 隐藏消息
  function hideMessages() {
    errorMessage.style.display = 'none';
    successMessage.style.display = 'none';
  }
});