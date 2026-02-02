<template>
  <!-- 主容器 -->
  <view class="container">
    <!-- 顶部固定栏 -->
    <view class="header">
      <!-- 左侧：返回按钮和菜单图标 -->
      <view class="header-left">
        <view class="back-btn" @tap="goBack">
          <image src="/static/back.png" class="icon" mode="widthFix"></image>
        </view>
        <view class="menu-icon">
          <image src="/static/menu.png" class="icon" mode="widthFix" @tap="showHistory"></image>
        </view>
      </view>
      <!-- 标题 -->
      <text class="title">元气饮食小助手</text>
      <!-- 右侧：新建对话图标 -->
      <view class="add-icon" @tap="newDialog">
        <image src="/static/add.png" class="icon" mode="widthFix"></image>
      </view>
    </view>

    <!-- 聊天滚动容器 -->
    <scroll-view 
      id="chatScrollContainer"
      ref="chatScroll"
      class="chat-scroll" 
      scroll-y 
      scroll-with-animation
      :scroll-top="scrollTop"
      :style="{ height: `calc(100vh - 100rpx)` }"
    >
      <view class="chat-container" id="chatContainer">
        <!-- 空状态：首次进入时显示 -->
        <view class="empty-state" v-if="messages.length === 0">
          <view class="logo">
            <image src="/static/标题.png" class="logo-img" mode="widthFix"></image>
          </view>
          <text class="hi">嗨～我是你的元气饮食小助手</text>
          <view class="desc">
            我可以帮你搭配健康饮食、解答食材疑惑、推荐美味食谱，把你的饮食需求告诉我吧～
          </view>
        </view>

        <!-- 聊天记录循环 -->
        <view
          class="chat-item"
          :class="{ user: item.type === 'user', assistant: item.type === 'assistant' }"
          v-for="(item, index) in messages"
          :key="index"
        >
          <!-- AI头像 -->
          <image
            v-if="item.type === 'assistant'"
            src="/static/avatar.png"
            class="avatar"
            mode="widthFix"
          />
        
          <view class="msg-list">
            <view
              class="msg-bubble"
              :class="{
                'user-msg': item.type === 'user',
                'assistant-msg': item.type === 'assistant'
              }"
            >
              <!-- 用户 -->
              <view class="user-msg-content" v-if="item.type === 'user'">
                <image
                  v-if="item.image"
                  :src="item.image"
                  class="chat-img"
                />
                <text class="msg-text">{{ item.text }}</text>
              </view>
        
              <!-- AI（只负责最终内容） -->
              <zero-markdown-view
                v-if="item.type === 'assistant'"
                :markdown="item.text"
                :aiMode="true"
                themeColor="#A37070"
                class="msg-text"
              />
            </view>
          </view>
        </view>
		
		<!-- ⭐ 流式推理临时显示 -->
		<view class="chat-item assistant" v-if="streamcontent">
		  <image src="/static/avatar.png" class="avatar" />
		  <view class="msg-list">
		    <view class="msg-bubble assistant-msg">
		      <zero-markdown-view
		        :markdown="streamcontent"
		        :aiMode="true"
		        themeColor="#A37070"
		        class="msg-text"
		      />
		    </view>
		  </view>
		</view>
        
        <!-- 底部锚点：用于滚动定位到最新消息 -->
        <view id="scrollBottomAnchor"></view>
      </view>
    </scroll-view>
    <!-- 底部输入区域 -->
    <view class="footer">
		<!-- 发送前图片缩略预览 -->
		<view class="image-preview" v-if="previewImage">
		  <image :src="previewImage" class="preview-img" mode="aspectFill"></image>
		  <view class="remove-img" @tap="previewImage = file_url = ''">×</view>
		</view>
      <!-- 输入框 -->
      <textarea class="input" v-model="query" auto-height fixed placeholder="想问饮食搭配、食材推荐或健康食谱吗？" placeholder-class="placeholder"></textarea>
      <!-- 操作按钮区域 -->
      <view class="actions">
        <!-- 深度思考按钮 -->
        <view class="action-btn" @tap="deepThink":class="deepthink == 1 ? 'web-search' : ''">
          <image src="/static/deepthink.png" class="action-icon" mode="widthFix"></image>
          <text>深度思考</text>
        </view>
        <!-- 联网搜索按钮（点击切换状态） -->
        <view class="action-btn" @tap="webSearch" :class="web == 1 ? 'web-search' : ''">
          <image src="/static/search.png" class="action-icon" mode="widthFix"></image>
          <text>联网搜索</text>
        </view>
        <!-- 上传按钮 -->
        <view class="action-btn plus-btn" @tap="uploadFile">
          <image src="/static/plus.png" class="action-icon" mode="widthFix"></image>
        </view>
        <!-- 发送按钮 -->
        <view class="send-btn" @tap="sendMsg">
          <image src="/static/send.png" class="send-icon" mode="widthFix"></image>
        </view>
      </view>
    </view>
  </view>
  
  <!-- 历史对话弹出层 -->
  <uni-popup ref="historyPopup" type="left">
    <view class="history-container">
      <view class="history-title">历史对话</view>
  
      <scroll-view scroll-y class="history-list">
        <view
          class="history-item"
          v-for="item in historyList"
          :key="item.theme_id"
          @click="openHistory(item)"
		  @longpress.stop.prevent="onLongPress(item)"
        >
          <view class="theme-name">{{ item.theme_name }}</view>
          <view class="theme-time">{{ item.create_time }}</view>
        </view>
      </scroll-view>
    </view>
  </uni-popup>
