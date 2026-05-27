// API服务 - 处理所有后端通信
const API_BASE = '';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  // 设置令牌
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  // 获取请求头
  getHeaders(contentType = 'application/json') {
    const headers = {};
    if (contentType) {
      headers['Content-Type'] = contentType;
    }
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  // 通用请求方法
  async request(url, options = {}) {
    try {
      const response = await fetch(`${API_BASE}${url}`, {
        ...options,
        headers: this.getHeaders(options.contentType)
      });

      if (response.status === 401) {
        this.setToken(null);
        window.location.href = '/';
        throw new Error('未授权，请重新登录');
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || '请求失败');
      }

      return data;
    } catch (error) {
      console.error('API请求错误:', error);
      throw error;
    }
  }

  // 用户注册
  async register(username, password, nickname) {
    return this.request('/users/register', {
      method: 'POST',
      body: JSON.stringify({ username, password, nickname })
    });
  }

  // 用户登录
  async login(username, password) {
    const data = await this.request('/users/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    this.setToken(data.access_token);
    return data;
  }

  // 获取当前用户信息
  async getCurrentUser() {
    return this.request('/users/me');
  }

  // 获取待审核用户
  async getPendingUsers() {
    return this.request('/users/pending');
  }

  // 审核用户
  async approveUser(userId, status) {
    return this.request('/users/approve', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, status })
    });
  }

  // 获取最新消息
  async getLatestMessages(limit = 50) {
    return this.request(`/messages/latest?limit=${limit}`);
  }

  // 发送消息
  async sendMessage(content, messageType = 'text', visibility = 'public', receiverId = null) {
    return this.request('/messages/send', {
      method: 'POST',
      body: JSON.stringify({
        content,
        message_type: messageType,
        visibility,
        receiver_id: receiverId
      })
    });
  }

  // 上传文件
  async uploadFile(file, visibility = 'public', receiverId = null) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('visibility', visibility);
    if (receiverId) {
      formData.append('receiver_id', receiverId);
    }

    const response = await fetch(`${API_BASE}/messages/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      },
      body: formData
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || '上传失败');
    }

    return response.json();
  }

  // 获取文件下载URL
  getFileUrl(messageId) {
    return `${API_BASE}/messages/file/${messageId}`;
  }

  // 获取所有消息（管理员）
  async getAllMessages() {
    return this.request('/messages/admin/all');
  }

  // 删除消息（管理员）
  async deleteMessage(messageId) {
    return this.request(`/messages/admin/${messageId}`, {
      method: 'DELETE'
    });
  }

  // 退出登录
  logout() {
    this.setToken(null);
    window.location.href = '/';
  }
}

// 创建全局API实例
const api = new ApiService();
