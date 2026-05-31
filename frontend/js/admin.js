// 管理模块 - 处理管理员功能
let currentTab = 'users';

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const user = await api.getCurrentUser();
    if (user.role !== 'admin') {
      window.location.href = '/chat.html';
      return;
    }
    
    await loadData();
    
    // 每5秒自动刷新，方便管理员看到新注册用户
    setInterval(loadData, 5000);
  } catch (error) {
    console.error('初始化失败:', error);
    window.location.href = '/';
  }
});

// 加载数据
async function loadData() {
  await Promise.all([
    loadAllUsers(),
    loadAllMessages()
  ]);
}

// 加载所有用户
async function loadAllUsers() {
  try {
    const users = await api.getAllUsers();
    document.getElementById('pending-count').textContent = users.length;
    
    const noUsers = document.getElementById('no-users');
    const usersList = document.getElementById('users-list');
    
    if (users.length === 0) {
      noUsers.style.display = 'block';
      usersList.innerHTML = '';
      return;
    }
    
    noUsers.style.display = 'none';
    usersList.innerHTML = '';
    
    users.forEach(user => {
      const card = createUserCard(user);
      usersList.appendChild(card);
    });
  } catch (error) {
    console.error('加载用户失败:', error);
  }
}

// 创建用户卡片
function createUserCard(user) {
  const div = document.createElement('div');
  div.className = 'user-card';
  
  const statusBadge = user.status === 'approved' ? 
    '<span class="status-badge approved">已通过</span>' : 
    user.status === 'pending' ? 
    '<span class="status-badge pending">待审核</span>' : 
    '<span class="status-badge rejected">已拒绝</span>';
  
  const mutedBadge = user.muted ? '<span class="status-badge muted">已禁言</span>' : '';
  
  div.innerHTML = `
    <div class="user-card-info" onclick="viewUserMessages(${user.id}, '${escapeHtml(user.nickname)}')" style="cursor:pointer">
      <div class="user-card-avatar">${user.nickname.charAt(0).toUpperCase()}</div>
      <div class="user-card-details">
        <h3>${escapeHtml(user.nickname)} ${statusBadge} ${mutedBadge}</h3>
        <p>用户名: ${escapeHtml(user.username)} | 角色: ${user.role === 'admin' ? '管理员' : '用户'}</p>
        <p>注册时间: ${formatDateTime(user.created_at)}</p>
      </div>
    </div>
    <div class="user-actions">
      ${user.status === 'pending' ? `
        <button class="btn btn-primary btn-sm" onclick="approveUser(${user.id}, 'approved')">通过</button>
        <button class="btn btn-danger btn-sm" onclick="approveUser(${user.id}, 'rejected')">拒绝</button>
      ` : ''}
      ${user.role !== 'admin' ? `
        <button class="btn btn-warning btn-sm" onclick="muteUser(${user.id}, ${user.muted ? 0 : 1})">${user.muted ? '解禁' : '禁言'}</button>
        <button class="btn btn-danger btn-sm" onclick="deleteUser(${user.id}, '${escapeHtml(user.username)}')">注销</button>
      ` : ''}
      <button class="btn btn-secondary btn-sm" onclick="viewUserMessages(${user.id}, '${escapeHtml(user.nickname)}')">查看发言</button>
    </div>
  `;
  return div;
}

// 审核用户
async function approveUser(userId, status) {
  try {
    await api.approveUser(userId, status);
    alert(`用户已${status === 'approved' ? '审核通过' : '拒绝'}`);
    await loadAllUsers();
  } catch (error) {
    alert('审核失败: ' + error.message);
  }
}

// 禁言/解禁用户
async function muteUser(userId, muted) {
  try {
    await api.muteUser(userId, muted);
    alert(muted ? '用户已被禁言' : '用户已被解禁');
    await loadAllUsers();
  } catch (error) {
    alert('操作失败: ' + error.message);
  }
}