</template>

<script>
	import {
		fetchSSE
	} from '@/common/tools.js'
	
export default {
  data() {
    return {
      query: '',             // 输入框内容
      messages: [],         // 聊天消息数组
      scrollTop: 0,         // 滚动位置
      oldScrollTop: 0,     // 旧滚动位置（用于滚动计算）
      web: 0,              // 联网搜索状态：0-关闭，1-开启
	  deepthink: 0,        // 深度思考状态
	  file_url: '',        // 上传图片的访问路径
	  previewImage: '',   // 发送前的图片缩略预览
	  theme_id:0,         // 对话主题id
	  historyList: []  ,  // 历史对话列表
	  // 替换写死的1，从缓存currentUser中取真实user_id，无则0
	  user_id: uni.getStorageSync("currentUser")?.user_id || 0, 
	  streamcontent: '',   // 用于流式显示
    }
  },
  
  // 新增onShow：页面每次显示时更新user_id
  onShow() {
    const currentUser = uni.getStorageSync("currentUser");
	console.log("【聊天助手页面】当前登录用户：", currentUser);
    // 如果有登录态，就把缓存里的user_id赋值给页面的user_id
    if (currentUser && currentUser.user_id) {
      this.user_id = currentUser.user_id;
    } else {
      // 未登录则重置为0（可选，保持和data默认值一致）
      this.user_id = 0;
    }
  },

  
  methods: {
	// 长按某条历史记录
	onLongPress(item) {
		console.log(item.theme_id)
		uni.showModal({
			title: '删除对话',
			content: '确定要删除这条历史记录吗？',
			confirmText: '删除',
			confirmColor: '#d48982',
			success: (res) => {
			      if (res.confirm) {
			        this.delTheme(item.theme_id)
			      }
			}
		})
	},
	
	// 删除对应历史记录
	delTheme(theme_id) {
	  uni.request({
	    url: 'http://localhost:8000/api/delTheme/',
	    method: 'POST',
	    data: {
	      theme_id: theme_id,
		  user_id: this.user_id
	    },
		header: { 'content-type': 'application/x-www-form-urlencoded' },
		// 异步：回调函数
	    success: (res) => {
	      if (res.data.status === 'success') {
	        uni.showToast({
	          title: '删除成功',
	          icon: 'success'
	        })
	        // 从历史列表中删除
	        this.historyList = this.historyList.filter(
	          item => item.theme_id !== theme_id
	        )
			// 如果删除的是当前对话
			if (this.theme_id === theme_id) {
			  this.newDialog()   
			}
			
	      } else {
	        uni.showToast({
	          title: res.data.msg || '删除失败',
	          icon: 'none'
	        })
	      }
	    }
	  })
	},
	
	// 点击某条历史记录，恢复当时的聊天内容
	openHistory(item) {
	  const user_id = this.user_id
	  const theme_id = item.theme_id
	  uni.request({
	    url: 'http://localhost:8000/api/continue/',
	    method: 'POST',
	    data: {
		  user_id: user_id,
	      theme_id: theme_id,
	    },
		header: { 'content-type': 'application/x-www-form-urlencoded' },
	    success: (res) => {
	      if (res.data.status === 'success') {
	        // 把后端 chat 转成前端 messages
	        this.messages = res.data.chat.map(msg => {
	          return {
	            type: msg.role,     // 'user' / 'assistant'
	            text: msg.content,  // 文本内容
	            image: msg.image_url || ''    // 多模态
	          }
	        })
	
	        // 同步当前主题 id（继续对话用）
	        this.theme_id = item.theme_id
	
	        // 关掉历史弹窗
	        this.$refs.historyPopup.close();
	        
	        // 加载历史对话后滚动到底部
	        this.$nextTick(() => {
	          setTimeout(() => {
	            this.scrollToBottom();
	          }, 50);
	        });
	      }
	    }
	  })
	},
	
	// 打开历史对话弹窗
	showHistory() {
	    this.getHistoryList()
	    this.$refs.historyPopup.open()
	  },
	  
	// 获取历史对话主题列表
	getHistoryList() {
		const user_id = this.user_id
	    uni.request({
	      url: 'http://localhost:8000/api/history/',
	      method: 'POST',
	      data: {
	        user_id: user_id   
	      },
		  header: { 'content-type': 'application/x-www-form-urlencoded' },
	      success: (res) => {
	        if (res.data.status === 'success') {
	          this.historyList = res.data.history_list
	        }
	      }
	    })
	  },
	  
	// 新建对话
	newDialog() {
	  this.query = ''
	  this.messages = []
	  this.theme_id = 0
	
	  this.file_url = ''
	  this.previewImage = ''
	
	  // 如果有滚动相关
	  this.scrollTop = 0
	  this.oldScrollTop = 0
	},
	  
	// 上传文件
	uploadFile() {
		uni.chooseImage({
			count:1,  //最多选择1张图片
			success: (chooseImageRes) => {
				const tempFilePaths = chooseImageRes.tempFilePaths;
				// 选择好图片后，提交给服务器
				uni.uploadFile({
					url: 'http://localhost:8000/api/upload/',  // 接受文件的服务器端地址
					filePath: tempFilePaths[0],
					name: 'file_1',
					success: (res) => {
						console.log(res.data)
						// 转换为 JSON格式
						const data = JSON.parse(res.data)
						// AI 用（相对路径）
						this.file_url = data.file_url.replace('http://localhost:8000', '')
						// 显示用（完整 URL）
						this.previewImage = data.file_url
						console.log(this.file_url)
					}
				});
			}
		});
	},
	  
	// 深度思考
	deepThink() {
		this.deepthink = this.deepthink == 1 ? 0 : 1;
	},
    // 切换联网搜索状态
    webSearch() {
      this.web = this.web == 1 ? 0 : 1;
    },
    
    // 返回上一页或首页
    goBack() {
      const pages = getCurrentPages();
      if (pages.length > 1) {
        uni.navigateBack({ delta: 1 });
      } else {
        uni.switchTab({
          url: "/pages/index/index",
          fail: () => {
            uni.redirectTo({ url: "/pages/index/index" });
          }
        });
      }
    },
    
    // 发送消息
    sendMsg() {
      const query = this.query.trim();
	  const web = this.web
	  const deepthink = this.deepthink
	  const file_url = this.file_url
	  const theme_id = this.theme_id
	  
      if (!query) {
        uni.showToast({ title: '请输入想要咨询的内容～', icon: 'none' });
        return;
      }
      
      // 用户消息
      this.messages.push({
        type: 'user',
        text: query,
        image: this.previewImage || '',
      });
      
      // 清空输入与图片
      this.query = '';
      this.file_url = '';
      this.previewImage = '';
	  this.streamText = '';
	  this.fullText = '';
      
      // 等待DOM更新后滚动到底部
      this.$nextTick(() => {
        setTimeout(() => {
          this.scrollToBottom();
        }, 50);
      });

      // 发送请求到后端API
	  // 流式推理：使用fetch和服务器进行SSE通信
	  fetchSSE('http://localhost:8000/api/ai/', {
		  body: {
			query: query,
			user_id: this.user_id,
			theme_id: theme_id,  // 对话主题 id
			file_url: file_url,  // 上传文件的访问路径（必须是相对路径）
			web:web,  // 联网搜索
			deepthink:deepthink,  // 深度思考
		  },
		  // 带token的头消息
		  headers: {
		  			"Content-Type": "application/x-www-form-urlencoded", 
		  },
	  }, (msg) => {
			console.log("收到:", msg);
			
			if (msg && msg.includes('[@#--END--#@]')) {
				console.log("流式结束")
				
				// 推入最终完整消息
				this.messages.push({
				  type: 'assistant',
				  text: this.streamcontent,
				});
				// 清空流式缓存
				this.streamcontent = '';
				// 强制一次 DOM 更新
				this.$nextTick(() => {
				    this.scrollToBottom();
				  });
				
				return;
			}
			// 获取对话的主题ID
			if (msg.includes("<theme_id_1>")) {
			  // 正则解释：
			  // <theme_id_1>：匹配开头标签
			  // (\d+)：捕获中间的数字（真实theme_id），括号是分组
			  // <theme_id_1>：匹配结尾标签
			  const match = msg.match(/<theme_id_1>(\d+)<theme_id_1>/);
			  if (match && match[1]) { // match[1]是分组捕获的真实ID
			    this.theme_id = Number(match[1]); // 转成数字类型，和后端一致
			    console.log("解析到正确的theme_id：", this.theme_id); // 调试用，可后续删除
			  }
			  return;
			}
			
			// 流式显示
		    this.streamcontent += msg.replace(/\\n/g, '\n');
		});
	},
		
	// 滚动到聊天区域底部
	scrollToBottom() {
	  // 通过改变scrollTop值实现滚动
	  this.scrollTop = this.oldScrollTop + 1;
	  this.$nextTick(() => {
	    this.scrollTop = 999999; // 设置足够大的值确保滚动到底部
	    this.oldScrollTop = this.scrollTop;
	  });
	},	
	
	}, 
}
</script>

