<template>
  <view class="my-container">
    <!-- 顶部用户信息卡片【核心】- 奶油风卡片布局 -->
    <view class="user-card">
      <!-- 头像：根据登录态显示不同图片（核心修改） -->
      <view class="avatar-box">
        <image 
          :src="isLogin ? '/static/hua.png' : '/static/图标/用户.png'" 
          class="user-avatar" 
          mode="aspectFit"
        ></image>
      </view>
      <!-- 用户名/登录提示：登录态判断 -->
      <view class="user-info">
        <text class="user-name" v-if="isLogin">{{ userInfo.username }}</text>
        <text class="unlogin-text" v-else>请先登录，体验完整功能</text>
        <!-- 登录按钮：未登录显示，登录后隐藏 -->
        <button class="login-btn" v-else @tap="toLogin">立即登录</button>
      </view>
    </view>

    <!-- 功能入口区域 - 卡片式布局 -->
    <view class="func-card">
      <view class="func-item" v-for="(item, index) in funcList" :key="index">
        <view class="icon-placeholder">
          <image :src="item.iconUrl" mode="aspectFit" class="icon-img"></image>
        </view>
        <text class="func-text">{{ item.name }}</text>
      </view>
    </view>

    <!-- 更多设置区域 - 列表式布局 -->
    <view class="setting-card">
      <view class="setting-item" @tap="handleSetting" v-for="(item, index) in settingList" :key="index">
        <view class="setting-left">
          <view class="icon-placeholder">
            <image :src="item.iconUrl" mode="aspectFit" class="icon-img"></image>
          </view>
          <text class="setting-text">{{ item.name }}</text>
        </view>
        <view class="icon-placeholder setting-arrow">
          <image :src="arrowIcon" mode="aspectFit" class="arrow-img"></image>
        </view>
      </view>
    </view>

    <!-- 退出登录按钮：登录后显示，未登录隐藏 -->
    <button class="logout-btn" v-if="isLogin" @tap="handleLogout">退出登录</button>
  </view>
</template>

<script>
export default {
  name: "MyPage",
  
  data() {
    return {
      // 登录态标识
      isLogin: false,
	  
      // 当前登录用户信息（仅保留用户名和user_id）
      userInfo: {
        username: "", 
        user_id: 0, 
      },
	  
      // 功能入口列表（保留原有配置）
      funcList: [
        { name: "我的收藏", iconUrl: "/static/my/金针菇.png" },
        { name: "我的浏览", iconUrl: "/static/my/杏鲍菇.png" },
        { name: "饮食记录", iconUrl: "/static/my/口蘑.png" },
        { name: "健康分析", iconUrl: "/static/my/猴头菇.png" }
      ],
	  
      // 设置列表（保留原有配置）
      settingList: [
        { name: "个人资料", iconUrl: "/static/my/竹荪.png" },
        { name: "消息通知", iconUrl: "/static/my/茶树菇.png" },
        { name: "隐私设置", iconUrl: "/static/my/木耳.png" },
        { name: "关于我们", iconUrl: "/static/my/香菇.png" },
        { name: "帮助中心", iconUrl: "/static/my/灵芝.png" }
      ],
	  
      arrowIcon: "/static/my/jiantou.png"
    };
  },
  
  // 页面每次显示都检查登录态（确保user_id和头像实时同步）
  onShow() {
    this.checkLoginStatus();
  },
  
  methods: {
    /**
     * 核心：检查登录态，初始化用户信息（用户名+user_id）
     */
    checkLoginStatus() {
      const currentUser = uni.getStorageSync("currentUser");
      console.log("【我的页面】当前登录用户：", currentUser);
	  
      // 已登录：同步用户信息
      if (currentUser && currentUser.user_id) {
        this.isLogin = true;
        this.userInfo.username = currentUser.username || "默认用户";
        this.userInfo.user_id = currentUser.user_id; // 供对话等功能使用
      } else {
        // 未登录：重置状态
        this.isLogin = false;
        this.userInfo = {
          user_id: 0,
          username: ""
        };
      }
    },

    /**
     * 跳转到登录页
     */
    toLogin() {
      uni.navigateTo({
        url: "/pages/login/login"
      });
    },

    /**
     * 退出登录：清除本地存储，重置状态
     */
    handleLogout() {
      uni.showModal({
        title: "提示",
        content: "确定要退出登录吗？",
        success: (res) => {
          if (res.confirm) {
            // 清除本地登录态
            uni.removeStorageSync("currentUser");
            uni.removeStorageSync("userList");
            // 重置状态（头像会自动切换为未登录态）
            this.isLogin = false;
            this.userInfo = { user_id: 0, username: "" };
            uni.showToast({ title: "退出登录成功", icon: "success" });
          }
        }
      });
    },

    /**
     * 设置项点击事件（预留扩展）
     */
    handleSetting() {
      uni.showToast({ title: "功能开发中~", icon: "none" });
    }
  }
};
</script>