// 注销用户
async function deleteUser(userId, username) {
  if (!confirm(`确定要注销用户 "${username}" 吗？\n该操作将删除该用户的所有消息！`)) return;
  
  try {
    const result = await api.deleteUser(userId);
    alert(result.message);
    await loadAllUsers();
    await loadAllMessages();
  } catch (error) {
    alert('注销失败: ' + error.message);
  }
}

// 查看用户消息
async function viewUserMessages(userId, nickname) {
  try {
    const messages = await api.getUserMessages(userId);
    
    const messagesList = document.getElementById('messages-list');
    const noMessages = document.getElementById('no-messages');
    
    // 切换到消息标签
    switchTab('messages');
    document.getElementById('tab-messages').textContent = `${nickname} 的发言 (${messages.length})`;
    
    if (messages.length === 0) {
      noMessages.style.display = 'block';
      noMessages.textContent = `${nickname} 暂无发言`;
      messagesList.innerHTML = '';
      return;
    }
    
    noMessages.style.display = 'none';
    messagesList.innerHTML = '';
    
    messages.forEach(message => {
      const card = createMessageCard(message);
      messagesList.appendChild(card);
    });
  } catch (error) {
    alert('获取消息失败: ' + error.message);
  }
}

// 加载所有消息
async function loadAllMessages() {
  try {
    const messages = await api.getAllMessages();
    document.getElementById('message-count').textContent = messages.length;
    
    const noMessages = document.getElementById('no-messages');
    const messagesList = document.getElementById('messages-list');
    
    if (messages.length === 0) {
      noMessages.style.display = 'block';
      messagesList.innerHTML = '';
      return;
    }
    
    noMessages.style.display = 'none';
    messagesList.innerHTML = '';
    
    messages.forEach(message => {
      const card = createMessageCard(message);
      messagesList.appendChild(card);
    });
  } catch (error) {
    console.error('加载消息失败:', error);
  }
}

// 创建消息卡片
function createMessageCard(message) {
  const div = document.createElement('div');
  div.className = 'message-card';
  
  let contentHtml = '';
  if (message.message_type === 'text') {
    contentHtml = `<p>${escapeHtml(message.content)}</p>`;
  } else {
    const fileUrl = api.getFileUrl(message.id);
    contentHtml = `
      <div class="file-card-info">
        <span class="file-type">${message.message_type}</span>
        <span class="file-card-name">${escapeHtml(message.content)}</span>
        <a href="${fileUrl}" target="_blank" class="file-link">查看文件</a>
      </div>
    `;
  }
  
  div.innerHTML = `
    <div class="message-card-header">
      <div class="message-sender">
        <span class="sender-name">${escapeHtml(message.sender.nickname)}</span>
        ${message.visibility === 'private' ? '<span class="private-badge">私密</span>' : ''}
      </div>
      <span class="message-card-time">${formatDateTime(message.created_at)}</span>
    </div>
    <div class="message-card-content">
      ${contentHtml}
    </div>
    <div class="message-card-actions">
      <button class="btn btn-danger btn-sm" onclick="deleteMessage(${message.id})">删除</button>
    </div>
  `;
  return div;
}

// 删除消息
async function deleteMessage(messageId) {
  if (!confirm('确定要删除这条消息吗？')) return;
  
  try {
    await api.deleteMessage(messageId);
    alert('消息已删除');
    await loadAllMessages();
  } catch (error) {
    alert('删除失败: ' + error.message);
  }
}

// 切换标签
function switchTab(tab) {
  currentTab = tab;
  
  document.getElementById('tab-users').classList.toggle('active', tab === 'users');
  document.getElementById('tab-messages').classList.toggle('active', tab === 'messages');
  document.getElementById('users-section').style.display = tab === 'users' ? 'block' : 'none';
  document.getElementById('messages-section').style.display = tab === 'messages' ? 'block' : 'none';
  
  // 重置消息标签文本
  if (tab === 'users') {
    document.getElementById('tab-messages').innerHTML = '所有消息 (<span id="message-count">0</span>)';
  }
}

// 格式化日期时间
function formatDateTime(dateStr) {
  if (!dateStr) return '未知';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '未知';
  return date.toLocaleString('zh-CN');
}

// HTML转义
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