<style scoped lang="scss">
/* ========== 混入定义 ========== */
@mixin flex {
  /* #ifndef APP-NVUE */
  display: flex;
  /* #endif */
  flex-direction: row;
}

@mixin height {
  /* #ifndef APP-NVUE */
  height: 100%;
  /* #endif */
  /* #ifdef APP-NVUE */
  flex: 1;
  /* #endif */
}

/* ========== 颜色变量定义 ========== */
$cream-bg: #fdfbf8;          // 主背景色
$cream-primary: #e8dcca;     // 主要色调（按钮、发送按钮背景）
$cream-secondary: #d4e6f1;   // 次要色调（用户消息背景）
$cream-text-main: #5c544b;   // 主要文字颜色
$cream-text-secondary: #a89f94; // 次要文字颜色（占位符）
$cream-shadow: 0 4rpx 16rpx rgba(200, 190, 170, 0.15); // 通用阴影

/* 联网搜索和深度思考激活状态样式 */
.web-search {
  background-color: #d4e6f1 !important;
}

/* ========== 主容器样式 ========== */
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: $cream-bg;
  justify-content: space-between;
  padding-bottom: env(safe-area-inset-bottom); // 适配底部安全区域
}

/* ========== 顶部导航栏样式 ========== */
.header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100rpx;
  background-color: $cream-bg;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 30rpx;
  box-sizing: border-box;
  box-shadow: $cream-shadow;
  z-index: 10;
  position: relative;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
  position: absolute;
  left: 30rpx;
}