<style scoped>
/* 统一奶油风CSS变量 - 保持风格统一 */
page {
  --cream-bg: #fdfbf8; /* 主背景色 */
  --cream-primary: #e8dcca; /* 主要色调（按钮、卡片边框） */
  --cream-secondary: #d4e6f1; /* 次要色调（辅助背景） */
  --cream-text-main: #5c544b; /* 主要文字颜色 */
  --cream-text-secondary: #a89f94; /* 次要文字颜色（占位/提示） */
  --cream-shadow: 0 4rpx 16rpx rgba(200, 190, 170, 0.15); /* 通用阴影 */
  --cream-radius: 20rpx; /* 主圆角（奶油风大圆角更柔和） */
  --cream-radius-sm: 12rpx; /* 小圆角 */
  --cream-border: 1rpx solid #f0ebe6; /* 通用轻边框 */
}

/* 页面容器：主背景色，占满屏幕，内边距适配 */
.my-container {
  min-height: 100vh;
  background-color: var(--cream-bg);
  padding: 30rpx 24rpx;
  box-sizing: border-box;
}

/* 顶部用户信息卡片：核心奶油风卡片 */
.user-card {
  display: flex;
  align-items: center;
  background-color: #fff;
  border-radius: var(--cream-radius);
  box-shadow: var(--cream-shadow);
  padding: 40rpx 30rpx;
  margin-bottom: 30rpx;
  gap: 24rpx;
}

/* 头像容器：固定样式（登录/未登录统一样式，仅换图片） */
.avatar-box {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  overflow: hidden;
  border: 4rpx solid var(--cream-primary);
  box-shadow: var(--cream-shadow);
  background-color: #f8f6f3; /* 背景色，避免图片加载异常显白 */
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 用户头像：固定大小，完整显示（适配两张图片） */
.user-avatar {
  width: 100% !important;
  height: 100% !important;
  object-fit: contain;
}

/* 用户信息区域：纵向布局 */
.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 16rpx;
}

/* 登录后用户名 */
.user-name {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--cream-text-main);
}

/* 未登录提示文字 */
.unlogin-text {
  font-size: 26rpx;
  color: var(--cream-text-secondary);
}

/* 未登录-立即登录按钮 */
.login-btn {
  width: 160rpx;
  height: 70rpx;
  line-height: 60rpx;
  background-color: var(--cream-primary) !important;
  color: var(--cream-text-main) !important;
  font-size: 26rpx;
  border-radius: var(--cream-radius-sm) !important;
  box-shadow: var(--cream-shadow);
  border: none !important;
}

.login-btn::after {
  border: none !important;
}

/* 功能入口卡片：网格布局，奶油风卡片 */
.func-card {
  background-color: #fff;
  border-radius: var(--cream-radius);
  box-shadow: var(--cream-shadow);
  padding: 40rpx 30rpx;
  margin-bottom: 30rpx;
}

/* 功能项：4列网格，居中对齐 */
.func-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 25%;
  margin-bottom: 20rpx;
  gap: 12rpx;
}

/* 功能文字 */
.func-text {
  font-size: 26rpx;
  color: var(--cream-text-main);
}

/* 设置卡片：奶油风卡片，列表式 */
.setting-card {
  background-color: #fff;
  border-radius: var(--cream-radius);
  box-shadow: var(--cream-shadow);
  margin-bottom: 40rpx;
  overflow: hidden;
}

/* 设置项：横向布局，底部轻边框 */
.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx 30rpx;
  border-bottom: var(--cream-border);
}

.setting-item:last-child {
  border-bottom: none;
}

/* 设置项左侧：图标+文字 */
.setting-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

/* 设置文字 */
.setting-text {
  font-size: 28rpx;
  color: var(--cream-text-main);
}

/* 右箭头容器：固定样式 */
.icon-placeholder.setting-arrow {
  width: 30rpx !important;
  height: 30rpx !important;
  background-color: transparent !important;
  padding: 0 !important;
  margin: 0 !important;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 右箭头图片专属样式 */
.arrow-img {
  width: 100% !important;
  height: 100% !important;
  object-fit: contain !important;
  transform: none !important;
}

/* 退出登录按钮：奶油风主色调，大圆角 */
.logout-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background-color: var(--cream-primary) !important;
  color: var(--cream-text-main) !important;
  font-size: 30rpx;
  font-weight: 500;
  border-radius: var(--cream-radius) !important;
  box-shadow: var(--cream-shadow);
  border: none !important;
}

.logout-btn::after {
  border: none !important;
}

/* 按钮点击态：缩放+颜色加深 */
.login-btn:active,
.logout-btn:active {
  background-color: #e0d0bc !important;
  transform: scale(0.98);
  transition: all 0.2s ease;
}

/* 图标占位通用样式 */
.icon-placeholder {
  width: 48rpx;
  height: 48rpx;
  background-color: #f8f6f3;
  border-radius: var(--cream-radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 功能入口图标占位：稍大 */
.func-item .icon-placeholder {
  width: 60rpx;
  height: 60rpx;
}

/* 所有图标image标签通用适配 */
.icon-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
</style>