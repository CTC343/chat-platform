// 聊天模块 - 处理消息收发逻辑
let currentUser = null;
let selectedUser = null;
let isPrivateMode = false;
let messagePollingInterval = null;

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', async () => {
  try {
    currentUser = await api.getCurrentUser();
    document.getElementById('user-nickname').textContent = currentUser.nickname;
    document.getElementById('user-role').textContent = currentUser.role === 'admin' ? '管理员' : '用户';
    
    if (currentUser.role === 'admin') {
      document.getElementById('admin-section').style.display = 'block';
    }
    
    // 加载消息
    await loadMessages();
    
    // 启动轮询
    messagePollingInterval = setInterval(loadMessages, 3000);
    
    // 加载用户列表
    await loadUsers();
  } catch (error) {
    console.error('初始化失败:', error);
    window.location.href = '/';
  }
});

// 加载消息
async function loadMessages() {
  try {
    const messages = await api.getLatestMessages();
    renderMessages(messages);
  } catch (error) {
    console.error('加载消息失败:', error);
  }
}

// 渲染消息
function renderMessages(messages) {
  const container = document.getElementById('messages-container');
  const noMessages = document.getElementById('no-messages');
  
  if (messages.length === 0) {
    noMessages.style.display = 'flex';
    container.innerHTML = '';
    container.appendChild(noMessages);
    return;
  }
  
  noMessages.style.display = 'none';
  
  // 保留no-messages元素
  container.innerHTML = '';
  container.appendChild(noMessages);
  
  messages.forEach(message => {
    const messageEl = createMessageElement(message);
    container.appendChild(messageEl);
  });
  
  // 滚动到底部
  container.scrollTop = container.scrollHeight;
}

// 创建消息元素
function createMessageElement(message) {
  const isOwn = message.sender_id === currentUser.id;
  const isPrivate = message.visibility === 'private';
  
  const div = document.createElement('div');
  div.className = `message ${isOwn ? 'own' : ''} ${isPrivate ? 'private' : ''}`;
  
  let contentHtml = '';
  if (message.message_type === 'text') {
    contentHtml = `<div class="message-text">${escapeHtml(message.content)}</div>`;
  } else {
    const icon = getFileIcon(message.message_type);
    const fileUrl = api.getFileUrl(message.id);
    
    // 图片类型直接显示预览
    if (message.message_type === 'image') {
      contentHtml = `
        <div class="message-file">
          <div class="file-info">
            <span class="file-icon">${icon}</span>
            <span class="file-name">${escapeHtml(message.content)}</span>
          </div>
          <img src="${fileUrl}" alt="${escapeHtml(message.content)}" class="message-image-preview" 
               onclick="window.open('${fileUrl}', '_blank')" 
               onerror="this.style.display='none'">
          <a href="${fileUrl}" target="_blank" class="file-download">下载</a>
        </div>
      `;
    } else {
      contentHtml = `
        <div class="message-file">
          <div class="file-info">
            <span class="file-icon">${icon}</span>
            <span class="file-name">${escapeHtml(message.content)}</span>
          </div>
          <a href="${fileUrl}" target="_blank" class="file-download">下载</a>
        </div>
      `;
    }
  }
  
  div.innerHTML = `
    <div class="message-avatar">${message.sender.nickname.charAt(0).toUpperCase()}</div>
    <div class="message-content">
      <div class="message-header">
        <span class="message-nickname">${escapeHtml(message.sender.nickname)}</span>
        ${isPrivate ? '<span class="private-badge">私密</span>' : ''}
        <span class="message-time">${formatTime(message.created_at)}</span>
      </div>
      ${contentHtml}
    </div>
  `;
  
  return div;
}

// 发送消息
async function sendMessage(e) {
  e.preventDefault();
  
  const input = document.getElementById('message-input');
  const content = input.value.trim();
  
  if (!content) return;
  
  try {
    await api.sendMessage(
      content,
      'text',
      isPrivateMode ? 'private' : 'public',
      isPrivateMode && selectedUser ? selectedUser.id : null
    );
    
    input.value = '';
    await loadMessages();
  } catch (error) {
    alert('发送失败: ' + error.message);
  }
}

// 上传文件
async function uploadFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  
  // 检查文件大小 (10MB)
  if (file.size > 10 * 1024 * 1024) {
    alert('文件大小不能超过10MB');
    return;
  }
  
  try {
    await api.uploadFile(
      file,
      isPrivateMode ? 'private' : 'public',
      isPrivateMode && selectedUser ? selectedUser.id : null
    );
    
    await loadMessages();
  } catch (error) {
    alert('上传失败: ' + error.message);
  }
  
  // 清空文件输入
  e.target.value = '';
}

// 加载用户列表
async function loadUsers() {
  try {
    const users = await api.getPendingUsers();
    renderUsers(users.filter(u => u.id !== currentUser.id));
  } catch (error) {
    console.error('加载用户列表失败:', error);
  }
}

// 渲染用户列表
function renderUsers(users) {
  const container = document.getElementById('users-container');
  container.innerHTML = '';
  
  users.forEach(user => {
    const div = document.createElement('div');
    div.className = `user-item ${selectedUser?.id === user.id ? 'selected' : ''}`;
    div.onclick = () => selectUser(user);
    div.innerHTML = `
      <div class="user-avatar">${user.nickname.charAt(0).toUpperCase()}</div>
      <div class="user-details">
        <span class="user-name">${escapeHtml(user.nickname)}</span>
        <span class="user-status">${user.status === 'approved' ? '在线' : '待审核'}</span>
      </div>
    `;
    container.appendChild(div);
  });
}

// 选择用户进行私聊
function selectUser(user) {
  selectedUser = user;
  isPrivateMode = true;
  
  document.getElementById('btn-public').classList.remove('active');
  document.getElementById('btn-private').classList.add('active');
  document.getElementById('chat-title').textContent = `与 ${user.nickname} 的私密对话`;
  document.getElementById('private-indicator').style.display = 'inline';
  document.getElementById('message-input').placeholder = '发送私密消息...';
  document.getElementById('user-list').style.display = 'none';
  
  // 更新用户列表选中状态
  document.querySelectorAll('.user-item').forEach(el => el.classList.remove('selected'));
  event.currentTarget.classList.add('selected');
  
  loadMessages();
}

// 切换到公共聊天
function switchToPublic() {
  selectedUser = null;
  isPrivateMode = false;
  
  document.getElementById('btn-public').classList.add('active');
  document.getElementById('btn-private').classList.remove('active');
  document.getElementById('chat-title').textContent = '公共聊天大厅';
  document.getElementById('private-indicator').style.display = 'none';
  document.getElementById('message-input').placeholder = '发送消息...';
  document.getElementById('user-list').style.display = 'none';
  
  loadMessages();
}

// 切换用户列表显示
function toggleUserList() {
  const userList = document.getElementById('user-list');
  userList.style.display = userList.style.display === 'none' ? 'block' : 'none';
}

// 获取文件图标
function getFileIcon(type) {
  const icons = {
    'image': '🖼️',
    'video': '🎥',
    'audio': '🎵',
    'file': '📄'
  };
  return icons[type] || '📄';
}

// 格式化时间
function formatTime(dateStr) {
  const date = new Date(dateStr);
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

// HTML转义
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