.add-icon {
  position: absolute;
  right: 30rpx;
}

.title {
  font-size: 36rpx;
  font-weight: 500;
  color: $cream-text-main;
}

.icon {
  width: 40rpx;
  height: 40rpx;
  border-radius: 8rpx;
}

/* ========== 聊天区域样式 ========== */
.chat-scroll {
  padding-top: 10rpx; // 为固定头部留出空间
  padding-bottom: 200rpx; // 为底部输入栏留出空间
  box-sizing: border-box;
}

.chat-container {
  display: flex;
  flex-direction: column;
  padding: 20rpx 30rpx;
  background-color: $cream-bg;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 0 60rpx;
  margin-top: 40rpx;
}

.empty-state .logo-img {
  width: 100%;
  height: auto;
  margin-bottom: 40rpx;
  border-radius: 24rpx;
}

.empty-state .hi {
  font-size: 40rpx;
  font-weight: 500;
  color: $cream-text-main;
  letter-spacing: 2rpx;
}

.empty-state .desc {
  font-size: 30rpx;
  color: $cream-text-secondary;
  margin-top: 20rpx;
  line-height: 50rpx;
  letter-spacing: 1rpx;
}

/* 单条聊天消息样式 */
.chat-item {
  display: flex;
  margin-bottom: 30rpx;
  align-items: flex-end;
  witdth: 100%;
}

/* 用户消息对齐方式 */
.chat-item.user {
  justify-content: flex-end;
}

/* AI消息对齐方式 */
.chat-item.assistant {
  justify-content: flex-start;
  align-items: flex-start;
}

/* ========== 消息列表容器样式 ========== */
.msg-list {

}

/* 用户消息的消息列表强制右对齐 */
.chat-item.user .msg-list {
  display: flex;
  justify-content: flex-end;
  max-width: 70%;
}

/* 助手消息的 msg-list 恢复默认 */
.chat-item.assistant .msg-list {
  display: block;
  max-width: 100%;
}

/* AI头像样式 */
.avatar {
  width: 60rpx;
  height: 60rpx;
  margin-right: 15rpx;
  border-radius: 50%;
  background-color: $cream-primary;
  box-shadow: $cream-shadow;
  flex-shrink: 0;
}

/* 消息气泡通用样式 */
.msg-bubble {
  padding: 0;
  max-width: 70%;
  box-shadow: none;
  border-radius: 20rpx;
  box-sizing: border-box;
}

/* 用户消息气泡样式 */
.user-msg {
  background-color: $cream-secondary;
  border-radius: 20rpx 20rpx 4rpx 20rpx; // 右下角直角
  color: $cream-text-main;
  max-width: 500rpx;
  display: block;  
  text-align: left;
  padding: 20rpx 15rpx;
  box-shadow: $cream-shadow;
  box-sizing: border-box;
  width: 100%;
}

/* AI消息气泡样式 */
.assistant-msg {
  background-color: #ffffff;
  border-radius: 20rpx 20rpx 20rpx 20rpx; // 全圆角
  max-width: 600rpx;
  padding: 20rpx 15rpx;
  box-shadow: $cream-shadow;
  text-align: left;
}

/* 消息文字样式 */
.msg-text {
  font-size: 30rpx;
  line-height: 46rpx;
  letter-spacing: 1rpx;
  color: $cream-text-main;
}

/* ========== 底部输入区域样式 ========== */
.footer {
  position: fixed;
  bottom: 0;
  left: 20rpx;
  width: 100%;
  background-color: $cream-bg;
  padding: 20rpx 30rpx 25rpx env(safe-area-inset-bottom);
  box-sizing: border-box;
  box-shadow: 0 -4rpx 16rpx rgba(200, 190, 170, 0.1);
  z-index: 9;
}

/* 输入框样式 */
.input {
  width: 100%;
  height: 90rpx;
  border-radius: 40rpx;
  background-color: #ffffff;
  padding: 24rpx 30rpx;
  font-size: 30rpx;
  margin-bottom: 15rpx;
  box-sizing: border-box;
  color: $cream-text-main;
  box-shadow: $cream-shadow;
  border: none;
  outline: none;
}

/* 占位符样式 */
.placeholder {
  color: $cream-text-secondary;
  font-size: 28rpx;
}

/* 操作按钮区域 */
.actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

/* 功能按钮样式 */
.action-btn {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  border-radius: 40rpx;
  padding: 12rpx 24rpx;
  font-size: 26rpx;
  color: $cream-text-main;
  box-shadow: $cream-shadow;
  transition: all 0.2s ease;
}

/* 加号按钮特殊样式 */
.action-btn.plus-btn {
  padding: 12rpx;
}

/* 按钮点击效果 */
.action-btn:active {
  transform: scale(0.96);
}

/* 按钮图标样式 */
.action-icon {
  width: 36rpx;
  height: 36rpx;
  margin-right: 10rpx;
}

/* 加号按钮图标调整 */
.plus-btn .action-icon {
  margin-right: 0;
}

/* 发送按钮样式 */
.send-btn {
  width: 80rpx;
  height: 80rpx;
  background-color: $cream-primary;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: $cream-shadow;
  transition: all 0.2s ease;
}

/* 发送按钮点击效果 */
.send-btn:active {
  transform: scale(0.96);
  background-color: #d8c8b8;
}

.send-icon {
  width: 40rpx;
  height: 40rpx;
}

/* 发送前图片预览 */
.image-preview {
  position: relative;
  width: 160rpx;
  margin-bottom: 10rpx;
}

.preview-img {
  width: 160rpx;
  height: 160rpx;
  border-radius: 16rpx;
  box-shadow: $cream-shadow;
}

.remove-img {
  position: absolute;
  top: -10rpx;
  right: -10rpx;
  width: 36rpx;
  height: 36rpx;
  background-color: rgba(0, 0, 0, 0.6);
  color: #fff;
  border-radius: 50%;
  text-align: center;
  line-height: 36rpx;
  font-size: 24rpx;
}

/* 聊天中的图片 */
.chat-img {
  width: 300rpx;
  height: 300rpx;
  border-radius: 16rpx;
  margin-bottom: 10rpx;
}

/* 用户消息内容区域（图片 + 文本纵向排列） */
.user-msg-content {
  display: flex;
  flex-direction: column;   /* 关键：上下排列 */
  align-items: flex-start;  /* 左对齐，防止被拉伸 */
  width: 100%;
}

/* ========== 历史对话侧边栏样式 ========== */
/* 整体容器 */
.history-container {
  width: 80vw;                        
  height: 100vh;                      
  background-color: #fdfbf8;          
  padding: 32rpx 24rpx;               
  box-shadow: 0 4rpx 16rpx rgba(200, 190, 170, 0.15); 
}

/* 历史对话标题 */
.history-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #5c544b;                      
  margin-bottom: 24rpx;
}

/* 历史对话列表滚动区域 */
.history-list {
  height: calc(100vh - 120rpx);        
}

/* 单条历史对话卡片 */
.history-item {
  background-color: #e8dcca;           
  border-radius: 16rpx;               
  padding: 20rpx 22rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(200, 190, 170, 0.12); 
}

/* 历史对话主题名称 */
.theme-name {
  font-size: 28rpx;
  color: #5c544b;                      
  line-height: 1.4;
}

/* 历史对话时间 */
.theme-time {
  font-size: 22rpx;
  color: #a89f94;                      
  margin-top: 8rpx;
}
</style>